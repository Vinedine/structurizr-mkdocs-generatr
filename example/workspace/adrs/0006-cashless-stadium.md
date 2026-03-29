# 6. Cashless-Only Stadium

Date: 2025-07-01

## Status

Completed

## Context

Cash handling at concession stands creates long queues during matches, increases security risks, and makes revenue tracking difficult. Post-COVID fan expectations have shifted toward contactless experiences.

## Decision

Implement a cashless-only policy for BelFoot Arena. All in-stadium purchases use the Cashless Payment system with NFC-enabled terminals. Fans top up digital wallets via the Fan Engagement App or at self-service kiosks. Payments are processed through Stripe.

![ContainerCashlessPayment](embed:ContainerCashlessPayment)

## Consequences

- Faster transaction times reducing queue lengths by an estimated 40%
- Complete digital audit trail for all in-stadium revenue
- Transaction events flow to Integration Platform for real-time analytics
- Accessibility considerations: self-service kiosks must support assisted top-up for fans without smartphones
- Initial investment in NFC terminal infrastructure across all concession points
