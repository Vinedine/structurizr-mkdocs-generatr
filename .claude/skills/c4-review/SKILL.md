---
name: c4-review
description: Run a Well-Architected-style review against a software system (or the whole landscape), using Microsoft Azure Well-Architected Framework pillars. Read-only — writes a Markdown review report without modifying the model.
allowed-tools: Read, Grep, Glob, Bash(ls:*), Bash(git:*), Bash(mkdir:*), Write, Agent, mcp__ado__repo_list_directory, mcp__ado__repo_get_repo_by_name_or_id, mcp__ado__repo_list_repos_by_project, mcp__ado__search_code
---

# Architecture Review (Azure Well-Architected, minimal)

You are a specialized read-only skill that evaluates a software system (or the whole landscape) against the **Microsoft Azure Well-Architected Framework**. You produce a Markdown review report with findings per pillar — you never modify the model.

The five pillars evaluated:

1. **Reliability** — availability, resilience, recovery, health modelling
2. **Security** — identity, data protection, network segmentation, secrets
3. **Cost Optimization** — right-sizing, unused resources, cost visibility
4. **Operational Excellence** — observability, automation, IaC, release practices
5. **Performance Efficiency** — scaling, bottlenecks, data path efficiency

**Scope caveats (v1):** report-only, no scoring/weighting, no cross-system comparison, no trend tracking. The skill writes a single Markdown file summarising observations and suggested follow-ups per pillar.

## Step 0: Discover Repo Structure

<!-- STEP-0-SYNC: keep this block in sync across all c4-* skills. -->

Try these workspace-root candidates in order, first match wins:

1. `src/master/workspace.dsl` → workspace root is `src/master/`
2. `src/workspace.dsl` → workspace root is `src/`
3. `./workspace.dsl` → workspace root is `./`
4. `example/workspace.dsl` → workspace root is `example/`

If none match, STOP and ask the user for the workspace root path.

Then detect the includes-directory layout (`workspace-includes/` or `workspace/`) — whichever exists under the workspace root.

1. **Canonical reference:** Check for `CLAUDE.md` at repo root (and `main.md` if it exists) for conventions.

## Step 1: Determine Scope

From the user's request, determine scope:

- **Single system** — the user named one software system (e.g., *"run a review on the ticketing platform"*). Locate it by Grep of the group DSL files and capture its variable name, display name, `!docs` path, and containers.
- **Landscape** — the user said `"whole landscape"` or didn't name a system. Enumerate all software systems from the group DSL files and review them at a summary level (less depth per pillar, broader coverage).

If scope is ambiguous, ask the user to choose.

## Step 2: Gather Evidence

For the target system(s):

1. **Read the DSL** — system definition, containers, relationships, tags, properties (especially `"Repository"` URLs).
2. **Read the system docs** — `0000-introduction.md`, `0001-technical.md` if present, any ADRs referenced.
3. **Read deployment views** — look for deployment nodes/environments and infrastructure zoning for this system (under `<includes-dir>/deployments/`).
4. **Access container source (optional but high-value)** — for containers with a `"Repository"` property, try in order:
   - Local clone: extract the repo name from the URL — the segment after `/_git/` for Azure DevOps, or the last path segment for GitHub/GitLab — and strip any trailing `.git`. Search under `~/Code/<repo-name>`, `~/source/<repo-name>`, `~/repos/<repo-name>`. Use an **Agent (Explore)** subagent to gather pillar-relevant signals (see Step 3).
   - Git-host MCP if available (`mcp__ado__*` for ADO; GitHub MCP for GitHub) → list directories and search code for the same signals.
   - If neither works, note the container as "no code evidence available" and continue.

## Step 3: Evaluate Pillars

For each pillar, answer 3–5 concrete questions using the evidence from Step 2. Example questions (the skill should adapt these to the tech stack in the system):

### Reliability
- Does the system have documented SLAs/SLOs anywhere (docs or ADRs)?
- Do the container(s) have retry policies / circuit breakers for outbound calls?
- Is there a deployment in more than one environment / region (from deployment views)?
- Is there evidence of a health endpoint or liveness/readiness probe?

### Security
- Is authentication documented in `0001-technical.md` or the code? What provider?
- Are secrets handled via a vault (Key Vault / environment) rather than config files?
- Are outbound integrations over HTTPS / TLS? (protocol strings in DSL relationships)
- Is there network-level segmentation in the deployment views (VNet, private endpoints)?

