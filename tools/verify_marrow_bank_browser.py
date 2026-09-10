#!/usr/bin/env python3
"""Run the full Marrow browser regression core with current taxonomy assertions."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "tools" / "verify_marrow_bank_browser_core.py"

source = CORE.read_text(encoding="utf-8")

replacements = {
    "            for marker in ('PrepLadder','Marrow','753'):": "            for marker in ('PrepLadder','Marrow','1,014'):",
    "            if page.locator('button.nk-topic-row').count()!=33: raise SystemExit('Marrow Physiology topic count is not 33')": "            if page.locator('button.nk-topic-row').count()!=43: raise SystemExit('Marrow Physiology topic count is not 43')",
}
for old, new in replacements.items():
    if source.count(old) != 1:
        raise SystemExit(f"Physiology browser source-count anchor count for {old!r}: {source.count(old)}")
    source = source.replace(old, new, 1)

old = "            assert_sections(['CNS Physiology','General Physiology','Cellular Physiology','Neuromuscular Physiology','Cardiovascular System','Respiratory System','Gastrointestinal System'])"
new = """            assert_sections(['General physiology','Nerve and muscle physiology','Gastrointestinal system','Cardiovascular system','Respiratory system','Renal physiology','Endocrine physiology','Reproductive physiology','Central nervous system','Integrated physiology'])
            pnums=[int(x) for x in page.locator('.nk-topic-index').all_inner_texts()]
            if pnums!=list(range(1,44)): raise SystemExit(f'Marrow Physiology learner numbering is not contiguous 1-43: {pnums!r}')

            # New automation-ingested content must render as normal learner content,
            # never as serialized JSON/schema text.
            page.locator('button.nk-topic-row').filter(has_text='Exercise Physiology').click();page.wait_for_timeout(80)
            if page.locator('button.nk-library-row').count()!=16: raise SystemExit('Marrow Physiology Exercise Physiology count is not 16')
            page.locator('button.nk-library-row').nth(0).click();page.wait_for_timeout(80)
            learner_text=page.locator('body').inner_text()
            for raw_marker in ('chapter_number','source_provenance','source_answer','schema_version','review_status','source_fidelity_notes'):
                if raw_marker in learner_text: raise SystemExit(f'Raw automation JSON key leaked into learner view: {raw_marker}')
            for raw_fragment in ('{\"chapter\"','\"source_answer\":','\"source_provenance\":'):
                if raw_fragment in learner_text: raise SystemExit(f'Serialized automation JSON leaked into learner view: {raw_fragment}')
            if not page.locator('.question-text').inner_text().strip(): raise SystemExit('Exercise Physiology source question did not render as a learner question')
            page.evaluate(\"window.QB.nav('banks','Physiology')\");page.wait_for_timeout(80)
            page.locator('button.nk-bank-card').filter(has_text='Marrow').click();page.wait_for_timeout(80)"""
if source.count(old) != 1:
    raise SystemExit(f"Physiology browser taxonomy assertion anchor count: {source.count(old)}")
source = source.replace(old, new, 1)

old_summary = "biochemistry=543/26 physiology=753/33 total=2115"
new_summary = "biochemistry=543/26 physiology=1014/43 physiology_plan=42 physiology_numbering=contiguous raw_json=clean total=2376"
if source.count(old_summary) != 1:
    raise SystemExit(f"Marrow browser summary anchor count: {source.count(old_summary)}")
source = source.replace(old_summary, new_summary, 1)

exec(
    compile(source, str(CORE), "exec"),
    {"__name__": "__main__", "__file__": str(CORE), "__builtins__": __builtins__},
)
