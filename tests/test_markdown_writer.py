"""Tests for markdown_writer pure functions."""

from __future__ import annotations



from structurizr_mkdocs_generatr.markdown_writer import (
    _abs_link_targets,
    _bump_headings,
    _element_tag_badges,
    _extract_description_paragraph,
    _extract_puml_blocks,
    _promote_headings,
    _resolve_embeds,
    _rewrite_absolute_links,
    _rewrite_asset_paths,
    _rewrite_decision_links,
    _strip_description_section,
)
from structurizr_mkdocs_generatr.mermaid_utils import add_mermaid_view_source as _add_mermaid_view_source
from structurizr_mkdocs_generatr.workspace import (
    Documentation,
    Section,
    SoftwareSystem,
    Workspace,
)


def _make_system(id: str, name: str) -> SoftwareSystem:
    return SoftwareSystem(
        id=id, name=name, description="", group=None, tags=[], url=None,
        containers=[], relationships=[], documentation=Documentation(), properties={},
    )


def _make_workspace_with_docs() -> Workspace:
    sections = [
        Section(content="## Home\n", filename="00-index.md", format="", order=0, title=""),
        Section(content="## Database Schemas\n", filename="06-databases.md", format="", order=6, title=""),
        Section(content="## Bounded Contexts\n", filename="02-bounded-contexts.md", format="", order=2, title=""),
    ]
    return Workspace(
        name="Test", description="",
        software_systems=[_make_system("1", "SCOREHUB"), _make_system("2", "Newsletter (Fanclub)")],
        people=[],
        documentation=Documentation(sections=sections),
        views=[], properties={},
    )


class TestBumpHeadings:
    def test_bump_by_one(self):
        assert _bump_headings("# Title", 1) == "## Title"

    def test_bump_by_two(self):
        assert _bump_headings("# Title\n## Sub", 2) == "### Title\n#### Sub"

    def test_clamps_at_h6(self):
        assert _bump_headings("##### H5", 2) == "###### H5"

    def test_clamps_h6_stays_h6(self):
        assert _bump_headings("###### H6", 1) == "###### H6"

    def test_clamps_h4_bump_5(self):
        assert _bump_headings("#### H4", 5) == "###### H4"

    def test_does_not_touch_headings_in_code_fences(self):
        # A `#` line inside a fenced code block is a comment, not a heading.
        text = "Some text\n```\n# comment in code\n```"
        assert _bump_headings(text, 1) == text

    def test_preserves_heading_content(self):
        assert _bump_headings("## Hello World!", 1) == "### Hello World!"


class TestResolveEmbeds:
    def test_replaces_known_view_key(self):
        content = "![diagram](embed:SystemContext)"
        result = _resolve_embeds(content, {"SystemContext"}, "diagrams/")
        assert '<div class="diagram-container">' in result
        assert '<object data="diagrams/structurizr-SystemContext.svg" type="image/svg+xml" class="diagram">diagram</object>' in result
        assert 'class="diagram-zoom-btn"' in result

    def test_leaves_unknown_key_unchanged(self):
        content = "![diagram](embed:Unknown)"
        result = _resolve_embeds(content, {"SystemContext"}, "diagrams/")
        assert result == "![diagram](embed:Unknown)"

    def test_multiple_embeds(self):
        content = "![a](embed:A)\n![b](embed:B)"
        result = _resolve_embeds(content, {"A", "B"}, "../diagrams/")
        assert "structurizr-A.svg" in result
        assert "structurizr-B.svg" in result

    def test_preserves_alt_text(self):
        content = "![My Alt Text](embed:Key1)"
        result = _resolve_embeds(content, {"Key1"}, "d/")
        assert '<object data="d/structurizr-Key1.svg" type="image/svg+xml" class="diagram">My Alt Text</object>' in result
        assert 'data-diagram-title="My Alt Text"' in result


class TestRewriteAssetPaths:
    def test_rewrites_absolute_image_path(self):
        content = "![logo](/pictures/logo.png)"
        assert _rewrite_asset_paths(content, "../../") == "![logo](../../pictures/logo.png)"

    def test_no_prefix(self):
        content = "![logo](/pictures/logo.png)"
        assert _rewrite_asset_paths(content, "") == "![logo](pictures/logo.png)"

    def test_leaves_relative_paths_alone(self):
        content = "![logo](pictures/logo.png)"
        assert _rewrite_asset_paths(content, "../../") == "![logo](pictures/logo.png)"


