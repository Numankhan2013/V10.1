#!/usr/bin/env python3
"""Behavior and generated-app checks for question content hygiene."""

from pathlib import Path
import json
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

    if "NK_QUESTION_CONTENT_HYGIENE_V1_START" in source:
        required = [
            "function nkCleanQuestionStem(value)",
            "function nkTableTakeaway(lines,tokens,answer)",
            "question.question=nkCleanQuestionStem(question.question)",
        ]
        for marker in required:
            if marker not in source:
                raise SystemExit(f"Generated content hygiene marker missing: {marker}")
        print("QUESTION_CONTENT_HYGIENE_INTEGRATION_OK: cleaner and comparison-aware takeaway installed")


if __name__ == "__main__":
    main()
