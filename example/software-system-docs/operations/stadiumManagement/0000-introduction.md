# Description

Facility operations platform managing stadium zones, IoT sensor monitoring, maintenance scheduling, energy management, and infrastructure assets for BelFoot Arena.

# Business Capabilities

- Monitor crowd levels and zone occupancy in real-time via IoT sensors
- Schedule and track facility maintenance requests
- Coordinate HVAC, lighting, and energy consumption
- Predict crowd density using AI for safety management
- Manage stadium expansion and construction projects
- Track energy consumption and sustainability targets
- Manage rolling assets, machinery, and equipment
- Administer rental contracts for commercial and leisure areas

# Bounded Context
- Asset/Infrastructure Management

# Data Landscape

| Entity | Description | Role | Software Systems |
|--------|-------------|------|------------------|
| [Venue](VENUE) | Physical location such as the stadium or training ground | Owns | |
| [Zone](ZONE) | Designated area within a venue for access control | Owns | |
| [IoT Sensor Reading](IOT_SENSOR_READING) | Data point from an IoT device monitoring a zone | Owns | |
| [Maintenance Request](MAINTENANCE_REQUEST) | Work order for facility repair or upkeep | Owns | |
| [Energy Reading](ENERGY_READING) | Measured energy consumption at a venue | Owns | |
| [Sustainability Target](SUSTAINABILITY_TARGET) | Environmental goal tracked against energy data | Owns | |
| [Rolling Asset](ROLLING_ASSET) | Movable equipment or vehicle owned by the club | Owns | |
| [Rental Contract](RENTAL_CONTRACT) | Lease agreement for venue or facility use | Owns | |
| [Construction Project](CONSTRUCTION_PROJECT) | Building or renovation project at a venue | Owns | |
| [Event](EVENT) | Organised gathering such as a match or concert | Uses | Ticketing Platform |
