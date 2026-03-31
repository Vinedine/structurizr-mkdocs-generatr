"""Generate Markdown files from a parsed Structurizr workspace."""

from __future__ import annotations

import base64
import re
import shutil
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path

from .fileutils import write_file as _write_file
from .bounded_context import (
    BoundedContextModel,
    map_contexts,
    write_bounded_context_index,
    write_bounded_context_pages,
)
from .mermaid_utils import _iter_top_level_lines, add_mermaid_view_source
from .properties import SiteProperties
from .workspace import (
    VIEW_COMPONENT,
    VIEW_CONTAINER,
    VIEW_DEPLOYMENT,
    VIEW_DYNAMIC,
    VIEW_IMAGE,
    VIEW_SYSTEM_CONTEXT,
    Decision,
    Documentation,
    Section,
    SoftwareSystem,
    Workspace,
    View,
    extract_zone_name,
    normalize_name,
    section_slug,
    sort_zone_views,
)

_DESCRIPTION_HEADING_RE = re.compile(r"^(#{1,6}) Description\s*$")
_ANY_HEADING_RE = re.compile(r"^(#{1,6}) ")


@dataclass
class GenerateOptions:
    """Bundled options for markdown generation."""
    assets_dir: Path | None = None
    inline_puml_dir: Path | None = None
    puml_dir: Path | None = None
    props: SiteProperties = field(default_factory=SiteProperties)
    view_keys: set[str] = field(default_factory=set)
    puml_counter: list[int] = field(default_factory=lambda: [0])
    bc_model: BoundedContextModel | None = None


def generate_markdown(
    workspace: Workspace, docs_dir: Path, svg_dir: Path,
    opts: GenerateOptions | None = None,
) -> None:
    """Generate all Markdown files for the MkDocs site."""
    if opts is None:
        opts = GenerateOptions()
    opts.view_keys = {v.key for v in workspace.views}
    opts.puml_counter = [0]

    docs_dir.mkdir(parents=True, exist_ok=True)

    _copy_workspace_assets(opts.assets_dir, docs_dir)
    _write_home_page(workspace, docs_dir, opts)
    _write_workspace_decisions(workspace.documentation, docs_dir, opts.view_keys)
    _write_workspace_docs(workspace.documentation, docs_dir, opts)
    _write_persons_index(workspace, docs_dir)
    _write_person_pages(workspace, docs_dir)
    _write_software_systems_index(workspace, docs_dir, opts.props)
    _write_group_pages(workspace, docs_dir, opts.props)
    _write_infrastructure_pages(workspace, docs_dir)
    _copy_diagrams(svg_dir, docs_dir, opts.puml_dir)
    _write_image_views(workspace, docs_dir)

    _copy_static_assets(docs_dir)
    _generate_color_overrides(opts.props, docs_dir)
    _generate_full_width_css(opts.props, docs_dir)
    _generate_external_links_js(opts.props, docs_dir)

    if opts.bc_model:
        system_map, cap_map = map_contexts(opts.bc_model, workspace)
        write_bounded_context_index(
            opts.bc_model, system_map, cap_map, docs_dir,
            mermaid_view_source=opts.props.mermaid_view_source,
        )
        write_bounded_context_pages(
            opts.bc_model, system_map, cap_map, workspace, docs_dir,
            mermaid_view_source=opts.props.mermaid_view_source,
        )

    for ss in workspace.software_systems:
        _write_software_system_pages(workspace, ss, docs_dir, opts)


def _copy_workspace_assets(assets_dir: Path | None, docs_dir: Path) -> None:
    if not assets_dir or not assets_dir.is_dir():
        return
    for item in assets_dir.iterdir():
        dest = docs_dir / item.name
        if item.is_dir():
            shutil.copytree(str(item), str(dest), dirs_exist_ok=True)
        elif item.is_file():
            shutil.copy2(str(item), dest)


