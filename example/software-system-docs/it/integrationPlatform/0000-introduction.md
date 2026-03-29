# Description

Event-driven integration backbone using Azure Service Bus to enable loosely coupled communication between all BelFoot FC software systems.

# Business Capabilities

- Route events between systems using publish-subscribe topics
- Transform message formats between heterogeneous systems
- Monitor message queues, dead-letter queues, and throughput
- Provide guaranteed message delivery with retry policies

# Bounded Context
- IT Management

# Data Landscape

| Entity | Description | Role | Software Systems |
|--------|-------------|------|------------------|
| [Integration Topic](INTEGRATION_TOPIC) | Message topic connecting systems via events | Owns | |
| [Ticket](TICKET) | Entry pass granting access to an event or seat | Uses | Ticketing Platform |
| [Order](ORDER) | Customer purchase of one or more products | Uses | Web Store |
| [Transaction](TRANSACTION) | Financial exchange recorded at point of sale | Uses | Cashless Payment |

# References

- [Integration Platform ADR](/decisions/3/)
