#!/usr/bin/env python3
"""Install conservative learner-facing Marrow text sanitation and source-footer cleanup."""

from pathlib import Path


HTML = Path("app/src/main/assets/index.html")
CORE = Path("tools/question_content_hygiene_core.js")
START = "/* NK_QUESTION_CONTENT_HYGIENE_V1_START */"
END = "/* NK_QUESTION_CONTENT_HYGIENE_V1_END */"
SUBJECT_MARKER = "  const SUBJECT_BY_NAME = Object.fromEntries(SUBJECTS.map(x=>[x.subject,x]));"
OLD_REGISTRY_CLEAN = "question.question=nkCleanQuestionStem(question.question);"
NEW_REGISTRY_CLEAN = "nkSanitizeMarrowQuestion(question);"


def install_core(source: str, core: str) -> str:
    if START in source or END in source:
        if source.count(START) != 1 or source.count(END) != 1:
            raise SystemExit("Question hygiene marker count is not exactly one pair")
        start = source.index(START)
        end = source.index(END, start) + len(END)
        return source[:start] + core + source[end:]

    if source.count(SUBJECT_MARKER) != 1:
        raise SystemExit(f"Subject registry marker count: {source.count(SUBJECT_MARKER)}")
    return source.replace(SUBJECT_MARKER, core + "\n" + SUBJECT_MARKER, 1)


def transform(source: str) -> str:
    core = CORE.read_text(encoding="utf-8").strip()
    source = install_core(source, core)

    # The current bank architecture registers PrepLadder and MARROW_BY_SUBJECT
    # separately. Replace the already-established per-question footer-cleaning
    # call at those registry boundaries, rather than guessing at data layout.
    old_count = source.count(OLD_REGISTRY_CLEAN)
    if old_count:
        source = source.replace(OLD_REGISTRY_CLEAN, NEW_REGISTRY_CLEAN)
    new_count = source.count(NEW_REGISTRY_CLEAN)
    if new_count < 2:
        raise SystemExit(f"Expected sanitation at both bank registry paths, found {new_count}")
    if old_count and old_count != new_count:
        raise SystemExit(f"Registry sanitation replacement mismatch: old={old_count} new={new_count}")

    if source.count(START) != 1 or source.count(END) != 1:
        raise SystemExit("Expected exactly one installed hygiene core marker pair")
    return source


def main() -> None:
    source = HTML.read_text(encoding="utf-8")
    result = transform(source)
    HTML.write_text(result, encoding="utf-8")
    print("Applied conservative Marrow learner-text sanitation at bank registry boundaries.")


if __name__ == "__main__":
    main()
