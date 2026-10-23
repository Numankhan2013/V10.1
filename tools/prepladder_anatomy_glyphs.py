"""Characters anatprep11.pdf could not print, restored from their context.

The PDF draws each lost character as one placeholder glyph
(tools/prepladder_prep11_pdf.py reads it as PLACEHOLDER). Anatomy prints few
formulas; what the rules below leave, the reader takes from the extraction's
text of the same question (`ALIGN`), where the same words surround it.
Placeholders neither restores are bullets, footnote marks or icon rows, and are
dropped.
"""
import re

from prepladder_prep11_pdf import PLACEHOLDER as P

PREFIX = "ANA11"  # figure IDs: ANA11_L<lesson>_Q<number>_<S|E><n>
ALIGN = True
FIXES = [
    # icon rows
    (P + r"{4,}[ " + P + r"]*", " "),
]
TRAILING = re.compile(r"[ \t]*" + P + r"+")  # leftover bullets and footnote marks


def fix(text: str, restore=None) -> str:
    if P not in text:
        return text
    for pattern, value in FIXES:
        text = re.sub(pattern, value, text)
    if restore and P in text:
        text = restore(text)
    text = TRAILING.sub(" ", text)
    return re.sub(r"  +", " ", text).strip()
