deploymentDevelopment = deploymentEnvironment "Development" {

    deploymentNodeDevelopmentAzure = deploymentNode "Azure Cloud" {

        deploymentNode "West Europe" "" "Azure Region" {

            deploymentNode "rg-belfoot-dev" "" "Resource Group" {

                deploymentNode "app-services-dev" "" "Azure App Service (B1)" {
                    containerInstance containerTicketingPlatformApi
                    containerInstance containerWebStoreApi
                    containerInstance containerFanEngagementApi
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
                    containerInstance containerExternalRelationsApi
                }

                deploymentNode "swa-dev" "" "Azure Static Web Apps (Free)" {
                    containerInstance containerTicketingPlatformUi
                    containerInstance containerWebStoreUi
                    containerInstance containerSponsorshipPortalUi
                    containerInstance containerFanEngagementApp
                    containerInstance containerCashlessPaymentApp
                    containerInstance containerLogisticsPlannerUi
                    containerInstance containerStadiumManagementUi
                    containerInstance containerHrPortalUi
                    containerInstance containerComplianceManagerUi
                    containerInstance containerMatchdayOperationsUi
                    containerInstance containerProductDevelopmentUi
                    containerInstance containerMarketingPlatformUi
                    containerInstance containerClubWebsiteUi
                    containerInstance containerStrategyPortalUi
                    containerInstance containerExternalRelationsUi
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
                    containerInstance containerExternalRelationsDatabase
                }

                deploymentNode "cosmos-dev" "" "Azure Cosmos DB (Serverless)" {
                    containerInstance containerFanEngagementDatabase
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
                    containerInstance containerDataPlatformDashboard
                }

                deploymentNode "ai-foundry-dev" "" "Azure AI Foundry (Basic)" {
                    containerInstance containerAzureAiFoundryStudio
                    containerInstance containerAzureAiFoundryApi
                }

                deploymentNode "entra-id-dev" "" "Microsoft Entra ID" {
                    containerInstance containerEntraIdApi
                }
            }
        }
    }
}
