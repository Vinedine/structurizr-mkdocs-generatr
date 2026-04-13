"""Generate mkdocs.yml from a parsed Structurizr workspace."""

from __future__ import annotations

from pathlib import Path

import yaml

from .properties import MATERIAL_NAMED_COLORS, SiteProperties


class _PythonName:
    """Wrapper to emit !!python/name: YAML tags for MkDocs config."""
    def __init__(self, value: str) -> None:
        self.value = value


def _python_name_representer(dumper: yaml.Dumper, data: _PythonName) -> yaml.Node:
    return yaml.ScalarNode(tag="tag:yaml.org,2002:python/name:" + data.value, value="")


yaml.add_representer(_PythonName, _python_name_representer)


from .workspace import (
    Documentation,
    Workspace,
    normalize_name,
    section_slug,
    section_title,
)


def generate_mkdocs_config(workspace: Workspace, site_dir: Path, props: SiteProperties) -> None:
    """Generate mkdocs.yml for the workspace."""
    config = {
        "site_name": workspace.name or "Architecture",
        "site_description": workspace.description,
        "theme": _build_theme(props),
        "plugins": ["search", "glightbox"],
        "docs_dir": "docs",
        "use_directory_urls": False,
        "nav": _build_nav(workspace),
        "extra_css": _build_extra_css(props),
        "extra_javascript": ["js/external-links.js"],
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
                    "format": _PythonName("pymdownx.superfences.fence_code_format"),
                }],
            }},
            "pymdownx.tabbed",
            "pymdownx.details",
        ],
    }

    site_dir.mkdir(parents=True, exist_ok=True)
    with open(site_dir / "mkdocs.yml", "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, allow_unicode=True)


def _build_theme(props: SiteProperties) -> dict:
    theme: dict = {"name": "material"}

    # Palette
    theme["palette"] = _build_palette(props)

    # Features
    features = [
        "navigation.sections",
        "navigation.indexes",
        "navigation.expand",
        "navigation.top",
        "search.suggest",
        "search.highlight",
    ]
    if props.navigation_instant:
        features.append("navigation.instant")
    if props.navigation_tabs:
        features.append("navigation.tabs")
    theme["features"] = features

    # Favicon and logo
    if props.favicon:
        theme["favicon"] = props.favicon
    if props.logo:
        theme["logo"] = props.logo

    return theme


def _build_palette(props: SiteProperties) -> list[dict] | dict:
    """Build palette config based on theme mode and color settings."""
    named_primary = props.primary_color if props.primary_color and props.primary_color in MATERIAL_NAMED_COLORS else None
    named_accent = props.accent_color if props.accent_color and props.accent_color in MATERIAL_NAMED_COLORS else None

    def _palette_entry(scheme: str, toggle: dict | None = None) -> dict:
        entry: dict = {"scheme": scheme}
        if named_primary:
            entry["primary"] = named_primary
        if named_accent:
            entry["accent"] = named_accent
        if toggle:
            entry["toggle"] = toggle
        return entry

    if props.theme == "light":
        return _palette_entry("default")
    if props.theme == "dark":
        return _palette_entry("slate")

    # auto: light/dark toggle
    return [
        _palette_entry("default", {"icon": "material/brightness-7", "name": "Dark mode"}),
        _palette_entry("slate", {"icon": "material/brightness-4", "name": "Light mode"}),
    ]


def _build_extra_css(props: SiteProperties) -> list[str]:
    css = []
    if props.has_hex_colors():
        css.append("css/color-overrides.css")
    if props.full_width:
        css.append("css/full-width.css")
    css.append("css/extra.css")
    if props.custom_css:
        css.append(props.custom_css)
    return css


def _build_nav(workspace: Workspace) -> list:
    """Build left sidebar nav with sections."""
    nav: list = [{"Home": "index.md"}]

    # Workspace documentation sections
    sorted_sections = sorted(workspace.documentation.sections, key=lambda s: s.order)
    for section in sorted_sections[1:]:
        slug = section_slug(section)
        title = section_title(section)
        nav.append({title: f"documentation/{slug}.md"})

    # Actors section (expandable)
    actors_nav = _actors_nav(workspace)
    if actors_nav:
        nav.append({"Actors": actors_nav})

    # Software Systems section (expandable)
    systems_nav = _systems_nav(workspace)
    nav.append({"Software Systems": systems_nav})

    # Workspace decisions
    decisions_nav = _decisions_nav(workspace.documentation, prefix="decisions")
    if decisions_nav:
        nav.append({"Architecture Decision Records": decisions_nav})

    return nav


def _decisions_nav(documentation: Documentation, prefix: str) -> list:
    decisions = documentation.decisions
    if not decisions:
        return []

    nav: list = [{"Overview": f"{prefix}/index.md"}]
    for d in sorted(decisions, key=lambda d: int(d.id)):
        nav.append({d.title: f"{prefix}/{d.id}.md"})
    return nav


def _actors_nav(workspace: Workspace) -> list:
    if not workspace.people:
        return []
    nav: list = [{"index": "actors/index.md"}]
    for person in sorted(workspace.people, key=lambda p: p.name):
        slug = normalize_name(person.name)
        nav.append({person.name: f"actors/{slug}/index.md"})
    return nav


def _systems_nav(workspace: Workspace) -> list:
    nav: list = [{"index": "software-systems/index.md"}]

    for ss in sorted(workspace.software_systems, key=lambda s: s.name):
        slug = normalize_name(ss.name)
        nav.append({ss.name: f"software-systems/{slug}/index.md"})

    return nav
