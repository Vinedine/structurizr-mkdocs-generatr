"""CLI entry point for structurizr-mkdocs-generatr."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import click

from .bounded_context import parse_bounded_contexts
from .exporter import export_workspace, process_puml_files, render_diagrams
from .markdown_writer import GenerateOptions, generate_markdown
from .mkdocs_config import generate_mkdocs_config
from .properties import resolve_properties
from .view_generator import OUTPUT_FILENAME, generate_views
from .workspace import parse_workspace


@click.command()
@click.argument("workspace_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option(
    "--workspace-file", "-w",
    default="workspace.dsl",
    help="Name of the DSL file inside the workspace directory.",
)
@click.option(
    "--output", "-o",
    default="build",
    type=click.Path(path_type=Path),
    help="Build output directory.",
)
@click.option("--serve", is_flag=True, help="Run mkdocs serve after generation.")
@click.option("--skip-export", is_flag=True, help="Skip Docker export (reuse existing build artifacts).")
@click.option("--skip-views-gen", is_flag=True, help="Skip auto-generation of DSL views.")
def main(
    workspace_dir: Path,
    workspace_file: str,
    output: Path,
    serve: bool,
    skip_export: bool,
    skip_views_gen: bool,
) -> None:
    """Generate an MkDocs site from a Structurizr workspace directory."""
    output = output.resolve()
    workspace_dir = workspace_dir.resolve()

    json_dir = output / "json"
    puml_dir = output / "puml"
    svg_dir = output / "svg"
    inline_puml_dir = output / "inline-puml"
    site_src = output / "site-src"

    # Step 0: Auto-generate DSL views
    if not skip_views_gen:
        click.echo("Auto-generating DSL views...")
        generated = generate_views(workspace_dir, workspace_file)
        if generated:
            click.echo(f"  Generated: {generated.name}")
            # Check if the include line is present in the DSL
            dsl_path = workspace_dir / workspace_file
            if dsl_path.exists():
                dsl_text = dsl_path.read_text(encoding="utf-8")
                if OUTPUT_FILENAME not in dsl_text:
                    click.echo(
                        f"  Note: Add '!include {OUTPUT_FILENAME}' inside your views {{ }} block in {workspace_file}"
                    )
    else:
        click.echo("Skipping view auto-generation (--skip-views-gen)")

    # Step 1: Export via Docker
    if not skip_export:
        click.echo("Step 1/4: Exporting workspace via Structurizr vNext...")
        export_workspace(workspace_dir, output)
    else:
        click.echo("Steps 1-2: Skipping export (--skip-export)")

    # Parse workspace JSON (needed before rendering to inject diagram links)
    workspace_json = json_dir / "workspace.json"
    if not workspace_json.exists():
        click.echo(f"Error: {workspace_json} not found. Run without --skip-export first.", err=True)
        sys.exit(1)

    workspace = parse_workspace(workspace_json)
    props = resolve_properties(workspace.view_properties)

    # Parse bounded context model if .mmd file exists
    bc_model = parse_bounded_contexts(workspace_dir / "boundedContext.mmd")

    # Step 2: Post-process PlantUML and render to SVG
    if not skip_export:
        click.echo("  Post-processing PlantUML diagrams...")
        process_puml_files(puml_dir, workspace, hide_legend=props.hide_legend)

        click.echo("Step 2/4: Rendering PlantUML diagrams to SVG...")
        render_diagrams(puml_dir, svg_dir)

    click.echo("Step 3/4: Generating MkDocs site source...")

    # Clean previous site source to avoid stale files
    docs_out = site_src / "docs"
    if docs_out.exists():
        shutil.rmtree(docs_out)

    # Step 3: Generate Markdown + mkdocs.yml
    opts = GenerateOptions(
        assets_dir=workspace_dir / "assets",
        inline_puml_dir=inline_puml_dir,
        puml_dir=puml_dir,
        props=props,
        bc_model=bc_model,
    )
    generate_markdown(workspace, docs_out, svg_dir, opts)
    generate_mkdocs_config(workspace, site_src, props, bc_model=bc_model)

    # Render inline PlantUML blocks if any were extracted
    inline_puml_files = list(inline_puml_dir.glob("*.puml")) if inline_puml_dir.exists() else []
    if inline_puml_files:
        diagrams_dir = site_src / "docs" / "diagrams"
        click.echo(f"  Rendering {len(inline_puml_files)} inline PlantUML diagrams...")
        render_diagrams(inline_puml_dir, diagrams_dir)

    click.echo("Step 4/4: Building MkDocs site...")
    mkdocs = [sys.executable, "-m", "mkdocs"]
    if serve:
        click.echo("Serving site at http://localhost:8000")
        subprocess.run(
            [*mkdocs, "serve", "-f", str(site_src / "mkdocs.yml")],
            check=True,
        )
    else:
        subprocess.run(
            [*mkdocs, "build", "-f", str(site_src / "mkdocs.yml"), "-d", str(output / "site")],
            check=True,
        )
        click.echo(f"Site generated at {output / 'site'}")
