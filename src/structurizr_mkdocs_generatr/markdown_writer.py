"""Generate Markdown files from a parsed Structurizr workspace."""

from __future__ import annotations

import base64
import re
import shutil
from dataclasses import dataclass, field
from importlib import resources
from pathlib import Path

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
    normalize_name,
    section_slug,
)


@dataclass
class GenerateOptions:
    """Bundled options for markdown generation."""
    assets_dir: Path | None = None
    inline_puml_dir: Path | None = None
    puml_dir: Path | None = None
    props: SiteProperties = field(default_factory=SiteProperties)
    view_keys: set[str] = field(default_factory=set)
    puml_counter: list[int] = field(default_factory=lambda: [0])


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
    _write_workspace_decisions(workspace.documentation, docs_dir)
    _write_workspace_docs(workspace.documentation, docs_dir, opts)
    _write_actors_index(workspace, docs_dir)
    _write_actor_pages(workspace, docs_dir)
    _write_software_systems_index(workspace, docs_dir, opts.props)
    _copy_diagrams(svg_dir, docs_dir, opts.puml_dir)
    _write_image_views(workspace, docs_dir)

    _copy_static_assets(docs_dir)
    _generate_color_overrides(opts.props, docs_dir)
    _generate_full_width_css(opts.props, docs_dir)
    _generate_external_links_js(opts.props, docs_dir)

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


def _write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_home_page(workspace: Workspace, docs_dir: Path, opts: GenerateOptions) -> None:
    sections = workspace.documentation.sections
    if sections:
        first = sorted(sections, key=lambda s: s.order)[0]
        content = _resolve_embeds(first.content, opts.view_keys, "diagrams/")
        content = _rewrite_asset_paths(content, "")
        if opts.inline_puml_dir:
            content = _extract_puml_blocks(content, opts.inline_puml_dir, "diagrams/", opts.puml_counter)
        content = _add_mermaid_view_source(content)
    else:
        content = f"# {workspace.name}\n\n{workspace.description}\n"
    _write_file(docs_dir / "index.md", content)


def _write_workspace_decisions(documentation: Documentation, docs_dir: Path) -> None:
    decisions = documentation.decisions
    if not decisions:
        return

    decisions_dir = docs_dir / "decisions"

    lines = ["# Architecture Decision Records\n\n"]
    lines.append("| ID | Date | Status | Title |\n")
    lines.append("|---|---|---|---|\n")
    for d in sorted(decisions, key=lambda d: int(d.id)):
        date = d.date[:10] if d.date else ""
        lines.append(f"| {d.id} | {date} | {d.status} | [{d.title}]({d.id}.md) |\n")
    _write_file(decisions_dir / "index.md", "".join(lines))

    decision_ids = {d.id for d in decisions}
    for d in decisions:
        content = _rewrite_decision_links(d.content, decision_ids)
        _write_file(decisions_dir / f"{d.id}.md", content)


def _rewrite_decision_links(content: str, decision_ids: set[str]) -> str:
    """Rewrite anchor links like (#3) to relative file links."""
    def _replace(m: re.Match) -> str:
        if m.group(1) in decision_ids:
            return f"]({m.group(1)}.md)"
        return m.group(0)

    return re.sub(r"\]\(#(\d+)\)", _replace, content)


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
        content = _add_mermaid_view_source(content)
        _write_file(docs_sections_dir / f"{slug}.md", content)


def _write_actors_index(workspace: Workspace, docs_dir: Path) -> None:
    if not workspace.people:
        return
    lines = ["# Actors\n\n"]
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
    _write_file(docs_dir / "actors" / "index.md", "".join(lines))


def _write_actor_pages(workspace: Workspace, docs_dir: Path) -> None:
    for person in sorted(workspace.people, key=lambda p: p.name):
        slug = normalize_name(person.name)
        actor_dir = docs_dir / "actors" / slug

        lines = [f"# {person.name}\n\n"]
        if person.description:
            lines.append(f"{person.description}\n\n")

        person_views = workspace.views_for_person(person.id)
        if person_views:
            for v in person_views:
                lines.append(f"{_diagram_embed(v)}\n\n")

        _write_file(actor_dir / "index.md", "".join(lines))


