## Welcome to the BelFoot FC IT Landscape

This is an auto-generated architecture website documenting every software system, integration, and deployment environment at **BelFoot FC**.

Everything you see on this site -- diagrams, system descriptions, deployment views, bounded contexts, capability maps, decision records -- is generated directly from version-controlled code. **No stale Visio files**. **No forgotten wikis**. **One source of truth**, always current.

BelFoot FC is a fictional football club created by [Jonas Van Riel](https://www.linkedin.com/in/jonasvanriel/) in his book [Leading with Capabilities: Capability-Based Management and Implementation](https://www.amazon.com/Leading-Capabilities-Capability-Based-Management-Implementation/dp/1998528227). It serves as a realistic reference case to demonstrate what a fully governed enterprise architecture looks like in practice, from bounded contexts and business capabilities down to concrete software systems and integrations.

## What This Means For Your Organization

Most organizations cannot confidently answer *"what do we have, and how does it fit together?"* Diagrams were drawn once for a project kickoff and never updated. Knowledge lives in senior engineers' heads. Architecture documentation is stale, scattered, and trusted by nobody.

This framework changes that. Here is what it delivers:

- **New engineers understand the full landscape in days, not months** -- every system, integration, and deployment is documented and navigable
- **Impact analysis before any change** -- trace which systems are affected when you modify an API, retire a service, or migrate to the cloud
- **Architecture decisions are traceable and auditable** -- every change goes through a pull request with full history
- **Documentation stays current by design** -- it is generated from the same code that defines the architecture, so it cannot drift
- **Executive visibility without manual reporting** -- bounded contexts, capabilities, and entity mappings are auto-extracted into Power BI dashboards

## One Tool That Brings the Whole Organization Together

Architecture is not just a technical concern. Business stakeholders need to see capabilities and bounded contexts. Solution architects need system integrations and data flows. Engineers need container internals and deployment topologies. Operations needs infrastructure mappings. Today, each group draws its own diagrams in its own tool, and none of them stay in sync.

This framework solves that by providing **a single model that generates views for every audience** -- from high-level business capability maps all the way down to production deployment diagrams. Because every view is generated from the same underlying architecture code, they are always consistent and always linked. Click from a business capability to the systems that support it, drill into a system to see its containers, then see exactly where those containers are deployed in each environment.

**Everything is configurable.** You decide which views to include, which groups to highlight, which deployment environments to show, and how deep to go. Want to display only the commercial department's landscape? Done. Need a fan-facing user journey alongside a cloud deployment diagram? Add it. Every organization's site looks different because every organization chooses what matters to them.

## The Framework Behind This Site

This site was built using an **Architecture as Code** framework that turns a scattered IT landscape into a living, governed, auto-generated architecture website. It is version-controlled, validated through CI/CD, and enhanced with AI-driven automation. Built on the [C4 Model](https://c4model.com/), [Structurizr](https://structurizr.com/) DSL, and [structurizr-mkdocs-generatr](https://github.com/xxx/structurizr-mkdocs-generatr) with [MkDocs Material](https://squidfundry.github.io/mkdocs-material/).

## Key Capabilities

- **Fully configurable**: choose which views, groups, environments, and detail levels to include -- the site reflects exactly what your organization needs
- A **fully navigable static website** covering every system, deployment environment, and integration
- **C4 Model views** at every level: system context, containers, components, deployment -- all linked so you can drill down from business context to infrastructure
- **Git-based governance**: architecture changes go through branch, pull request, review, merge, auto-deploy
- **Architecture Decision Records** tracked alongside the architecture
- **Auto-extracted metadata** (bounded contexts, business capabilities, entity mappings) fed into Power BI dashboards
- **Cloud integration**: connectors for Azure, AWS, and GCP that pull live deployment data so views reflect reality
- **Documentation portal sync**: architecture data can be published to portals like Atlassian Compass, Backstage, and Port, keeping architecture and developer portals aligned
- **AI automation**: custom agent skills handle system creation, entity audits, branch validation, and technical page generation, turning what used to be manual architecture work into repeatable, automated workflows

