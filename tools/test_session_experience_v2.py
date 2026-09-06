#!/usr/bin/env python3
from pathlib import Path
import re


HTML=Path("app/src/main/assets/index.html")


def section(source: str, start: str, end: str) -> str:
    a=source.index(start);b=source.index(end,a)
    return source[a:b]


def main() -> None:
    source=HTML.read_text(encoding="utf-8")
    required=[
      'id="nk-session-experience-v114"',
      "function nkSourceTakeaway(q)",
      "function nkSessionHeader(q,s,mode,timerHtml='')",
      "function nkSessionOptions(q,selected,mode,submitted)",
      "function nkStudySupport(q,timeMs,unattempted=false)",
      'class="nk-v114-session is-practice"',
      'class="nk-v114-session is-exam"',
      'class="nk-v114-session is-review"',
      "window.QB.openQuestionNavigator()",
      'id="cr-grid"',
      "window.QB.jumpFromNavigator(${i})",
      "window.QB.selectPractice('${q.id}',${n})",
      "window.QB.selectExam(${n})",
      "bottom:0!important",
      "grid-template-columns:38px minmax(0,1fr)!important",
      "dna:`<svg ${common}>",
      "renderExplanationText(q.explanation,q)",
      "&scale=4",
    ]
    missing=[x for x in required if x not in source]
    if missing:raise SystemExit(f"Missing shared-session markers: {missing}")
    practice=section(source,"function practicePage()","function practiceActionBar")
    exam=section(source,"function examPage()","function resultPage")
    review=section(source,"function reviewTestPage()","function closeQuestionNavigator")
    navigator=section(source,"function openQuestionNavigator()","function jumpFromNavigator")
    if "nk-option-state" in source:raise SystemExit("Option-side status holes remain")
    if "<aside class=\"card navigator\">" in practice+exam+review:raise SystemExit("Legacy inline navigator remains")
    if "nkStudySupport" in exam or "renderExplanationText" in exam or "correctOption" in exam:raise SystemExit("CBT correctness/explanation leakage risk")
    if "option?.text?String(option.text)" in source:raise SystemExit("Correct-option takeaway fallback remains")
    if "s.mode==='exam'" not in navigator or "else if(submitted)" not in navigator:raise SystemExit("Mode-specific navigator states missing")
    if source.count('id="nk-session-experience-v114"')!=1:raise SystemExit("Shared-session style duplicated")
    print("SESSION_EXPERIENCE_OK: docked footer, no holes, functional grid, shared modes, CBT privacy, source takeaways")


if __name__=="__main__":main()
