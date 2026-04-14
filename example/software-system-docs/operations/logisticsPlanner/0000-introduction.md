# Description

Procurement and logistics platform managing suppliers, purchase orders, and inbound deliveries for stadium operations and merchandise.

# Business Capabilities

- Onboard and manage supplier profiles and catalogs
- Create and track purchase orders through approval workflows
- Schedule and monitor inbound deliveries to the stadium
- Integrate with SAP S4HANA for financial reconciliation

# Bounded Context
- Product Delivery & Material Management

# Data Landscape

| Entity | Description | Role | Software Systems |
|--------|-------------|------|------------------|
| [Supplier](SUPPLIER) | External vendor providing goods or services | Owns | |
| [Purchase Order](PURCHASE_ORDER) | Formal order placed with a supplier | Owns | |
| [Delivery Schedule](DELIVERY_SCHEDULE) | Planned timeline for supplier deliveries | Owns | |
| [Inventory](INVENTORY) | Stock levels of products and materials | Uses | SAP S/4HANA |
| [Invoice](INVOICE) | Bill issued for goods or services rendered | Uses | SAP S/4HANA |
