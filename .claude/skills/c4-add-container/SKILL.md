---
name: c4-add-container
description: Add a container (API, service, database, UI, ETL, function) with its relationships and Repository URL to a software system that already exists in a Structurizr DSL workspace. Use when the user asks to add or model a container in an existing system. If the system does not exist yet, use c4-add-system first.
allowed-tools: Read, Grep, Glob, Edit, Write
---

# Add a container

Add a container, described by the user in their own words, to an existing software system. If the system doesn't exist, use `c4-add-system` first.

## Step 0: Find the workspace

<!-- STEP-0-SYNC: keep this block in sync across all c4-* skills. -->

The workspace root is the first of these that exists:

1. `src/master/workspace.dsl` → workspace root is `src/master/`
2. `src/workspace.dsl` → workspace root is `src/`
3. `./workspace.dsl` → workspace root is `./`
4. `example/workspace.dsl` → workspace root is `example/`

If none exists, ask the user. Under the root, the includes directory (`groups/`, `views/`, `deployments/`, `users.dsl`) is `workspace-includes/` or `workspace/`. The repo's conventions live in `CLAUDE.md` at its root, or `main.md` if present; read them, and where they differ from this skill, they win.

## Step 1: Gather the fields

Required: the target system, the container's name, a one-line description, its technology, and its type tag (valid tags come from the repo's conventions; `SERVICE`, `DATASET`, `UI_ELEMENT`, and so on). Optional: the `"Repository"` URL, which the code-reading skills depend on, so encourage it; and relationships in either direction, each with a purpose and protocol (default `"JSON/HTTPS"`, but a database is usually `"SQL/TCP"`).

**Naming rule.** The display name starts with the system's display name plus a space (system `"Ticketing Platform"` → `"Ticketing Platform API"`), so diagrams stay legible when several systems have an "API". The variable is `container` plus the display name in PascalCase without punctuation: `"Salesforce CRM REST API"` → `containerSalesforceCrmRestApi`. If the user gives a bare role like "API", propose the prefixed name.

## Step 2: Check against the model

Find the system's block in `<includes-dir>/groups/`, and confirm the variable is free and every relationship target exists as a `softwareSystem<X>`, `container<X>`, or `user<X>` variable. Ask about anything that doesn't resolve.

## Step 3: Confirm

Show the variable, display name, description, technology, tag, repository, and relationships, plus any warnings, and wait for a yes before editing.

## Step 4: Insert

Place the container inside the system block after its existing containers, matching their indentation. Omit `properties` if there's no repository URL.

```dsl
        container<Name> = container "<Name>" "<Description>" "<Technology>" "<TAG>" {
            properties {
                "Repository" "<URL>"
            }
        }
```

Write outbound relationships the way sibling containers do: inside the new block as `this -> <target> ...`, or at system level as `container<Name> -> <target> ...`. Inbound relationships (`<source> -> container<Name> ...`) go at system level after the containers. Views, deployments, and docs are out of scope.

## Step 5: Report

Say what changed. Suggest `c4-validate-changes` before the PR, `structurizr-mkdocs <workspace-root> --serve` to see it rendered, and, if a repository URL was given, `c4-document-system` to write its technical page.
