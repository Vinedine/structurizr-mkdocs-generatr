# Description

Player health management system tracking medical history, injuries, rehabilitation protocols, and return-to-play clearance for BelFoot FC squad.

# Business Capabilities

- Record player medical history and pre-season examinations
- Log injuries with diagnosis, treatment plans, and timelines
- Track rehabilitation progress against recovery milestones
- Manage return-to-play medical clearance workflow
- Provide player availability reports to coaching staff

# Bounded Context
- Staff, Player & Team Development

# Data Landscape

| Entity | Description | Role | Software Systems |
|--------|-------------|------|------------------|
| [Injury](INJURY) | Recorded physical injury affecting a player | Owns | |
| [Medical Record](MEDICAL_RECORD) | Clinical documentation of a player's health | Owns | |
| [Rehabilitation Plan](REHABILITATION_PLAN) | Recovery programme for an injured player | Owns | |
| [Player](PLAYER) | Professional footballer registered with the club | Uses | Player Performance |
| [Training Session](TRAINING_SESSION) | Planned practice session for players | Uses | Player Performance |
