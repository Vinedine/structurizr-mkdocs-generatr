"""Generate mkdocs.yml from a parsed Structurizr workspace."""

from __future__ import annotations

from pathlib import Path

import yaml

from .bounded_context import BoundedContextModel
from .properties import MATERIAL_NAMED_COLORS, SiteProperties
from .workspace import (
    Documentation,
    Workspace,
    extract_zone_name,
    normalize_name,
    section_slug,
    section_title,
    sort_zone_views,
)


class _PythonName:
    """Wrapper to emit !!python/name: YAML tags for MkDocs config."""
    def __init__(self, value: str) -> None:
        self.value = value


def _python_name_representer(dumper: yaml.Dumper, data: _PythonName) -> yaml.Node:
    return yaml.ScalarNode(tag="tag:yaml.org,2002:python/name:" + data.value, value="")


class _PythonObjectApply:
    """Wrapper to emit !!python/object/apply: YAML tags (factory calls with kwargs)."""
    def __init__(self, value: str, kwds: dict | None = None) -> None:
        self.value = value
        self.kwds = kwds or {}


def _python_object_apply_representer(dumper: yaml.Dumper, data: _PythonObjectApply) -> yaml.Node:
    if data.kwds:
        mapping = dumper.represent_mapping("tag:yaml.org,2002:map", {"kwds": data.kwds})
        return yaml.MappingNode(
            tag="tag:yaml.org,2002:python/object/apply:" + data.value,
            value=mapping.value,
        )
    return yaml.ScalarNode(tag="tag:yaml.org,2002:python/object/apply:" + data.value, value="")


yaml.add_representer(_PythonName, _python_name_representer)
yaml.add_representer(_PythonObjectApply, _python_object_apply_representer)