### Cost Optimization
- Are there containers deployed in every environment (prod + non-prod), or only where needed?
- Any "free"/dev SKUs visible in deployment nodes?
- Any unused/stale systems (systems tagged `"Legacy"` or `"External System"` with no active relationships)?

### Operational Excellence
- Is there evidence of IaC (Bicep/Terraform files in the container repo)?
- Is there a CI/CD pipeline file (`azure-pipelines.yml`, `.github/workflows/`)?
- Does the system have logging/observability (App Insights key in config, structured logging)?
- Are ADRs or runbooks linked from the docs?

### Performance Efficiency
- Is the container horizontally scalable (Azure Function consumption plan, AKS, Container Apps) vs. a single VM?
- Is there caching (Redis container, HTTP cache headers, CDN) in the architecture?
- Are heavy workloads decoupled from request paths (queues, Service Bus, events)?

For each question, capture: answer, evidence (file:line or "not found"), suggested follow-up if the answer is weak.

## Step 4: Rate Each Pillar

For each pillar, assign a status:

- **Green** — all questions answered affirmatively with evidence.
- **Amber** — at least one gap, but the system has the fundamentals.
- **Red** — multiple gaps, or a critical pillar (Security especially) has no evidence at all.

Be conservative: absence of evidence is amber, not green. If you couldn't access the code at all, state this explicitly and downgrade Operational Excellence / Security accordingly.

## Step 5: Write the Report

Create the reviews folder if needed:

```bash
mkdir -p "<workspace-root>/software-system-docs/<group-path>/<systemFolder>/reviews"
```

Write to:
`<workspace-root>/software-system-docs/<group-path>/<systemFolder>/reviews/YYYY-MM-DD-well-architected.md`

(For a landscape-scope review, write to `<workspace-root>/<includes-dir>/pages/reviews/YYYY-MM-DD-well-architected-landscape.md`, using the includes directory detected in Step 0 — so `workspace/pages/reviews/` or `workspace-includes/pages/reviews/` depending on the repo layout.)

### Report structure

```markdown
<!-- Last updated: YYYY-MM-DD -->

# Well-Architected Review: <System Name>

**Framework:** [Microsoft Azure Well-Architected Framework](https://learn.microsoft.com/en-us/azure/well-architected/)
**Scope:** <single system | landscape>
**Date:** YYYY-MM-DD

## Summary

| Pillar | Status |
|---|---|
| Reliability | 🟢 / 🟡 / 🔴 |
| Security | 🟢 / 🟡 / 🔴 |
| Cost Optimization | 🟢 / 🟡 / 🔴 |
| Operational Excellence | 🟢 / 🟡 / 🔴 |
| Performance Efficiency | 🟢 / 🟡 / 🔴 |

## Reliability — 🟢/🟡/🔴

**Observations:**
- <observation 1 with evidence reference>
- <observation 2>

**Suggested follow-ups:**
- <follow-up 1>
- <follow-up 2>

## Security — 🟢/🟡/🔴

[same shape as Reliability]

## Cost Optimization — 🟢/🟡/🔴

[same shape]

## Operational Excellence — 🟢/🟡/🔴

[same shape]

## Performance Efficiency — 🟢/🟡/🔴

[same shape]

## Evidence limitations

<one paragraph noting anything that couldn't be evaluated — missing code access, missing deployment views, etc. — so the reader knows where the gaps are>
```

## Step 6: Post-Generation

1. Tell the user where the report was written.
2. Recommend running `structurizr-mkdocs . --serve` to see it rendered in the site at `http://localhost:8000`.
3. Remind the user this is v1 scope: report-only, no scoring, no tracking. Running the skill again later writes a new dated file alongside the old one — history accumulates in the `reviews/` folder.

## Important Notes

- **This skill is read-only.** Never edit the DSL, `0000-introduction.md`, or `0001-technical.md`. Only write the new review file.
- **Cite evidence.** Every observation should reference a file, a DSL relationship, or an explicit "not found" — avoid unsupported claims.
- **Be conservative on ratings.** If evidence is missing, that's amber, not green.
- **No auto-remediation in v1.** Suggest follow-ups, don't act on them.
- **Stay within the framework.** The skill evaluates the five Azure Well-Architected pillars — not general opinions on the architecture. If the user wants a different framework, they should say so, and this skill should note the mismatch rather than silently apply a different rubric.
- **Landscape scope is broader and shallower.** For landscape reviews, summarise per pillar across all systems rather than drilling into any single system. Mention the 2–3 systems that most move the needle per pillar.
