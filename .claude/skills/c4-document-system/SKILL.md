---
name: c4-document-system
description: Write or refresh a software system's 0001-technical.md (authentication, storage, background jobs, API reference) by analyzing the code repositories linked from its containers in the Structurizr DSL. Use when the user asks for a technical page, API documentation, or technical architecture for a system.
allowed-tools: Read, Grep, Glob, Edit, Write, Bash(ls:*), Bash(git:*), Agent, mcp__ado__repo_list_directory, mcp__ado__repo_get_repo_by_name_or_id, mcp__ado__repo_list_repos_by_project, mcp__ado__search_code
---

# Write a system's technical page

Generate `0001-technical.md` for a software system from its DSL definition and the code in its repositories. The code is the source of truth: document what it does, not what the DSL or anyone hopes it does.

## Step 0: Find the workspace

<!-- STEP-0-SYNC: keep this block in sync across all c4-* skills. -->

The workspace root is the first of these that exists:

1. `src/master/workspace.dsl` → workspace root is `src/master/`
2. `src/workspace.dsl` → workspace root is `src/`
3. `./workspace.dsl` → workspace root is `./`
4. `example/workspace.dsl` → workspace root is `example/`

If none exists, ask the user. Under the root, the includes directory (`groups/`, `views/`, `deployments/`, `users.dsl`) is `workspace-includes/` or `workspace/`. The repo's conventions live in `CLAUDE.md` at its root, or `main.md` if present; read them, and where they differ from this skill, they win.

Read an existing `0001-technical.md` first and match its density and tone: one elsewhere in this workspace, or the bundled reference at `example/software-system-docs/commercial/ticketingPlatform/0001-technical.md`.

## Step 1: Read the system

From the system's block in `<includes-dir>/groups/`: its `!docs` folder, and each container's name, technology, tag, `"Repository"` URL, and relationships. Read `0000-introduction.md` for business context. If `0001-technical.md` already exists, ask whether to rewrite or update it.

## Step 2: Read the code

Find each repository's code in this order:

1. **A local clone.** The repo name is the segment after `/_git/` (Azure DevOps) or the last path segment (GitHub, GitLab), without `.git`. Look next to the architecture repo (`../<repo-name>`), then under `~/Code/`, `~/source/`, `~/repos/`. Note the commit you read (`git -C <path> log -1 --format='%h %cd'`).
2. **A Git-host MCP** for that host (`mcp__ado__*` for Azure DevOps, a GitHub MCP for GitHub), if one is connected.
3. **Ask the user** where the code is.

Analyze each repository in its own Explore subagent, all started in the same turn, so code doesn't flood the main context.

Ask each subagent for: the runtime and key library versions, read from the manifest (`*.csproj`, `package.json`, `pyproject.toml`, `pom.xml`, `go.mod`), never inferred; authentication and authorization (provider, token type, how identity flows between layers, the authorization model, CORS, the classes and config sections involved); every endpoint with method, route, and purpose; tables with key columns and relationships; external integrations and their protocols; scheduled and background jobs; notable patterns. For a large codebase, endpoints, storage, and auth come first.

Containers without a repository (databases, storage) belong in the page when their schema or contents can be read from the code that uses them; skip plumbing like key vaults.

## Step 3: Confirm

Show the containers analyzed (with repository and commit), the main findings, and the proposed section outline, and wait for a yes.

## Step 4: Write

```markdown
<!-- Last updated: YYYY-MM-DD -->

# Technical Architecture

One or two sentences: stack, repository link, number of deployable components.

## Authentication & Authorization
## <non-API containers: UI, workers, database tables, events and jobs, complex flows>

# API Reference

## <API container name>
| Endpoint | Purpose |
| --- | --- |
| `GET /path` | ... |
```

The rules that matter:

- **Exactly two `#` headings**, `Technical Architecture` then `API Reference`. The generated site uses `toc_depth: 2`, so these become the page's two table-of-contents entries; merging them breaks that.
- **Authentication & Authorization is always the first section**, specific to what the code implements per container.
- **API Reference holds endpoint tables only**, grouped under `###` by controller or domain when there are many. Everything else, storage included, goes under Technical Architecture.
- **No Consumers section:** the site already generates a dependencies page from the DSL relationships.
- Don't put a framework version in prose unless you read it in the manifest ("ASP.NET Core" is fine; "ASP.NET Core 8" needs evidence).

## Step 5: Report

Say where the file is, suggest `structurizr-mkdocs <workspace-root> --serve` to preview it, and note that the `Last updated` comment should change with future edits.
