# Description

Online merchandise and memorabilia shop offering official BelFoot FC products with integrated inventory management and order fulfillment.

# Capabilities

- Display product catalog with real-time stock levels
- Process online orders with payment and shipping
- Manage product returns and refund workflows
- Sync inventory levels with SAP S4HANA
- Support promotional campaigns and discount codes

# Bounded Context
- Product Delivery & Material Management

# Data Landscape

| Entity | Description | Role | Software Systems |
|--------|-------------|------|------------------|
| [Product](PRODUCT) | Physical or digital item available for sale | Owns | |
| [Order](ORDER) | Customer purchase of one or more products | Owns | |
| [Cart](CART) | Temporary collection of items before checkout | Owns | |
| [Shipment](SHIPMENT) | Dispatched delivery of an order to a customer | Owns | |
| [Inventory](INVENTORY) | Stock levels of products and materials | Uses | SAP S/4HANA |
| [Customer Profile](CUSTOMER_PROFILE) | Contact and purchase history of a customer | Uses | Salesforce CRM |
