"""Resolve workspace view properties into site configuration."""

from __future__ import annotations

import re
from dataclasses import dataclass


MATERIAL_NAMED_COLORS = frozenset({
    "red", "pink", "purple", "deep-purple", "indigo", "blue", "light-blue",
    "cyan", "teal", "green", "light-green", "lime", "yellow", "amber",
    "orange", "deep-orange", "brown", "grey", "blue-grey", "black", "white",
})

_HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{3,8}$")


@dataclass
class SiteProperties:
    theme: str = "auto"
    primary_color: str | None = None
    accent_color: str | None = None
    header_text_color: str | None = None
    favicon: str | None = None
    logo: str | None = None
    custom_css: str | None = None
    svg_link_target: str = "_blank"
    navigation_instant: bool = False
    navigation_tabs: bool = True
    full_width: bool = True
    show_legend: bool = False
    mermaid_view_source: bool = False
    description: str | None = None
    copyright: str | None = None
    site_url: str | None = None

    def has_hex_colors(self) -> bool:
        return any(
            v and _HEX_COLOR_RE.match(v)
            for v in (self.primary_color, self.accent_color, self.header_text_color)
        )

    def hex_colors(self) -> dict[str, str]:
        """Return only the color properties that are valid hex colors."""
        result: dict[str, str] = {}
        if self.primary_color and _HEX_COLOR_RE.match(self.primary_color):
            result["primary"] = self.primary_color
        if self.header_text_color and _HEX_COLOR_RE.match(self.header_text_color):
            result["header_text"] = self.header_text_color
        if self.accent_color and _HEX_COLOR_RE.match(self.accent_color):
            result["accent"] = self.accent_color
        return result


def _parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in ("true", "1", "yes")


def _validate_color(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if value.lower() in MATERIAL_NAMED_COLORS:
        return value.lower()
    if _HEX_COLOR_RE.match(value):
        return value
    return None


def _validate_theme(value: str | None) -> str:
    if value and value.strip().lower() in ("auto", "light", "dark"):
        return value.strip().lower()
    return "auto"


def _validate_svg_target(value: str | None) -> str:
    if value and value.strip() in ("_self", "_blank", "_parent", "_top"):
        return value.strip()
    return "_blank"


def resolve_properties(view_properties: dict[str, str]) -> SiteProperties:
    """Resolve workspace ``mkdocs.*`` view properties into a SiteProperties instance."""
    get = view_properties.get
    return SiteProperties(
        theme=_validate_theme(get("mkdocs.theme")),
        primary_color=_validate_color(get("mkdocs.color.primary")),
        accent_color=_validate_color(get("mkdocs.color.accent")),
        header_text_color=_validate_color(get("mkdocs.color.headerText")),
        favicon=get("mkdocs.favicon"),
        logo=get("mkdocs.logo"),
        custom_css=get("mkdocs.customCss"),
        svg_link_target=_validate_svg_target(get("mkdocs.svgLinkTarget")),
        navigation_instant=_parse_bool(get("mkdocs.navigation.instant")),
        navigation_tabs=_parse_bool(get("mkdocs.navigation.tabs"), default=True),
        full_width=_parse_bool(get("mkdocs.fullWidth"), default=True),
        show_legend=_parse_bool(get("mkdocs.showLegend")),
        mermaid_view_source=_parse_bool(get("mkdocs.mermaid.viewSource")),
        description=get("mkdocs.description"),
        copyright=get("mkdocs.copyright"),
        site_url=get("mkdocs.siteUrl"),
    )
