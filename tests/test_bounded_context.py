"""Tests for bounded context parsing, analysis, and markdown generation."""

from __future__ import annotations

from pathlib import Path

import pytest

from structurizr_mkdocs_generatr.bounded_context import (
    BoundedContextModel,
    map_contexts,
    parse_bounded_contexts,
    write_bounded_context_index,
    write_bounded_context_pages,
)
from structurizr_mkdocs_generatr.workspace import (
    Documentation,
    Section,
    SoftwareSystem,
    Workspace,
)


MINIMAL_MMD = """\
flowchart TB

    %% [START.CONTEXT] [Alpha]

    subgraph Alpha
        A1[Entity One]
        A2[Entity Two]
    end

    A1 --> |uses| A2

    click A1 'A1'
    click A2 'A2'

    %% [END.CONTEXT] [Alpha]

    %% [START.CONTEXT] [Beta]

    subgraph Beta
        B1[Beta One]
        B2[Beta Two]
    end

    B1 --> |feeds| B2

    click B1 'B1'
    click B2 'B2'

    %% [END.CONTEXT] [Beta]

    %% [START.LINK]

    A1 --> |connects| B1
    B2 --> |returns| A2

    %% [END.LINK]
"""


@pytest.fixture
def mmd_file(tmp_path: Path) -> Path:
    p = tmp_path / "boundedContext.mmd"
    p.write_text(MINIMAL_MMD, encoding="utf-8")
    return p


@pytest.fixture
def model(mmd_file: Path) -> BoundedContextModel:
    m = parse_bounded_contexts(mmd_file)
    assert m is not None
    return m


class TestParsing:
    def test_returns_none_for_missing_file(self, tmp_path: Path) -> None:
        assert parse_bounded_contexts(tmp_path / "nope.mmd") is None

    def test_returns_none_for_empty_file(self, tmp_path: Path) -> None:
        p = tmp_path / "empty.mmd"
        p.write_text("flowchart TB\n", encoding="utf-8")
        assert parse_bounded_contexts(p) is None

    def test_extracts_contexts(self, model: BoundedContextModel) -> None:
        names = [c.name for c in model.contexts]
        assert names == ["Alpha", "Beta"]

    def test_extracts_entities(self, model: BoundedContextModel) -> None:
        alpha = model.contexts[0]
        assert alpha.entities == ["A1", "A2"]

    def test_extracts_entity_labels(self, model: BoundedContextModel) -> None:
        alpha = model.contexts[0]
        assert alpha.entity_labels == {"A1": "Entity One", "A2": "Entity Two"}

    def test_extracts_cross_links(self, model: BoundedContextModel) -> None:
        assert len(model.cross_links) == 2
        assert "A1 --> |connects| B1" in model.cross_links

    def test_entity_to_context_mapping(self, model: BoundedContextModel) -> None:
        assert model.entity_to_context["A1"] == "Alpha"
        assert model.entity_to_context["B1"] == "Beta"

    def test_mermaid_section_excludes_comments(self, model: BoundedContextModel) -> None:
        for ctx in model.contexts:
            assert "%%" not in ctx.mermaid_section


class TestAnalysis:
    def test_related_contexts(self, model: BoundedContextModel) -> None:
        related = model.related_contexts("Alpha")
        assert "Beta" in related
        assert "B1" in related["Beta"]

    def test_related_contexts_bidirectional(self, model: BoundedContextModel) -> None:
        related_alpha = model.related_contexts("Alpha")
        related_beta = model.related_contexts("Beta")
        assert "Beta" in related_alpha
        assert "Alpha" in related_beta

    def test_context_relations(self, model: BoundedContextModel) -> None:
        relations = model.context_relations()
        assert len(relations) == 1
        src, tgt, bidi = relations[0]
        assert {src, tgt} == {"Alpha", "Beta"}
        assert bidi is True

    def test_context_relations_unidirectional(self, tmp_path: Path) -> None:
        mmd = """\
flowchart TB
    %% [START.CONTEXT] [X]
    subgraph X
        X1[X One]
    end
    click X1 'X1'
    %% [END.CONTEXT] [X]

    %% [START.CONTEXT] [Y]
    subgraph Y
        Y1[Y One]
    end
    click Y1 'Y1'
    %% [END.CONTEXT] [Y]

    %% [START.LINK]
    X1 --> |to| Y1
    %% [END.LINK]
"""
        p = tmp_path / "bc.mmd"
        p.write_text(mmd, encoding="utf-8")
        m = parse_bounded_contexts(p)
        assert m is not None
        relations = m.context_relations()
        assert len(relations) == 1
        assert relations[0][2] is False