def _copy_static_assets(docs_dir: Path) -> None:
    static = resources.files("structurizr_mkdocs_generatr") / "static"
    dest_dirs = {"css": docs_dir / "css", "js": docs_dir / "js"}
    for d in dest_dirs.values():
        d.mkdir(parents=True, exist_ok=True)
    for asset in static.iterdir():
        if not asset.is_file():
            continue
        ext = str(asset.name).rsplit(".", 1)[-1]
        dest = dest_dirs.get(ext, docs_dir / "css")
        shutil.copy2(str(asset), dest / asset.name)


def _generate_color_overrides(props: SiteProperties, docs_dir: Path) -> None:
    """Generate css/color-overrides.css when hex colors are configured."""
    hex_colors = props.hex_colors()
    if not hex_colors:
        return

    css_var_map = {
        "primary": "--md-primary-fg-color",
        "header_text": "--md-primary-bg-color",
        "accent": "--md-accent-fg-color",
    }
    lines = [":root {"]
    for key, color in hex_colors.items():
        lines.append(f"  {css_var_map[key]}: {color};")
    lines.append("}")

    (docs_dir / "css" / "color-overrides.css").write_text("\n".join(lines), encoding="utf-8")


def _generate_full_width_css(props: SiteProperties, docs_dir: Path) -> None:
    """Generate css/full-width.css when fullWidth is enabled."""
    if not props.full_width:
        return

    css = """\
.md-grid {
  max-width: none;
}
"""
    (docs_dir / "css" / "full-width.css").write_text(css, encoding="utf-8")


def _generate_external_links_js(props: SiteProperties, docs_dir: Path) -> None:
    """Generate external-links.js with configurable SVG link target."""
    target = props.svg_link_target
    js = f'''// Open external links in a new tab, SVG links use target="{target}"
document.addEventListener("DOMContentLoaded", function () {{
  document.querySelectorAll("a[href]").forEach(function (link) {{
    if (link.hostname && link.hostname !== window.location.hostname) {{
      link.setAttribute("target", "_blank");
      link.setAttribute("rel", "noopener noreferrer");
    }}
  }});
  document.querySelectorAll("object[data$='.svg'] a, svg a").forEach(function (link) {{
    link.setAttribute("target", "{target}");
  }});
}});
'''
    (docs_dir / "js" / "external-links.js").write_text(js, encoding="utf-8")


def _write_home_page(workspace: Workspace, docs_dir: Path, opts: GenerateOptions) -> None:
    sections = workspace.documentation.sections
    if sections:
        first = sorted(sections, key=lambda s: s.order)[0]
        content = _resolve_embeds(first.content, opts.view_keys, "diagrams/")
        content = _rewrite_asset_paths(content, "")
        if opts.inline_puml_dir:
            content = _extract_puml_blocks(content, opts.inline_puml_dir, "diagrams/", opts.puml_counter)
        content = add_mermaid_view_source(content, opts.props.mermaid_view_source)
    else:
        content = f"# {workspace.name}\n\n{workspace.description}\n"
    _write_file(docs_dir / "index.md", content)


def _write_workspace_decisions(documentation: Documentation, docs_dir: Path, view_keys: set[str] | None = None) -> None:
    decisions = documentation.decisions
    if not decisions:
        return

    decisions_dir = docs_dir / "adrs"

    lines = [
        '??? question "What questions does this answer?"\n\n'
        "    - *What architectural decisions have been made and why?*\n"
        "    - *What was the context and status of each decision?*\n"
        "    - *How have our architectural choices evolved over time?*\n"
        "    - *Which decisions are still proposed vs. accepted or superseded?*\n\n"
    ]
    lines.append("| ID | Date | Status | Title | Context |\n")
    lines.append("|---|---|---|---|---|\n")
    for d in sorted(decisions, key=lambda d: int(d.id)):
        date = d.date[:10] if d.date else ""
        context = _extract_decision_context(d.content)
        lines.append(f"| {d.id} | {date} | {d.status} | [{d.title}]({d.id}.md) | {context} |\n")
    _write_file(decisions_dir / "index.md", "".join(lines))

    decision_ids = {d.id for d in decisions}
    for d in decisions:
        content = _rewrite_decision_links(d.content, decision_ids)
        if view_keys:
            content = _resolve_embeds(content, view_keys, "../diagrams/")
        _write_file(decisions_dir / f"{d.id}.md", content)


