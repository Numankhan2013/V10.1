#!/usr/bin/env python3
"""Microbiology Marrow emphasis markers must render as emphasis, never raw.

The Microbiology bank is the only shipped bank whose extracted explanations
carry Markdown emphasis: **bold** and *italic* (mostly italic species names).
Two learner-facing surfaces must convert them:

- the ordered explanation renderer, tables and legacy Marrow text (richText),
  which converted **bold** but leaked every single-star italic, and
- the Key takeaway card, which printed both marker kinds raw whenever the
  takeaway was derived from the explanation (no reviewed keyTakeaway).

The renderer must keep multiplication ("900 mg * 100 ml"), allele notation
(HLA-B*27) and OCR artifacts outside the markers, and a derived takeaway
sentence cut out of a longer bold span must lose its unmatched marker.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

from app_page import app_source
from marrow_bank_data import load_sharded

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "app/src/main/modules/question_presentation.js"
PREFIX = "microbiology_marrow_qbank"


def fragment(page: str, name: str) -> str:
    needle = f"  function {name}("
    start = page.rindex(needle)
    end = page.index("\n  function ", start + len(needle))
    return page[start:end]


def main() -> None:
    page = app_source()
    for marker in (
        "function nkEmphasisHtml(html){",
        "return nkEmphasisHtml(nkScientificMarkup(text));",
        "${richText(takeaway)}",
    ):
        assert marker in page, f"shipped page lost {marker!r}"
    assert "${nkScientificMarkup(takeaway)}" not in page

    record = load_sharded(PREFIX)
    questions = record["questions"]

    runtime = (
        r"""
const assert=require('assert'),fs=require('fs');
global.window=globalThis;let SUBJECTS=[];
"""
        + CORE.read_text(encoding="utf-8")
        + "\n\n"
        + fragment(page, "esc")
        + "\n\n"
        + fragment(page, "nkEmphasisHtml")
        + "\n\n"
        + fragment(page, "richText")
        + "\n\n"
        + fragment(page, "nkSourceTakeaway")
        + "\n\n"
        + fragment(page, "nkMarrowTakeaway")
        + r"""

const same=(input,expect,label)=>{
  const out=richText(input);
  assert.strictEqual(out,expect,label+': '+JSON.stringify(out));
};
same('**bold**','<strong>bold</strong>','bold');
same('*italic*','<em>italic</em>','italic');
same('***both***','<strong><em>both</em></strong>','bold+italic');
same('**a) *Streptococcus pyogenes***','<strong>a) <em>Streptococcus pyogenes</em></strong>','bold span ending in italic');
same('***Staphylococcus* is pathogenic.**','<strong><em>Staphylococcus</em> is pathogenic.</strong>','bold span starting with italic');
// A Key takeaway sentence cut out of a longer bold span keeps one marker only.
same('start **blood should be cultured.','start blood should be cultured.','dangling bold opener');
same('growth was seen.**','growth was seen.','dangling bold closer');
same('***Corynebacterium diphtheria*.','<em>Corynebacterium diphtheria</em>.','dangling bold kept italic');
// Multiplication and allele notation must stay literal.
for(const keep of ['900 mg * 100 ml','15 g/dL *1.34 mL','HLA-B*27:05 carriers','CYP2D6*4 poor metabolizer']){
  assert(richText(keep)===keep,'marker change for '+JSON.stringify(keep)+' -> '+JSON.stringify(richText(keep)));
}
// Emphasis never unescapes markup.
const escaped=richText('<img src=x onerror=alert(1)> **ok**');
assert(!escaped.includes('<img')&&escaped.includes('&lt;img')&&escaped.includes('<strong>ok</strong>'),'escape leak: '+escaped);

const QUESTIONS=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const leftovers=[],unbalanced=[],leaks=[];
let chunks=0,takeaways=0,markerQuestions=0;
const check=(qid,rendered)=>{
  if(rendered.includes('*'))leftovers.push([qid,rendered.slice(0,140)]);
  const strong=(rendered.match(/<strong>/g)||[]).length,strongClose=(rendered.match(/<\/strong>/g)||[]).length;
  const em=(rendered.match(/<em>/g)||[]).length,emClose=(rendered.match(/<\/em>/g)||[]).length;
  if(strong!==strongClose||em!==emClose)unbalanced.push([qid,rendered.slice(0,140)]);
  if(/<(?!\/?(strong|em|sup|sub|span)\b)[a-zA-Z]/.test(rendered))leaks.push([qid,rendered.slice(0,140)]);
};
const chunkTexts=q=>{
  const out=[];const se=q.structuredExplanation||{};
  const push=v=>{if(typeof v==='string'&&v.trim())out.push(v);};
  push(q.explanation);push(se.text);
  for(const b of se.blocks||[]){
    if(!b||typeof b!=='object')continue;
    push(b.text);push(b.title);
    for(const it of b.items||[]){
      if(!it||typeof it!=='object')continue;
      push(it.text);
      for(const c of it.items||[])if(c&&typeof c==='object')push(c.text);
    }
  }
  for(const t of se.tables||[]){
    if(!t||typeof t!=='object')continue;
    push(t.title);
    for(const c of t.columns||[])push(String(c));
    for(const r of t.rows||[]){if(!Array.isArray(r)){push(String(r));continue;}for(const c of r)push(String(c));}
  }
  return out;
};
for(const q of QUESTIONS){
  const texts=chunkTexts(q);
  if(texts.some(t=>t.includes('*')))markerQuestions++;
  for(const chunk of texts){chunks++;check(q.id,richText(chunk));}
  const takeaway=nkMarrowTakeaway(q);
  if(takeaway){takeaways++;check(q.id,richText(takeaway));}
  // Stems and options render through the scientific boundary only, so their
  // source text must never carry markers in the first place.
  if(typeof q.question==='string'&&q.question.includes('*'))leaks.push([q.id,'stem carries markers']);
  for(const o of q.options||[])if(o&&typeof o.text==='string'&&o.text.includes('*'))leaks.push([q.id,'option carries markers']);
}
assert.strictEqual(leftovers.length,0,'raw markers reached the reader: '+JSON.stringify(leftovers.slice(0,4)));
assert.strictEqual(unbalanced.length,0,'unbalanced emphasis tags: '+JSON.stringify(unbalanced.slice(0,4)));
assert.strictEqual(leaks.length,0,'unexpected markup: '+JSON.stringify(leaks.slice(0,4)));
assert(markerQuestions>=150,'marker scan found only '+markerQuestions+' marker-bearing questions');
console.log('MICROBIOLOGY_MARROW_EMPHASIS_OK questions='+QUESTIONS.length+' chunks='+chunks+' takeaways='+takeaways+' marker_questions='+markerQuestions);
"""
    )

    with tempfile.NamedTemporaryFile("w", suffix=".json", encoding="utf-8", delete=False) as payload:
        json.dump(questions, payload, ensure_ascii=False)
        payload_path = Path(payload.name)
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
        handle.write(runtime)
        test_path = Path(handle.name)
    try:
        result = subprocess.run(
            ["node", str(test_path), str(payload_path)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        print(result.stdout.strip())
    finally:
        test_path.unlink(missing_ok=True)
        payload_path.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
