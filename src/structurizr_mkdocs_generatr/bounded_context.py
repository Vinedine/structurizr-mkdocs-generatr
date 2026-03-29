"""Parse boundedContext.mmd and generate bounded context documentation pages."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .workspace import SoftwareSystem, Workspace, normalize_name

# Entity IDs in boundedContext.mmd must be UPPER_CASE with underscores
# (e.g. ACCOUNT, LOAN_APP). camelCase or PascalCase IDs are not matched.
_ENTITY_ID_RE = re.compile(r"([A-Z_][A-Z_0-9]*)")
_CLICK_RE = re.compile(r"click\s+([A-Z_][A-Z_0-9]*)\s")


def _extract_entity_ids(text: str, valid: dict[str, str]) -> list[str]:
    """Extract entity IDs from text, keeping only those present in *valid* mapping."""
    return [eid for eid in _ENTITY_ID_RE.findall(text) if eid in valid]


@dataclass
class BoundedContext:
    name: str
    entities: list[str] = field(default_factory=list)
    entity_labels: dict[str, str] = field(default_factory=dict)
    mermaid_section: str = ""


@dataclass
class BoundedContextModel:
    contexts: list[BoundedContext] = field(default_factory=list)
    cross_links: list[str] = field(default_factory=list)
    entity_to_context: dict[str, str] = field(default_factory=dict)

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

    context_regex = re.compile(
        r"%% \[START\.CONTEXT\] \[(.*?)\]([\s\S]*?)%% \[END\.CONTEXT\] \[\1\]"
    )
    for match in context_regex.finditer(content):
        name = match.group(1)
        section = match.group(2).strip()

        # Extract entity IDs from click lines
        entities: list[str] = []
        for click_match in _CLICK_RE.finditer(section):
            entities.append(click_match.group(1))

        # Extract entity labels from ENTITY_ID[Label] notation
        entity_labels: dict[str, str] = {}
        for eid in entities:
            label_match = re.search(
                rf"{re.escape(eid)}\[([^\]]+)\]", section
            )
            if label_match:
                entity_labels[eid] = label_match.group(1)

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
        )
        contexts.append(ctx)

        for eid in entities:
            entity_to_context[eid] = name

    if not contexts:
        return None

    contexts.sort(key=lambda c: c.name)

    return BoundedContextModel(
        contexts=contexts,
        cross_links=cross_links,
        entity_to_context=entity_to_context,
    )


def _parse_intro(intro_content: str) -> tuple[list[str], list[str]]:
    """Extract context names and capabilities from an introduction doc."""
    context_names: list[str] = []
    capabilities: list[str] = []
    current_section = ""

    for line in intro_content.split("\n"):
        stripped = line.strip()
        if stripped.startswith("# ") and not stripped.startswith("## "):
            current_section = stripped[2:].strip()
            continue
        if stripped.startswith("## "):
            if current_section == "Business Data":
                sub = stripped[3:].strip()
                current_section = f"Business Data/{sub}"
            else:
                current_section = ""
            continue

        if current_section == "Business Data/Context":
            link_match = re.search(r"\[([^\]]+)\]", stripped)
            if link_match:
                context_names.append(link_match.group(1))
        elif current_section == "Business Capabilities":
            if stripped.startswith("- "):
                cap = stripped[2:].strip()
                # Strip markdown links from capability text
                cap = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cap)
                if cap:
                    capabilities.append(cap)

    return context_names, capabilities


def map_contexts(
    model: BoundedContextModel, workspace: Workspace,
) -> tuple[dict[str, list[SoftwareSystem]], dict[str, dict[str, list[str]]]]:
    """Single-pass mapping of contexts to systems and capabilities."""
    context_names = {c.name for c in model.contexts}
    system_map: dict[str, list[SoftwareSystem]] = {name: [] for name in context_names}
    cap_map: dict[str, dict[str, list[str]]] = {name: {} for name in context_names}

    for ss in workspace.software_systems:
        intro = next(
            (s for s in ss.documentation.sections
             if s.filename and s.filename.endswith("introduction.md")),
            None,
        )
        if not intro:
            continue

        ctx_names, capabilities = _parse_intro(intro.content)
        for ctx_name in ctx_names:
            if ctx_name in context_names:
                system_map[ctx_name].append(ss)
                if capabilities:
                    cap_map[ctx_name][ss.name] = capabilities

    for ctx_name in system_map:
        system_map[ctx_name].sort(key=lambda s: s.name)

    return system_map, cap_map


def _context_id(name: str) -> str:
    """Convert context name to mermaid node ID."""
    return name.replace(" ", "_").upper()


def write_bounded_context_index(
    model: BoundedContextModel,
    system_map: dict[str, list[SoftwareSystem]],
    cap_map: dict[str, dict[str, list[str]]],
    docs_dir: Path,
) -> None:
    """Write docs/capability-map/index.md with intro, table, and relations diagram."""
    bc_dir = docs_dir / "capability-map"
    bc_dir.mkdir(parents=True, exist_ok=True)

    lines: list[str] = []
    lines.append("# Capability Map\n\n")
    lines.append(
        "A **capability map** connects what the business *does* to the systems that "
        "make it happen. It organises the enterprise into "
        "**bounded contexts**{ title=\"A linguistic and organisational boundary around "
        "a specific business domain, containing its own unified model and key data "
        "entities\" } — distinct domain areas such as ticketing, finance, or player "
        "development — and then maps each context to the **software systems** and "
        "**business capabilities** that support it.\n\n"
    )
    lines.append(
        '!!! question "What questions does this answer?"\n\n'
        "    - *Which systems support our revenue stream?*\n"
        "    - *Where do we have capability gaps or redundant overlap?*\n"
        "    - *If we decommission a system, which business areas are affected?*\n"
        "    - *How many capabilities does each domain area actually have?*\n\n"
    )
    lines.append(
        "For every bounded context the table below shows the software systems that "
        "belong to it and the total number of capabilities they provide. Click a "
        "context to see the detailed **entity model**, **cross-context relationships**, "
        "and a full **capability breakdown** per system.\n\n"
    )

    # Table
    lines.append("| Bounded Context | Software Systems | Capabilities |\n")
    lines.append("|---|---|---|\n")
    for ctx in model.contexts:
        slug = normalize_name(ctx.name)
        sys_count = len(system_map.get(ctx.name, []))
        cap_count = sum(len(caps) for caps in cap_map.get(ctx.name, {}).values())
        lines.append(f"| [{ctx.name}]({slug}.md) | {sys_count} | {cap_count} |\n")
    lines.append("\n")

    # Relations diagram
    relations = model.context_relations()
    if relations:
        lines.append("## Bounded Context Relations\n\n")
        lines.append("```mermaid\n")
        lines.append("flowchart TB\n")
        for ctx in model.contexts:
            cid = _context_id(ctx.name)
            lines.append(f"\t{cid}[{ctx.name}]\n")
        lines.append("\n")
        for src, tgt, bidi in relations:
            src_id = _context_id(src)
            tgt_id = _context_id(tgt)
            if bidi:
                lines.append(f"\t{src_id} <--> {tgt_id}\n")
            else:
                lines.append(f"\t{src_id} --> {tgt_id}\n")
        lines.append("```\n")

    (bc_dir / "index.md").write_text("".join(lines), encoding="utf-8")


def write_bounded_context_pages(
    model: BoundedContextModel,
    system_map: dict[str, list[SoftwareSystem]],
    cap_map: dict[str, dict[str, list[str]]],
    workspace: Workspace,
    docs_dir: Path,
) -> None:
    """Write individual bounded context pages to docs/capability-map/{slug}.md."""
    bc_dir = docs_dir / "capability-map"
    bc_dir.mkdir(parents=True, exist_ok=True)

    for ctx in model.contexts:
        slug = normalize_name(ctx.name)
        lines: list[str] = []
        lines.append(f"# {ctx.name}\n\n")
        lines.append("## Bounded Context\n\n")
        lines.append("```mermaid\n")
        lines.append("flowchart TB\n\n")

        # Main context mermaid section
        lines.append(f"{ctx.mermaid_section}\n")

        # Related context subgraphs (only entities used in cross-links)
        related = model.related_contexts(ctx.name)
        for related_name in sorted(related):
            related_ctx = next(
                (c for c in model.contexts if c.name == related_name), None
            )
            if not related_ctx:
                continue
            entity_ids = sorted(related[related_name])
            lines.append(f'\n\tsubgraph "{related_name}"\n')
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

        # Capabilities by software system
        ctx_caps = cap_map.get(ctx.name, {})
        if ctx_caps:
            lines.append("## Capabilities\n\n")
            for system_name in sorted(ctx_caps):
                ss_slug = normalize_name(system_name)
                lines.append(f"### [{system_name}](../software-systems/{ss_slug}/index.md)\n\n")
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
                ss_slug = normalize_name(ss.name)
                lines.append(
                    f"- [{ss.name}](../software-systems/{ss_slug}/index.md)\n"
                )
            lines.append("\n")

        (bc_dir / f"{slug}.md").write_text("".join(lines), encoding="utf-8")
