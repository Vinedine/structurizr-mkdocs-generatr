# Description

B2B partner and sponsor management platform for onboarding sponsors, managing contracts, tracking campaigns, and coordinating hospitality packages.

# Business Capabilities

- Onboard new sponsors and manage partner profiles
- Track sponsorship contract terms and renewal dates
- Coordinate matchday hospitality packages for sponsors
- Report on campaign reach and brand visibility metrics

# Bounded Context
- Marketing & Sales

# Data Landscape

| Entity | Description | Role | Software Systems |
|--------|-------------|------|------------------|
| [Sponsor](SPONSOR) | Business partner providing funding or services to the club | Owns | |
| [Contract](CONTRACT) | Legal agreement between the club and a sponsor | Owns | |
| [Campaign](CAMPAIGN) | Sponsor-driven promotional or activation campaign | Owns | |
| [Hospitality Package](HOSPITALITY_PACKAGE) | Premium matchday experience included in a contract | Owns | |
| [Match](MATCH) | Scheduled football match at the stadium | Uses | Ticketing Platform |
