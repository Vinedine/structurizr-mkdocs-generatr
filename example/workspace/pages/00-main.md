## Welcome to the BelFoot FC IT Landscape

This is a **living architecture website** -- every diagram, system description, and decision record is auto-generated from version-controlled code. Built with [structurizr-mkdocs-generatr](https://github.com/xxx/structurizr-mkdocs-generatr), powered by the [C4 Model](https://c4model.com/) and [MkDocs Material](https://squidfundry.github.io/mkdocs-material/).

## From Business Strategy to Infrastructure -- One Connected Model

Most architecture tools stop at software diagrams. This framework goes further. It connects **business capabilities** to **bounded contexts** to **C4 software systems** to **deployment infrastructure** -- all in a single model, all generated from code.

```mermaid
flowchart LR
    A["Business Capabilities"] --> B["Bounded Contexts"]
    B --> C["C4 Software Systems"]
    C --> D["Infrastructure & Deployment"]

    style A fill:#4CAF50,color:#fff
    style B fill:#2196F3,color:#fff
    style C fill:#438DD5,color:#fff
    style D fill:#FF9800,color:#fff
```

<div class="grid cards" markdown>

- :material-strategy: **Business Capabilities**

    ---

    Define what your organization does -- the strategic business capabilities that drive value. Map them to the software systems that support them.

- :material-domain: **Bounded Contexts**

    ---

    Model business domains with their entities and relationships. See how data flows across domain boundaries.

- :material-sitemap: **C4 Architecture**

    ---

    Software systems, containers, and components at every zoom level -- from landscape overview to container internals.

- :material-server-network: **Infrastructure & Deployment**

    ---

    Map containers onto real infrastructure per environment -- on-premise, Azure, AWS, multi-cloud.

- :material-connection: **Tool & Cloud Connectors**

    ---

    Push architecture data to developer portals like Atlassian Compass and Backstage, or pull live deployment info from Azure, AWS, and GCP.

- :material-robot-outline: **AI-Powered Automation**

    ---

    Claude AI skills retrieve code from Git and Azure DevOps to auto-generate architecture, validate changes, audit entities, and create technical documentation.

</div>

:material-arrow-right: Learn more: [Capabilities & Bounded Contexts](documentation/01-capabilities-and-contexts.md) | [Architecture Decisions](documentation/03-architecture-decisions.md) | [Infrastructure & Deployment](documentation/05-infrastructure.md)

## Who Is This For?

=== "For Technical Teams"

    You define your architecture once in [Structurizr DSL](https://docs.structurizr.com/dsl/language) and get a fully navigable website with:

    - **Auto-generated C4 diagrams** at every level -- landscape, context, container, component, deployment
    - **Bounded contexts and business capability maps** linking business domains to software systems
    - **Deployment views per environment** -- see exactly where containers run across clouds and on-premise
    - **Git-based governance** -- every change goes through branch, pull request, review, merge, auto-deploy
    - **Architecture Decision Records** tracking every strategic decision with full context
    - **Tool connectors** pushing data to Atlassian Compass, Backstage, or Port, and pulling from Azure, AWS, GCP
    - **AI automation** with Claude Code skills that generate architecture from Git repos and Azure DevOps

    :material-arrow-right: See [Example Diagrams](documentation/02-example-diagrams.md) to see what gets generated. | [C4 Model](documentation/04-c4-model.md) for the theory.

=== "For Business Leaders"

    Most organizations cannot confidently answer *"what do we have, and how does it fit together?"* This framework changes that:

    - **Business capabilities mapped to IT systems** -- see which software supports which part of the business
    - **Bounded contexts reveal domain complexity** -- understand how data flows between business areas
    - **Impact analysis before any change** -- trace from a business capability down to the infrastructure that runs it
    - **Architecture decisions are transparent** -- every strategic choice is documented with context and consequences
    - **Documentation stays current by design** -- generated from the same code that defines the architecture

    :material-arrow-right: See [How It Works](documentation/06-how-it-works.md) to understand the approach.

!!! info "About This Reference Case"

    BelFoot FC is a fictional football club created by [Jonas Van Riel](https://www.linkedin.com/in/jonasvanriel/) in his book [Leading with Capabilities: Capability-Based Management and Implementation](https://www.amazon.com/Leading-Capabilities-Capability-Based-Management-Implementation/dp/1998528227). It serves as a realistic reference case demonstrating what a fully governed enterprise architecture looks like in practice.

!!! tip "Bring This to Your Organization"

    This framework can be set up for any enterprise -- from startups to large organizations with hundreds of software systems. Interested in what this could look like for your IT landscape? [Get in touch](https://www.linkedin.com/in/jonasvanriel/).
