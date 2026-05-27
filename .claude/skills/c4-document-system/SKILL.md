---
name: c4-document-system
description: Generate a 0001-technical.md technical architecture page for a software system by analyzing its code repositories. Use when user wants to document a product's API endpoints, data model, and technical details.
allowed-tools: Read, Grep, Glob, Edit, Write, Bash(ls:*), Bash(git:*), Agent, mcp__ado__repo_list_directory, mcp__ado__repo_get_repo_by_name_or_id, mcp__ado__repo_list_repos_by_project, mcp__ado__search_code
---

# Create Technical Architecture Page

You are a specialized skill for generating `0001-technical.md` technical architecture documentation for a software system by analyzing its actual code repositories and DSL definitions.

**This skill is project-agnostic.** It discovers groups, containers, and repository URLs at runtime from the current repo's DSL structure.

## Reference Example

Before generating any page, read a reference `0001-technical.md` to understand the exact style, structure, and level of detail expected. Try in order:

1. `example/software-system-docs/commercial/ticketingPlatform/0001-technical.md` (bundled reference in the structurizr-mkdocs-generatr repo)
2. Any existing `0001-technical.md` in the current workspace — use Glob/Grep to find one

If no reference is found in the current workspace, fall back to the style rules documented below in Step 4.

## Step 0: Discover Repo Structure

<!-- STEP-0-SYNC: keep this block in sync across all c4-* skills. -->

Try these workspace-root candidates in order, first match wins:

1. `src/master/workspace.dsl` → workspace root is `src/master/`
2. `src/workspace.dsl` → workspace root is `src/`
3. `./workspace.dsl` → workspace root is `./`
4. `example/workspace.dsl` → workspace root is `example/`

If none match, STOP and ask the user for the workspace root path.

Then detect the includes-directory layout (`workspace-includes/` or `workspace/`) — whichever exists under the workspace root.

1. **Canonical reference:** Check for `CLAUDE.md` at repo root (and `main.md` if it exists) — read whichever is present for conventions.
2. **Reference technical page:** Find and read an existing `0001-technical.md` as described in "Reference Example" above.

## Step 1: Identify the Software System

When the user provides a software system name (or you infer it from context):

1. **Find the software system definition** in the DSL files under `<workspace-root>/<includes-dir>/groups/`:
   - Search for the software system by name using Grep
   - Read the full software system block including all containers

2. **Extract from the DSL:**
   - Software system variable name (e.g., `softwareSystemBusinessPartnersService`)
   - Software system display name (e.g., `"Business Partners Service"`)
   - `!docs` path → docs folder location
   - For each container:
     - Variable name (e.g., `containerBusinessPartnersServiceApi`)
     - Display name (e.g., `"Business Partners Service API"`)
     - Technology (e.g., `".NET (Core)"`, `"Node.Js"`)
     - Container type tag (e.g., `"SERVICE"`, `"DATASET"`, `"APPLICATION"`)
     - `"Repository"` property value (if present) — this is the code repo URL
     - All relationships (`this -> ...` and `... -> this`)

3. **Read `0000-introduction.md`** from the docs folder for business context (description, bounded context, entities).

4. **Check if `0001-technical.md` already exists.** If so, warn the user and ask whether to overwrite or update.

## Step 2: Analyze Code Repositories

For each container that has a `"Repository"` property:

### 2a: Access the Repository

Try these access paths in order, use the first that works:

1. **Local clone (preferred — fastest, no network):**
   - Extract the repo name from the URL:
     - Azure DevOps: the segment after `/_git/` (e.g., `https://dev.azure.com/Org/Project/_git/my-repo` → `my-repo`)
     - GitHub / GitLab / generic: the last path segment (e.g., `https://github.com/org/my-repo` → `my-repo`)
     - Strip any trailing `.git` suffix (e.g., `my-repo.git` → `my-repo`)
   - Search common local paths: `~/Code/<repo-name>`, `~/source/<repo-name>`, `~/repos/<repo-name>`
   - Run `ls` to verify the directory exists
   - If found, use an **Agent (Explore)** subagent to analyze the codebase. Send the agent a detailed prompt asking for:
     - All API endpoints (HTTP method, route, purpose, auth requirements)
     - Database schema (tables, columns, relationships, indexes)
     - Authentication/authorization setup
     - External service integrations
     - Scheduled jobs or background processes
     - Key architectural patterns
     - Tech stack details (runtime version, key dependencies)

2. **Git-host MCP (if available):**
   - If the URL is an Azure DevOps repo and `mcp__ado__*` tools are available, use them:
     - `mcp__ado__repo_list_directory` for structure
     - `mcp__ado__search_code` for controllers, endpoints, entities
     - Read key files: `Program.cs`/`Startup.cs`, controllers, models, database contexts, `package.json`, etc.
   - If the URL is a GitHub repo and a GitHub MCP is available, use its equivalent tools.
   - If neither MCP is available for the repo's host, fall through to step 3.

