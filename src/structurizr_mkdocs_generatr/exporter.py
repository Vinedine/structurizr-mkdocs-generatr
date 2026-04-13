"""Export Structurizr workspace via Docker (vNext CLI + PlantUML)."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


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
    src_json.rename(dst_json)
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
        puml_file.rename(puml_dir / puml_file.name)
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
