---
name: c4-add-container
description: Add a container (API, service, database, UI, ETL, function) with its relationships and Repository URL to a software system that already exists in a Structurizr DSL workspace. Use when the user asks to add or model a container in an existing system. If the system does not exist yet, use c4-add-system first.
allowed-tools: Read, Grep, Glob, Edit, Write
---

# Add Container to Existing Software System

Add a new container to a software system that already exists in the Structurizr DSL.

**This skill is project-agnostic.** It discovers groups, existing systems, and container conventions at runtime from the current repo's DSL structure.

The user describes the new container in natural language. Extract the fields, confirm them, then write.

Use `c4-add-system` (not this skill) when the parent software system does not yet exist.

## Step 0: Discover Repo Structure

<!-- STEP-0-SYNC: keep this block in sync across all c4-* skills. -->

Try these workspace-root candidates in order, first match wins:

1. `src/master/workspace.dsl` → workspace root is `src/master/`
2. `src/workspace.dsl` → workspace root is `src/`
3. `./workspace.dsl` → workspace root is `./`
4. `example/workspace.dsl` → workspace root is `example/`

If none match, stop and ask the user for the workspace root path.

Then detect the includes-directory layout (`workspace-includes/` or `workspace/`) — whichever exists under the workspace root.

1. **Available groups:** List directories/files under `<workspace-root>/<includes-dir>/groups/`.
2. **Canonical reference:** Check for `CLAUDE.md` at repo root (and `main.md` if it exists) — read whichever is present for container naming/tagging conventions.

## Step 1: Parse the User's Request

From the user's description, extract:

- **Target software system** (required) — the name of the existing system to add the container to
- **Container name** (required) — the human-readable display name. It **MUST begin with the parent software system's display name**, followed by a space and the component role. The variable is derived from this name. Examples: system `"Ticketing Platform"` → `"Ticketing Platform API"`, `"Ticketing Platform Database"`; system `"Salesforce CRM"` → `"Salesforce CRM Lightning"`, `"Salesforce CRM REST API"`. A bare role name (e.g. `"API"`, `"Lightning"`, `"Salesforce"`) is NOT valid — stop and ask the user to prefix it with the system name.
- **Description** (required) — one line on what the container does
- **Technology** (required) — e.g., `".NET (Core)"`, `"Node.Js"`, `"PostgreSQL"`, `"React"`, `"Azure Function"`
- **Container type tag** (required) — e.g., `"SERVICE"`, `"DATASET"`, `"APPLICATION"`, `"UI"`, `"ETL"`. Valid tags per the canonical reference.
- **Repository URL** (optional, encouraged) — the Git URL; enables downstream skills (`c4-document-system`, `c4-audit-system`, `c4-review`) to pull code
- **Inbound relationships** (optional) — other containers/systems/users that call THIS container
- **Outbound relationships** (optional) — other containers/systems this container calls

For each relationship, capture: direction (inbound/outbound), other side's variable name, purpose, protocol (default `"JSON/HTTPS"` if unclear).

If any required field is missing or ambiguous, stop and ask.

## Step 2: Locate and Validate the Target System

1. **Find the parent software system** by grepping `<workspace-root>/<includes-dir>/groups/` for its variable name. If zero or multiple matches, stop and ask the user to disambiguate.

2. **Read the matching group DSL file** and locate the exact `softwareSystem<Name> = ... { ... }` block that owns the target system.

3. **Note the indentation style** used inside that block — match it for the new container.

4. **Check for name collisions** — grep the group file to verify no existing `container<Name>` variable already has the same name inside this system.

5. **Validate display-name prefix** — confirm the container's display name starts with the parent system's display name (case-sensitive, followed by a space). If not, stop and ask the user to restate the name with the system prefix (e.g. `"Lightning"` → `"Salesforce CRM Lightning"`). The prefix keeps container diagrams legible when several systems have containers with similar role names. If peers in the same system predate the rule and lack the prefix, still apply it to the new container and mention the older names in the summary.

6. **Validate each referenced relationship target** — for every other-side variable the user mentioned, grep the workspace to confirm it exists (either as a `softwareSystem<X>` or `container<X>` variable). If ANY target can't be found, stop and report the unresolved list.

