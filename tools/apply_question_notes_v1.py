#!/usr/bin/env python3
"""Install one question-linked personal note surface after all question transforms."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"
CORE = ROOT / "tools/question_notes_core.js"

CSS = '''<style id="nk-question-notes-v1">
.nk-question-note{margin:18px 0 8px;border:1px solid #dce3ef;border-radius:14px;background:#fff;overflow:hidden;color:#17204b}.nk-question-note summary{min-height:58px;display:flex;justify-content:space-between;align-items:center;gap:12px;padding:12px 15px;cursor:pointer;list-style:none}.nk-question-note summary::-webkit-details-marker{display:none}.nk-question-note summary span:first-child{display:grid;gap:3px}.nk-question-note summary strong{font-size:14px}.nk-question-note summary small{color:#66708d;font-size:11px}.nk-question-note summary span:last-child{font-size:20px;color:#5367a4}.nk-question-note details[open] summary span:last-child{transform:rotate(180deg)}.nk-question-note-body{padding:0 15px 15px}.nk-question-note-body label{display:block;margin-bottom:7px;color:#5a6582;font-size:11px;font-weight:800}.nk-question-note-body textarea{width:100%;min-height:110px;padding:12px;border:1px solid #cfd7e7;border-radius:10px;background:#fff;color:#17204b;font:inherit;font-size:14px;line-height:1.5;resize:vertical}.nk-question-note-body textarea:focus{outline:3px solid #e7ecff;border-color:#6d82ca}.nk-question-note-actions{display:flex;justify-content:space-between;align-items:center;gap:10px;margin-top:10px}.nk-question-note-actions small{color:#697391;font-size:11px}.nk-question-note-actions button{min-height:44px;padding:0 16px;border:0;border-radius:10px;background:#3f63c5;color:#fff;font-size:12px;font-weight:800}
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
    return source


if __name__ == "__main__":
    result = transform(HTML.read_text(encoding="utf-8"))
    HTML.write_text(result, encoding="utf-8")
    print("QUESTION_NOTES_INSTALLED: Practice and Review, durable state, sync-ready")
