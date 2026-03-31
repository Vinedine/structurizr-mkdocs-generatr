"""Export Structurizr workspace via Docker or local CLI (vNext + PlantUML)."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

from .workspace import (
    VIEW_COMPONENT,
    VIEW_CONTAINER,
    VIEW_DYNAMIC,
    VIEW_SYSTEM_CONTEXT,
    VIEW_SYSTEM_LANDSCAPE,
    Workspace,
    normalize_name,
)

# Paths to local tools installed in the Docker image
_LOCAL_STRUCTURIZR_CLI = Path("/opt/structurizr-cli/structurizr.sh")
_LOCAL_PLANTUML_JAR = Path("/opt/plantuml.jar")


def has_local_tools() -> bool:
    """Check if Structurizr CLI and PlantUML are installed locally (i.e. inside Docker)."""
    return _LOCAL_STRUCTURIZR_CLI.exists() and _LOCAL_PLANTUML_JAR.exists()


def _run(args: list[str], label: str) -> None:
    print(f"  {label}...")
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: {label} failed", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"{label} failed with exit code {result.returncode}")


def export_workspace(
    workspace_dir: Path, output_dir: Path, workspace_file: str = "workspace.dsl",
) -> tuple[Path, Path]:
    """Validate and export a Structurizr workspace.

    Runs validation first, then exports workspace.json and PlantUML files.

    Args:
        workspace_dir: Directory containing the DSL file.
        output_dir: Build output directory.
        workspace_file: Name of the DSL file inside workspace_dir.

    Returns:
        Tuple of (json_dir, puml_dir) paths.
    """
    json_dir = output_dir / "json"
    puml_dir = output_dir / "puml"
    json_dir.mkdir(parents=True, exist_ok=True)
    puml_dir.mkdir(parents=True, exist_ok=True)

    if has_local_tools():
        _export_local(workspace_dir, json_dir, puml_dir, workspace_file)
    else:
        _export_docker(workspace_dir, json_dir, puml_dir, workspace_file)

    return json_dir, puml_dir


def _export_local(
    workspace_dir: Path, json_dir: Path, puml_dir: Path, workspace_file: str,
) -> None:
    """Export using locally installed Structurizr CLI (inside Docker container)."""
    dsl = str(workspace_dir / workspace_file)

    _run([
        str(_LOCAL_STRUCTURIZR_CLI),
        "validate", "-w", dsl,
    ], "Validating workspace")

    _run([
        str(_LOCAL_STRUCTURIZR_CLI),
        "export", "-w", dsl, "-f", "json", "-o", str(json_dir),
    ], "Exporting workspace JSON")

    _run([
        str(_LOCAL_STRUCTURIZR_CLI),
        "export", "-w", dsl, "-f", "plantuml/c4plantuml", "-o", str(puml_dir),
    ], "Exporting C4 PlantUML")


def _export_docker(
    workspace_dir: Path, json_dir: Path, puml_dir: Path, workspace_file: str,
) -> None:
    """Export using Docker containers (host execution)."""
    workspace_dir_str = str(workspace_dir.resolve()).replace("\\", "/")

    # Validate workspace
    _run([
        "docker", "run", "--rm",
        "-v", f"{workspace_dir_str}:/usr/local/structurizr",
        "structurizr/structurizr",
        "validate", "-w", workspace_file,
    ], "Validating workspace")

    # Export JSON
    _run([
        "docker", "run", "--rm",
        "-v", f"{workspace_dir_str}:/usr/local/structurizr",
        "structurizr/structurizr",
        "export", "-w", workspace_file, "-f", "json", "-o", "output-json",
    ], "Exporting workspace JSON")

    # Copy JSON output to our build dir (copy, not move — Docker creates
    # root-owned files that cannot be unlinked by the runner user in CI)
    src_json_dir = workspace_dir / "output-json"
    shutil.copy2(src_json_dir / "workspace.json", json_dir / "workspace.json")
    shutil.rmtree(src_json_dir, ignore_errors=True)

    # Export PlantUML
    _run([
        "docker", "run", "--rm",
        "-v", f"{workspace_dir_str}:/usr/local/structurizr",
        "structurizr/structurizr",
        "export", "-w", workspace_file, "-f", "plantuml/c4plantuml", "-o", "output-puml",
    ], "Exporting C4 PlantUML")

    # Copy PUML files to our build dir (same root-ownership issue as JSON)
    puml_src_dir = workspace_dir / "output-puml"
    for puml_file in puml_src_dir.glob("*.puml"):
        shutil.copy2(str(puml_file), str(puml_dir / puml_file.name))
    shutil.rmtree(puml_src_dir, ignore_errors=True)


def render_diagrams(puml_dir: Path, svg_dir: Path) -> None:
    """Render PlantUML files to SVG using local JAR or Docker.

    Args:
        puml_dir: Directory containing .puml files.
        svg_dir: Output directory for .svg files.
    """
    svg_dir.mkdir(parents=True, exist_ok=True)

    puml_files = list(puml_dir.glob("*.puml"))
    if not puml_files:
        print("  No PlantUML files to render.")
        return

    label = f"Rendering {len(puml_files)} diagrams to SVG"

    if has_local_tools():
        _run([
            "java", "-jar", str(_LOCAL_PLANTUML_JAR),
            "-tsvg", "-o", str(svg_dir.resolve()),
            *[str(f) for f in puml_files],
        ], label)
    else:
        puml_dir_str = str(puml_dir.resolve()).replace("\\", "/")
        svg_dir_str = str(svg_dir.resolve()).replace("\\", "/")

        _run([
            "docker", "run", "--rm",
            "-v", f"{puml_dir_str}:/data",
            "-v", f"{svg_dir_str}:/output",
            "plantuml/plantuml",
            "-tsvg", "-o", "/output", "/data/*.puml",
        ], label)


def _system_view_types(workspace: Workspace) -> dict[str, set[str]]:
    """Map each software system ID to the set of view types defined for it."""
    result: dict[str, set[str]] = {}
    for v in workspace.views:
        sid = v.software_system_id or v.element_id
        if sid:
            result.setdefault(sid, set()).add(v.type)
    return result


# Anchors matching the tab slug IDs generated by pymdownx.tabbed in
# _write_software_system_pages() of markdown_writer.py.
ANCHOR_CONTEXT_VIEW = "#context-views"
ANCHOR_CONTAINER_VIEW = "#container-views"
ANCHOR_COMPONENT_VIEWS = "#component-views"


def _drill_down_anchor(
    system_id: str,
    view_type: str | None,
    subject_system_id: str | None,
    available_views: dict[str, set[str]],
) -> str:
    """Determine the drill-down anchor for a system link based on diagram context."""
    avail = available_views.get(system_id, set())

    # Subject system in a context view → drill to container view
    if (view_type == VIEW_SYSTEM_CONTEXT
            and system_id == subject_system_id
            and VIEW_CONTAINER in avail):
        return ANCHOR_CONTAINER_VIEW

    # Subject system in a container/component view → already expanded, no anchor
    if (view_type in (VIEW_CONTAINER, VIEW_COMPONENT)
            and system_id == subject_system_id):
        return ""

    # Any other system link → drill to its context view
    if view_type in (VIEW_SYSTEM_LANDSCAPE, VIEW_SYSTEM_CONTEXT,
                     VIEW_CONTAINER, VIEW_COMPONENT, VIEW_DYNAMIC):
        if VIEW_SYSTEM_CONTEXT in avail:
            return ANCHOR_CONTEXT_VIEW

    return ""


def _build_element_url_map(
    workspace: Workspace,
    view_type: str | None = None,
    subject_system_id: str | None = None,
    available_views: dict[str, set[str]] | None = None,
) -> dict[str, str]:
    """Build a mapping from element name to relative URL path (from diagrams/).

    When *view_type* is provided, links include drill-down anchors so that
    clicking an element navigates to the next level of detail (e.g. from a
    landscape diagram straight to a system's context-view section).
    """
    available = available_views if available_views is not None else _system_view_types(workspace)

    urls: dict[str, str] = {}
    for person in workspace.people:
        slug = normalize_name(person.name)
        urls[person.name] = f"../persons/{slug}/"
    for ss in workspace.software_systems:
        ss_slug = normalize_name(ss.name)
        base = f"../software-systems/{ss_slug}/"
        anchor = _drill_down_anchor(ss.id, view_type, subject_system_id, available)
        urls[ss.name] = f"{base}{anchor}"
        for c in ss.containers:
            if c.name in urls:
                continue
            container_anchor = ""
            if (view_type == VIEW_CONTAINER
                    and VIEW_COMPONENT in available.get(ss.id, set())):
                container_anchor = ANCHOR_COMPONENT_VIEWS
            urls[c.name] = f"{base}{container_anchor}"
            for comp in c.components:
                if comp.name not in urls:
                    urls[comp.name] = base
    return urls


_ELEMENT_NAME_RE = re.compile(r'\(\w+,\s*"([^"]+)"')
_LINK_RE = re.compile(r'\$link="[^"]*"')


def process_puml_files(puml_dir: Path, workspace: Workspace, *, show_legend: bool = False) -> None:
    """Single-pass post-processing of .puml files: inject links, strip titles/legends."""
    view_by_key = {v.key: v for v in workspace.views}
    available_views = _system_view_types(workspace)

    for puml_file in puml_dir.glob("*.puml"):
        content = puml_file.read_text(encoding="utf-8")
        original = content

        key = puml_file.stem.removeprefix("structurizr-")
        view = view_by_key.get(key)
        view_type = view.type if view else None
        subject_id = (view.software_system_id or view.element_id) if view else None
        url_map = _build_element_url_map(workspace, view_type, subject_id, available_views)

        lines = content.split("\n")
        for i, line in enumerate(lines):
            if "$link=" not in line:
                continue
            match = _ELEMENT_NAME_RE.search(line)
            if not match:
                continue
            name = match.group(1)
            url = url_map.get(name)
            if url:
                lines[i] = _LINK_RE.sub(f'$link="{url}"', line)
        content = "\n".join(lines)

        # Strip titles
        content = re.sub(r"^title .*\n?", "", content, flags=re.MULTILINE)

        # Strip legends
        if not show_legend:
            content = re.sub(r"^SHOW_LEGEND\(.*\)\s*\n?", "", content, flags=re.MULTILINE)

        if content != original:
            puml_file.write_text(content, encoding="utf-8")