class TestRewriteDecisionLinks:
    def test_rewrites_known_decision(self):
        content = "See [ADR](#3) for details."
        assert _rewrite_decision_links(content, {"3", "4"}) == "See [ADR](3.md) for details."

    def test_leaves_unknown_decision(self):
        content = "See [ADR](#99) for details."
        assert _rewrite_decision_links(content, {"3"}) == "See [ADR](#99) for details."

    def test_multiple_links(self):
        content = "See [A](#1) and [B](#2)."
        result = _rewrite_decision_links(content, {"1", "2"})
        assert result == "See [A](1.md) and [B](2.md)."


class TestExtractPumlBlocks:
    def test_extracts_puml_block(self, tmp_path):
        content = "before\n```puml\n@startuml\nA -> B\n@enduml\n```\nafter"
        counter = [0]
        result = _extract_puml_blocks(content, tmp_path, "diagrams/", counter)
        assert "![Diagram](diagrams/inline-1.svg)" in result
        assert "before" in result
        assert "after" in result
        assert (tmp_path / "inline-1.puml").exists()
        assert "@startuml" in (tmp_path / "inline-1.puml").read_text()

    def test_skips_nested_puml(self, tmp_path):
        content = "````markdown\n```puml\n@startuml\n```\n````"
        counter = [0]
        result = _extract_puml_blocks(content, tmp_path, "d/", counter)
        assert "inline-" not in result
        assert counter[0] == 0

    def test_counter_increments(self, tmp_path):
        content = "```puml\nA\n```\n```puml\nB\n```"
        counter = [0]
        _extract_puml_blocks(content, tmp_path, "d/", counter)
        assert counter[0] == 2
        assert (tmp_path / "inline-1.puml").exists()
        assert (tmp_path / "inline-2.puml").exists()


class TestExtractDescriptionParagraph:
    def test_extracts_first_paragraph(self):
        content = "# Description\n\nThis is the description.\n\n## Next Section\n"
        assert _extract_description_paragraph(content) == "This is the description."

    def test_returns_none_when_no_description_heading(self):
        content = "# Overview\n\nSome text.\n"
        assert _extract_description_paragraph(content) is None

    def test_returns_none_when_description_empty(self):
        content = "# Description\n\n## Next Section\n"
        assert _extract_description_paragraph(content) is None

    def test_works_with_h2(self):
        content = "## Description\n\nA h2 description.\n"
        assert _extract_description_paragraph(content) == "A h2 description."

    def test_skips_blank_lines_before_paragraph(self):
        content = "# Description\n\n\n\nActual text.\n"
        assert _extract_description_paragraph(content) == "Actual text."


class TestStripDescriptionSection:
    def test_strips_description_section(self):
        content = "# Description\n\nSome text.\n\n# Next Section\n\nKeep this.\n"
        result = _strip_description_section(content)
        assert "Description" not in result
        assert "Some text." not in result
        assert "# Next Section" in result
        assert "Keep this." in result

    def test_preserves_content_without_description(self):
        content = "# Overview\n\nSome text.\n"
        assert _strip_description_section(content) == content

    def test_strips_h2_description(self):
        content = "# Intro\n\n## Description\n\nDesc text.\n\n## Other\n\nKept.\n"
        result = _strip_description_section(content)
        assert "Desc text." not in result
        assert "# Intro" in result
        assert "## Other" in result
        assert "Kept." in result

    def test_strips_description_at_end(self):
        content = "# Intro\n\n# Description\n\nLast section.\n"
        result = _strip_description_section(content)
        assert "Last section." not in result
        assert "# Intro" in result


class TestElementTagBadges:
    def test_returns_badges_for_styled_tags(self):
        styles = {"External System": {"background": "#999"}, "New": {"background": "#0f0"}}
        result = _element_tag_badges(["Software System", "External System", "New"], styles)
        assert '<span class="element-tag">External System</span>' in result
        assert '<span class="element-tag">New</span>' in result

    def test_hides_structural_tags(self):
        styles = {"Software System": {"background": "#fff"}}
        result = _element_tag_badges(["Element", "Software System", "Container"], styles)
        assert result == ""

    def test_skips_unstyled_tags(self):
        styles = {"External System": {"background": "#999"}}
        result = _element_tag_badges(["External System", "CustomTag"], styles)
        assert "External System" in result
        assert "CustomTag" not in result

    def test_empty_tags(self):
        assert _element_tag_badges([], {}) == ""



    def test_adds_view_source_when_enabled(self):
        content = "```mermaid\ngraph LR\n  A --> B\n```"
        result = _add_mermaid_view_source(content, enabled=True)
        assert "```mermaid" in result
        assert '??? info "View Source"' in result
        assert "    graph LR" in result

    def test_disabled_by_default(self):
        content = "```mermaid\ngraph LR\n  A --> B\n```"
        result = _add_mermaid_view_source(content)
        assert '??? info "View Source"' not in result
        assert result == content

    def test_skips_nested_mermaid(self):
        content = "````markdown\n```mermaid\ngraph LR\n```\n````"
        result = _add_mermaid_view_source(content, enabled=True)
        assert '??? info "View Source"' not in result

    def test_preserves_non_mermaid_content(self):
        content = "# Title\n\nSome text.\n"
        assert _add_mermaid_view_source(content, enabled=True) == content


