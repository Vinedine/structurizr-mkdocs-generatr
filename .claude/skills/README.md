# Claude Code Skills

Six skills that turn this repo into an AI-assisted architecture workbench. Each skill is a single-file definition Claude Code auto-discovers when it runs inside a repo that contains this folder.

## What each skill does

| Skill | What you say | What it writes | Read-only? |
|---|---|---|---|
| [`c4-add-system`](c4-add-system/SKILL.md) | *"add a new system from this intake"* | DSL block in the right group file + docs folder + system-context view | No |
| [`c4-add-container`](c4-add-container/SKILL.md) | *"add a container X to system Y"* | Container block + relationships inside the existing software system | No |
| [`c4-document-system`](c4-document-system/SKILL.md) | *"generate a technical page for system X"* | `0001-technical.md` by analyzing the container's source repo | No |
| [`c4-audit-system`](c4-audit-system/SKILL.md) | *"audit the entities for system X"* | Report comparing `0000-introduction.md` against the actual code | Report first, then offers fixes |
| [`c4-review`](c4-review/SKILL.md) | *"run a Well-Architected review on system X"* | Markdown report in `reviews/YYYY-MM-DD-well-architected.md`, five Azure Well-Architected pillars | Yes |
| [`c4-validate-changes`](c4-validate-changes/SKILL.md) | *"validate this branch"* | Report of errors/warnings against standards + peer-container comparison | Yes |

The read/write skills all ask for confirmation before touching the DSL or docs.

## The pipeline

The skills are designed to feed each other. A common loop:

1. **Intake** — `c4-add-system` creates the software system from a template.
2. **Detail** — `c4-add-container` adds each container with its technology and `"Repository"` URL.
3. **Ground truth** — `c4-document-system` pulls the latest source via the Repository URL and writes `0001-technical.md`.
4. **Drift check** — `c4-audit-system` compares the documented entities against what the code actually manages/consumes.
5. **Assess** — `c4-review` produces a Well-Architected report against the five Azure pillars.
6. **Ship** — `c4-validate-changes` checks your branch against conventions and peers before the PR.

The technical page produced in step 3 becomes the reference that downstream skills read — the output of one skill is the input for the next.

## Install

### Option A: Global install (recommended)

Makes the skills available in every Claude Code session on your machine, regardless of which Structurizr repo you're working in. Best for architects across multiple repos.

```bash
git clone --depth 1 https://github.com/Vinedine/structurizr-mkdocs-generatr.git /tmp/smg
mkdir -p ~/.claude/skills && cp -r /tmp/smg/.claude/skills/c4-* ~/.claude/skills/
rm -rf /tmp/smg
```

### Option B: Project-scoped install

Skills are available only inside your architecture repo. Best for teams who want skills version-pinned alongside their DSL.

```bash
git clone --depth 1 https://github.com/Vinedine/structurizr-mkdocs-generatr.git /tmp/smg
mkdir -p .claude/skills && cp -r /tmp/smg/.claude/skills/c4-* .claude/skills/
rm -rf /tmp/smg
```

After either install, open the repo in Claude Code and type `/c4` — the six skills appear in the picker.

If you're already inside this repo's clone, the skills are picked up automatically.

## Prerequisites

- **Claude Code.** The skills are invoked through the Claude Code CLI, desktop app, web app, or IDE extension.
- **For the code-linked skills** (`c4-document-system`, `c4-audit-system`, `c4-review`): the containers in your DSL should have a `"Repository"` property with the Git URL. The skills prefer local clones under `~/Code/`, `~/source/`, or `~/repos/`; otherwise they fall back to a Git-host MCP if available (Azure DevOps or GitHub), and last resort ask you to clone locally.
- **For `c4-validate-changes`**: a Git branch with diffs against `main` or `master`.

## How they discover your repo

Every skill first runs a **Step 0: Discover Repo Structure** pass that probes for `workspace.dsl` in these locations, first match wins:

1. `src/master/workspace.dsl`
2. `src/workspace.dsl`
3. `./workspace.dsl`
4. `example/workspace.dsl`

They also auto-detect whether your includes directory is `workspace-includes/` or `workspace/`. No configuration needed.

## Not here yet

- An orchestrating skill that runs the whole pipeline (create → detail → technical → audit → review → validate) unattended.
- Scoring/weighting for `c4-review`, cross-system comparison, trend tracking.
- A "while you're here" drift-sidecar pass in `c4-document-system` that flags DSL/model drift at the same time it writes the technical page.

Open an issue if any of these would be useful for your workflow.
