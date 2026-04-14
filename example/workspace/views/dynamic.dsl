dynamic softwareSystemTicketingPlatform "PurchaseTicket" {
    title "Fan Purchases a Match Ticket"
    userFan -> containerTicketingPlatformUi "Browse available matches and select seats"
    containerTicketingPlatformUi -> softwareSystemMicrosoftEntraId "Authenticate fan"
    containerTicketingPlatformUi -> containerTicketingPlatformApi "Submit ticket purchase"
    containerTicketingPlatformApi -> containerStripeApi "Process payment"
    containerTicketingPlatformApi -> containerTicketingPlatformDatabase "Store ticket record"
    containerTicketingPlatformApi -> containerSalesforceCrmApi "Update customer purchase history"
    containerTicketingPlatformApi -> containerIntegrationPlatformServiceBus "Publish ticket purchase event"
    autoLayout
}

dynamic softwareSystemStadiumManagement "GamedayFlow" {
    title "Gameday Stadium Operations"
    containerStadiumManagementIoTHub -> containerStadiumManagementApi "Send turnstile and crowd sensor data"
    containerStadiumManagementApi -> containerAzureAiFoundryApi "Predict crowd density for safety zones"
    userStadiumOperator -> containerStadiumManagementUi "Monitor crowd levels and facility status"
    containerStadiumManagementUi -> containerStadiumManagementApi "Get real-time facility data"
    userFan -> containerCashlessPaymentApp "Pay for food and drinks"
    containerCashlessPaymentApp -> containerCashlessPaymentApi "Process in-stadium payment"
    containerCashlessPaymentApi -> containerStripeApi "Settle payment transaction"
    autoLayout
}

dynamic softwareSystemDataPlatform "DataIngestionFlow" {
    title "Event-Driven Data Ingestion to Lakehouse"
    containerTicketingPlatformApi -> containerIntegrationPlatformServiceBus "Publish ticket events"
    containerWebStoreApi -> containerIntegrationPlatformServiceBus "Publish order events"
    containerCashlessPaymentApi -> containerIntegrationPlatformServiceBus "Publish transaction events"
    containerIntegrationPlatformServiceBus -> containerDataPlatformEtl "Route events for ingestion"
    containerDataPlatformEtl -> containerDatabricksUnityCatalog "Load transformed data"
    containerDataPlatformLakehouse -> containerDatabricksUnityCatalog "Read curated data products"
    userDataAnalyst -> containerDataPlatformDashboard "View business intelligence reports"
    containerDataPlatformDashboard -> containerDataPlatformLakehouse "Query curated data"
    autoLayout
}

dynamic softwareSystemPlayerPerformance "InjuryRiskPrediction" {
    title "AI-Driven Injury Risk Prediction"
    containerPlayerPerformanceApi -> containerPlayerPerformanceDatabase "Get historical training and fitness data"
    containerPlayerPerformanceApi -> containerDatabricksWorkspace "Query aggregated performance metrics"
    containerPlayerPerformanceApi -> containerAzureAiFoundryApi "Run injury risk prediction model"
    userHeadCoach -> containerPlayerPerformanceDashboard "View injury risk scores and recommendations"
    containerPlayerPerformanceDashboard -> containerPlayerPerformanceApi "Get prediction results"
    autoLayout
}
