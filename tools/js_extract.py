#!/usr/bin/env python3
"""Extract a JavaScript function declaration from a source file.

The app's modules and the assembled page hold their functions as plain
declarations, so a test can take one out and drive it directly. Finding the
end of a declaration means matching braces, and braces also appear inside
string, template and regex literals, so the scan tracks literal context the
way a JavaScript parser would.
"""

from __future__ import annotations

import re

# A regular expression literal may start where an expression may start.
_REGEX_PRECEDERS = "(,=:[!&|?{};+-*%~^"


def extract_function(text: str, name: str, indent: str = "  ") -> str:
    """The last declaration of `name` in `text`, with its body.

    The last declaration wins in JavaScript, so the last one is the one the
    app runs.
    """
    needle = f"{indent}function {name}("
    start = text.rindex(needle)
    index = start + len(needle) - 1  # the '(' of the parameter list
    depth = 0
    previous = ""
    length = len(text)
    while index < length:
        char = text[index]
        if char in "'\"":
            quote = char
            index += 1
            while index < length and text[index] != quote:
                index += 2 if text[index] == "\\" else 1
            index += 1
            previous = "x"
            continue
        if char == "`":
            index += 1
            while index < length:
                if text[index] == "\\":
                    index += 2
                    continue
                if text[index] == "`":
                    index += 1
                    break
                index += 1
            previous = "x"
            continue
        if char == "/" and index + 1 < length:
            following = text[index + 1]
            if following == "/":
                while index < length and text[index] != "\n":
                    index += 1
                continue
            if following == "*":
                index += 2
                while index + 1 < length and not (text[index] == "*" and text[index + 1] == "/"):
                    index += 1
                index += 2
                continue
            if previous == "" or previous in _REGEX_PRECEDERS:
                index += 1
                in_class = False
                while index < length:
                    if text[index] == "\\":
                        index += 2
                        continue
                    if text[index] == "[":
                        in_class = True
                    elif text[index] == "]":
                        in_class = False
                    elif text[index] == "/" and not in_class:
                        index += 1
                        break
                    index += 1
                while index < length and text[index].isalpha():
                    index += 1
                previous = "x"
                continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
        if not char.isspace():
            previous = char
        index += 1
    raise AssertionError(f"function {name} is not closed in the source")


def extract_assignment(text: str, target: str) -> str:
    """The module-level `let`/`const` declaration of `target`."""
    pattern = re.compile(r"^\s*(?:let|const|var)\s+" + re.escape(target) + r"\s*=", re.M)
    match = pattern.search(text)
    if not match:
        raise AssertionError(f"{target} is not declared")
    start = match.start()
    end = text.index("\n", match.end())
    return text[start:end].strip()
