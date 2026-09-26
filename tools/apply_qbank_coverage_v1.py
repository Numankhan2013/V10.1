#!/usr/bin/env python3
"""Add an all-bank QBank coverage tracker to Insights."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"
CORE = ROOT / "tools/qbank_coverage_core.js"
MARKER = "NK_QBANK_COVERAGE_V1_START"
OLD_START = '      <section class="nk-section"><div class="nk-section-head"><div><div class="nk-kicker">CHAPTER PERFORMANCE</div>'
OLD_END = '      <section class="nk-section"><div class="nk-section-head"><div><div class="nk-kicker">RECENT</div>'

CSS = '''<style id="nk-qbank-coverage-v1">
.nk-coverage{margin-top:16px}.nk-coverage>.nk-section-head>span{font-size:10px;color:#647394;font-weight:800;text-align:right}
.nk-coverage-intro{margin:7px 0 13px;color:#647394;font-size:11px;line-height:1.55}
.nk-coverage-overall{padding:16px;border:1px solid #dce5f8;border-radius:14px;background:#f4f7ff}
.nk-coverage-overall>div{display:flex;align-items:baseline;justify-content:space-between;gap:9px;margin-bottom:11px}
.nk-coverage-overall strong{color:#23366f;font-size:19px}.nk-coverage-overall span{color:#5e6f94;font-size:10.5px;font-weight:750;text-align:right}
.nk-coverage-track{display:block;height:6px;overflow:hidden;border-radius:99px;background:#e3e9f4}
.nk-coverage-track>i{display:block;height:100%;border-radius:inherit;background:#536dca}
.nk-coverage-banks{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:9px;margin:12px 0}
.nk-coverage-bank{min-width:0;min-height:105px;display:grid;grid-template-columns:minmax(0,1fr) auto;column-gap:7px;align-content:space-between;align-items:start;padding:12px;border:1px solid #e1e6ef;border-radius:12px;background:#fff;color:#1e2b59;font:inherit;text-align:left}
.nk-coverage-bank.is-active{border-color:#637cd0;background:#f7f9ff;box-shadow:inset 0 0 0 1px #637cd0}
.nk-coverage-bank strong,.nk-coverage-bank small{display:block}.nk-coverage-bank strong{font-size:12px;line-height:1.25}.nk-coverage-bank small{margin-top:3px;color:#67758f;font-size:10px;line-height:1.35}
.nk-coverage-bank>b{font-size:12px}.nk-coverage-bank>.nk-coverage-track{grid-column:1/-1;margin-top:11px;height:5px}
.nk-coverage-bank em{grid-column:1/-1;margin-top:5px;color:#61708d;font-size:10px;font-style:normal}
.nk-coverage-detail{border:1px solid #e1e6ef;border-radius:14px;background:#fff;overflow:hidden}
.nk-coverage-detail-head{display:flex;align-items:baseline;justify-content:space-between;gap:10px;padding:15px 15px 0}
.nk-coverage-detail-head strong{font-size:14px;color:#1e2b59}.nk-coverage-detail-head span{font-size:10px;color:#66748c;text-align:right}
.nk-coverage-tools{display:grid;grid-template-columns:minmax(0,1fr) 142px;gap:9px;padding:13px 15px}
.nk-coverage-tools label>span{display:block;margin-bottom:5px;color:#51617e;font-size:10px;font-weight:800}
.nk-coverage-tools input,.nk-coverage-tools select{width:100%;height:43px;box-sizing:border-box;padding:0 11px;border:1px solid #dbe1eb;border-radius:9px;background:#fff;color:#20315c;font:inherit;font-size:12px}
.nk-coverage-list-meta{padding:0 15px 10px;color:#697691;font-size:10px;font-weight:700}
.nk-coverage-list{border-top:1px solid #ebedf3}.nk-coverage-topic{width:100%;min-height:67px;display:grid;grid-template-columns:minmax(0,1fr) 36px 16px;align-items:center;gap:10px;padding:11px 15px;border:0;border-bottom:1px solid #ebedf3;background:#fff;color:#21315c;font:inherit;text-align:left}
.nk-coverage-topic:last-child{border-bottom:0}.nk-coverage-topic-copy{min-width:0}.nk-coverage-topic strong,.nk-coverage-topic small{display:block;overflow-wrap:anywhere}
.nk-coverage-topic strong{font-size:12px;line-height:1.3}.nk-coverage-topic small{margin-top:3px;color:#68758d;font-size:10px;line-height:1.4}
.nk-coverage-topic .nk-coverage-track{width:100%;height:4px;margin-top:8px}.nk-coverage-topic>b{font-size:11px;text-align:right}
.nk-coverage-more{width:100%;min-height:45px;border:0;border-top:1px solid #e8ebf2;background:#f8faff;color:#405ca6;font:inherit;font-size:11px;font-weight:800}
.nk-coverage-empty{margin:0;padding:18px 15px;color:#647394;font-size:11px;line-height:1.5}
.nk-coverage button:focus-visible,.nk-coverage input:focus-visible,.nk-coverage select:focus-visible{outline:3px solid #9db1ed;outline-offset:2px}
@media(max-width:620px){.nk-coverage-banks{grid-template-columns:repeat(2,minmax(0,1fr))}.nk-coverage-bank{min-height:108px}.nk-coverage-overall>div{align-items:flex-start;flex-direction:column;gap:2px}.nk-coverage-overall span{text-align:left}}
@media(max-width:380px){.nk-coverage-tools{grid-template-columns:minmax(0,1fr) 115px}.nk-coverage-bank{padding:10px}.nk-coverage-bank strong{font-size:11px}}
</style>'''


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return source.replace(old, new, 1)


def transform(source: str) -> str:
    if MARKER in source:
        return source
    if "NK_CBT_RESULT_ANALYSIS_V1_START" not in source:
        raise SystemExit("QBank coverage must run after the saved-test result analysis")
    source = replace_once(source, "</head>", CSS + "\n</head>", "coverage styles")
    start = source.find(OLD_START)
    end = source.find(OLD_END, start)
    if start < 0 or end < 0 or source.count(OLD_START) != 1:
        raise SystemExit("Old active-bank chapter list anchor missing or duplicated")
    source = source[:start] + source[end:]
    source = replace_once(source, "      ${nkInsightsFocusSection()}\n",
                          "      ${nkCoverageSection()}\n      ${nkInsightsFocusSection()}\n",
                          "Insights tracker position")
    source = replace_once(source, "  window.QB={", CORE.read_text(encoding="utf-8").rstrip() +
                          "\n\n  window.QB={nkCoverageSelectBank,nkCoverageSetSearch,nkCoverageSetStatus,nkCoverageShowMore,nkCoverageOpen,",
                          "coverage actions")
    return source


if __name__ == "__main__":
    HTML.write_text(transform(HTML.read_text(encoding="utf-8")), encoding="utf-8")
    print("QBANK_COVERAGE_INSTALLED: source-exact all-bank study map in Insights")
