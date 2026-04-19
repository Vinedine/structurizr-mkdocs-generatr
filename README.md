# structurizr-mkdocs-generatr

**A control center for architecture-as-code. C4 on the outside, Claude Code on the inside.**

Generate a browsable MkDocs Material site from a Structurizr DSL workspace -- and pair it with a set of [Claude Code](https://claude.com/claude-code) skills that turn the same repo into an AI-assisted architecture workbench.

**Live demo:** [belfoot.trotstar.tech](https://belfoot.trotstar.tech) -- generated from the included BelFoot FC example workspace. Open the [Ticketing Platform page](https://belfoot.trotstar.tech/software-systems/ticketing-platform/#technical-architecture) and select the **Technical** tab for an example `0001-technical.md` of the kind the `c4-document-system` skill produces from a container's source repo. That file then becomes the reference downstream skills read.

> Inspired by and based on [structurizr-site-generatr](https://github.com/avisi-cloud/structurizr-site-generatr) by Avisi Cloud. This project provides similar functionality using Python, MkDocs Material, and Structurizr vNext instead of the archived Java libraries. Thank you to the original authors for their excellent work.

## The control center: six Claude Code skills

| Skill | What you say | What it does | Read-only? |
|---|---|---|---|
| [`c4-add-system`](.claude/skills/c4-add-system/SKILL.md) | *"add a new system from this intake"* | Adds DSL block, docs folder, and system-context view | No |
| [`c4-add-container`](.claude/skills/c4-add-container/SKILL.md) | *"add a container X to system Y"* | Inserts container + relationships into an existing system | No |
| [`c4-document-system`](.claude/skills/c4-document-system/SKILL.md) | *"generate a technical page for system X"* | Analyzes a container's source repo -> `0001-technical.md` | No |
| [`c4-audit-system`](.claude/skills/c4-audit-system/SKILL.md) | *"audit the entities for system X"* | Compares `0000-introduction.md` vs. the code | Report first, then offers fixes |
| [`c4-review`](.claude/skills/c4-review/SKILL.md) | *"run a Well-Architected review on system X"* | Writes a Markdown report against the five Azure Well-Architected pillars | Yes |
| [`c4-validate-changes`](.claude/skills/c4-validate-changes/SKILL.md) | *"validate this branch"* | Pre-PR DSL validation + peer-container comparison | Yes |

See [`.claude/skills/README.md`](.claude/skills/README.md) for skill-by-skill details, prerequisites, and the discovery logic each skill uses to find your workspace.

## Quick Start

### Docker (recommended)

No local dependencies needed -- everything is bundled in the image.

```bash
# Generate a static site
docker run --rm -v ./my-workspace:/var/model ghcr.io/vinedine/structurizr-mkdocs-generatr .

# Serve locally with live reload
docker run --rm -v ./my-workspace:/var/model -p 8000:8000 ghcr.io/vinedine/structurizr-mkdocs-generatr . --serve
```

### Python

```bash
# Install from source
git clone https://github.com/Vinedine/structurizr-mkdocs-generatr.git
cd structurizr-mkdocs-generatr
pip install -e .

# Generate the example site and serve it locally
structurizr-mkdocs example/ --serve
```

## Prerequisites

**Docker image:** No prerequisites -- Java, Structurizr CLI, PlantUML, and Python are all bundled.

**Python install:** Docker (for Structurizr vNext and PlantUML) + Python >= 3.11

## Install the skills

Most people use this tool via the Docker image and never clone the repo -- but the skills are distributed as files, so you need them on disk for Claude Code to pick them up. Two paths:

### Option A: Global install (recommended)

Makes the skills available in every Claude Code session on your machine, across every Structurizr repo you touch.

```bash
git clone --depth 1 https://github.com/Vinedine/structurizr-mkdocs-generatr.git /tmp/smg
mkdir -p ~/.claude/skills && cp -r /tmp/smg/.claude/skills/c4-* ~/.claude/skills/
rm -rf /tmp/smg
```

### Option B: Project-scoped install

Skills version-pinned alongside your architecture repo. Best for teams.

```bash
git clone --depth 1 https://github.com/Vinedine/structurizr-mkdocs-generatr.git /tmp/smg
mkdir -p .claude/skills && cp -r /tmp/smg/.claude/skills/c4-* .claude/skills/
rm -rf /tmp/smg
```

After either install, open the repo in Claude Code and type `/c4` -- the six skills appear in the picker. If you're working inside this repo's clone, you already have them.

## The Example: BelFoot FC IT Landscape

This repo ships with a complete enterprise architecture example: the **BelFoot FC IT Landscape** -- a fictional football club with 28 software systems across 5 organizational groups, multi-cloud deployments (on-premise + Azure + AWS), 18 actors, 13 bounded contexts, 4 dynamic workflow views, and 6 architecture decision records.

BelFoot FC is created by [Jonas Van Riel](https://www.linkedin.com/in/jonasvanriel/) in his book [Leading with Capabilities](https://www.amazon.com/Leading-Capabilities-Capability-Based-Management-Implementation/dp/1998528227). It serves as a realistic reference case to demonstrate what a fully governed enterprise architecture looks like in practice.

The example workspace is in [`example/`](example/) and includes:

- **Modular DSL** -- `workspace.dsl` with includes for groups, users, deployments, and views
- **5 organizational groups** -- Commercial (8 systems), Corporate (5), IT (5), Operations (4), Sporting (3)
- **Software system docs** -- 28 `0000-introduction.md` files with business capabilities and data entity mappings
- **Bounded contexts** -- `boundedContext.mmd` defining 13 business domains with 100+ entities and cross-context relationships
- **Dynamic views** -- 4 animated workflows: ticket purchasing, gameday operations, data ingestion, and AI injury prediction
- **Architecture Decision Records** -- 6 ADRs covering multi-cloud strategy, event-driven integration, data lakehouse, AI, and more
- **Multi-cloud deployments** -- 4 environments (production, acceptance, test, dev) with on-premise stadium systems, Azure cloud platform, and AWS sporting analytics
- **7 documentation pages** -- Landing page, business-to-infrastructure traceability, systems overview, infrastructure guide, decisions lifecycle, AI automation, and a writing guide

Run `structurizr-mkdocs example/ --serve` to explore it locally, or see the [live demo](https://belfoot.trotstar.tech).

## Usage

### Docker

```bash
# Generate a static site (output appears in ./my-workspace/build/site/)
docker run --rm -v ./my-workspace:/var/model ghcr.io/vinedine/structurizr-mkdocs-generatr .

# Serve locally with live reload
docker run --rm -v ./my-workspace:/var/model -p 8000:8000 ghcr.io/vinedine/structurizr-mkdocs-generatr . --serve

# Custom workspace filename
docker run --rm -v ./my-workspace:/var/model ghcr.io/vinedine/structurizr-mkdocs-generatr . -w custom.dsl
```

### Python CLI

```bash
# Generate a static site
structurizr-mkdocs path/to/workspace/

# Serve locally with live reload
structurizr-mkdocs path/to/workspace/ --serve

# Skip Docker export (reuse previous build artifacts)
structurizr-mkdocs path/to/workspace/ --skip-export

# Custom output directory and workspace filename
structurizr-mkdocs path/to/workspace/ -o my-build -w custom.dsl
```

## Features

### Auto-Generated Views

The CLI automatically generates system landscape, system context, container, and deployment views from your DSL model and writes them to `_auto_generated_views.dsl` in your workspace directory. Hand-written views with the same key take priority and are skipped.

To use the generated views, add the following line inside your `views { }` block:

```dsl
views {
    !include _auto_generated_views.dsl

    properties { ... }
}
```

To skip view generation, pass `--skip-views-gen`.

### Capability Map (Bounded Contexts)

If a file named `boundedContext.mmd` exists in your workspace directory, the CLI parses it and generates a **Capability Map** section in the site. This Mermaid file defines bounded contexts, their entities, and cross-context relationships.

The file must be named exactly `boundedContext.mmd` and placed in the root of your workspace directory (next to `workspace.dsl`).

See [example/boundedContext.mmd](example/boundedContext.mmd) for the expected format.

### What Gets Generated

From a single Structurizr DSL workspace, the tool produces:

- **C4 diagrams** at every level (landscape, context, container, component, deployment, dynamic) as clickable SVGs with drill-down navigation between levels
- **Software system pages** with tabbed sections for overview, context/container/component/dynamic views, deployment views, dependencies (inbound & outbound tables), documentation, and decisions
- **Software system groups** with group-level landscape diagrams and tag badges (External, Shared, New)
- **Actor/person pages** showing which systems each person interacts with
- **Infrastructure pages** organized by deployment environment and infrastructure zone
- **Bounded context pages** with entity relationship diagrams and cross-context links
- **Capability maps** linking business capabilities to software systems
- **Architecture Decision Records** with status tracking, context summaries, and cross-linking between decisions
- **Workspace-level documentation** rendered from Structurizr `!docs` sections
- **Inline diagram support** -- PlantUML code blocks in documentation are extracted, rendered to SVG, and embedded automatically; Mermaid blocks pass through natively
- **Image views** with base64 decoding for embedded PNG, JPEG, GIF, and SVG
- **Full-text search** via MkDocs Material
- **Theme customization** with color overrides, custom CSS, logos, and favicons

## Configuration Properties

Properties are set in the `views { properties { } }` block of your Structurizr DSL workspace. All properties use the `mkdocs.*` prefix. For backward compatibility with [structurizr-site-generatr](https://github.com/avisi-cloud/structurizr-site-generatr), the equivalent `generatr.*` keys are also supported as fallbacks.

### Theme

| Property | Default | Description |
|---|---|---|
| `mkdocs.theme` | `auto` | Color scheme: `auto`, `light`, or `dark`. Auto enables a light/dark toggle. |
| `mkdocs.color.primary` | -- | Primary theme color. Accepts Material named colors (e.g. `indigo`) or hex values (e.g. `#485fc7`). |
| `mkdocs.color.accent` | -- | Accent color for links and interactive elements. Same format as primary. |
| `mkdocs.color.headerText` | -- | Header text color override (hex only, e.g. `#ffffff`). |
| `mkdocs.favicon` | -- | Path to favicon file, relative to the workspace directory. |
| `mkdocs.logo` | -- | Path to logo file, relative to the workspace directory. |
| `mkdocs.customCss` | -- | Path to a custom CSS file to include in the generated site. |

### Navigation

| Property | Default | Description |
|---|---|---|
| `mkdocs.navigation.tabs` | `true` | Show top-level sections as tabs in the header bar. |
| `mkdocs.navigation.instant` | `false` | Enable instant navigation (XHR-based page loads without full reload). |

### Behavior

| Property | Default | Description |
|---|---|---|
| `mkdocs.svgLinkTarget` | `_blank` | Link target for clickable SVG diagrams: `_self`, `_blank`, `_parent`, or `_top`. |
| `mkdocs.fullWidth` | `true` | Use full-width layout instead of the default centered content. |
| `mkdocs.showLegend` | `false` | Show legend boxes on generated PlantUML diagrams. |

### Site

| Property | Default | Description |
|---|---|---|
| `mkdocs.siteUrl` | -- | Site URL for sitemap generation and canonical links (e.g. `https://example.com`). |
| `mkdocs.copyright` | -- | Footer copyright/attribution text. Supports HTML (e.g. `Built by <a href='...'>Company</a>`). |

### Example

```dsl
views {
    properties {
        "mkdocs.theme" "auto"
        "mkdocs.color.primary" "#485fc7"
        "mkdocs.color.accent" "indigo"
        "mkdocs.navigation.tabs" "true"
        "mkdocs.svgLinkTarget" "_self"
    }
}
```


## Pipeline

```
workspace.dsl
  -> [Auto-generate views]     _auto_generated_views.dsl
  -> [Structurizr vNext Docker] workspace.json + C4 PlantUML (.puml)
  -> [PlantUML Docker]          .puml -> .svg
  -> [Python CLI]               Parse JSON, generate Markdown + mkdocs.yml
  -> [mkdocs build]             Static site
```

## Contributing

Contributions are welcome! Please open an issue first to discuss what you'd like to change.

```bash
# Development setup
git clone https://github.com/Vinedine/structurizr-mkdocs-generatr.git
cd structurizr-mkdocs-generatr
pip install -e .
pytest
```

## Acknowledgments

- [structurizr-site-generatr](https://github.com/avisi-cloud/structurizr-site-generatr) by Avisi Cloud -- the original Kotlin tool that inspired this project
- [Structurizr](https://structurizr.com/) by Simon Brown -- the C4 model tooling
- [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) -- the theme powering the generated sites
- [Jonas Van Riel](https://www.linkedin.com/in/jonasvanriel/) -- creator of the BelFoot FC fictional case study from [Leading with Capabilities](https://www.amazon.com/Leading-Capabilities-Capability-Based-Management-Implementation/dp/1998528227)

## Built by

[TrotStar Technologies](https://trotstar.tech) -- Architecture as Code, automated.

## License

MIT
