#!/usr/bin/env python3
"""Install the full-page, bank-aware timed CBT builder after the Insights phase."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"
CORE = ROOT / "tools/bank_aware_cbt_builder_core.js"
MARKER = "NK_BANK_AWARE_CBT_BUILDER_V1_START"

CSS = '''<style id="nk-bank-aware-cbt-builder-v1">
.page:has(.nk-cbt-builder){animation:none!important;transform:none!important}
.nk-cbt-builder{max-width:820px}.nk-cbt-builder .nk-module-builder-card{min-height:0}
.nk-cbt-builder .nk-module-stepper{grid-template-columns:repeat(3,1fr)}
.nk-cbt-builder .nk-module-choice-grid{margin-top:13px}
.nk-cbt-bank-intro{display:flex;justify-content:space-between;align-items:baseline;gap:10px;color:#192452}
.nk-cbt-bank-intro strong{font-size:15px}.nk-cbt-bank-intro span{color:#647394;font-size:11px;font-weight:750}
.nk-cbt-bank-tools{margin:14px 0 0}
.nk-cbt-pyq-action{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-top:17px}
.nk-cbt-pyq-action button{min-height:44px;padding:0 14px;border:1px solid #647ad1;border-radius:10px;background:#eef2ff;color:#354da1;font:inherit;font-size:12px;font-weight:800}
.nk-cbt-pyq-action span{color:#465373;font-size:12px;font-weight:750;text-align:right}
.nk-cbt-pyq-status{margin:7px 0 0;color:#647394;font-size:11px;line-height:1.5}
.nk-cbt-builder .nk-module-subject{min-height:104px}
.nk-cbt-builder .nk-module-subject:focus-visible,.nk-cbt-count-grid button:focus-visible,.nk-cbt-main-actions button:focus-visible{outline:3px solid #abbaf3;outline-offset:2px}
.nk-cbt-main-actions{display:flex;justify-content:flex-end;margin-top:15px}
.nk-cbt-main-actions button{min-width:190px;min-height:48px;padding:0 16px;border:0;border-radius:11px;background:#423790;color:#fff;font:inherit;font-size:13px;font-weight:800}
.nk-cbt-main-actions button:disabled{opacity:.45}
.nk-cbt-summary{display:grid;grid-template-columns:1fr 1fr;gap:11px}
.nk-cbt-summary>div{padding:14px;border:1px solid #e1e5ee;border-radius:12px;background:#f8faff}
.nk-cbt-summary small,.nk-cbt-summary strong{display:block}.nk-cbt-summary small{margin-bottom:7px;color:#647394;font-size:11px;font-weight:750}
.nk-cbt-summary strong{color:#1b2855;font-size:13px;line-height:1.6}.nk-cbt-summary p{margin:3px 0 0;color:#647394;font-size:11px}
.nk-cbt-count{margin-top:22px}.nk-cbt-count h2{margin:0;color:#1b2855;font-size:17px}.nk-cbt-count p{margin:5px 0 12px;color:#647394;font-size:12px}
.nk-cbt-count-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(64px,1fr));gap:8px}
.nk-cbt-count-grid button{min-height:50px;border:1px solid #dfe4ed;border-radius:10px;background:#fff;color:#1b2855;font:inherit;font-size:14px;font-weight:800}
.nk-cbt-count-grid button.is-selected{border-color:#647ad1;background:#eef2ff;color:#354da1}
.nk-cbt-count label{display:block;margin-top:14px;color:#465373;font-size:12px;font-weight:800}
.nk-cbt-count input{display:block;width:100%;height:48px;box-sizing:border-box;margin-top:6px;padding:0 12px;border:1px solid #dfe4ed;border-radius:10px;background:#fff;color:#1b2855;font:inherit;font-size:15px}
.nk-cbt-timing{display:flex;gap:11px;align-items:flex-start;margin-top:18px;padding:14px;border:1px solid #dfe7fb;border-radius:12px;background:#f2f5ff;color:#334d93}
.nk-cbt-timing>span{flex:none}.nk-cbt-timing strong{font-size:13px}.nk-cbt-timing p{margin:5px 0 0;font-size:11px;line-height:1.5}
@media(max-width:620px){body:has(.nk-cbt-builder) .page{padding-bottom:190px!important}.nk-cbt-bank-intro{align-items:flex-start;flex-direction:column}.nk-cbt-builder .nk-module-subject{min-height:76px}.nk-cbt-pyq-action{align-items:flex-start;flex-direction:column;gap:6px}.nk-cbt-pyq-action span{text-align:left}.nk-cbt-summary{grid-template-columns:1fr}.nk-cbt-builder.is-topics .nk-module-topic-actions>span{font-size:10.5px}.nk-cbt-main-actions{position:fixed;bottom:96px;left:50%;z-index:35;width:calc(100% - 28px);max-width:760px;min-height:72px;box-sizing:border-box;align-items:center;margin:0;padding:10px;border:1px solid #dfe4ef;border-radius:14px;background:rgba(255,255,255,.97);box-shadow:0 -8px 26px rgba(29,38,78,.09);transform:translateX(-50%)}.nk-cbt-main-actions button{width:100%}}
</style>'''


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return source.replace(old, new, 1)


def transform(source: str) -> str:
    if MARKER in source:
        return source
    if "NK_INSIGHTS_FOCUS_V1_START" not in source or "NK_CUSTOM_STUDY_MODULES_V1_START" not in source:
        raise SystemExit("CBT builder must run after the bank-aware study modules and Insights")
    source = replace_once(source, "</head>", CSS + "\n</head>", "CBT styles")
    source = replace_once(source, "    else if(route.page==='module-builder') out=studyModuleBuilderPage();",
                          "    else if(route.page==='test-builder') out=nkCbtBuilderPage();\n    else if(route.page==='module-builder') out=studyModuleBuilderPage();", "CBT route")
    source = replace_once(source, "  window.QB={", CORE.read_text(encoding="utf-8").rstrip() +
                          "\n\n  window.QB={nkCbtSetBanks,nkCbtToggleBank,nkCbtSetStep,nkCbtSetTopics,nkCbtSelectVerifiedPyqs,nkCbtToggleGroup,nkCbtToggleTopic,nkCbtFilterTopics,nkCbtSetCount,nkCbtStart,", "CBT actions")
    return source


if __name__ == "__main__":
    HTML.write_text(transform(HTML.read_text(encoding="utf-8")), encoding="utf-8")
    print("BANK_AWARE_CBT_BUILDER_INSTALLED: full-page banks, topics, and question count")
