# structurizr-mkdocs-generatr

Generate MkDocs Material sites from Structurizr DSL workspaces.

> Inspired by and based on [structurizr-site-generatr](https://github.com/avisi-cloud/structurizr-site-generatr) by Avisi Cloud. This project aims to provide similar functionality using Python, MkDocs Material, and Structurizr vNext instead of the archived Java libraries. Thank you to the original authors for their excellent work!

**Backwards compatible** — any workspace that works with [structurizr-site-generatr](https://github.com/avisi-cloud/structurizr-site-generatr) will also work with this tool. The same DSL properties (`generatr.*`) are supported, so you can switch without modifying your workspace.

## Prerequisites

- Docker (for Structurizr vNext and PlantUML)
- Python >= 3.11

## Installation

```bash
pip install structurizr-mkdocs-generatr
```

## Usage

```bash
# Generate a static site
structurizr-mkdocs path/to/workspace/

# Serve locally with live reload
structurizr-mkdocs path/to/workspace/ --serve

# Skip Docker export (reuse previous build artifacts)
structurizr-mkdocs path/to/workspace/ --skip-export
```

## Auto-Generated Views

The CLI automatically generates system landscape, system context, container, and deployment views from your DSL model and writes them to `_auto_generated_views.dsl` in your workspace directory. Hand-written views with the same key take priority and are skipped.

To use the generated views, add the following line inside your `views { }` block:

```dsl
views {
    !include _auto_generated_views.dsl

    properties { ... }
}
```

To skip view generation, pass `--skip-views-gen`.

## Capability Map (Bounded Contexts)

If a file named `boundedContext.mmd` exists in your workspace directory, the CLI parses it and generates a **Capability Map** section in the site. This Mermaid file defines bounded contexts, their entities, and cross-context relationships.

The file must be named exactly `boundedContext.mmd` and placed in the root of your workspace directory (next to `workspace.dsl`).

See [example/boundedContext.mmd](example/boundedContext.mmd) for the expected format.

## Configuration Properties

Properties are set in the `views { properties { } }` block of your Structurizr DSL workspace. All properties use the `mkdocs.*` prefix. For backward compatibility with [structurizr-site-generatr](https://github.com/avisi-cloud/structurizr-site-generatr), the equivalent `generatr.*` keys are also supported as fallbacks.

### Theme

| Property | Default | Description |
|---|---|---|
| `mkdocs.theme` | `auto` | Color scheme: `auto`, `light`, or `dark`. Auto enables a light/dark toggle. |
| `mkdocs.color.primary` | — | Primary theme color. Accepts Material named colors (e.g. `indigo`) or hex values (e.g. `#485fc7`). |
| `mkdocs.color.accent` | — | Accent color for links and interactive elements. Same format as primary. |
| `mkdocs.color.headerText` | — | Header text color override (hex only, e.g. `#ffffff`). |
| `mkdocs.favicon` | — | Path to favicon file, relative to the workspace directory. |
| `mkdocs.logo` | — | Path to logo file, relative to the workspace directory. |
| `mkdocs.customCss` | — | Path to a custom CSS file to include in the generated site. |

### Navigation

| Property | Default | Description |
|---|---|---|
| `mkdocs.navigation.tabs` | `true` | Show top-level sections as tabs in the header bar. |
| `mkdocs.navigation.instant` | `false` | Enable instant navigation (XHR-based page loads without full reload). |
| `mkdocs.navigation.nestGroups` | `false` | Nest Structurizr groups as sub-sections in the navigation. |

### Behavior

| Property | Default | Description |
|---|---|---|
| `mkdocs.svgLinkTarget` | `_blank` | Link target for clickable SVG diagrams: `_self`, `_blank`, `_parent`, or `_top`. |
| `mkdocs.externalTag` | — | Structurizr tag used to identify external systems (shown with a badge in the UI). |
| `mkdocs.fullWidth` | `true` | Use full-width layout instead of the default centered content. |
| `mkdocs.hideLegend` | `false` | Strip legend boxes from generated PlantUML diagrams. |

### Example

```dsl
views {
    properties {
        "mkdocs.theme" "auto"
        "mkdocs.color.primary" "#485fc7"
        "mkdocs.color.accent" "indigo"
        "mkdocs.navigation.tabs" "true"
        "mkdocs.svgLinkTarget" "_self"
        "mkdocs.externalTag" "External System"
    }
}
```

### Backward Compatibility

The following `generatr.*` properties from structurizr-site-generatr are supported as fallbacks:

| `mkdocs.*` key | `generatr.*` fallback |
|---|---|
| `mkdocs.theme` | `generatr.site.theme` |
| `mkdocs.color.primary` | `generatr.style.colors.primary` |
| `mkdocs.color.accent` | `generatr.style.colors.accent` |
| `mkdocs.color.headerText` | `generatr.style.colors.secondary` |
| `mkdocs.favicon` | `generatr.style.faviconPath` |
| `mkdocs.logo` | `generatr.style.logoPath` |
| `mkdocs.customCss` | `generatr.style.customStylesheet` |
| `mkdocs.svgLinkTarget` | `generatr.svglink.target` |
| `mkdocs.externalTag` | `generatr.site.externalTag` |
| `mkdocs.navigation.nestGroups` | `generatr.site.nestGroups` |
| `mkdocs.navigation.instant` | `generatr.site.navigation.instant` |
| `mkdocs.navigation.tabs` | `generatr.site.navigation.tabs` |
| `mkdocs.fullWidth` | `generatr.site.fullWidth` |
| `mkdocs.hideLegend` | `generatr.site.hideLegend` |
