# Bug hunt — 2026-10-19

Six parallel reviewers audited the app on branch `bug-hunt/2026-10-19`
(from `main` at `25fa6b66`). One file per bug, grouped by area:

| Area | Directory | Scope |
| --- | --- | --- |
| 1 | `01-persistence-sync/` | progress store, durable persistence, cross-device sync, account switching |
| 2 | `02-study-engines/` | Practice, timed CBT, FSRS, checkpoints, session review, revision queues |
| 3 | `03-question-rendering/` | question presentation, content hygiene, interaction, details, source visuals |
| 4 | `04-navigation-ui/` | Home, Topics, Tests, Insights, modules, notes, search, routing |
| 5 | `05-android-pwa-security/` | Android shell, service worker, PWA update, CSP/headers, release packaging |
| 6 | `06-build-data-content/` | bank builders, data contracts, question completeness, content generation |

Every file follows the same shape and ends with a **Main-agent review** block.
The lead reviewer fills that block after checking the evidence and the patch:
`approved` (fix is correct and safe), `flagged` (fix is wrong, incomplete, or
risky), or `needs-work` (direction is right but the patch is not ready).

Ground rules used by all reviewers:

- Read-only on product code. Only the bug files were written.
- Every finding cites exact `file:line` evidence and explains the learner impact.
- No style, naming, or speculative performance findings.
- Known issues already recorded in `.project-memory/STATE.md` or `docs/` were
  not re-reported unless the recorded state is wrong.
- Proposed fixes are minimal diffs, not applied to the app in this branch.
  Nothing here is build-verified or device-verified until CI and a real device
  run it.

## Result

31 findings, all reviewed by the lead. 30 approved, 1 flagged (rejected).

| Area | Findings | high | medium | low | Approved | Flagged / needs-work |
| --- | --- | --- | --- | --- | --- | --- |
| 01 persistence & sync | 6 | 1 | 3 | 2 | 6 | 0 |
| 02 study engines | 5 | 1 | 4 | 0 | 5 | 0 |
| 03 question rendering | 5 | 0 | 4 | 1 | 4 | 1 |
| 04 navigation & UI | 6 | 0 | 3 | 3 | 6 | 0 |
| 05 Android / PWA / security | 6 | 1 | 5 | 0 | 6 | 0 |
| 06 build, data & content | 3 | 0 | 3 | 0 | 3 | 0 |
| **Total** | **31** | **3** | **22** | **6** | **30** | **1** |

Every proposed diff in every file was checked with `git apply --check` against
this checkout and applies cleanly (41 diff blocks across the 31 files).

### The one that matters most

`BUG-03-005` — the page carries a stale inline copy of `nkSourceTakeaway` that
shadows the maintained module version, because both end up in the same script
scope and the later declaration wins. The module's implementation never runs.
Measured over all 10,105 shipped questions, 2,354 "Key takeaway" values are
wrong and 1,940 of them render no takeaway at all — the learner loses the card
on roughly one question in five. The fix is to delete the stale copy, and
`tools/test_app_source_parity.py` should then refuse to let a module and the
page declare the same function again.

### Flagged and rejected

`BUG-03-001` — UWorld question-block figures were reported to render
non-essential, which would make 496 figure-bearing questions permanently
unanswerable. The premise is false: every question-block figure carries
`role: 'question'`, and the build refuses a figure whose role does not
match its slot (`tools/uworld_reviewed_document.py:47`). The shipped
expression already marks them essential. The proposed patch would have
made it worse, because it added a flag that the function never read.
The finding is withdrawn; the file records why, and the one real
observation behind it, with a corrected patch.

### Reworked during review

`BUG-06-001` — the PrepLadder text banks shipped a flat `explanation` string
captured before the restructure overlay, so it no longer matched the structured
blocks the app renders: 2,668 of the 3,982 questions were affected, and 8
Microbiology questions had an empty flat copy although the learner saw a table.
The patch needed rework before it could be applied, and was reworked: the flat
copy is now computed from the same blocks the app renders, and the table
flattening format was decided and stated (the table's title, then one line per
row with the cells joined by two spaces, which is what the app's own
table-aware takeaway picker splits a row on). The three banks were rebuilt, and
357 Key takeaways changed — none lost its card.

## Reproducing the measurements

The two counted findings can be reproduced from this checkout:

```bash
# BUG-03-005: the two nkSourceTakeaway declarations and the one that wins
python3 - <<'PY'
import sys; sys.path.insert(0, 'tools')
from app_page import app_page
page = app_page()
print('declarations:', page.count('function nkSourceTakeaway'))
PY

# BUG-06-001: the flat copy against the shipped structured blocks
python3 - <<'PY'
import base64, json, zlib, sys
from pathlib import Path
sys.path.insert(0, 'tools')
from build_prepladder_microbiology_bank import plain_text
R = Path('.')
def load(slug, prefix):
    parts = sorted((R/'data/Prepladder'/slug).glob(f'{prefix}.zlib.b64.part*'))
    raw = ''.join(p.read_text().strip() for p in parts)
    return json.loads(zlib.decompress(base64.b64decode(raw)))
for slug, prefix in [('microbiology', 'prepladder_microbiology_qbank'),
                     ('pathology', 'prepladder_pathology_qbank'),
                     ('pharmacology', 'prepladder_pharmacology_qbank')]:
    bank = load(slug, prefix)
    bad = 0
    for q in bank['questions']:
        se = q['structuredExplanation']
        if plain_text(se['blocks'], se.get('tables')) != (q.get('explanation') or ''): bad += 1
    print(slug, bad, 'of', len(bank['questions']))
PY
```

