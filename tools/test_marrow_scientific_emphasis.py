#!/usr/bin/env python3
"""Regression coverage for scientific-markup-aware Marrow emphasis anchors."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
from app_page import app_source


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"
PHYSIO_Q18 = ROOT / "data/marrow/explanation_physio_ch23_q018_q018_v1.json"
CLEANUP = ROOT / "data/marrow/explanation_source_cleanup_v1.json"
PRESENTATION_START = "  /* NK_QUESTION_PRESENTATION_V1_START"
PRESENTATION_END = "  /* NK_QUESTION_PRESENTATION_V1_END */"


def function_fragment(source: str, start: str, end: str) -> str:
    if source.count(start) != 1:
        raise AssertionError(f"Expected one {start!r} in index.html, found {source.count(start)}")
    start_at = source.index(start)
    end_at = source.index(end, start_at)
    return source[start_at:end_at].rstrip()


def load_configs() -> dict[str, dict]:
    configs: dict[str, dict] = {}
    for path in sorted((ROOT / "data/marrow").glob("explanation_*_v1.json")):
        if path.name == CLEANUP.name:
            continue
        document = json.loads(path.read_text(encoding="utf-8"))
        questions = document.get("questions", {})
        if not isinstance(questions, dict):
            continue
        for qid, config in questions.items():
            if qid in configs:
                raise AssertionError(f"Duplicate explanation config for {qid}")
            if isinstance(config, dict) and isinstance(config.get("displayText"), str):
                configs[qid] = config
    if not configs:
        raise AssertionError("No explanation configs with displayText were found")
    # The source cleanup replaces shipped text, so its anchors are checked as shipped.
    for qid, entry in json.loads(CLEANUP.read_text(encoding="utf-8"))["questions"].items():
        if qid in configs:
            configs[qid] = dict(configs[qid], displayText=entry["displayText"],
                                emphasis=entry.get("emphasis", configs[qid].get("emphasis", [])))
    return configs


def main() -> None:
    page = app_source()
    gold_text = function_fragment(page, "function nkGoldText(", "function nkGoldSignalWords(")
    gold_renderer = function_fragment(
        page, "function nkRenderMarrowGoldText(", "function nkRenderGoldWrongOptions("
    )
    presentation = function_fragment(page, PRESENTATION_START, PRESENTATION_END)
    # The shipped gold renderer must route text and anchors through the shared
    # scientific-notation/escaping boundary.
    for wired in ("let html=nkScientificMarkup(text);", "const needle=nkScientificMarkup(phrase);"):
        if wired not in gold_text:
            raise AssertionError(f"Gold emphasis is not wired into scientific markup: {wired}")

    q18_document = json.loads(PHYSIO_Q18.read_text(encoding="utf-8"))
    q18_id, q18_cfg = next(iter(q18_document["questions"].items()))
    configs = load_configs()
    if q18_id not in configs:
        raise AssertionError(f"Q18 config {q18_id} is absent from the corpus scan")

    # The presentation core and the two gold functions are extracted verbatim
    # from the shipped index.html.
    shipped = presentation + "\n\n" + gold_text + "\n\n" + gold_renderer

    configs_json = json.dumps(configs, ensure_ascii=False, separators=(",", ":"))
    q18_json = json.dumps(q18_cfg, ensure_ascii=False, separators=(",", ":"))
    runtime = r'''const assert=require('assert');
global.window=globalThis;
const esc=value=>String(value??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
''' + shipped + r'''
const configs=JSON.parse(__CONFIGS__);
const q18=JSON.parse(__Q18__);
const q18html=nkRenderMarrowGoldText(q18.displayText,q18);
assert(q18html.includes('<strong class="nk-gold-em">The stimulus to ventilation after strenuous exercise is increased mean arterial H<sup class="nk-sci-sup">+</sup></strong>'),
  'PHYSIO_CH23_Q018 emphasis anchor must survive H+ scientific markup');
// A spaced hyphen is a dash, not an ionic charge; attached charges still lift.
assert.strictEqual(nkScientificMarkup('Order: P - K - K'),'Order: P - K - K','spaced hyphen after K must stay a dash');
assert(nkScientificMarkup('Cl- and K+ and Ca2-').split('nk-sci-sup').length===4,'attached ionic charges must stay superscripts');
const source='<img src=x onerror="alert(1)"> A < B & C';
const safe=nkGoldText(source,['A < B & C']);
assert(safe.includes('&lt;img src=x onerror="alert(1)"&gt;'), 'plain text HTML must stay escaped');
assert(safe.includes('<strong class="nk-gold-em">A &lt; B &amp; C</strong>'), 'emphasized HTML must be escaped');
assert(!safe.includes('<img'), 'source HTML must not become an element');
const failures=[];
for(const [qid,cfg] of Object.entries(configs)){
  const rendered=nkRenderMarrowGoldText(cfg.displayText,cfg);
  if(!rendered.includes('<strong class="nk-gold-em">')) failures.push(qid);
}
assert.deepStrictEqual(failures, [], 'every scanned displayText must render at least one emphasis anchor');
console.log(`SCIENTIFIC_EMPHASIS_OK q18=${q18html.includes('<sup')} corpus=${Object.keys(configs).length}`);
'''.replace("__CONFIGS__", json.dumps(configs_json)).replace("__Q18__", json.dumps(q18_json))

    with tempfile.TemporaryDirectory(prefix="nk-marrow-scientific-emphasis-") as temp_dir:
        script = Path(temp_dir) / "check.js"
        script.write_text(runtime, encoding="utf-8")
        subprocess.run(["node", str(script)], cwd=ROOT, check=True)


if __name__ == "__main__":
    main()
