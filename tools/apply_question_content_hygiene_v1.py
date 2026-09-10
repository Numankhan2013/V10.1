#!/usr/bin/env python3
"""Install comparison-safe takeaways and remove source footer metadata from stems."""

from pathlib import Path

from apply_marrow_topic_numbering_v1 import main as apply_marrow_topic_numbering


HTML = Path("app/src/main/assets/index.html")
CORE = Path("tools/question_content_hygiene_core.js")
START = "/* NK_QUESTION_CONTENT_HYGIENE_V1_START */"
END = "/* NK_QUESTION_CONTENT_HYGIENE_V1_END */"


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


def transform(source: str) -> str:
    if START in source:
        return source
    core = CORE.read_text(encoding="utf-8").strip()
    source = replace_function(source, "nkSourceTakeaway", core)
    subject_marker = "  const SUBJECT_BY_NAME = Object.fromEntries(SUBJECTS.map(x=>[x.subject,x]));"
    if subject_marker not in source:
        raise SystemExit("Subject registry marker not found")
    cleaning = "\n  SUBJECTS.forEach(record=>(record.questions||[]).forEach(question=>{question.question=nkCleanQuestionStem(question.question);}));"
    return source.replace(subject_marker, subject_marker + cleaning, 1)


def main() -> None:
    source = HTML.read_text(encoding="utf-8")
    result = transform(source)
    HTML.write_text(result, encoding="utf-8")
    # Whole-app Topics is installed earlier in the deterministic pipeline. Apply
    # the Marrow-only learner serial patch here so reordered taxonomies keep
    # immutable source chapter IDs while displaying contiguous arranged numbers.
    apply_marrow_topic_numbering()
    print("Applied comparison-safe takeaways and cleaned question-source metadata.")


if __name__ == "__main__":
    main()
