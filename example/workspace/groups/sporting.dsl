groupSporting = group "Sporting" {

    softwareSystemPlayerPerformance = softwareSystem "Player Performance" "Training analytics, GPS tracking, and match statistics" {

        !docs ../../software-system-docs/sporting/playerPerformance

        containerPlayerPerformanceDatabase = container "Performance Database" "Training sessions, GPS data, match statistics, and fitness scores" "PostgreSQL" "DATASET" {
        }

        containerPlayerPerformanceApi = container "Player Performance API" "Training data ingestion, analytics, and performance reporting" "Python" "SERVICE" {
            properties {
                "Repository" "https://dev.azure.com/BelFoot/_git/player-performance-api"
            }
            this -> containerPlayerPerformanceDatabase "Manage data" "SQL/TCP"
        }

        containerPlayerPerformanceDashboard = container "Performance Dashboard" "Visual analytics for player fitness, load management, and match performance" "Power BI" "DASHBOARD" {
            userHeadCoach -> this "Review player performance and set training plans"
            this -> containerPlayerPerformanceApi "Get performance data" "JSON/HTTPS"
        }
    }

    softwareSystemMedicalRecords = softwareSystem "Medical Records" "Player health, injury tracking, and rehabilitation protocols" {

        !docs ../../software-system-docs/sporting/medicalRecords

        containerMedicalRecordsDatabase = container "Medical Database" "Player medical history, injuries, and rehabilitation plans" "PostgreSQL" "DATASET" {
        }

        containerMedicalRecordsApi = container "Medical Records API" "Injury logging, rehabilitation tracking, and medical clearance" "Python" "SERVICE" {
            properties {
                "Repository" "https://dev.azure.com/BelFoot/_git/medical-records-api"
            }
            this -> containerMedicalRecordsDatabase "Manage data" "SQL/TCP"
        }

        containerMedicalRecordsUi = container "Medical Records Portal" "Player health management and injury tracking interface" "React" "UI_ELEMENT" {
            properties {
            }
            userMedicalStaff -> this "Manage player medical records and rehabilitation"
            userHeadCoach -> this "View player availability status"
            this -> containerMedicalRecordsApi "Manage medical data" "JSON/HTTPS"
            this -> containerEntraIdApi "Authenticate" "JSON/HTTPS"
        }
    }

    softwareSystemYouthAcademy = softwareSystem "Youth Academy" "Scouting, youth player development, and talent tracking" {

        !docs ../../software-system-docs/sporting/youthAcademy

        containerYouthAcademyDatabase = container "Youth Academy Database" "Scout reports, youth players, development milestones, and contracts" "PostgreSQL" "DATASET" {
        }

        containerYouthAcademyApi = container "Youth Academy API" "Scouting workflow, player development tracking, and contract management" "Node.js" "SERVICE" {
            properties {
                "Repository" "https://dev.azure.com/BelFoot/_git/youth-academy-api"
            }
            this -> containerYouthAcademyDatabase "Manage data" "SQL/TCP"
        }

        containerYouthAcademyUi = container "Youth Academy Portal" "Scout reports, player profiles, and development tracking" "React" "UI_ELEMENT" {
            userYouthScout -> this "Submit scout reports and track youth talent"
            userHeadCoach -> this "Review youth player development"
            this -> containerYouthAcademyApi "Manage scouting data" "JSON/HTTPS"
            this -> containerEntraIdApi "Authenticate" "JSON/HTTPS"
        }
    }
}
