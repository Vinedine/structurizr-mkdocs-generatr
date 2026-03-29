# Description

Customer Relationship Management platform for managing fan interactions, sponsor relationships, sales pipeline, and support cases.

# Business Capabilities

- Manage fan and customer profiles across all touchpoints
- Track sponsor and partner relationship lifecycle
- Handle fan complaints and support tickets
- Provide 360-degree customer view for sales and marketing teams
- Manage B2B sales pipeline and opportunities
- Track customer and corporate account relationships

# Bounded Context
- Customer/Fan Services & Relationship
- Marketing & Sales

# Data Landscape

| Entity | Description | Role | Software Systems |
|--------|-------------|------|------------------|
| [Customer Profile](CUSTOMER_PROFILE) | Contact and purchase history of a customer | Owns | |
| [Support Case](SUPPORT_CASE) | Customer service request or complaint | Owns | |
| [Sales Opportunity](SALES_OPPORTUNITY) | Prospective deal tracked in the sales pipeline | Owns | |
| [Account](ACCOUNT) | Business or individual account in the CRM system | Owns | |
| [Ticket](TICKET) | Entry pass granting access to an event or seat | Uses | Ticketing Platform |
| [Order](ORDER) | Customer purchase of one or more products | Uses | Web Store |
| [Sponsor](SPONSOR) | Business partner providing funding or services to the club | Uses | Sponsorship Portal |

# References

- [Salesforce Documentation]()
