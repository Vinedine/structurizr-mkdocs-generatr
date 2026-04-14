deploymentAcceptance = deploymentEnvironment "Acceptance" {

    deploymentNode "Azure Cloud" {

        deploymentNode "West Europe" "" "Azure Region" {

            deploymentNode "rg-belfoot-acc" "" "Resource Group" {

                deploymentNode "app-services-acc" "" "Azure App Service (S1)" {
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
                }

                deploymentNode "cosmos-acc" "" "Azure Cosmos DB (Provisioned)" {
                    containerInstance containerFanEngagementDatabase
                }

                deploymentNode "sb-acc" "" "Azure Service Bus (Standard)" {
                    containerInstance containerIntegrationPlatformServiceBus
                }
            }
        }
    }
}
