# Description

Training analytics and match statistics platform providing GPS tracking data, fitness scores, AI-driven injury risk predictions, and player contract and transfer management for coaching staff.

# Business Capabilities

- Ingest GPS and biometric data from training sessions
- Calculate player fitness scores and workload metrics
- Generate match performance statistics and heatmaps
- Run AI injury risk prediction models via Azure AI Foundry
- Provide coaching dashboards for squad management decisions
- Manage player contracts, negotiations, and transfers

# Bounded Context
- Staff, Player & Team Development

# Data Landscape

| Entity | Description | Role | Software Systems |
|--------|-------------|------|------------------|
| [Player](PLAYER) | Professional footballer registered with the club | Owns | |
| [Training Session](TRAINING_SESSION) | Planned practice session for players | Owns | |
| [Match Performance](MATCH_PERFORMANCE) | Player statistics and ratings from a match | Owns | |
| [Fitness Score](FITNESS_SCORE) | Quantified measure of a player's physical condition | Owns | |
| [Player Contract](PLAYER_CONTRACT) | Employment agreement between player and club | Owns | |
| [Transfer](TRANSFER) | Player movement between clubs via sale or loan | Owns | |
| [Injury](INJURY) | Recorded physical injury affecting a player | Uses | Medical Records |
