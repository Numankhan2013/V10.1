#!/usr/bin/env python3
"""Add source-exact post-CBT topic analysis and targeted practice to results."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"
CORE = ROOT / "tools/cbt_result_analysis_core.js"
MARKER = "NK_CBT_RESULT_ANALYSIS_V1_START"

CSS = '''<style id="nk-cbt-result-analysis-v1">
.nk-cbt-analysis-intro{margin:0 0 14px;color:#66728c;font-size:12px;line-height:1.5}
.nk-cbt-followup{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:16px;margin-bottom:12px;border:1px solid #d8e1fa;border-radius:14px;background:#f2f5ff}
.nk-cbt-followup strong,.nk-cbt-followup small{display:block}.nk-cbt-followup strong{color:#263875;font-size:14px}.nk-cbt-followup small{margin-top:4px;color:#647394;font-size:11px;line-height:1.4}
.nk-cbt-followup button{min-height:42px;padding:0 13px;border:0;border-radius:10px;background:#423790;color:#fff;font:inherit;font-size:11px;font-weight:800;display:flex;align-items:center;justify-content:center;gap:5px;white-space:nowrap}
.nk-cbt-followup button:focus-visible,.nk-cbt-analysis-rest summary:focus-visible{outline:3px solid #abbaf3;outline-offset:2px}
.nk-cbt-followup.is-clear{background:#effaf5;border-color:#d3ebdf}
.nk-cbt-analysis-list{border:1px solid #e1e5ee;border-radius:14px;background:#fff;overflow:hidden}
.nk-cbt-analysis-row{display:grid;grid-template-columns:minmax(0,1fr) auto;column-gap:14px;row-gap:10px;align-items:center;padding:15px 16px;border-bottom:1px solid #edf0f5}
.nk-cbt-analysis-row:last-child{border-bottom:0}.nk-cbt-analysis-copy{min-width:0}.nk-cbt-analysis-copy strong,.nk-cbt-analysis-copy small,.nk-cbt-analysis-numbers b,.nk-cbt-analysis-numbers small{display:block}
.nk-cbt-analysis-copy strong{color:#1b2855;font-size:13px;line-height:1.3;overflow-wrap:anywhere}.nk-cbt-analysis-copy small,.nk-cbt-analysis-numbers small{margin-top:4px;color:#647394;font-size:10.5px;line-height:1.35}
.nk-cbt-analysis-numbers{text-align:right}.nk-cbt-analysis-numbers b{color:#27375d;font-size:12px;white-space:nowrap}
.nk-cbt-analysis-track{grid-column:1/-1;height:5px;overflow:hidden;border-radius:99px;background:#e9edf5}.nk-cbt-analysis-track span{display:block;height:100%;border-radius:inherit;background:#4486df}
.nk-cbt-analysis-rest{border-bottom:1px solid #edf0f5}.nk-cbt-analysis-rest:last-child{border-bottom:0}.nk-cbt-analysis-rest summary{padding:14px 16px;color:#405782;font-size:12px;font-weight:800;cursor:pointer}.nk-cbt-analysis-rest .nk-cbt-analysis-row{background:#fbfcff}
.nk-cbt-analysis-unavailable{margin:10px 0 0;color:#7a6670;font-size:11px}
@media(max-width:560px){.nk-cbt-followup{align-items:stretch;flex-direction:column}.nk-cbt-followup button{width:100%;min-height:46px}.nk-cbt-analysis-row{grid-template-columns:1fr auto;padding:14px 12px;gap:8px}.nk-cbt-analysis-numbers small{max-width:125px}}
</style>'''


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return source.replace(old, new, 1)


def transform(source: str) -> str:
    if MARKER in source:
        return source
    if "NK_BANK_AWARE_CBT_BUILDER_V1_START" not in source:
        raise SystemExit("CBT result analysis must run after the bank-aware CBT builder")
    source = replace_once(source, "</head>", CSS + "\n</head>", "analysis styles")
    source = replace_once(source, "      ${studyModule?nkModuleResultExtras(t,studyModule):''}",
                          "      ${nkCbtResultSection(t)}\n      ${studyModule?nkModuleResultExtras(t,studyModule):''}", "result section")
    source = replace_once(source, "  window.QB={", CORE.read_text(encoding="utf-8").rstrip() +
                          "\n\n  window.QB={nkCbtPracticeMisses,", "analysis action")
    return source


if __name__ == "__main__":
    HTML.write_text(transform(HTML.read_text(encoding="utf-8")), encoding="utf-8")
    print("CBT_RESULT_ANALYSIS_INSTALLED: saved-test topic breakdown and targeted practice")
