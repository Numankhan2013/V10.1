#!/usr/bin/env python3
"""Remove the low-value subject/chapter bar from shared question cards."""
from pathlib import Path


HTML = Path("app/src/main/assets/index.html")


def replace_function(source: str, name: str, replacement: str) -> str:
    start = source.find(f"function {name}(")
    if start < 0:
        raise SystemExit(f"{name} not found")
    brace = source.find("{", start)
    depth = 0
    for index in range(brace, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[:start] + replacement.rstrip() + source[index + 1 :]
    raise SystemExit(f"{name} end not found")


def transform(source: str) -> str:
    return replace_function(source, "nkQuestionContext", "function nkQuestionContext(q) { return ''; }")


def main() -> None:
    source = HTML.read_text(encoding="utf-8")
    transformed = transform(source)
    if "function nkQuestionContext(q) { return ''; }" not in transformed:
        raise SystemExit("Subject/chapter bar removal did not install")
    HTML.write_text(transformed, encoding="utf-8")
    print("QUESTION_CONTEXT_BAR_REMOVED: shared Practice/CBT/Review renderer")


if __name__ == "__main__":
    main()
