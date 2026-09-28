"""Tests for mkdocs.yml navigation building."""

from __future__ import annotations

from structurizr_mkdocs_generatr.mkdocs_config import _persons_nav, _systems_nav
from structurizr_mkdocs_generatr.workspace import (
    Documentation,
    Person,
    SoftwareSystem,
    Workspace,
)


MIXED_CASE = ["Payroll", "eBilling", "Visitor Pass", "iRoster", "Archive Hub", "eForms"]
MIXED_CASE_SORTED = ["Archive Hub", "eBilling", "eForms", "iRoster", "Payroll", "Visitor Pass"]


def _make_system(id: str, name: str, group: str | None = None) -> SoftwareSystem:
    return SoftwareSystem(
        id=id, name=name, description="", group=group, tags=[], url=None,
        containers=[], relationships=[], documentation=Documentation(), properties={},
    )


def _make_workspace(
    systems: list[SoftwareSystem] | None = None,
    people: list[Person] | None = None,
) -> Workspace:
    return Workspace(
        name="Test", description="", software_systems=systems or [], people=people or [],
        documentation=Documentation(), views=[], properties={},
    )


def _titles(entries: list) -> list[str]:
    """Nav entry titles, skipping the leading index page."""
    return [next(iter(entry)) for entry in entries[1:]]


class TestSystemsNav:
    def test_flat_list_is_case_insensitive(self):
        ws = _make_workspace(systems=[_make_system(str(i), n) for i, n in enumerate(MIXED_CASE)])
        assert _titles(_systems_nav(ws)) == MIXED_CASE_SORTED

    def test_grouped_systems_are_case_insensitive(self):
        ws = _make_workspace(systems=[_make_system(str(i), n, group="Ops") for i, n in enumerate(MIXED_CASE)])
        nav = _systems_nav(ws)
        group_nav = nav[1]["Ops"]
        assert _titles(group_nav) == MIXED_CASE_SORTED

    def test_ungrouped_systems_are_case_insensitive(self):
        systems = [_make_system(str(i), n) for i, n in enumerate(MIXED_CASE)]
        ws = _make_workspace(systems=[*systems, _make_system("g", "Grouped", group="Ops")])
        nav = _systems_nav(ws)
        # Group sub-section first, then the ungrouped systems
        assert _titles(nav) == ["Ops", *MIXED_CASE_SORTED]


class TestPersonsNav:
    def test_is_case_insensitive(self):
        people = [
            Person(id=f"p{i}", name=n, description="", tags=[], relationships=[])
            for i, n in enumerate(["Visitor", "eLearning Admin", "Approver"])
        ]
        assert _titles(_persons_nav(_make_workspace(people=people))) == ["Approver", "eLearning Admin", "Visitor"]
