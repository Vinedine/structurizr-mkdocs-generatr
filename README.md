# structurizr-mkdocs-generatr

Generate MkDocs Material sites from Structurizr DSL workspaces.

## Prerequisites

- Docker (for Structurizr vNext and PlantUML)
- Python >= 3.11

## Installation

```bash
pip install structurizr-mkdocs-generatr
```

## Usage

```bash
# Generate a static site
structurizr-mkdocs path/to/workspace/

# Serve locally with live reload
structurizr-mkdocs path/to/workspace/ --serve

# Skip Docker export (reuse previous build artifacts)
structurizr-mkdocs path/to/workspace/ --skip-export
```
