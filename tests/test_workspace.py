"""Tests for workspace dataclass methods and helpers."""

from __future__ import annotations

from structurizr_mkdocs_generatr.workspace import (
    Component,
    Container,
    Documentation,
    Person,
    Relationship,
    Section,
    SoftwareSystem,
    VIEW_SYSTEM_LANDSCAPE,
    View,
    Workspace,
    normalize_name,
    section_slug,
    section_title,
)


def _make_workspace(
    systems: list[SoftwareSystem] | None = None,
    people: list[Person] | None = None,
    views: list[View] | None = None,
    properties: dict[str, str] | None = None,
    view_properties: dict[str, str] | None = None,
) -> Workspace:
    return Workspace(
        name="Test",
        description="",
        software_systems=systems or [],
        people=people or [],
        documentation=Documentation(),
        views=views or [],
        properties=properties or {},
        view_properties=view_properties or {},
    )


def _make_system(
    id: str, name: str = "System",
    containers: list[Container] | None = None,
    relationships: list[Relationship] | None = None,
    group: str | None = None,
) -> SoftwareSystem:
    return SoftwareSystem(
        id=id, name=name, description="", group=group, tags=[], url=None,
        containers=containers or [], relationships=relationships or [],
        documentation=Documentation(), properties={},
    )


def _make_container(
    id: str, name: str = "Container",
    components: list[Component] | None = None,
    relationships: list[Relationship] | None = None,
) -> Container:
    return Container(
        id=id, name=name, description="", technology="",
        tags=[], components=components or [],
        relationships=relationships or [], documentation=Documentation(),
    )


def _make_component(id: str, name: str = "Comp", relationships: list[Relationship] | None = None) -> Component:
    return Component(
        id=id, name=name, description="", technology="", tags=[],
        relationships=relationships or [], documentation=Documentation(),
    )


def _rel(id: str, src: str, dst: str, desc: str = "", tech: str = "") -> Relationship:
    return Relationship(id=id, source_id=src, destination_id=dst, description=desc, technology=tech)


class TestNormalizeName:
    def test_simple(self):
        assert normalize_name("Internet Banking System") == "internet-banking-system"

    def test_special_chars(self):
        assert normalize_name("API (v2.0)") == "api-v2-0"

    def test_strips_leading_trailing_hyphens(self):
        assert normalize_name("--hello--") == "hello"


class TestSectionSlugAndTitle:
    def test_slug_from_title(self):
        s = Section(content="", filename="foo.md", format="", order=1, title="My Title")
        assert section_slug(s) == "my-title"

    def test_slug_from_filename(self):
        s = Section(content="", filename="01-getting-started.md", format="", order=1, title="")
        assert section_slug(s) == "01-getting-started"

    def test_title_from_title_field(self):
        s = Section(content="", filename="foo.md", format="", order=1, title="Custom Title")
        assert section_title(s) == "Custom Title"

    def test_title_from_filename_strips_number_prefix(self):
        s = Section(content="", filename="01-getting-started.md", format="", order=1, title="")
        assert section_title(s) == "Getting Started"

    def test_title_prefers_content_heading(self):
        s = Section(
            content="## Directorate for Translation\n\nIntro text.",
            filename="07-dt.md", format="", order=7, title="",
        )
        assert section_title(s) == "Directorate for Translation"

    def test_content_heading_beats_title_field(self):
        s = Section(
            content="# Real Heading\n\nText.",
            filename="foo.md", format="", order=1, title="Metadata Title",
        )
        assert section_title(s) == "Real Heading"

    def test_heading_inside_code_fence_ignored(self):
        s = Section(
            content="```\n# not a heading\n```\n\nNo headings here.",
            filename="02-notes.md", format="", order=2, title="",
        )
        assert section_title(s) == "Notes"

    def test_doc_opening_with_prose_keeps_filename_title(self):
        # A heading further down is a section heading, not the document title
        s = Section(
            content="Some intro text.\n\n### Deep Heading\n",
            filename="02-systems-and-workflows.md", format="", order=2, title="",
        )
        assert section_title(s) == "Systems And Workflows"

    def test_title_heading_may_be_any_level(self):
        s = Section(content="### Deep Title\n\nText.", filename="x.md", format="", order=1, title="")
        assert section_title(s) == "Deep Title"


class TestDependenciesForSystem:
    def test_outbound(self):
        sys_a = _make_system("1", "System A", relationships=[_rel("r1", "1", "2", "Uses", "REST")])
        sys_b = _make_system("2", "System B")
        ws = _make_workspace(systems=[sys_a, sys_b])
        inbound, outbound = ws.dependencies_for_system("1")
        assert len(outbound) == 1
        assert outbound[0][1] == "System B"
        assert len(inbound) == 0

    def test_inbound(self):
        sys_a = _make_system("1", "System A", relationships=[_rel("r1", "1", "2", "Uses", "REST")])
        sys_b = _make_system("2", "System B")
        ws = _make_workspace(systems=[sys_a, sys_b])
        inbound, outbound = ws.dependencies_for_system("2")
        assert len(inbound) == 1
        assert inbound[0][1] == "System A"
        assert len(outbound) == 0

    def test_container_level_deduplicates(self):
        c1 = _make_container("c1", relationships=[_rel("r1", "c1", "2", "Reads", "SQL")])
        c2 = _make_container("c2", relationships=[_rel("r2", "c2", "2", "Writes", "SQL")])
        sys_a = _make_system("1", "System A", containers=[c1, c2])
        sys_b = _make_system("2", "System B")
        ws = _make_workspace(systems=[sys_a, sys_b])
        _, outbound = ws.dependencies_for_system("1")
        # Both containers talk to System B, but should deduplicate to one entry
        assert len(outbound) == 1

    def test_person_inbound(self):
        sys_a = _make_system("1", "System A")
        person = Person(id="p1", name="User", description="", tags=[],
                        relationships=[_rel("r1", "p1", "1", "Uses", "Web")])
        ws = _make_workspace(systems=[sys_a], people=[person])
        inbound, _ = ws.dependencies_for_system("1")
        assert len(inbound) == 1
        assert inbound[0][1] == "User"

    def test_no_dependencies(self):
        sys_a = _make_system("1", "System A")
        ws = _make_workspace(systems=[sys_a])
        inbound, outbound = ws.dependencies_for_system("1")
        assert inbound == []
        assert outbound == []


