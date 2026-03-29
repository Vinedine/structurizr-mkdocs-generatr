# Description

Online payment processing platform handling ticket purchases, merchandise orders, and in-stadium cashless transactions.

# Business Capabilities

- Process credit card and digital wallet payments
- Manage recurring subscription payments for season passes
- Handle payment refunds and disputes
- Provide PCI-compliant payment infrastructure

# Bounded Context
- Product Delivery & Material Management

# Data Landscape

| Entity | Description | Role | Software Systems |
|--------|-------------|------|------------------|
| [Payment](PAYMENT) | Settlement of an invoice or transaction | Uses | SAP S/4HANA |

# References

- [Stripe Documentation]()
