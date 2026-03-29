"""Integration tests using the BelFoot FC example workspace."""

from pathlib import Path

import pytest

from structurizr_mkdocs_generatr.bounded_context import parse_bounded_contexts
from structurizr_mkdocs_generatr.properties import resolve_properties
from structurizr_mkdocs_generatr.view_generator import (
    _find_includes_dir,
    _parse_deployments,
    _parse_groups,
    _parse_users,
    generate_views,
)

EXAMPLE_DIR = Path(__file__).resolve().parent.parent / "example"


@pytest.fixture
def example_dir() -> Path:
    if not (EXAMPLE_DIR / "workspace.dsl").exists():
        pytest.skip("Example workspace not available")
    return EXAMPLE_DIR


# ---------------------------------------------------------------------------
# Bounded contexts
# ---------------------------------------------------------------------------


class TestBoundedContexts:
    def test_parses_13_contexts(self, example_dir: Path) -> None:
        model = parse_bounded_contexts(example_dir / "boundedContext.mmd")
        assert model is not None
        assert len(model.contexts) == 13

    def test_expected_context_names(self, example_dir: Path) -> None:
        model = parse_bounded_contexts(example_dir / "boundedContext.mmd")
        assert model is not None
        names = {c.name for c in model.contexts}
        expected = {
            "Asset/Infrastructure Management",
            "Club Strategy Management",
            "Customer/Fan Services & Relationship",
            "Enterprise Risk, Compliance & Resiliency",
            "External Relationships Management",
            "Fan Engagement & Communications",
            "Financial Resources Management",
            "Gameday Match/Event Delivery",
            "IT Management",
            "Marketing & Sales",
            "Product Delivery & Material Management",
            "Products & Services Development",
            "Staff, Player & Team Development",
        }
        assert names == expected

    def test_cross_links_exist(self, example_dir: Path) -> None:
        model = parse_bounded_contexts(example_dir / "boundedContext.mmd")
        assert model is not None
        assert len(model.cross_links) > 5

    def test_context_relations(self, example_dir: Path) -> None:
        model = parse_bounded_contexts(example_dir / "boundedContext.mmd")
        assert model is not None
        relations = model.context_relations()
        assert len(relations) > 3


# ---------------------------------------------------------------------------
# View generator — modular DSL parsing
# ---------------------------------------------------------------------------


class TestModularDslParsing:
    def test_parses_users(self, example_dir: Path) -> None:
        includes_dir = _find_includes_dir(example_dir)
        users = _parse_users(example_dir, includes_dir)
        assert len(users) == 20

    def test_parses_5_groups(self, example_dir: Path) -> None:
        includes_dir = _find_includes_dir(example_dir)
        groups = _parse_groups(example_dir, includes_dir)
        assert len(groups) == 5
        names = {g.display_name for g in groups}
        assert names == {"Commercial", "Corporate", "IT", "Operations", "Sporting"}

    def test_parses_26_systems(self, example_dir: Path) -> None:
        includes_dir = _find_includes_dir(example_dir)
        groups = _parse_groups(example_dir, includes_dir)
        total_systems = sum(len(g.systems) for g in groups)
        assert total_systems == 26

    def test_parses_deployment_environments(self, example_dir: Path) -> None:
        includes_dir = _find_includes_dir(example_dir)
        envs = _parse_deployments(example_dir, includes_dir)
        env_names = {e.display_name for e in envs}
        assert "Production" in env_names
        assert len(envs) >= 4

    def test_generate_views_skips_existing(self, example_dir: Path) -> None:
        """View generator should produce a file but most views should be skipped."""
        result = generate_views(example_dir)
        assert result is not None
        content = result.read_text(encoding="utf-8")
        assert "AUTO-GENERATED VIEWS" in content
        result.unlink()


# ---------------------------------------------------------------------------
# Properties — BelFoot workspace properties
# ---------------------------------------------------------------------------


class TestBelfootProperties:
    def test_resolves_mkdocs_properties(self) -> None:
        props = {
            "mkdocs.color.primary": "#2c4390",
            "mkdocs.color.headerText": "#ffffff",
            "mkdocs.favicon": "site/favicon.ico",
        }
        site = resolve_properties(props)
        assert site.primary_color == "#2c4390"
        assert site.header_text_color == "#ffffff"
        assert site.favicon == "site/favicon.ico"
