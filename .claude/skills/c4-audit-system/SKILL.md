---
name: c4-audit-system
description: Audit a software system for drift between its architecture docs and its code: compares the entities 0000-introduction.md says the system manages or consumes against what the linked repositories implement, and checks container naming. Use when the user asks to audit a system, check docs against code, or find documentation drift.
allowed-tools: Read, Grep, Glob, Edit, Write, Bash(git:*), Bash(ls:*), Agent, mcp__ado__repo_list_directory, mcp__ado__repo_get_repo_by_name_or_id, mcp__ado__repo_list_repos_by_project, mcp__ado__search_code
---

# Audit a system's docs against its code

Compare the entities a system's `0000-introduction.md` claims it manages and consumes with what its code actually does, report the differences, then offer fixes.

## Step 0: Find the workspace

<!-- STEP-0-SYNC: keep this block in sync across all c4-* skills. -->

The workspace root is the first of these that exists:

1. `src/master/workspace.dsl` → workspace root is `src/master/`
2. `src/workspace.dsl` → workspace root is `src/`
3. `./workspace.dsl` → workspace root is `./`
4. `example/workspace.dsl` → workspace root is `example/`

If none exists, ask the user. Under the root, the includes directory (`groups/`, `views/`, `deployments/`, `users.dsl`) is `workspace-includes/` or `workspace/`. The repo's conventions live in `CLAUDE.md` at its root, or `main.md` if present; read them, and where they differ from this skill, they win.

If `boundedContext.mmd` exists in the workspace root, it holds the canonical entity names and links.

## Step 1: Read the documented side

Find the system in `<includes-dir>/groups/`: its `!docs` folder, its containers, and their `"Repository"` properties. If no container has a repository, stop and tell the user to add one.

Check container naming while you're there: each display name should start with the system's name, and the variable should be `container` plus that name in PascalCase. Report violations as naming drift, but don't rename anything; renames ripple through views, deployments, and other systems' relationships.

From `0000-introduction.md`, take the bounded contexts and the entities listed under Manage and Consume.

## Step 2: Read the code

Find each repository's code in this order:

1. **A local clone.** The repo name is the segment after `/_git/` (Azure DevOps) or the last path segment (GitHub, GitLab), without `.git`. Look next to the architecture repo (`../<repo-name>`), then under `~/Code/`, `~/source/`, `~/repos/`. Note the commit you read (`git -C <path> log -1 --format='%h %cd'`).
2. **A Git-host MCP** for that host (`mcp__ado__*` for Azure DevOps, a GitHub MCP for GitHub), if one is connected.
3. **Ask the user** where the code is.

Analyze each repository in its own Explore subagent, all started in the same turn, so code doesn't flood the main context.

Look for the entities the code owns or reads: ORM models and migrations, controllers and routes, HTTP clients, shared domain libraries, OpenAPI specs. Classify each:

- **Manages:** the service owns it (creates, updates, deletes).
- **Consumes:** it actively reads the entity from another service. A foreign key alone is not consumption.
- **Infrastructure:** audit trails, caches, logs, migration staging tables. Leave these out of the docs.

Map code names to bounded-context names (via `boundedContext.mmd`, or entity links in other systems' introductions); the docs never use raw class names.

## Step 3: Report

Per repository (with the commit you read): a table of code entity, bounded-context name, link, whether it's documented, and Manages/Consumes; then the lists of documented-but-not-in-code, in-code-but-undocumented, relationship mismatches, bounded-context gaps (if the file exists), naming drift, and counts.

## Step 4: Offer fixes

Ask whether to update `0000-introduction.md`, `boundedContext.mmd` (if it exists), both, or neither. Change nothing until the user picks. When updating, keep existing links that are still valid and use empty links (`[Entity]()`) for entities without a page yet; in `boundedContext.mmd`, follow the file's existing subgraph, relationship, and click-link conventions.
