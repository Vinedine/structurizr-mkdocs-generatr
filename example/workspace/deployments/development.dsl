deploymentDevelopment = deploymentEnvironment "Development" {

    deploymentNode "Azure Cloud" {

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
                }

                deploymentNode "cosmos-dev" "" "Azure Cosmos DB (Serverless)" {
                    containerInstance containerFanEngagementDatabase
                }

                deploymentNode "sb-dev" "" "Azure Service Bus (Basic)" {
                    containerInstance containerIntegrationPlatformServiceBus
                }
            }
        }
    }
}
