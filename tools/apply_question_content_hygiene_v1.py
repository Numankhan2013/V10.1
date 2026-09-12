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


def context(source: str, needle: str, radius: int = 700) -> str:
    index = source.find(needle)
    if index < 0:
        return "<not found>"
    return source[max(0, index-radius):min(len(source), index+len(needle)+radius)].replace("\n", "\\n")


def transform(source: str) -> str:
    core = CORE.read_text(encoding="utf-8").strip()
    source = install_core(source, core)

    old_count = source.count(OLD_REGISTRY_CLEAN)
    marrow_marker_count = source.count("MARROW_BY_SUBJECT")
    bank_marker_count = source.count("BANKS_BY_SUBJECT")
    if old_count != 1:
        raise SystemExit(
            f"Unexpected legacy stem-clean count={old_count}; MARROW_BY_SUBJECT={marrow_marker_count}; "
            f"BANKS_BY_SUBJECT={bank_marker_count}; context={context(source, OLD_REGISTRY_CLEAN)}"
        )

    # Do not guess whether this lone legacy call belongs to the Marrow path. The
    # current generated shell has diverged from the source transformer; emit its
    # exact context so the next patch can target the live Marrow registry safely.
    raise SystemExit(
        f"LIVE_REGISTRY_CONTEXT MARROW_BY_SUBJECT={marrow_marker_count} BANKS_BY_SUBJECT={bank_marker_count} "
        f"legacy={context(source, OLD_REGISTRY_CLEAN)}"
    )


def main() -> None:
    source = HTML.read_text(encoding="utf-8")
    result = transform(source)
    HTML.write_text(result, encoding="utf-8")


if __name__ == "__main__":
    main()
