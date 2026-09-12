#!/usr/bin/env python3
"""Install conservative learner-facing Marrow text sanitation and source-footer cleanup."""

from pathlib import Path

from apply_marrow_topic_numbering_v1 import main as apply_marrow_topic_numbering


HTML = Path("app/src/main/assets/index.html")
CORE = Path("tools/question_content_hygiene_core.js")
START = "/* NK_QUESTION_CONTENT_HYGIENE_V1_START */"
END = "/* NK_QUESTION_CONTENT_HYGIENE_V1_END */"
OLD_CLEANING = "  SUBJECTS.forEach(record=>(record.questions||[]).forEach(question=>{question.question=nkCleanQuestionStem(question.question);}));"
NEW_CLEANING = "  SUBJECTS.forEach(record=>(record.questions||[]).forEach(question=>nkSanitizeMarrowQuestion(question)));"


def replace_function(source: str, name: str, replacement: str) -> str:
    start = source.find(f"function {name}(")
    if start < 0:
        raise SystemExit(f"{name} not found")
    brace = source.find("{", start)
    depth = 0
    quote = None
    escaped = False
    for index in range(brace, len(source)):
        char = source[index]
        if quote:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
            continue
        if char in "'\"`":
            quote = char
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[:start] + replacement.rstrip() + source[index + 1 :]
    raise SystemExit(f"{name} end not found")


def install_core(source: str, core: str) -> str:
    if START in source or END in source:
        if source.count(START) != 1 or source.count(END) != 1:
            raise SystemExit("Question hygiene marker count is not exactly one pair")
        start = source.index(START)
        end = source.index(END, start) + len(END)
        return source[:start] + core + source[end:]
    return replace_function(source, "nkSourceTakeaway", core)


def transform(source: str) -> str:
    core = CORE.read_text(encoding="utf-8").strip()
    source = install_core(source, core)

    subject_marker = "  const SUBJECT_BY_NAME = Object.fromEntries(SUBJECTS.map(x=>[x.subject,x]));"
    if subject_marker not in source:
        raise SystemExit("Subject registry marker not found")

    if NEW_CLEANING not in source:
        if OLD_CLEANING in source:
            source = source.replace(OLD_CLEANING, NEW_CLEANING, 1)
        else:
            source = source.replace(subject_marker, subject_marker + "\n" + NEW_CLEANING, 1)

    if source.count(NEW_CLEANING) != 1:
        raise SystemExit(f"Expected exactly one Marrow sanitation hook, found {source.count(NEW_CLEANING)}")
    return source


def main() -> None:
    source = HTML.read_text(encoding="utf-8")
    result = transform(source)
    HTML.write_text(result, encoding="utf-8")
    # Whole-app Topics is installed earlier in the deterministic pipeline. Apply
    # the Marrow-only learner serial patch here so reordered taxonomies keep
    # immutable source chapter IDs while displaying contiguous arranged numbers.
    apply_marrow_topic_numbering()
    print("Applied conservative Marrow learner-text sanitation and question-source cleanup.")


if __name__ == "__main__":
    main()
