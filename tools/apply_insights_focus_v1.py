#!/usr/bin/env python3
"""Add one evidence-backed cross-bank study recommendation section to Insights."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"
CORE = ROOT / "tools/insights_focus_core.js"
MARKER = "NK_INSIGHTS_FOCUS_V1_START"
ANCHOR = '      <section class="nk-section"><div class="nk-section-head"><div><div class="nk-kicker">CHAPTER PERFORMANCE</div>'

CSS = """<style id="nk-insights-focus-v1">
.nk-insights-focus{margin-top:16px}
.nk-insights-focus>.nk-section-head>span{font-size:10px;color:#647394;font-weight:800}
.nk-insights-focus-explain{margin:8px 0 12px;color:#647394;font-size:11px;line-height:1.5}
.nk-insights-focus-row{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:13px 0;border-top:1px solid #e5e9f2}
.nk-insights-focus-row small{display:block;color:#526893;font-size:10px;font-weight:800}
.nk-insights-focus-row h3{margin:3px 0;color:#17204b;font-size:13px;line-height:1.35}
.nk-insights-focus-row p{margin:0;color:#697592;font-size:11px}
.nk-insights-focus-row button{min-height:44px;min-width:130px;display:flex;align-items:center;justify-content:space-between;gap:7px;padding:0 10px;border:0;border-radius:9px;background:#eef2fb;color:#3658ad;font:inherit;font-size:11px;font-weight:800;text-align:left}
.nk-insights-focus-row button:focus-visible{outline:3px solid #8ca3ed;outline-offset:2px}
.nk-insights-focus-empty{padding:16px;border:1px solid #e5e9f2;border-radius:11px;background:#f8faff}
.nk-insights-focus-empty strong{color:#263861;font-size:12px}
.nk-insights-focus-empty p{margin:5px 0 0;color:#697592;font-size:11px;line-height:1.5}
@media(max-width:420px){.nk-insights-focus-row{align-items:stretch;flex-direction:column}.nk-insights-focus-row button{width:100%}}
</style>"""


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return source.replace(old, new, 1)


def transform(source: str) -> str:
    if MARKER in source:
        return source
    if "NK_REVISION_DESK_V1_START" not in source:
        raise SystemExit("Insights focus must run after the bank-aware revision desk")
    source = replace_once(source, "</head>", CSS + "\n</head>", "Insights styles")
    source = replace_once(source, ANCHOR, "      ${nkInsightsFocusSection()}\n" + ANCHOR, "Insights section")
    source = replace_once(source, "  window.QB={", CORE.read_text(encoding="utf-8").rstrip() + "\n\n  window.QB={nkPracticeInsightFocus,", "Insights action")
    return source


if __name__ == "__main__":
    HTML.write_text(transform(HTML.read_text(encoding="utf-8")), encoding="utf-8")
    print("INSIGHTS_FOCUS_INSTALLED: cross-bank current-miss topics and direct Practice")
