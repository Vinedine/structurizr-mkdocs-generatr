from importlib.metadata import version

from click.testing import CliRunner

from structurizr_mkdocs_generatr.cli import main


def test_version_option():
    result = CliRunner().invoke(main, ["--version"])
    assert result.exit_code == 0
    assert version("structurizr-mkdocs-generatr") in result.output