class TestPromoteHeadings:
    def test_promotes_h2_to_h1(self):
        content = "## Title\n\n### Sub\n\nText."
        assert _promote_headings(content) == "# Title\n\n## Sub\n\nText."

    def test_leaves_h1_content_alone(self):
        content = "# Title\n\n## Sub\n"
        assert _promote_headings(content) == content

    def test_no_headings_unchanged(self):
        content = "Just text.\n"
        assert _promote_headings(content) == content

    def test_promotes_h3_start_by_two(self):
        content = "### Deep\n\n#### Deeper\n"
        assert _promote_headings(content) == "# Deep\n\n## Deeper\n"

    def test_doc_opening_with_admonition_left_alone(self):
        # Headings below prose/admonitions are section headings, not a title
        content = '!!! note "Quick Summary"\n\n    text\n\n## Bounded Contexts\n\n## Personas\n'
        assert _promote_headings(content) == content


class TestRewriteAbsoluteLinks:
    def test_system_link(self):
        ws = _make_workspace_with_docs()
        content = "[SCOREHUB](/scorehub/) runs on-prem."
        result = _rewrite_absolute_links(content, _abs_link_targets(ws), "../../")
        assert result == "[SCOREHUB](../../software-systems/scorehub/index.md) runs on-prem."

    def test_system_link_with_parens_in_slug(self):
        ws = _make_workspace_with_docs()
        content = "See [Newsletter](/newsletter-(fanclub)/)."
        result = _rewrite_absolute_links(content, _abs_link_targets(ws), "../")
        assert result == "See [Newsletter](../software-systems/newsletter-fanclub/index.md)."

    def test_doc_section_link_with_anchor(self):
        ws = _make_workspace_with_docs()
        content = "[Prod](/database-schemas/#production)"
        result = _rewrite_absolute_links(content, _abs_link_targets(ws), "../")
        assert result == "[Prod](../documentation/06-databases.md#production)"

    def test_decision_link(self):
        ws = _make_workspace_with_docs()
        content = "See [ADR 11](/decisions/11/)."
        result = _rewrite_absolute_links(content, _abs_link_targets(ws), "../")
        assert result == "See [ADR 11](../adrs/11.md)."

    def test_system_deep_link_maps_to_index(self):
        ws = _make_workspace_with_docs()
        content = "[Ref](/scorehub/sections/technical-architecture/)"
        result = _rewrite_absolute_links(content, _abs_link_targets(ws), "../../")
        assert result == "[Ref](../../software-systems/scorehub/index.md)"

    def test_unknown_slug_left_alone(self):
        ws = _make_workspace_with_docs()
        content = "[Mystery](/does-not-exist/)"
        assert _rewrite_absolute_links(content, _abs_link_targets(ws), "../") == content

    def test_asset_path_left_alone(self):
        ws = _make_workspace_with_docs()
        content = "![logo](/pictures/logo.png)"
        assert _rewrite_absolute_links(content, _abs_link_targets(ws), "../") == content

    def test_home_section_maps_to_index(self):
        ws = _make_workspace_with_docs()
        content = "[Home](/home/)"
        result = _rewrite_absolute_links(content, _abs_link_targets(ws), "../")
        assert result == "[Home](../index.md)"

    def test_link_inside_code_fence_left_alone(self):
        ws = _make_workspace_with_docs()
        content = "```\n[SCOREHUB](/scorehub/)\n```"
        assert _rewrite_absolute_links(content, _abs_link_targets(ws), "../") == content


class TestResolveEmbedsImageViews:
    def test_raster_image_view_embeds_as_img(self):
        content = "![State machine](embed:StateMachine)"
        result = _resolve_embeds(content, {"StateMachine"}, "diagrams/", {"StateMachine": ".png"})
        assert result == "![State machine](diagrams/structurizr-StateMachine.png)"

    def test_svg_view_keeps_object_embed(self):
        content = "![diagram](embed:Ctx)"
        result = _resolve_embeds(content, {"Ctx"}, "diagrams/", {})
        assert "structurizr-Ctx.svg" in result
        assert "<object" in result
