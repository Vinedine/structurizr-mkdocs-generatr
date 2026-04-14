# Description

Central data platform providing ETL pipelines, curated data products, and Power BI business intelligence dashboards for executive and operational reporting.

# Capabilities

- Ingest operational events from Integration Platform via ETL pipelines
- Transform and curate data into governed data products
- Provide self-service Power BI dashboards for KPI monitoring
- Enable trend analysis and market intelligence reporting
- Track application portfolio and IT project reporting

# Bounded Context
- IT Management

# Data Landscape

| Entity | Description | Role | Software Systems |
|--------|-------------|------|------------------|
| [Data Product](DATA_PRODUCT) | Curated dataset published for analytical consumption | Owns | |
| [Dashboard Report](DASHBOARD_REPORT) | Visual report displaying key metrics and KPIs | Owns | |
| [Ticket](TICKET) | Entry pass granting access to an event or seat | Uses | Ticketing Platform |
| [Order](ORDER) | Customer purchase of one or more products | Uses | Web Store |
| [Transaction](TRANSACTION) | Financial exchange recorded at point of sale | Uses | Cashless Payment |
| [Invoice](INVOICE) | Bill issued for goods or services rendered | Uses | SAP S/4HANA |
| [Customer Profile](CUSTOMER_PROFILE) | Contact and purchase history of a customer | Uses | Salesforce CRM |
| [Match Performance](MATCH_PERFORMANCE) | Player statistics and ratings from a match | Uses | Player Performance |

# References

- [Data Lakehouse ADR](/decisions/4/)
