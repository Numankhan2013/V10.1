"""Characters biochemprep11.pdf could not print, restored from their context.

The PDF draws each lost character as one placeholder glyph
(tools/prepladder_prep11_pdf.py reads it as PLACEHOLDER): "CO■" is CO₂,
"HCO■■" is HCO₃⁻, "■-1,4" is α-1,4. Each rule was checked against the
explanation around it. Placeholders no rule names are footnote marks, table-row
marks or icon rows, and are dropped.
"""
import re

from prepladder_prep11_pdf import PLACEHOLDER as P

PREFIX = "BIO11"  # figure IDs: BIO11_L<lesson>_Q<number>_<S|E><n>
FIXES = [
    # icon rows and footnote marks
    (P + r"{4,}[ " + P + r"]*", " "),
    (r"Mitochondria " + P + "+", "Mitochondria"),
    # formulas
    ("H" + P + "O" + P, "H₂O₂"), ("H2" + P + "O", "H₂O"), ("H" + P + "O", "H₂O"),
    ("HCO" + P + P, "HCO₃⁻"), ("HNO" + P, "HNO₂"), ("NO" + P + P, "NO₃⁻"), ("NO" + P, "NO•"),
    (r"NH 3 " + P + " " + P + r"\+", "NH₃ +"), (r"NH 3 " + P, "NH₃"),
    (r"\(-NH" + P + P + r"\)", "(-NH₃⁺)"), (r"NH" + P + P, "NH₄⁺"),
    (r"ammonia \(NH" + P + r"\)", "ammonia (NH₃)"), (r"\+ NH" + P + r" \+", "+ NH₃ +"), ("NH" + P, "NH₂"),
    ("pCO" + P, "pCO₂"), ("CO" + P, "CO₂"), ("FADH" + P, "FADH₂"), ("BH" + P, "BH₄"),
    ("CH" + P + "CONH", "CH₃CONH"), (r"\(-CH" + P + r"\) to", "(-CH₃) to"), (r"-CH" + P + r", -CH" + P, "-CH₂, -CH₃"),
    ("–CH" + P + "–", "–CH₂–"), ("5,10-CH" + P + "-H" + P, "5,10-CH₂-H₄"), ("H" + P + "-folate", "H₄-folate"),
    ("N" + P + ", N¹" + P, "N⁵, N¹⁰"), ("N" + P + ",N¹" + P, "N⁵,N¹⁰"), ("THFA" + P, "THFA"),
    ("α" + P + "β" + P + " α" + P + "γ" + P, "α₂β₂ α₂γ₂"), ("α" + P + " and γ" + P, "α₂ and γ₂"),
    (r"\(T" + P + r"\)", "(T₄)"), ("O" + P, "O₂"), ("bc" + P, "bc₁"),
    (r"The F" + P + " portion, which is embedded", "The F₀ portion, which is embedded"),
    ("the F" + P + " portion", "the F₁ portion"), ("the F" + P + " component", "the F₀ component"),
    ("T" + P + "B" + P + "NK" + P, "T⁻B⁻NK⁻"), ("10" + P + "¹" + P, "10⁻¹⁵"),
    # ions
    (r"(Mg|Ca|Fe|Cu)²" + P, r"\1²⁺"), ("Fe³" + P, "Fe³⁺"), (r"\b(NADP|NAD|Na|K|H)" + P, r"\1⁺"),
    (r"\b(Cl|CN)" + P, r"\1⁻"),
    # Greek letters
    (P + "-1,4", "α-1,4"), ("7-" + P + "-hydroxylase", "7-α-hydroxylase"), (P + "-Glucosidase", "β-Glucosidase"),
    ("enzyme " + P + " ALA", "enzyme δ-ALA"), ("presence of " + P + " ALAsynthase", "presence of δ-ALA synthase"),
    # arrows and signs
    ("ATP" + P + " AMP", "ATP → AMP"), (r"5\.9 " + P + " 6", "5.9 ≈ 6"), (r"\( " + P + " urease", "(↓ urease"),
    ("Ammonia " + P + "-Amide", "Ammonia; Amide"),
    (r"v=Km" + P + r"\+\[S\]Vmax" + P + r"\[S\]" + P, "v = Vmax[S] / (Km + [S])"),
    (r"(Vmax|Km) ?" + P, r"\1"),
    (r" " + P + r" (?=[A-Za-z])", " → "),
]
TRAILING = re.compile(r"[ \t]*" + P + r"+")  # leftover footnote and row marks


def fix(text: str) -> str:
    if P not in text:
        return text
    for pattern, value in FIXES:
        text = re.sub(pattern, value, text)
    text = TRAILING.sub("", text)
    return re.sub(r"  +", " ", text).strip()
