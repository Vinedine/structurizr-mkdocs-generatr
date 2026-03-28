"""Parse Structurizr workspace JSON into Python dataclasses."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Section:
    content: str
    filename: str
    format: str
    order: int
    title: str


@dataclass
class Decision:
    id: str
    date: str
    status: str
    title: str
    content: str
    format: str


@dataclass
class Documentation:
    sections: list[Section] = field(default_factory=list)
    decisions: list[Decision] = field(default_factory=list)


@dataclass
class Relationship:
    id: str
    source_id: str
    destination_id: str
    description: str
    technology: str


@dataclass
class Component:
    id: str
    name: str
    description: str
    technology: str
    tags: list[str]
    documentation: Documentation


@dataclass
class Container:
    id: str
    name: str
    description: str
    technology: str
    tags: list[str]
    components: list[Component]
    documentation: Documentation


@dataclass
class SoftwareSystem:
    id: str
    name: str
    description: str
    group: str | None
    tags: list[str]
    url: str | None
    containers: list[Container]
    relationships: list[Relationship]
    documentation: Documentation
    properties: dict[str, str]


@dataclass
class Person:
    id: str
    name: str
    description: str
    tags: list[str]


@dataclass
class View:
    key: str
    type: str
    software_system_id: str | None
    container_id: str | None
    title: str
    description: str


@dataclass
class Workspace:
    name: str
    description: str
    software_systems: list[SoftwareSystem]
    people: list[Person]
    documentation: Documentation
    views: list[View]
    properties: dict[str, str]

    def find_system_by_id(self, system_id: str) -> SoftwareSystem | None:
        for ss in self.software_systems:
            if ss.id == system_id:
                return ss
        return None

    def find_container_by_id(self, container_id: str) -> tuple[SoftwareSystem, Container] | None:
        for ss in self.software_systems:
            for c in ss.containers:
                if c.id == container_id:
                    return ss, c
        return None

    def views_for_system(self, system_id: str) -> list[View]:
        return [v for v in self.views if v.software_system_id == system_id]

    def views_for_container(self, container_id: str) -> list[View]:
        return [v for v in self.views if v.container_id == container_id]

    def landscape_views(self) -> list[View]:
        return [v for v in self.views if v.type == "systemLandscape"]


def _parse_documentation(data: dict) -> Documentation:
    doc = data.get("documentation", {})
    sections = [
        Section(
            content=s.get("content", ""),
            filename=s.get("filename", ""),
            format=s.get("format", "Markdown"),
            order=s.get("order", 0),
            title=s.get("title", ""),
        )
        for s in doc.get("sections", [])
    ]
    decisions = [
        Decision(
            id=d["id"],
            date=d.get("date", ""),
            status=d.get("status", ""),
            title=d.get("title", ""),
            content=d.get("content", ""),
            format=d.get("format", "Markdown"),
        )
        for d in doc.get("decisions", [])
    ]
    return Documentation(sections=sections, decisions=decisions)


def _parse_components(data: list[dict]) -> list[Component]:
    return [
        Component(
            id=c["id"],
            name=c["name"],
            description=c.get("description", ""),
            technology=c.get("technology", ""),
            tags=_parse_tags(c.get("tags", "")),
            documentation=_parse_documentation(c),
        )
        for c in data
    ]


def _parse_containers(data: list[dict]) -> list[Container]:
    return [
        Container(
            id=c["id"],
            name=c["name"],
            description=c.get("description", ""),
            technology=c.get("technology", ""),
            tags=_parse_tags(c.get("tags", "")),
            components=_parse_components(c.get("components", [])),
            documentation=_parse_documentation(c),
        )
        for c in data
    ]


def _parse_relationships(data: list[dict]) -> list[Relationship]:
    return [
        Relationship(
            id=r["id"],
            source_id=r["sourceId"],
            destination_id=r["destinationId"],
            description=r.get("description", ""),
            technology=r.get("technology", ""),
        )
        for r in data
    ]


def _parse_tags(tags_str: str) -> list[str]:
    if not tags_str:
        return []
    return [t.strip() for t in tags_str.split(",")]


def _parse_views(views_data: dict) -> list[View]:
    views = []
    view_type_map = {
        "systemLandscapeViews": "systemLandscape",
        "systemContextViews": "systemContext",
        "containerViews": "container",
        "componentViews": "component",
        "dynamicViews": "dynamic",
        "deploymentViews": "deployment",
        "imageViews": "image",
    }
    for json_key, view_type in view_type_map.items():
        for v in views_data.get(json_key, []):
            views.append(View(
                key=v["key"],
                type=view_type,
                software_system_id=v.get("softwareSystemId"),
                container_id=v.get("containerId"),
                title=v.get("title", ""),
                description=v.get("description", ""),
            ))
    return views


def parse_workspace(workspace_json: Path) -> Workspace:
    """Parse a workspace.json file into a Workspace dataclass."""
    with open(workspace_json) as f:
        data = json.load(f)

    model = data.get("model", {})

    software_systems = [
        SoftwareSystem(
            id=ss["id"],
            name=ss["name"],
            description=ss.get("description", ""),
            group=ss.get("group"),
            tags=_parse_tags(ss.get("tags", "")),
            url=ss.get("url"),
            containers=_parse_containers(ss.get("containers", [])),
            relationships=_parse_relationships(ss.get("relationships", [])),
            documentation=_parse_documentation(ss),
            properties=ss.get("properties", {}),
        )
        for ss in model.get("softwareSystems", [])
    ]

    people = [
        Person(
            id=p["id"],
            name=p["name"],
            description=p.get("description", ""),
            tags=_parse_tags(p.get("tags", "")),
        )
        for p in model.get("people", [])
    ]

    return Workspace(
        name=data.get("name", ""),
        description=data.get("description", ""),
        software_systems=software_systems,
        people=people,
        documentation=_parse_documentation(data),
        views=_parse_views(data.get("views", {})),
        properties=data.get("properties", {}),
    )


def normalize_name(name: str) -> str:
    """Convert a name to a URL-safe directory name."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
