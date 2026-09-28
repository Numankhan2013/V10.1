#!/usr/bin/env python3
"""Add a saved-result correction pass to the existing Practice journey."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"
CORE = ROOT / "tools/practice_correction_core.js"
MARKER = "NK_PRACTICE_CORRECTION_V1_START"
REVIEW_ANCHOR = '      <section class="nk-section"><div class="nk-section-head"><div><div class="nk-kicker">QUESTION REVIEW</div>'

CSS = '''<style id="nk-practice-correction-v1">
.nk-correction-section{margin-top:16px;padding:18px;border:1px solid #dce5f5;border-radius:16px;background:#f7f9ff;color:#243464}
.nk-correction-section h2{margin:5px 0 12px;font-size:19px;line-height:1.25}
.nk-correction-progress,.nk-correction-clear,.nk-correction-unavailable{margin:0 0 11px;font-size:12px;line-height:1.55;color:#526482}
.nk-correction-progress strong{color:#267357}.nk-correction-clear{margin:0;color:#267357;font-weight:700}
.nk-correction-action{display:flex;align-items:center;justify-content:space-between;gap:14px;padding:15px;border:1px solid #d5def2;border-radius:12px;background:#fff}
.nk-correction-action>div{min-width:0}.nk-correction-action strong,.nk-correction-action small{display:block}
.nk-correction-action strong{font-size:14px;color:#23356b}.nk-correction-action small{margin-top:5px;font-size:11px;line-height:1.45;color:#62718d}
.nk-correction-action button{display:inline-flex;align-items:center;justify-content:center;gap:5px;flex:none;min-height:48px;padding:9px 14px;border:0;border-radius:10px;background:#475db5;color:#fff;font:inherit;font-size:14px;font-weight:800;cursor:pointer}
.nk-correction-parent{display:inline-block;min-height:44px;margin:5px 8px 0 0;padding:0 4px;border:0;background:transparent;color:#3f59a6;font:inherit;font-size:11px;font-weight:800;text-decoration:underline;cursor:pointer}
.nk-correction-section button:focus-visible{outline:3px solid #a3b5ec;outline-offset:2px}
@media(max-width:560px){.nk-correction-action{align-items:stretch;flex-direction:column}.nk-correction-action button{width:100%}}
</style>'''


def replace_once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return source.replace(old, new, 1)


def transform(source: str) -> str:
    if MARKER in source:
        return source
    if "NK_CONTINUE_PRACTICE_RESUME_V1_START" not in source or "NK_QUESTION_SEARCH_V1_START" not in source:
        raise SystemExit("Practice correction must follow durable Practice and all-bank search")
    source = replace_once(source, "</head>", CSS + "\n</head>", "correction styles")
    source = replace_once(source, REVIEW_ANCHOR,
                          "      ${nkCorrectionResultSection(t)}\n" + REVIEW_ANCHOR,
                          "Practice result insertion")
    source = replace_once(source, "  window.QB={", CORE.read_text(encoding="utf-8").rstrip() +
                          "\n\n  window.QB={nkCorrectionStart,", "correction action")
    return source


if __name__ == "__main__":
    HTML.write_text(transform(HTML.read_text(encoding="utf-8")), encoding="utf-8")
    print("PRACTICE_CORRECTION_INSTALLED: saved misses and linked correction pass")
