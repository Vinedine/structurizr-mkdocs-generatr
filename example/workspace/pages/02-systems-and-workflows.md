!!! note "Quick Summary"

    18 personas interact with 28 software systems across the BelFoot FC landscape. Each system gets auto-generated context diagrams, container diagrams, and documentation pages. Four dynamic views show how systems collaborate at runtime.

## Personas

18 personas interact with the BelFoot FC landscape -- from fans and sponsors to coaches, analysts, and IT architects. See the full index in [Persons](../persons/index.md).

![All Personas](embed:SystemLandscapeUsers)

## All Software Systems

28 software systems power everything from ticketing and stadium operations to data analytics and AI-driven coaching. See the full index in [Software Systems](../software-systems/index.md). The landscape view below shows every system and how they relate to each other.

![Software Systems](embed:SystemLandscapeSoftwareSystems)

## System Deep-Dive: Ticketing Platform

Every software system on this site has auto-generated pages with container diagrams, dependencies, and documentation. Here is the Ticketing Platform -- a system that crosses organizational boundaries, touching fans, agents, payment processing, and stadium infrastructure:

![Ticketing Platform — Containers](embed:ContainerTicketingPlatform)

## Dynamic Views

Dynamic views animate a specific workflow step by step, showing how containers collaborate at runtime to fulfill a use case.

=== "Fan Buys a Ticket"

    A fan browses matches, authenticates, pays via Stripe, and the event propagates to CRM and the integration platform.

    ![Purchase Ticket](embed:PurchaseTicket)

=== "Gameday Operations"

    IoT sensors feed crowd density data to AI predictions while fans pay cashlessly at food and drink outlets.

    ![Gameday Flow](embed:GamedayFlow)

=== "Data Ingestion"

    Events from ticketing, web store, and payments flow through the integration platform into the data lakehouse.

    ![Data Ingestion Flow](embed:DataIngestionFlow)

=== "Injury Risk Prediction"

    Training data and performance metrics feed an AI model that scores injury risk for the head coach.

    ![Injury Risk Prediction](embed:InjuryRiskPrediction)
