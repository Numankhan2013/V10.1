#!/usr/bin/env python3
from pathlib import Path
import re
from app_page import app_source


HTML = Path("app/src/main/assets/index.html")


def require(source: str, markers: list[str]) -> None:
    missing = [marker for marker in markers if marker not in source]
    if missing:
        raise SystemExit(f"Question experience markers missing: {missing}")


def main() -> None:
    source = app_source()
    require(source, [
        # The shared session experience (V11.4) superseded the V11.3 stylesheet and context bar.
        '/* ── nk-session-experience-v114 ── */',
        "function nkPracticeSubject(q)",
        "function nkFormatQuestionTime(ms)",
        "s.questionTimes?.[q.id]",
        "function nkQuestionContext(q) { return ''; }",
        'class="nk-v114-session is-practice"',
        'class="nk-key-takeaway"',
        'class="nk-source-section"',
        "Original PDF",
        "&scale=4",
        "window.QB.openQuestionNavigator()",
        "window.QB.selectPractice('${q.id}',${n},'${owner}')",
        "window.QB.prevQ()",
        "window.QB.nextQ()",
        "renderExplanationText(q.explanation,q)",
    ])
    practice = source[source.index("function practicePage()") : source.index("function practiceActionBar", source.index("function practicePage()"))]
    forbidden = ["feedback-title", "Well done", "Keep going", "Correct answer</div>"]
    present = [marker for marker in forbidden if marker in practice]
    if present:
        raise SystemExit(f"Duplicate correctness feedback returned: {present}")
    if source.count('/* ── nk-session-experience-v114 ── */') != 1:
        raise SystemExit("Question experience style must be installed exactly once")
    if 'id="nk-question-experience-v113"' in source:
        raise SystemExit("Superseded V11.3 question style returned")
    print("QUESTION_EXPERIENCE_OK: approved layout, real timing, canonical PDF, no duplicate success panel")


if __name__ == "__main__":
    main()
