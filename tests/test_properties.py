"""Tests for properties resolution."""

from __future__ import annotations

from structurizr_mkdocs_generatr.properties import SiteProperties, resolve_properties


class TestResolveProperties:
    def test_defaults(self):
        props = resolve_properties({})
        assert props.theme == "auto"
        assert props.primary_color is None
        assert props.svg_link_target == "_blank"
        assert props.full_width is True
        assert props.navigation_tabs is True
        assert props.show_legend is False

    def test_mkdocs_keys(self):
        props = resolve_properties({
            "mkdocs.theme": "dark",
            "mkdocs.color.primary": "indigo",
            "mkdocs.color.accent": "pink",
            "mkdocs.fullWidth": "true",
            "mkdocs.showLegend": "true",
        })
        assert props.theme == "dark"
        assert props.primary_color == "indigo"
        assert props.accent_color == "pink"
        assert props.full_width is True
        assert props.show_legend is True

    def test_invalid_theme_defaults_to_auto(self):
        props = resolve_properties({"mkdocs.theme": "neon"})
        assert props.theme == "auto"

    def test_style_keys_resolved(self):
        props = resolve_properties({
            "mkdocs.color.primary": "#2c4390",
            "mkdocs.color.headerText": "#ffffff",
            "mkdocs.favicon": "site/favicon.ico",
            "mkdocs.logo": "site/logo.png",
        })
        assert props.primary_color == "#2c4390"
        assert props.header_text_color == "#ffffff"
        assert props.favicon == "site/favicon.ico"
        assert props.logo == "site/logo.png"

    def test_legacy_generatr_keys_ignored(self):
        props = resolve_properties({
            "generatr.style.colors.primary": "#2c4390",
            "generatr.style.logoPath": "old/logo.png",
        })
        assert props.primary_color is None
        assert props.logo is None

    def test_hex_color_accepted(self):
        props = resolve_properties({"mkdocs.color.primary": "#ff5722"})
        assert props.primary_color == "#ff5722"

    def test_invalid_color_rejected(self):
        props = resolve_properties({"mkdocs.color.primary": "not-a-color"})
        assert props.primary_color is None

    def test_svg_link_target_validation(self):
        props = resolve_properties({"mkdocs.svgLinkTarget": "_self"})
        assert props.svg_link_target == "_self"

    def test_invalid_svg_target_defaults(self):
        props = resolve_properties({"mkdocs.svgLinkTarget": "evil"})
        assert props.svg_link_target == "_blank"

    def test_bool_parsing(self):
        assert resolve_properties({"mkdocs.navigation.instant": "true"}).navigation_instant is True
        assert resolve_properties({"mkdocs.navigation.instant": "false"}).navigation_instant is False
        assert resolve_properties({"mkdocs.navigation.instant": "1"}).navigation_instant is True
        assert resolve_properties({"mkdocs.navigation.instant": "yes"}).navigation_instant is True


class TestSitePropertiesHexColors:
    def test_no_hex_colors(self):
        props = SiteProperties(primary_color="indigo")
        assert props.has_hex_colors() is False
        assert props.hex_colors() == {}

    def test_with_hex_colors(self):
        props = SiteProperties(primary_color="#ff0000", accent_color="#00ff00")
        assert props.has_hex_colors() is True
        colors = props.hex_colors()
        assert colors["primary"] == "#ff0000"
        assert colors["accent"] == "#00ff00"

    def test_mixed_named_and_hex(self):
        props = SiteProperties(primary_color="indigo", header_text_color="#fff")
        assert props.has_hex_colors() is True
        colors = props.hex_colors()
        assert "primary" not in colors
        assert colors["header_text"] == "#fff"