## Step 3: Present Summary and Ask for Confirmation

Do not edit anything until the user confirms. A wrong variable name or relationship target is cheap to fix here and expensive once views and deployments reference it.

Present a clear summary:

```
## New Container Summary

### Target
- Software system: <Name> (in <group-file-path>)

### Container
- Variable: container<DerivedName>
- Display name: "<Container Name>"
- Description: "<Description>"
- Technology: "<Technology>"
- Tag: "<TAG>"
- Repository: <URL or "(not provided — consider adding later for downstream skills)">

### Relationships
<inbound and outbound with validation status>

### Issues/Warnings
<any name collisions, tag questions, missing peers>

### What will be created
- Edit: <group-file-path> — inserting container block and relationships inside softwareSystem<Name>
- (No docs folder, no view changes in this skill)
```

**WAIT for user confirmation before proceeding!**

## Step 4: Insert the Container (Only After Confirmation)

### 4.1: Derive the variable name

`container<ContainerNameInCamelCase>` — take the display name (which, per Step 1, already starts with the system's display name), remove spaces, lowercase the first letter after `container`, strip punctuation. Examples: `"Salesforce CRM Lightning"` → `containerSalesforceCrmLightning`; `"SAP S/4HANA API"` → `containerSapS4HanaApi`; `"Ticketing Platform API"` → `containerTicketingPlatformApi`.

### 4.2: Edit the group DSL file

Use `Edit` to insert the container block INSIDE the `softwareSystem<Name> { ... }` block, AFTER the `properties { }` section and after any other containers already defined there, but BEFORE the system's closing brace.

**First, check how peer containers in the same system model their outbound relationships** — Structurizr allows two styles and the skill must match whichever this codebase uses:

- **Style A (inside the container block, using `this`):** e.g. `this -> containerOther "Manage data" "SQL/TCP"`. This is the style used in the bundled `example/workspace/groups/*.dsl` files.
- **Style B (at the system level, using the container variable):** e.g. `containerFoo -> containerBar "..." "..."`, placed outside any container block but inside the system block.

Match the indentation of existing containers in the same system:

```dsl

        container<Name> = container "<Container Name>" "<Description>" "<Technology>" "<TAG>" {
            properties {
                "Repository" "<URL>"
            }

            # Style A: outbound relationships go here, using `this ->`
        }
```

Omit the `properties { }` block entirely if no Repository URL was provided.

### 4.3: Add Relationships

**Outbound relationships** (this container → another):

- If peers use **Style A**, add `this -> <other-side-variable> "<Purpose>" "<Protocol>"` INSIDE the new container's block.
- If peers use **Style B**, add `container<Name> -> <other-side-variable> "<Purpose>" "<Protocol>"` at the system level, AFTER all container declarations.

**Inbound relationships** (another container/system/user → this container) always live at the system level, because the `this` keyword refers only to the enclosing block:

```dsl
        <other-side-variable> -> container<Name> "<Purpose>" "<Protocol>"
```

Place inbound relationships AFTER all container declarations in the system block.

## Step 5: Summary and Next Steps

After the edit, tell the user:

1. What was changed (file + line numbers if possible).
2. Suggest running `c4-validate-changes` to check the change against standards and peers.
3. Suggest running `structurizr-mkdocs <workspace-root> --serve` to confirm the container renders in the site at `http://localhost:8000` (or the repo's own serve command if different).
4. If a Repository URL was provided, point out that `c4-document-system` can now generate a `0001-technical.md` for this system.

## Important Notes

- **ALWAYS ask for confirmation** before editing.
- **Do NOT create container views, deployment nodes, or docs folders** — those are out of scope for this skill.
- **Do NOT touch the parent system's `0000-introduction.md`** — container-level docs go in `0001-technical.md` via the `c4-document-system` skill.
- **Preserve indentation exactly** — match the style of existing containers in the same block.
- **Relationship protocol defaults to `"JSON/HTTPS"`** if the user doesn't specify — but ask if unclear (e.g., DB container should be `"SQL"`).
- **If the parent system does not exist**, stop and recommend `c4-add-system` instead.
