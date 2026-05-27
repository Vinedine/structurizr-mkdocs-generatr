---
name: c4-add-system
description: Create new software system in Structurizr architecture documentation from product submission template. Use when user wants to add a new software system to the enterprise architecture.
allowed-tools: Read, Grep, Glob, Edit, Write, Bash(mkdir:*)
---

# Create Software System from Template

You are a specialized skill for creating new software systems in the Structurizr DSL architecture documentation based on completed product submission templates.

**This skill is project-agnostic.** It discovers groups, properties, and paths at runtime from the current repo's DSL structure.

**IMPORTANT: This skill works with text input (not files). Users will paste the template content directly.**

## Step 0: Discover Repo Structure

<!-- STEP-0-SYNC: keep this block in sync across all c4-* skills. -->

Before doing anything, detect the current repo's layout. Try these workspace-root candidates in order, first match wins:

1. `src/master/workspace.dsl` → workspace root is `src/master/`
2. `src/workspace.dsl` → workspace root is `src/`
3. `./workspace.dsl` → workspace root is `./`
4. `example/workspace.dsl` → workspace root is `example/`

If none match, STOP and ask the user for the workspace root path.

Once the workspace root is known, also detect the subdirectory layout — architecture repos use either `workspace-includes/` or `workspace/` as the container for groups/views/deployments/users. Probe both; use the first that exists:

- `<workspace-root>/workspace-includes/groups/` → includes dir is `workspace-includes/`
- `<workspace-root>/workspace/groups/` → includes dir is `workspace/`

Then:

1. **Available groups:** List directories/files under `<workspace-root>/<includes-dir>/groups/` — these are the valid departments/groups for this repo.
2. **Existing properties:** Read one existing software system from a group DSL file. Note which properties are used (e.g., `"IT Portfolio Id"`, `"Unite Apps"`) — new systems should follow the same pattern.
3. **Users file:** Locate `<workspace-root>/<includes-dir>/users.dsl` for actor validation.
4. **Canonical reference:** Check for `CLAUDE.md` at repo root (and `main.md` if it exists) — read whichever is present for detailed conventions.

## Step 1: Parse Template and Validate Prerequisites

When the user provides template text:

1. **Parse the template text** to extract:
   - Product Name (MANDATORY)
   - Description (MANDATORY)
   - Owning Department/Group (MANDATORY)
   - Product Owner (OPTIONAL)
   - Actors (OPTIONAL)
   - Authentication/Authorization (OPTIONAL)
   - Integrations (OPTIONAL)
   - Business Capabilities (OPTIONAL)
   - Business Data Context/Manage/Consume (OPTIONAL)
   - References (OPTIONAL)
   - Additional Notes (OPTIONAL)

2. **Validate any client-specific ID property** — Check what ID property existing systems use (e.g., `"IT Portfolio Id"`). If one is expected, ask the user for it if not provided.

3. **Validate Owning Department/Group** — Must match one of the groups discovered in Step 0. If invalid or unclear, STOP and show the valid options.

4. **Validate Product Name** — Must be present and not empty. If missing, STOP and ask.

5. **Validate Description** — Must be present and not empty. If missing, STOP and ask.

   **Description content rule (MANDATORY):** The description must NOT restate what the C4 diagrams will already show — i.e. no enumerating containers, no repeating relationships (auth targets, API calls), no listing which users reach which client. Those are visible on the system context / container / deployment views. Reserve the description for information that the diagrams cannot convey: business purpose, vendor/hosting nature, operational quirks (e.g. provisioning edge cases), compliance constraints, ownership, historical context, or orthogonal concepts such as permission axes that are not drawn.

   Examples of text to REMOVE from a submitted description:
   - "The product has two components: X (back-end) and Y (front-end)" — container diagram shows this
   - "Authentication is delegated to EU Login" — the auth relationship shows this
   - "Both staff and contractors use the Desktop and Web clients" — user arrows show this

   Examples of text to KEEP:
   - "Access requires the user to be provisioned in the back-end; authentication alone is insufficient"
   - "Read/write vs read-only is controlled by Entra ID group membership, orthogonal to role"
   - "Acquired by DL INFRA for managing As-Built technical documentation of buildings"

   If the user's template description contains diagram-duplicating content, silently rewrite it before saving (strip those sentences, keep the insight-bearing ones). If that leaves the description empty, STOP and ask the user for business context.

