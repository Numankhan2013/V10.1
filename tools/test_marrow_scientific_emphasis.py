#!/usr/bin/env python3
"""Regression coverage for scientific-markup-aware Marrow emphasis anchors."""

from __future__ import annotations

import ast
import json
from pathlib import Path
import re
import subprocess
import tempfile

from apply_question_presentation_v1 import transform


ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "tools/apply_marrow_bank_pilot.py"
PHYSIO_Q18 = ROOT / "data/marrow/explanation_physio_ch23_q018_q018_v1.json"


def wrapper_source() -> str:
    tree = ast.parse(PILOT.read_text(encoding="utf-8"), filename=str(PILOT))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "wrapper"
            for target in node.targets
        ):
            expression = node.value
            if isinstance(expression, ast.Call) and isinstance(expression.func, ast.Attribute):
                expression = expression.func.value
            value = ast.literal_eval(expression)
            if isinstance(value, str) and "function nkGoldText(" in value:
                return value
    raise AssertionError("Could not find the literal wrapper containing nkGoldText")


def function_fragment(wrapper: str, start: str, end: str) -> str:
    start_at = wrapper.index(start)
    end_at = wrapper.index(end, start_at)
    return wrapper[start_at:end_at].rstrip()


def load_configs() -> dict[str, dict]:
    configs: dict[str, dict] = {}
    for path in sorted((ROOT / "data/marrow").glob("explanation_*_v1.json")):
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
    return configs


def main() -> None:
    wrapper = wrapper_source()
    gold_text = function_fragment(
        wrapper, "function nkGoldText(", "function nkGoldSignalWords("
    )
    gold_renderer = function_fragment(
        wrapper, "function nkRenderMarrowGoldText(", "function nkRenderGoldWrongOptions("
    )

    q18_document = json.loads(PHYSIO_Q18.read_text(encoding="utf-8"))
    q18_id, q18_cfg = next(iter(q18_document["questions"].items()))
    configs = load_configs()
    if q18_id not in configs:
        raise AssertionError(f"Q18 config {q18_id} is absent from the corpus scan")

    # This fixture supplies the real transformation's anchors. The two gold
    # functions above are extracted verbatim from the production wrapper AST.
    fixture = r'''<!doctype html><html><head></head><body>
<script>
  function richText(text) {
    return esc(String(text||'')).replace(/\*\*(.*?)\*\*/g,'<strong>$1</strong>');
  }
  function nkSessionOptions(q,selected,mode,submitted) {
    const locked=false;
    return `${esc(o.text)}`;
  }
  const practice = '<div class="question-text">${esc(q.question)}</div>';
  const cbt = '<div class="question-text">${esc(q.question)}</div>';
  const review = '<div class="question-text">${esc(q.question)}</div>';
__GOLD_FUNCTIONS__
  window.QB={};
</script></body></html>'''
    fixture = fixture.replace("__GOLD_FUNCTIONS__", gold_text + "\n\n" + gold_renderer)
    transformed = transform(fixture)
    scripts = re.findall(r"<script>(.*?)</script>", transformed, flags=re.S)
    if len(scripts) != 1:
        raise AssertionError(f"Expected one transformed fixture script, got {len(scripts)}")

    configs_json = json.dumps(configs, ensure_ascii=False, separators=(",", ":"))
    q18_json = json.dumps(q18_cfg, ensure_ascii=False, separators=(",", ":"))
    runtime = r'''const assert=require('assert');
global.window=globalThis;
const esc=value=>String(value??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
''' + scripts[0] + r'''
const configs=JSON.parse(__CONFIGS__);
const q18=JSON.parse(__Q18__);
const q18html=nkRenderMarrowGoldText(q18.displayText,q18);
assert(q18html.includes('<strong class="nk-gold-em">The stimulus to ventilation after strenuous exercise is increased mean arterial H<sup class="nk-sci-sup">+</sup></strong>'),
  'PHYSIO_CH23_Q018 emphasis anchor must survive H+ scientific markup');
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
