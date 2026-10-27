---
name: c4-validate-changes
description: Read-only pre-PR check of an architecture branch, including uncommitted and untracked changes: validates DSL, views, and docs against the repo's documented standards and compares new containers with technology peers. Use before opening a PR, or when the user asks to validate, lint, or check their architecture changes.
allowed-tools: Read, Grep, Glob, Bash(git:*), Agent
---

# Validate branch changes

Check everything this branch changes against the repo's documented standards, compare new containers with their technology peers, and report. This skill is read-only.

## Step 0: Find the workspace

<!-- STEP-0-SYNC: keep this block in sync across all c4-* skills. -->

The workspace root is the first of these that exists:

1. `src/master/workspace.dsl` → workspace root is `src/master/`
2. `src/workspace.dsl` → workspace root is `src/`
3. `./workspace.dsl` → workspace root is `./`
4. `example/workspace.dsl` → workspace root is `example/`

If none exists, ask the user. Under the root, the includes directory (`groups/`, `views/`, `deployments/`, `users.dsl`) is `workspace-includes/` or `workspace/`. The repo's conventions live in `CLAUDE.md` at its root, or `main.md` if present; read them, and where they differ from this skill, they win.

Read the standards fresh each run rather than from memory: the conventions file, any guides under `docs/` (such as `howToValidateArchitecture.md`), and `boundedContext.mmd` if it exists. Note which files are generated and must not be hand-edited: anything whose header says `AUTO-GENERATED` and `DO NOT EDIT` (such as `_auto_generated_views.dsl`) and whatever the conventions file lists.

## Step 1: Collect the change

The change is everything on this branch that `main` (or `master`) lacks, committed or not, because validation usually runs before the commit:

```bash
base=$(git merge-base HEAD main 2>/dev/null || git merge-base HEAD master)
git diff "$base" --stat                     # branch commits plus uncommitted edits
git diff "$base"
git ls-files --others --exclude-standard    # untracked files: read each in full as new
```

Diff from the merge base, never `main..HEAD`: that misses uncommitted edits, and once `main` moves on it shows main's new commits as reversed changes here. Record the merge-base commit and how many files are committed, uncommitted, and untracked.

## Step 2: Check it against the standards

Apply whatever the conventions define (naming, container types, tags, required properties, protocol and authentication strings, which container types users may connect to, required doc sections, `!docs` paths) to every changed system, container, view, deployment, and doc. Each finding cites its file, its line where possible, and the rule's source. Beyond the repo's own rules, always check:

- **Container naming (error):** the display name starts with the system's display name plus a space, and the variable is `container` plus that name in PascalCase.
- **One relationship per source and destination (warning):** when a source has several lines to the same destination, the container diagram draws several arrows and the system-level view keeps only one description. Propose a single line with a combined description. Look at the whole source element, not just the added lines; the repeat is often an old line next to a new one.
- **`!docs` paths** resolve relative to their DSL file, with matching case, and every new system has a `0000-introduction.md`.
- **Views:** with `_auto_generated_views.dsl` included, only hand-written views need checking; otherwise each new system needs a system-context view, a container view if it has containers, and deployment views per environment.
- **Descriptions that repeat the diagrams (warning):** sentences listing containers, auth or integration relationships, or which users reach which client. Quote each with a trimmed version; keep anything a diagram can't show.
- **Generated files** edited by hand, `FIXME`/`TODO`/`HACK` markers, and commented-out code in `workspace.dsl`.
- **`boundedContext.mmd`**, if changed: matching START/END markers, UPPER_CASE entity codes that aren't substrings of each other, a click link per entity.

## Step 3: Compare with peers

For each new or changed container, find the existing containers with the same technology and type, and tabulate naming, properties, auth relationships, deployment environments, views, and parent-system docs side by side. Flag anything every peer has and the new container lacks. This comparison is often the most useful part of the report.

## Step 4: Report

```markdown
# Branch Validation Report: `<branch>`

**Baseline:** `<merge-base sha>` against the working tree: <N> committed, <M> uncommitted, <K> untracked

## Errors (must fix)
- **[E001]** <finding> (`<file>:<line>`). Rule: <source>

## Warnings (should fix)
## Info
## Technology Peer Comparison
## Summary
<counts of errors, warnings, info, files, systems, and containers>
```

End by recommending `structurizr-mkdocs <workspace-root> --serve` (or the repo's own command) to confirm the DSL parses and the changes render before opening the PR.
