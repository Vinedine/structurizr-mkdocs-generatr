deploymentTest = deploymentEnvironment "Test" {

    deploymentNodeTestAzure = deploymentNode "Azure Cloud" {

        deploymentNode "West Europe" "" "Azure Region" {

            deploymentNode "rg-belfoot-tst" "" "Resource Group" {

                deploymentNode "app-services-tst" "" "Azure App Service (B2)" {
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

                deploymentNode "swa-tst" "" "Azure Static Web Apps (Free)" {
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
                    containerInstance containerExternalRelationsPortalDatabase
                }

                deploymentNode "cosmos-tst" "" "Azure Cosmos DB (Serverless)" {
                    containerInstance containerFanEngagementPlatformDatabase
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
                    containerInstance containerDataPlatformBiDashboard
                }

                deploymentNode "ai-foundry-tst" "" "Azure AI Foundry (Basic)" {
                    containerInstance containerAzureAiFoundryStudio
                    containerInstance containerAzureAiFoundryInferenceApi
                }

                deploymentNode "entra-id-tst" "" "Microsoft Entra ID" {
                    containerInstance containerMicrosoftEntraIdApi
                }
            }
        }
    }
}
