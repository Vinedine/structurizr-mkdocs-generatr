!!! note "Quick Summary"

    BelFoot FC runs a multi-cloud deployment: latency-critical gameday systems on-premise, core business on Azure, sporting analytics on AWS. Deployment views show exactly where every container runs per environment.

## Production Deployment

Production runs across three infrastructure zones. Each zone exists for a specific reason -- not because multi-cloud is trendy, but because the workloads demand it.

=== "On-Premise — Stadium Data Center"

    Ticketing terminals, access control, IoT sensors, and stadium management. These systems cannot tolerate cloud round-trips during a match.

    ![Production — On-Premise](embed:DeploymentProductionOnPremise)

=== "Azure Cloud"

    Digital fan platform, data platform, integration backbone, corporate systems, and identity management. Azure hosts the majority of the IT landscape.

    ![Production — Azure](embed:DeploymentProductionAzure)

=== "AWS Cloud"

    Sporting analytics, player performance tracking, and medical records. Leverages the AWS sports analytics ecosystem for specialized ML workloads.

    ![Production — AWS](embed:DeploymentProductionAws)

## All Environments

Each environment has its own deployment view with zone-level detail -- see the full breakdown in [Infrastructure](../infrastructure/index.md).

!!! warning "The Gap Operations Teams Face"

    C4 diagrams show architects and developers how software is structured. But operations teams need a different view: *where does this actually run, and what depends on what?*

    Without deployment views, this information lives in spreadsheets, Terraform configs, or tribal knowledge. With deployment views in the architecture model, infrastructure is documented alongside the software it runs -- always in sync, always reviewable.