_CONTEXT_SECTION_RE = re.compile(r"## Context\s*\n\s*\n(.+?)(?:\n\s*\n|\n##|\Z)", re.DOTALL)


def _extract_decision_context(content: str) -> str:
    """Extract the first paragraph of the ## Context section from decision content."""
    match = _CONTEXT_SECTION_RE.search(content)
    if not match:
        return ""
    first_para = match.group(1).strip().split("\n\n")[0]
    # Collapse to single line for table cell
    return " ".join(first_para.split())


def _rewrite_decision_links(content: str, decision_ids: set[str]) -> str:
    """Rewrite anchor links like (#3) to relative file links."""
    def _replace(m: re.Match) -> str:
        if m.group(1) in decision_ids:
            return f"]({m.group(1)}.md)"
        return m.group(0)

    return re.sub(r"\]\(#(\d+)\)", _replace, content)


def _rewrite_absolute_decision_links(content: str, prefix: str) -> str:
    """Rewrite absolute /decisions/{id}/ links to relative paths."""
    return re.sub(r"\]\(/decisions/(\d+)/?\)", lambda m: f"]({prefix}{m.group(1)}.md)", content)


def _write_workspace_docs(documentation: Documentation, docs_dir: Path, opts: GenerateOptions) -> None:
    sections = documentation.sections
    if len(sections) <= 1:
        return

    docs_sections_dir = docs_dir / "documentation"
    sorted_sections = sorted(sections, key=lambda s: s.order)

    for section in sorted_sections[1:]:
        slug = section_slug(section)
        content = _resolve_embeds(section.content, opts.view_keys, "../diagrams/")
        content = _rewrite_asset_paths(content, "../")
        if opts.inline_puml_dir:
            content = _extract_puml_blocks(content, opts.inline_puml_dir, "../diagrams/", opts.puml_counter)
        content = add_mermaid_view_source(content, opts.props.mermaid_view_source)
        _write_file(docs_sections_dir / f"{slug}.md", content)


def _write_persons_index(workspace: Workspace, docs_dir: Path) -> None:
    if not workspace.people:
        return
    lines = [
        '??? question "What questions does this answer?"\n\n'
        "    - *Who are the persons interacting with our systems?*\n"
        "    - *Which systems does a specific person interact with?*\n"
        "    - *How many systems does each person depend on?*\n"
        "    - *Are there persons with no system interactions?*\n\n"
    ]
    lines.append("| Name | Description | Software Systems |\n")
    lines.append("|---|---|---|\n")
    for person in sorted(workspace.people, key=lambda p: p.name):
        slug = normalize_name(person.name)
        system_ids = {
            ss.id
            for r in person.relationships
            for ss in [workspace.system_for_element_id(r.destination_id)]
            if ss
        }
        count = len(system_ids)
        lines.append(f"| [{person.name}]({slug}/index.md) | {person.description} | {count} |\n")
    _write_file(docs_dir / "persons" / "index.md", "".join(lines))


def _write_person_pages(workspace: Workspace, docs_dir: Path) -> None:
    for person in sorted(workspace.people, key=lambda p: p.name):
        slug = normalize_name(person.name)
        user_dir = docs_dir / "persons" / slug

        lines = [f"# {person.name}\n\n"]
        if person.description:
            lines.append(f"{person.description}\n\n")

        person_views = workspace.views_for_person(person.id)
        if person_views:
            lines.append("## Context\n\n")
            for v in person_views:
                lines.append(f"{_diagram_embed(v)}\n\n")

        _write_file(user_dir / "index.md", "".join(lines))