class TestSystemForElementId:
    def test_finds_system(self):
        sys_a = _make_system("1", "System A")
        ws = _make_workspace(systems=[sys_a])
        assert ws.system_for_element_id("1") == sys_a

    def test_finds_via_container(self):
        c = _make_container("c1")
        sys_a = _make_system("1", "System A", containers=[c])
        ws = _make_workspace(systems=[sys_a])
        assert ws.system_for_element_id("c1") == sys_a

    def test_finds_via_component(self):
        comp = _make_component("comp1")
        c = _make_container("c1", components=[comp])
        sys_a = _make_system("1", "System A", containers=[c])
        ws = _make_workspace(systems=[sys_a])
        assert ws.system_for_element_id("comp1") == sys_a

    def test_returns_none_for_unknown(self):
        ws = _make_workspace()
        assert ws.system_for_element_id("unknown") is None


def _landscape_view(key: str) -> View:
    return View(
        key=key, type=VIEW_SYSTEM_LANDSCAPE, software_system_id=None,
        container_id=None, title="", description="",
    )


NESTED = {"structurizr.groupSeparator": "/"}


class TestGroups:
    def test_alphabetical_by_default(self):
        ws = _make_workspace(systems=[
            _make_system("1", group="BELFOOT/DIGITAL"),
            _make_system("2", group="BELFOOT/ACADEMY"),
            _make_system("3", group="External"),
        ])
        assert ws.groups() == ["BELFOOT/ACADEMY", "BELFOOT/DIGITAL", "External"]

    def test_group_order_property_wins(self):
        ws = _make_workspace(
            systems=[
                _make_system("1", group="BELFOOT/DIGITAL"),
                _make_system("2", group="BELFOOT/ACADEMY"),
                _make_system("3", group="External"),
            ],
            view_properties={"mkdocs.groupOrder": "BELFOOT/DIGITAL, BELFOOT/ACADEMY"},
        )
        assert ws.groups() == ["BELFOOT/DIGITAL", "BELFOOT/ACADEMY", "External"]

    def test_group_order_matches_loosely(self):
        ws = _make_workspace(
            systems=[
                _make_system("1", group="BELFOOT/DIGITAL"),
                _make_system("2", group="BELFOOT/ACADEMY"),
            ],
            view_properties={"mkdocs.groupOrder": "belfoot/digital"},
        )
        assert ws.groups() == ["BELFOOT/DIGITAL", "BELFOOT/ACADEMY"]

    def test_group_order_ignores_unknown_names(self):
        ws = _make_workspace(
            systems=[_make_system("1", group="External")],
            view_properties={"mkdocs.groupOrder": "Nope, External"},
        )
        assert ws.groups() == ["External"]


class TestGroupLandscapeView:
    def test_matches_plain_group_name(self):
        view = _landscape_view("SystemLandscapeBigBank")
        ws = _make_workspace(systems=[_make_system("1", group="Big Bank")], views=[view])
        assert ws.group_landscape_view("Big Bank") is view

    def test_nested_group_matches_last_segment(self):
        view = _landscape_view("SystemLandscapeDigital")
        ws = _make_workspace(
            systems=[_make_system("1", group="BELFOOT/DIGITAL")],
            views=[view], properties=NESTED,
        )
        assert ws.group_landscape_view("BELFOOT/DIGITAL") is view

    def test_nested_group_matches_full_name(self):
        view = _landscape_view("SystemLandscapeBELFOOT-DIGITAL")
        ws = _make_workspace(
            systems=[_make_system("1", group="BELFOOT/DIGITAL")],
            views=[view], properties=NESTED,
        )
        assert ws.group_landscape_view("BELFOOT/DIGITAL") is view

    def test_ambiguous_last_segment_is_not_matched(self):
        view = _landscape_view("SystemLandscapeAcademy")
        ws = _make_workspace(
            systems=[
                _make_system("1", group="BELFOOT/ACADEMY"),
                _make_system("2", group="OTHER/ACADEMY"),
            ],
            views=[view], properties=NESTED,
        )
        assert ws.group_landscape_view("BELFOOT/ACADEMY") is None

    def test_returns_none_when_no_view_exists(self):
        ws = _make_workspace(
            systems=[_make_system("1", group="BELFOOT/ACADEMY")],
            views=[_landscape_view("SystemLandscapeDigital")], properties=NESTED,
        )
        assert ws.group_landscape_view("BELFOOT/ACADEMY") is None