class TestSystemMapping:
    def _make_system(self, name: str, intro_content: str) -> SoftwareSystem:
        return SoftwareSystem(
            id="1", name=name, description="", group="",
            tags=[], url="",
            containers=[], relationships=[],
            documentation=Documentation(
                sections=[Section(content=intro_content, filename="0000-introduction.md", format="Markdown", order=0, title="")],
                decisions=[],
            ),
            properties={},
        )

    def test_maps_contexts_to_systems(self, model: BoundedContextModel) -> None:
        intro_content = "# Description\nSome system\n\n# Business Data\n\n# Bounded Context\n- [Alpha](/bounded-contexts/)\n\n# Data Landscape\n\n| Entity | Role |\n|--------|------|\n| stuff | Owns |\n"
        ss = self._make_system("Test System", intro_content)
        ws = Workspace(
            name="Test", description="", software_systems=[ss],
            people=[], documentation=Documentation(), views=[], properties={},
        )
        system_map, _ = map_contexts(model, ws)
        assert len(system_map["Alpha"]) == 1
        assert system_map["Alpha"][0].name == "Test System"
        assert system_map["Beta"] == []

    def test_maps_capabilities(self, model: BoundedContextModel) -> None:
        intro_content = "# Description\nTest\n\n# Capabilities\n\n- Cap one\n- Cap two\n\n# Business Data\n\n# Bounded Context\n- [Alpha](/bounded-contexts/)\n"
        ss = self._make_system("Test System", intro_content)
        ws = Workspace(
            name="Test", description="", software_systems=[ss],
            people=[], documentation=Documentation(), views=[], properties={},
        )
        _, cap_map = map_contexts(model, ws)
        assert "Test System" in cap_map["Alpha"]
        assert cap_map["Alpha"]["Test System"] == ["Cap one", "Cap two"]
        assert cap_map["Beta"] == {}


class TestMarkdownGeneration:
    def test_writes_index(self, model: BoundedContextModel, tmp_path: Path) -> None:
        docs_dir = tmp_path / "docs"
        cap_map: dict[str, dict[str, list[str]]] = {"Alpha": {}, "Beta": {}}
        write_bounded_context_index(model, {"Alpha": [], "Beta": []}, cap_map, docs_dir)
        index = docs_dir / "capability-map" / "index.md"
        assert index.exists()
        content = index.read_text(encoding="utf-8")
        assert "# Capability Map" in content
        assert "capability map" in content
        assert '!!! question "What questions does this answer?"' in content
        assert "| Bounded Context | Description | Software Systems | Capabilities |" in content
        assert "[Alpha](alpha.md)" in content
        assert "[Beta](beta.md)" in content
        assert "| 0 |" in content
        assert "```mermaid" in content

    def test_writes_context_pages(self, model: BoundedContextModel, tmp_path: Path) -> None:
        docs_dir = tmp_path / "docs"
        ws = Workspace(
            name="Test", description="", software_systems=[],
            people=[], documentation=Documentation(), views=[], properties={},
        )
        cap_map: dict[str, dict[str, list[str]]] = {"Alpha": {}, "Beta": {}}
        write_bounded_context_pages(model, {"Alpha": [], "Beta": []}, cap_map, ws, docs_dir)
        alpha_page = docs_dir / "capability-map" / "alpha.md"
        beta_page = docs_dir / "capability-map" / "beta.md"
        assert alpha_page.exists()
        assert beta_page.exists()

        content = alpha_page.read_text(encoding="utf-8")
        assert "# Alpha" in content
        assert "```mermaid" in content
        assert 'subgraph "Beta"' in content

    def test_context_page_includes_capabilities(self, model: BoundedContextModel, tmp_path: Path) -> None:
        docs_dir = tmp_path / "docs"
        intro_content = "# Description\nTest\n\n# Capabilities\n\n- Do thing one\n- Do thing two\n\n# Business Data\n\n# Bounded Context\n- [Alpha](/bounded-contexts/)\n"
        ss = SoftwareSystem(
            id="1", name="My System", description="", group="",
            tags=[], url="", containers=[], relationships=[],
            documentation=Documentation(
                sections=[Section(content=intro_content, filename="0000-introduction.md", format="Markdown", order=0, title="")],
                decisions=[],
            ),
            properties={},
        )
        ws = Workspace(
            name="Test", description="", software_systems=[ss],
            people=[], documentation=Documentation(), views=[], properties={},
        )
        system_map = {"Alpha": [ss], "Beta": []}
        cap_map = {"Alpha": {"My System": ["Do thing one", "Do thing two"]}, "Beta": {}}
        write_bounded_context_pages(model, system_map, cap_map, ws, docs_dir)
        content = (docs_dir / "capability-map" / "alpha.md").read_text(encoding="utf-8")
        assert "## Capabilities" in content
        assert "### [My System](../software-systems/my-system/index.md)" in content
        assert "- Do thing one" in content
        assert "- Do thing two" in content


class TestExampleFile:
    """Test with the actual example boundedContext.mmd file."""

    @pytest.fixture
    def example_model(self) -> BoundedContextModel | None:
        example_path = Path(__file__).parent.parent / "example" / "boundedContext.mmd"
        if not example_path.exists():
            pytest.skip("Example file not found")
        return parse_bounded_contexts(example_path)

    def test_parses_all_contexts(self, example_model: BoundedContextModel) -> None:
        assert example_model is not None
        assert len(example_model.contexts) == 13

    def test_has_cross_links(self, example_model: BoundedContextModel) -> None:
        assert example_model is not None
        assert len(example_model.cross_links) > 10

    def test_context_names(self, example_model: BoundedContextModel) -> None:
        assert example_model is not None
        names = [c.name for c in example_model.contexts]
        assert "Club Strategy Management" in names
        assert "Fan Engagement & Communications" in names
        assert "Gameday Match/Event Delivery" in names

    def test_relations_exist(self, example_model: BoundedContextModel) -> None:
        assert example_model is not None
        relations = example_model.context_relations()
        assert len(relations) > 5
