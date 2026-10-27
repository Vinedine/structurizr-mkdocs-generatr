---
name: c4-review
description: Read-only Azure Well-Architected review of one software system or the whole landscape, written as a dated Markdown report with a status and evidence per pillar (reliability, security, cost, operations, performance). Use when the user asks for an architecture review, Well-Architected assessment, or health check.
allowed-tools: Read, Grep, Glob, Bash(ls:*), Bash(git:*), Bash(mkdir:*), Write, Agent, mcp__ado__repo_list_directory, mcp__ado__repo_get_repo_by_name_or_id, mcp__ado__repo_list_repos_by_project, mcp__ado__search_code
---

# Well-Architected review

Review a software system, or the whole landscape, against the five pillars of the [Microsoft Azure Well-Architected Framework](https://learn.microsoft.com/en-us/azure/well-architected/): Reliability, Security, Cost Optimization, Operational Excellence, and Performance Efficiency. The report is the only file this skill writes; it never edits the model or the docs, and it suggests follow-ups rather than acting on them. If the user wants a different framework, say this skill doesn't cover it instead of improvising one.

## Step 0: Find the workspace

<!-- STEP-0-SYNC: keep this block in sync across all c4-* skills. -->

The workspace root is the first of these that exists:

1. `src/master/workspace.dsl` → workspace root is `src/master/`
2. `src/workspace.dsl` → workspace root is `src/`
3. `./workspace.dsl` → workspace root is `./`
4. `example/workspace.dsl` → workspace root is `example/`

If none exists, ask the user. Under the root, the includes directory (`groups/`, `views/`, `deployments/`, `users.dsl`) is `workspace-includes/` or `workspace/`. The repo's conventions live in `CLAUDE.md` at its root, or `main.md` if present; read them, and where they differ from this skill, they win.

## Step 1: Scope

A named system gets a deep review. "The whole landscape", or no system named, gets a broad, shallow one that names the two or three systems that matter most per pillar. Ask if it's unclear.

## Step 2: Gather evidence

The system's DSL (containers, relationships and their protocols, tags, properties), its docs (`0000-introduction.md`, `0001-technical.md`, linked ADRs), and its deployment nodes under `<includes-dir>/deployments/`. Code is optional but valuable:

Find each repository's code in this order:

1. **A local clone.** The repo name is the segment after `/_git/` (Azure DevOps) or the last path segment (GitHub, GitLab), without `.git`. Look next to the architecture repo (`../<repo-name>`), then under `~/Code/`, `~/source/`, `~/repos/`. Note the commit you read (`git -C <path> log -1 --format='%h %cd'`).
2. **A Git-host MCP** for that host (`mcp__ado__*` for Azure DevOps, a GitHub MCP for GitHub), if one is connected.
3. **Ask the user** where the code is.

Analyze each repository in its own Explore subagent, all started in the same turn, so code doesn't flood the main context.

If code isn't reachable, record that and carry on.

## Step 3: Assess each pillar

Judge each pillar from what you found, adapted to the system's stack. Typical signals: SLOs, retries, multi-environment or multi-region deployment, and health probes (reliability); the auth provider, secrets in a vault, TLS on every integration, and network segmentation (security); right-sized SKUs, environments that need not exist, and orphaned systems (cost); IaC, CI/CD, observability, and runbooks or ADRs (operations); horizontal scaling, caching, and heavy work moved off the request path (performance).

Rate each pillar 🟢 (fundamentals in place, with evidence), 🟡 (gaps, or evidence missing), or 🔴 (several gaps, or no evidence at all for security). Absence of evidence is amber, never green; without code access, say so and rate Security and Operational Excellence accordingly. Every observation cites a file, a DSL relationship, or "not found".

## Step 4: Write the report

Write `<workspace-root>/software-system-docs/<group-path>/<systemFolder>/reviews/YYYY-MM-DD-well-architected.md`, or `<workspace-root>/<includes-dir>/pages/reviews/YYYY-MM-DD-well-architected-landscape.md` for a landscape review. Start with `<!-- Last updated: YYYY-MM-DD -->`, a title, the framework link, scope, and date; then a summary table of pillar and status; then one section per pillar with **Observations** and **Suggested follow-ups**; and finish with **Evidence limitations**, saying what couldn't be checked.

Tell the user where it is and suggest `structurizr-mkdocs <workspace-root> --serve`. Each run writes a new dated file, so `reviews/` doubles as a history.
