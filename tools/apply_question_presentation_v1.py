#!/usr/bin/env python3
"""Install shared question schema normalization and semantic matching tables."""

from pathlib import Path
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"
CORE = ROOT / "tools/question_presentation_core.js"
START = "  /* NK_QUESTION_PRESENTATION_V1_START"
END = "  /* NK_QUESTION_PRESENTATION_V1_END */"

CSS = r'''<style id="nk-question-presentation-v1">
.nk-question-prompt{display:block}.nk-match-table-scroll{max-width:100%;margin:16px 0 4px;overflow-x:auto;border:1px solid #dce3ee;border-radius:13px;background:#fff}.nk-match-table{width:100%;min-width:420px;border-collapse:collapse;font-size:14px;line-height:1.42;font-weight:520;color:#202849}.nk-match-table th{padding:9px 12px;background:#f3f6fb;color:#59647d;font-size:11px;font-weight:850;letter-spacing:.7px;text-align:left;text-transform:uppercase}.nk-match-table td{width:50%;padding:11px 12px;border-top:1px solid #e5e9f0;vertical-align:top}.nk-match-table td+td{border-left:1px solid #e5e9f0}.nk-match-table td b{display:inline-grid;place-items:center;min-width:24px;height:24px;margin-right:7px;padding:0 5px;border-radius:7px;background:#eef2f8;color:#34405d;font-size:11px}.nk-match-table td span{font-weight:560}.nk-question-unavailable{display:grid;gap:3px;margin:14px 0 0;padding:12px 13px;border:1px solid #efd6a4;border-radius:12px;background:#fff8e8;color:#704d12;font-size:12px;line-height:1.45}.nk-question-unavailable strong{font-size:13px}.nk-question-unavailable span{font-weight:500}.nk-v114-session .question-text:has(.nk-match-table){font-size:19px!important}.nk-v114-session .question-text:has(.nk-match-table) .nk-question-prompt{font-size:21px;line-height:1.4;font-weight:720}
@media(max-width:520px){.nk-match-table{min-width:360px;font-size:13px}.nk-match-table th,.nk-match-table td{padding:9px}.nk-v114-session .question-text:has(.nk-match-table) .nk-question-prompt{font-size:20px}}
</style>'''


def transform(source: str) -> str:
    core = CORE.read_text(encoding="utf-8").rstrip()
    if START in source:
        start = source.index(START)
        end = source.index(END, start) + len(END)
        source = source[:start] + core + source[end:]
    else:
        anchor = "  window.QB={"
        if source.count(anchor) != 1:
            raise SystemExit(f"QB export anchor count: {source.count(anchor)}")
        source = source.replace(anchor, core + "\n\n" + anchor, 1)

    source = re.sub(r'<style id="nk-question-presentation-v1">.*?</style>', CSS, source, count=1, flags=re.S)
    if 'id="nk-question-presentation-v1"' not in source:
        if source.count("</head>") != 1:
            raise SystemExit("head anchor count is not one")
        source = source.replace("</head>", CSS + "\n</head>", 1)

    pattern = re.compile(r'(<div class="question-text"[^>]*>)\$\{esc\(q\.question\)\}(</div>)')
    source, count = pattern.subn(r'\1${nkQuestionStemMarkup(q)}\2', source)
    if count not in (0, 3):
        raise SystemExit(f"Expected zero refreshed or three question renderer call sites, found {count}")
    if source.count("${nkQuestionStemMarkup(q)}") < 3:
        raise SystemExit("Shared question markup is not wired into Practice, CBT, and Review")

    options_anchor = "function nkSessionOptions(q,selected,mode,submitted) {\n    const locked="
    options_replacement = "function nkSessionOptions(q,selected,mode,submitted) {\n    const presentation=nkQuestionPresentationFor(q);if(!presentation.valid)return '';\n    const locked="
    if options_anchor in source:
        if source.count(options_anchor) != 1:
            raise SystemExit(f"Session option renderer anchor count: {source.count(options_anchor)}")
        source = source.replace(options_anchor, options_replacement, 1)
    elif "const presentation=nkQuestionPresentationFor(q);if(!presentation.valid)return '';" not in source:
        raise SystemExit("Shared option validation is not wired into the session renderer")
    return source


def main() -> None:
    source = HTML.read_text(encoding="utf-8")
    HTML.write_text(transform(source), encoding="utf-8")
    print("QUESTION_PRESENTATION_OK normalized_choices=true matching_tables=true invalid_fail_closed=true")

    # Keep the community-statistics pilot downstream of the final shared
    # question renderer without adding a second renderer or modifying option
    # correctness classes. Its own build-time matcher fails closed.
    runpy.run_path(str(ROOT / "tools/apply_community_stats_v1.py"), run_name="__main__")
    runpy.run_path(str(ROOT / "tools/test_community_stats_v1.py"), run_name="__main__")


if __name__ == "__main__":
    main()
