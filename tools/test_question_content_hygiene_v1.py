#!/usr/bin/env python3
"""Behavior and generated-app checks for conservative Marrow learner-text hygiene."""

from pathlib import Path
import base64
import json
import zlib
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"
CORE = ROOT / "tools/question_content_hygiene_core.js"


def main() -> None:
    source = HTML.read_text(encoding="utf-8")

    behavior = CORE.read_text(encoding="utf-8") + r'''
const q={
  correctOption:3,
  options:[{text:'Insoluble fibre is fermented in the large intestine'},{text:'Dietary fibre provides a significant source of energy'},{text:'Soluble fibre helps lower LDL cholesterol'},{text:'Soluble fibre promotes bowel movements'}],
  explanation:`Correct answer: C) Soluble fiber helps lower LDL cholesterol
Explanation:

  Soluble fiber                                                 Insoluble fiber

  Lower LDL cholesterol levels by increasing bile acid          Adds bulk and promotes bowel movements. (Option D)
  excretion and interfering with bile acid reabsorption         Passes through the digestive tract largely unchanged
  Fermented in the large intestine to short-chain fatty acids   (Option A) Ex: whole wheat, walnuts, chickpeas, etc`
};
const takeaway=nkSourceTakeaway(q);
if(takeaway!=='Soluble fibre helps lower LDL cholesterol. This occurs by increasing bile acid excretion and interfering with bile acid reabsorption.')throw new Error(takeaway);
if(/adds bulk|bowel movements/i.test(takeaway))throw new Error('Opposite table column leaked into takeaway');
const dirty='Which statement is accurate?\nPrepladder X Qbank • Biochemistry       Page 12 of 966';
if(nkCleanQuestionStem(dirty)!=='Which statement is accurate?')throw new Error(nkCleanQuestionStem(dirty));

const plain='The set {A, B} and Na+/K+ ATPase are physiologic notation.';
if(nkSanitizeMarrowText(plain)!==plain)throw new Error('Legitimate brace/medical notation changed');
const malformed='{"text":"keep this malformed"';
if(nkSanitizeMarrowText(malformed)!==malformed)throw new Error('Malformed/non-whole JSON was modified');
if(nkSanitizeMarrowText('{"text":"Clean learner text"}')!=='Clean learner text')throw new Error('Single JSON wrapper not decoded');
const twice=JSON.stringify(JSON.stringify({text:'Double encoded learner text'}));
if(nkSanitizeMarrowText(twice)!=='Double encoded learner text')throw new Error('Double JSON wrapper not decoded');
const rich={type:'doc',content:[{type:'paragraph',content:[{type:'text',text:'First sentence.'}]},{type:'paragraph',content:[{type:'text',text:'Second sentence.'}]}]};
if(nkSanitizeMarrowText(rich)!=='First sentence.\nSecond sentence.')throw new Error('Structured rich text not flattened safely');
const array='[{"text":"Alpha"},{"text":"Beta"}]';
if(nkSanitizeMarrowText(array)!=='Alpha\nBeta')throw new Error('Serialized text array not decoded');

const marrow={
  id:'marrow__PHYSIO_CH07_Q999',
  question:'{"text":"Stem"}',
  options:[{text:'{"text":"Option A"}',explanation:'{"text":"Option reason"}'},{text:'Normal option'}],
  explanation:'{"content":[{"text":"Explanation line"}]}',
  correctAnswerText:'{"text":"Correct answer"}',
  structuredExplanation:{text:'{"text":"Structured detail"}',blocks:[{type:'paragraph',content:{text:'Block detail'}}],tables:[],figures:[]}
};
nkSanitizeMarrowQuestion(marrow);
if(marrow.question!=='Stem'||marrow.options[0].text!=='Option A'||marrow.options[0].explanation!=='Option reason'||marrow.options[1].text!=='Normal option'||marrow.explanation!=='Explanation line'||marrow.correctAnswerText!=='Correct answer'||marrow.structuredExplanation.text!=='Structured detail'||marrow.structuredExplanation.blocks[0].content!=='Block detail')throw new Error(JSON.stringify(marrow));
const once=JSON.stringify(marrow);
nkSanitizeMarrowQuestion(marrow);
if(JSON.stringify(marrow)!==once)throw new Error('Sanitizer is not idempotent');
console.log('QUESTION_CONTENT_HYGIENE_BEHAVIOR_OK');
'''
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8") as handle:
        handle.write(behavior)
        handle.flush()
        subprocess.run(["node", handle.name], check=True)

    lines = source.splitlines()
    base_line = next(line for line in lines if line.startswith("window.QBANK_DATA = "))
    subjects_line = next(line for line in lines if line.startswith("window.SUBJECT_QBANK_DATA="))
    base = json.loads(base_line[base_line.find("{") : base_line.rfind(";")])
    subjects = json.loads(subjects_line[subjects_line.find("{") : subjects_line.rfind(";")])
    questions = list(base.get("questions", []))
    for subject in subjects.get("subjects", []):
        for topic in subject.get("topics", []):
            questions.extend(q for q in topic.get("questions", []) if q)
    contaminated = [q["id"] for q in questions if "prepladder" in str(q.get("question", "")).lower()]
    if len(contaminated) != 78:
        raise SystemExit(f"Expected 78 known source-contaminated stems, found {len(contaminated)}")
    print(f"QUESTION_CONTENT_HYGIENE_OK questions={len(questions)} cleaned_stems={len(contaminated)}")


    marrow_records = []
    for prefix in ("anatomy_ch001_063", "biochemistry_ch001_028", "physiology_ch001_043"):
        parts = sorted((ROOT / "data/marrow").glob(f"{prefix}.zlib.b64.part*"))
        raw = zlib.decompress(
            base64.b64decode("".join(part.read_text(encoding="utf-8").strip() for part in parts))
        )
        marrow_records.append(json.loads(raw.decode("utf-8")))
    corpus_behavior = (
        CORE.read_text(encoding="utf-8")
        + "\nconst records="
        + json.dumps(marrow_records, ensure_ascii=False, separators=(",", ":"))
        + r""";
const leak=(value)=>{
  const text=String(value??'').trim();
  if(text.includes('[object Object]'))return true;
  if(!nkWholeJsonCandidate(text))return false;
  try{JSON.parse(text);return true;}catch(_error){return false;}
};
let fields=0;
for(const record of records){
  for(const question of record.questions||[]){
    nkSanitizeMarrowQuestion(question);
    const values=[question.question,question.explanation,question.correctAnswerText];
    const structured=question.structuredExplanation;
    if(structured&&typeof structured==='object'){
      values.push(structured.text,structured.content);
      for(const block of structured.blocks||[])values.push(block?.text,block?.content,block?.label,block?.title);
    }
    for(const option of question.options||[])values.push(option?.text,option?.explanation,option?.rationale,option?.whyWrong,option?.whyCorrect);
    for(const value of values){
      if(value===undefined||value===null)continue;
      fields++;
      if(typeof value!=='string'||leak(value))throw new Error('Learner serialization leak after sanitation: '+question.id+' '+JSON.stringify(value).slice(0,240));
    }
  }
}
if(records.reduce((n,record)=>n+(record.questions||[]).length,0)!==2711)throw new Error('Canonical Marrow corpus count changed');
console.log('MARROW_CONTENT_CORPUS_HYGIENE_OK questions=2711 fields='+fields);
"""
    )
    with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8") as handle:
        handle.write(corpus_behavior)
        handle.flush()
        subprocess.run(["node", handle.name], check=True)

    installed = "NK_QUESTION_CONTENT_HYGIENE_V1_START" in source or "NK_QUESTION_CONTENT_HYGIENE_V1_END" in source
    if installed:
        required = [
            "function nkSanitizeMarrowText(value)",
            "function nkSanitizeMarrowStructuredExplanation(value)",
            "function nkSanitizeMarrowQuestion(question)",
            "function nkCleanQuestionStem(value)",
            "function nkTableTakeaway(lines,tokens,answer)",
            "SUBJECTS.forEach(record=>(record.questions||[]).forEach(question=>nkSanitizeMarrowQuestion(question)))",
        ]
        for marker in required:
            if marker not in source:
                raise SystemExit(f"Generated content hygiene marker missing: {marker}")
        if source.count("NK_QUESTION_CONTENT_HYGIENE_V1_START") != 1 or source.count("NK_QUESTION_CONTENT_HYGIENE_V1_END") != 1:
            raise SystemExit("Generated app must contain exactly one hygiene marker pair")

        has_marrow = "const MARROW_DATA = " in source
        generated_bank_hooks = source.count("(record.questions||[]).forEach(question=>{\n      nkSanitizeMarrowQuestion(question);")
        if has_marrow and generated_bank_hooks != 2:
            raise SystemExit(f"Post-Marrow app must sanitize both generated bank registry paths; found {generated_bank_hooks}")
        if not has_marrow and generated_bank_hooks != 0:
            raise SystemExit(f"Pre-Marrow app unexpectedly has generated-bank hooks: {generated_bank_hooks}")
        print(
            "QUESTION_CONTENT_HYGIENE_INTEGRATION_OK: "
            f"phase={'post-marrow' if has_marrow else 'pre-marrow'} generated_bank_hooks={generated_bank_hooks}"
        )
    else:
        print("QUESTION_CONTENT_HYGIENE_SOURCE_SHELL_OK: behavior tested; integration markers are installed during the deterministic build")


if __name__ == "__main__":
    main()
