#!/usr/bin/env python3
"""Regression checks for the V11.4 whole-app visual transformation."""

from pathlib import Path
import re
from app_page import app_page


HTML = Path("app/src/main/assets/index.html")


def section(source: str, start: str, end: str) -> str:
    a = source.index(start)
    b = source.index(end, a)
    return source[a:b]


def function_section(source: str, start: str) -> str:
    a = source.index(start)
    next_function = re.search(r"\n\s*function [A-Za-z_$][\w$]*\(", source[a + len(start):])
    if not next_function:
        raise SystemExit(f"No function follows {start}")
    return source[a:a + len(start) + next_function.start()]


def main() -> None:
    source = app_page()
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
        # Home V3 (nk-home-command-center-v1) and the focused Tests page later replaced the V11.4 Home/Tests shells.
        'class="nk-home-approved-v1 nk-home-command-center"',
        'class="nk-app-v114 nk-topics-v114"',
        'class="nk-app-v114 nk-chapter-v114"',
        'class="nk-new-test-v2 nk-tests-focused"',
        'class="nk-app-v114 nk-analytics-v114 nk-learning-insights"',
        'class="nk-app-v114 nk-more-v114"',
        'class="nk-app-v114 nk-library-v114"',
        'class="nk-app-v114 nk-result-v114"',
        "window.QB.nkOpenSubjectLibrary('${esc(x.subject)}')",
        "window.QB.openMultiSubjectTestBuilder()",
        "startAllSubjectPractice,",
        "window.QB.startLibrary('${kind}')",
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
    apply_subject = section(source, "function applySubject", "applySubject(activeSubject,activeBank)")
    all_banks = section(source, "function nkAllBankQuestionsBuild(", "function nkAllBankQuestions(")
    if "BY_ID=Object.fromEntries(nkAllBankQuestions()" not in apply_subject or "Object.values(BANKS_BY_SUBJECT)" not in all_banks:
        raise SystemExit("Question lookup is still limited to the active subject")
    if '<span>Q</span><strong>${esc(title)}</strong>' in source:
        raise SystemExit("Legacy Q tile brand returned")
    if "openSessionBuilder(null,'exam')" in section(source, "function openTestBuilder", "function openModeBuilder"):
        raise SystemExit("App-level CBT still opens the active-subject-only builder")
    more = function_section(source, "function morePage()")
    for duplicate in ("row('test','Timed CBT'", "row('chart','Insights'", "row('book','Topics'", "row('clock','Due review'", "row('book','Create module'"):
        if duplicate in more:
            raise SystemExit(f"More retained a duplicate launcher: {duplicate}")
    # Learning Insights replaced the expandable topic list with a capped, sortable one.
    insights = function_section(source, "function analytics()")
    content = function_section(source, "function nkLearningContent(model)")
    topics = function_section(source, "function nkLearningTopics(model)")
    if "nkLearningContent(model)" not in insights or "nkLearningTopics(model)" not in content or ".slice(0,6)" not in topics or "window.QB.nkLearningSetTopics(" not in topics:
        raise SystemExit("Insights topic list is not capped and sortable")
    print("WHOLE_APP_VISION_OK: professional subject identity, motivational streak, all-subject random practice and multi-subject CBT are installed; protected session UI retained")


if __name__ == "__main__":
    main()
