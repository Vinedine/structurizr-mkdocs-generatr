"""Generate Markdown files from a parsed Structurizr workspace."""

from __future__ import annotations

import shutil
from pathlib import Path

from .workspace import (
    Decision,
    Documentation,
    Section,
    SoftwareSystem,
    Workspace,
    View,
    normalize_name,
)


def generate_markdown(workspace: Workspace, docs_dir: Path, svg_dir: Path) -> None:
    """Generate all Markdown files for the MkDocs site."""
    docs_dir.mkdir(parents=True, exist_ok=True)

    _write_home_page(workspace, docs_dir)
    _write_workspace_decisions(workspace.documentation, docs_dir)
    _write_workspace_docs(workspace.documentation, docs_dir)
    _write_software_systems_index(workspace, docs_dir)
    _copy_diagrams(svg_dir, docs_dir)

    for ss in workspace.software_systems:
        _write_software_system_pages(workspace, ss, docs_dir)


def _write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_home_page(workspace: Workspace, docs_dir: Path) -> None:
    sections = workspace.documentation.sections
    if sections:
        first = sorted(sections, key=lambda s: s.order)[0]
        content = first.content
    else:
        content = f"# {workspace.name}\n\n{workspace.description}\n"
    _write_file(docs_dir / "index.md", content)


def _write_workspace_decisions(documentation: Documentation, docs_dir: Path) -> None:
    decisions = documentation.decisions
    if not decisions:
        return

    decisions_dir = docs_dir / "decisions"

    lines = ["# Architecture Decisions\n\n"]
    lines.append("| ID | Date | Status | Title |\n")
    lines.append("|---|---|---|---|\n")
    for d in sorted(decisions, key=lambda d: int(d.id)):
        date = d.date[:10] if d.date else ""
        lines.append(f"| {d.id} | {date} | {d.status} | [{d.title}]({d.id}.md) |\n")
    _write_file(decisions_dir / "index.md", "".join(lines))

    for d in decisions:
        _write_file(decisions_dir / f"{d.id}.md", d.content)


def _write_workspace_docs(documentation: Documentation, docs_dir: Path) -> None:
    sections = documentation.sections
    if len(sections) <= 1:
        return

    docs_sections_dir = docs_dir / "documentation"
    sorted_sections = sorted(sections, key=lambda s: s.order)

    for section in sorted_sections[1:]:
        slug = _section_slug(section)
        _write_file(docs_sections_dir / f"{slug}.md", section.content)


def _section_slug(section: Section) -> str:
    if section.title:
        return normalize_name(section.title)
    name = section.filename.rsplit(".", 1)[0]
    return normalize_name(name)


def _write_software_systems_index(workspace: Workspace, docs_dir: Path) -> None:
    lines = ["# Software Systems\n\n"]
    lines.append("| Name | Description |\n")
    lines.append("|---|---|\n")
    for ss in sorted(workspace.software_systems, key=lambda s: s.name):
        slug = normalize_name(ss.name)
        lines.append(f"| [{ss.name}]({slug}/index.md) | {ss.description} |\n")
    _write_file(docs_dir / "software-systems" / "index.md", "".join(lines))


def _write_software_system_pages(
    workspace: Workspace, ss: SoftwareSystem, docs_dir: Path
) -> None:
    slug = normalize_name(ss.name)
    ss_dir = docs_dir / "software-systems" / slug

    # System overview page
    lines = [f"# {ss.name}\n\n"]
    if ss.description:
        lines.append(f"{ss.description}\n\n")
    if ss.group:
        lines.append(f"**Group:** {ss.group}\n\n")
    if ss.url:
        lines.append(f"**URL:** [{ss.url}]({ss.url})\n\n")
    if ss.containers:
        lines.append("## Containers\n\n")
        lines.append("| Name | Technology | Description |\n")
        lines.append("|---|---|---|\n")
        for c in sorted(ss.containers, key=lambda c: c.name):
            lines.append(f"| {c.name} | {c.technology} | {c.description} |\n")
    _write_file(ss_dir / "index.md", "".join(lines))

    # Diagram pages
    system_views = workspace.views_for_system(ss.id)
    _write_diagram_pages(system_views, ss_dir)

    # System-level decisions
    if ss.documentation.decisions:
        _write_decisions(ss.documentation.decisions, ss_dir / "decisions")

    # System-level documentation sections
    if ss.documentation.sections:
        _write_sections(ss.documentation.sections, ss_dir / "docs")


def _write_diagram_pages(views: list[View], ss_dir: Path) -> None:
    view_groups: dict[str, list[View]] = {}
    for v in views:
        view_groups.setdefault(v.type, []).append(v)

    type_labels = {
        "systemContext": ("Context Views", "context.md"),
        "container": ("Container Views", "containers.md"),
        "component": ("Component Views", "components.md"),
        "dynamic": ("Dynamic Views", "dynamic.md"),
        "deployment": ("Deployment Views", "deployment.md"),
        "image": ("Image Views", "images.md"),
    }

    for view_type, (label, filename) in type_labels.items():
        group = view_groups.get(view_type, [])
        if not group:
            continue

        lines = [f"# {label}\n\n"]
        for v in group:
            title = v.title or v.key
            lines.append(f"## {title}\n\n")
            if v.description:
                lines.append(f"{v.description}\n\n")
            svg_filename = f"structurizr-{v.key}.svg"
            rel_path = f"../../diagrams/{svg_filename}"
            lines.append(f"![{title}]({rel_path})\n\n")

        _write_file(ss_dir / filename, "".join(lines))


def _write_decisions(decisions: list[Decision], decisions_dir: Path) -> None:
    lines = ["# Decisions\n\n"]
    lines.append("| ID | Date | Status | Title |\n")
    lines.append("|---|---|---|---|\n")
    for d in sorted(decisions, key=lambda d: int(d.id)):
        date = d.date[:10] if d.date else ""
        lines.append(f"| {d.id} | {date} | {d.status} | [{d.title}]({d.id}.md) |\n")
    _write_file(decisions_dir / "index.md", "".join(lines))

    for d in decisions:
        _write_file(decisions_dir / f"{d.id}.md", d.content)


def _write_sections(sections: list[Section], sections_dir: Path) -> None:
    # Index page
    lines = ["# Documentation\n\n"]
    for section in sorted(sections, key=lambda s: s.order):
        slug = _section_slug(section)
        title = _section_title(section)
        lines.append(f"- [{title}]({slug}.md)\n")
    _write_file(sections_dir / "index.md", "".join(lines))

    # Individual pages
    for section in sorted(sections, key=lambda s: s.order):
        slug = _section_slug(section)
        _write_file(sections_dir / f"{slug}.md", section.content)


def _section_title(section: Section) -> str:
    if section.title:
        return section.title
    name = section.filename.rsplit(".", 1)[0]
    parts = name.split("-", 1)
    if len(parts) > 1 and parts[0].isdigit():
        name = parts[1]
    return name.replace("-", " ").capitalize()


def _copy_diagrams(svg_dir: Path, docs_dir: Path) -> None:
    diagrams_dir = docs_dir / "diagrams"
    diagrams_dir.mkdir(parents=True, exist_ok=True)

    if not svg_dir.exists():
        return

    for svg_file in svg_dir.glob("*.svg"):
        shutil.copy2(svg_file, diagrams_dir / svg_file.name)
