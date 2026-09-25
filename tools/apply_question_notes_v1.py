#!/usr/bin/env python3
"""Install one question-linked personal note surface after all question transforms."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"
CORE = ROOT / "tools/question_notes_core.js"

CSS = '''<style id="nk-question-notes-v1">
.nk-question-note{margin:18px 0 8px;border:1px solid #dce3ef;border-radius:14px;background:#fff;overflow:hidden;color:#17204b}
.nk-question-note-head{min-height:58px;display:flex;justify-content:space-between;align-items:center;gap:12px;padding:12px 15px}
.nk-question-note-head>div:first-child{display:grid;gap:3px}
.nk-question-note-head strong{font-size:14px}
.nk-question-note-head small{color:#66708d;font-size:11px}
.nk-note-tools,.nk-question-note-actions>div{display:flex;align-items:center;gap:5px}
.nk-question-note button{min-height:44px;padding:0 11px;border:0;border-radius:9px;background:transparent;color:#3658ad;font-size:12px;font-weight:800;cursor:pointer}
.nk-question-note .nk-note-delete{color:#b83f51}
.nk-question-note .nk-note-save{padding:0 16px;background:#3f63c5;color:#fff}
.nk-question-note button:focus-visible,.nk-notes-page button:focus-visible{outline:3px solid #8ca3ed;outline-offset:2px}
.nk-note-readonly{margin:0 15px 15px;padding:13px 14px;border:1px solid #e1e7f1;border-radius:10px;background:#f8faff;color:#293653;font-size:14px;line-height:1.55;white-space:pre-wrap;overflow-wrap:anywhere}
.nk-question-note-body{padding:0 15px 15px}
.nk-question-note-body label{display:block;margin-bottom:7px;color:#5a6582;font-size:11px;font-weight:800}
.nk-question-note-body textarea{width:100%;min-height:110px;padding:12px;border:1px solid #cfd7e7;border-radius:10px;background:#fff;color:#17204b;font:inherit;font-size:14px;line-height:1.5;resize:vertical}
.nk-question-note-body textarea:focus{outline:3px solid #e7ecff;border-color:#6d82ca}
.nk-question-note-actions{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-top:10px}
.nk-question-note-actions small{color:#697391;font-size:11px}
.nk-notes-page{padding-bottom:24px}
.nk-notes-count{color:#65718b;font-size:12px;font-weight:700;margin:0 0 12px}
.nk-notes-search{display:flex;align-items:center;gap:8px;padding:0 12px;min-height:48px;border:1px solid #dce3ef;border-radius:12px;background:#fff;color:#647394}
.nk-notes-search input{width:100%;border:0;background:transparent;color:#17204b;font:inherit;font-size:14px;outline:0}
.nk-notes-list{display:grid;gap:12px;margin-top:14px}
.nk-notes-item{border:1px solid #dce3ef;border-radius:14px;background:#fff;padding:15px;color:#17204b}
.nk-notes-item[hidden],.nk-notes-no-match[hidden]{display:none}
.nk-notes-item-meta{color:#526893;font-size:11px;font-weight:800;line-height:1.5}
.nk-notes-item-question{margin:8px 0 10px;font-size:13px;line-height:1.45;font-weight:700;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.nk-notes-item-text{padding:11px 12px;border-radius:10px;background:#f8faff;color:#293653;font-size:13px;line-height:1.5;white-space:pre-wrap;overflow-wrap:anywhere}
.nk-notes-item button{width:100%;min-height:44px;margin-top:8px;border:0;background:transparent;color:#3658ad;text-align:right;font:inherit;font-size:12px;font-weight:800}
.nk-notes-item button span{font-size:18px;vertical-align:middle}
.nk-notes-no-match{padding:20px;text-align:center;color:#65718b;font-size:13px}
</style>'''


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return source.replace(old, new, 1)


def transform(source: str) -> str:
    if "NK_QUESTION_NOTES_V1_START" in source:
        return source
    source = replace_once(source, "</head>", CSS + "\n</head>", "notes style")
    source = replace_once(source, "    bookmarks: {},\n    reviews: {},", "    bookmarks: {},\n    questionNotes: {},\n    reviews: {},", "notes default state")
    source = replace_once(source, "  window.QB={", CORE.read_text(encoding="utf-8").rstrip() + "\n\n  window.QB={", "notes core")
    source = replace_once(source, "    app.innerHTML=out;", "    app.innerHTML=out;\n    nkMountQuestionNote();", "notes render hook")
    source = replace_once(source, "else if(route.page==='more') out=morePage();",
                          "else if(route.page==='notes') out=nkNotesPage();\n    else if(route.page==='more') out=morePage();",
                          "notes route")
    modern = "${row('bookmark','Bookmarks',`${fmtNum(bm)} saved by you`,\"window.QB.nav('bookmarks')\",'is-violet')}</div></section>"
    if modern in source:
        source = replace_once(source, modern,
                              "${row('bookmark','Bookmarks',`${fmtNum(bm)} saved by you`,\"window.QB.nav('bookmarks')\",'is-violet')}${row('book','My notes',`${fmtNum(nkSavedQuestionNotes().length)} recall cues`,\"window.QB.nav('notes')\")}</div></section>",
                              "More notes link")
    else:
        legacy = '<button class="more-action" onclick="window.QB.nav(\'bookmarks\')"><div class="mi">${navIcon(\'bookmark\',20)}</div><div><div class="mt">Bookmarks</div><div class="mm">${fmtNum(bm)} saved by you</div></div></button>'
        source = replace_once(source, legacy,
                              legacy + '<button class="more-action" onclick="window.QB.nav(\'notes\')"><div class="mi">${navIcon(\'book\',20)}</div><div><div class="mt">My notes</div><div class="mm">${fmtNum(nkSavedQuestionNotes().length)} recall cues</div></div></button>',
                              "legacy More notes link")
    source = replace_once(source, "  window.QB={", "  window.QB={nkFilterNotes,nkOpenNotedQuestion,", "notes actions")
    return source


if __name__ == "__main__":
    result = transform(HTML.read_text(encoding="utf-8"))
    HTML.write_text(result, encoding="utf-8")
    print("QUESTION_NOTES_INSTALLED: Practice and Review, durable state, sync-ready")
