# structurizr-mkdocs-generatr

> Early POC. Breaking changes likely. Pin a Docker image tag if you depend on it.

**Architecture documentation shouldn't be a side project. It should be a side effect.**

A control center for architecture-as-code: a Python CLI that generates a browsable MkDocs Material site from a Structurizr DSL workspace, plus a set of [Claude Code](https://claude.com/claude-code) skills that turn the same repo into an AI-assisted architecture workbench. C4 on the outside, Claude Code on the inside.

**Live demo:** [belfoot.trotstar.tech](https://belfoot.trotstar.tech) -- generated from the included BelFoot FC example workspace. Open the [Ticketing Platform page](https://belfoot.trotstar.tech/software-systems/ticketing-platform/#technical-architecture) and select the **Technical** tab for an example `0001-technical.md` of the kind the `c4-document-system` skill produces from a container's source repo. That file then becomes the reference downstream skills read.

> Inspired by and based on [structurizr-site-generatr](https://github.com/avisi-cloud/structurizr-site-generatr) by Avisi Cloud. Python, MkDocs Material, and Structurizr vNext in place of the archived Java libraries. Thank you to the original authors.

## Six Claude Code skills

| Skill | What you say | What it does | Read-only? |
|---|---|---|---|
| [`c4-add-system`](.claude/skills/c4-add-system/SKILL.md) | *"add a new system from this intake"* | Adds DSL block, docs folder, and system-context view | No |
| [`c4-add-container`](.claude/skills/c4-add-container/SKILL.md) | *"add a container X to system Y"* | Inserts container + relationships into an existing system | No |
| [`c4-document-system`](.claude/skills/c4-document-system/SKILL.md) | *"generate a technical page for system X"* | Analyzes a container's source repo -> `0001-technical.md` | No |
| [`c4-audit-system`](.claude/skills/c4-audit-system/SKILL.md) | *"audit the entities for system X"* | Compares `0000-introduction.md` vs. the code | Report first, then offers fixes |
| [`c4-review`](.claude/skills/c4-review/SKILL.md) | *"run a Well-Architected review on system X"* | Writes a Markdown report against the five Azure Well-Architected pillars | Yes |
| [`c4-validate-changes`](.claude/skills/c4-validate-changes/SKILL.md) | *"validate this branch"* | Pre-PR DSL validation + peer-container comparison | Yes |

See [`.claude/skills/README.md`](.claude/skills/README.md) for skill-by-skill details, prerequisites, and the discovery logic each skill uses to find your workspace.

## Quick start (Docker)

No local dependencies needed -- Java, Structurizr CLI, PlantUML, and Python are all bundled.

```bash
# Generate a static site (output in ./my-workspace/build/site/)
docker run --rm -v ./my-workspace:/var/model ghcr.io/vinedine/structurizr-mkdocs-generatr .

# Serve locally with live reload
docker run --rm -v ./my-workspace:/var/model -p 8000:8000 ghcr.io/vinedine/structurizr-mkdocs-generatr . --serve

# Custom workspace filename
docker run --rm -v ./my-workspace:/var/model ghcr.io/vinedine/structurizr-mkdocs-generatr . -w custom.dsl
```

For development or running without Docker: clone the repo and `pip install -e .`, then `structurizr-mkdocs example/ --serve`. Requires Python >= 3.11 plus Docker (still needed for the Structurizr vNext and PlantUML steps).

## Install the skills

The Docker image runs the generator. The skills are separate files Claude Code reads from disk, so you need them on your machine too -- own it openly:

```bash
# Global install (recommended): available in every Claude Code session
git clone --depth 1 https://github.com/Vinedine/structurizr-mkdocs-generatr.git /tmp/smg
mkdir -p ~/.claude/skills && cp -r /tmp/smg/.claude/skills/c4-* ~/.claude/skills/
rm -rf /tmp/smg
```

For a project-scoped install (skills version-pinned alongside your architecture repo, best for teams), substitute `.claude/skills/` inside the repo for `~/.claude/skills/` in the second command.

Open Claude Code and type `/c4` to confirm the six skills appear. If you're working inside this repo's clone, you already have them.

## The example: BelFoot FC

[`example/`](example/) ships a complete fictional enterprise architecture: 28 software systems across 5 organizational groups, 18 actors, 13 bounded contexts, 6 ADRs, multi-cloud deployments (on-premise + Azure + AWS), and 4 animated workflow views. The case study is from Jonas Van Riel's [Leading with Capabilities](https://www.amazon.com/Leading-Capabilities-Capability-Based-Management-Implementation/dp/1998528227).

Run `structurizr-mkdocs example/ --serve` to explore it locally, or see the [live demo](https://belfoot.trotstar.tech).

## Configuration

Properties go under `views { properties { } }` in your DSL with the `mkdocs.*` prefix. The full reference (theme, color, navigation, behavior, site URL, copyright) lives in [`src/structurizr_mkdocs_generatr/properties.py`](src/structurizr_mkdocs_generatr/properties.py). Only `mkdocs.*` keys are read; a workspace migrating from [structurizr-site-generatr](https://github.com/avisi-cloud/structurizr-site-generatr) must rename its `generatr.*` keys (`generatr.style.colors.primary` becomes `mkdocs.color.primary`, `generatr.style.colors.secondary` becomes `mkdocs.color.headerText`, `generatr.style.faviconPath` becomes `mkdocs.favicon`, `generatr.style.logoPath` becomes `mkdocs.logo`).

```dsl
views {
    properties {
        "mkdocs.theme" "auto"
        "mkdocs.color.primary" "#485fc7"
        "mkdocs.color.accent" "indigo"
        "mkdocs.navigation.tabs" "true"
        "mkdocs.groupOrder" "IT, Commercial, Corporate"
    }
}
```

`mkdocs.groupOrder` sets the order of the group sub-sections under Software Systems; groups it doesn't name follow alphabetically. Each group's index page embeds the landscape view keyed `SystemLandscape{Group}` (e.g. `SystemLandscapeCommercial`). For a nested group such as `BELFOOT/DIGITAL`, a view named after the last segment (`SystemLandscapeDigital`) also matches, since a view key can't contain the group separator.

Two opt-in features worth knowing about:

- **Auto-generated views.** The CLI writes system-landscape, system-context, container, and deployment views into `_auto_generated_views.dsl`. Add `!include _auto_generated_views.dsl` inside your `views { }` block to consume them; hand-written views with the same key take priority. Pass `--skip-views-gen` to turn it off.
- **Capability map.** If `boundedContext.mmd` exists in your workspace root, the CLI renders it as a capability-map section in the site. See [`example/boundedContext.mmd`](example/boundedContext.mmd) for the expected format.

## Pipeline

```
workspace.dsl
  -> [Auto-generate views]      _auto_generated_views.dsl
  -> [Structurizr vNext Docker] workspace.json + C4 PlantUML (.puml)
  -> [PlantUML Docker]          .puml -> .svg
  -> [Python CLI]               Parse JSON, generate Markdown + mkdocs.yml
  -> [mkdocs build]             Static site
```

## Contributing

Contributions welcome. Open an issue first to discuss.

```bash
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

## License

[MIT](LICENSE). Copy it, adapt it, build your own.
