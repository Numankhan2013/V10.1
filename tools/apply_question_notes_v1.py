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
.nk-question-note{margin:18px 0 8px;border:0;background:transparent;overflow:visible}
.nk-question-note .nk-note-bar{width:100%;min-height:64px;display:flex;align-items:center;gap:12px;padding:12px 14px;border:1px solid #dce3ef;border-radius:14px;background:#fff;color:#17204b;text-align:left;font:inherit;cursor:pointer;-webkit-tap-highlight-color:transparent;transition:background .15s,border-color .15s,transform .1s}
.nk-question-note .nk-note-bar:active{transform:scale(.99);background:#f6f7fc}
.nk-note-bar-icon{flex:none;width:38px;height:38px;display:grid;place-items:center;border-radius:11px;background:var(--nk-selection,#f1ecfa);color:var(--nk-action,#493394)}
.nk-note-bar-copy{flex:1;min-width:0;display:grid;gap:2px}
.nk-note-bar-copy strong{font-size:15px;font-weight:800}
.nk-note-bar-copy small{color:#66708d;font-size:12.5px;font-weight:500;line-height:1.35;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.nk-note-bar-count{flex:none;min-width:24px;height:24px;padding:0 7px;display:grid;place-items:center;border-radius:12px;background:var(--nk-action,#493394);color:#fff;font-size:12px;font-weight:800}
.nk-note-bar-chevron{flex:none;color:#8a93ad;display:grid}
.nk-note-media-frame{position:relative;display:block;width:100%;overflow:hidden;background:linear-gradient(100deg,#eceff6 30%,#f8f9fc 50%,#eceff6 70%);background-size:220% 100%;animation:nk-note-shimmer 1.3s linear infinite}
.nk-note-media-frame img{display:block;width:100%;height:100%;object-fit:contain;opacity:0;transition:opacity .28s ease}
.nk-note-media-frame.is-loaded{animation:none;background:#fff}
.nk-note-media-frame.is-loaded img{opacity:1}
.nk-note-media-frame.is-missing{animation:none;background:#f5f7fb}
.nk-note-media-missing{display:none;position:absolute;inset:0;align-items:center;justify-content:center;padding:12px;color:#66708d;font-size:12px;line-height:1.4;text-align:center}
.nk-note-media-frame.is-missing .nk-note-media-missing{display:flex}
@keyframes nk-note-shimmer{from{background-position:120% 0}to{background-position:-120% 0}}
.nk-note-page{position:fixed;inset:0;z-index:1900;display:flex;flex-direction:column;background:var(--nk-paper,#fbfbfe);color:#17204b;animation:nk-note-page-in .2s ease-out}
@keyframes nk-note-page-in{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
.nk-np-head{flex:none;display:flex;align-items:center;gap:8px;padding:calc(8px + env(safe-area-inset-top)) 12px 8px;border-bottom:1px solid #e6e9f2;background:#fff}
.nk-np-head h2{margin:0;font-size:18px;font-weight:700;letter-spacing:-.01em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.nk-np-head h2 span{color:#3a4466;font-weight:600}
.nk-np-back{flex:none;width:44px;height:44px;display:grid;place-items:center;border:0;border-radius:12px;background:transparent;color:#17204b;cursor:pointer}
.nk-np-body{flex:1;overflow-y:auto;-webkit-overflow-scrolling:touch;overscroll-behavior:contain;padding:6px 0 120px}
.nk-np-blocks{width:min(760px,100%);margin:0 auto;padding:0 18px}
.nk-nb{position:relative;padding:20px 0;border-top:1px solid #e6e9f2;-webkit-touch-callout:none;-webkit-user-select:none;user-select:none}
.nk-nb:first-child{border-top:0}
.nk-nb-head,.nk-nb-foot{display:flex;align-items:center;gap:10px}
.nk-nb-head{margin-bottom:10px}
.nk-nb-foot{margin-top:8px}
.nk-nb-kind{flex:1;color:var(--nk-action,#493394);font-size:12px;font-weight:800;letter-spacing:.08em;text-transform:uppercase}
.nk-note-page .nk-nb-text{margin:0;padding:0;border:0;border-radius:0;background:transparent;color:#25304f;font-size:16.5px;line-height:1.6;white-space:pre-wrap;overflow-wrap:anywhere}
.nk-nb-title{flex:1;min-width:0;font-size:16px;font-weight:700;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.nk-nb-caption{flex:1;min-width:0;color:#4a5474;font-size:14px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.nk-nb-badge{flex:none;width:30px;height:36px;display:grid;place-items:end center;padding-bottom:5px;border-radius:4px 10px 4px 4px;background:#e5484d;color:#fff;font-size:9px;font-weight:800}
.nk-nb-dots{flex:none;width:40px;height:40px;margin-right:-8px;display:grid;place-items:center;border:0;border-radius:10px;background:transparent;color:#5a6380;cursor:pointer}
.nk-nb-dots:active,.nk-np-back:active{background:#eef0f7}
.nk-nb-open{display:block;width:100%;padding:0;border:1px solid #e1e5ef;border-radius:12px;background:#fff;overflow:hidden;cursor:zoom-in;-webkit-tap-highlight-color:transparent}
.nk-nb.is-editing{-webkit-user-select:text;user-select:text}
.nk-nb.is-editing .nk-nb-kind{display:block;margin-bottom:8px}
.nk-nb.is-editing textarea{width:100%;min-height:140px;padding:12px;border:1px solid #cfd7e7;border-radius:12px;background:#fff;color:#17204b;font:inherit;font-size:16px;line-height:1.55;resize:vertical}
.nk-nb.is-editing textarea:focus{outline:3px solid #e7e3f8;border-color:var(--nk-action,#493394)}
.nk-nb-edit-actions{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-top:10px}
.nk-nb-edit-actions small{color:#697391;font-size:12px}
.nk-nb-edit-actions>div{display:flex;gap:6px}
.nk-nb-edit-actions button{min-height:44px;padding:0 14px;border:0;border-radius:10px;background:transparent;color:var(--nk-action,#493394);font-weight:800;cursor:pointer}
.nk-nb-edit-actions .nk-note-save{padding:0 18px;background:var(--nk-action,#493394);color:#fff}
.nk-nb.is-skeleton{display:grid;gap:12px}
.nk-skel{display:block;border-radius:8px;background:linear-gradient(100deg,#eceff6 30%,#f8f9fc 50%,#eceff6 70%);background-size:220% 100%;animation:nk-note-shimmer 1.3s linear infinite}
.nk-skel-line{width:42%;height:16px}
.nk-skel-box{width:100%;aspect-ratio:4/3;border-radius:12px}
.nk-np-empty{padding:56px 12px;text-align:center;color:#5a6380}
.nk-np-empty strong{display:block;margin-bottom:6px;color:#17204b;font-size:17px}
.nk-np-empty p{margin:0 auto;max-width:300px;font-size:14px;line-height:1.5}
.nk-np-status{width:min(760px,100%);margin:6px auto 0;padding:0 18px;color:#5a6380;font-size:13px;text-align:center;min-height:1em}
.nk-np-add{position:absolute;left:50%;bottom:calc(20px + env(safe-area-inset-bottom));transform:translateX(-50%);display:flex;flex-direction:column;align-items:center;gap:10px}
.nk-np-add-btn{display:flex;align-items:center;gap:8px;min-height:52px;padding:0 26px;border:0;border-radius:26px;background:var(--nk-action,#493394);color:#fff;font:inherit;font-size:16px;font-weight:700;box-shadow:0 10px 24px rgba(73,51,148,.32);cursor:pointer;transition:transform .1s}
.nk-np-add-btn:active{transform:scale(.97)}
.nk-np-add-menu,.nk-nb-menu{min-width:190px;padding:6px;border:1px solid #e1e5ef;border-radius:14px;background:#fff;box-shadow:0 14px 34px rgba(23,32,75,.18)}
.nk-np-add-menu[hidden]{display:none}
.nk-np-add-menu button,.nk-nb-menu button{display:block;width:100%;min-height:44px;padding:0 14px;border:0;border-radius:9px;background:transparent;color:#17204b;font:inherit;font-size:15px;font-weight:600;text-align:left;cursor:pointer}
.nk-np-add-menu button:hover,.nk-nb-menu button:hover,.nk-np-add-menu button:focus-visible,.nk-nb-menu button:focus-visible{background:#f2f0fa;outline:0}
.nk-np-add-menu button:disabled,.nk-nb-menu button:disabled{opacity:.4;cursor:default}
.nk-nb-menu{position:fixed;z-index:1950;animation:nk-note-pop .12s ease-out}
.nk-nb-menu .is-danger{color:#c03a4c}
@keyframes nk-note-pop{from{opacity:0;transform:scale(.96)}to{opacity:1;transform:none}}
.nk-note-page button:focus-visible,.nk-question-note .nk-note-bar:focus-visible{outline:3px solid #8ca3ed;outline-offset:2px}
.nk-note-file{position:absolute;width:1px;height:1px;overflow:hidden;opacity:0;pointer-events:none}
@media (prefers-reduced-motion:reduce){.nk-note-media-frame,.nk-skel,.nk-note-page,.nk-nb-menu{animation:none}}
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