3. **Ask the user to clone locally** and re-run the skill.

### 2b: What to Extract

For each repository, build a structured understanding:

**Tech Stack (REQUIRED — extract this first):**
- Runtime / framework version — read it from the project manifest, do NOT infer from code style:
  - .NET: `<TargetFramework>` in `*.csproj` (e.g. `net8.0`, `net6.0`, `net48`)
  - Node.js: `engines.node` and key framework versions in `package.json`
  - Python: `python_requires` in `setup.py` / `pyproject.toml`, runtime in `requirements.txt` or `Pipfile`
  - Java: `<java.version>` / `<maven.compiler.target>` in `pom.xml`, or `sourceCompatibility` in `build.gradle`
  - Go: `go` directive in `go.mod`
- Key libraries that shape the architecture (ORM, web framework, auth lib, message bus client) — also from the manifest
- Never write a runtime version into the opening paragraph or any heading without having opened and read the manifest file. "ASP.NET Core" alone is fine when the major version isn't verified, but "ASP.NET Core 6" requires evidence.

**API Endpoints:**
- HTTP method (GET, POST, PUT, PATCH, DELETE)
- Full route path (e.g., `/api/v1/business-partners/{id}`)
- Purpose (what it does)
- Auth requirements (if discoverable)
- Group endpoints by domain/controller

**Database/Storage:**
- Tables with key columns and their types
- Relationships (FK, cascade behaviors)
- Naming conventions (snake_case, camelCase)
- Storage technology (PostgreSQL, Oracle, Azure Table Storage, etc.)

**Authentication & Authorization (REQUIRED — always extract and document this):**
- Auth provider (Entra ID, Active Directory, custom tokens, SharePoint context)
- Token type (JWT, API key, Basic Auth, Windows/NTLM/Kerberos)
- How identity flows between layers (e.g., token delegation, impersonation, pass-through)
- Authorization model (role-based, policy-based, resource-level security trimming)
- Custom auth middleware, action filters, or attributes (reference class names)
- CORS configuration (allowed origins, credentials)
- Role/policy definitions

**External Integrations:**
- What external services are called
- Protocol used (REST, SOAP, GraphQL, SQL)
- Purpose of each integration

**Scheduled Jobs / Background Processes:**
- Schedule (cron, timer triggers)
- What each job does

**Architecture Patterns:**
- Clean Architecture, CQRS, event-driven, etc.
- Notable patterns worth documenting

## Step 3: Present Summary and Confirm

**CRITICAL: NEVER write the file without user confirmation!**

Present a summary showing:

```
## Technical Page Summary: [Software System Name]

### Containers Analyzed
| Container | Technology | Repository | Endpoints Found |
|---|---|---|---|
| [Name] | [Tech] | [Local/Remote] | [Count] |

### Database/Storage
- [Table/storage descriptions]

### Authentication & Authorization
- [Summary of auth mechanisms per container]

### Proposed Document Structure
1. Authentication & Authorization
2. [Section 2 heading]
3. [Section 3 heading]
...

Ready to generate 0001-technical.md?
```

**WAIT for user confirmation before proceeding!**

## Step 4: Generate `0001-technical.md`

Write the file to `<docs-folder>/0001-technical.md` following these conventions from the reference example:

### Document Structure

The file uses **two top-level (`#`) sections** — `Technical Architecture` first, then `API Reference`. The site generator renders these as the two H2 entries in the page's right-side table of contents, which is intentional. Do NOT merge them into a single heading like "Technical Architecture and API Reference".

> **Note:** this two-`#` convention is coupled to `toc_depth: 2` in the generator's `mkdocs.yml` — any `###` subheadings are intentionally omitted from the right-side TOC so the two top-level sections stay prominent. If the site's `toc_depth` is ever raised, revisit this rule.

