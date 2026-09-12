#!/usr/bin/env python3
'''Install durable Practice pause/resume with one final Pause/Submit review grid.'''

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"
CORE = ROOT / "tools/continue_practice_resume_core.js"
FLOW_CORE = ROOT / "tools/practice_single_review_grid_core.js"
STYLE_ID = "nk-continue-practice-resume-v1"
START = "/* NK_CONTINUE_PRACTICE_RESUME_V1_START */"
END = "/* NK_CONTINUE_PRACTICE_RESUME_V1_END */"
FLOW_START = "/* NK_PRACTICE_SINGLE_REVIEW_GRID_V1_START */"
FLOW_END = "/* NK_PRACTICE_SINGLE_REVIEW_GRID_V1_END */"

CSS = r'''<style id="nk-continue-practice-resume-v1">
#nk-session-review.nk-practice-final-review .nk-session-review-actions{
  display:grid!important;
  grid-template-columns:repeat(2,minmax(0,1fr))!important;
  gap:12px!important;
}
#nk-session-review.nk-practice-final-review .nk-session-review-actions .nk-practice-pause,
#nk-session-review.nk-practice-final-review .nk-session-review-actions .nk-practice-submit{
  width:100%!important;
  min-height:52px!important;
  grid-column:auto!important;
  border:0!important;
  border-radius:16px!important;
  background:linear-gradient(135deg,#5153e8 0%,#7354ff 100%)!important;
  color:#fff!important;
  font-weight:800!important;
}
body:has(#nk-session-review.nk-practice-final-review) .nk-session-footer{
  display:none!important;
}
@media(max-width:420px){
  #nk-session-review.nk-practice-final-review .nk-session-review-actions{gap:10px!important}
  #nk-session-review.nk-practice-final-review .nk-session-review-actions .nk-practice-pause,
  #nk-session-review.nk-practice-final-review .nk-session-review-actions .nk-practice-submit{
    min-height:50px!important;
  }
}
</style>'''


def transform(source: str) -> str:
    source = re.sub(rf"\s*{re.escape(START)}.*?{re.escape(END)}\s*", "\n", source, flags=re.S)
    source = re.sub(rf"\s*{re.escape(FLOW_START)}.*?{re.escape(FLOW_END)}\s*", "\n", source, flags=re.S)
    source = re.sub(rf'<style id="{STYLE_ID}">.*?</style>\s*', '', source, flags=re.S)

    # Do not restore the obsolete mutation observer that hid every Practice Submit
    # control; Submit is valid in the single final review grid.
    source = re.sub(r'<style id="v102-practice-layer">.*?</style>\s*', '', source, flags=re.S)
    source = re.sub(r'<script id="v102-practice-layer-script">.*?</script>\s*', '', source, flags=re.S)

    anchor = "/* NK_HOME_FLOW_V3_END */"
    if source.count(anchor) != 1:
        raise SystemExit(f"Expected one Home V3 flow anchor, found {source.count(anchor)}")

    core = CORE.read_text(encoding="utf-8").strip()
    flow_core = FLOW_CORE.read_text(encoding="utf-8").strip()
    source = source.replace(anchor, anchor + "\n" + core + "\n" + flow_core, 1)

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
    print("CONTINUE_PRACTICE_RESUME_OK pause_resume=true single_final_grid=true footer=previous_next")


if __name__ == "__main__":
    main()
