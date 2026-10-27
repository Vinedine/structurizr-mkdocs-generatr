groupCorporate = group "Corporate" {

    softwareSystemSapS4Hana = softwareSystem "SAP S4HANA" "Enterprise Resource Planning for finance, procurement, and HR" "External System" {

        !docs ../../software-system-docs/corporate/sapS4Hana

        containerSapS4HanaFioriLaunchpad = container "SAP S4HANA Fiori Launchpad" "Self-service portal for finance, procurement, and HR users" "SAP Fiori" "CLOUD_RESOURCE" {
            userHrManager -> this "Manage employee master data"
            userFinanceController -> this "Review financial reports"
            userMerchandisingManager -> this "Manage inventory levels"
        }

        containerSapS4HanaApi = container "SAP S4HANA API" "OData APIs for finance, materials, and HR data" "SAP OData" "SERVICE" {
        }

        containerSapS4HanaDatabase = container "SAP S4HANA Database" "Central ERP data store" "SAP HANA" "DATASET" {
        }

        containerSapS4HanaFioriLaunchpad -> containerSapS4HanaApi "Manage data" "OData/HTTPS"
        containerSapS4HanaApi -> containerSapS4HanaDatabase "Read and write data" "SQL/TCP"
    }

    softwareSystemHrPortal = softwareSystem "HR Portal" "Staff recruitment, onboarding, and payroll integration" {

        !docs ../../software-system-docs/corporate/hrPortal

        containerHrPortalDatabase = container "HR Portal Database" "Employees, contracts, recruitment pipelines, and volunteer records" "PostgreSQL" "DATASET" {
        }

        containerHrPortalApi = container "HR Portal API" "Employee management, recruitment workflow, and payroll sync" ".NET" "SERVICE" {
            properties {
                "Repository" "https://dev.azure.com/BelFoot/_git/hr-portal-api"
            }
            this -> containerHrPortalDatabase "Manage data" "SQL/TCP"
        }

        containerHrPortalWebApp = container "HR Portal Web App" "Staff management, recruitment, and volunteer coordination" "React" "UI_ELEMENT" {
            userHrManager -> this "Manage staff recruitment and onboarding"
            this -> containerHrPortalApi "Manage HR data" "JSON/HTTPS"
            this -> containerMicrosoftEntraIdApi "Authenticate" "JSON/HTTPS"
        }
    }

    softwareSystemComplianceManager = softwareSystem "Compliance Manager" "Risk registers, ethical governance, and legal case tracking" {

        !docs ../../software-system-docs/corporate/complianceManager

        containerComplianceManagerDatabase = container "Compliance Manager Database" "Risk registers, audit trails, legal cases, and policy documents" "PostgreSQL" "DATASET" {
        }

        containerComplianceManagerApi = container "Compliance Manager API" "Risk assessment, audit management, and legal case workflow" ".NET" "SERVICE" {
            properties {
                "Repository" "https://dev.azure.com/BelFoot/_git/compliance-api"
            }
            this -> containerComplianceManagerDatabase "Manage data" "SQL/TCP"
        }

        containerComplianceManagerPortal = container "Compliance Manager Portal" "Risk management, compliance tracking, and legal case management" "React" "UI_ELEMENT" {
            userComplianceOfficer -> this "Manage risk registers and compliance audits"
            userFinanceController -> this "Review audit findings"
            this -> containerComplianceManagerApi "Manage compliance data" "JSON/HTTPS"
            this -> containerMicrosoftEntraIdApi "Authenticate" "JSON/HTTPS"
        }
    }

    softwareSystemStrategyPortal = softwareSystem "Strategy Portal" "Club strategy, innovation, and portfolio management" {

        !docs ../../software-system-docs/corporate/strategyPortal

        containerStrategyPortalDatabase = container "Strategy Portal Database" "Strategic plans, trend reports, innovation proposals, and portfolio items" "PostgreSQL" "DATASET" {
        }

        containerStrategyPortalApi = container "Strategy Portal API" "Strategy planning, trend analysis, and portfolio management" ".NET" "SERVICE" {
            properties {
                "Repository" "https://dev.azure.com/BelFoot/_git/strategy-portal-api"
            }
            this -> containerStrategyPortalDatabase "Manage data" "SQL/TCP"
        }

        containerStrategyPortalWebApp = container "Strategy Portal Web App" "Strategic planning, innovation tracking, and portfolio overview" "React" "UI_ELEMENT" {
            userStrategyDirector -> this "Define strategy and manage portfolio"
            userFinanceController -> this "Review portfolio financials"
            this -> containerStrategyPortalApi "Manage strategy data" "JSON/HTTPS"
            this -> containerMicrosoftEntraIdApi "Authenticate" "JSON/HTTPS"
        }
    }

    softwareSystemExternalRelations = softwareSystem "External Relations Portal" "Press, federation, and stakeholder relationship management" {

        !docs ../../software-system-docs/corporate/externalRelations

        containerExternalRelationsPortalDatabase = container "External Relations Portal Database" "Press releases, stakeholders, federation memberships, and community programs" "PostgreSQL" "DATASET" {
        }

        containerExternalRelationsPortalApi = container "External Relations Portal API" "Press management, stakeholder tracking, and community program coordination" ".NET" "SERVICE" {
            properties {
                "Repository" "https://dev.azure.com/BelFoot/_git/external-relations-api"
            }
            this -> containerExternalRelationsPortalDatabase "Manage data" "SQL/TCP"
        }

        containerExternalRelationsPortalWebApp = container "External Relations Portal Web App" "Press releases, stakeholder management, and community programs" "React" "UI_ELEMENT" {
            userCommunicationsManager -> this "Manage press and stakeholder relations"
            this -> containerExternalRelationsPortalApi "Manage relations data" "JSON/HTTPS"
            this -> containerMicrosoftEntraIdApi "Authenticate" "JSON/HTTPS"
        }
    }
}
