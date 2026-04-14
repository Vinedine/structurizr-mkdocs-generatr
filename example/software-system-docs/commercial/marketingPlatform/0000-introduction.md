# Description

Marketing campaign management and brand activation platform for planning multi-channel campaigns, managing brand assets, and coordinating sponsorship program marketing.

# Capabilities

- Develop and execute marketing campaigns across all channels
- Manage brand assets, guidelines, and visual identity
- Coordinate sponsorship program marketing and activation
- Market B2C and B2B ticket options and hospitality packages
- Market merchandise and gameday products and services
- Implement brand strategy through content and communications

# Bounded Context
- Marketing & Sales

# Data Landscape

| Entity | Description | Role | Software Systems |
|--------|-------------|------|------------------|
| [Marketing Campaign](MARKETING_CAMPAIGN) | Planned promotional activity targeting fans or sponsors | Owns | |
| [Brand Asset](BRAND_ASSET) | Logo, image, or creative material used in marketing | Owns | |
| [Sponsorship Program](SPONSORSHIP_PROGRAM) | Structured programme managing sponsor partnerships | Owns | |
| [Fan Profile](FAN_PROFILE) | Digital identity and preferences of a fan | Uses | Fan Engagement |
| [Customer Profile](CUSTOMER_PROFILE) | Contact and purchase history of a customer | Uses | Salesforce CRM |
| [Sponsor](SPONSOR) | Business partner providing funding or services to the club | Uses | Sponsorship Portal |
