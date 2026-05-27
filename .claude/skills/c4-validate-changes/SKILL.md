---
name: c4-validate-changes
description: Validate architecture branch changes against documented standards and compare with technology peers. Use before creating a PR.
allowed-tools: Read, Grep, Glob, Bash(git:*), Agent
---

# Validate Branch Changes

You are a specialized read-only skill that validates branch changes against the documented architecture standards. You produce a structured report of errors, warnings, and observations — but never modify any files.

**This skill is project-agnostic.** It discovers paths, standards docs, and generated file lists at runtime from the current repo's structure.

## Step 0: Discover Repo Structure

<!-- STEP-0-SYNC: keep this block in sync across all c4-* skills. -->

Try these workspace-root candidates in order, first match wins:

1. `src/master/workspace.dsl` → workspace root is `src/master/`
2. `src/workspace.dsl` → workspace root is `src/`
3. `./workspace.dsl` → workspace root is `./`
4. `example/workspace.dsl` → workspace root is `example/`

If none match, STOP and ask the user for the workspace root path.

Then detect the includes-directory layout (`workspace-includes/` or `workspace/`) — whichever exists under the workspace root.

1. **Canonical reference:** Check for `CLAUDE.md` at repo root (and `main.md` if it exists) — read whichever is present as the primary standards document.
2. **Validation docs:** Check if `docs/` folder exists — read any available guides (e.g., `howToValidateArchitecture.md`, `howToUpdateBoundedContext.md`).
3. **Generated files:** Identify files that are auto-generated and must not be hand-edited. Look for a header comment like `AUTO-GENERATED — DO NOT EDIT` in workspace files (e.g., `_auto_generated_views.dsl`), and treat these as a conservative default: `*.csv` files, any file under `workspace-docs/` named `01-actors.md` or `02-bounded-contexts.md`. If the repo's CLAUDE.md lists additional generated artifacts, include those too.
4. **Bounded context file:** Check if `boundedContext.mmd` exists — only validate it if present.

## Step 1: Identify What Changed

Run these git commands to understand the branch diff against `main` (or `master`):

```bash
git diff main..HEAD --stat 2>/dev/null || git diff master..HEAD --stat
git diff main..HEAD 2>/dev/null || git diff master..HEAD
```

From the diff output:

1. **Categorize changed files** into:
   - **DSL definitions** — files under `<includes-dir>/groups/`
   - **Views** — files under `<includes-dir>/views/`
   - **Deployments** — files under `<includes-dir>/deployments/`
   - **Documentation** — files under `software-system-docs/`
   - **Generated files** — as discovered in Step 0
   - **Bounded context** — `boundedContext.mmd` (if present)
   - **Workspace root** — `workspace.dsl`, `<includes-dir>/users.dsl`

2. **Extract new/modified software systems and containers** from `+` lines in the diff.

## Step 2: Read Standards by Reference

Read the actual standards documents at runtime. Do NOT rely on memorized rules — always read the current versions:

### Canonical reference (CLAUDE.md or main.md)
Look for:
- **Naming conventions** — variable naming patterns
- **Container types** — allowed types
- **Software system tags** — valid tags and when to use each
- **Relationship patterns** — protocol strings, authentication exact strings, user interaction rules
- **Documentation structure** — required sections in `0000-introduction.md`
- **Generated artifacts** — which files are auto-generated
- **`!docs` path conventions** — how paths are calculated

### Validation docs (if they exist in `docs/`)
Look for architecture validation checklists, deployment validation rules, bounded context rules.

## Step 3: Validate Changes Against Standards

Apply the rules from Step 2 to the changes from Step 1:

