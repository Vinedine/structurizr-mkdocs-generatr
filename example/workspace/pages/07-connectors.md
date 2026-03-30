## Tool & Cloud Connectors

Architecture is most valuable when it flows into the tools your teams already use. This framework supports pushing architecture data to developer portals and pulling live deployment information from cloud providers.

### Developer Portal Integration

Architecture data defined in Structurizr DSL can be synchronized to developer portals, giving teams a single source of truth without maintaining documentation in multiple places.

**Supported portals:**

- **Atlassian Compass** -- Push software system and container metadata as components. Teams see architecture context directly in their Compass catalog alongside CI/CD and incident data.
- **Backstage** -- Export system and API definitions as Backstage catalog entities. Developers discover services and their dependencies through the portal they already use.
- **Port** -- Publish architecture entities as Port blueprints. Map software systems, containers, and deployment environments into Port's internal developer platform.

### Cloud Provider Integration

Pull live infrastructure data from cloud providers to keep deployment views accurate and detect drift between documented architecture and actual state.

**Supported providers:**

- **Microsoft Azure** -- Query resource groups, App Services, Azure Functions, databases, and networking via Azure Resource Manager APIs. Compare what is deployed against what the architecture model describes.
- **Amazon Web Services** -- Discover EC2 instances, ECS services, RDS databases, and Lambda functions. Map discovered resources back to containers in the C4 model.
- **Google Cloud Platform** -- Retrieve Cloud Run services, GKE clusters, Cloud SQL instances, and related infrastructure.

### How It Works

Connectors run as part of the CI/CD pipeline or on-demand. They read the parsed workspace model and translate it into the target platform's format:

1. **Export** -- Structurizr DSL is parsed into a workspace model
2. **Transform** -- Software systems, containers, and relationships are mapped to the target platform's entity model
3. **Sync** -- Entities are created or updated in the target platform via its API
4. **Drift detection** -- For cloud providers, discovered resources are compared against the architecture model and differences are flagged

This keeps architecture documentation aligned with both the developer portal and the actual cloud infrastructure.
