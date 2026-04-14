deploymentProduction = deploymentEnvironment "Production" {

    // ============================================================
    // On-Premise: Stadium Data Center
    // ============================================================

    deploymentNodeProductionOnPremise = deploymentNode "On-Premise" {

        deploymentNode "Stadium Data Center" "" "Co-located infrastructure" {

            deploymentNode "sql-prod-01" "" "Microsoft SQL Server" {
                containerInstance containerTicketingPlatformDatabase
                containerInstance containerStadiumManagementDatabase
            }

            deploymentNode "app-prod-01" "" "Windows Server / IIS" {
                containerInstance containerTicketingPlatformApi
                containerInstance containerStadiumManagementApi
                containerInstance containerMatchdayOperationsApi
            }

            deploymentNode "app-prod-02" "" "Windows Server / IIS" {
                containerInstance containerTicketingPlatformUi
                containerInstance containerStadiumManagementUi
                containerInstance containerMatchdayOperationsUi
            }

            deploymentNode "psql-prod-01" "" "PostgreSQL" {
                containerInstance containerMatchdayOperationsDatabase
            }

            deploymentNode "iot-gateway-01" "" "Azure IoT Edge" {
                containerInstance containerStadiumManagementIoTHub
            }
        }
    }

    // ============================================================
    // Azure Cloud: Digital Platform
    // ============================================================

    deploymentNodeProductionAzure = deploymentNode "Azure Cloud" {

        deploymentNode "West Europe" "" "Azure Region" {

            deploymentNode "rg-fan-digital-prd" "" "Resource Group" {

                deploymentNode "app-fan-engagement" "" "Azure App Service" {
                    containerInstance containerFanEngagementApi
                }

                deploymentNode "app-fan-engagement-app" "" "Azure Static Web Apps" {
                    containerInstance containerFanEngagementApp
                }

                deploymentNode "cosmos-fan-engagement" "" "Azure Cosmos DB" {
                    containerInstance containerFanEngagementDatabase
                }

                deploymentNode "app-webstore" "" "Azure App Service" {
                    containerInstance containerWebStoreApi
                }

                deploymentNode "swa-webstore" "" "Azure Static Web Apps" {
                    containerInstance containerWebStoreUi
                }

                deploymentNode "psql-webstore" "" "Azure Database for PostgreSQL" {
                    containerInstance containerWebStoreDatabase
                }

                deploymentNode "app-cashless" "" "Azure App Service" {
                    containerInstance containerCashlessPaymentApi
                }

                deploymentNode "swa-cashless" "" "Azure Static Web Apps" {
                    containerInstance containerCashlessPaymentApp
                }

                deploymentNode "app-club-website" "" "Azure App Service" {
                    containerInstance containerClubWebsiteCms
                }

                deploymentNode "swa-club-website" "" "Azure Static Web Apps" {
                    containerInstance containerClubWebsiteUi
                }

                deploymentNode "psql-club-website" "" "Azure Database for PostgreSQL" {
                    containerInstance containerClubWebsiteDatabase
                }
            }

            deploymentNode "rg-commercial-prd" "" "Resource Group" {

                deploymentNode "app-sponsorship" "" "Azure App Service" {
                    containerInstance containerSponsorshipPortalApi
                }

                deploymentNode "swa-sponsorship" "" "Azure Static Web Apps" {
                    containerInstance containerSponsorshipPortalUi
                }

                deploymentNode "psql-sponsorship" "" "Azure Database for PostgreSQL" {
                    containerInstance containerSponsorshipPortalDatabase
                }

                deploymentNode "app-logistics" "" "Azure App Service" {
                    containerInstance containerLogisticsPlannerApi
                }

                deploymentNode "swa-logistics" "" "Azure Static Web Apps" {
                    containerInstance containerLogisticsPlannerUi
                }

                deploymentNode "psql-logistics" "" "Azure Database for PostgreSQL" {
                    containerInstance containerLogisticsPlannerDatabase
                }

                deploymentNode "app-product-dev" "" "Azure App Service" {
                    containerInstance containerProductDevelopmentApi
                }

                deploymentNode "swa-product-dev" "" "Azure Static Web Apps" {
                    containerInstance containerProductDevelopmentUi
                }

                deploymentNode "psql-product-dev" "" "Azure Database for PostgreSQL" {
                    containerInstance containerProductDevelopmentDatabase
                }

                deploymentNode "app-marketing" "" "Azure App Service" {
                    containerInstance containerMarketingPlatformApi
                }

                deploymentNode "swa-marketing" "" "Azure Static Web Apps" {
                    containerInstance containerMarketingPlatformUi
                }

                deploymentNode "psql-marketing" "" "Azure Database for PostgreSQL" {
                    containerInstance containerMarketingPlatformDatabase
                }
            }

            deploymentNode "rg-corporate-prd" "" "Resource Group" {

                deploymentNode "app-hr" "" "Azure App Service" {
                    containerInstance containerHrPortalApi
                }

                deploymentNode "swa-hr" "" "Azure Static Web Apps" {
                    containerInstance containerHrPortalUi
                }

                deploymentNode "psql-hr" "" "Azure Database for PostgreSQL" {
                    containerInstance containerHrPortalDatabase
                }

                deploymentNode "app-compliance" "" "Azure App Service" {
                    containerInstance containerComplianceManagerApi
                }

                deploymentNode "swa-compliance" "" "Azure Static Web Apps" {
                    containerInstance containerComplianceManagerUi
                }

                deploymentNode "psql-compliance" "" "Azure Database for PostgreSQL" {
                    containerInstance containerComplianceManagerDatabase
                }

                deploymentNode "app-strategy" "" "Azure App Service" {
                    containerInstance containerStrategyPortalApi
                }

                deploymentNode "swa-strategy" "" "Azure Static Web Apps" {
                    containerInstance containerStrategyPortalUi
                }

                deploymentNode "psql-strategy" "" "Azure Database for PostgreSQL" {
                    containerInstance containerStrategyPortalDatabase
                }

                deploymentNode "app-external-relations" "" "Azure App Service" {
                    containerInstance containerExternalRelationsApi
                }

                deploymentNode "swa-external-relations" "" "Azure Static Web Apps" {
                    containerInstance containerExternalRelationsUi
                }

                deploymentNode "psql-external-relations" "" "Azure Database for PostgreSQL" {
                    containerInstance containerExternalRelationsDatabase
                }
            }

            deploymentNode "rg-data-platform-prd" "" "Resource Group" {

                deploymentNode "adf-data-platform" "" "Azure Data Factory" {
                    containerInstance containerDataPlatformEtl
                }

                deploymentNode "dbw-data-platform" "" "Azure Databricks" {
                    containerInstance containerDataPlatformLakehouse
                }

                deploymentNode "pbi-data-platform" "" "Power BI Service" {
                    containerInstance containerDataPlatformDashboard
                }

                deploymentNode "sb-integration" "" "Azure Service Bus" {
                    containerInstance containerIntegrationPlatformServiceBus
                }

                deploymentNode "func-integration" "" "Azure Functions" {
                    containerInstance containerIntegrationPlatformApi
                }
            }

            deploymentNode "rg-ai-prd" "" "Resource Group" {

                deploymentNode "ai-foundry" "" "Azure AI Foundry" {
                    containerInstance containerAzureAiFoundryStudio
                    containerInstance containerAzureAiFoundryApi
                }
            }

            deploymentNode "rg-identity-prd" "" "Resource Group" {

                deploymentNode "entra-id" "" "Microsoft Entra ID" {
                    containerInstance containerEntraIdApi
                }
            }
        }
    }

    // ============================================================
    // AWS Cloud: Sporting Analytics
    // ============================================================

    deploymentNodeProductionAws = deploymentNode "AWS Cloud" {

        deploymentNode "eu-west-1" "" "AWS Region" {

            deploymentNode "ecs-sporting-analytics" "" "Amazon ECS Fargate" {
                containerInstance containerPlayerPerformanceApi
                containerInstance containerMedicalRecordsApi
                containerInstance containerYouthAcademyApi
            }

            deploymentNode "rds-sporting" "" "Amazon RDS PostgreSQL" {
                containerInstance containerPlayerPerformanceDatabase
                containerInstance containerMedicalRecordsDatabase
                containerInstance containerYouthAcademyDatabase
            }

            deploymentNode "grafana-sporting" "" "Amazon Managed Grafana" {
                containerInstance containerPlayerPerformanceDashboard
            }

            deploymentNode "ecs-sporting-ui" "" "Amazon ECS Fargate" {
                containerInstance containerMedicalRecordsUi
                containerInstance containerYouthAcademyUi
            }
        }
    }

    // ============================================================
    // SaaS: External Systems
    // ============================================================

    deploymentNode "Salesforce Cloud" {

        deploymentNode "Salesforce EU" "" "Salesforce Platform" {
            containerInstance containerSalesforceCrmUi
            containerInstance containerSalesforceCrmApi
        }
    }

    deploymentNode "Stripe Cloud" {

        deploymentNode "Stripe EU" "" "Stripe Platform" {
            containerInstance containerStripeApi
        }
    }

    deploymentNode "SAP Cloud" {

        deploymentNode "SAP EU" "" "SAP S/4HANA Cloud" {
            containerInstance containerSapS4HanaUi
            containerInstance containerSapS4HanaApi
            containerInstance containerSapS4HanaDatabase
        }
    }

    deploymentNode "Databricks Cloud" {

        deploymentNode "Databricks EU" "" "Databricks Platform" {
            containerInstance containerDatabricksWorkspace
            containerInstance containerDatabricksUnityCatalog
        }
    }
}
