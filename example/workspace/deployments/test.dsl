deploymentTest = deploymentEnvironment "Test" {

    deploymentNode "Azure Cloud" {

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
                }

                deploymentNode "cosmos-tst" "" "Azure Cosmos DB (Serverless)" {
                    containerInstance containerFanEngagementDatabase
                }

                deploymentNode "sb-tst" "" "Azure Service Bus (Standard)" {
                    containerInstance containerIntegrationPlatformServiceBus
                }
            }
        }
    }
}
