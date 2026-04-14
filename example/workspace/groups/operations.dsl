groupOperations = group "Operations" {

    softwareSystemStadiumManagement = softwareSystem "Stadium Management" "Facility operations, access control, and IoT monitoring" {

        !docs ../../software-system-docs/operations/stadiumManagement

        containerStadiumManagementDatabase = container "Stadium Database" "Venues, zones, maintenance requests, and sensor readings" "Microsoft SQL Server" "DATASET" {
        }

        containerStadiumManagementApi = container "Stadium Management API" "Facility booking, access control, and maintenance management" ".NET" "SERVICE" {
            properties {
                "Repository" "https://dev.azure.com/BelFoot/_git/stadium-management-api"
            }
            this -> containerStadiumManagementDatabase "Manage data" "SQL/TCP"
        }

        containerStadiumManagementIoTHub = container "Stadium IoT Hub" "Collects sensor data from turnstiles, HVAC, and crowd counters" "Azure IoT Hub" "CLOUD_RESOURCE" {
            this -> containerStadiumManagementApi "Send sensor telemetry" "AMQP/TCP"
        }

        containerStadiumManagementUi = container "Stadium Operations Dashboard" "Real-time facility monitoring and gameday operations" "React" "UI_ELEMENT" {
            userStadiumOperator -> this "Monitor facilities and manage gameday operations"
            this -> containerStadiumManagementApi "Manage operations" "JSON/HTTPS"
            this -> containerEntraIdApi "Authenticate" "JSON/HTTPS"
        }
    }

    softwareSystemCashlessPayment = softwareSystem "Cashless Payment" "Contactless in-stadium payments for food, drinks, and merchandise" {

        !docs ../../software-system-docs/operations/cashlessPayment

        containerCashlessPaymentApi = container "Cashless Payment API" "Wallet top-up, balance management, and transaction processing" "Node.js" "SERVICE" {
            properties {
                "Repository" "https://dev.azure.com/BelFoot/_git/cashless-payment-api"
            }
        }

        containerCashlessPaymentApp = container "Cashless Payment App" "NFC-enabled in-stadium payment terminal app" "Kotlin" "APPLICATION" {
            userFan -> this "Pay for food and drinks at the stadium"
            userStadiumOperator -> this "Process in-stadium transactions"
            this -> containerCashlessPaymentApi "Process payments" "JSON/HTTPS"
        }
    }

    softwareSystemLogisticsPlanner = softwareSystem "Logistics Planner" "Procurement, supplier management, and inbound logistics" {

        !docs ../../software-system-docs/operations/logisticsPlanner

        containerLogisticsPlannerDatabase = container "Logistics Database" "Suppliers, purchase orders, and delivery schedules" "PostgreSQL" "DATASET" {
        }

        containerLogisticsPlannerApi = container "Logistics API" "Supplier onboarding, purchase order management, and delivery tracking" ".NET" "SERVICE" {
            properties {
                "Repository" "https://dev.azure.com/BelFoot/_git/logistics-api"
            }
            this -> containerLogisticsPlannerDatabase "Manage data" "SQL/TCP"
        }

        containerLogisticsPlannerUi = container "Logistics Portal" "Supplier and procurement management interface" "Angular" "UI_ELEMENT" {
            userMerchandisingManager -> this "Manage suppliers and purchase orders"
            this -> containerLogisticsPlannerApi "Manage logistics" "JSON/HTTPS"
            this -> containerEntraIdApi "Authenticate" "JSON/HTTPS"
        }
    }

    softwareSystemMatchdayOperations = softwareSystem "Matchday Operations" "Gameday planning, security, access control, and away match coordination" {

        !docs ../../software-system-docs/operations/matchdayOperations

        containerMatchdayOperationsDatabase = container "Matchday Database" "Matchday plans, security deployments, access badges, and away trips" "PostgreSQL" "DATASET" {
        }

        containerMatchdayOperationsApi = container "Matchday Operations API" "Gameday coordination, security management, and access control" ".NET" "SERVICE" {
            properties {
                "Repository" "https://dev.azure.com/BelFoot/_git/matchday-operations-api"
            }
            this -> containerMatchdayOperationsDatabase "Manage data" "SQL/TCP"
        }

        containerMatchdayOperationsUi = container "Matchday Operations Dashboard" "Gameday planning, security coordination, and access monitoring" "React" "UI_ELEMENT" {
            userMatchdayDirector -> this "Plan and coordinate matchday operations"
            userStadiumOperator -> this "Monitor access control and crowd safety"
            this -> containerMatchdayOperationsApi "Manage operations" "JSON/HTTPS"
            this -> containerEntraIdApi "Authenticate" "JSON/HTTPS"
        }
    }
}