def _write_software_systems_index(workspace: Workspace, docs_dir: Path, props: SiteProperties | None = None) -> None:
    external_tag = props.external_tag if props else None
    lines = ["# Software Systems\n\n"]
    lines.append("| Name | Description |\n")
    lines.append("|---|---|\n")
    for ss in sorted(workspace.software_systems, key=lambda s: s.name):
        slug = normalize_name(ss.name)
        name = ss.name
        if external_tag and external_tag in ss.tags:
            name = f"{ss.name} :material-open-in-new:{{ title=\"External\" }}"
        lines.append(f"| [{name}]({slug}/index.md) | {ss.description} |\n")
    _write_file(docs_dir / "software-systems" / "index.md", "".join(lines))


def _write_software_system_pages(
    workspace: Workspace, ss: SoftwareSystem, docs_dir: Path, opts: GenerateOptions,
) -> None:
    slug = normalize_name(ss.name)
    ss_dir = docs_dir / "software-systems" / slug

    lines = [f"# {ss.name}\n\n"]
    if ss.description:
        lines.append(f'<p class="subtitle">{ss.description}</p>\n\n')
    if ss.group:
        lines.append(f"**Group:** {ss.group}\n\n")
    if ss.url:
        lines.append(f"**URL:** [{ss.url}]({ss.url})\n\n")

    intro = next(
        (s for s in ss.documentation.sections if s.filename and s.filename.endswith("introduction.md")),
        None,
    )
    if intro:
        lines.append(f"{_bump_headings(intro.content, 1)}\n\n")

    system_views = workspace.views_for_system(ss.id)
    _append_diagrams(system_views, lines)
    _append_dependencies(workspace, ss, lines)

    if ss.documentation.decisions:
        _append_decisions(ss.documentation.decisions, lines)

    other_sections = [s for s in ss.documentation.sections if s is not intro]
    if other_sections:
        _append_sections(other_sections, lines, opts.view_keys)

    content = _resolve_embeds("".join(lines), opts.view_keys, "../../diagrams/")
    content = _rewrite_asset_paths(content, "../../")
    if opts.inline_puml_dir:
        content = _extract_puml_blocks(content, opts.inline_puml_dir, "../../diagrams/", opts.puml_counter)
    content = _add_mermaid_view_source(content)
    _write_file(ss_dir / "index.md", content)


def _append_diagrams(views: list[View], lines: list[str]) -> None:
    view_groups: dict[str, list[View]] = {}
    for v in views:
        view_groups.setdefault(v.type, []).append(v)

    type_labels = {
        VIEW_SYSTEM_CONTEXT: "Context View",
        VIEW_CONTAINER: "Container View",
        VIEW_COMPONENT: "Component Views",
        VIEW_DYNAMIC: "Dynamic Views",
        VIEW_DEPLOYMENT: "Deployment Views",
        VIEW_IMAGE: "Image Views",
    }

    for view_type, label in type_labels.items():
        group = view_groups.get(view_type, [])
        if not group:
            continue

        lines.append(f"## {label}\n\n")
        for v in group:
            if view_type == VIEW_DEPLOYMENT:
                title = v.title or v.key
                lines.append(f"### {title}\n\n")
            lines.append(f"{_diagram_embed(v)}\n\n")


def _dep_link(workspace: Workspace, name: str, element_id: str) -> str:
    """Create a markdown link for a dependency target — system or person."""
    slug = normalize_name(name)
    for p in workspace.people:
        if p.id == element_id:
            return f"[{name}](../../actors/{slug}/index.md)"
    return f"[{name}](../{slug}/index.md)"


def _append_dependencies(workspace: Workspace, ss: SoftwareSystem, lines: list[str]) -> None:
    inbound, outbound = workspace.dependencies_for_system(ss.id)
    if not inbound and not outbound:
        return

    lines.append("## Dependencies\n\n")

    lines.append("### Inbound\n\n")
    if inbound:
        lines.append("| System | Description | Technology |\n")
        lines.append("|---|---|---|\n")
        for element_id, name, desc, tech in inbound:
            link = _dep_link(workspace, name, element_id)
            lines.append(f"| {link} | {desc} | {tech} |\n")
    else:
        lines.append("No inbound dependencies.\n")
    lines.append("\n")

    lines.append("### Outbound\n\n")
    if outbound:
        lines.append("| System | Description | Technology |\n")
        lines.append("|---|---|---|\n")
        for element_id, name, desc, tech in outbound:
            link = _dep_link(workspace, name, element_id)
            lines.append(f"| {link} | {desc} | {tech} |\n")
    else:
        lines.append("No outbound dependencies.\n")
    lines.append("\n")


