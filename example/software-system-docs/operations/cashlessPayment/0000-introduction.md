# Description

Contactless in-stadium payment system enabling fans to purchase food, drinks, and merchandise using NFC-enabled devices and digital wallets.

# Capabilities

- Process contactless payments via NFC at point-of-sale terminals
- Manage digital wallet top-ups and balance inquiries
- Track real-time transaction volumes per stadium zone
- Generate sales reports per concession stand and product category
- Process food and drinks orders at stadium concessions

# Bounded Context
- Product Delivery & Material Management

# Data Landscape

| Entity | Description | Role | Software Systems |
|--------|-------------|------|------------------|
| [Transaction](TRANSACTION) | Financial exchange recorded at point of sale | Owns | |
| [Digital Wallet](DIGITAL_WALLET) | Stored-value account for cashless stadium payments | Owns | |
| [Menu](MENU) | Food and beverage offerings at stadium outlets | Owns | |
| [Customer Profile](CUSTOMER_PROFILE) | Contact and purchase history of a customer | Uses | Salesforce CRM |
