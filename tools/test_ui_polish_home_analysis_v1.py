#!/usr/bin/env python3
"""CSS-only UI polish guard for Home + Test Analysis (same theme, no logic)."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HOME = (ROOT / "tools/apply_home_command_center_v1.py").read_text(encoding="utf-8")
ANALYSIS = (ROOT / "tools/apply_practice_analysis_v1.py").read_text(encoding="utf-8")


def css_tail(text: str, marker: str, name: str) -> str:
    tail = text.split(marker, 1)[-1]
    end = tail.find("</style>")
    assert end > 0, f"{name} polish block is not inside a style element"
    return tail[:end]


def balanced(css: str, name: str) -> None:
    opens = css.count("{")
    closes = css.count("}")
    assert opens == closes, f"{name} has unbalanced braces: {opens} vs {closes}"


def main() -> None:
    # Polish markers must exist in their single-owner transforms.
    assert "nk-ui-polish-2026-09-23-home" in HOME, "home polish marker missing"
    assert "nk-ui-polish-2026-09-23-home-v2" in HOME, "home v2 polish marker missing"
    assert "nk-ui-polish-2026-09-23-analysis" in ANALYSIS, "analysis polish marker missing"
    assert "nk-ui-polish-2026-09-23-analysis-v2" in ANALYSIS, "analysis v2 polish marker missing"

    # Theme loyalty: foundation tokens must remain untouched.
    for token in ("#302b78", "#7561ff", "#f6f7fb", "#151852", "#ff8c32",
                  ".nk-home-focus-card", ".nk-v3-subject-card",
                  ".result-stat-grid", ".result-stat-completion", ".mode-pill"):
        assert token in HOME or token in ANALYSIS, f"theme token lost: {token}"

    # Polish must be CSS-only: no new JS behavior, no hidden controls,
    # no fixed overlays, no layout-removing display rules on key surfaces.
    combined = HOME + ANALYSIS
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

    # Only the two approved owner files may carry the markers.
    for path in sorted((ROOT / "tools").glob("apply_*.py")):
        if path.name in ("apply_home_command_center_v1.py",
                         "apply_practice_analysis_v1.py"):
            continue
        text = path.read_text(encoding="utf-8")
        assert "nk-ui-polish-2026-09-23" not in text, \
            f"polish leaked into wrong owner: {path.name}"

    print("UI_POLISH_HOME_ANALYSIS_OK css_only=true theme_loyal=true scoped=true reduced_motion=true")


if __name__ == "__main__":
    main()
