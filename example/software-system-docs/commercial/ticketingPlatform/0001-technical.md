<!-- Last updated: 2026-04-17 -->

# Technical Architecture

Node.js ticketing service backed by PostgreSQL with a React portal front-end. Two deployable components ([ticketing-api](https://dev.azure.com/BelFoot/_git/ticketing-api) + `ticketing-portal`) plus a shared Azure Database for PostgreSQL instance. The API publishes purchase events to Service Bus for downstream ingestion and calls Stripe for payments and Salesforce CRM for customer history.

## Authentication & Authorization

- **Portal (`ticketing-portal`, React):** OAuth 2.0 PKCE flow against Microsoft Entra ID (tenant `belfoot.onmicrosoft.com`). The portal acquires an access token via `@azure/msal-browser` and attaches it as a Bearer token on every API call.
- **API (`ticketing-api`, Node.js/Express):** Validates Entra ID JWTs using `passport-azure-ad` (JWKS, RS256). Two app roles are defined in the Entra app manifest:
  - `Fan` — granted to all authenticated fans and season-ticket holders; allows `GET /tickets`, `POST /tickets`, `GET /season-pass`.
  - `TicketingAgent` — granted to agents in the `Ticketing Agents` AD group; allows allocation endpoints under `/admin/allocations`.
- Authorization is enforced by the `requireRole(role)` Express middleware at the route level. Requests without a valid token return 401; authenticated requests without the required role return 403.
- CORS: `https://tickets.belfoot.com` and `https://tickets-acc.belfoot.com` are the only allowed origins; credentials are disabled (token flows through `Authorization` header).
- Stripe and Salesforce CRM outbound calls use service-principal client-credentials flow; secrets are pulled at startup from Azure Key Vault `kv-belfoot-ticketing`.

## Ticketing Portal

React single-page app (Vite, TypeScript). Deployed to Azure Static Web Apps with the API as its linked backend. Major routes:

- `/` — match listing with real-time availability badges (polls `/availability` every 30s)
- `/match/:id/seats` — interactive seat picker
- `/checkout` — Stripe Elements + purchase confirmation
- `/season-pass` — season-pass dashboard for subscribers
- `/admin` — agent allocation console (role-gated)

## Ticketing Database

Azure Database for PostgreSQL (v15). Key tables:

| Table | Domain | Usage |
| --- | --- | --- |
| `ticket` | Ticket | One row per issued ticket; includes `qr_code`, `status`, `event_id`, `seat_id`, `owner_email` |
| `season_pass` | Season Pass | Active + historical passes with `holder_id`, `season_year`, `tier` |
| `seat` | Seat | Stadium seat inventory; `section`, `row`, `number`, `accessibility_flag` |
| `event` | Event | Match or non-match events; `kickoff_at`, `capacity`, `status` |
| `allocation` | Ticket | B2B seat blocks; links `partner_id` to reserved seats |
| `purchase_audit` | Infrastructure | Append-only log of purchase intents and outcomes (for dispute resolution) |

Migrations are managed via `node-pg-migrate` under `migrations/` in the `ticketing-api` repo.

## Event Publishing

On successful purchase, refund, or transfer, the API publishes a JSON message to the `ticket-events` topic on the Integration Platform's Azure Service Bus. The message schema lives at [`docs/events/ticket-events.schema.json`](https://dev.azure.com/BelFoot/_git/ticketing-api) in the API repo. The Data Platform subscribes to this topic for lakehouse ingestion (see the *Event-Driven Data Ingestion to Lakehouse* dynamic view).

## Payment Flow

```
Portal  -> API      POST /tickets { matchId, seatId, paymentMethodId }
API     -> DB       INSERT ticket (status=pending)
API     -> Stripe   POST /v1/payment_intents (confirm=true)
Stripe  -> API      { status: succeeded, paymentIntentId }
API     -> DB       UPDATE ticket SET status=confirmed
API     -> CRM      POST /Contact/{id}/Purchase (Salesforce)
API     -> Bus      PUBLISH ticket.purchased
API     -> Portal   { ticket, qrCode }
```

If Stripe fails, the pending row stays in `ticket` with `status=failed` for 24h before being hard-deleted by the `ticket-cleanup` cron job (runs daily at 02:00 UTC).

# API Reference

## Ticketing API

Node.js/Express service exposing ticket and season-pass operations. Runs on Azure App Service (S1 in acceptance, P1v3 in production) with horizontal scale-out enabled.

### Ticket endpoints (`/api/v1/tickets/`)

| Endpoint | Purpose |
| --- | --- |
| `GET /api/v1/tickets/availability?matchId=` | List remaining seats for a match, grouped by section |
| `POST /api/v1/tickets` | Purchase a ticket: reserves seat, charges Stripe, persists ticket, publishes `ticket.purchased` event |
| `GET /api/v1/tickets/{ticketId}` | Retrieve a single ticket including QR code payload |
| `POST /api/v1/tickets/{ticketId}/transfer` | Transfer a ticket to another fan by email |
| `DELETE /api/v1/tickets/{ticketId}` | Cancel a ticket and issue a Stripe refund |

### Season pass endpoints (`/api/v1/season-pass/`)

| Endpoint | Purpose |
| --- | --- |
| `GET /api/v1/season-pass/me` | Return the current user's season pass and renewal status |
| `POST /api/v1/season-pass/renew` | Renew a season pass for the next season |
| `GET /api/v1/season-pass/{passId}/matches` | List matches covered by the pass, with check-in status |

### Agent endpoints (`/api/v1/admin/allocations/`) — role `TicketingAgent`

| Endpoint | Purpose |
| --- | --- |
| `POST /api/v1/admin/allocations` | Reserve a block of seats for a B2B partner |
| `GET /api/v1/admin/allocations?partnerId=` | List current allocations for a corporate partner |
| `DELETE /api/v1/admin/allocations/{allocationId}` | Release an allocation back to general availability |
