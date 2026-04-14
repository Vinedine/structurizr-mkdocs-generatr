workspace "BelFoot FC IT Landscape" {

    !docs workspace/pages
    !adrs workspace/adrs

    model {

        properties {
            "structurizr.groupSeparator" "/"
            "group.Commercial.description" "The Commercial group owns all revenue-generating and fan-facing systems: ticketing, merchandise, sponsorship, marketing, and CRM. These systems share a common fan identity and push events into the integration platform so downstream analytics can track the full customer journey."
            "group.Corporate.description" "Corporate systems handle finance (SAP S/4HANA), HR, compliance, strategy, and external relations. They form the governance backbone of the club, with payroll and procurement data flowing between HR, SAP, and the data platform for consolidated reporting."
            "group.IT.description" "The IT group provides shared infrastructure that every other group depends on: identity management (Entra ID), event-driven integration (Service Bus), data platform (ETL + Power BI), the Databricks lakehouse, and AI/ML capabilities. These are the horizontal enablers that tie the landscape together."
            "group.Operations.description" "Operations covers everything that happens at the stadium: facility management, IoT sensors, matchday coordination, and cashless payments. These systems run on-premise for latency-critical gameday scenarios, while their data feeds into the cloud for long-term analytics and AI-driven crowd predictions."
            "group.Sporting.description" "Sporting systems track player performance (GPS, biometrics, match stats), medical records, and youth academy scouting. They run on AWS to leverage its sports analytics ecosystem and feed injury risk models through Azure AI Foundry."
            "deployment.Production.description" "Production hosts all live workloads across three infrastructure zones. BelFoot FC follows a multi-cloud strategy where each workload runs in the environment best suited to its latency, ecosystem, and regulatory requirements. This is a deliberate architectural decision driven by latency, ecosystem, and compliance considerations."
            "deployment.Production.On-Premise.description" "Latency-critical gameday systems (ticketing validation, stadium access control, IoT sensors) run in the stadium data center. Sub-second response times during peak crowd flow cannot depend on an internet round-trip. Event data is replicated to the cloud asynchronously for analytics."
            "deployment.Production.Azure Cloud.description" "The majority of the landscape runs on Azure: fan-facing digital platforms, corporate systems, the data platform, integration backbone, and AI/ML workloads. Resources are organized into dedicated resource groups per domain, each with its own scaling and cost boundaries."
            "deployment.Production.AWS Cloud.description" "Sporting analytics (player performance, medical records, youth academy) run on AWS to leverage its sports-specific ecosystem. ECS Fargate services keep operational overhead low, while RDS PostgreSQL handles persistence and Amazon Managed Grafana provides coaching dashboards."
            "deployment.Acceptance.description" "Acceptance mirrors production topology at reduced scale for final validation before release. All services run in a single Azure resource group with appropriately sized SKUs."
            "deployment.Test.description" "Test provides isolated environments for integration and regression testing. Infrastructure matches acceptance but with minimal SKUs to keep costs low."
            "deployment.Development.description" "Development uses shared, cost-optimized Azure infrastructure for daily development work. All services are consolidated into a single resource group with burstable and serverless SKUs."
        }

        !include workspace/users.dsl

        !include workspace/groups/it.dsl
        !include workspace/groups/commercial.dsl
        !include workspace/groups/corporate.dsl
        !include workspace/groups/sporting.dsl
        !include workspace/groups/operations.dsl

        !include workspace/deployments/development.dsl
        !include workspace/deployments/test.dsl
        !include workspace/deployments/acceptance.dsl
        !include workspace/deployments/production.dsl

        // ============================================================
        // Cross-group relationships: Commercial
        // ============================================================

        containerTicketingPlatformApi -> containerSalesforceCrmApi "Sync customer data on ticket purchase" "JSON/HTTPS"
        containerTicketingPlatformApi -> containerStripeApi "Process ticket payments" "JSON/HTTPS"
        containerTicketingPlatformApi -> containerIntegrationPlatformServiceBus "Publish ticket purchase events" "AMQP/TCP"

        containerWebStoreApi -> containerStripeApi "Process merchandise payments" "JSON/HTTPS"
        containerWebStoreApi -> containerSapS4HanaApi "Sync inventory and orders" "JSON/HTTPS"
        containerWebStoreApi -> containerIntegrationPlatformServiceBus "Publish order events" "AMQP/TCP"

        containerSponsorshipPortalApi -> containerSalesforceCrmApi "Sync sponsor contacts" "JSON/HTTPS"

        containerFanEngagementApi -> containerSalesforceCrmApi "Get fan profile data" "JSON/HTTPS"
        containerFanEngagementApi -> containerTicketingPlatformApi "Get ticket purchase history" "JSON/HTTPS"

        containerMarketingPlatformApi -> containerSalesforceCrmApi "Get customer and account data" "JSON/HTTPS"
        containerMarketingPlatformApi -> containerSponsorshipPortalApi "Get sponsor and campaign data" "JSON/HTTPS"
        containerMarketingPlatformApi -> containerFanEngagementApi "Target fan segments for campaigns" "JSON/HTTPS"

        containerProductDevelopmentApi -> containerWebStoreApi "Publish new products" "JSON/HTTPS"
        containerProductDevelopmentApi -> containerTicketingPlatformApi "Publish ticket products" "JSON/HTTPS"

        // ============================================================
        // Cross-group relationships: Operations
        // ============================================================

        containerCashlessPaymentApi -> containerStripeApi "Process in-stadium payments" "JSON/HTTPS"
        containerCashlessPaymentApi -> containerIntegrationPlatformServiceBus "Publish transaction events" "AMQP/TCP"

        containerStadiumManagementApi -> containerAzureAiFoundryApi "Predict crowd density from sensor data" "JSON/HTTPS"

        containerLogisticsPlannerApi -> containerSapS4HanaApi "Manage purchase orders and supplier data" "JSON/HTTPS"

        containerMatchdayOperationsApi -> containerStadiumManagementApi "Get venue and zone data" "JSON/HTTPS"
        containerMatchdayOperationsApi -> containerTicketingPlatformApi "Get event and ticket data" "JSON/HTTPS"
        containerMatchdayOperationsApi -> containerAzureAiFoundryApi "Predict crowd density for safety planning" "JSON/HTTPS"

        // ============================================================
        // Cross-group relationships: Sporting
        // ============================================================

        containerPlayerPerformanceApi -> containerAzureAiFoundryApi "Run injury risk prediction models" "JSON/HTTPS"
        containerPlayerPerformanceApi -> containerDatabricksWorkspace "Store and query training data" "JSON/HTTPS"

        containerMedicalRecordsApi -> containerPlayerPerformanceApi "Get player fitness data" "JSON/HTTPS"

        // ============================================================
        // Cross-group relationships: Corporate
        // ============================================================

        containerHrPortalApi -> containerSapS4HanaApi "Sync payroll and employee data" "JSON/HTTPS"

        containerComplianceManagerApi -> containerSapS4HanaApi "Query financial audit records" "JSON/HTTPS"

        containerStrategyPortalApi -> containerDataPlatformDashboard "Access strategic KPI dashboards" "JSON/HTTPS"

        containerExternalRelationsApi -> containerSalesforceCrmApi "Get stakeholder contact data" "JSON/HTTPS"

        // ============================================================
        // Cross-group relationships: IT
        // ============================================================

        containerIntegrationPlatformServiceBus -> containerDataPlatformEtl "Route events for data ingestion" "AMQP/TCP"
        containerDataPlatformEtl -> containerDatabricksUnityCatalog "Load transformed data into lakehouse" "SQL/TCP"
        containerDataPlatformLakehouse -> containerDatabricksUnityCatalog "Read curated data products" "SQL/TCP"

    }

    views {

        !include workspace/views/dynamic.dsl
        !include _auto_generated_views.dsl

        properties {
            "c4plantuml.tags" "true"
            "mkdocs.navigation.nestGroups" "true"
            "mkdocs.color.primary" "#2c4390"
            "mkdocs.color.headerText" "#ffffff"
            "mkdocs.favicon" "site/favicon.ico"
            "mkdocs.externalTag" "External System"
        }

        styles {

            element "Person" {
                shape person
                background #7bb6b3
                color #ffffff
            }

            element "Software System" {
                background #2c4390
                color #ffffff
            }

            element "External System" {
                background #324b4a
            }

            element "Shared" {
                background #158582
            }

            element "New" {
                background #d88c42
            }

            // Container Types (https://support.atlassian.com/compass/docs/what-are-components/)

            // An independently-deployable software unit that is usually is operated by a person or a team. Services can be as large as monoliths or smaller microservices.
            // Service components have a Tier field to indicate how critical the service is to your business.
            element "SERVICE" {
                shape RoundedBox
            }
            // A reusable collection of objects, functions, and methods. A library is typically used by other components.
            element "LIBRARY" {
                shape Robot
            }

            // A fully-packaged application, like a mobile application, desktop application, or a CLI-type tool.
            element "APPLICATION" {
                shape Window
            }

            // A higher-level product functionality that end-users understand and in which they see value. A capability is an abstraction of one or more underlying software components that power it.
            element "CAPABILITY" {
                shape Component
            }

            // An entity or service provided by a cloud vendor, with consumer-managed configuration and monitoring.
            element "CLOUD_RESOURCE" {
                shape WebBrowser
            }

            // A sequence of tools and processes used to automate the transformation and movement of data from a source to a target system.
            element "DATA_PIPELINE" {
                shape Pipe
            }

            // Reusable building blocks of a design system that meet a specific interaction or user interface need and work together to create patterns and user experiences.
            element "UI_ELEMENT" {
                shape WebBrowser
            }

            // Website — A single web page or a collection of related web pages under a single domain. Websites mainly consist of audio-visual or text content for reading, listening, or viewing.
            // People can't edit, contribute to, or affect the website content. Websites are typically publicly accessible and don't require authentication.
            element "WEBSITE" {
                shape WebBrowser
            }

            // A collection of data about a specific topic that can be referenced by code, generally a table.
            element "DATASET" {
                shape Cylinder
            }

            // Data visuals that provide views of key performance indicators relevant to a particular objective or business process.
            element "DASHBOARD" {
                shape WebBrowser
            }

            // A governed, self-contained, cohesive, read-optimized data unit.
            element "DATA_PRODUCT" {
                shape Folder
            }

        }

    }

}
