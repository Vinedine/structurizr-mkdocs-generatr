"""Tests for exporter drill-down URL generation."""

from __future__ import annotations

from structurizr_mkdocs_generatr.exporter import (
    ANCHOR_COMPONENT_VIEWS,
    ANCHOR_CONTAINER_VIEW,
    ANCHOR_CONTEXT_VIEW,
    _build_element_url_map,
    _drill_down_anchor,
    _system_view_types,
)
from structurizr_mkdocs_generatr.workspace import (
    VIEW_COMPONENT,
    VIEW_CONTAINER,
    VIEW_SYSTEM_CONTEXT,
    VIEW_SYSTEM_LANDSCAPE,
    Component,
    Container,
    Documentation,
    Person,
    SoftwareSystem,
    View,
    Workspace,
)


def _make_workspace(
    systems: list[SoftwareSystem] | None = None,
    people: list[Person] | None = None,
    views: list[View] | None = None,
) -> Workspace:
    return Workspace(
        name="Test",
        description="",
        software_systems=systems or [],
        people=people or [],
        documentation=Documentation(),
        views=views or [],
        properties={},
    )


def _make_system(
    id: str, name: str = "System",
    containers: list[Container] | None = None,
) -> SoftwareSystem:
    return SoftwareSystem(
        id=id, name=name, description="", group=None, tags=[], url=None,
        containers=containers or [], relationships=[],
        documentation=Documentation(), properties={},
    )


def _make_container(id: str, name: str = "Container", components: list[Component] | None = None) -> Container:
    return Container(
        id=id, name=name, description="", technology="",
        tags=[], components=components or [], relationships=[],
        documentation=Documentation(),
    )


def _make_component(id: str, name: str = "Component") -> Component:
    return Component(
        id=id, name=name, description="", technology="",
        tags=[], relationships=[], documentation=Documentation(),
    )


def _make_view(key: str, type: str, software_system_id: str | None = None, element_id: str | None = None) -> View:
    return View(
        key=key, type=type, software_system_id=software_system_id,
        container_id=None, title="", description="",
        element_id=element_id,
    )


def _make_person(id: str, name: str = "Person") -> Person:
    return Person(id=id, name=name, description="", tags=[])


# --- _system_view_types ---

def test_system_view_types_maps_views_to_systems():
    ws = _make_workspace(
        systems=[_make_system("1", "Alpha")],
        views=[
            _make_view("ctx", VIEW_SYSTEM_CONTEXT, software_system_id="1"),
            _make_view("cnt", VIEW_CONTAINER, software_system_id="1"),
        ],
    )
    result = _system_view_types(ws)
    assert result["1"] == {VIEW_SYSTEM_CONTEXT, VIEW_CONTAINER}


def test_system_view_types_uses_element_id_fallback():
    ws = _make_workspace(
        systems=[_make_system("1", "Alpha")],
        views=[_make_view("ctx", VIEW_SYSTEM_CONTEXT, element_id="1")],
    )
    result = _system_view_types(ws)
    assert result["1"] == {VIEW_SYSTEM_CONTEXT}


# --- _drill_down_anchor ---

def test_anchor_landscape_to_context():
    available = {"1": {VIEW_SYSTEM_CONTEXT, VIEW_CONTAINER}}
    assert _drill_down_anchor("1", VIEW_SYSTEM_LANDSCAPE, None, available) == ANCHOR_CONTEXT_VIEW


def test_anchor_context_to_context_for_other_system():
    available = {"2": {VIEW_SYSTEM_CONTEXT}}
    assert _drill_down_anchor("2", VIEW_SYSTEM_CONTEXT, "1", available) == ANCHOR_CONTEXT_VIEW


def test_anchor_context_subject_to_container():
    available = {"1": {VIEW_SYSTEM_CONTEXT, VIEW_CONTAINER}}
    assert _drill_down_anchor("1", VIEW_SYSTEM_CONTEXT, "1", available) == ANCHOR_CONTAINER_VIEW


def test_anchor_context_subject_no_container_view():
    available = {"1": {VIEW_SYSTEM_CONTEXT}}
    # No container view → falls through to context-view anchor
    assert _drill_down_anchor("1", VIEW_SYSTEM_CONTEXT, "1", available) == ANCHOR_CONTEXT_VIEW


def test_anchor_no_views_available():
    assert _drill_down_anchor("1", VIEW_SYSTEM_LANDSCAPE, None, {}) == ""


def test_anchor_container_view_other_system_to_context():
    available = {
        "1": {VIEW_SYSTEM_CONTEXT, VIEW_CONTAINER},
        "2": {VIEW_SYSTEM_CONTEXT},
    }
    # Other system in a container view → drill to its context view
    assert _drill_down_anchor("2", VIEW_CONTAINER, "1", available) == ANCHOR_CONTEXT_VIEW


