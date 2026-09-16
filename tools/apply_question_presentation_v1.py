#!/usr/bin/env python3
"""Install shared question schema normalization and semantic matching tables."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"
CORE = ROOT / "tools/question_presentation_core.js"
START = "  /* NK_QUESTION_PRESENTATION_V1_START"
END = "  /* NK_QUESTION_PRESENTATION_V1_END */"

CSS = r'''<style id="nk-question-presentation-v1">
.nk-sci-sub,.nk-sci-sup{position:relative;font-size:.72em;line-height:0;vertical-align:baseline}.nk-sci-sup{top:-.48em}.nk-sci-sub{bottom:-.16em}
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

    rich_before = """  function richText(text) {
    return esc(String(text||'')).replace(/\\*\\*(.*?)\\*\\*/g,'<strong>$1</strong>');
  }"""
    rich_after = """  function richText(text) {
    return nkScientificMarkup(text).replace(/\\*\\*(.*?)\\*\\*/g,'<strong>$1</strong>');
  }"""
    if rich_before in source:
        if source.count(rich_before) != 1:
            raise SystemExit(f"Expected one shared rich-text renderer, found {source.count(rich_before)}")
        source = source.replace(rich_before, rich_after, 1)
    elif rich_after not in source:
        raise SystemExit("Shared explanation renderer is not wired into scientific notation")

    # All answer-choice paths, including the locked timed-CBT branch, use the
    # same safe formatter. This replacement is intentionally presentation-only.
    option_before = "${esc(o.text)}"
    option_after = "${nkScientificMarkup(o.text)}"
    option_count = source.count(option_before)
    if option_count:
        source = source.replace(option_before, option_after)
    elif option_after not in source:
        raise SystemExit("No learner answer-choice renderer was found")

    takeaway_before = "${esc(takeaway)}"
    takeaway_after = "${nkScientificMarkup(takeaway)}"
    if takeaway_before in source:
        source = source.replace(takeaway_before, takeaway_after)

    # Enhanced Marrow explanations have a separate presentation wrapper. Keep
    # its emphasis hierarchy, but route text and distractor rationales through
    # the exact same notation and escaping boundary.
    marrow_replacements = (
        ("let html=esc(String(text||''));", "let html=nkScientificMarkup(text);"),
        ("'<strong>'+esc(o.text||'')+'</strong>", "'<strong>'+nkScientificMarkup(o.text||'')+'</strong>"),
        ("esc(reason)", "nkScientificMarkup(reason)"),
    )
    for before, after in marrow_replacements:
        if before in source:
            source = source.replace(before, after)

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


if __name__ == "__main__":
    main()
