#!/usr/bin/env python3
"""Install the pinned offline FSRS v6 scheduler after sync integration."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"
CORE = ROOT / "tools/fsrs_scheduler_core.js"

CSS = r'''<style id="nk-fsrs-v1">
.nk-fsrs-today{display:grid;gap:14px;margin:14px 0}.nk-fsrs-counts{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.nk-fsrs-counts b{display:grid;gap:3px;padding:11px;border-radius:13px;background:#f5f7fb;font-size:22px}.nk-fsrs-counts small{font-size:10px;color:var(--muted);text-transform:uppercase}.nk-fsrs-forecast{height:62px;display:flex;align-items:end;gap:9px}.nk-fsrs-forecast span{height:100%;flex:1;display:flex;flex-direction:column;align-items:center;justify-content:end;gap:4px}.nk-fsrs-forecast i{display:block;width:100%;max-width:32px;border-radius:6px 6px 2px 2px;background:var(--primary)}.nk-fsrs-forecast small{font-size:9px;color:var(--muted)}.nk-fsrs-rating{margin:16px 0;padding:13px;border:1px solid var(--line);border-radius:15px;display:grid;grid-template-columns:1fr repeat(3,minmax(65px,auto));gap:8px;align-items:center}.nk-fsrs-rating>span{font-size:12px;font-weight:800}.nk-fsrs-rating button{min-height:48px;border:1px solid var(--line);border-radius:11px;background:#fff;display:grid;place-items:center}.nk-fsrs-rating button.is-default{border-color:var(--primary);background:rgba(63,207,232,.09)}.nk-fsrs-rating small{font-size:9px;color:var(--muted)}.nk-fsrs-settings{display:grid;gap:12px}.nk-fsrs-settings label{display:flex;align-items:center;justify-content:space-between;gap:10px;font-size:12px;font-weight:750}.nk-fsrs-settings input{width:92px;min-height:42px;padding:0 9px;border:1px solid var(--line);border-radius:10px}.nk-fsrs-warning{padding:10px;border-radius:10px;background:#fff4dd;color:#835400;font-size:11px}.nk-fsrs-breakdown{padding:12px;border-radius:12px;background:#f5f7fb;font-size:11px;line-height:1.6}.modal label{display:grid;gap:6px;font-size:11px;font-weight:800}.modal select{min-height:44px;border:1px solid var(--line);border-radius:11px;padding:0 10px;background:#fff}@media(max-width:640px){.nk-fsrs-rating{grid-template-columns:repeat(3,1fr)}.nk-fsrs-rating>span{grid-column:1/-1}}
</style>'''


def transform(source: str) -> str:
    if "NK_FSRS_V6_START" in source:
        start = source.index("  /* NK_FSRS_V6_START")
        end_marker = "  /* NK_FSRS_V6_END */"
        end = source.index(end_marker, start) + len(end_marker)
        source = source[:start] + CORE.read_text(encoding="utf-8").rstrip() + source[end:]
        print("FSRS scheduler already installed; core refreshed")
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
    additions = "nkRateCurrent,nkStartTodaysReview,nkFsrsQueueDialog,nkFsrsTopicOptions,nkFsrsSetPreference,nkFsrsUndo,"
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
        source = source.replace("nkRateCurrent,nkStartTodaysReview,nkFsrsQueueDialog,nkFsrsTopicOptions,nkFsrsSetPreference,nkFsrsUndo,", "")
        source = source.replace("\nwindow.QB={", "\n  window.QB={")
        HTML.write_text(source, encoding="utf-8")
        return
    HTML.write_text(transform(source), encoding="utf-8")
    print("FSRS_V1_OK: offline FSRS 6 scheduler, migration, ratings, queue, forecast and settings installed")


if __name__ == "__main__":
    main()
