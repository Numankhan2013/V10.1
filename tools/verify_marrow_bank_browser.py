#!/usr/bin/env python3
"""Run the full Marrow browser suite against the canonical V3 subject→Topics flow.

The historical suite remains the regression authority for question rendering,
images, explanations, answer states, FSRS, source PDFs, PrepLadder isolation and
responsive behavior. This adapter changes only obsolete Marrow entry navigation
and Phase-A corpus/taxonomy expectations.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / "tools" / "verify_marrow_bank_browser_legacy.py"
wrapper = LEGACY.read_text(encoding="utf-8")
anchor = "\nexec(\n    compile(source, str(CORE), \"exec\"),"
if wrapper.count(anchor) != 1:
    raise SystemExit(f"Legacy Marrow browser exec anchor count: {wrapper.count(anchor)}")

compat = r'''
# Canonical V3 compatibility: Marrow is the preferred subject library, so a
# learner subject card goes straight to Topics rather than an intermediate
# PrepLadder/Marrow selector. Keep every downstream browser assertion intact.
import re as _re

def _replace_initial_subject_entry(subject, screenshot_name):
    global source
    escaped = _re.escape(subject)
    pattern = (
        r"            page\.locator\('button\.nk-subject-row'\)\.filter\(has_text='" + escaped + r"'\)\.click\(\)"
        r"(?:;page\.wait_for_timeout\(\d+\)|\n            page\.wait_for_timeout\(\d+\))\n"
        r".*?"
        r"            [A-Za-z_]*cards\.filter\(has_text='Marrow'\)\.click\(\);page\.wait_for_timeout\(\d+\)"
    )
    replacement = (
        "            page.evaluate(\"window.QB.nkOpenSubjectLibrary('" + subject + "')\");page.wait_for_timeout(120)\n"
        "            page.screenshot(path=str(OUT/'" + screenshot_name + "'),full_page=True)"
    )
    source, count = _re.subn(pattern, replacement, source, count=1, flags=_re.S)
    if count != 1:
        raise SystemExit(f'Canonical V3 initial {subject} navigation adapter count: {count}')

_replace_initial_subject_entry('Biochemistry', '00-biochemistry-topics.png')
_replace_initial_subject_entry('Physiology', '00-physiology-topics.png')
_replace_initial_subject_entry('Anatomy', '01-anatomy-topics.png')

# Historical Marrow-only jumps used the now-hidden bank selector. Replace only
# jumps that explicitly select Marrow; PrepLadder selector checks remain intact.
for _subject in ('Biochemistry', 'Physiology', 'Anatomy'):
    _escaped = _re.escape(_subject)
    _pattern = (
        r"            page\.evaluate\(\"window\.QB\.nav\('banks','" + _escaped + r"'\)\"\);page\.wait_for_timeout\(\d+\)\n"
        r"            page\.locator\('button\.nk-bank-card'\)\.filter\(has_text='Marrow'\)\.click\(\);page\.wait_for_timeout\(\d+\)"
    )
    _replacement = "            page.evaluate(\"window.QB.nkOpenSubjectLibrary('" + _subject + "')\");page.wait_for_timeout(120)"
    source = _re.sub(_pattern, _replacement, source)

# The legacy Physiology expansion duplicated persistence coverage by requiring a
# Home quick-grid "Wrong questions" entry after one seeded miss. Canonical V3
# owns this through FSRS/history persistence tests instead; the quick-access
# surface is not part of the Marrow content contract. Keep the preceding real
# red/green answer assertion and resume the browser suite from Physiology Topics.
_wrong_path_pattern = (
    r"            # Reproduce the user-reported path without reaching into module-scoped state\.\n"
    r"            page\.evaluate\(\"window\.QB\.nav\('dashboard'\)\"\);page\.wait_for_timeout\(100\)\n"
    r".*?"
    r"            page\.evaluate\(\"window\.QB\.nkOpenSubjectLibrary\('Physiology'\)\"\);page\.wait_for_timeout\(120\)"
)
_wrong_replacement = (
    "            # Wrong-answer persistence/review-only eligibility is verified "
    "by the dedicated FSRS/history regressions.\n"
    "            page.evaluate(\"window.QB.nkOpenSubjectLibrary('Physiology')\");page.wait_for_timeout(120)"
)
source, _wrong_count = _re.subn(_wrong_path_pattern, _wrong_replacement, source, count=1, flags=_re.S)
if _wrong_count != 1:
    raise SystemExit(f'Canonical V3 obsolete Wrong Questions path adapter count: {_wrong_count}')

# Complete-corpus counts and learner-visible numbering.
source = source.replace("for marker in ('PrepLadder','Marrow','543')", "for marker in ('PrepLadder','Marrow','582')")
source = source.replace("for marker in ('PrepLadder','Marrow','753')", "for marker in ('PrepLadder','Marrow','1,014')")
source = source.replace("for marker in ('PrepLadder','Marrow','1,068','819')", "for marker in ('PrepLadder','Marrow','1,068','1,115')")
source = source.replace("count()!=26: raise SystemExit('Marrow Biochemistry topic count is not 26')", "count()!=28: raise SystemExit('Marrow Biochemistry topic count is not 28')")
source = source.replace("list(range(1,27))", "list(range(1,29))")
source = source.replace("numbering is not contiguous 1-26", "numbering is not contiguous 1-28")
source = source.replace("count()!=33: raise SystemExit('Marrow Physiology topic count is not 33')", "count()!=43: raise SystemExit('Marrow Physiology topic count is not 43')")
source = source.replace("count()!=48: raise SystemExit('Marrow Anatomy topic count is not 48')", "count()!=63: raise SystemExit('Marrow Anatomy topic count is not 63')")
source = source.replace("range(1,49)", "range(1,64)")

# The source-complete taxonomy now exposes all verified sections. These are
# authoritative section orders from topic_index_taxonomy.json.
source = source.replace(
    "assert_sections(['CNS Physiology','General Physiology','Cellular Physiology','Neuromuscular Physiology','Cardiovascular System','Respiratory System','Gastrointestinal System'])",
    "assert_sections(['General physiology','Nerve and muscle physiology','Gastrointestinal system','Cardiovascular system','Respiratory system','Renal physiology','Endocrine physiology','Reproductive physiology','Central nervous system','Integrated physiology'])",
)
source = source.replace(
    "assert_sections(['Embryology','Histology','Neuroanatomy','Head, neck, and face','Upper limb','Thorax','Abdomen and pelvis'])",
    "assert_sections(['Embryology','Histology','Neuroanatomy','Head, neck, and face','Upper limb','Thorax','Abdomen and pelvis','Lower limb','Back','General anatomy'])",
)

# These groups are now populated, so only the old empty-placeholder assertion is
# obsolete; the section/order assertion above positively verifies them instead.
source = source.replace(
    "            if any(x in page.locator('body').inner_text() for x in ('Lower limb\\n0 topics','Back\\n0 topics','General anatomy\\n0 topics')):\n                raise SystemExit('Unimported Anatomy planned section leaked as an empty learner-facing group')\n",
    "",
)

# Final status strings used by the historical suite.
source = source.replace("biochemistry=543/26", "biochemistry=582/28")
source = source.replace("physiology=753/33", "physiology=1014/43")
source = source.replace("anatomy=819/48", "anatomy=1115/63")
source = source.replace("total=2115", "total=2711")
source = source.replace("enhanced=184 rationales=552", "enhanced=429 pending=2282")
'''

wrapper = wrapper.replace(anchor, "\n" + compat + anchor, 1)
exec(
    compile(wrapper, str(LEGACY), "exec"),
    {"__name__": "__main__", "__file__": str(LEGACY), "__builtins__": __builtins__},
)
