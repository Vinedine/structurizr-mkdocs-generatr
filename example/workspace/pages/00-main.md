!!! example "Demonstration Workspace"

    You're looking at a showcase of the **Architecture as Code** framework -- not a real client. BelFoot FC is a fictional football club from [Jonas Van Riel](https://www.linkedin.com/in/jonasvanriel/)'s book [Leading with Capabilities](https://www.amazon.com/Leading-Capabilities-Capability-Based-Management-Implementation/dp/1998528227), used here as a reference case with a fully modeled capability map, bounded contexts, and entity relationships.

**A control center for architecture-as-code -- C4 on the outside, Claude Code on the inside.**

Architecture documentation shouldn't be a side project. It should be a side effect.

This site -- every diagram, every system description, every deployment view -- is generated directly from code. Change the model, push to Git, and the documentation updates itself. The [Claude Code skills](documentation/05-ai-automation.md) bundled with this framework read and write the same model, so AI-assisted development uses *your* architecture as context instead of guessing.

What you're looking at is BelFoot FC's full digital architecture: 28 software systems, 13 bounded contexts, 4 environments, zero manual upkeep. The diagram below shows one of five organizational groups -- click any box to start the journey.

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

??? question "But what about TOGAF / ArchiMate / Lean IX?"

    Great question -- and one that comes up in every architecture conversation.

    **This site uses C4 + Structurizr deliberately.** Not because TOGAF and ArchiMate are wrong, but because they solve different problems at a different pace.

    | | C4 / Structurizr | ArchiMate / TOGAF |
    |---|---|---|
    | **Focus** | Software systems, containers, components | Enterprise & solution: strategy, capabilities, cross-system flows |
    | **Audience** | Development teams, tech leads | Enterprise & solution architects, governance boards |
    | **Maintenance** | DSL-as-code in Git, auto-generated on every merge | Typically a separate modeling tool, manually maintained |
    | **Time to value** | Days | Months |
    | **Process modeling** | Not its job (use BPMN) | Built-in motivation, business process, and migration views |

    C4 is intentionally narrow. It answers *"what software do we have, how does it connect, and where does it run?"* -- and keeps that answer current because it lives in the same Git workflow as the code.

    ArchiMate answers broader questions -- strategy, business processes, data flows across the enterprise. If your organization needs that, C4 doesn't replace it. But C4 **feeds into it**: the Application layer in ArchiMate maps directly to C4 models.

    **Our approach:** Start with C4 to get immediate, maintainable value. If the organization later adopts ArchiMate or Lean IX, nothing is wasted -- the C4 models slot right into the application architecture viewpoint.

!!! tip "Bring this to your organization"

    This framework can be set up for any enterprise -- from startups to large organizations with hundreds of software systems. Interested in what this could look like for your landscape? [Get in touch](https://trotstar.tech).
