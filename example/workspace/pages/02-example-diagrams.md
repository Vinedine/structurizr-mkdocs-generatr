## Introduction

Every diagram below is auto-generated from a single architecture model. Nothing is drawn by hand -- update the model and every view updates with it. Click any diagram to zoom in.

=== "Landscape & Actor Views"

    ### System Landscape

    Shows all software systems and how actors interact with them, scoped to a single organizational group.

    ![System Landscape - Commercial](embed:SystemLandscapeCommercial)

    ### Actor View

    Shows the systems a specific actor interacts with -- in this case from the fan's perspective.

    ![Fan Perspective](embed:SystemLandscapeUserFan)

=== "System & Container Views"

    ### Software System Context

    Zooms into a single software system, showing its users and the other systems it depends on or integrates with.

    ![Cashless Payment - System Context](embed:SystemContextCashlessPayment)

    ### Container View

    Breaks a system open to reveal its internal building blocks: APIs, databases, frontends, message queues.

    ![Player Performance - Containers](embed:ContainerPlayerPerformance)

=== "Dynamic & Deployment Views"

    ### Dynamic View

    Animates a specific workflow step by step, showing how containers collaborate at runtime to fulfill a use case.

    ![AI-Driven Injury Risk Prediction](embed:InjuryRiskPrediction)

    ### Deployment View

    Maps containers onto real infrastructure (cloud regions, resource groups, app services) per environment.

    ![Production Deployment - AWS](embed:DeploymentProductionAws)

!!! info "How Diagrams Are Generated"

    Diagrams are defined in the Structurizr DSL workspace and exported as C4 PlantUML, then rendered to clickable SVG. You can also embed diagrams inline in any documentation page using `embed:ViewKey` syntax. See [Documentation Features](07-documentation-features.md) for details.
