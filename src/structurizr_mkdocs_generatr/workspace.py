"""Parse Structurizr workspace JSON into Python dataclasses."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path


# View type constants — used across workspace parsing and markdown generation
VIEW_SYSTEM_LANDSCAPE = "systemLandscape"
VIEW_SYSTEM_CONTEXT = "systemContext"
VIEW_CONTAINER = "container"
VIEW_COMPONENT = "component"
VIEW_DYNAMIC = "dynamic"
VIEW_DEPLOYMENT = "deployment"
VIEW_IMAGE = "image"


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
    relationships: list[Relationship]
    documentation: Documentation


@dataclass
class Container:
    id: str
    name: str
    description: str
    technology: str
    tags: list[str]
    components: list[Component]
    relationships: list[Relationship]
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
    relationships: list[Relationship] = field(default_factory=list)


@dataclass
class View:
    key: str
    type: str
    software_system_id: str | None
    container_id: str | None
    title: str
    description: str
    element_ids: list[str] = field(default_factory=list)
    element_id: str | None = None
    content: str | None = None
    content_type: str | None = None
    environment: str | None = None


@dataclass
class Workspace:
    name: str
    description: str
    software_systems: list[SoftwareSystem]
    people: list[Person]
    documentation: Documentation
    views: list[View]
    properties: dict[str, str]
    view_properties: dict[str, str] = field(default_factory=dict)
    element_styles: dict[str, dict[str, str]] = field(default_factory=dict)

    def find_system_by_id(self, system_id: str) -> SoftwareSystem | None:
        for ss in self.software_systems:
            if ss.id == system_id:
                return ss
        return None

    def views_for_system(self, system_id: str) -> list[View]:
        return [v for v in self.views
                if v.software_system_id == system_id or v.element_id == system_id]


    def landscape_views(self) -> list[View]:
        return [v for v in self.views if v.type == VIEW_SYSTEM_LANDSCAPE]

    def groups(self) -> list[str]:
        """Return sorted unique group names from software systems."""
        return sorted({ss.group for ss in self.software_systems if ss.group})

    def group_description(self, group_name: str) -> str:
        """Return the description for a group from model properties (group.{name}.description)."""
        return self.properties.get(f"group.{group_name}.description", "")

    def systems_in_group(self, group_name: str) -> list[SoftwareSystem]:
        """Return software systems belonging to a group, sorted by name."""
        return sorted(
            [ss for ss in self.software_systems if ss.group == group_name],
            key=lambda s: s.name,
        )

    def group_landscape_view(self, group_name: str) -> View | None:
        """Find the landscape view for a group (key: SystemLandscape{GroupNoSpaces})."""
        key = f"SystemLandscape{group_name.replace(' ', '')}"
        for v in self.views:
            if v.type == VIEW_SYSTEM_LANDSCAPE and v.key == key:
                return v
        return None

    def views_for_person(self, person_id: str) -> list[View]:
        """Return the dedicated per-user landscape view for this person.

        Prefers views where the person is the only person element (e.g.
        SystemLandscapeUserFan) to avoid showing group-level or full landscape
        views. Falls back to any landscape view containing the person if no
        single-person view exists.
        """
        person_ids = {p.id for p in self.people}
        single_person_views = []
        all_matching_views = []
        for v in self.views:
            if v.type != VIEW_SYSTEM_LANDSCAPE or person_id not in v.element_ids:
                continue
            all_matching_views.append(v)
            persons_in_view = [eid for eid in v.element_ids if eid in person_ids]
            if len(persons_in_view) == 1:
                single_person_views.append(v)
        return single_person_views if single_person_views else all_matching_views

    def system_for_element_id(self, element_id: str) -> SoftwareSystem | None:
        """Find the software system that owns an element (system, container, or component)."""
        for ss in self.software_systems:
            if ss.id == element_id:
                return ss
            for c in ss.containers:
                if c.id == element_id:
                    return ss
                for comp in c.components:
                    if comp.id == element_id:
                        return ss
        return None

    def _all_element_ids_for_system(self, system_id: str) -> set[str]:
        """Get all element IDs belonging to a system (system + containers + components)."""
        ids: set[str] = set()
        ss = self.find_system_by_id(system_id)
        if not ss:
            return ids
        ids.add(ss.id)
        for c in ss.containers:
            ids.add(c.id)
            for comp in c.components:
                ids.add(comp.id)
        return ids

    def _all_relationships(self) -> list[Relationship]:
        """Collect all relationships from all elements (cached after first call)."""
        if hasattr(self, "_cached_relationships"):
            return self._cached_relationships
        rels: list[Relationship] = []
        for p in self.people:
            rels.extend(p.relationships)
        for ss in self.software_systems:
            rels.extend(ss.relationships)
            for c in ss.containers:
                rels.extend(c.relationships)
                for comp in c.components:
                    rels.extend(comp.relationships)
        self._cached_relationships = rels
        return rels

    def dependencies_for_system(
        self, system_id: str,
    ) -> tuple[list[tuple[str, str, str, str]], list[tuple[str, str, str, str]]]:
        """Return (inbound, outbound) dependencies as (element_id, name, description, technology) tuples.

        Deduplicates by source/target — shows system-level dependencies, not per-container.
        """
        my_ids = self._all_element_ids_for_system(system_id)
        all_rels = self._all_relationships()

        inbound: dict[str, tuple[str, str, str, str]] = {}
        outbound: dict[str, tuple[str, str, str, str]] = {}

        for rel in all_rels:
            src_in = rel.source_id in my_ids
            dst_in = rel.destination_id in my_ids

            if src_in and not dst_in:
                target_ss = self.system_for_element_id(rel.destination_id)
                if target_ss and target_ss.id not in outbound:
                    outbound[target_ss.id] = (target_ss.id, target_ss.name, rel.description, rel.technology)
            elif dst_in and not src_in:
                source_ss = self.system_for_element_id(rel.source_id)
                if source_ss:
                    if source_ss.id not in inbound:
                        inbound[source_ss.id] = (source_ss.id, source_ss.name, rel.description, rel.technology)
                else:
                    # Could be a person
                    name = self.find_element_name_by_id(rel.source_id)
                    if name and rel.source_id not in inbound:
                        inbound[rel.source_id] = (rel.source_id, name, rel.description, rel.technology)

        return (
            sorted(inbound.values(), key=lambda x: x[1]),
            sorted(outbound.values(), key=lambda x: x[1]),
        )

    def find_element_name_by_id(self, element_id: str) -> str | None:
        for p in self.people:
            if p.id == element_id:
                return p.name
        for ss in self.software_systems:
            if ss.id == element_id:
                return ss.name
            for c in ss.containers:
                if c.id == element_id:
                    return c.name
                for comp in c.components:
                    if comp.id == element_id:
                        return comp.name
        return None

    def deployment_environments(self) -> list[str]:
        """Return unique environment names from deployment views, ordered by convention."""
        env_order = ["Production", "Acceptance", "Test", "Development"]
        envs = {v.environment for v in self.views
                if v.type == VIEW_DEPLOYMENT and v.environment}
        return [e for e in env_order if e in envs] + sorted(envs - set(env_order))

    def zone_level_views(self, environment: str) -> list[View]:
        """Return deployment views for an environment with no softwareSystemId (zone-level)."""
        return [v for v in self.views
                if v.type == VIEW_DEPLOYMENT
                and v.environment == environment
                and not v.software_system_id]

    def environment_description(self, environment: str) -> str:
        """Return description for a deployment environment from model properties."""
        return self.properties.get(f"deployment.{environment}.description", "")

    def zone_description(self, environment: str, zone_name: str) -> str:
        """Return description for a deployment zone from model properties."""
        return self.properties.get(f"deployment.{environment}.{zone_name}.description", "")


def extract_zone_name(view: View) -> str:
    """Extract zone name from deployment view description ('Deployment - Env - Zone')."""
    desc = view.description or view.title or view.key
    parts = desc.split(" - ")
    return parts[2].strip() if len(parts) >= 3 else desc


def sort_zone_views(views: list[View]) -> list[View]:
    """Sort zone views: On-Premise first, then cloud providers alphabetically."""
    def sort_key(v: View) -> tuple[int, str]:
        name = extract_zone_name(v).lower()
        if "on-premise" in name or "on premise" in name:
            return (0, name)
        return (1, name)
    return sorted(views, key=sort_key)


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
            relationships=_parse_relationships(c.get("relationships", [])),
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
            relationships=_parse_relationships(c.get("relationships", [])),
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
        "systemLandscapeViews": VIEW_SYSTEM_LANDSCAPE,
        "systemContextViews": VIEW_SYSTEM_CONTEXT,
        "containerViews": VIEW_CONTAINER,
        "componentViews": VIEW_COMPONENT,
        "dynamicViews": VIEW_DYNAMIC,
        "deploymentViews": VIEW_DEPLOYMENT,
        "imageViews": VIEW_IMAGE,
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
                element_ids=[e["id"] for e in v.get("elements", [])],
                element_id=v.get("elementId"),
                content=v.get("content"),
                content_type=v.get("contentType"),
                environment=v.get("environment"),
            ))
    return views


def parse_workspace(workspace_json: Path) -> Workspace:
    """Parse a workspace.json file into a Workspace dataclass."""
    with open(workspace_json, encoding="utf-8") as f:
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
            relationships=_parse_relationships(p.get("relationships", [])),
        )
        for p in model.get("people", [])
    ]

    views_data = data.get("views", {})
    view_config = views_data.get("configuration", {})

    # Parse element styles (tag -> {background, color, ...})
    element_styles: dict[str, dict[str, str]] = {}
    for style in view_config.get("styles", {}).get("elements", []):
        tag = style.get("tag", "")
        if tag:
            props = {k: v for k, v in style.items() if k != "tag" and isinstance(v, str)}
            if props:
                element_styles[tag] = props

    return Workspace(
        name=data.get("name", ""),
        description=data.get("description", ""),
        software_systems=software_systems,
        people=people,
        documentation=_parse_documentation(data),
        views=_parse_views(views_data),
        properties=model.get("properties", {}),
        view_properties=view_config.get("properties", {}),
        element_styles=element_styles,
    )


def normalize_name(name: str) -> str:
    """Convert a name to a URL-safe directory name."""
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def section_slug(section: Section) -> str:
    """Generate a URL-safe slug for a documentation section."""
    if section.title:
        return normalize_name(section.title)
    name = section.filename.rsplit(".", 1)[0]
    return normalize_name(name)


def section_title(section: Section) -> str:
    """Generate a human-readable title for a documentation section."""
    if section.title:
        return section.title
    name = section.filename.rsplit(".", 1)[0]
    parts = name.split("-", 1)
    if len(parts) > 1 and parts[0].isdigit():
        name = parts[1]
    return name.replace("-", " ").capitalize()
