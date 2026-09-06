#!/usr/bin/env python3
from pathlib import Path
import re


HTML = Path("app/src/main/assets/index.html")


def require(source: str, markers: list[str]) -> None:
    missing = [marker for marker in markers if marker not in source]
    if missing:
        raise SystemExit(f"Question experience markers missing: {missing}")


def main() -> None:
    source = HTML.read_text(encoding="utf-8")
    require(source, [
        'id="nk-question-experience-v113"',
        "function nkPracticeSubject(q)",
        "function nkFormatQuestionTime(ms)",
        "s.questionTimes?.[q.id]",
        'class="nk-question-context is-${esc(subjectKey)}"',
        'class="nk-key-takeaway"',
        'class="nk-source-section"',
        "Original PDF",
        "&scale=4",
        "window.QB.openQuestionNavigator()",
        "window.QB.selectPractice('${q.id}',${n})",
        "window.QB.prevQ()",
        "window.QB.nextQ()",
        "renderExplanationText(q.explanation,q)",
    ])
    practice = source[source.index("function practicePage()") : source.index("function practiceActionBar", source.index("function practicePage()"))]
    forbidden = ["feedback-title", "Well done", "Keep going", "Correct answer</div>"]
    present = [marker for marker in forbidden if marker in practice]
    if present:
        raise SystemExit(f"Duplicate correctness feedback returned: {present}")
    if len(re.findall(r'id="nk-question-experience-v113"', source)) != 1:
        raise SystemExit("Question experience style must be installed exactly once")
    print("QUESTION_EXPERIENCE_OK: approved layout, real timing, canonical PDF, no duplicate success panel")


if __name__ == "__main__":
    main()
