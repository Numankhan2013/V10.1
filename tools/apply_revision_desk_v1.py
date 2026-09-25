#!/usr/bin/env python3
"""Add one all-bank revision entry to More and its four existing study queues."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"
CORE = ROOT / "tools/revision_desk_core.js"
MARKER = "NK_REVISION_DESK_V1_START"

CSS = """<style id="nk-revision-desk-v1">
.nk-revision-desk{padding-bottom:24px}
.nk-revision-scope{display:flex;align-items:center;gap:7px;margin:0 0 14px;color:#586a90;font-size:12px;font-weight:800}
.nk-revision-scope span{color:#9ba5ba}
.nk-revision-list{display:grid;gap:11px}
.nk-revision-card{padding:14px;border:1px solid #dce3ef;border-radius:14px;background:#fff;color:#17204b}
.nk-revision-card-head{display:grid;grid-template-columns:38px 1fr auto;align-items:center;gap:11px}
.nk-revision-icon{width:38px;height:38px;display:grid;place-items:center;border-radius:11px;background:#f0f3fb;color:#3658ad}
.nk-revision-card-copy{display:grid;gap:3px}
.nk-revision-card-copy strong{font-size:14px}
.nk-revision-card-copy small{color:#697592;font-size:11px;line-height:1.4}
.nk-revision-card-head>b{color:#263861;font-size:17px;font-variant-numeric:tabular-nums}
.nk-revision-detail{margin:8px 0 0 49px;color:#697592;font-size:11px;line-height:1.45}
.nk-revision-actions{display:flex;gap:7px;margin-top:9px}
.nk-revision-actions>button{min-height:44px;display:flex;justify-content:space-between;align-items:center;padding:0 11px;border:0;border-radius:10px;background:#f4f6fc;color:#3658ad;font:inherit;font-size:12px;font-weight:800;text-align:left}
.nk-revision-actions>button:first-child{flex:1}
.nk-revision-actions>button.nk-revision-view-all{justify-content:center;background:transparent;color:#617095}
.nk-revision-actions>button:disabled{background:#f7f8fb;color:#8b93a6}
.nk-revision-actions>button:focus-visible{outline:3px solid #8ca3ed;outline-offset:2px}
.nk-revision-search{display:flex;align-items:center;gap:8px;min-height:48px;padding:0 12px;border:1px solid #dce3ef;border-radius:12px;background:#fff;color:#647394}
.nk-revision-search input{width:100%;border:0;background:transparent;color:#17204b;font:inherit;font-size:14px;outline:0}
.nk-revision-browse-list{display:grid;gap:10px;margin-top:14px}
.nk-revision-item{padding:14px;border:1px solid #dce3ef;border-radius:13px;background:#fff}
.nk-revision-item[hidden],.nk-revision-no-match[hidden]{display:none}
.nk-revision-item small{color:#526893;font-size:11px;font-weight:800;line-height:1.4}
.nk-revision-item p{margin:8px 0;font-size:13px;font-weight:700;line-height:1.45}
.nk-revision-item button{width:100%;min-height:44px;display:flex;justify-content:space-between;align-items:center;border:0;border-radius:9px;background:#f4f6fc;color:#3658ad;font:inherit;font-size:12px;font-weight:800}
.nk-revision-item button:focus-visible{outline:3px solid #8ca3ed;outline-offset:2px}
.nk-revision-no-match{padding:18px;text-align:center;color:#697592;font-size:13px}
</style>"""

OLD_MORE_ROWS = """${row('refresh','Wrong questions',`${fmtNum(wrong)} missed · retrieval practice`,\"window.QB.nav('wrong')\",'is-red')}${row('bookmark','Bookmarks',`${fmtNum(bm)} saved by you`,\"window.QB.nav('bookmarks')\",'is-violet')}${row('book','My notes',`${fmtNum(nkSavedQuestionNotes().length)} recall cues`,\"window.QB.nav('notes')\")}"""
NEW_MORE_ROWS = """${row('refresh','Quick revision','Mistakes · bookmarks · unseen · due',\"window.QB.nav('quick-revision')\")}${row('book','My notes',`${fmtNum(nkSavedQuestionNotes().length)} recall cues`,\"window.QB.nav('notes')\")}"""


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return source.replace(old, new, 1)


def transform(source: str) -> str:
    if MARKER in source:
        return source
    if "NK_QUESTION_NOTES_V1_START" not in source:
        raise SystemExit("Revision Desk must run after personal question notes")
    source = replace_once(source, "</head>", CSS + "\n</head>", "revision styles")
    source = replace_once(source, "const bm=bookmarkedQuestions().length,wrong=wrongQuestions().length;",
                          "", "remove redundant More counts")
    source = replace_once(source, "else if(route.page==='notes') out=nkNotesPage();",
                          "else if(route.page==='quick-revision') out=nkRevisionDeskPage();\n    else if(route.page==='revision-browse') out=nkRevisionBrowsePage(route.id);\n    else if(route.page==='notes') out=nkNotesPage();",
                          "revision route")
    source = replace_once(source, OLD_MORE_ROWS, NEW_MORE_ROWS, "More revision entry")
    bridge = "  window.QB={nkFilterNotes,nkOpenNotedQuestion,"
    source = replace_once(source, bridge,
                          CORE.read_text(encoding="utf-8").rstrip() + "\n\n  window.QB={nkFilterNotes,nkOpenNotedQuestion,nkStartRevisionQueue,nkFilterRevisionBrowse,nkOpenRevisionQuestion,",
                          "revision core and action")
    return source


if __name__ == "__main__":
    HTML.write_text(transform(HTML.read_text(encoding="utf-8")), encoding="utf-8")
    print("REVISION_DESK_INSTALLED: mistakes/bookmarks/unseen/due across all subjects and banks")
