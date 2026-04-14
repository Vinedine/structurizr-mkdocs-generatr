# 3. Implement Event-Driven Integration

Date: 2025-04-10

## Status

Completed

## Context

BelFoot FC has 20 software systems across 5 departments that need to exchange data. Point-to-point integrations would create an unmanageable web of connections and tight coupling between systems.

## Decision

Implement Azure Service Bus as the central event-driven integration backbone. All systems publish domain events to topics, and interested systems subscribe to relevant events. An Integration Platform API handles message routing, transformation, and monitoring.

![ContainerIntegrationPlatform](embed:ContainerIntegrationPlatform)

## Consequences

- Systems are loosely coupled through publish-subscribe messaging
- New systems can subscribe to existing events without modifying producers
- Dead-letter queues provide built-in error handling and retry capabilities
- Data Platform ETL pipelines consume events for near real-time data ingestion
- Requires operational monitoring of message queues and throughput