def _write_software_systems_index(workspace: Workspace, docs_dir: Path, props: SiteProperties | None = None) -> None:
    lines = [
        '??? question "What questions does this answer?"\n\n'
        "    - *What systems exist in our landscape and what do they do?*\n"
        "    - *Which systems are internal and which are external?*\n"
        "    - *How do our systems relate to each other at a high level?*\n"
        "    - *Who owns or is responsible for a given system?*\n\n"
    ]

    sw_view = next(
        (v for v in workspace.landscape_views()
         if v.key == "SystemLandscapeSoftwareSystems"),
        None,
    )
    if sw_view:
        lines.append(f"{_diagram_embed(sw_view, '../diagrams/')}\n\n")

    _write_file(docs_dir / "software-systems" / "index.md", "".join(lines))


def _write_group_pages(workspace: Workspace, docs_dir: Path, props: SiteProperties | None = None) -> None:
    """Write an index page for each group with its landscape diagram and system table."""
    for group_name in workspace.groups():
        group_slug = normalize_name(group_name)
        group_dir = docs_dir / "software-systems" / group_slug
        lines = [f"# {group_name}\n\n"]

        description = workspace.group_description(group_name)
        if description:
            lines.append(f"{description}\n\n")

        # Group landscape diagram
        group_view = workspace.group_landscape_view(group_name)
        if group_view:
            lines.append(f"## System Landscape\n\n{_diagram_embed(group_view, '../../diagrams/')}\n\n")

        _write_file(group_dir / "index.md", "".join(lines))


def _write_infrastructure_pages(workspace: Workspace, docs_dir: Path) -> None:
    """Generate Infrastructure section: index + per-environment + per-zone pages."""
    infra_dir = docs_dir / "infrastructure"

    environments = workspace.deployment_environments()
    if not environments:
        return

    # Infrastructure index page
    lines = [
        '??? question "What questions does this answer?"\n\n'
        "    - *Where are our systems deployed in each environment?*\n"
        "    - *Which cloud providers and on-premise zones do we use?*\n"
        "    - *How does the infrastructure differ between production and lower environments?*\n"
        "    - *What is the multi-cloud strategy and how are workloads distributed?*\n\n"
    ]
    lines.append("| Environment | Description | Zones |\n")
    lines.append("|---|---|---|\n")
    for env in environments:
        env_slug = normalize_name(env)
        env_desc = workspace.environment_description(env)
        zone_views = workspace.zone_level_views(env)
        zone_count = len(zone_views) if zone_views else 1
        lines.append(f"| [{env}]({env_slug}/index.md) | {env_desc} | {zone_count} |\n")
    _write_file(infra_dir / "index.md", "".join(lines))

    # Per-environment pages
    for env in environments:
        env_slug = normalize_name(env)
        env_dir = infra_dir / env_slug

        env_lines = [f"# {env}\n\n"]
        env_desc = workspace.environment_description(env)
        if env_desc:
            env_lines.append(f"{env_desc}\n\n")

        zone_views = workspace.zone_level_views(env)

        if zone_views:
            zone_views_sorted = sort_zone_views(zone_views)

            for v in zone_views_sorted:
                zone_name = extract_zone_name(v)
                zone_slug = normalize_name(zone_name)
                env_lines.append(f"- [{zone_name}]({zone_slug}.md)\n")

            _write_file(env_dir / "index.md", "".join(env_lines))

            # Per-zone pages
            for v in zone_views_sorted:
                zone_name = extract_zone_name(v)
                zone_slug = normalize_name(zone_name)
                zone_lines = [f"# {zone_name}\n\n"]
                zone_desc = workspace.zone_description(env, zone_name)
                if zone_desc:
                    zone_lines.append(f"{zone_desc}\n\n")
                zone_lines.append(f"{_diagram_embed(v, '../../diagrams/')}\n\n")
                _write_file(env_dir / f"{zone_slug}.md", "".join(zone_lines))
        else:
            # No zone-level views — description only
            _write_file(env_dir / "index.md", "".join(env_lines))


