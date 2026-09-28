#!/usr/bin/env python3
"""Add all-bank question and ID search using the existing Practice engine."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"
CORE = ROOT / "tools/question_search_core.js"
MARKER = "NK_QUESTION_SEARCH_V1_START"
NOTES_ROW = "${row('book','My notes',`${fmtNum(nkSavedQuestionNotes().length)} recall cues`,\"window.QB.nav('notes')\",'is-violet')}"
SEARCH_ROW = "${row('search','Find a question','Search every subject and bank',\"window.QB.nav('question-search')\",'is-blue')}"

CSS = '''<style id="nk-question-search-v1">
.nk-question-search{padding-bottom:28px}
.nk-question-search-box{display:flex;align-items:center;gap:10px;min-height:54px;margin:14px 0 11px;padding:0 15px;border:1px solid #d7dfea;border-radius:13px;background:#fff;color:#647394}
.nk-question-search-box:focus-within{border-color:#6178c8;box-shadow:0 0 0 3px #e8edff}
.nk-question-search-box>span{font-size:21px;line-height:1}
.nk-question-search-box input{min-width:0;flex:1;height:50px;border:0;outline:0;background:transparent;color:#1f2d59;font:inherit;font-size:15px}
.nk-question-search-filters{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:9px;margin-bottom:15px}
.nk-question-search-filters label{min-width:0;color:#52617e;font-size:11px;font-weight:800}
.nk-question-search-filters select{display:block;width:100%;height:45px;margin-top:5px;padding:0 10px;border:1px solid #dbe2ed;border-radius:10px;background:#fff;color:#21315b;font:inherit;font-size:12px}
.nk-question-search-summary{display:flex;align-items:center;justify-content:space-between;gap:10px;margin:0 0 11px;color:#61708b;font-size:12px;font-weight:700}
.nk-question-search-summary button{min-height:44px;padding:0 13px;border:0;border-radius:10px;background:#405db9;color:#fff;font:inherit;font-size:12px;font-weight:800;cursor:pointer}
.nk-question-search-list{display:grid;gap:10px}
.nk-question-search-item{padding:15px;border:1px solid #dfe5ef;border-radius:14px;background:#fff;color:#1d2c55}
.nk-question-search-meta{color:#526992;font-size:11px;font-weight:800;line-height:1.5;overflow-wrap:anywhere}
.nk-question-search-item p{display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:3;overflow:hidden;margin:8px 0 12px;font-size:14px;font-weight:700;line-height:1.45;overflow-wrap:anywhere}
.nk-question-search-bottom{display:flex;align-items:center;justify-content:space-between;gap:12px}
.nk-question-search-id{min-width:0;color:#697890;font-size:11px;line-height:1.4;overflow-wrap:anywhere}
.nk-question-search-bottom button{flex:none;min-height:44px;padding:0 12px;border:1px solid #dce4f4;border-radius:9px;background:#f5f7fd;color:#3e58a8;font:inherit;font-size:12px;font-weight:800;cursor:pointer}
.nk-question-search-empty{padding:25px 18px;border:1px solid #e2e8f2;border-radius:14px;background:#fff;color:#61708a;font-size:13px;line-height:1.6}
.nk-question-search-more{display:block;width:100%;min-height:48px;margin-top:12px;border:1px solid #d9e1f0;border-radius:11px;background:#f8faff;color:#405ba8;font:inherit;font-size:12px;font-weight:800;cursor:pointer}
.nk-question-search button:focus-visible,.nk-question-search select:focus-visible{outline:3px solid #9db1ed;outline-offset:2px}
@media(max-width:620px){.nk-question-search-filters{grid-template-columns:repeat(2,minmax(0,1fr))}.nk-question-search-filters label:last-child{grid-column:1/-1}.nk-question-search-summary{align-items:flex-start;flex-direction:column}.nk-question-search-summary button{width:100%}}
@media(max-width:365px){.nk-question-search-bottom{align-items:flex-start;flex-direction:column}.nk-question-search-bottom button{width:100%}}
</style>'''


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return source.replace(old, new, 1)


def transform(source: str) -> str:
    if MARKER in source:
        return source
    if "NK_QBANK_COVERAGE_V1_START" not in source or "NK_REVISION_DESK_V1_START" not in source:
        raise SystemExit("Question search must follow the shared bank and revision transforms")
    source = replace_once(source, "</head>", CSS + "\n</head>", "question search styles")
    source = replace_once(source, "else if(route.page==='quick-revision') out=nkRevisionDeskPage();",
                          "else if(route.page==='question-search') out=nkQuestionSearchPage();\n    else if(route.page==='quick-revision') out=nkRevisionDeskPage();",
                          "question search route")
    source = replace_once(source, NOTES_ROW, NOTES_ROW + SEARCH_ROW, "More question search action")
    source = replace_once(source, "  window.QB={", CORE.read_text(encoding="utf-8").rstrip() +
                          "\n\n  window.QB={nkQuestionSearchQuery,nkQuestionSearchSetFilter,nkQuestionSearchMore,nkQuestionSearchOpen,nkQuestionSearchPracticeMatches,",
                          "question search core and actions")
    return source


if __name__ == "__main__":
    HTML.write_text(transform(HTML.read_text(encoding="utf-8")), encoding="utf-8")
    print("QUESTION_SEARCH_INSTALLED: all-bank ID/text search and Practice entry")
