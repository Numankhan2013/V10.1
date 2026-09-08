#!/usr/bin/env python3
"""Install the pinned offline FSRS v6 scheduler after sync integration."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"
CORE = ROOT / "tools/fsrs_scheduler_core.js"

CSS = r'''<style id="nk-fsrs-v1">
.nk-fsrs-today{display:grid;gap:14px;margin:14px 0}.nk-fsrs-counts{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.nk-fsrs-counts b{display:grid;gap:3px;padding:11px;border-radius:13px;background:#f5f7fb;font-size:22px}.nk-fsrs-counts small{font-size:10px;color:var(--muted);text-transform:uppercase}.nk-fsrs-forecast{height:62px;display:flex;align-items:end;gap:9px}.nk-fsrs-forecast span{height:100%;flex:1;display:flex;flex-direction:column;align-items:center;justify-content:end;gap:4px}.nk-fsrs-forecast i{display:block;width:100%;max-width:32px;border-radius:6px 6px 2px 2px;background:var(--primary)}.nk-fsrs-forecast small{font-size:9px;color:var(--muted)}/* NK_FSRS_RECALL_DOCK_V2 */
.nk-session-footer .nk-fsrs-rating{position:relative;isolation:isolate;box-sizing:border-box;width:min(100%,760px);margin:0 auto 10px;padding:9px;min-height:66px;border:1px solid #eee8ff;border-radius:24px;display:grid;grid-template-columns:minmax(112px,1.4fr) repeat(3,minmax(0,.75fr));gap:6px;align-items:center;background:linear-gradient(120deg,#fff 10%,#f7f3ff 100%);box-shadow:0 3px 12px #6e41c51a,0 9px 24px #986ae83d}
.nk-fsrs-rating::before{content:"";position:absolute;z-index:-1;inset:9px 8px -6px;border-radius:30px;background:#a777ea;opacity:.17;filter:blur(14px);pointer-events:none}
.nk-fsrs-recall-label{display:flex;align-items:center;gap:8px;min-width:0;color:#26213b}.nk-fsrs-medallion{display:grid;place-items:center;flex:0 0 30px;height:30px;border-radius:50%;background:#ece2ff;color:#7950bc}.nk-fsrs-medallion svg{width:22px;height:22px}.nk-fsrs-recall-label>span:last-child{border-left:1px solid #dfd6ed;padding-left:8px;display:grid;gap:3px}.nk-fsrs-recall-label strong{font-size:11px;font-weight:800;white-space:nowrap}.nk-fsrs-recall-label small{font-size:9px;color:#797086;white-space:nowrap}
.nk-session-footer .nk-fsrs-rating .nk-fsrs-pill{min-height:44px!important;padding:0 4px!important;border:1px solid #e8e1f1!important;border-radius:14px!important;background:#fff!important;color:#30263f!important;font-size:12px!important;box-shadow:0 2px 5px #412d6310}
.nk-session-footer .nk-fsrs-rating .nk-fsrs-pill.is-default{background:#6941bd!important;color:#fff!important;border-color:#6941bd!important;box-shadow:0 3px 9px #6941bd40}.nk-fsrs-pill:focus-visible{outline:3px solid #ab89e8;outline-offset:2px}
body:has(.nk-fsrs-docked) .nk-v114-session.is-practice{padding-bottom:86px}
@media(prefers-reduced-motion:reduce){.nk-fsrs-rating,.nk-fsrs-rating::before{animation:none!important;transition:none!important}}
.nk-fsrs-settings{display:grid;gap:12px}.nk-fsrs-settings label{display:flex;align-items:center;justify-content:space-between;gap:10px;font-size:12px;font-weight:750}.nk-fsrs-settings input{width:92px;min-height:42px;padding:0 9px;border:1px solid var(--line);border-radius:10px}.nk-fsrs-customization>summary{min-height:68px;padding:12px 14px;border:1px solid var(--line);border-radius:14px;background:#fff;display:flex;align-items:center;justify-content:space-between;list-style:none;cursor:pointer}.nk-fsrs-customization>summary b,.nk-fsrs-customization>summary small{display:block}.nk-fsrs-customization>summary small{margin-top:4px;color:var(--muted);font-size:10px}.nk-fsrs-customization[open]>summary{border-radius:14px 14px 0 0}.nk-fsrs-customization[open] .nk-fsrs-settings{border-radius:0 0 14px 14px}.nk-fsrs-save-actions{display:grid;grid-template-columns:1.3fr 1fr;gap:9px}.nk-fsrs-warning{padding:10px;border-radius:10px;background:#fff4dd;color:#835400;font-size:11px}.nk-fsrs-breakdown{padding:12px;border-radius:12px;background:#f5f7fb;font-size:11px;line-height:1.6}.modal label{display:grid;gap:6px;font-size:11px;font-weight:800}.modal select{min-height:44px;border:1px solid var(--line);border-radius:11px;padding:0 10px;background:#fff}

.nk-fsrs-settings-entry{width:100%;display:grid;grid-template-columns:48px 1fr 20px;align-items:center;gap:14px;text-align:left;border:1px solid #e2d9f5;border-radius:20px;padding:20px;background:#f7f2ff;color:#322544;box-shadow:0 6px 24px #8965ba18;margin:18px 0}
.nk-fsrs-settings-entry strong,.nk-fsrs-settings-entry small{display:block}.nk-fsrs-settings-entry strong{font-size:16px}.nk-fsrs-settings-entry small{font-size:12px;line-height:1.5;color:#80728f;margin-top:5px}
.nk-fsrs-settings-mark{display:grid;place-items:center;width:48px;height:48px;background:#e9dcff;color:#7650b8;border-radius:16px;box-shadow:0 0 22px #c2a5f34a}
.nk-fsrs-settings{display:block;max-width:740px;margin:auto;padding-bottom:145px;--line:#e5ddef}
.nk-fsrs-settings-hero{padding:22px 4px 28px}.nk-fsrs-settings-hero .nk-fsrs-settings-mark{margin-bottom:20px;width:56px;height:56px;border-radius:19px}.nk-fsrs-settings-hero h1{font-size:30px;letter-spacing:-.8px;margin:8px 0;color:#2b1c40}.nk-fsrs-settings-hero p{color:#857492;font-size:14px;line-height:1.5;max-width:300px}
.nk-fsrs-settings-section{border:1px solid #e9e0f3;background:#fff;border-radius:20px;overflow:hidden;margin-bottom:18px;box-shadow:0 5px 22px #6e48830a}
.nk-fsrs-settings-section>header{display:flex;align-items:center;gap:12px;padding:18px;background:#faf7ff}.nk-fsrs-settings-section>header>span{color:#b09acb;font-size:12px;font-weight:800}.nk-fsrs-settings-section h2{font-size:17px;margin:0;color:#3b294f}.nk-fsrs-settings-section header p{margin:4px 0 0;font-size:12px;color:#9684a5}
.nk-fsrs-settings label.nk-fsrs-field{display:grid;grid-template-columns:minmax(0,1fr) 86px;gap:18px;padding:20px 18px;border-top:1px solid #f0eaf6;align-items:start;font-weight:400}
.nk-fsrs-field strong{display:block;font-size:14px;line-height:1.4;color:#42334f}.nk-fsrs-field small{display:block;font-size:12px;line-height:1.55;color:#8a7b97;margin-top:6px}.nk-fsrs-field em{display:block;font-size:10px;color:#9886aa;font-style:normal;margin-top:8px}
.nk-fsrs-value input{width:86px!important;min-height:49px!important;text-align:center;font-size:19px;font-weight:650;color:#67459a;background:#faf7ff;border-color:#d9c9ef!important;border-radius:13px!important}.nk-fsrs-value b{display:block;text-align:center;font-size:10px;color:#9b89aa;font-weight:500;margin-top:5px}
.nk-fsrs-settings-note{font-size:12px;line-height:1.6;color:#8d7a9d;padding:0 5px}.nk-fsrs-settings-save{position:fixed;z-index:90;bottom:calc(86px + env(safe-area-inset-bottom));left:14px;right:14px;max-width:712px;margin:auto;background:#f7f2fff5;border:1px solid #fff;border-radius:19px;padding:12px 14px;box-shadow:0 4px 28px #79579d30;backdrop-filter:blur(12px)}
.nk-fsrs-settings-save>small{display:block;text-align:center;color:#9a7cad;font-size:10px;margin-bottom:9px}.nk-fsrs-settings-save>div{display:grid;grid-template-columns:1fr 1.5fr;gap:10px}.nk-fsrs-settings-save button{min-height:46px;border-radius:13px!important}.nk-fsrs-settings-save .primary-btn{background:#7952b4!important}.nk-fsrs-leave-actions{display:grid;gap:10px}.nk-fsrs-settings .nk-fsrs-warning{margin:12px 18px}
body:has(.nk-fsrs-settings){background:#f7f4fc!important}
@media(min-width:768px) and (min-height:600px){.nk-fsrs-settings-save{left:104px;right:16px;bottom:22px}}
</style>'''


def transform(source: str) -> str:
    if "else if(route.page==='fsrs-settings')" not in source:
        source=source.replace("else if(route.page==='more') out=morePage();", "else if(route.page==='fsrs-settings') out=nkFsrsSettingsMarkup();\n    else if(route.page==='more') out=morePage();",1)
        source=source.replace("function render() {", "function render() {\n    if(nkFsrsGuardRoute()) return;",1)
    extra="nkFsrsEditSetting,nkFsrsCancelSettings,nkFsrsLeaveSettings,"
    if extra not in source:
        source=source.replace("window.QB={", "window.QB={"+extra,1)
    if "NK_FSRS_V6_START" in source:
        start = source.index("  /* NK_FSRS_V6_START")
        end_marker = "  /* NK_FSRS_V6_END */"
        end = source.index(end_marker, start) + len(end_marker)
        source = source[:start] + CORE.read_text(encoding="utf-8").rstrip() + source[end:]
        source = re.sub(r'<style id="nk-fsrs-v1">.*?</style>', lambda _: CSS, source, count=1, flags=re.S)
        source = source.replace("nkFsrsSetPreference,nkFsrsUndo,", "nkFsrsSetPreference,nkFsrsSaveSettings,nkFsrsUndo,", 1)
        print("FSRS scheduler already installed; core and recall-dock CSS refreshed")
        return source
    script = '<script src="vendor/ts-fsrs/ts-fsrs-5.4.2.umd.js"></script>'
    if "</head>" not in source:
        raise SystemExit("head anchor missing")
    source = source.replace("</head>", script + "\n" + CSS + "\n</head>", 1)
    anchor = "  window.QB={"
    if source.count(anchor) != 1:
        raise SystemExit(f"QB export anchor count: {source.count(anchor)}")
    source = source.replace(anchor, CORE.read_text(encoding="utf-8") + "\n" + anchor, 1)
    cloud_boot = "  render();\n  nkCloudInit();\n})();"
    plain_boot = "  render();\n})();"
    if cloud_boot in source:
        source = source.replace(cloud_boot, "  nkFsrsInit();\n  render();\n  nkCloudInit();\n})();", 1)
    elif plain_boot in source:
        source = source.replace(plain_boot, "  nkFsrsInit();\n  render();\n})();", 1)
    else:
        raise SystemExit("boot anchor missing")
    additions = "nkRateCurrent,nkStartTodaysReview,nkFsrsQueueDialog,nkFsrsTopicOptions,nkFsrsSetPreference,nkFsrsSaveSettings,nkFsrsUndo,"
    export_end = "nkCloudAuthenticate,nkCloudSignOut,nkCloudSyncNow,"
    if export_end in source:
        source = source.replace(export_end, export_end + additions, 1)
    else:
        source = source.replace("  window.QB={", "  window.QB={" + additions, 1)
    required = ["NK_FSRS_V6_START", script, "nkFsrsInit();", "nkRateCurrent,nkStartTodaysReview"]
    missing = [item for item in required if item not in source]
    if missing:
        raise SystemExit(f"FSRS markers missing: {missing}")
    return source


def main() -> None:
    source = HTML.read_text(encoding="utf-8")
    if "--remove-source-layer" in sys.argv:
        source = re.sub(r"  /\* NK_FSRS_V6_START.*?/\* NK_FSRS_V6_END \*/\s*", "", source, flags=re.S)
        source = re.sub(r'<style id="nk-fsrs-v1">.*?</style>\s*', "", source, flags=re.S)
        source = source.replace('<script src="vendor/ts-fsrs/ts-fsrs-5.4.2.umd.js"></script>\n', "")
        source = source.replace("  nkFsrsInit();\n", "")
        source = source.replace("nkRateCurrent,nkStartTodaysReview,nkFsrsQueueDialog,nkFsrsTopicOptions,nkFsrsSetPreference,nkFsrsSaveSettings,nkFsrsUndo,", "")
        source = source.replace("\nwindow.QB={", "\n  window.QB={")
        HTML.write_text(source, encoding="utf-8")
        return
    HTML.write_text(transform(source), encoding="utf-8")
    print("FSRS_V1_OK: offline FSRS 6 scheduler, migration, ratings, queue, forecast and settings installed")


if __name__ == "__main__":
    main()