# Tags that are structural / implicit — not shown as badges
_HIDDEN_TAGS = {"Element", "Software System", "Person", "Container", "Component"}


def _element_tag_badges(tags: list[str], element_styles: dict[str, dict[str, str]]) -> str:
    """Return HTML spans for display tags (External System, New, Shared, etc.)."""
    badges = []
    for tag in tags:
        if tag in _HIDDEN_TAGS:
            continue
        # Only show tags that have a defined style in the workspace
        if tag not in element_styles:
            continue
        badges.append(f' <span class="element-tag">{tag}</span>')
    return "".join(badges)


def _build_system_heading(
    workspace: Workspace, ss: SoftwareSystem,
) -> tuple[list[str], Section | None]:
    """Build the heading, description, and URL lines for a software system page.

    Returns the lines and the intro section (if found).
    """
    lines: list[str] = []
    tag_html = _element_tag_badges(ss.tags, workspace.element_styles)
    group_html = f" <span class=\"group-tag\">{ss.group}</span>" if ss.group else ""
    lines.append(f"# {ss.name}{group_html}{tag_html}\n\n")

    intro = next(
        (s for s in ss.documentation.sections if s.filename and s.filename.endswith("introduction.md")),
        None,
    )
    intro_description = _extract_description_paragraph(intro.content) if intro else None
    description = intro_description or ss.description
    if description:
        lines.append(f"{description}\n\n")
    if ss.url:
        lines.append(f"**URL:** [{ss.url}]({ss.url})\n\n")

    return lines, intro


def _build_info_tab(
    ss: SoftwareSystem, intro: Section | None, view_keys: set[str],
) -> str | None:
    """Build the Info tab content from introduction, decisions, and doc sections."""
    info_lines: list[str] = []
    if intro:
        intro_content = _strip_description_section(intro.content)
        info_lines.append(f"{_bump_headings(intro_content, 1)}\n\n")
    if ss.documentation.decisions:
        _append_decisions(ss.documentation.decisions, info_lines)
    other_sections = [s for s in ss.documentation.sections if s is not intro]
    if other_sections:
        _append_sections(other_sections, info_lines, view_keys)
    return "".join(info_lines) if info_lines else None


def _build_diagram_tabs(workspace: Workspace, ss: SoftwareSystem) -> list[tuple[str, str]]:
    """Build one tab per view type for a software system's diagrams."""
    system_views = workspace.views_for_system(ss.id)
    view_groups: dict[str, list[View]] = {}
    for v in system_views:
        view_groups.setdefault(v.type, []).append(v)

    type_labels = {
        VIEW_SYSTEM_CONTEXT: "Context views",
        VIEW_CONTAINER: "Container views",
        VIEW_COMPONENT: "Component views",
        VIEW_DYNAMIC: "Dynamic views",
        VIEW_DEPLOYMENT: "Deployment views",
        VIEW_IMAGE: "Image views",
    }

    tabs: list[tuple[str, str]] = []
    for view_type, label in type_labels.items():
        group = view_groups.get(view_type, [])
        if not group:
            continue
        tab_lines: list[str] = []
        for v in group:
            if view_type in (VIEW_DEPLOYMENT, VIEW_DYNAMIC):
                title = v.title or v.description or v.key
                tab_lines.append(f"### {title}\n\n")
                if v.description and v.description != title:
                    tab_lines.append(f"{v.description}\n\n")
            tab_lines.append(f"{_diagram_embed(v)}\n\n")
        tabs.append((label, "".join(tab_lines)))
    return tabs


