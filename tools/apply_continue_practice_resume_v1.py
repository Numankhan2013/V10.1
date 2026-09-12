#!/usr/bin/env python3
"""Install durable Pause/Submit and same-session Continue Practice behavior."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"
CORE = ROOT / "tools/continue_practice_resume_core.js"
STYLE_ID = "nk-continue-practice-resume-v1"
START = "/* NK_CONTINUE_PRACTICE_RESUME_V1_START */"
END = "/* NK_CONTINUE_PRACTICE_RESUME_V1_END */"

CSS = r'''<style id="nk-continue-practice-resume-v1">
.nk-practice-session-controls{width:min(100%,760px);margin:0 auto 8px;display:grid;grid-template-columns:1fr 1fr;gap:10px}
.nk-session-footer .nk-practice-session-controls button{min-height:46px!important}
.nk-session-footer .nk-practice-pause{border:1px solid #cfd5e1!important;background:#fff!important;color:#1b2452!important}
.nk-session-footer .nk-practice-submit{border:0!important;background:var(--nk-indigo,#29265f)!important;color:#fff!important}
.qbank-session-page:has(.nk-practice-session-controls){padding-bottom:calc(166px + env(safe-area-inset-bottom))!important}
.qbank-session-page:has(.nk-practice-session-controls):has(.nk-fsrs-rating){padding-bottom:calc(246px + env(safe-area-inset-bottom))!important}
.nk-session-review-actions:has(.nk-practice-pause){grid-template-columns:repeat(2,minmax(0,1fr))}
.nk-session-review-actions:has(.nk-practice-pause) .nk-practice-submit,.nk-session-review-actions:has(.nk-practice-pause) .nk-practice-pause{min-height:48px}
@media(max-width:420px){.nk-practice-session-controls{gap:8px}.nk-session-footer .nk-practice-session-controls button{min-height:44px!important}.qbank-session-page:has(.nk-practice-session-controls){padding-bottom:calc(160px + env(safe-area-inset-bottom))!important}.qbank-session-page:has(.nk-practice-session-controls):has(.nk-fsrs-rating){padding-bottom:calc(240px + env(safe-area-inset-bottom))!important}}
</style>'''


def transform(source: str) -> str:
    source = re.sub(rf"\s*{re.escape(START)}.*?{re.escape(END)}\s*", "\n", source, flags=re.S)
    source = re.sub(rf'<style id="{STYLE_ID}">.*?</style>\s*', '', source, flags=re.S)
    # This legacy mutation observer hid every Practice button whose visible label
    # was Submit. The approved session contract now requires that control.
    source = re.sub(r'<style id="v102-practice-layer">.*?</style>\s*', '', source, flags=re.S)
    source = re.sub(r'<script id="v102-practice-layer-script">.*?</script>\s*', '', source, flags=re.S)
    anchor = "/* NK_HOME_FLOW_V3_END */"
    if source.count(anchor) != 1:
        raise SystemExit(f"Expected one Home V3 flow anchor, found {source.count(anchor)}")
    core = CORE.read_text(encoding="utf-8").strip()
    source = source.replace(anchor, anchor + "\n" + core, 1)
    if "</head>" not in source:
        raise SystemExit("HTML head anchor missing")
    source = source.replace("</head>", CSS + "\n</head>", 1)
    exports = "nkPausePractice,nkSubmitPracticeSession,"
    if exports not in source:
        qb = "window.QB={"
        if source.count(qb) != 1:
            raise SystemExit(f"Expected one QB export object, found {source.count(qb)}")
        source = source.replace(qb, qb + exports, 1)
    return source


def main() -> None:
    HTML.write_text(transform(HTML.read_text(encoding="utf-8")), encoding="utf-8")
    print("CONTINUE_PRACTICE_RESUME_OK pause_resume=true completed_next_topic=true")


if __name__ == "__main__":
    main()
