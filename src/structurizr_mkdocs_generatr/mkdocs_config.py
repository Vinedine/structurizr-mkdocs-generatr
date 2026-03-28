"""Generate mkdocs.yml from a parsed Structurizr workspace."""

from __future__ import annotations

from pathlib import Path

import yaml

from .workspace import (
    Documentation,
    Section,
    SoftwareSystem,
    Workspace,
    normalize_name,
)


def generate_mkdocs_config(workspace: Workspace, site_dir: Path) -> None:
    """Generate mkdocs.yml for the workspace."""
    config = {
        "site_name": workspace.name or "Architecture",
        "site_description": workspace.description,
        "theme": {
            "name": "material",
            "palette": [
                {"scheme": "default", "toggle": {"icon": "material/brightness-7", "name": "Dark mode"}},
                {"scheme": "slate", "toggle": {"icon": "material/brightness-4", "name": "Light mode"}},
            ],
            "features": [
                "navigation.tabs",
                "navigation.top",
                "search.suggest",
                "search.highlight",
            ],
        },
        "docs_dir": "docs",
        "use_directory_urls": False,
        "nav": _build_nav(workspace),
        "markdown_extensions": [
            "admonition",
            "tables",
            "attr_list",
            "md_in_html",
            {"toc": {"permalink": True}},
            {"pymdownx.superfences": {
                "custom_fences": [{
                    "name": "mermaid",
                    "class": "mermaid",
                    "format": "!!python/name:pymdownx.superfences.fence_mermaid",
                }],
            }},
            "pymdownx.tabbed",
            "pymdownx.details",
        ],
    }

    site_dir.mkdir(parents=True, exist_ok=True)
    with open(site_dir / "mkdocs.yml", "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def _build_nav(workspace: Workspace) -> list:
    """Build nav with top-level tabs."""
    nav = []

    # Tab 1: Home + workspace documentation in left sidebar
    home_items: list = [{"Home": "index.md"}]
    sorted_sections = sorted(workspace.documentation.sections, key=lambda s: s.order)
    for section in sorted_sections[1:]:
        slug = _section_slug(section)
        title = _section_title(section)
        home_items.append({title: f"documentation/{slug}.md"})
    nav.append({"Home": home_items})

    # Tab 3: Decisions (workspace-level ADRs)
    decisions_nav = _decisions_nav(workspace.documentation, prefix="decisions")
    if decisions_nav:
        nav.append({"Decisions": decisions_nav})

    # Tab 4+: One tab per software system with sub-pages in left sidebar
    # Or a single "Software Systems" tab with systems as sections
    systems_nav = _systems_nav(workspace)
    nav.append({"Software Systems": systems_nav})

    return nav


def _decisions_nav(documentation: Documentation, prefix: str) -> list:
    decisions = documentation.decisions
    if not decisions:
        return []

    nav: list = [{"Overview": f"{prefix}/index.md"}]
    for d in sorted(decisions, key=lambda d: int(d.id)):
        nav.append({f"{d.id}. {d.title}": f"{prefix}/{d.id}.md"})
    return nav


def _systems_nav(workspace: Workspace) -> list:
    nav: list = [{"Overview": "software-systems/index.md"}]

    for ss in sorted(workspace.software_systems, key=lambda s: s.name):
        ss_nav = _system_nav(workspace, ss)
        nav.append({ss.name: ss_nav})

    return nav


def _system_nav(workspace: Workspace, ss: SoftwareSystem) -> list:
    slug = normalize_name(ss.name)
    prefix = f"software-systems/{slug}"
    nav: list = [{"Info": f"{prefix}/index.md"}]

    # Diagram pages
    system_views = workspace.views_for_system(ss.id)
    view_types_present = {v.type for v in system_views}

    type_labels = {
        "systemContext": ("Context Views", "context.md"),
        "container": ("Container Views", "containers.md"),
        "component": ("Component Views", "components.md"),
        "dynamic": ("Dynamic Views", "dynamic.md"),
        "deployment": ("Deployment Views", "deployment.md"),
        "image": ("Image Views", "images.md"),
    }

    for view_type, (label, filename) in type_labels.items():
        if view_type in view_types_present:
            nav.append({label: f"{prefix}/{filename}"})

    # System decisions
    if ss.documentation.decisions:
        dec_nav = _decisions_nav(ss.documentation, prefix=f"{prefix}/decisions")
        nav.append({"Decisions": dec_nav})

    # System documentation
    if ss.documentation.sections:
        docs_nav = []
        for section in sorted(ss.documentation.sections, key=lambda s: s.order):
            sec_slug = _section_slug(section)
            title = _section_title(section)
            docs_nav.append({title: f"{prefix}/docs/{sec_slug}.md"})
        nav.append({"Documentation": docs_nav})

    return nav


def _section_slug(section: Section) -> str:
    if section.title:
        return normalize_name(section.title)
    name = section.filename.rsplit(".", 1)[0]
    return normalize_name(name)


def _section_title(section: Section) -> str:
    if section.title:
        return section.title
    name = section.filename.rsplit(".", 1)[0]
    parts = name.split("-", 1)
    if len(parts) > 1 and parts[0].isdigit():
        name = parts[1]
    return name.replace("-", " ").capitalize()
