!!! note "Quick Summary"

    Four Claude Code skills automate the tedious parts of architecture documentation: creating system definitions, generating technical pages, auditing entity coverage, and validating branch changes. Every software system on this site was generated using these skills.

## This Site Is the Proof

The BelFoot FC workspace is not a hand-crafted example -- it is the output. Every software system definition, container relationship, and documentation page you see on this site was generated using the AI skills described below. The 28 software systems, 13 bounded contexts, and deployment views were created through a combination of `/arch-create-system` and `/arch-create-technical-page`, then validated with `/arch-audit-entities` and `/arch-validate-branch`.

## Why Plain Text Makes This Possible

Traditional architecture lives in diagrams -- Visio files, Lucidchart canvases, PowerPoint slides. An AI agent cannot read those. This framework stores everything as plain text: Structurizr DSL for system definitions, Mermaid for domain diagrams, and Markdown for documentation. An AI agent reads, understands, and modifies all of it just as easily as a developer reads source code.

## Architecture Skills

### :material-plus-circle: `/arch-create-system` -- Create a Software System

Given a product submission (name, description, tech stack, repositories), Claude generates the full Structurizr DSL definition: software system, containers with technology tags, relationships, and a `0000-introduction.md` documentation page with business capabilities, data entities, and reference links.

**Input:** A product submission form with name, description, tech stack, and repository URLs.

**Output:** A complete DSL block and documentation page -- ready to commit. Browse any software system on this site (e.g., Player Performance, Ticketing Platform) to see real output from this skill.

### :material-file-document-outline: `/arch-create-technical-page` -- Generate Technical Documentation

Claude reads a code repository (via Git or Azure DevOps), analyzes its API endpoints, data models, authentication patterns, and infrastructure, and generates a `0001-technical.md` page documenting the system's technical architecture.

**Input:** A repository URL or local path.

**Output:** A technical documentation page with endpoint tables, data model descriptions, authentication details, and infrastructure notes.

### :material-magnify: `/arch-audit-entities` -- Audit Entity Coverage

Claude compares architecture documentation against the actual code in a repository. It identifies entities that exist in code but are missing from docs, entities documented but no longer in code, and discrepancies in descriptions or relationships.

**Input:** A software system name and its repository.

**Output:** An audit report listing gaps, mismatches, and recommendations.

### :material-check-circle: `/arch-validate-branch` -- Validate Before Pull Request

Before creating a pull request, Claude validates architecture changes against documented standards. It checks naming conventions, required properties, documentation completeness, and consistency with peer systems using the same technology stack.

**Input:** A branch with architecture changes.

**Output:** A validation report with pass/fail status and specific issues to fix.

## How It Fits Into the Workflow

1. **Create a branch** for an architecture change
2. **Run a skill** -- `/arch-create-system` for new systems, `/arch-create-technical-page` for existing repos
3. **Review the output** and adjust as needed
4. **Validate with `/arch-validate-branch`** before creating a pull request
5. **Merge** -- the CI/CD pipeline rebuilds and deploys the architecture site
