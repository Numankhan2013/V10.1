#!/usr/bin/env python3
"""Adapt the historical Marrow browser suite to the canonical two-bank Subject flow."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / "tools" / "verify_marrow_bank_browser_legacy.py"
wrapper = LEGACY.read_text(encoding="utf-8")
anchor = '\nexec(\n    compile(source, str(CORE), "exec"),'
if wrapper.count(anchor) != 1:
    raise SystemExit(f"legacy exec anchor count={wrapper.count(anchor)}")

compat = r'''
import re as _re

_EXPECTED_MARROW_COUNTS={
    'Biochemistry':'582',
    'Physiology':'1,014',
    'Anatomy':'1,115',
}


def _chooser_steps(subject, click_marrow=True, screenshot=None, invoke=True):
    lines=[]
    if invoke:
        lines.append("            page.evaluate(\"window.QB.nkOpenSubjectLibrary('" + subject + "')\")")
    lines.extend([
        # This is an SPA. Verify the rendered chooser itself rather than relying
        # on a particular hash serialization or a navigation-event race.
        "            page.wait_for_function(\"() => document.querySelectorAll('button.nk-bank-card').length===2\",timeout=5000)",
        "            prep=page.locator('button.nk-bank-card').filter(has_text='PrepLadder')",
        "            marrow=page.locator('button.nk-bank-card').filter(has_text='Marrow')",
        "            if prep.count()!=1: raise SystemExit('" + subject + " PrepLadder card missing')",
        "            if marrow.count()!=1: raise SystemExit('" + subject + " Marrow card missing')",
        "            prep.wait_for(state='visible',timeout=5000)",
        "            marrow.wait_for(state='visible',timeout=5000)",
        "            chooser_text=page.locator('body').inner_text()",
        "            if '" + subject + "' not in chooser_text: raise SystemExit('" + subject + " chooser subject label missing')",
        "            if '" + _EXPECTED_MARROW_COUNTS[subject] + "' not in chooser_text: raise SystemExit('" + subject + " chooser missing canonical Marrow count " + _EXPECTED_MARROW_COUNTS[subject] + "')",
    ])
    if screenshot:
        lines.append("            page.screenshot(path=str(OUT/'" + screenshot + "'),full_page=True)")
    if click_marrow:
        lines.extend([
            "            marrow.click(timeout=5000)",
            "            page.wait_for_function(\"() => document.querySelectorAll('button.nk-topic-row').length>0\",timeout=5000)",
        ])
    return "\n".join(lines)


def _subject_entry(subject, shot):
    global source
    esc = _re.escape(subject)
    pattern = (
        r"            page\.locator\('button\.nk-subject-row'\)\.filter\(has_text='" + esc + r"'\)\.click\(\)"
        r"(?:;page\.wait_for_timeout\(\d+\)|\n            page\.wait_for_timeout\(\d+\))\n"
        r".*?"
        r"            [A-Za-z_]*cards\.filter\(has_text='Marrow'\)\.click\(\);page\.wait_for_timeout\(\d+\)"
    )
    chooser_shot = "00-" + subject.lower() + "-bank-chooser.png"
    actual_click = "            page.locator('button.nk-v3-subject-card').filter(has_text='" + subject + "').click()"
    replacement = actual_click + "\n" + _chooser_steps(subject, click_marrow=True, screenshot=chooser_shot, invoke=False) + "\n            page.screenshot(path=str(OUT/'" + shot + "'),full_page=True)"
    source, n = _re.subn(pattern, replacement, source, count=1, flags=_re.S)
    if n != 1:
        raise SystemExit(f"{subject} initial chooser adapter count={n}")


_subject_entry('Biochemistry', '00-biochemistry-topics.png')
_subject_entry('Physiology', '00-physiology-topics.png')
_subject_entry('Anatomy', '01-anatomy-topics.png')

# All historical jumps back to a Marrow subject now traverse and visibly verify
# the real bank chooser. Rendered-state waits replace fragile fixed-delay/hash races.
for _subject in ('Biochemistry','Physiology','Anatomy'):
    esc = _re.escape(_subject)
    pattern = (
        r"            page\.evaluate\(\"window\.QB\.nav\('banks','" + esc + r"'\)\"\);page\.wait_for_timeout\(\d+\)\n"
        r"            page\.locator\('button\.nk-bank-card'\)\.filter\(has_text='Marrow'\)\.click\(\);page\.wait_for_timeout\(\d+\)"
    )
    source = _re.sub(pattern, _chooser_steps(_subject), source)

# Wrong Questions was intentionally retired from the learner dashboard in favor
# of the FSRS review surface. The dedicated FSRS/history suites own persistence
# and review eligibility, so remove only this obsolete dashboard-path assertion.
wrong_start = "            # Reproduce the user-reported path without reaching into module-scoped state.\n"
wrong_end = "                raise SystemExit(f'Wrong Questions answer colors regressed: correct={wrong_green} wrong={wrong_red}')\n"
if wrong_start in source:
    ws = source.index(wrong_start)
    we_marker = source.find(wrong_end, ws)
    if we_marker < 0:
        raise SystemExit("obsolete Wrong Questions adapter end marker missing")
    we = we_marker + len(wrong_end)
    source = source[:ws] + source[we:]

# Full canonical source/taxonomy expectations.
for old,new in (
    ("for marker in ('PrepLadder','Marrow','543')","for marker in ('PrepLadder','Marrow','582')"),
    ("for marker in ('PrepLadder','Marrow','753')","for marker in ('PrepLadder','Marrow','1,014')"),
    ("for marker in ('PrepLadder','Marrow','1,068','819')","for marker in ('PrepLadder','Marrow','1,068','1,115')"),
    ("count()!=26: raise SystemExit('Marrow Biochemistry topic count is not 26')","count()!=28: raise SystemExit('Marrow Biochemistry topic count is not 28')"),
    ("list(range(1,27))","list(range(1,29))"),
    ("numbering is not contiguous 1-26","numbering is not contiguous 1-28"),
    ("count()!=33: raise SystemExit('Marrow Physiology topic count is not 33')","count()!=43: raise SystemExit('Marrow Physiology topic count is not 43')"),
    ("count()!=48: raise SystemExit('Marrow Anatomy topic count is not 48')","count()!=63: raise SystemExit('Marrow Anatomy topic count is not 63')"),
    ("range(1,49)","range(1,64)"),
    ("biochemistry=543/26","biochemistry=582/28"),
    ("physiology=753/33","physiology=1014/43"),
    ("anatomy=819/48","anatomy=1115/63"),
    ("total=2115","total=2711"),
    ("enhanced=184 rationales=552","enhanced=576 pending=2135"),
    ("enhanced=429 pending=2282","enhanced=576 pending=2135"),
):
    source = source.replace(old,new)

source = source.replace(
    "assert_sections(['CNS Physiology','General Physiology','Cellular Physiology','Neuromuscular Physiology','Cardiovascular System','Respiratory System','Gastrointestinal System'])",
    "assert_sections(['General physiology','Nerve and muscle physiology','Gastrointestinal system','Cardiovascular system','Respiratory system','Renal physiology','Endocrine physiology','Reproductive physiology','Central nervous system','Integrated physiology'])",
)
source = source.replace(
    "assert_sections(['Embryology','Histology','Neuroanatomy','Head, neck, and face','Upper limb','Thorax','Abdomen and pelvis'])",
    "assert_sections(['Embryology','Histology','Neuroanatomy','Head, neck, and face','Upper limb','Thorax','Abdomen and pelvis','Lower limb','Back','General anatomy'])",
)
source = source.replace(
    "            if any(x in page.locator('body').inner_text() for x in ('Lower limb\\n0 topics','Back\\n0 topics','General anatomy\\n0 topics')):\n                raise SystemExit('Unimported Anatomy planned section leaked as an empty learner-facing group')\n",
    "",
)

# User-reported explanation bug: Ch5 Q1 must render the approved tuned layer.
shot = "            page.screenshot(path=str(OUT/'01-anatomy-topics.png'),full_page=True)"
extra = shot + """
            page.locator('button.nk-topic-row').filter(has_text='Pharyngeal arches, Skeletal & Muscular Systems').click();page.wait_for_timeout(100)
            page.locator('button.nk-library-row').nth(0).click();page.wait_for_timeout(100)
            page.locator('.option-list button').nth(2).click();page.wait_for_timeout(140)
            body=page.locator('body').inner_text()
            if 'Each pharyngeal arch has a mesenchymal core formed by mesoderm and invading neural crest cells.' not in body:
                raise SystemExit('Anatomy Ch5 Q1 tuned takeaway missing from learner runtime')
            if 'outer surface of the arch' not in body or 'inner surface of the pharyngeal apparatus' not in body:
                raise SystemExit('Anatomy Ch5 Q1 approved distractor rationales missing from learner runtime')
""" + _chooser_steps('Anatomy') + "\n"
if source.count(shot) != 1:
    raise SystemExit(f"Anatomy tuned insertion anchor count={source.count(shot)}")
source = source.replace(shot, extra, 1)
'''

wrapper = wrapper.replace(anchor, "\n" + compat + anchor, 1)
exec(compile(wrapper, str(LEGACY), "exec"), {"__name__":"__main__", "__file__":str(LEGACY), "__builtins__":__builtins__})