def _build_dependencies_tab(
    workspace: Workspace, ss: SoftwareSystem,
) -> str | None:
    """Build the Dependencies tab with inbound/outbound tables."""
    inbound, outbound = workspace.dependencies_for_system(ss.id)
    if not inbound and not outbound:
        return None

    dep_lines: list[str] = []
    dep_lines.append("### Inbound\n\n")
    if inbound:
        dep_lines.append("| System | Description | Technology |\n")
        dep_lines.append("|---|---|---|\n")
        for element_id, name, desc, tech in inbound:
            link = _dep_link(workspace, name, element_id)
            dep_lines.append(f"| {link} | {desc} | {tech} |\n")
    else:
        dep_lines.append("No inbound dependencies.\n")
    dep_lines.append("\n")
    dep_lines.append("### Outbound\n\n")
    if outbound:
        dep_lines.append("| System | Description | Technology |\n")
        dep_lines.append("|---|---|---|\n")
        for element_id, name, desc, tech in outbound:
            link = _dep_link(workspace, name, element_id)
            dep_lines.append(f"| {link} | {desc} | {tech} |\n")
    else:
        dep_lines.append("No outbound dependencies.\n")
    dep_lines.append("\n")
    return "".join(dep_lines)


def _render_tabs(tabs: list[tuple[str, str]], lines: list[str]) -> None:
    """Render tabs as MkDocs tabbed content, or flat content if only one tab."""
    if len(tabs) > 1:
        for tab_title, tab_content in tabs:
            lines.append(f'=== "{tab_title}"\n\n')
            for line in tab_content.splitlines(keepends=True):
                lines.append(f"    {line}" if line.strip() else "\n")
            lines.append("\n")
    elif tabs:
        lines.append(tabs[0][1])


def _write_software_system_pages(
    workspace: Workspace, ss: SoftwareSystem, docs_dir: Path, opts: GenerateOptions,
) -> None:
    slug = normalize_name(ss.name)
    ss_dir = docs_dir / "software-systems" / slug

    lines, intro = _build_system_heading(workspace, ss)

    tabs: list[tuple[str, str]] = []

    info_content = _build_info_tab(ss, intro, opts.view_keys)
    if info_content:
        tabs.append(("Info", info_content))

    tabs.extend(_build_diagram_tabs(workspace, ss))

    deps_content = _build_dependencies_tab(workspace, ss)
    if deps_content:
        tabs.append(("Dependencies", deps_content))

    _render_tabs(tabs, lines)

    content = _resolve_embeds("".join(lines), opts.view_keys, "../../diagrams/")
    content = _rewrite_asset_paths(content, "../../")
    if opts.inline_puml_dir:
        content = _extract_puml_blocks(content, opts.inline_puml_dir, "../../diagrams/", opts.puml_counter)
    content = add_mermaid_view_source(content, opts.props.mermaid_view_source)
    if opts.bc_model:
        content = _rewrite_bc_links(content, opts.bc_model)
    content = _rewrite_absolute_decision_links(content, "../../adrs/")
    _write_file(ss_dir / "index.md", content)


def _rewrite_bc_links(content: str, bc_model: BoundedContextModel) -> str:
    """Rewrite bounded-context references in introduction docs.

    - Plain-text context names under a ``## Bounded Context`` heading are
      turned into links: ``- Name`` → ``- [Name](../../capability-map/{slug}.md)``
    - ``[Label](ENTITY_ID)`` → ``[Label](../../capability-map/{context-slug}.md)``
    """
    ctx_slugs = {normalize_name(c.name): c.name for c in bc_model.contexts}

    # Turn plain-text bounded-context names into links
    result_lines: list[str] = []
    in_bc_section = False
    for line in content.splitlines(keepends=True):
        stripped = line.strip()
        if stripped.startswith("## "):
            in_bc_section = stripped in ("## Bounded Context", "## Bounded Contexts")
        if in_bc_section and stripped.startswith("- "):
            name = stripped[2:].strip()
            slug = normalize_name(name)
            if slug in ctx_slugs:
                line = line.replace(
                    stripped, f"- [{name}](../../capability-map/{slug}.md)"
                )
        result_lines.append(line)
    content = "".join(result_lines)

    # Rewrite entity ID links to their bounded-context page
    def _replace_entity(m: re.Match) -> str:
        entity_id = m.group(1)
        ctx_name = bc_model.entity_to_context.get(entity_id)
        if ctx_name:
            ctx_slug = normalize_name(ctx_name)
            return f"](../../capability-map/{ctx_slug}.md)"
        return m.group(0)

    content = re.sub(r"\]\(([A-Z_][A-Z_0-9]*)\)", _replace_entity, content)
    return content


