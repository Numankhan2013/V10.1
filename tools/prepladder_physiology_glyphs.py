"""Characters prep11physio.pdf could not print, restored from their context.

The PDF draws each lost character as one placeholder glyph
(tools/prepladder_prep11_pdf.py reads it as PLACEHOLDER): "Na■" is Na⁺, "HCO3■"
is HCO₃⁻, "PO2■■" is PO₂. The rules below cover the ions and gas tensions the
PDF prints throughout. What they leave, the reader takes from the extraction's
text of the same question (`ALIGN`), where the same words surround it: "B-■■■"
is "B-PAH", "di■erent" is "different", "■-subunits" is "β-subunits". Placeholders
neither restores are bullets, footnote marks or icon rows, and are dropped.
"""
import re

from prepladder_prep11_pdf import PLACEHOLDER as P

PREFIX = "PHY11"  # figure IDs: PHY11_L<lesson>_Q<number>_<S|E><n>
ALIGN = True
FIXES = [
    # icon rows
    (P + r"{4,}[ " + P + r"]*", " "),
    # embryonic and adult haemoglobins
    (r"Gower 1 ζ 2 " + P + " 2", "Gower 1 ζ₂ε₂"), (r"Gower 2 α 2 " + P + " 2", "Gower 2 α₂ε₂"),
    (r"Portland ζ 2 " + P + " 2", "Portland ζ₂γ₂"), ("Hb-A" + P + r" α 2 δ 2", "Hb-A₂ α₂δ₂"),
    # gas tensions: "PO2■■", "PaCO■", "CO■", "O■"
    (r"\b([pP]a?C?O)2 ?" + P + P, r"\1₂"),
    (r"(?<![A-Za-z])((?:[pP]a?)?C?O)" + P + r"(?!" + P + ")", r"\1₂"),
    # ions
    (r"HCO ?3 ?" + P, "HCO₃⁻"), ("HCO" + P + P, "HCO₃⁻"), ("H2PO4" + P, "H₂PO₄⁻"), (r"NH4 ?" + P, "NH₄⁺"),
    (r"(Ca|Mg)²" + P, r"\1²⁺"), ("Fe³" + P, "Fe³⁺"),
    (r"\b(Na|K|H) ?" + P + r"(?: (?=-))?", r"\1⁺"), (r"\bCl ?" + P + r"(?: (?=-))?", "Cl⁻"),
    ("voltage" + P + "gated", "voltage-gated"),
    # worked figures
    ("= " + P + r" x 100 = 80%", "= (4/5) × 100 = 80%"), ("transit time = " + P + r" x 0\.75", "transit time = 1/3 × 0.75"),
    ("at " + P + "4 atm", "at ≥4 atm"),
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
