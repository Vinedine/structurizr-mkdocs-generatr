---
name: c4-add-system
description: Add a new software system to a Structurizr DSL workspace from a product intake or submission template: DSL block in the right group file, docs folder with 0000-introduction.md, and relationships. Use when the user pastes an intake or asks to add or register a new system. Not for adding containers to an existing system (use c4-add-container).
allowed-tools: Read, Grep, Glob, Edit, Write, Bash(mkdir:*)
---

# Add a software system

Turn a pasted product intake into a new software system. Business owners fill in these templates, so expect loose formatting, misspelled names, and missing fields.

## Step 0: Find the workspace

<!-- STEP-0-SYNC: keep this block in sync across all c4-* skills. -->

The workspace root is the first of these that exists:

1. `src/master/workspace.dsl` → workspace root is `src/master/`
2. `src/workspace.dsl` → workspace root is `src/`
3. `./workspace.dsl` → workspace root is `./`
4. `example/workspace.dsl` → workspace root is `example/`

If none exists, ask the user. Under the root, the includes directory (`groups/`, `views/`, `deployments/`, `users.dsl`) is `workspace-includes/` or `workspace/`. The repo's conventions live in `CLAUDE.md` at its root, or `main.md` if present; read them, and where they differ from this skill, they win.

Learn the repo's patterns from what is already there: the groups under `groups/`, the properties and tags that existing systems in the target group carry, and the actors in `users.dsl`.

## Step 1: Read the intake

Product name, description, and owning group are required; ask for any that are missing, and show the valid groups if the owning group doesn't match one. If existing systems carry an ID property (a portfolio ID, say), ask for it too. Everything else is optional: product owner, actors, authentication, integrations, business capabilities, business data (context, manage, consume), references.

Resolve every actor, auth provider, and integration to an existing variable (`user<Name>`, `softwareSystem<Name>`). Names in intakes are often slightly off: propose the likely match, and ask about anything you can't resolve rather than dropping it. Integrations without a protocol default to `"JSON/HTTPS"`.

**The description must not repeat what the diagrams show.** Containers, auth relationships, integrations, and which users reach which client are all drawn. Keep what a diagram can't say: business purpose, vendor or hosting arrangement, provisioning quirks, compliance, ownership, history, permission models. For example, drop "Authentication is delegated to Microsoft Entra ID"; keep "Access requires the user to be provisioned in the back-end; authentication alone is insufficient". Rewrite the submitted description accordingly, and ask for business context if nothing is left.

## Step 2: Confirm

Show the user what you will create (variable and folder names, target files, description, resolved actors and relationships, open issues) and wait for a yes. This is where misread fields and wrong groups get caught cheaply.

## Step 3: Create

- **Variable** `softwareSystem<PascalCaseName>`; **docs folder** `<workspace-root>/software-system-docs/<group-path>/<lowerCamelName>/`.
- **DSL:** append the system to `<includes-dir>/groups/<group-path>.dsl`, matching the tags and properties of its neighbours, with `!docs` relative to that file. Relationships go inside the block, after `properties`: `user<Actor> -> this "<what they do>"`, `this -> softwareSystem<Auth> "Authenticate" "JSON/HTTPS"`, `this -> softwareSystem<X> "<purpose>" "<protocol>"`.
- **View:** if `workspace.dsl` includes `_auto_generated_views.dsl`, views are generated on the next build; add nothing. Otherwise append a system-context view to `<includes-dir>/views/systemContext.dsl`:

  ```dsl
  systemContext softwareSystem<Name> "SystemContext<Name>" {
      include *
      autoLayout
  }
  ```
- **Docs:** `0000-introduction.md` with Description, Business Capabilities, Business Data (Context, Manage, Consume), and References.

Containers and deployments are out of scope; a system with no containers is valid. Point the user to `c4-add-container` for the next step.

## Step 4: Report

Summarize what changed and suggest `structurizr-mkdocs <workspace-root> --serve` (or the repo's own serve command) to check that the DSL parses and the page renders.
