"""Auto-generate Structurizr DSL view definitions from workspace source files.

Parses users.dsl, groups/*.dsl, and deployments/*.dsl to produce a single
_auto_generated_views.dsl file containing system landscape, system context,
container, and deployment views.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import click

# ---------------------------------------------------------------------------
# Shared regex patterns
# ---------------------------------------------------------------------------

_PERSON_RE = re.compile(r'(\w+)\s*=\s*person\s+"([^"]+)"')
_GROUP_RE = re.compile(r'(\w+)\s*=\s*group\s+"([^"]+)"')
_GROUP_OPT_VAR_RE = re.compile(r'(?:(\w+)\s*=\s*)?group\s+"([^"]+)"')
_SYSTEM_RE = re.compile(r'(\w+)\s*=\s*softwareSystem\s+"([^"]+)"')
_SYSTEM_CI_RE = re.compile(r'(\w+)\s*=\s*softwareSystem\s+"([^"]+)"', re.IGNORECASE)
_CONTAINER_KW_RE = re.compile(r'\bcontainer\s+"')
_CONTAINER_KW_ML_RE = re.compile(r"(?:^|\s)container\s+\"", re.MULTILINE)
_USER_TO_THIS_RE = re.compile(r"(user\w+)\s*->\s*this")
_THIS_TO_USER_RE = re.compile(r"this\s*->\s*(user\w+)")
_ENV_RE = re.compile(r'(\w+)\s*=\s*deploymentEnvironment\s+"([^"]+)"')
_ENV_OPT_VAR_RE = re.compile(r'(?:(\w+)\s*=\s*)?deploymentEnvironment\s+"([^"]+)"')
_ZONE_RE = re.compile(r'(\w+)\s*=\s*deploymentNode\s+"([^"]+)"')
_CONTAINER_INSTANCE_RE = re.compile(r"containerInstance\s+(container\w+)")
_SYSTEM_INSTANCE_RE = re.compile(r"softwareSystemInstance\s+(\w+)", re.IGNORECASE)
_RELATIONSHIP_RE = re.compile(r"(\w+)\s*->\s*(\w+)")

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

OUTPUT_FILENAME = "_auto_generated_views.dsl"


@dataclass
class DslUser:
    var_name: str
    display_name: str


@dataclass
class DslSoftwareSystem:
    var_name: str
    display_name: str
    group_name: str
    has_containers: bool
    user_var_names: list[str] = field(default_factory=list)


@dataclass
class DslGroup:
    var_name: str
    display_name: str
    systems: list[DslSoftwareSystem] = field(default_factory=list)


@dataclass
class DslDeploymentZone:
    var_name: str
    display_name: str


@dataclass
class DslDeploymentEnvironment:
    var_name: str
    display_name: str
    has_var_name: bool = True
    zones: list[DslDeploymentZone] = field(default_factory=list)
    system_var_names: list[str] = field(default_factory=list)
    container_vars: set[str] = field(default_factory=set)


# ---------------------------------------------------------------------------
# DSL parsing helpers
# ---------------------------------------------------------------------------

def _find_matching_brace(text: str, open_pos: int) -> int | None:
    """Return the index *after* the closing '}' that matches the '{' at *open_pos*.

    Returns None if braces are unbalanced.
    """
    depth = 1
    i = open_pos + 1
    while i < len(text) and depth > 0:
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1
    return i if depth == 0 else None


def _extract_top_level_blocks(text: str) -> list[tuple[str, str, str]]:
    """Extract top-level brace-delimited blocks from DSL text.

    Returns list of (pre_brace_line, block_body, full_match) tuples.
    pre_brace_line is everything on the line before the opening brace.
    """
    blocks: list[tuple[str, str, str]] = []
    i = 0
    while i < len(text):
        brace_pos = text.find("{", i)
        if brace_pos == -1:
            break

        line_start = text.rfind("\n", 0, brace_pos)
        line_start = line_start + 1 if line_start != -1 else 0
        pre_brace = text[line_start:brace_pos].strip()

        end = _find_matching_brace(text, brace_pos)
        if end is None:
            break

        body = text[brace_pos + 1 : end - 1]
        full = text[line_start:end]
        blocks.append((pre_brace, body, full))
        i = end

    return blocks


def _extract_brace_body(text: str, search_start: int) -> str | None:
    """Find the first '{' from search_start and return content up to matching '}'."""
    brace_pos = text.find("{", search_start)
    if brace_pos == -1:
        return None
    end = _find_matching_brace(text, brace_pos)
    if end is None:
        return None
    return text[brace_pos + 1 : end - 1]


def _display_to_var(display_name: str, prefix: str) -> str:
    """Convert display name to camelCase var: 'Big Bank plc' + 'group' → 'groupBigBankPlc'."""
    words = re.split(r"[^a-zA-Z0-9]+", display_name)
    words = [w for w in words if w]
    return prefix + "".join(w.capitalize() for w in words)


def _find_includes_dir(workspace_dir: Path, workspace_file: str = "workspace.dsl") -> Path | None:
    """Detect the includes directory by checking common conventions.

    Looks for ``workspace-includes/`` first, then parses ``!include`` paths
    from the workspace DSL to find the actual directory.
    """
    candidates = [workspace_dir / "workspace-includes"]

    dsl_path = workspace_dir / workspace_file
    if dsl_path.exists():
        text = dsl_path.read_text(encoding="utf-8")
        for m in re.finditer(r"!include\s+(\S+)", text):
            parent = Path(m.group(1)).parts[0]
            candidate = workspace_dir / parent
            if candidate not in candidates:
                candidates.append(candidate)

    for d in candidates:
        if d.is_dir():
            return d
    return None


def _parse_users(workspace_dir: Path, includes_dir: Path | None = None) -> list[DslUser]:
    """Parse person definitions from users.dsl in the includes directory."""
    if includes_dir is None:
        includes_dir = _find_includes_dir(workspace_dir)
    if includes_dir is None:
        return []
    users_path = includes_dir / "users.dsl"
    if not users_path.exists():
        return []

    text = users_path.read_text(encoding="utf-8")
    return [DslUser(var_name=m.group(1), display_name=m.group(2)) for m in _PERSON_RE.finditer(text)]


def _parse_groups(workspace_dir: Path, includes_dir: Path | None = None) -> list[DslGroup]:
    """Parse group, software system, container, and user interaction data."""
    if includes_dir is None:
        includes_dir = _find_includes_dir(workspace_dir)
    if includes_dir is None:
        return []
    groups_dir = includes_dir / "groups"
    if not groups_dir.exists():
        return []

    groups: list[DslGroup] = []

    for dsl_file in sorted(groups_dir.glob("*.dsl")):
        text = dsl_file.read_text(encoding="utf-8")
        blocks = _extract_top_level_blocks(text)

        for pre_brace, body, _ in blocks:
            gm = _GROUP_RE.search(pre_brace)
            if not gm:
                continue

            group = DslGroup(var_name=gm.group(1), display_name=gm.group(2))

            # Parse software systems within group body
            system_blocks = _extract_top_level_blocks(body)
            for sys_pre, sys_body, _ in system_blocks:
                sm = _SYSTEM_RE.search(sys_pre)
                if not sm:
                    continue

                has_containers = bool(_CONTAINER_KW_RE.search(sys_body))

                # Collect user interactions from entire system body
                user_vars: set[str] = set()
                for m in _USER_TO_THIS_RE.finditer(sys_body):
                    user_vars.add(m.group(1))
                for m in _THIS_TO_USER_RE.finditer(sys_body):
                    user_vars.add(m.group(1))

                system = DslSoftwareSystem(
                    var_name=sm.group(1),
                    display_name=sm.group(2),
                    group_name=group.display_name,
                    has_containers=has_containers,
                    user_var_names=sorted(user_vars),
                )
                group.systems.append(system)

            groups.append(group)

    return groups


def _parse_deployments(workspace_dir: Path, includes_dir: Path | None = None) -> list[DslDeploymentEnvironment]:
    """Parse deployment environments, named zone nodes, and container instances."""
    if includes_dir is None:
        includes_dir = _find_includes_dir(workspace_dir)
    if includes_dir is None:
        return []
    deploy_dir = includes_dir / "deployments"
    if not deploy_dir.exists():
        return []

    envs: list[DslDeploymentEnvironment] = []

    for dsl_file in sorted(deploy_dir.glob("*.dsl")):
        text = dsl_file.read_text(encoding="utf-8")
        blocks = _extract_top_level_blocks(text)

        for pre_brace, body, _ in blocks:
            em = _ENV_RE.search(pre_brace)
            if not em:
                continue

            env = DslDeploymentEnvironment(var_name=em.group(1), display_name=em.group(2))

            # Find named zone deployment nodes (direct children with variable assignment)
            zone_blocks = _extract_top_level_blocks(body)
            for zone_pre, zone_body, _ in zone_blocks:
                zm = _ZONE_RE.search(zone_pre)
                if zm:
                    env.zones.append(DslDeploymentZone(var_name=zm.group(1), display_name=zm.group(2)))

            # Collect all container instances to determine which systems are deployed
            env.container_vars = set(_CONTAINER_INSTANCE_RE.findall(body))
            envs.append(env)

    return envs


def _resolve_deployed_systems(
    envs: list[DslDeploymentEnvironment],
    groups: list[DslGroup],
) -> None:
    """Map container instances back to their owning software systems.

    Uses a naming convention heuristic: container var names are expected to
    mirror their parent system var name with a ``container`` prefix instead of
    ``softwareSystem`` (e.g. ``softwareSystemFoo`` → ``containerFooApi``).
    Workspaces that don't follow this convention will need hand-written
    deployment views.
    """
    all_systems = [s for g in groups for s in g.systems]

    for env in envs:
        system_vars: set[str] = set()

        for cvar in env.container_vars:
            # Try to match container to system by prefix
            for sys in all_systems:
                # e.g., softwareSystemTicketingPlatform -> containerTicketingPlatform*
                sys_suffix = sys.var_name.replace("softwareSystem", "", 1)
                if cvar.replace("container", "", 1).startswith(sys_suffix):
                    system_vars.add(sys.var_name)
                    break

        # Merge with any system vars already set (e.g. from softwareSystemInstance)
        existing = set(env.system_var_names) if env.system_var_names else set()
        env.system_var_names = sorted(system_vars | existing)
        env.container_vars = set()


# ---------------------------------------------------------------------------
# View generation
# ---------------------------------------------------------------------------

def _short_name(var_name: str, prefix: str) -> str:
    """Strip a prefix from a var name: softwareSystemFoo -> Foo.

    When the prefix isn't present (e.g. monolithic DSL uses short var names
    like 'backend'), capitalizes the first letter for consistent key casing.
    """
    if var_name.startswith(prefix):
        return var_name[len(prefix):]
    return var_name[0].upper() + var_name[1:] if var_name else var_name


def _camel_to_spaced(name: str) -> str:
    """Convert CamelCase to spaced words: 'TicketingPlatform' -> 'Ticketing Platform'."""
    return re.sub(r"(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", " ", name)


def _view_block(view_type: str, element_var: str | None, key: str, include: str, description: str = "") -> str:
    """Format a single DSL view block."""
    desc_line = f'    description "{description}"\n' if description else ""
    if element_var:
        return (
            f'{view_type} {element_var} "{key}" {{\n'
            f"{desc_line}"
            f"    include {include}\n"
            f"    autoLayout\n"
            f"}}"
        )
    return (
        f'{view_type} "{key}" {{\n'
        f"{desc_line}"
        f"    include {include}\n"
        f"    autoLayout\n"
        f"}}"
    )


def _deployment_view_block(system_var: str | None, env_ref: str, key: str, include: str, description: str = "") -> str:
    """Format a deployment view block.

    env_ref is either a variable name (bare) or a quoted display name.
    """
    desc_line = f'    description "{description}"\n' if description else ""
    scope = system_var if system_var else "*"
    return (
        f'deployment {scope} {env_ref} "{key}" {{\n'
        f"{desc_line}"
        f"    include {include}\n"
        f"    autoLayout\n"
        f"}}"
    )


def _generate_landscape_views(
    users: list[DslUser],
    groups: list[DslGroup],
) -> tuple[str, list[str]]:
    """Generate system landscape view section. Returns (section_text, view_keys)."""
    lines: list[str] = []
    keys: list[str] = []

    all_systems = [s for g in groups for s in g.systems]
    all_system_vars = [s.var_name for s in all_systems]
    all_user_vars = [u.var_name for u in users]

    # 1. Full landscape
    lines.append("# [auto-generated] Full system landscape")
    lines.append(_view_block("systemlandscape", None, "SystemLandscape", "*", "System Landscape"))
    keys.append("SystemLandscape")
    lines.append("")

    # 2. Software systems only (no users)
    if all_system_vars:
        lines.append("# [auto-generated] All software systems (no users)")
        key = "SystemLandscapeSoftwareSystems"
        title = "System Landscape - Software Systems"
        lines.append(_view_block("systemlandscape", None, key, " ".join(all_system_vars), title))
        keys.append(key)
        lines.append("")

    # 3. Per-group landscapes
    for group in groups:
        sys_vars = [s.var_name for s in group.systems]
        # Collect users that interact with any system in this group
        group_user_vars: set[str] = set()
        for s in group.systems:
            group_user_vars.update(s.user_var_names)

        include_items = sys_vars + sorted(group_user_vars)
        if include_items:
            key = f"SystemLandscape{group.display_name.replace(' ', '')}"
            lines.append(f"# [auto-generated] {group.display_name} group landscape")
            title = f"System Landscape - {group.display_name}"
            lines.append(_view_block("systemlandscape", None, key, " ".join(include_items), title))
            keys.append(key)
            lines.append("")

    # 4. Per-user landscapes
    # Build reverse map: user -> systems
    user_to_systems: dict[str, set[str]] = {u.var_name: set() for u in users}
    for s in all_systems:
        for uvar in s.user_var_names:
            if uvar in user_to_systems:
                user_to_systems[uvar].add(s.var_name)

    for user in users:
        sys_vars = sorted(user_to_systems.get(user.var_name, set()))
        if sys_vars:
            short = user.display_name.replace(" ", "")
            key = f"SystemLandscapeUser{short}"
            lines.append(f"# [auto-generated] {user.display_name} landscape")
            includes = f"{user.var_name} {' '.join(sys_vars)}"
            title = f"System Landscape - {user.display_name}"
            lines.append(_view_block("systemlandscape", None, key, includes, title))
            keys.append(key)
            lines.append("")

    # 5. All users (no systems)
    if all_user_vars:
        lines.append("# [auto-generated] All users (no systems)")
        key = "SystemLandscapeUsers"
        lines.append(_view_block("systemlandscape", None, key, " ".join(all_user_vars), "System Landscape - Users"))
        keys.append(key)
        lines.append("")

    return "\n".join(lines), keys


def _generate_system_context_views(groups: list[DslGroup]) -> tuple[str, list[str]]:
    """Generate system context views. Returns (section_text, view_keys)."""
    lines: list[str] = []
    keys: list[str] = []

    for group in groups:
        lines.append(f"# {group.display_name}")
        for sys in group.systems:
            short = _short_name(sys.var_name, "softwareSystem")
            key = f"SystemContext{short}"
            lines.append("# [auto-generated]")
            lines.append(_view_block("systemContext", sys.var_name, key, "*", f"System Context - {sys.display_name}"))
            keys.append(key)
            lines.append("")

    return "\n".join(lines), keys


def _generate_container_views(groups: list[DslGroup]) -> tuple[str, list[str]]:
    """Generate container views for systems with containers."""
    lines: list[str] = []
    keys: list[str] = []

    for group in groups:
        group_has_containers = any(s.has_containers for s in group.systems)
        if not group_has_containers:
            continue

        lines.append(f"# {group.display_name}")
        for sys in group.systems:
            if not sys.has_containers:
                continue
            short = _short_name(sys.var_name, "softwareSystem")
            key = f"Container{short}"
            lines.append("# [auto-generated]")
            lines.append(_view_block("container", sys.var_name, key, "*", f"Container - {sys.display_name}"))
            keys.append(key)
            lines.append("")

    return "\n".join(lines), keys


def _generate_deployment_views(
    envs: list[DslDeploymentEnvironment],
    groups: list[DslGroup] | None = None,
) -> tuple[str, list[str]]:
    """Generate deployment views per environment/zone and per system."""
    lines: list[str] = []
    keys: list[str] = []

    # Build var -> display name lookup
    sys_display_map: dict[str, str] = {}
    if groups:
        for g in groups:
            for s in g.systems:
                sys_display_map[s.var_name] = s.display_name

    for env in envs:
        env_short = _short_name(env.var_name, "deployment").capitalize()
        if env_short == env.var_name:
            env_short = env.display_name.replace(" ", "")

        # Use quoted display name when no DSL variable was assigned
        env_ref = env.var_name if env.has_var_name else f'"{env.display_name}"'

        # Per-zone views
        for zone in env.zones:
            zone_short = _short_name(zone.var_name, f"deploymentNode{env_short}")
            if not zone_short or zone_short == zone.var_name:
                zone_short = zone.display_name.replace(" ", "")
            key = f"Deployment{env_short}{zone_short}"
            lines.append(f"# [auto-generated] {env.display_name} — {zone.display_name}")
            title = f"Deployment - {env.display_name} - {zone.display_name}"
            lines.append(_deployment_view_block(None, env_ref, key, zone.var_name, title))
            keys.append(key)
            lines.append("")

        # Per-system views
        for sys_var in env.system_var_names:
            short = _short_name(sys_var, "softwareSystem")
            sys_display = sys_display_map.get(sys_var, _camel_to_spaced(short))
            key = f"Deployment{env_short}{short}"
            lines.append("# [auto-generated]")
            title = f"Deployment - {env.display_name} - {sys_display}"
            lines.append(_deployment_view_block(sys_var, env_ref, key, "*", title))
            keys.append(key)
            lines.append("")

    return "\n".join(lines), keys


# ---------------------------------------------------------------------------
# Monolithic DSL parsing (single-file workspace.dsl)
# ---------------------------------------------------------------------------


def _parse_monolithic_dsl(
    workspace_dir: Path,
    workspace_file: str = "workspace.dsl",
) -> tuple[list[DslUser], list[DslGroup], list[DslDeploymentEnvironment]]:
    """Parse users, groups, and systems from a single-file workspace DSL."""
    dsl_path = workspace_dir / workspace_file
    if not dsl_path.exists():
        return [], [], []

    text = dsl_path.read_text(encoding="utf-8")

    # Find model block
    model_match = re.search(r"\bmodel\s*\{", text)
    if not model_match:
        return [], [], []
    model_body = _extract_brace_body(text, model_match.start())
    if not model_body:
        return [], [], []

    # --- Users ---
    users = [DslUser(m.group(1), m.group(2)) for m in _PERSON_RE.finditer(model_body)]

    # --- Groups & Systems ---
    groups: list[DslGroup] = []
    for gm in _GROUP_OPT_VAR_RE.finditer(model_body):
        var_name = gm.group(1) or _display_to_var(gm.group(2), "group")
        display_name = gm.group(2)
        group_body = _extract_brace_body(model_body, gm.start())
        if not group_body:
            continue

        group = DslGroup(var_name=var_name, display_name=display_name)

        # Systems with brace blocks (have containers/components)
        sys_blocks = _extract_top_level_blocks(group_body)
        seen_vars: set[str] = set()
        for sys_pre, sys_body, _ in sys_blocks:
            sm = _SYSTEM_CI_RE.search(sys_pre)
            if not sm:
                continue
            has_containers = bool(_CONTAINER_KW_ML_RE.search(sys_body))
            system = DslSoftwareSystem(
                var_name=sm.group(1),
                display_name=sm.group(2),
                group_name=display_name,
                has_containers=has_containers,
            )
            group.systems.append(system)
            seen_vars.add(sm.group(1))

        # Systems without brace blocks (single-line definitions)
        for sm in _SYSTEM_CI_RE.finditer(group_body):
            if sm.group(1) not in seen_vars:
                group.systems.append(DslSoftwareSystem(
                    var_name=sm.group(1),
                    display_name=sm.group(2),
                    group_name=display_name,
                    has_containers=False,
                ))

        groups.append(group)

    # --- User ↔ System relationships ---
    user_vars = {u.var_name for u in users}
    sys_map: dict[str, DslSoftwareSystem] = {}
    for g in groups:
        for s in g.systems:
            sys_map[s.var_name] = s

    for rm in _RELATIONSHIP_RE.finditer(model_body):
        src, dst = rm.group(1), rm.group(2)
        if src in user_vars and dst in sys_map:
            if src not in sys_map[dst].user_var_names:
                sys_map[dst].user_var_names.append(src)
        elif dst in user_vars and src in sys_map:
            if dst not in sys_map[src].user_var_names:
                sys_map[src].user_var_names.append(dst)

    # --- Deployment Environments ---
    # Monolithic DSL uses a more general container instance pattern (any \w+, not just container*)
    mono_container_instance_re = re.compile(r"containerInstance\s+(\w+)")

    envs: list[DslDeploymentEnvironment] = []
    for em in _ENV_OPT_VAR_RE.finditer(model_body):
        has_var = em.group(1) is not None
        var_name = em.group(1) or _display_to_var(em.group(2), "env")
        env_body = _extract_brace_body(model_body, em.start())
        if not env_body:
            continue

        env = DslDeploymentEnvironment(var_name=var_name, display_name=em.group(2), has_var_name=has_var)

        # Collect container instances for system resolution
        env.container_vars = set(mono_container_instance_re.findall(env_body))

        # Collect direct software system instances
        env.system_var_names = sorted(set(_SYSTEM_INSTANCE_RE.findall(env_body)))
        envs.append(env)

    _resolve_deployed_systems(envs, groups)

    return users, groups, envs


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def _find_existing_view_keys(views_dir: Path, workspace_dsl: Path | None = None) -> set[str]:
    """Scan existing .dsl files for view keys (excluding auto-generated file).

    Also scans the views block in *workspace_dsl* when provided, so that
    hand-written views in a monolithic workspace.dsl are detected.
    """
    keys: set[str] = set()
    key_pattern = re.compile(r'"(\w+)"\s*\{')

    for dsl_file in views_dir.rglob("*.dsl"):
        if dsl_file.name == OUTPUT_FILENAME:
            continue
        text = dsl_file.read_text(encoding="utf-8")
        for m in key_pattern.finditer(text):
            keys.add(m.group(1))

    # Scan views block in monolithic workspace.dsl
    if workspace_dsl and workspace_dsl.exists():
        text = workspace_dsl.read_text(encoding="utf-8")
        views_match = re.search(r"\bviews\s*\{", text)
        if views_match:
            views_body = _extract_brace_body(text, views_match.start())
            if views_body:
                for m in key_pattern.finditer(views_body):
                    keys.add(m.group(1))

    return keys


def _filter_views(section_text: str, view_keys: list[str], existing_keys: set[str]) -> str:
    """Remove view blocks whose keys conflict with existing hand-written views."""
    if not existing_keys:
        return section_text

    conflicts = set(view_keys) & existing_keys
    if not conflicts:
        return section_text

    # Remove conflicting view blocks, tracking brace depth so nested braces
    # (e.g. properties inside a view) don't cause premature termination.
    result_lines: list[str] = []
    skip_depth = 0

    for line in section_text.split("\n"):
        if skip_depth == 0:
            for key in conflicts:
                if f'"{key}"' in line and "{" in line:
                    # Start skipping; count braces on this line to set initial depth
                    skip_depth = line.count("{") - line.count("}")
                    if skip_depth < 1:
                        skip_depth = 1
                    if result_lines and result_lines[-1].startswith("# [auto-generated]"):
                        result_lines.pop()
                    break
            if skip_depth > 0:
                continue

        if skip_depth > 0:
            skip_depth += line.count("{") - line.count("}")
            if skip_depth <= 0:
                skip_depth = 0
            continue

        result_lines.append(line)

    for key in conflicts:
        click.echo(f"  Warning: skipping auto-generated view '{key}' — already defined in hand-written DSL", err=True)

    return "\n".join(result_lines)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_views(workspace_dir: Path, workspace_file: str = "workspace.dsl") -> Path | None:
    """Parse DSL sources and generate _auto_generated_views.dsl.

    Returns the path to the generated file, or None if nothing was generated.
    Tries workspace-includes/ structure first, falls back to monolithic DSL.
    """
    includes_dir = _find_includes_dir(workspace_dir, workspace_file)
    users = _parse_users(workspace_dir, includes_dir)
    groups = _parse_groups(workspace_dir, includes_dir)
    envs = _parse_deployments(workspace_dir, includes_dir)
    _resolve_deployed_systems(envs, groups)

    # Fallback: parse from monolithic workspace.dsl
    if not users and not groups and not envs:
        users, groups, envs = _parse_monolithic_dsl(workspace_dir, workspace_file)

    if not users and not groups and not envs:
        click.echo("  No DSL sources found — skipping view generation.", err=True)
        return None

    views_dir = (includes_dir or workspace_dir / "workspace-includes") / "views"

    workspace_dsl = workspace_dir / workspace_file
    existing_keys = _find_existing_view_keys(views_dir, workspace_dsl)

    # Build sections
    sections: list[str] = []

    header = (
        "# ============================================================\n"
        "# AUTO-GENERATED VIEWS — DO NOT EDIT\n"
        "# Generated by structurizr-mkdocs-generatr\n"
        "# Re-run the CLI to regenerate. Hand-written views in other\n"
        "# files take priority (matching keys are skipped).\n"
        "# ============================================================"
    )
    sections.append(header)

    # System Landscape
    landscape_text, landscape_keys = _generate_landscape_views(users, groups)
    if landscape_text.strip():
        landscape_text = _filter_views(landscape_text, landscape_keys, existing_keys)
        sections.append("# --- System Landscape Views ---\n")
        sections.append(landscape_text)

    # System Context
    context_text, context_keys = _generate_system_context_views(groups)
    if context_text.strip():
        context_text = _filter_views(context_text, context_keys, existing_keys)
        sections.append("# --- System Context Views ---\n")
        sections.append(context_text)

    # Container
    container_text, container_keys = _generate_container_views(groups)
    if container_text.strip():
        container_text = _filter_views(container_text, container_keys, existing_keys)
        sections.append("# --- Container Views ---\n")
        sections.append(container_text)

    # Deployment
    deploy_text, deploy_keys = _generate_deployment_views(envs, groups)
    if deploy_text.strip():
        deploy_text = _filter_views(deploy_text, deploy_keys, existing_keys)
        sections.append("# --- Deployment Views ---\n")
        sections.append(deploy_text)

    output_path = workspace_dir / OUTPUT_FILENAME
    output_path.write_text("\n\n".join(sections) + "\n", encoding="utf-8")

    return output_path