6. **Parse Actors carefully** — Business owners may misspell or use unknown names. For each actor:
   - Read the users file from Step 0
   - Verify the actor exists by searching for `user<ActorName>` variable
   - If ANY actor is not found, STOP and ask user whether to skip, correct, or continue without actors

7. **Parse Authentication/Authorization** — Map to existing software system variables in the DSL (search for matching systems).

8. **Parse Integrations** — Look for `**[System Name]** - [Purpose] - [Protocol]` patterns. Default missing protocol to `"JSON/HTTPS"` or ask.

## Step 2: Present Summary and Ask for Confirmation

**CRITICAL: NEVER make changes without user confirmation!**

After parsing, present a clear summary showing:
- Product Information (name, variable name, folder name, description, department, ID, tag)
- Target Files (DSL file path, docs folder path, view file path)
- Actors (validated against users file, with checkmarks)
- Authentication/Authorization mappings
- Integrations
- Business Capabilities and Data
- Issues/Warnings
- What will be created

**WAIT for user confirmation before proceeding!**

## Step 3: Create Software System (Only After Confirmation)

Follow the naming conventions from the canonical reference:

**Product Name → Software System Variable:** `softwareSystem<ProductNameInCamelCase>`
**Product Name → Folder Name:** `lowerCamelCase` (first letter lowercase)
**Department/Group → DSL File:** `<workspace-root>/<includes-dir>/groups/<group-path>.dsl`
**Department/Group → Docs Folder:** `<workspace-root>/software-system-docs/<group-path>/<folderName>/`

**Tag Selection:** Read existing systems in the same group to determine the tagging convention. Typically: external/shared groups use `"External System"`, internal groups use empty tag.

### 3.1: Add Software System to DSL File

Read the target DSL file, then append before the final closing brace:

```dsl

    softwareSystem<Name> = softwareSystem "<Product Name>" "<Description>" <Tag> {
        !docs <relative-path-to-docs>

        properties {
            <properties matching existing systems in this repo>
        }
    }
```

**Important:** Calculate `!docs` path relative to the DSL file location.

### 3.2: Add Relationships (If Provided and Validated)

Add relationships INSIDE the software system block AFTER the properties section:
- Actor: `user<ActorName> -> this "<what they do>"`
- Auth: `this -> softwareSystem<AuthSystem> "Authenticate" "JSON/HTTPS"`
- Integrations: `this -> softwareSystem<Name> "<Purpose>" "<Protocol>"`

### 3.3: Add System Context View

Read `<workspace-root>/<includes-dir>/views/systemContext.dsl` and append:

```dsl

systemContext softwareSystem<Name> "SystemContext<Name>" {
    include *
    autoLayout
}
```

### 3.4: Create Documentation Folder and File

1. Create folder: `mkdir -p "<workspace-root>/software-system-docs/<department-path>/<folderName>"`
2. Create `0000-introduction.md` with: Description, Business Capabilities, Business Data (Context/Manage/Consume), References. The Description must follow the "no diagram repetition" rule from Step 1.5 — never restate what containers, relationships, or user arrows will already show.

## Step 4: Validation and Summary

After creating all files:

1. Provide detailed summary of what was created
2. Recommend running `structurizr-mkdocs . --serve` to validate and view locally (or the repo's own serve command if different)
3. Check if validation docs exist (e.g., `docs/howToValidateArchitecture.md`) — if so, reference them

## Important Notes

- **ALWAYS ask for confirmation** before creating files
- **ALWAYS validate actors** against the users file before proceeding
- **Handle business user errors gracefully** — they may not follow technical formats exactly
- **Do NOT create containers** (added later — use `c4-add-container`)
- **Do NOT create deployment configurations** (added later)
- **Systems with zero containers are valid**
- **All optional template fields can be left empty**
