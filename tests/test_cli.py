import json
import subprocess
from importlib.metadata import version

import click
import pytest
from click.testing import CliRunner

from structurizr_mkdocs_generatr import cli
from structurizr_mkdocs_generatr.cli import main


def test_version_option():
    result = CliRunner().invoke(main, ["--version"])
    assert result.exit_code == 0
    assert version("structurizr-mkdocs-generatr") in result.output


def test_missing_workspace_file_is_reported(tmp_path):
    result = CliRunner().invoke(main, [str(tmp_path), "-o", str(tmp_path / "build")])
    assert result.exit_code != 0
    assert "workspace.dsl" in result.output
    assert isinstance(result.exception, SystemExit)


def test_page_collisions_stop_the_build(tmp_path):
    json_dir = tmp_path / "build" / "json"
    json_dir.mkdir(parents=True)
    model = {"softwareSystems": [{"id": "1", "name": "Payments", "group": "Payments"}]}
    (json_dir / "workspace.json").write_text(json.dumps({"name": "T", "model": model, "views": {}}), encoding="utf-8")
    result = CliRunner().invoke(
        main, [str(tmp_path), "-o", str(tmp_path / "build"), "--skip-export", "--skip-views-gen"],
    )
    assert result.exit_code == 1
    assert "software-systems/payments/" in result.output
    assert not (tmp_path / "build" / "site-src").exists()


def test_failed_mkdocs_build_is_reported(tmp_path, monkeypatch):
    monkeypatch.setattr(cli.subprocess, "run", lambda args, **kwargs: subprocess.CompletedProcess(args, 1))
    with pytest.raises(click.ClickException, match="mkdocs build failed"):
        cli._step_build_site(tmp_path, tmp_path, tmp_path, in_docker=False, serve=False)
