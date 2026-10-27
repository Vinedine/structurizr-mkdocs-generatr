deploymentDevelopment = deploymentEnvironment "Development" {

    deploymentNodeDevelopmentAzure = deploymentNode "Azure Cloud" {

        deploymentNode "West Europe" "" "Azure Region" {

            deploymentNode "rg-belfoot-dev" "" "Resource Group" {

                deploymentNode "app-services-dev" "" "Azure App Service (B1)" {
                    containerInstance containerTicketingPlatformApi
                    containerInstance containerWebStoreApi
                    containerInstance containerFanEngagementPlatformApi
                    containerInstance containerSponsorshipPortalApi
                    containerInstance containerCashlessPaymentApi
                    containerInstance containerLogisticsPlannerApi
                    containerInstance containerStadiumManagementApi
                    containerInstance containerHrPortalApi
                    containerInstance containerComplianceManagerApi
                    containerInstance containerPlayerPerformanceApi
                    containerInstance containerMedicalRecordsApi
                    containerInstance containerYouthAcademyApi
                    containerInstance containerIntegrationPlatformApi
                    containerInstance containerMatchdayOperationsApi
                    containerInstance containerProductDevelopmentApi
                    containerInstance containerMarketingPlatformApi
                    containerInstance containerClubWebsiteCms
                    containerInstance containerStrategyPortalApi
                    containerInstance containerExternalRelationsPortalApi
                }

                deploymentNode "swa-dev" "" "Azure Static Web Apps (Free)" {
                    containerInstance containerTicketingPlatformPortal
                    containerInstance containerWebStoreStorefront
                    containerInstance containerSponsorshipPortalWebApp
                    containerInstance containerFanEngagementPlatformMobileApp
                    containerInstance containerCashlessPaymentApp
                    containerInstance containerLogisticsPlannerPortal
                    containerInstance containerStadiumManagementOperationsDashboard
                    containerInstance containerHrPortalWebApp
                    containerInstance containerComplianceManagerPortal
                    containerInstance containerMatchdayOperationsUi
                    containerInstance containerProductDevelopmentUi
                    containerInstance containerMarketingPlatformPortal
                    containerInstance containerClubWebsiteFrontend
                    containerInstance containerStrategyPortalWebApp
                    containerInstance containerExternalRelationsPortalWebApp
                    containerInstance containerMedicalRecordsUi
                    containerInstance containerYouthAcademyUi
                    containerInstance containerPlayerPerformanceDashboard
                }

                deploymentNode "psql-dev" "" "Azure Database for PostgreSQL (Burstable B1ms)" {
                    containerInstance containerTicketingPlatformDatabase
                    containerInstance containerWebStoreDatabase
                    containerInstance containerSponsorshipPortalDatabase
                    containerInstance containerLogisticsPlannerDatabase
                    containerInstance containerStadiumManagementDatabase
                    containerInstance containerHrPortalDatabase
                    containerInstance containerComplianceManagerDatabase
                    containerInstance containerPlayerPerformanceDatabase
                    containerInstance containerMedicalRecordsDatabase
                    containerInstance containerYouthAcademyDatabase
                    containerInstance containerMatchdayOperationsDatabase
                    containerInstance containerProductDevelopmentDatabase
                    containerInstance containerMarketingPlatformDatabase
                    containerInstance containerClubWebsiteDatabase
                    containerInstance containerStrategyPortalDatabase
                    containerInstance containerExternalRelationsPortalDatabase
                }

                deploymentNode "cosmos-dev" "" "Azure Cosmos DB (Serverless)" {
                    containerInstance containerFanEngagementPlatformDatabase
                }

                deploymentNode "sb-dev" "" "Azure Service Bus (Basic)" {
                    containerInstance containerIntegrationPlatformServiceBus
                }

                deploymentNode "adf-dev" "" "Azure Data Factory (Managed)" {
                    containerInstance containerDataPlatformEtl
                }

                deploymentNode "dbw-dev" "" "Azure Databricks (Standard)" {
                    containerInstance containerDataPlatformLakehouse
                }

                deploymentNode "pbi-dev" "" "Power BI Service (Pro)" {
                    containerInstance containerDataPlatformBiDashboard
                }

                deploymentNode "ai-foundry-dev" "" "Azure AI Foundry (Basic)" {
                    containerInstance containerAzureAiFoundryStudio
                    containerInstance containerAzureAiFoundryInferenceApi
                }

                deploymentNode "entra-id-dev" "" "Microsoft Entra ID" {
                    containerInstance containerMicrosoftEntraIdApi
                }
            }
        }
    }
}
