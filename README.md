# structurizr-mkdocs-generatr

Generate MkDocs Material sites from Structurizr DSL workspaces.

> Inspired by and based on [structurizr-site-generatr](https://github.com/avisi-cloud/structurizr-site-generatr) by Avisi Cloud. This project aims to provide similar functionality using Python, MkDocs Material, and Structurizr vNext instead of the archived Java libraries. Thank you to the original authors for their excellent work!

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
