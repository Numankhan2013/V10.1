#!/usr/bin/env python3
"""Install one question-linked personal note surface after all question transforms."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"
CORE = ROOT / "tools/question_notes_core.js"
MEDIA = ROOT / "tools/question_note_media_core.js"

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
.nk-note-blocks{display:grid;gap:10px;margin:0 15px 15px}
.nk-note-blocks .nk-note-readonly{margin:0}
.nk-note-figure{margin:0}
.nk-question-note .nk-note-figure-open{display:block;width:100%;min-height:0;padding:0;border:1px solid #e1e7f1;border-radius:10px;background:#fff;overflow:hidden;cursor:zoom-in}
.nk-note-figure figcaption{margin-top:5px;color:#66708d;font-size:11px;overflow-wrap:anywhere}
.nk-note-media-frame{position:relative;display:block;width:100%;background:#fff;overflow:hidden}
.nk-note-media-frame img{display:block;width:100%;height:100%;object-fit:contain}
.nk-note-media-missing{display:none;position:absolute;inset:0;align-items:center;justify-content:center;padding:12px;background:#f5f7fb;color:#66708d;font-size:12px;line-height:1.4;text-align:center}
.nk-note-media-frame.is-missing .nk-note-media-missing{display:flex}
.nk-note-parts{display:grid;gap:10px}
.nk-note-part.is-media{display:grid;grid-template-columns:88px 1fr;align-items:center;gap:10px;padding:8px;border:1px solid #e1e7f1;border-radius:10px;background:#fbfcff}
.nk-note-part.is-media .nk-note-media-frame{width:88px;max-height:120px;border:1px solid #e1e7f1;border-radius:6px}
.nk-note-part.is-media .nk-note-media-missing{font-size:0}
.nk-note-part.is-media .nk-note-part-tools{grid-column:1/-1}
.nk-note-part-label{color:#3c4766;font-size:12px;font-weight:700;overflow-wrap:anywhere}
.nk-note-part-tools{display:flex;justify-content:flex-end;gap:4px;margin-top:4px}
.nk-question-note .nk-note-part-tools button{min-width:44px;padding:0 10px;background:#f2f5fb}
.nk-note-add-row{position:relative;display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}
.nk-note-file{position:absolute;width:1px;height:1px;overflow:hidden;opacity:0;pointer-events:none}
.nk-question-note .nk-note-add-row button{flex:1 1 auto;border:1px dashed #b9c4e0;background:#f8faff}
.nk-question-note button:disabled{opacity:.45;cursor:default}
.nk-notes-item-media{display:flex;align-items:center;gap:8px;margin-top:10px}
.nk-notes-item-media .nk-note-media-frame{width:72px;height:72px;border:1px solid #dce3ef;border-radius:8px}
.nk-notes-item-media .nk-note-media-frame img{object-fit:cover}
.nk-notes-item-media .nk-note-media-missing{font-size:0}
.nk-notes-item-more{color:#526893;font-size:12px;font-weight:800}
.nk-note-sheet{position:fixed;inset:0;z-index:2000;display:flex;align-items:flex-end;justify-content:center;background:rgba(20,24,40,.5)}
.nk-note-sheet-panel{width:min(760px,100%);max-height:88vh;display:flex;flex-direction:column;border-radius:18px 18px 0 0;background:#fff;color:#17204b;padding-bottom:env(safe-area-inset-bottom)}
@media (min-width:700px){.nk-note-sheet{align-items:center}.nk-note-sheet-panel{border-radius:18px}}
.nk-note-sheet header,.nk-note-sheet footer{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:14px 16px}
.nk-note-sheet header div{display:grid;gap:2px}
.nk-note-sheet header strong{font-size:15px}
.nk-note-sheet header small,.nk-note-sheet footer span{color:#66708d;font-size:12px}
.nk-note-sheet-close{min-width:44px;min-height:44px;border:0;border-radius:10px;background:transparent;color:#17204b;font-size:18px;cursor:pointer}
.nk-note-pdf-grid{flex:1;display:grid;grid-template-columns:repeat(auto-fill,minmax(104px,1fr));gap:10px;padding:4px 16px 16px;overflow:auto;-webkit-overflow-scrolling:touch}
.nk-note-pdf-page{display:grid;gap:5px;padding:6px;border:2px solid #e1e7f1;border-radius:10px;background:#fff;cursor:pointer}
.nk-note-pdf-page[aria-pressed="true"]{border-color:#3f63c5;background:#eef2ff}
.nk-note-pdf-thumb{display:flex;align-items:center;justify-content:center;aspect-ratio:3/4;border-radius:6px;background:#f3f5fa;overflow:hidden}
.nk-note-pdf-canvas{max-width:100%;max-height:100%}
.nk-note-pdf-label{color:#3c4766;font-size:11px;font-weight:700}
.nk-note-sheet-add{min-height:44px;padding:0 18px;border:0;border-radius:10px;background:#3f63c5;color:#fff;font-weight:800;cursor:pointer}
.nk-note-sheet-add:disabled{opacity:.45;cursor:default}
.nk-note-sheet button:focus-visible,.nk-note-viewer button:focus-visible{outline:3px solid #8ca3ed;outline-offset:2px}
.nk-note-viewer{position:fixed;inset:0;z-index:2100;display:flex;flex-direction:column;background:#0f1220;color:#fff}
.nk-note-viewer-bar{display:flex;justify-content:space-between;align-items:center;gap:8px;padding:calc(8px + env(safe-area-inset-top)) 12px 8px}
.nk-note-viewer-bar button{min-width:44px;min-height:44px;margin-left:6px;border:0;border-radius:10px;background:rgba(255,255,255,.14);color:#fff;font-size:20px;cursor:pointer}
.nk-note-viewer-count{min-width:0;overflow:hidden;font-size:13px;opacity:.85;text-overflow:ellipsis;white-space:nowrap}
.nk-note-viewer-stage{position:relative;flex:1;overflow:hidden;touch-action:none}
.nk-note-viewer-stage img{position:absolute;inset:0;width:100%;height:100%;object-fit:contain;transform-origin:0 0;user-select:none;-webkit-user-select:none;-webkit-user-drag:none}
.nk-note-viewer-nav{position:absolute;top:50%;min-width:44px;min-height:64px;border:0;border-radius:10px;background:rgba(255,255,255,.14);color:#fff;font-size:28px;transform:translateY(-50%);cursor:pointer}
.nk-note-viewer-nav.is-prev{left:8px}
.nk-note-viewer-nav.is-next{right:8px}
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
    cores = CORE.read_text(encoding="utf-8").rstrip() + "\n\n" + MEDIA.read_text(encoding="utf-8").rstrip()
    source = replace_once(source, "  window.QB={", cores + "\n\n  window.QB={", "notes core")
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
    print("QUESTION_NOTES_INSTALLED: Practice and Review, text/image/PDF parts, durable state, sync-ready")