def _dep_link(workspace: Workspace, name: str, element_id: str) -> str:
    """Create a markdown link for a dependency target — system or person."""
    slug = normalize_name(name)
    for p in workspace.people:
        if p.id == element_id:
            return f"[{name}](../../persons/{slug}/index.md)"
    return f"[{name}](../{slug}/index.md)"


def _append_decisions(decisions: list[Decision], lines: list[str]) -> None:
    lines.append("## Architecture Decision Records\n\n")
    lines.append("| ID | Date | Status | Title | Context |\n")
    lines.append("|---|---|---|---|---|\n")
    sorted_decisions = sorted(decisions, key=lambda d: int(d.id))
    for d in sorted_decisions:
        date = d.date[:10] if d.date else ""
        context = _extract_decision_context(d.content)
        lines.append(f"| {d.id} | {date} | {d.status} | {d.title} | {context} |\n")
    lines.append("\n")

    for d in sorted_decisions:
        lines.append(f"{_bump_headings(d.content, 2)}\n\n")


def _append_sections(sections: list[Section], lines: list[str], view_keys: set[str] | None = None) -> None:
    lines.append("## Documentation\n\n")
    for section in sorted(sections, key=lambda s: s.order):
        content = section.content
        if view_keys:
            content = _resolve_embeds(content, view_keys, "../../diagrams/")
        lines.append(f"{_bump_headings(content, 2)}\n\n")


def _strip_description_section(content: str) -> str:
    """Remove the first Description heading section from introduction content."""
    lines = content.split("\n")
    result: list[str] = []
    skipping = False
    skip_level = 0
    for line in lines:
        if not skipping and _DESCRIPTION_HEADING_RE.match(line):
            skipping = True
            skip_level = len(line) - len(line.lstrip("#"))
            continue
        if skipping:
            heading_match = _ANY_HEADING_RE.match(line)
            if heading_match and len(heading_match.group(1)) <= skip_level:
                skipping = False
            else:
                continue
        result.append(line)
    return "\n".join(result).lstrip("\n")


def _extract_description_paragraph(content: str) -> str | None:
    """Extract the first paragraph under the # Description heading."""
    lines = content.split("\n")
    in_desc = False
    for line in lines:
        if not in_desc and _DESCRIPTION_HEADING_RE.match(line):
            in_desc = True
            continue
        if in_desc:
            if line.strip() == "":
                continue
            if _ANY_HEADING_RE.match(line):
                return None
            return line.strip()
    return None


def _bump_headings(content: str, levels: int) -> str:
    """Increase all markdown heading levels by *levels* (e.g. # → ### when levels=2), clamped to h6."""
    def _clamp(m: re.Match) -> str:
        new_level = min(len(m.group(1)) + levels, 6)
        return f"{'#' * new_level} "

    return re.sub(r"^(#{1,6})\s", _clamp, content, flags=re.MULTILINE)


def _resolve_embeds(content: str, view_keys: set[str], diagrams_prefix: str) -> str:
    """Replace ![alt](embed:ViewKey) with <object> tags for clickable SVG links."""
    def _replace(m: re.Match) -> str:
        alt, key = m.group(1), m.group(2)
        if key in view_keys:
            path = f"{diagrams_prefix}structurizr-{key}.svg"
            return f'<object data="{path}" type="image/svg+xml" class="diagram">{alt}</object>'
        return m.group(0)

    return re.sub(r"!\[([^\]]*)\]\(embed:([^)]+)\)", _replace, content)