def generate_mkdocs_config(
    workspace: Workspace, site_dir: Path, props: SiteProperties,
    bc_model: BoundedContextModel | None = None,
) -> None:
    """Generate mkdocs.yml for the workspace."""
    config = {
        "site_name": workspace.name or "Architecture",
        "site_description": props.description or workspace.description,
        **({"copyright": props.copyright} if props.copyright else {}),
        **({"site_url": props.site_url} if props.site_url else {}),
        "theme": _build_theme(props),
        "plugins": ["search", "glightbox"],
        "docs_dir": "docs",
        "use_directory_urls": False,
        "nav": _build_nav(workspace, bc_model),
        "extra_css": _build_extra_css(props),
        "extra_javascript": ["js/external-links.js", "js/diagram-zoom.js", "js/tab-anchor.js"],
        "markdown_extensions": [
            "admonition",
            "tables",
            "attr_list",
            "md_in_html",
            {"toc": {"permalink": True, "toc_depth": 2}},
            {"pymdownx.superfences": {
                "custom_fences": [{
                    "name": "mermaid",
                    "class": "mermaid",
                    "format": _PythonName("pymdownx.superfences.fence_code_format"),
                }],
            }},
            {"pymdownx.tabbed": {
                "alternate_style": True,
                "slugify": _PythonObjectApply(
                    "pymdownx.slugs.slugify", kwds={"case": "lower"},
                ),
            }},
            "pymdownx.details",
            {"pymdownx.emoji": {
                "emoji_index": _PythonName("material.extensions.emoji.twemoji"),
                "emoji_generator": _PythonName("material.extensions.emoji.to_svg"),
            }},
            {"pymdownx.highlight": {"anchor_linenums": True}},
            "pymdownx.inlinehilite",
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
        features.append("navigation.tabs.sticky")
    theme["features"] = features

    # Favicon and logo
    if props.favicon:
        theme["favicon"] = props.favicon
    if props.logo:
        theme["logo"] = props.logo

    return theme


def _build_palette(props: SiteProperties) -> list[dict] | dict:
    """Build palette config based on theme mode and color settings."""
    named_primary = (
        props.primary_color if props.primary_color and props.primary_color in MATERIAL_NAMED_COLORS else None
    )
    named_accent = (
        props.accent_color if props.accent_color and props.accent_color in MATERIAL_NAMED_COLORS else None
    )

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


def _build_nav(workspace: Workspace, bc_model: BoundedContextModel | None = None) -> list:
    """Build left sidebar nav with sections."""
    # Workspace documentation sections under "Main" section (index.md is the home page)
    skip_slugs = {"bounded-contexts", "capability-map"} if bc_model else set()
    sorted_sections = sorted(workspace.documentation.sections, key=lambda s: s.order)
    home_title = section_title(sorted_sections[0]) if sorted_sections else "Home"
    main_nav: list = [{home_title: "index.md"}]
    for section in sorted_sections[1:]:
        slug = section_slug(section)
        if slug in skip_slugs:
            continue
        title = section_title(section)
        main_nav.append({title: f"documentation/{slug}.md"})
    nav: list = [{"Main": main_nav}]

    # Capability Map section with children (when auto-generated from boundedContext.mmd)
    if bc_model:
        bc_nav: list = [{"Capability Map": "capability-map/index.md"}]
        for ctx in bc_model.contexts:
            ctx_slug = normalize_name(ctx.name)
            bc_nav.append({ctx.name: f"capability-map/{ctx_slug}.md"})
        nav.append({"Capability Map": bc_nav})

    # Persons section (expandable)
    persons_nav = _persons_nav(workspace)
    if persons_nav:
        nav.append({"Persons": persons_nav})

    # Software Systems section (expandable)
    systems_nav = _systems_nav(workspace)
    nav.append({"Software Systems": systems_nav})

    # Infrastructure section (before ADRs)
    infra_nav = _infrastructure_nav(workspace)
    if infra_nav:
        nav.append({"Infrastructure": infra_nav})

    # Workspace decisions
    decisions_nav = _decisions_nav(workspace.documentation, prefix="adrs")
    if decisions_nav:
        nav.append({"Architecture Decision Records": decisions_nav})

    return nav


def _decisions_nav(documentation: Documentation, prefix: str) -> list:
    decisions = documentation.decisions
    if not decisions:
        return []

    nav: list = [{"Architecture Decision Records": f"{prefix}/index.md"}]
    for d in sorted(decisions, key=lambda d: int(d.id)):
        nav.append({f"{d.id}. {d.title}": f"{prefix}/{d.id}.md"})
    return nav


def _persons_nav(workspace: Workspace) -> list:
    if not workspace.people:
        return []
    nav: list = [{"Persons": "persons/index.md"}]
    for person in sorted(workspace.people, key=lambda p: p.name):
        slug = normalize_name(person.name)
        nav.append({person.name: f"persons/{slug}/index.md"})
    return nav


def _systems_nav(workspace: Workspace) -> list:
    nav: list = [{"Software Systems": "software-systems/index.md"}]

    groups = workspace.groups()
    if groups:
        # Nest systems under group sub-sections
        for group_name in groups:
            group_slug = normalize_name(group_name)
            group_nav: list = [{group_name: f"software-systems/{group_slug}/index.md"}]
            for ss in workspace.systems_in_group(group_name):
                slug = normalize_name(ss.name)
                group_nav.append({ss.name: f"software-systems/{slug}/index.md"})
            nav.append({group_name: group_nav})

        # Systems without a group (ungrouped) go at the end
        ungrouped = sorted(
            [ss for ss in workspace.software_systems if not ss.group],
            key=lambda s: s.name,
        )
        for ss in ungrouped:
            slug = normalize_name(ss.name)
            nav.append({ss.name: f"software-systems/{slug}/index.md"})
    else:
        # No groups — flat list like before
        for ss in sorted(workspace.software_systems, key=lambda s: s.name):
            slug = normalize_name(ss.name)
            nav.append({ss.name: f"software-systems/{slug}/index.md"})

    return nav


def _infrastructure_nav(workspace: Workspace) -> list:
    """Build Infrastructure section nav entries."""
    environments = workspace.deployment_environments()
    if not environments:
        return []

    nav: list = [{"Infrastructure": "infrastructure/index.md"}]

    for env in environments:
        env_slug = normalize_name(env)
        zone_views = workspace.zone_level_views(env)

        if zone_views:
            env_nav: list = [{env: f"infrastructure/{env_slug}/index.md"}]
            zone_views_sorted = sort_zone_views(zone_views)
            for v in zone_views_sorted:
                zone_name = extract_zone_name(v)
                zone_slug = normalize_name(zone_name)
                env_nav.append({zone_name: f"infrastructure/{env_slug}/{zone_slug}.md"})
            nav.append({env: env_nav})
        else:
            nav.append({env: [{env: f"infrastructure/{env_slug}/index.md"}]})

    return nav
