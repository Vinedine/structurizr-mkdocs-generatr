!!! note "Quick Summary"

    28 software systems defined in a single workspace. Each gets auto-generated context diagrams, container diagrams, and documentation pages. Four dynamic views show how systems collaborate at runtime.

## Personas

18 personas interact with the BelFoot FC landscape -- from fans and sponsors to coaches, analysts, and IT architects. Each persona gets an auto-generated page showing which systems they interact with.

![All Personas](embed:SystemLandscapeUsers)

## System Deep-Dive: Ticketing Platform

Every software system on this site has auto-generated pages with container diagrams, dependencies, and documentation. Here is the Ticketing Platform -- a system that crosses organizational boundaries, touching fans, agents, payment processing, and stadium infrastructure:

![Ticketing Platform — Containers](embed:ContainerTicketingPlatform)

The container diagram shows the API, database, and web application that make up the system, along with their technology choices and relationships to other systems.

## Dynamic Views

Dynamic views animate a specific workflow step by step, showing how containers collaborate at runtime to fulfill a use case.

=== "Fan Buys a Ticket"

    ![Purchase Ticket](embed:PurchaseTicket)

    A fan browses matches, authenticates, pays via Stripe, and the event propagates to CRM and the integration platform.

=== "Gameday Operations"

    ![Gameday Flow](embed:GamedayFlow)

    IoT sensors feed crowd density data to AI predictions while fans pay cashlessly at food and drink outlets.

=== "Data Ingestion"

    ![Data Ingestion Flow](embed:DataIngestionFlow)

    Events from ticketing, web store, and payments flow through the integration platform into the data lakehouse.

=== "Injury Risk Prediction"

    ![Injury Risk Prediction](embed:InjuryRiskPrediction)

    Training data and performance metrics feed an AI model that scores injury risk for the head coach.

??? example "The DSL Behind It"

    Everything above is generated from Structurizr DSL. Here is what a software system definition looks like:

    ```dsl
    softwareSystemPlayerPerformance = softwareSystem "Player Performance" "Training analytics, GPS tracking, and match statistics" {

        containerPlayerPerformanceDatabase = container "Performance Database" "Training sessions, GPS data, match statistics, and fitness scores" "PostgreSQL" "DATASET" {
        }

        containerPlayerPerformanceApi = container "Player Performance API" "Training data ingestion, analytics, and performance reporting" "Python" "SERVICE" {
            properties {
                "Repository" "https://dev.azure.com/BelFoot/_git/player-performance-api"
            }
            this -> containerPlayerPerformanceDatabase "Manage data" "SQL/TCP"
        }

        containerPlayerPerformanceDashboard = container "Performance Dashboard" "Visual analytics for player fitness, load management, and match performance" "Power BI" "DASHBOARD" {
            userHeadCoach -> this "Review player performance and set training plans"
            this -> containerPlayerPerformanceApi "Get performance data" "JSON/HTTPS"
        }
    }
    ```

    One block of DSL produces the system context diagram, container diagram, and all associated pages -- automatically.