def _append_decisions(decisions: list[Decision], lines: list[str]) -> None:
    lines.append("## Architecture Decision Records\n\n")
    lines.append("| ID | Date | Status | Title |\n")
    lines.append("|---|---|---|---|\n")
    for d in sorted(decisions, key=lambda d: int(d.id)):
        date = d.date[:10] if d.date else ""
        lines.append(f"| {d.id} | {date} | {d.status} | {d.title} |\n")
    lines.append("\n")

    for d in sorted(decisions, key=lambda d: int(d.id)):
        lines.append(f"{_bump_headings(d.content, 2)}\n\n")


def _append_sections(sections: list[Section], lines: list[str], view_keys: set[str] | None = None) -> None:
    lines.append("## Documentation\n\n")
    for section in sorted(sections, key=lambda s: s.order):
        content = section.content
        if view_keys:
            content = _resolve_embeds(content, view_keys, "../../diagrams/")
        lines.append(f"{_bump_headings(content, 2)}\n\n")


def _bump_headings(content: str, levels: int) -> str:
    """Increase all markdown heading levels by *levels* (e.g. # → ### when levels=2), clamped to h6."""
    def _clamp(m: re.Match) -> str:
        new_level = min(len(m.group(1)) + levels, 6)
        return f"{'#' * new_level} "

    return re.sub(r"^(#{1,6})\s", _clamp, content, flags=re.MULTILINE)


def _resolve_embeds(content: str, view_keys: set[str], diagrams_prefix: str) -> str:
    """Replace ![alt](embed:ViewKey) with actual diagram image paths."""
    def _replace(m: re.Match) -> str:
        alt, key = m.group(1), m.group(2)
        if key in view_keys:
            return f"![{alt}]({diagrams_prefix}structurizr-{key}.svg)"
        return m.group(0)

    return re.sub(r"!\[([^\]]*)\]\(embed:([^)]+)\)", _replace, content)


def _rewrite_asset_paths(content: str, prefix: str) -> str:
    """Rewrite absolute image paths like (/pictures/foo.png) to relative paths."""
    return re.sub(
        r"(!\[[^\]]*\])\(/([^)]+)\)",
        lambda m: f"{m.group(1)}({prefix}{m.group(2)})",
        content,
    )


def _iter_top_level_lines(content: str):
    """Yield (line, is_nested) tuples, tracking 4+ backtick outer fences.

    Lines inside outer fences have is_nested=True and should be passed through unchanged.
    """
    outer_fence = False
    for line in content.split("\n"):
        stripped = line.strip()
        if not outer_fence and re.match(r"^`{4,}", stripped):
            outer_fence = True
            yield line, True
        elif outer_fence:
            if re.match(r"^`{4,}$", stripped):
                outer_fence = False
            yield line, True
        else:
            yield line, False


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


def _add_mermaid_view_source(content: str) -> str:
    """Append a collapsible 'View Source' admonition after each top-level ```mermaid block."""
    result: list[str] = []
    in_mermaid = False
    mermaid_lines: list[str] = []

    for line, nested in _iter_top_level_lines(content):
        if nested:
            result.append(line)
            continue

        stripped = line.strip()
        if not in_mermaid and stripped == "```mermaid":
            in_mermaid = True
            mermaid_lines = [line]
            continue
        if in_mermaid:
            mermaid_lines.append(line)
            if stripped == "```":
                result.extend(mermaid_lines)
                result.append("")
                result.append('??? info "View Source"')
                result.append("")
                result.append("    ```text")
                for ml in mermaid_lines[1:-1]:
                    result.append(f"    {ml}")
                result.append("    ```")
                in_mermaid = False
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
    title = view.title or view.key
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
