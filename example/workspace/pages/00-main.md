Every diagram, system page, and decision record on this site is **generated from code** -- a single [Structurizr DSL](https://docs.structurizr.com/dsl/language) workspace, version-controlled in Git, rebuilt on every merge. Nothing is drawn by hand. The model is the documentation.

Below is one of five organizational groups in the BelFoot FC IT landscape -- a fictional football club with 28 software systems, 18 personas, and multi-cloud infrastructure.

![BelFoot FC — IT Systems](embed:SystemLandscapeIT)

<div class="grid cards" markdown>

- :material-domain: **[From Business to Infrastructure](documentation/01-business-to-infrastructure.md)**

    ---

    Trace from a business capability through bounded contexts and software systems down to the infrastructure that runs it. See all five organizational groups and 13 bounded contexts.

- :material-sitemap: **[Systems and Workflows](documentation/02-systems-and-workflows.md)**

    ---

    Browse 28 software systems with auto-generated diagrams, and four animated workflows showing how systems collaborate at runtime.

- :material-server-network: **[Infrastructure](documentation/03-infrastructure.md)**

    ---

    Multi-cloud deployment across on-premise, Azure, and AWS -- with deployment views per environment for production, acceptance, test, and development.

</div>

<div class="grid cards" markdown>

- :material-shape-outline: **[13 Bounded Contexts](capability-map/index.md)**

    ---

    Business domains mapped to data entities and software systems

- :material-account-group: **[18 Personas](persons/index.md)**

    ---

    From fans and sponsors to coaches, analysts, and IT architects

- :material-domain: **[5 Org Groups](software-systems/index.md)**

    ---

    Commercial, Corporate, IT, Operations, and Sporting -- each with its own landscape view

- :material-package-variant-closed: **[28 Software Systems](software-systems/index.md)**

    ---

    Browse every system with auto-generated diagrams, dependencies, and documentation

- :material-cloud-outline: **[4 Environments](infrastructure/index.md)**

    ---

    Production (multi-cloud), acceptance, test, and development

- :material-file-document-check-outline: **[6 ADRs](adrs/index.md)**

    ---

    Strategic decisions with full context, consequences, and audit trail

</div>

---

=== "For Technical Teams"

    - **[Auto-generated C4 diagrams](documentation/02-systems-and-workflows.md)** at every level -- landscape, context, container, component, deployment
    - **[Bounded contexts and capability maps](documentation/01-business-to-infrastructure.md)** linking business domains to software systems
    - **[Deployment views per environment](documentation/03-infrastructure.md)** -- see exactly where containers run across production, acceptance, development, and test
    - **[AI-powered automation](documentation/05-ai-automation.md)** -- every system on this site was generated using Claude Code skills
    - **[Git-based governance](documentation/06-how-it-works.md)** -- every change goes through branch, pull request, review, merge, auto-deploy

=== "For Business Leaders"

    - **[Business capabilities mapped to IT systems](documentation/01-business-to-infrastructure.md)** -- see which software supports which part of the business
    - **[Impact analysis before any change](documentation/01-business-to-infrastructure.md)** -- trace from a business capability down to the infrastructure that runs it
    - **[Architecture decisions are transparent](documentation/04-decisions.md)** -- every strategic choice is documented with context and consequences
    - **[Documentation stays current by design](documentation/06-how-it-works.md)** -- generated from the same code that defines the architecture

!!! tip "Bring This to Your Organization"

    This framework can be set up for any enterprise -- from startups to large organizations with hundreds of software systems. Interested in what this could look like for your landscape? [Get in touch](https://www.linkedin.com/in/vincent-weijburg-191aa9/).
