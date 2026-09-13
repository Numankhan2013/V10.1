#!/usr/bin/env python3
"""Install conservative learner-facing content hygiene.

The deterministic build invokes this once before Marrow is installed and a
second time from the post-Marrow renderer step. The transform is intentionally
idempotent: PrepLadder keeps its existing footer cleanup, while the second pass
upgrades the generated Marrow bank-registration loops to sanitize learner-facing
stems, options, and explanations without mutating canonical source bundles.
"""

from pathlib import Path


HTML = Path("app/src/main/assets/index.html")
CORE = Path("tools/question_content_hygiene_core.js")
START = "/* NK_QUESTION_CONTENT_HYGIENE_V1_START */"
END = "/* NK_QUESTION_CONTENT_HYGIENE_V1_END */"
SUBJECT_MARKER = "  const SUBJECT_BY_NAME = Object.fromEntries(SUBJECTS.map(x=>[x.subject,x]));"
PREP_HOOK = "  SUBJECTS.forEach(record=>(record.questions||[]).forEach(question=>nkSanitizeMarrowQuestion(question)));"
REGISTRY_OLD = "(record.questions||[]).forEach(question=>{\n      question.question=nkCleanQuestionStem(question.question);"
REGISTRY_NEW = "(record.questions||[]).forEach(question=>{\n      nkSanitizeMarrowQuestion(question);"


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
    # Post-Marrow generated registries have two identical per-question cleanup
    # blocks (PrepLadder + Marrow). Replace those before refreshing the helper
    # core so the helper's own non-Marrow branch can never be mistaken for a
    # registry call.
    registry_old_count = source.count(REGISTRY_OLD)
    if registry_old_count not in (0, 2):
        raise SystemExit(f"Unexpected generated bank cleanup block count: {registry_old_count}")
    if registry_old_count == 2:
        source = source.replace(REGISTRY_OLD, REGISTRY_NEW)

    core = CORE.read_text(encoding="utf-8").strip()
    source = install_core(source, core)

    if SUBJECT_MARKER not in source:
        raise SystemExit("Subject registry marker not found")
    if PREP_HOOK not in source:
        source = source.replace(SUBJECT_MARKER, SUBJECT_MARKER + "\n" + PREP_HOOK, 1)
    if source.count(PREP_HOOK) != 1:
        raise SystemExit(f"Expected exactly one PrepLadder hygiene hook, found {source.count(PREP_HOOK)}")

    registry_new_count = source.count(REGISTRY_NEW)
    if registry_old_count == 2 and registry_new_count != 2:
        raise SystemExit(f"Expected two upgraded generated-bank hooks, found {registry_new_count}")
    if source.count(START) != 1 or source.count(END) != 1:
        raise SystemExit("Expected exactly one installed hygiene core marker pair")
    return source


def main() -> None:
    source = HTML.read_text(encoding="utf-8")
    result = transform(source)
    HTML.write_text(result, encoding="utf-8")
    post_marrow = result.count(REGISTRY_NEW) == 2
    print(
        "QUESTION_CONTENT_HYGIENE_APPLIED "
        f"prep_hook=1 post_marrow={'yes' if post_marrow else 'no'} "
        f"generated_bank_hooks={result.count(REGISTRY_NEW)}"
    )


if __name__ == "__main__":
    main()