```markdown
<!-- Last updated: YYYY-MM-DD -->

# Technical Architecture

[Opening paragraph: 1-2 sentences summarizing the tech stack, repository link (as markdown), and number of deployable components. Match the tone of the reference example.]

## Authentication & Authorization

[Describe how the system authenticates and authorizes requests. Cover each container that has a distinct auth mechanism. Include:]
- Auth provider (IIS Windows Auth, Entra ID JWT, API keys, SharePoint context tokens, etc.)
- How identity flows through the system (e.g., token delegation, impersonation, pass-through)
- Authorization model (role-based, policy-based, resource-level security trimming, etc.)
- CORS configuration if applicable
- Any notable auth patterns (custom action filters, middleware, token helpers)

[Be specific to what the code implements — not generic descriptions. Reference class names, attributes, and configuration sections where relevant.]

## [Non-API container(s) — e.g. UI, worker, database]

[Brief description of each container that is NOT an API: what it does, its role, key configuration.]

## [Database/Storage Section - if applicable]

[Document database tables, their purpose, and key relationships.]

| Table | Domain | Usage |
| --- | --- | --- |
| TABLE_NAME | Domain | What it stores and why |

## [Event Publishing / Background Jobs - if applicable]

[Describe async outbound: topics, schemas, schedules.]

## [Architecture/Flow Section - if there are complex orchestration flows]

[Use text diagrams (``` blocks) for complex flows.]

# API Reference

## [API Container Name]

[Brief description of what this container does and its role.]

| Endpoint | Purpose |
| --- | --- |
| `GET /path` | What it does |
| `POST /path` | What it does |

[If the container has notable sub-sections (e.g., grouped endpoints by domain), use ### subheadings.]

### [Domain/Controller Group] endpoints (`/api/path/`)

| Endpoint | Purpose |
| --- | --- |
| `GET /path/action` | What it does |

## [Second API Container - if multiple API containers exist]

[Same pattern as above.]
```

**Do NOT include a Consumers section.** Consumer relationships are already defined in the DSL and the site generator auto-generates a dependencies page from them. Duplicating this in the technical page adds maintenance burden with no value.

### Style Rules

1. **First line:** `<!-- Last updated: YYYY-MM-DD -->` with today's date
2. **Two top-level headings (REQUIRED):** The file must have exactly two `#` headings — first `# Technical Architecture`, then `# API Reference`. These become the two H2 entries in the site's right-side table of contents. Do NOT combine them into `# Technical Architecture and API Reference`.
3. **Opening paragraph:** Concise, under `# Technical Architecture`. Mentions repo name as a link, tech stack summary, component count
4. **Endpoint tables:** Use backticks for endpoint paths (`` `GET /path` ``). Include the HTTP method
5. **Group endpoints** by controller/domain when there are many (use ### subheadings)
6. **Database tables:** Document when the system has its own database or uses shared storage. Database goes under `# Technical Architecture`, not under `# API Reference`
7. **Orchestration flows:** Only include if the system has complex async/multi-step processes. Goes under `# Technical Architecture`
8. **Keep it factual:** Document what the code does, not aspirational architecture
9. **No fluff:** Every section should contain concrete technical details (endpoints, tables, protocols)
10. **Match the reference:** The reference `0001-technical.md` located in Step 0 is your style guide — match its density and style
11. **Authentication & Authorization section is REQUIRED:** Always include it as the first `##` section under `# Technical Architecture`. Document the actual auth mechanism per container — reference class names, attributes, config sections. Cover identity flow, authorization model, and CORS where applicable
12. **API Reference contains endpoints only:** Put each API container's endpoint tables under `# API Reference`. Non-API containers (UI, worker, database, dashboard) go under `# Technical Architecture`
13. **No Consumers section:** Consumer relationships are auto-generated by the site generator from DSL relationships — do not duplicate them

### Containers WITHOUT Repositories

Some containers (databases, key vaults, dashboards, storage accounts) don't have code repositories. Include them in the document when they are architecturally significant:
- Databases: Document schema if discoverable from the API's code (EF Core entities, migrations)
- Storage: Document what's stored and how it's organized
- Dashboards: Brief mention of what they display
- Skip infrastructure containers (key vaults, etc.) unless they have notable configuration

## Step 5: Post-Generation

After writing the file:

1. Inform the user the file has been created
2. Recommend running `structurizr-mkdocs . --serve` to validate DSL and preview the page (or the repo's own serve command if different)
3. Suggest navigating to the product's documentation section at `http://localhost:8000` to verify rendering
4. Note that the `<!-- Last updated -->` comment should be updated when the page is revised in the future

## Important Notes

- **ALWAYS ask for confirmation** before writing the file
- **ALWAYS read the reference `0001-technical.md`** before generating — match its style exactly
- **Prefer local repos** over remote access for speed and completeness
- **Use Agent (Explore) subagents** for local repos to avoid flooding the main context with code
- **Use the Git-host MCP** for remote repos when local clones are not available
- **Document what exists in code**, not what the DSL says should exist — the code is the source of truth for technical details
- **Do NOT include a Consumers section** — consumer relationships are defined in the DSL and auto-generated by the site generator
- **Skip containers without repositories** unless their schema is discoverable from related API code
- **Handle multi-repo systems** by documenting each container with a repo in its own section
- **If the codebase is too large** to analyze completely, focus on API endpoints and database schema first — these are the most valuable sections