def _rewrite_asset_paths(content: str, prefix: str) -> str:
    """Rewrite absolute image paths like (/pictures/foo.png) to relative paths."""
    return re.sub(
        r"(!\[[^\]]*\])\(/([^)]+)\)",
        lambda m: f"{m.group(1)}({prefix}{m.group(2)})",
        content,
    )


def _extract_puml_blocks(content: str, puml_dir: Path, diagrams_prefix: str, counter: list[int] | None = None) -> str:
    """Extract top-level ```puml blocks, write .puml files, replace with image refs."""
    if counter is None:
        counter = [0]
    puml_dir.mkdir(parents=True, exist_ok=True)

    result: list[str] = []
    in_puml = False
    puml_lines: list[str] = []

    for line, nested in _iter_top_level_lines(content):
        if nested:
            result.append(line)
            continue

        stripped = line.strip()
        if not in_puml and stripped == "```puml":
            in_puml = True
            puml_lines = []
            continue
        if in_puml:
            if stripped == "```":
                counter[0] += 1
                name = f"inline-{counter[0]}"
                puml_file = puml_dir / f"{name}.puml"
                puml_file.write_text("\n".join(puml_lines), encoding="utf-8")
                result.append(f"![Diagram]({diagrams_prefix}{name}.svg)")
                in_puml = False
            else:
                puml_lines.append(line)
            continue

        result.append(line)

    return "\n".join(result)


_IMAGE_EXTENSIONS = {"image/png": ".png", "image/jpeg": ".jpg", "image/gif": ".gif", "image/svg+xml": ".svg"}


def _diagram_path(view: View, prefix: str = "../../diagrams/") -> str:
    if view.content_type and view.content_type in _IMAGE_EXTENSIONS:
        ext = _IMAGE_EXTENSIONS[view.content_type]
        return f"{prefix}structurizr-{view.key}{ext}"
    return f"{prefix}structurizr-{view.key}.svg"


def _diagram_embed(view: View, prefix: str = "../../diagrams/") -> str:
    """Generate an <object> tag for SVG diagrams (supports clickable links) or <img> for raster."""
    path = _diagram_path(view, prefix)
    title = view.title or view.description or view.key
    if view.content_type and view.content_type in _IMAGE_EXTENSIONS and view.content_type != "image/svg+xml":
        return f"![{title}]({path})"
    return f'<object data="{path}" type="image/svg+xml" class="diagram">{title}</object>'


def _write_image_views(workspace: Workspace, docs_dir: Path) -> None:
    diagrams_dir = docs_dir / "diagrams"
    diagrams_dir.mkdir(parents=True, exist_ok=True)

    for view in workspace.views:
        if view.type != VIEW_IMAGE or not view.content:
            continue
        ext = _IMAGE_EXTENSIONS.get(view.content_type or "", ".png")
        filename = f"structurizr-{view.key}{ext}"
        # content is a data URI like "data:image/png;base64,iVBOR..."
        data = view.content
        if data.startswith("data:"):
            data = data.split(",", 1)[1]
        image_bytes = base64.b64decode(data)
        (diagrams_dir / filename).write_bytes(image_bytes)


def _copy_diagrams(svg_dir: Path, docs_dir: Path, puml_dir: Path | None = None) -> None:
    diagrams_dir = docs_dir / "diagrams"
    diagrams_dir.mkdir(parents=True, exist_ok=True)

    if svg_dir.exists():
        for svg_file in svg_dir.glob("*.svg"):
            shutil.copy2(svg_file, diagrams_dir / svg_file.name)

    if puml_dir and puml_dir.exists():
        for puml_file in puml_dir.glob("*.puml"):
            shutil.copy2(puml_file, diagrams_dir / puml_file.name)
