groupIt = group "IT" {

    softwareSystemMicrosoftEntraId = softwareSystem "Microsoft Entra ID" "Identity and access management" "External System" {

        !docs ../../software-system-docs/it/microsoftEntraId

        containerEntraIdApi = container "Entra ID API" "OAuth 2.0 / OpenID Connect authentication and authorization endpoints" "Microsoft Entra ID" "CLOUD_RESOURCE" {
        }
    }

    softwareSystemDatabricks = softwareSystem "Databricks" "Unified analytics and data lakehouse platform" "External System" {

        !docs ../../software-system-docs/it/databricks

        containerDatabricksWorkspace = container "Databricks Workspace" "Notebooks, jobs, and ML experiments" "Databricks" "CLOUD_RESOURCE" {
            userDataAnalyst -> this "Run notebooks and queries"
        }

        containerDatabricksUnityCatalog = container "Unity Catalog" "Centralized data governance and lakehouse storage" "Delta Lake" "DATASET" {
        }

        containerDatabricksWorkspace -> containerDatabricksUnityCatalog "Read and write data" "SQL/TCP"
    }

    softwareSystemAzureAiFoundry = softwareSystem "Azure AI Foundry" "AI and ML platform for model training and deployment" "External System" {

        !docs ../../software-system-docs/it/azureAiFoundry

        containerAzureAiFoundryStudio = container "AI Foundry Studio" "Model management and experimentation UI" "Azure AI" "CLOUD_RESOURCE" {
            userDataAnalyst -> this "Train and evaluate models"
        }

        containerAzureAiFoundryApi = container "AI Foundry Inference API" "Real-time model inference endpoints" "Azure AI" "CLOUD_RESOURCE" {
        }

        containerAzureAiFoundryStudio -> containerAzureAiFoundryApi "Deploy and test models" "JSON/HTTPS"
    }

    softwareSystemIntegrationPlatform = softwareSystem "Integration Platform" "Event-driven integration backbone for cross-system messaging" "Shared" {

        !docs ../../software-system-docs/it/integrationPlatform

        containerIntegrationPlatformApi = container "Integration Platform API" "Message routing, transformation, and monitoring" "Azure Functions" "SERVICE" {
            properties {
                "Repository" "https://dev.azure.com/BelFoot/_git/integration-platform-api"
            }
        }

        containerIntegrationPlatformServiceBus = container "Azure Service Bus" "Topics and subscriptions for event-driven messaging" "Azure Service Bus" "CLOUD_RESOURCE" {
            userItArchitect -> this "Monitor message queues and dead-letter queues"
        }

        containerIntegrationPlatformApi -> containerIntegrationPlatformServiceBus "Publish and subscribe to events" "AMQP/TCP"
    }

    softwareSystemDataPlatform = softwareSystem "Data Platform" "Central data products, ETL pipelines, and business intelligence" "Shared" {

        !docs ../../software-system-docs/it/dataPlatform

        containerDataPlatformEtl = container "Data Platform ETL" "Extract, transform, and load pipelines for all operational data" "Azure Data Factory" "DATA_PIPELINE" {
        }

        containerDataPlatformLakehouse = container "Data Lakehouse" "Curated data products for business intelligence and analytics" "Databricks" "DATA_PRODUCT" {
        }

        containerDataPlatformDashboard = container "Business Intelligence Dashboard" "KPI reporting and executive analytics" "Power BI" "DASHBOARD" {
            userFinanceController -> this "View financial and operational KPIs"
            userDataAnalyst -> this "Create and manage reports"
        }

        containerDataPlatformEtl -> containerDataPlatformLakehouse "Load transformed data" "SQL/TCP"
        containerDataPlatformLakehouse -> containerDataPlatformDashboard "Provide curated data" "SQL/TCP"
    }
}
