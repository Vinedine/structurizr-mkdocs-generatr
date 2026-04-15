deploymentTest = deploymentEnvironment "Test" {

    deploymentNodeTestAzure = deploymentNode "Azure Cloud" {

        deploymentNode "West Europe" "" "Azure Region" {

            deploymentNode "rg-belfoot-tst" "" "Resource Group" {

                deploymentNode "app-services-tst" "" "Azure App Service (B2)" {
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

                deploymentNode "swa-tst" "" "Azure Static Web Apps (Free)" {
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

                deploymentNode "psql-tst" "" "Azure Database for PostgreSQL (Burstable B2s)" {
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

                deploymentNode "cosmos-tst" "" "Azure Cosmos DB (Serverless)" {
                    containerInstance containerFanEngagementDatabase
                }

                deploymentNode "sb-tst" "" "Azure Service Bus (Standard)" {
                    containerInstance containerIntegrationPlatformServiceBus
                }

                deploymentNode "adf-tst" "" "Azure Data Factory (Managed)" {
                    containerInstance containerDataPlatformEtl
                }

                deploymentNode "dbw-tst" "" "Azure Databricks (Standard)" {
                    containerInstance containerDataPlatformLakehouse
                }

                deploymentNode "pbi-tst" "" "Power BI Service (Pro)" {
                    containerInstance containerDataPlatformDashboard
                }

                deploymentNode "ai-foundry-tst" "" "Azure AI Foundry (Basic)" {
                    containerInstance containerAzureAiFoundryStudio
                    containerInstance containerAzureAiFoundryApi
                }

                deploymentNode "entra-id-tst" "" "Microsoft Entra ID" {
                    containerInstance containerEntraIdApi
                }
            }
        }
    }
}
