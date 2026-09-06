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
        "window.QB.startAllPractice()",
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
    print("WHOLE_APP_VISION_OK: all non-question routes themed; actions retained; protected session engine untouched")


if __name__ == "__main__":
    main()
