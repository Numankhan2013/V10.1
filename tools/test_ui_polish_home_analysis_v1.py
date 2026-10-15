#!/usr/bin/env python3
"""CSS-only UI polish guard for Home + Test Analysis (same theme, no logic).

The polish blocks lived in inline `<style id=...>` elements until the stylesheet
was consolidated into app.css on 2026-10-12; each surface still owns exactly one
`/* ── <id> ── */` section and one polish marker.
"""

from pathlib import Path
from app_page import app_css, app_source, css_section

ROOT = Path(__file__).resolve().parents[1]
PAGE = app_source()
SHEET = app_css()


def style_block(style_id: str) -> str:
    return css_section(style_id)


HOME = style_block("nk-home-command-center-v1")
ANALYSIS = style_block("qbank-practice-analysis-v1")


def css_tail(text: str, marker: str, name: str) -> str:
    assert marker in text, f"{name} polish marker missing"
    tail = text.split(marker, 1)[-1]
    end = tail.find("/* ── ")
    return tail[:end] if end > 0 else tail


def balanced(css: str, name: str) -> None:
    opens = css.count("{")
    closes = css.count("}")
    assert opens == closes, f"{name} has unbalanced braces: {opens} vs {closes}"


def main() -> None:
    # Polish markers must exist in their single-owner stylesheets.
    assert "nk-ui-polish-2026-09-23-home" in HOME, "home polish marker missing"
    assert "nk-ui-polish-2026-09-23-home-v2" in HOME, "home v2 polish marker missing"
    assert "nk-ui-polish-2026-09-23-analysis" in ANALYSIS, "analysis polish marker missing"
    assert "nk-ui-polish-2026-09-23-analysis-v2" in ANALYSIS, "analysis v2 polish marker missing"

    # Theme loyalty: the foundation theme (Geist tokens and the retained Home /
    # Analysis surfaces) must remain untouched by the polish layer.
    for token in ("--nkg-fg", "--nkg-bg-subtle", "--nkg-border", "--nkg-amber", "--nkg-orange",
                  ".nk-home-focus-card", ".nk-v3-subject-card",
                  ".result-stat-grid", ".result-stat-completion", ".mode-pill"):
        assert token in SHEET, f"theme token lost: {token}"

    # Polish must be CSS-only: no new JS behavior, no hidden controls,
    # no fixed overlays, no layout-removing display rules on key surfaces.
    home_css = css_tail(HOME, "nk-ui-polish-2026-09-23-home", "home")
    analysis_css = css_tail(ANALYSIS, "nk-ui-polish-2026-09-23-analysis", "analysis")
    assert "position:fixed" not in home_css, \
        "home polish must not introduce fixed overlays"
    for bad in ('display:none', 'visibility:hidden'):
        assert bad not in analysis_css, f"analysis polish must not hide content: {bad}"

    # New selectors must stay scoped to Home / result surfaces.
    home_tail = css_tail(HOME, "nk-ui-polish-2026-09-23-home", "home")
    for selector in (".nk-home-focus-card", ".nk-v3-subject-card",
                     ".nk-home-quick-grid", ".nk-home-streak-card"):
        assert selector in home_tail, f"home polish missing scope: {selector}"
    analysis_tail = css_tail(ANALYSIS, "nk-ui-polish-2026-09-23-analysis", "analysis")
    for selector in (".result-stat", ".mode-pill", ".v102-review-action"):
        assert selector in analysis_tail, f"analysis polish missing scope: {selector}"

    # Reduced-motion safety for every new hover lift.
    assert "prefers-reduced-motion" in home_tail or "prefers-reduced-motion" in HOME, \
        "home reduced-motion guard missing"
    assert "prefers-reduced-motion" in analysis_tail, \
        "analysis reduced-motion guard missing"

    balanced(home_css, "home polish")
    balanced(analysis_css, "analysis polish")

    # Only the two approved owner stylesheets may carry the markers.
    marker = "nk-ui-polish-2026-09-23"
    assert PAGE.count(marker) == HOME.count(marker) + ANALYSIS.count(marker), \
        "polish leaked outside the Home / Analysis stylesheets"

    print("UI_POLISH_HOME_ANALYSIS_OK css_only=true theme_loyal=true scoped=true reduced_motion=true")


if __name__ == "__main__":
    main()
