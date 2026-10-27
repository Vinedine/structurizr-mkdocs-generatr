deploymentAcceptance = deploymentEnvironment "Acceptance" {

    deploymentNodeAcceptanceAzure = deploymentNode "Azure Cloud" {

        deploymentNode "West Europe" "" "Azure Region" {

            deploymentNode "rg-belfoot-acc" "" "Resource Group" {

                deploymentNode "app-services-acc" "" "Azure App Service (S1)" {
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

                deploymentNode "swa-acc" "" "Azure Static Web Apps (Standard)" {
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

                deploymentNode "psql-acc" "" "Azure Database for PostgreSQL (General Purpose D2s)" {
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

                deploymentNode "cosmos-acc" "" "Azure Cosmos DB (Provisioned)" {
                    containerInstance containerFanEngagementPlatformDatabase
                }

                deploymentNode "sb-acc" "" "Azure Service Bus (Standard)" {
                    containerInstance containerIntegrationPlatformServiceBus
                }

                deploymentNode "adf-acc" "" "Azure Data Factory (Managed)" {
                    containerInstance containerDataPlatformEtl
                }

                deploymentNode "dbw-acc" "" "Azure Databricks (Premium)" {
                    containerInstance containerDataPlatformLakehouse
                }

                deploymentNode "pbi-acc" "" "Power BI Service (Premium Per User)" {
                    containerInstance containerDataPlatformBiDashboard
                }

                deploymentNode "ai-foundry-acc" "" "Azure AI Foundry (Standard)" {
                    containerInstance containerAzureAiFoundryStudio
                    containerInstance containerAzureAiFoundryInferenceApi
                }

                deploymentNode "entra-id-acc" "" "Microsoft Entra ID" {
                    containerInstance containerMicrosoftEntraIdApi
                }
            }
        }
    }
}