### DSL Definitions
For each new/modified software system or container:
- **Naming conventions (variable)** — variable follows `softwareSystem<Name>` or `container<Name>` in camelCase
- **Container display-name prefix (ERROR if violated)** — every container's display name MUST begin with the parent software system's display name followed by a space. Examples of valid: system `"Primo"` → `"Primo Alma"`, `"Primo Discovery"`; system `"M-Files"` → `"M-Files Server"`. Examples of invalid: a container inside system `"Primo"` named `"Alma"` or `"Primo"` alone — raise an error asking the user to re-prefix the name. The variable and the display name must match (spaces removed, first letter after `container` lowercased).
- **Required properties** — check which properties existing peers have (ID fields, Repository, etc.)
- **Container types** — type is valid per the canonical reference
- **Relationship protocols** — all relationships include protocol
- **Authentication strings** — auth relationships use exact strings from the canonical reference
- **User interaction rules** — user relationships only on UI-facing container types
- **`!docs` path** — path is correct relative to DSL file, target folder exists (check case sensitivity)
- **Description** — system/container has a non-empty description
- **Tags** — system has appropriate tag

### Views
For each new/modified software system:
- **System context view** exists
- **Container view** exists (if system has containers)
- **Deployment views** exist for each environment

### Documentation
For each new/modified software system:
- **`0000-introduction.md` exists** in the correct folder
- **Required sections present** — per the canonical reference
- **Entity links** — links point to valid URLs (not placeholders)
- **Description does not duplicate diagram content (WARNING)** — scan the `# Description` section for phrases that merely restate what the C4 diagrams already show:
  - Enumerations of containers ("The product has two components: X and Y", "consists of a back-end and a front-end")
  - Authentication/integration relationships ("authenticates via EU Login", "calls the X API")
  - User-to-client arrows ("both staff and contractors use the Desktop and Web clients")

  These belong on diagrams, not in text. Flag such sentences as warnings and quote them with the suggested trimmed version. Keep prose that adds information diagrams cannot convey (business purpose, vendor/hosting, operational quirks, provisioning edge cases, compliance, ownership, orthogonal permission axes).

### Generated Files
- **Flag any manual edits** to generated files discovered in Step 0

### Bounded Context (only if `boundedContext.mmd` was changed and exists)
- **START/END markers** match
- **Entity codes** are UPPER_CASE
- **Global uniqueness** — no entity code is a substring of another
- **Click links** — every entity has a click statement
- **Cross-context links** in correct section

### Workspace Root
- **Check for FIXME/TODO/HACK** in changed files
- **Check workspace.dsl** for commented-out code

## Step 4: Technology Peer Comparison

For each **new or modified container** found in Step 1:

1. **Extract the container's technology and type**
2. **Find all peer containers** — Grep all group DSL files for containers with the same technology+type
3. **Read each peer's full context** (definition, deployments, views, parent system docs)
4. **Build a comparison table:**

   | Dimension | New Container | Peer 1 | Peer 2 |
   |-----------|--------------|--------|--------|
   | Naming pattern | follows convention? | | |
   | Properties | which ones? missing any? | | |
   | Auth relationships | present? | | |
   | Deployment environments | which? | | |
   | Views | which include it? | | |
   | Parent system docs | complete? | | |

5. **Flag inconsistencies** — if the new container is missing something ALL peers have

## Step 5: Report

```markdown
# Branch Validation Report: `<branch-name>`

## Errors (must fix)
- **[E001]** <description> — `<file>:<line>` — Rule: <source document and section>

## Warnings (should fix)
- **[W001]** <description> — `<file>` — Rule: <source document and section>

## Info (observations)
- **[I001]** <description>

## Technology Peer Comparison
<comparison table from Step 4>

## Summary

| Category | Count |
|----------|-------|
| Errors | X |
| Warnings | X |
| Info | X |
| Files changed | X |
| New/modified systems | X |
| New/modified containers | X |

**Recommendation:** Run `structurizr-mkdocs . --serve` to validate DSL syntax and visually verify all changes at http://localhost:8000 before creating a PR. (If the repo uses a different serve command, use that instead.)
```

## Important Notes

- **This skill is read-only** — it reports findings but never modifies files
- **Always read the actual docs** — do not rely on cached or memorized rules
- **Be specific with file:line references** — every error and warning should point to the exact location
- **Cite the rule source** — every finding should reference which document defines the rule
- **Peer comparison is key** — comparing against existing containers with the same technology is often the most valuable insight
