## AI-Powered Automation

Maintaining architecture documentation by hand does not scale. This framework uses Claude AI skills to generate, validate, and audit architecture directly from source code and DevOps platforms.

### Why Architecture as Code Is AI-Ready

Traditional architecture lives in diagrams -- Visio files, Lucidchart canvases, PowerPoint slides. An AI agent cannot read those. This framework stores everything as plain text: Structurizr DSL for system definitions, Mermaid for domain diagrams, and Markdown for documentation. An AI agent can read, understand, and modify all of it just as easily as a developer reads source code. That is what makes the automation below possible.

### Architecture Skills

Each skill is a specialized task that Claude executes against your codebase and architecture model:

**:material-plus-circle: Create System** -- Given a product submission (name, description, tech stack, repositories), Claude generates the full Structurizr DSL definition: software system, containers, relationships, and a `0000-introduction.md` documentation page. What takes hours of manual work happens in minutes.

**:material-file-document-outline: Create Technical Page** -- Claude reads a code repository (via Git or Azure DevOps), analyzes its API endpoints, data models, authentication patterns, and infrastructure, and generates a `0001-technical.md` page documenting the system's technical architecture.

**:material-magnify: Audit Entities** -- Claude compares the architecture documentation against the actual code in a repository. It identifies entities that exist in code but are missing from docs, entities documented but no longer in code, and discrepancies in descriptions or relationships.

**:material-check-circle: Validate Branch** -- Before creating a pull request, Claude validates architecture changes against documented standards. It checks naming conventions, required properties, documentation completeness, and consistency with peer systems using the same technology stack.

### How It Fits Into the Workflow

AI skills integrate into the existing Git-based governance model:

1. **Developer creates a branch** for an architecture change
2. **Claude skills generate or update** DSL definitions and documentation
3. **Developer reviews** the generated output and adjusts as needed
4. **Pull request** is created for peer review
5. **Merge triggers** the CI/CD pipeline to rebuild and deploy the architecture site

The AI does not replace human judgment -- it accelerates the tedious parts (writing DSL boilerplate, documenting endpoints, cross-checking entities) so architects can focus on design decisions.

### What Gets Generated

For a typical software system onboarding, Claude produces:

- Structurizr DSL block with software system, containers, and technology tags
- Container relationships (API calls, database connections, message queues)
- `0000-introduction.md` with business capabilities, data entities, and reference links
- `0001-technical.md` with API endpoints, data model, authentication, and infrastructure details

All output is plain text (DSL and Markdown) committed to the same Git repository as the rest of the architecture -- fully version-controlled and reviewable.
