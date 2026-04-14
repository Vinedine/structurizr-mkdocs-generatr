"""Export Structurizr workspace via Docker (vNext CLI + PlantUML)."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

from .workspace import Workspace, normalize_name


def _run(args: list[str], label: str) -> None:
    print(f"  {label}...")
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: {label} failed", file=sys.stderr)
        print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"{label} failed with exit code {result.returncode}")


def export_workspace(workspace_dir: Path, output_dir: Path) -> tuple[Path, Path]:
    """Run Structurizr vNext export to produce workspace.json and PlantUML files.

    Args:
        workspace_dir: Directory containing the workspace.dsl file.
        output_dir: Build output directory.

    Returns:
        Tuple of (json_dir, puml_dir) paths.
    """
    json_dir = output_dir / "json"
    puml_dir = output_dir / "puml"
    json_dir.mkdir(parents=True, exist_ok=True)
    puml_dir.mkdir(parents=True, exist_ok=True)

    workspace_dir_str = str(workspace_dir.resolve()).replace("\\", "/")

    # Export JSON
    _run([
        "docker", "run", "--rm",
        "-v", f"{workspace_dir_str}:/usr/local/structurizr",
        "structurizr/structurizr",
        "export", "-w", "workspace.dsl", "-f", "json", "-o", "output-json",
    ], "Exporting workspace JSON")

    # Move JSON output to our build dir
    src_json = workspace_dir / "output-json" / "workspace.json"
    dst_json = json_dir / "workspace.json"
    shutil.move(str(src_json), str(dst_json))
    (workspace_dir / "output-json").rmdir()

    # Export PlantUML
    _run([
        "docker", "run", "--rm",
        "-v", f"{workspace_dir_str}:/usr/local/structurizr",
        "structurizr/structurizr",
        "export", "-w", "workspace.dsl", "-f", "plantuml/c4plantuml", "-o", "output-puml",
    ], "Exporting C4 PlantUML")

    # Move PUML files to our build dir
    puml_src_dir = workspace_dir / "output-puml"
    for puml_file in puml_src_dir.glob("*.puml"):
        shutil.move(str(puml_file), str(puml_dir / puml_file.name))
    puml_src_dir.rmdir()

    return json_dir, puml_dir


def render_diagrams(puml_dir: Path, svg_dir: Path) -> None:
    """Render PlantUML files to SVG using the PlantUML Docker image.

    Args:
        puml_dir: Directory containing .puml files.
        svg_dir: Output directory for .svg files.
    """
    svg_dir.mkdir(parents=True, exist_ok=True)

    puml_files = list(puml_dir.glob("*.puml"))
    if not puml_files:
        print("  No PlantUML files to render.")
        return

    puml_dir_str = str(puml_dir.resolve()).replace("\\", "/")
    svg_dir_str = str(svg_dir.resolve()).replace("\\", "/")

    _run([
        "docker", "run", "--rm",
        "-v", f"{puml_dir_str}:/data",
        "-v", f"{svg_dir_str}:/output",
        "plantuml/plantuml",
        "-tsvg", "-o", "/output", "/data/*.puml",
    ], f"Rendering {len(puml_files)} diagrams to SVG")


def _build_element_url_map(workspace: Workspace) -> dict[str, str]:
    """Build a mapping from element name to relative URL path (from diagrams/)."""
    urls: dict[str, str] = {}
    for person in workspace.people:
        slug = normalize_name(person.name)
        urls[person.name] = f"../users/{slug}/"
    for ss in workspace.software_systems:
        ss_slug = normalize_name(ss.name)
        urls[ss.name] = f"../software-systems/{ss_slug}/"
        for c in ss.containers:
            urls[c.name] = f"../software-systems/{ss_slug}/"
            for comp in c.components:
                urls[comp.name] = f"../software-systems/{ss_slug}/"
    return urls


_ELEMENT_NAME_RE = re.compile(r'\(\w+,\s*"([^"]+)"')


def process_puml_files(puml_dir: Path, workspace: Workspace, *, hide_legend: bool = False) -> None:
    """Single-pass post-processing of .puml files: inject links, strip titles/legends."""
    url_map = _build_element_url_map(workspace)

    for puml_file in puml_dir.glob("*.puml"):
        content = puml_file.read_text(encoding="utf-8")
        original = content

        # Inject links
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if '$link=""' not in line:
                continue
            match = _ELEMENT_NAME_RE.search(line)
            if not match:
                continue
            name = match.group(1)
            url = url_map.get(name)
            if url:
                lines[i] = line.replace('$link=""', f'$link="{url}"')
        content = "\n".join(lines)

        # Strip titles
        content = re.sub(r"^title .*\n?", "", content, flags=re.MULTILINE)

        # Strip legends
        if hide_legend:
            content = re.sub(r"^SHOW_LEGEND\(.*\)\s*\n?", "", content, flags=re.MULTILINE)

        if content != original:
            puml_file.write_text(content, encoding="utf-8")


