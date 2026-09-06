#!/usr/bin/env python3
"""Regression checks for the V11.4 whole-app visual transformation."""

from pathlib import Path
import re


HTML = Path("app/src/main/assets/index.html")


def section(source: str, start: str, end: str) -> str:
    a = source.index(start)
    b = source.index(end, a)
    return source[a:b]


def main() -> None:
    source = HTML.read_text(encoding="utf-8")
    required = [
        'id="nk-whole-app-vision-v114"',
        "function nkAppSubjectMeta(name=activeSubject)",
        "function nkSubjectGraphic(name,size=20)",
        "function nkFlameGraphic(size=24)",
        "function nkStreakMilestoneCopy()",
        "function startAllSubjectPractice()",
        "function openMultiSubjectTestBuilder()",
        "function nkMultiExamPoolIds()",
        "function nkConfirmMultiSubjectExam()",
        'aria-label="NK QBank"',
        "All Subjects · Random Practice",
        "All Subjects CBT",
        'name="nk-multi-subject"',
        'id="nk-multi-scope-topics"',
        'class="nk-subject-svg"',
        'class="nk-flame-svg"',
        'class="nk-app-v114 nk-home-v114"',
        'class="nk-app-v114 nk-topics-v114"',
        'class="nk-app-v114 nk-chapter-v114"',
        'class="nk-app-v114 nk-tests-v114"',
        'class="nk-app-v114 nk-analytics-v114"',
        'class="nk-app-v114 nk-more-v114"',
        'class="nk-app-v114 nk-library-v114"',
        'class="nk-app-v114 nk-result-v114"',
        "window.QB.openSubjectTopics('${esc(x.subject)}')",
        "window.QB.openTestBuilder()",
        "window.QB.startAllSubjectPractice()",
        "window.QB.startLibrary('review')",
        "window.QB.practiceOne('${q.id}')",
        "window.QB.openChapter('${c.id}')",
        "window.QB.confirmSession('${selectedId||''}','exam',${pool})",
        "window.__QB_OPEN_REVIEW(this.getAttribute('data-review-test-id'))",
        'data-v102-review-cta="1"',
        'id="nk-session-experience-v114"',
        'id="cr-grid"',
        "&scale=4",
    ]
    missing = [marker for marker in required if marker not in source]
    if missing:
        raise SystemExit(f"Whole-app vision markers missing: {missing}")
    for name in ("dashboard", "topics", "chapterPage", "testsPage", "analytics", "morePage", "libraryPage", "resultPage"):
        if source.count(f"function {name}(") != 1:
            raise SystemExit(f"{name} renderer must exist exactly once")
    exam = section(source, "function examPage()", "function resultPage")
    review = section(source, "function reviewTestPage()", "function closeQuestionNavigator")
    if "nk-app-v114" in exam or "nk-app-v114" in review:
        raise SystemExit("Whole-app renderer leaked into protected CBT/Review question pages")
    if "nk-option-state" in source:
        raise SystemExit("Option-side status holes returned")
    if source.count('id="nk-whole-app-vision-v114"') != 1:
        raise SystemExit("Whole-app style must be installed exactly once")
    if re.search(r"NaN Questions|NaN Topics", source):
        raise SystemExit("Invalid subject-count copy returned")
    apply_subject = section(source, "function applySubject", "applySubject(activeSubject)")
    if "SUBJECTS.flatMap" not in apply_subject:
        raise SystemExit("Question lookup is still limited to the active subject")
    if '<span>Q</span><strong>${esc(title)}</strong>' in source:
        raise SystemExit("Legacy Q tile brand returned")
    if "openSessionBuilder(null,'exam')" in section(source, "function openTestBuilder", "function openModeBuilder"):
        raise SystemExit("App-level CBT still opens the active-subject-only builder")
    print("WHOLE_APP_VISION_OK: professional subject identity, motivational streak, all-subject random practice and multi-subject CBT are installed; protected session UI retained")


if __name__ == "__main__":
    main()
