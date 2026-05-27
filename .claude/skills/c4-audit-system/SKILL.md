---
name: c4-audit-system
description: Audit a software system by comparing its repository code against documented entities in 0000-introduction.md. Use when user wants to verify if architecture docs match what the code actually manages/consumes.
allowed-tools: Read, Grep, Glob, Edit, Write, Bash(git:*), Bash(ls:*), Agent, mcp__ado__repo_list_directory, mcp__ado__repo_get_repo_by_name_or_id, mcp__ado__repo_list_repos_by_project, mcp__ado__search_code
---

# Audit Software System Entities

You are a specialized skill for auditing software system documentation against actual source code. You compare what a software system's `0000-introduction.md` documents (managed/consumed entities) against what the code repository actually implements, then report differences.

**This skill is project-agnostic.** It discovers paths, properties, and artifacts at runtime from the current repo's DSL structure.

## Step 0: Discover Repo Structure

<!-- STEP-0-SYNC: keep this block in sync across all c4-* skills. -->

Try these workspace-root candidates in order, first match wins:

1. `src/master/workspace.dsl` → workspace root is `src/master/`
2. `src/workspace.dsl` → workspace root is `src/`
3. `./workspace.dsl` → workspace root is `./`
4. `example/workspace.dsl` → workspace root is `example/`

If none match, STOP and ask the user for the workspace root path.

Then detect the includes-directory layout (`workspace-includes/` or `workspace/`) — whichever exists under the workspace root.

1. **Bounded context file:** Check if `boundedContext.mmd` exists in the workspace root — only use it if present.
2. **Canonical reference:** Check for `CLAUDE.md` at repo root (and `main.md` if it exists) — read whichever is present for entity naming conventions.

## Step 1: Identify the Software System

When the user provides a software system name (or you infer it from context):

1. **Find the software system definition** in the DSL files under `<workspace-root>/<includes-dir>/groups/`:
   - Search for the software system by name using Grep
   - Note the `!docs` path to find its documentation folder
   - Note any `"Repository"` property on its containers — these are the code repos to audit
   - **Capture each container's display name and variable name** — you will use these for the naming-compliance check below

2. **Naming-compliance check (drift detection)** — for each container in this system, verify:
   - The container's display name begins with the parent software system's display name followed by a space (e.g., system `"Primo"` must have containers named `"Primo Alma"`, `"Primo Discovery"`, NOT bare `"Alma"` / `"Primo"`).
   - The variable name equals the display name with spaces removed and the first letter after `container` lowercased (e.g., `"Primo Discovery"` → `containerPrimoDiscovery`).

   Record any violations as **Naming Drift** findings and include them in the Step 3 report. Do not auto-fix here — suggest the rename to the user in Step 4 instead, since renames require coordinated updates across views, deployments, and cross-system relationships.

3. **Read the `0000-introduction.md`** file from the docs folder and extract:
   - **Context**: Which bounded contexts are listed
   - **Manage**: Which entities the system claims to manage (with links if present)
   - **Consume**: Which entities the system claims to consume (with links if present)

4. **List all repositories** found via `"Repository"` properties on containers belonging to this software system.

If no `"Repository"` property is found on any container, STOP and inform the user that no repository URLs are configured for this software system's containers. Suggest they add `"Repository"` properties first.

If multiple containers have repositories, audit each one.

## Step 2: Analyze the Code Repository

For each repository found:

### 2a: Access the Repository

Try these access paths in order, use the first that works:

1. **Local clone (preferred — fastest, no network):**
   - Extract the repo name from the URL:
     - Azure DevOps: the segment after `/_git/` (e.g., `https://dev.azure.com/Org/Project/_git/my-repo` → `my-repo`)
     - GitHub / GitLab / generic: the last path segment (e.g., `https://github.com/org/my-repo` → `my-repo`)
     - Strip any trailing `.git` suffix (e.g., `my-repo.git` → `my-repo`)
   - Search common local paths: `~/Code/<repo-name>`, `~/source/<repo-name>`, `~/repos/<repo-name>`
   - Run `ls` to verify the directory exists
   - If found, use an **Agent (Explore)** subagent to analyze the codebase

