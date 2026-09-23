#!/usr/bin/env python3
from pathlib import Path
import re


HTML = Path("app/src/main/assets/index.html")


def section(source: str, start: str, end: str) -> str:
    a = source.index(start)
    b = source.index(end, a)
    return source[a:b]


def main() -> None:
    source = HTML.read_text(encoding="utf-8")
    if not re.search(r"function nkQuestionContext\(q\)\s*\{\s*return\s+['\"]{2};\s*\}", source):
        raise SystemExit("Question context helper must render nothing")
    renderers = "".join((
        section(source, "function practicePage()", "function practiceActionBar"),
        section(source, "function examPage()", "function resultPage"),
        section(source, "function reviewTestPage()", "function closeQuestionNavigator"),
    ))
    if 'class="nk-question-context' in renderers:
        raise SystemExit("Subject/chapter context bar markup remains in an active question renderer")
    print("QUESTION_CONTEXT_BAR_OK: absent from Practice, CBT and Review")


if __name__ == "__main__":
    main()
