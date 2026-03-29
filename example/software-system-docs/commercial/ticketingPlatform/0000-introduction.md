# Description

B2C and B2B ticket sales platform managing match tickets, season passes, seat allocation, and event access for BelFoot FC.

# Business Capabilities

- Sell match tickets online with real-time seat availability
- Manage season pass subscriptions and renewals
- Allocate B2B ticket blocks for corporate hospitality
- Generate e-tickets with QR codes for stadium access
- Track ticket sales performance and attendance statistics

# Bounded Context
- Gameday Match/Event Delivery

# Data Landscape

| Entity | Description | Role | Software Systems |
|--------|-------------|------|------------------|
| [Ticket](TICKET) | Entry pass granting access to an event or seat | Owns | |
| [Season Pass](SEASON_PASS) | Subscription covering all home matches for a season | Owns | |
| [Seat](SEAT) | Specific seat location within the stadium | Owns | |
| [Event](EVENT) | Organised gathering such as a match or concert | Owns | |
| [Match](MATCH) | Scheduled football match at the stadium | Owns | |
| [Customer Profile](CUSTOMER_PROFILE) | Contact and purchase history of a customer | Uses | Salesforce CRM |