2. **Git-host MCP (if available):**
   - If the URL is an Azure DevOps repo and `mcp__ado__*` tools are available, use them:
     - `mcp__ado__repo_list_directory` for structure
     - `mcp__ado__search_code` for controllers, endpoints, entities
   - If the URL is a GitHub repo and a GitHub MCP is available, use its equivalent tools.
   - If neither MCP is available for the repo's host, fall through to step 3.

3. **Ask the user to clone locally** and re-run the skill.

### 2b: Identify entities

- Database models / entity definitions (EF Core DbContext, migrations, model classes)
- API controllers / endpoints (what CRUD operations exist)
- External service references (HTTP clients, shared domain libraries, service references)
- OpenAPI / Swagger specifications if available
- Schema files, migration files

### 2c: Classify each code entity

- **Manages**: Full CRUD operations — the entity is owned by this service
- **Consumes**: Only reads from an external source (API calls, shared libraries, read-only DB contexts)
- **Infrastructure**: Audit trails, caching, logging — typically not documented as business entities

### 2d: Map code entities to bounded context entity names

- Code entity names often differ from bounded context names
- If `boundedContext.mmd` exists, use it to find canonical entity names and their URLs
- Search existing `0000-introduction.md` files across the project for entity links that might match

## Step 3: Compare and Report

Present a clear comparison:

```
## Audit Report: [Software System Name]

### Repository: [repo URL]
**Stack**: [detected technology stack]

### Entities in Code vs Documentation

| Code Entity | Bounded Context Name | Link | In Docs? | Relationship |
|---|---|---|---|---|
| [CodeName] | [BC Name] | [URL or "needs page"] | yes / no | Manages / Consumes |

### Documented but NOT in Code
- [Entity Name] — listed as [Manage/Consume]

### In Code but NOT Documented
- [Entity Name] — code shows [Manages/Consumes]

### Relationship Mismatches
- [Entity Name] — documented as [Consume] but code shows [Manages]

### Bounded Context Gaps (only if boundedContext.mmd exists)
- [Entity Name] — no entry in bounded context file

### Naming Drift (container display names / variables)
- [Container Variable] — display name `"[current]"` does not start with system name `"[System]"`; suggested rename: `"[System] [current]"` (variable → `container[System][Current]`)

### Summary
- Documented entities: [count]
- Code entities: [count]
- Matches: [count]
- Missing from docs: [count]
- Missing from code: [count]
- Relationship mismatches: [count]
```

## Step 4: Offer to Fix

After presenting the report, ask the user:

```
Would you like me to:
1. Update 0000-introduction.md to match the code
2. Update boundedContext.mmd to add missing entities (only if file exists)
3. Both
4. Just take note (no changes)
```

### When updating 0000-introduction.md:

- **Remove** entities listed in docs that don't exist in code
- **Add** entities found in code that are missing from docs
- **Fix** relationship types (Manage vs Consume) to match code behavior
- **Preserve** existing links where entities remain valid
- **Use empty links** `[Entity Name]()` for entities without pages yet

### When updating boundedContext.mmd (only if it exists):

- **Add new entities** to the appropriate subgraph
- **Add relationships** matching the code's data model
- **Add click handlers** using URLs if available
- Follow existing naming conventions in the file

## Important Notes

- **Legacy/migration staging tables are NOT important** — ignore tables that exist purely for data migration
- **Audit trail entities** are infrastructure, not business entities — do not document them
- **Always map code entity names to their bounded context equivalents** — never use raw code class names in the docs
- **A FK reference alone does not make an entity "Consumed"** — Consume means the service actively reads/fetches data from another service
- **Do NOT make changes without user confirmation**
- **Present the report first**, then offer to fix