def test_anchor_container_view_subject_no_drill():
    available = {"1": {VIEW_SYSTEM_CONTEXT, VIEW_CONTAINER}}
    # Subject system in container view → already expanded, no anchor
    assert _drill_down_anchor("1", VIEW_CONTAINER, "1", available) == ""


# --- _build_element_url_map ---

def test_url_map_without_view_context():
    """Without view context, no anchors are appended."""
    ws = _make_workspace(
        systems=[_make_system("1", "Alpha")],
        people=[_make_person("p1", "Bob")],
    )
    urls = _build_element_url_map(ws)
    assert urls["Alpha"] == "../software-systems/alpha/"
    assert urls["Bob"] == "../persons/bob/"


def test_url_map_landscape_adds_context_anchor():
    ws = _make_workspace(
        systems=[_make_system("1", "Alpha"), _make_system("2", "Beta")],
        views=[
            _make_view("ctx1", VIEW_SYSTEM_CONTEXT, software_system_id="1"),
            _make_view("ctx2", VIEW_SYSTEM_CONTEXT, software_system_id="2"),
        ],
    )
    urls = _build_element_url_map(ws, VIEW_SYSTEM_LANDSCAPE)
    assert urls["Alpha"] == f"../software-systems/alpha/{ANCHOR_CONTEXT_VIEW}"
    assert urls["Beta"] == f"../software-systems/beta/{ANCHOR_CONTEXT_VIEW}"


def test_url_map_context_subject_drills_to_container():
    ws = _make_workspace(
        systems=[_make_system("1", "Alpha"), _make_system("2", "Beta")],
        views=[
            _make_view("ctx1", VIEW_SYSTEM_CONTEXT, software_system_id="1"),
            _make_view("cnt1", VIEW_CONTAINER, software_system_id="1"),
            _make_view("ctx2", VIEW_SYSTEM_CONTEXT, software_system_id="2"),
        ],
    )
    urls = _build_element_url_map(ws, VIEW_SYSTEM_CONTEXT, subject_system_id="1")
    # Subject system drills to container view
    assert urls["Alpha"] == f"../software-systems/alpha/{ANCHOR_CONTAINER_VIEW}"
    # Other system drills to its context view
    assert urls["Beta"] == f"../software-systems/beta/{ANCHOR_CONTEXT_VIEW}"


def test_url_map_container_view_drills_to_components():
    comp = _make_component("c1", "MyComp")
    container = _make_container("ct1", "WebApp", components=[comp])
    ws = _make_workspace(
        systems=[_make_system("1", "Alpha", containers=[container])],
        views=[
            _make_view("cnt1", VIEW_CONTAINER, software_system_id="1"),
            _make_view("cmp1", VIEW_COMPONENT, software_system_id="1"),
        ],
    )
    urls = _build_element_url_map(ws, VIEW_CONTAINER, subject_system_id="1")
    assert urls["WebApp"] == f"../software-systems/alpha/{ANCHOR_COMPONENT_VIEWS}"
    assert urls["MyComp"] == "../software-systems/alpha/"


def test_url_map_container_view_no_component_views():
    container = _make_container("ct1", "WebApp")
    ws = _make_workspace(
        systems=[_make_system("1", "Alpha", containers=[container])],
        views=[_make_view("cnt1", VIEW_CONTAINER, software_system_id="1")],
    )
    urls = _build_element_url_map(ws, VIEW_CONTAINER, subject_system_id="1")
    # No component views → no anchor
    assert urls["WebApp"] == "../software-systems/alpha/"


def test_url_map_container_same_name_as_system():
    """Container sharing name with parent system must not overwrite system anchor."""
    container = _make_container("ct1", "Alpha")  # Same name as system
    ws = _make_workspace(
        systems=[_make_system("1", "Alpha", containers=[container])],
        views=[
            _make_view("ctx1", VIEW_SYSTEM_CONTEXT, software_system_id="1"),
        ],
    )
    urls = _build_element_url_map(ws, VIEW_SYSTEM_LANDSCAPE)
    # System-level anchor must win over container entry
    assert urls["Alpha"] == f"../software-systems/alpha/{ANCHOR_CONTEXT_VIEW}"


def test_url_map_persons_never_get_anchors():
    ws = _make_workspace(
        systems=[_make_system("1", "Alpha")],
        people=[_make_person("p1", "Bob")],
        views=[_make_view("ctx1", VIEW_SYSTEM_CONTEXT, software_system_id="1")],
    )
    urls = _build_element_url_map(ws, VIEW_SYSTEM_LANDSCAPE)
    assert urls["Bob"] == "../persons/bob/"
