"""Parse boundedContext.mmd and generate bounded context documentation pages."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .fileutils import write_file
from .mermaid_utils import add_mermaid_view_source
from .workspace import SoftwareSystem, Workspace, normalize_name

# Entity IDs in boundedContext.mmd must be UPPER_CASE with underscores
# (e.g. ACCOUNT, LOAN_APP). camelCase or PascalCase IDs are not matched.
_ENTITY_ID_RE = re.compile(r"([A-Z_][A-Z_0-9]*)")
# Matches node definitions like ENTITY_ID[Label]
_NODE_DEF_RE = re.compile(r"([A-Z_][A-Z_0-9]*)\[([^\]]+)\]")
# Matches click lines like: click ENTITY_ID 'https://...'
_CLICK_RE = re.compile(r"click\s+([A-Z_][A-Z_0-9]*)\s+['\"]([^'\"]+)['\"]")
# Matches a markdown link [Label](target)
_MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def _extract_entity_ids(text: str, valid: dict[str, str]) -> list[str]:
    """Extract entity IDs from text, keeping only those present in *valid* mapping."""
    return [eid for eid in _ENTITY_ID_RE.findall(text) if eid in valid]


def _system_link(name: str) -> str:
    """Markdown link from a capability-map page to a software-system page."""
    return f"[{name}](../software-systems/{normalize_name(name)}/index.md)"


def _entity_cell(label: str, url: str | None) -> str:
    """Render an entity table cell: a link only for http(s) URLs.

    Non-URL click values (e.g. a self-referential ``click A1 'A1'``) would
    produce broken relative links, so they're shown as literal text instead.
    """
    if url and url.startswith(("http://", "https://")):
        return f"[{label}]({url})"
    if url:
        return f"{label} (`{url}`)"
    return label


@dataclass
class BoundedContext:
    name: str
    entities: list[str] = field(default_factory=list)
    entity_labels: dict[str, str] = field(default_factory=dict)
    mermaid_section: str = ""
    description: str = ""


@dataclass
class BoundedContextModel:
    contexts: list[BoundedContext] = field(default_factory=list)
    cross_links: list[str] = field(default_factory=list)
    entity_to_context: dict[str, str] = field(default_factory=dict)
    entity_urls: dict[str, str] = field(default_factory=dict)  # entity ID -> click URL

    def related_contexts(self, ctx_name: str) -> dict[str, set[str]]:
        """For a context, find other contexts linked via cross-links.

        Returns mapping of other_context_name -> set of entity IDs used from that context.
        """
        ctx = next((c for c in self.contexts if c.name == ctx_name), None)
        if not ctx:
            return {}

        own_entities = set(ctx.entities)
        result: dict[str, set[str]] = {}

        for link_line in self.cross_links:
            entity_ids = _extract_entity_ids(link_line, self.entity_to_context)
            if not any(eid in own_entities for eid in entity_ids):
                continue
            for eid in entity_ids:
                if eid not in own_entities:
                    other_ctx = self.entity_to_context[eid]
                    result.setdefault(other_ctx, set()).add(eid)

        return result

    def context_relations(self) -> list[tuple[str, str, bool]]:
        """Compute context-to-context relationships for the overview diagram.

        Returns list of (source, target, bidirectional) tuples, deduplicated.
        """
        directed: set[tuple[str, str]] = set()

        for link_line in self.cross_links:
            entity_ids = _extract_entity_ids(link_line, self.entity_to_context)
            if len(entity_ids) < 2:
                continue
            source_ctx = self.entity_to_context[entity_ids[0]]
            for eid in entity_ids[1:]:
                target_ctx = self.entity_to_context[eid]
                if source_ctx != target_ctx:
                    directed.add((source_ctx, target_ctx))

        # Deduplicate into bidirectional pairs
        seen: set[tuple[str, str]] = set()
        result: list[tuple[str, str, bool]] = []

        for src, tgt in sorted(directed):
            pair = tuple(sorted([src, tgt]))
            if pair in seen:
                continue
            seen.add(pair)
            bidi = (src, tgt) in directed and (tgt, src) in directed
            if bidi:
                result.append((pair[0], pair[1], True))
            else:
                result.append((src, tgt, False))

        return result


def parse_bounded_contexts(mmd_path: Path) -> BoundedContextModel | None:
    """Parse a boundedContext.mmd file into a BoundedContextModel."""
    if not mmd_path.exists():
        return None

    content = mmd_path.read_text(encoding="utf-8")

    # Extract cross-context links
    cross_links: list[str] = []
    link_match = re.search(
        r"%% \[START\.LINK\]([\s\S]*?)%% \[END\.LINK\]", content
    )
    if link_match:
        for line in link_match.group(1).strip().split("\n"):
            line = line.strip()
            if line and not line.startswith("%%"):
                cross_links.append(line)

    # Extract context blocks
    contexts: list[BoundedContext] = []
    entity_to_context: dict[str, str] = {}
    entity_urls: dict[str, str] = {}

    context_regex = re.compile(
        r"%% \[START\.CONTEXT\] \[(.*?)\]([\s\S]*?)%% \[END\.CONTEXT\] \[\1\]"
    )
    for match in context_regex.finditer(content):
        name = match.group(1)
        section = match.group(2).strip()

        # Extract description from %% [DESC] line
        description = ""
        desc_match = re.search(r"%% \[DESC\]\s*(.+)", section)
        if desc_match:
            description = desc_match.group(1).strip()

        # Extract entity IDs and labels from node definitions like ID[Label]
        entities: list[str] = []
        entity_labels: dict[str, str] = {}
        for node_match in _NODE_DEF_RE.finditer(section):
            eid, label = node_match.group(1), node_match.group(2)
            if eid not in entity_labels:
                entities.append(eid)
                entity_labels[eid] = label

        # Build mermaid section: strip comment markers, keep subgraph/edges/clicks
        mermaid_lines: list[str] = []
        for line in section.split("\n"):
            if not line.strip().startswith("%%"):
                mermaid_lines.append(line)
        mermaid_section = "\n".join(mermaid_lines).strip()

        ctx = BoundedContext(
            name=name,
            entities=entities,
            entity_labels=entity_labels,
            mermaid_section=mermaid_section,
            description=description,
        )
        contexts.append(ctx)

        for eid in entities:
            entity_to_context[eid] = name

        # Entity click-through URLs (e.g. Confluence pages)
        for click_match in _CLICK_RE.finditer(section):
            entity_urls.setdefault(click_match.group(1), click_match.group(2))

    if not contexts:
        return None

    contexts.sort(key=lambda c: c.name)

    return BoundedContextModel(
        contexts=contexts,
        cross_links=cross_links,
        entity_to_context=entity_to_context,
        entity_urls=entity_urls,
    )


def _parse_intro(intro_content: str) -> tuple[list[str], list[str], list[tuple[str, str]]]:
    """Extract context names, capabilities, and entity references from an introduction doc.

    Entity references come in two dialects and are returned as (label, target)
    tuples: ``- [Label](https://confluence/...)`` list items under Business
    Data / Manage / Consume, and ``| [Label](ENTITY_ID) | ...`` rows in a
    Data Landscape table.
    """
    context_names: list[str] = []
    capabilities: list[str] = []
    entity_refs: list[tuple[str, str]] = []
    current_section = ""

    for line in intro_content.split("\n"):
        stripped = line.strip()
        if stripped.startswith("# ") and not stripped.startswith("## "):
            current_section = stripped[2:].strip()
            continue
        if stripped.startswith("## "):
            if current_section.startswith("Business Data"):
                sub = stripped[3:].strip()
                current_section = f"Business Data/{sub}"
            else:
                current_section = ""
            continue

        if current_section in (
            "Business Data/Context", "Business Data/Bounded Context",
            "Bounded Context",
        ):
            link_match = re.search(r"\[([^\]]+)\]", stripped)
            if link_match:
                context_names.append(link_match.group(1))
            elif stripped.startswith("- "):
                name = stripped[2:].strip()
                if name:
                    context_names.append(name)
        elif current_section in ("Capabilities", "Business Capabilities"):
            if stripped.startswith("- "):
                cap = stripped[2:].strip()
                # Strip markdown links from capability text
                cap = _MD_LINK_RE.sub(r"\1", cap)
                if cap:
                    capabilities.append(cap)
        elif (
            (current_section in ("Business Data/Manage", "Business Data/Consume")
             and stripped.startswith("- "))
            or (current_section == "Data Landscape" and stripped.startswith("|"))
        ):
            m = _MD_LINK_RE.search(stripped)
            if m:
                entity_refs.append((m.group(1), m.group(2)))

    return context_names, capabilities, entity_refs


@dataclass
class ContextMapping:
    """Everything the capability-map pages need about system/entity usage."""
    system_map: dict[str, list[SoftwareSystem]]
    cap_map: dict[str, dict[str, list[str]]]
    # entity ID -> sorted system names whose intro references it
    entity_systems: dict[str, list[str]] = field(default_factory=dict)
    # entity references that resolve to no modelled entity: (label, target, sorted system names)
    unlinked_entities: list[tuple[str, str, list[str]]] = field(default_factory=list)


def _resolve_entity_ref(
    label: str, target: str, model: BoundedContextModel,
    url_to_eid: dict[str, str], label_to_eid: dict[str, str],
) -> str | None:
    """Resolve an intro entity reference to a modelled entity ID, or None."""
    if target in model.entity_to_context:  # [Label](ENTITY_ID) dialect
        return target
    if target in url_to_eid:  # [Label](click-url) dialect
        return url_to_eid[target]
    return label_to_eid.get(normalize_name(label))  # last resort: label match


def map_contexts(model: BoundedContextModel, workspace: Workspace) -> ContextMapping:
    """Single-pass mapping of contexts to systems, capabilities, and entity usage."""
    context_names = {c.name for c in model.contexts}
    system_map: dict[str, list[SoftwareSystem]] = {name: [] for name in context_names}
    cap_map: dict[str, dict[str, list[str]]] = {name: {} for name in context_names}

    url_to_eid = {url: eid for eid, url in model.entity_urls.items()}
    label_to_eid: dict[str, str] = {}
    for ctx in model.contexts:
        for eid, label in ctx.entity_labels.items():
            label_to_eid.setdefault(normalize_name(label), eid)

    entity_systems: dict[str, set[str]] = {}
    unlinked: dict[tuple[str, str], set[str]] = {}

    for ss in workspace.software_systems:
        intro = next(
            (s for s in ss.documentation.sections
             if s.filename and s.filename.endswith("introduction.md")),
            None,
        )
        if not intro:
            continue

        ctx_names, capabilities, entity_refs = _parse_intro(intro.content)
        for ctx_name in ctx_names:
            if ctx_name in context_names:
                system_map[ctx_name].append(ss)
                if capabilities:
                    cap_map[ctx_name][ss.name] = capabilities

        for label, target in entity_refs:
            eid = _resolve_entity_ref(label, target, model, url_to_eid, label_to_eid)
            if eid:
                entity_systems.setdefault(eid, set()).add(ss.name)
            else:
                unlinked.setdefault((label, target), set()).add(ss.name)

    for ctx_name in system_map:
        system_map[ctx_name].sort(key=lambda s: s.name)

    return ContextMapping(
        system_map=system_map,
        cap_map=cap_map,
        entity_systems={eid: sorted(names) for eid, names in entity_systems.items()},
        unlinked_entities=[
            (label, target, sorted(names))
            for (label, target), names in sorted(unlinked.items())
        ],
    )


def _context_id(name: str) -> str:
    """Convert context name to mermaid node ID."""
    return name.replace(" ", "_").upper()


_LABEL_SPLIT_RE = re.compile(r"(?<=/) |(?<=&) | ")
_MARGIN_PER_EXTRA_LINE = 20  # px per line beyond the first


def _wrap_label(name: str, max_len: int = 20) -> str:
    """Wrap a long label with <br/> for Mermaid rendering.

    Splits on spaces, ``/``, and ``&`` (keeping the delimiter with the first
    part) and builds lines up to *max_len* characters each.
    """
    if len(name) <= max_len:
        return name
    tokens = _LABEL_SPLIT_RE.split(name)
    lines: list[str] = []
    current = tokens[0]
    for token in tokens[1:]:
        if len(current) + 1 + len(token) <= max_len:
            current += " " + token
        else:
            lines.append(current)
            current = token
    lines.append(current)
    return "<br/>".join(lines)


def _mermaid_init(labels: list[str]) -> str:
    """Build a Mermaid init directive with dynamic subgraph title margin."""
    max_lines = max((label.count("<br/>") + 1 for label in labels), default=1)
    if max_lines <= 1:
        return ""
    margin = (max_lines - 1) * _MARGIN_PER_EXTRA_LINE
    return f'%%{{init: {{"flowchart": {{"subGraphTitleMargin": {{"bottom": {margin}}}}}}} }}%%\n'


def write_bounded_context_index(
    model: BoundedContextModel,
    mapping: ContextMapping,
    docs_dir: Path,
    *,
    mermaid_view_source: bool = False,
) -> None:
    """Write docs/capability-map/index.md with intro, table, and relations diagram."""
    system_map, cap_map = mapping.system_map, mapping.cap_map
    bc_dir = docs_dir / "capability-map"
    bc_dir.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("# Capability Map\n\n")
    lines.append(
        '??? question "What questions does this answer?"\n\n'
        "    - *Which systems support our revenue stream?*\n"
        "    - *Where do we have business capability gaps or redundant overlap?*\n"
        "    - *If we decommission a system, which business areas are affected?*\n"
        "    - *Which key data entities does no system claim, and which claims are unknown to the model?*\n\n"
    )
    lines.append("## Bounded Contexts\n\n")

    # Relations diagram
    relations = model.context_relations()
    if relations:
        lines.append("```mermaid\n")
        lines.append("flowchart TB\n")
        for ctx in model.contexts:
            cid = _context_id(ctx.name)
            label = _wrap_label(ctx.name)
            lines.append(f'\t{cid}["{label}"]\n')
        lines.append("\n")
        for src, tgt, bidi in relations:
            src_id = _context_id(src)
            tgt_id = _context_id(tgt)
            if bidi:
                lines.append(f"\t{src_id} <--> {tgt_id}\n")
            else:
                lines.append(f"\t{src_id} --> {tgt_id}\n")
        lines.append("```\n\n")

    # Table
    lines.append(
        "| Bounded Context | Description | Software Systems | Business Capabilities | Unreferenced Entities |\n")
    lines.append("|---|---|---|---|---|\n")
    for ctx in model.contexts:
        slug = normalize_name(ctx.name)
        sys_count = len(system_map.get(ctx.name, []))
        cap_count = sum(len(caps) for caps in cap_map.get(ctx.name, {}).values())
        unref_count = sum(1 for eid in ctx.entities if eid not in mapping.entity_systems)
        desc = ctx.description or ""
        lines.append(f"| [{ctx.name}]({slug}.md) | {desc} | {sys_count} | {cap_count} | {unref_count} |\n")
    lines.append("\n")

    # Entities claimed by product docs but unknown to the model
    if mapping.unlinked_entities:
        lines.append("## Unlinked Entities\n\n")
        lines.append(
            "Key data entities referenced on product pages but not mapped to any "
            "bounded context. Add them to `boundedContext.mmd` or fix the product doc.\n\n"
        )
        lines.append("| Entity | Referenced by |\n")
        lines.append("|---|---|\n")
        for label, target, systems in mapping.unlinked_entities:
            entity_cell = _entity_cell(label, target)
            system_cells = ", ".join(_system_link(name) for name in systems)
            lines.append(f"| {entity_cell} | {system_cells} |\n")
        lines.append("\n")

    content = add_mermaid_view_source("".join(lines), mermaid_view_source)
    write_file(bc_dir / "index.md", content)


def write_bounded_context_pages(
    model: BoundedContextModel,
    mapping: ContextMapping,
    workspace: Workspace,
    docs_dir: Path,
    *,
    mermaid_view_source: bool = False,
) -> None:
    """Write individual bounded context pages to docs/capability-map/{slug}.md."""
    system_map, cap_map = mapping.system_map, mapping.cap_map
    bc_dir = docs_dir / "capability-map"
    bc_dir.mkdir(parents=True, exist_ok=True)

    context_by_name = {c.name: c for c in model.contexts}

    for ctx in model.contexts:
        slug = normalize_name(ctx.name)
        lines: list[str] = []
        lines.append(f"# {ctx.name}\n\n")
        lines.append("## Bounded Context\n\n")
        if ctx.description:
            lines.append(f"{ctx.description}\n\n")

        # Collect related subgraph labels to calculate dynamic margin
        related = model.related_contexts(ctx.name)
        related_label_map = {rn: _wrap_label(rn) for rn in related}
        init_directive = _mermaid_init(list(related_label_map.values()))

        lines.append("```mermaid\n")
        if init_directive:
            lines.append(init_directive)
        lines.append("flowchart TB\n\n")

        # Main context mermaid section
        lines.append(f"{ctx.mermaid_section}\n")

        # Related context subgraphs (only entities used in cross-links)
        for related_name in sorted(related):
            related_ctx = context_by_name.get(related_name)
            if not related_ctx:
                continue
            entity_ids = sorted(related[related_name])
            lines.append(f'\n\tsubgraph "{related_label_map[related_name]}"\n')
            for eid in entity_ids:
                label = related_ctx.entity_labels.get(eid, eid)
                lines.append(f"\t\t{eid}[{label}]\n")
            lines.append("\tend\n")

        # Cross-context link lines relevant to this context
        own_entities = set(ctx.entities)
        all_related_entities = set()
        for eids in related.values():
            all_related_entities.update(eids)
        relevant_entities = own_entities | all_related_entities

        for link_line in model.cross_links:
            entity_ids = _extract_entity_ids(link_line, model.entity_to_context)
            if any(eid in relevant_entities for eid in entity_ids) and all(
                eid in relevant_entities for eid in entity_ids
            ):
                lines.append(f"\n    {link_line}")

        lines.append("\n```\n\n")

        # Key data entities: which systems actually reference each one.
        # An empty "Referenced by" cell is the drift signal (modelled entity
        # that no product doc claims).
        if ctx.entities:
            lines.append("## Key Data Entities\n\n")
            lines.append("| Entity | Referenced by |\n")
            lines.append("|---|---|\n")
            for eid in sorted(ctx.entities, key=lambda e: ctx.entity_labels.get(e, e).lower()):
                label = ctx.entity_labels.get(eid, eid)
                entity_cell = _entity_cell(label, model.entity_urls.get(eid))
                systems = mapping.entity_systems.get(eid, [])
                system_cells = ", ".join(_system_link(name) for name in systems) or "*none*"
                lines.append(f"| {entity_cell} | {system_cells} |\n")
            lines.append("\n")

        # Capabilities by software system
        ctx_caps = cap_map.get(ctx.name, {})
        if ctx_caps:
            lines.append("## Business Capabilities\n\n")
            for system_name in sorted(ctx_caps):
                lines.append(f"### {_system_link(system_name)}\n\n")
                for cap in ctx_caps[system_name]:
                    lines.append(f"- {cap}\n")
                lines.append("\n")

        # Software Systems (only if there are systems without capabilities)
        systems = system_map.get(ctx.name, [])
        systems_without_caps = [s for s in systems if s.name not in ctx_caps]
        if systems_without_caps:
            if not ctx_caps:
                lines.append("## Software Systems\n\n")
            for ss in systems_without_caps:
                lines.append(f"- {_system_link(ss.name)}\n")
            lines.append("\n")

        content = add_mermaid_view_source("".join(lines), mermaid_view_source)
        write_file(bc_dir / f"{slug}.md", content)
