"""Shared Mermaid utilities used by markdown_writer and bounded_context."""

from __future__ import annotations

import re


def _iter_top_level_lines(content: str):
    """Yield (line, is_nested) tuples, tracking 4+ backtick outer fences.

    Lines inside outer fences have is_nested=True and should be passed through unchanged.
    """
    outer_fence = False
    for line in content.split("\n"):
        stripped = line.strip()
        if not outer_fence and re.match(r"^`{4,}", stripped):
            outer_fence = True
            yield line, True
        elif outer_fence:
            if re.match(r"^`{4,}$", stripped):
                outer_fence = False
            yield line, True
        else:
            yield line, False


def add_mermaid_view_source(content: str, enabled: bool = False) -> str:
    """Append a collapsible 'View Source' admonition after each top-level ```mermaid block.

    Only adds the admonition when *enabled* is True (controlled by the
    ``mkdocs.mermaid.viewSource`` property, default OFF).
    """
    if not enabled:
        return content

    result: list[str] = []
    in_mermaid = False
    mermaid_lines: list[str] = []

    for line, nested in _iter_top_level_lines(content):
        if nested:
            result.append(line)
            continue

        stripped = line.strip()
        if not in_mermaid and stripped == "```mermaid":
            in_mermaid = True
            mermaid_lines = [line]
            continue
        if in_mermaid:
            mermaid_lines.append(line)
            if stripped == "```":
                result.extend(mermaid_lines)
                result.append("")
                result.append('??? info "View Source"')
                result.append("")
                result.append("    ```text")
                for ml in mermaid_lines[1:-1]:
                    result.append(f"    {ml}")
                result.append("    ```")
                in_mermaid = False
            continue

        result.append(line)

    return "\n".join(result)
