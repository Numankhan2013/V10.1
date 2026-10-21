# BUG-06-003 — 15 Marrow questions ship a stem that points at an image the app never releases, and the completeness gate does not cover the Microbiology bank

- **Area:** 06 build, data & content
- **Severity:** medium
- **Confidence:** high
- **Status:** open — proposed fix, not applied
- **Files:** `tools/marrow_image_coverage.py:27`, `tools/audit_question_structure.py:131`, `tools/queue_question_completeness.py:31`, `app/src/main/assets/marrow_visual_renderer.js:11`, `app/src/main/assets/marrow_visual_renderer.js:5`, `tools/microbiology_visuals.py:122`
- **Introduced by:** unknown (the Microbiology Marrow bank landed on 2026-10-14; the coverage tool was written for the three ED8 banks)

## What happens

Fifteen Marrow questions have a stem that refers to a picture — "Tumbling motility is shown by ______.", "The type of motility shown by Vibrio cholerae is :", "An image of her teeth are shown below" — but the app ships **no question-role figure** for them. Nine of the fifteen have no figure binding at all; the other six have only an *explanation*-role figure, which the renderer deliberately hides until after the answer.

The learner sees a question that says "shown below" with nothing below it. The question is unanswerable: it asks which organism produces a named phenomenon, and the phenomenon was only ever in an image that was never released.

The build does not catch this. The completeness tooling (`tools/audit_question_structure.py`, `tools/queue_question_completeness.py`) and the figure-coverage tool (`tools/marrow_image_coverage.py`) all enumerate exactly three subjects — `('Anatomy', 'Biochemistry', 'Physiology')` — and the Microbiology Marrow bank (726 questions) is outside every one of them.

## Evidence

### The renderer silently shows nothing

`app/src/main/assets/marrow_visual_renderer.js` filters the figures by role and returns without inserting anything when the list is empty:

```javascript
 5:  document.querySelectorAll('[data-marrow-question],[data-marrow-explanation]').forEach(node=>{
 8:    const role=node.hasAttribute('data-marrow-question')?'question':'explanation';
 9:    const id=node.getAttribute('data-marrow-'+role);
10:    const figures=(window.MARROW_VISUALS?.[id]||[]).filter(f=>f.role===role);
11:    if(!figures.length)return;
```

Line 10 filters to `f.role===role`, so an `explanation` figure is never shown for a `question` slot, and line 11 returns silently when nothing matches — no placeholder, no warning, no broken-image marker.

### The 15 affected questions

Evaluating the merged runtime metadata (`app/src/main/assets/marrow_visual_metadata.js` + `app/src/main/assets/microbiology_visual_metadata.js`) against the shipped Marrow questions, using the same text cue the repository's own queue tool uses (`tools/queue_question_completeness.py:43`):

```
ALL marrow questions with a figure cue but no released QUESTION figure: 15
by subject: {"Anatomy":1,"Biochemistry":1,"Microbiology":13}

--- questions with NO figure entries at all (any role): 9
    marrow__BIOCHEM_CH17_Q014 | An infant presented with delayed eruption of her teeth. An image of her ...
    marrow__MICRO_CH05_Q004   | A positive catalase test and bacitracin sensitivity are shown by _____.
    marrow__MICRO_CH06_Q022   | Tumbling motility is shown by _______.
    marrow__MICRO_CH10_Q002   | The type of motility shown by Vibrio cholerae is :
    marrow__MICRO_CH10_Q017   | Kanagawa phenomenon is shown by ________.
    marrow__MICRO_CH10_Q022   | Darting motility shown by Vibrio cholerae is also observed in
    marrow__MICRO_CH10_Q038   | Kanagawa phenomenon is shown by _________.
    marrow__MICRO_CH22_Q021   | Reynolds-Braude phenomenon is shown by _____
    marrow__MICRO_CH24_Q011   | Falling leaf motility is shown by ________.

--- questions whose only figures are explanation-role: 6
    marrow__ANAT_CH45_Q004    | The region marked corresponds to the surface marking for which of the fo
    marrow__MICRO_CH05_Q005   | Which factor forms the basis of co-agglutination reaction shown by Staph
    marrow__MICRO_CH07_Q005   | Stormy fermentation of lactose in milk is shown by
    marrow__MICRO_CH07_Q033   | M'Fadyean's reaction is shown by
    marrow__MICRO_CH09_Q035   | Bipolar staining or safety pin appearance is shown by _________.
    marrow__MICRO_CH12_Q004   | Type of motility shown by T.pallidum?
```

For example, `marrow__MICRO_CH10_Q002` — "The type of motility shown by Vibrio cholerae is :" — has an empty `MARROW_VISUALS` entry:

```
=== marrow__MICRO_CH10_Q002 | The type of motility shown by Vibrio cholerae is :
   MARROW_VISUALS: []
```

The six explanation-only cases are confirmed to have the figure but in the wrong slot:

```
=== marrow__MICRO_CH07_Q005 | Stormy fermentation of lactose in milk is shown by
   MARROW_VISUALS: [{"id":"...","role":"explanation",...}]
```

### The completeness gate does not cover the Microbiology bank

`tools/marrow_image_coverage.py` fixes the subject list at line 27:

```python
27: SUBJECTS = ('Anatomy', 'Biochemistry', 'Physiology')
```

and asserts every registry entry is one of them (lines 92 and 114). The registry itself holds 1,308 assets and **zero** Microbiology ones:

```
$ python3 -c "
import json
r=json.load(open('data/marrow/images/registry.json'))
ids=[a.get('questionId') for a in r['assets']]
print('registry assets', len(ids))
print('microbiology ones:', len([i for i in ids if i and 'MICRO' in i]))
"
registry assets 1308
microbiology ones: 0
```

`data/marrow/images/coverage.json` has the same three-subject summary, so `sourceVisualCoverageComplete` is never computed for Microbiology at all.

The structural audit has the same blind spot — `tools/audit_question_structure.py:131`:

```python
131:    for prefix in ("anatomy_ch001_063", "biochemistry_ch001_028", "physiology_ch001_043"):
```

and `tools/queue_question_completeness.py:31` only looks at those banks:

```python
31:    flagged = {qid for qid, q in raw.items()
32:               if str(q.get('reviewStatus', '')).startswith('needs_manual_review')}
```

where `raw` comes from `load_marrow()`, i.e. the same three prefixes.

The result is visible in the generated queue: all 15 of these questions are **absent** from `build/question-fidelity/completeness-review-queue.json`. Only two of the 44 figure-cue questions across all Marrow banks have a review decision, and the other 42 have none:

```
44-ish figure-cue questions without a released question figure: 44
decisions found: {(('CONTEXTUAL_RECONSTRUCTION', 'review-visual-gap-3.json'),): 2}
NO review decision found for: 42
```

### Microbiology's own validator cannot see the gap either

`tools/microbiology_visuals.py:122` `validate()` checks that the released figures match the figures the extraction produced:

```python
126:    expected = {image["image_id"] for _, image in source_images()}
...
137:    assert seen == expected, f"figures differ from JSONL images: missing=..."
```

That is a round-trip check on what *was* extracted. It cannot detect that the extraction itself never produced a question figure for a stem that needs one — there is no comparison against the stem's text cue.

## Learner impact

Wrong visible information, and a flow that cannot be completed. The learner is shown "Tumbling motility is shown by _______." with no image, and asked to pick an organism from four options with no way to know which test is being shown. The question is scored like any other, so an answer chosen at random is recorded as a real attempt and pollutes the learner's progress and FSRS statistics. 13 of the 15 are in Microbiology, which is a bank the learner can practise; the two others are one Anatomy question ("The region marked corresponds to the surface marking for which of the following structures") and one Biochemistry question (an image of a child's teeth).

Nothing is lost and the app does not crash, and a learner who already knows the answer can still answer it, so this is `medium` rather than `high`.

## Root cause

The figure-completeness tooling was written for the three canonical ED8 banks and its subject list was never extended when the Microbiology Marrow bank was added. `tools/marrow_image_coverage.py` has a hard-coded `SUBJECTS` tuple; `tools/audit_question_structure.py` and `tools/queue_question_completeness.py` hard-code the three shard prefixes. Microbiology's own validator is a round-trip check against its own extraction, not a check against the stem text. So the whole chain of gates is blind to a class of defect — a stem that refers to a picture — for exactly one bank.

## Proposed fix

Two changes. First, extend the coverage tool's subject list to include Microbiology and make the completeness queue able to see the Microbiology bank. Second, and independently, make the *builder* refuse to ship a stem whose text cue promises an image that the bank does not bind — that is the gate that actually prevents the class of defect, and it belongs where the data is produced.

The builder-side gate is the important one. `tools/build_microbiology_marrow_bank.py` already has a question-iteration loop that fails on missing figure metadata; add the cue check there:

```diff
--- a/tools/build_microbiology_marrow_bank.py
+++ b/tools/build_microbiology_marrow_bank.py
@@ -699,6 +699,12 @@
             fail(f"{mcq}: correct_answer_text differs from the keyed option text")
         stem = str(q.get("question_stem") or "").strip()
         if not stem or any(not str(o.get("text", "")).strip() for o in options):
+            # A stem that points at a picture ("shown below", "the region marked")
+            # is unanswerable without one: the figure must be bound as a question
+            # figure, not only as an explanation figure.
+            if QUESTION_FIGURE_CUE.search(stem) and not any(
+                    f.get("location") == "question_stem" for f in q.get("images") or []):
+                fail(f"{mcq}: stem refers to a figure the bank does not bind")
             fail(f"{mcq}: blank stem or option")
         hygiene = Hygiene()
         blocks, tables = parse_v2(q, hygiene) if q.get("_schema") == 2 else parse_markdown(q, hygiene)
```

with the cue and the lookup defined next to the builder's other helpers:

```python
QUESTION_FIGURE_CUE = re.compile(
    r"\b(?:shown|depicted|illustrated)\b"
    r"|\b(?:structure|area|region|organ|part|nerve)\s+(?:marked|labelled|labeled)\b"
    r"|\b(?:marked|labelled|labeled)\s+(?:structure|area|region)\b"
    r"|\b(?:image|figure|diagram|graph|photograph)\s+(?:below|above|given)\b",
    re.I,
)
```

This reuses the same cue the repository already applies in `tools/queue_question_completeness.py:43`, so the two agree on what "points at a picture" means.

Then extend the coverage tool so the Microbiology bank is audited like the others:

```diff
--- a/tools/marrow_image_coverage.py
+++ b/tools/marrow_image_coverage.py
@@ -24,7 +24,7 @@
 DEFAULT_PAGE_REVIEWS = DATA / 'images/source_reference_page_reviews.json'
 DEFAULT_CUE_REVIEWS = DATA / 'images/source_text_cue_reviews.json'
 DEFAULT_DISCOVERY_REVIEWS = DATA / 'images/source_visual_discoveries.json'
-SUBJECTS = ('Anatomy', 'Biochemistry', 'Physiology')
+SUBJECTS = ('Anatomy', 'Biochemistry', 'Physiology', 'Microbiology')
 ADJUDICATION_STATUS = 'SOURCE_METADATA_INVALID'
 
 
```

and widen the audit's bank list so the queue can see Microbiology:

```diff
--- a/tools/audit_question_structure.py
+++ b/tools/audit_question_structure.py
@@ -128,7 +128,7 @@
 
 def load_marrow() -> tuple[list, dict]:
     records, hashes = [], {}
-    for prefix in ("anatomy_ch001_063", "biochemistry_ch001_028", "physiology_ch001_043"):
+    for prefix in ("anatomy_ch001_063", "biochemistry_ch001_028", "physiology_ch001_043", "microbiology_marrow_qbank"):
         parent = ROOT / "data/marrow"
         manifest = json.loads((parent / f"{prefix}_manifest.json").read_text())
         parts = sorted(parent.glob(f"{prefix}.zlib.b64.part*"))
```

**Before applying the coverage-tool change, note that it is a larger change than the builder gate.** `tools/marrow_image_coverage.py` asserts every registry entry's subject is one of `SUBJECTS` (lines 92 and 114), but the registry holds no Microbiology assets at all — the Microbiology figures live in `data/marrow/images/` under a separate manifest and are released by `tools/microbiology_visuals.py`. Wiring Microbiology into the shared coverage tool therefore requires reconciling two registries, which is a bigger piece of work than this bug needs. The safe sequence is:

1. Apply the builder gate first. It will fail the build on the 15 questions, which is the correct outcome — those questions must not ship as they are.
2. Release the missing question figures from the source PDF pages (the crops already exist for six of them as explanation figures; they need to be re-bound with `role: "question"`), or withdraw the 15 questions from the bank until their figures are released.
3. Only then widen the coverage tool's subject list, so the shared gate covers Microbiology too.

If step 2 is judged too large for one change, the minimal containment is the builder gate alone plus a note in `docs/MARROW_BANK_INTEGRATION.md` that the shared coverage tooling does not yet cover Microbiology.

## Verification

- Reproduce, then verify the fix:
  1. Before the fix: `python3 tools/build_microbiology_marrow_bank.py` succeeds while 13 Microbiology questions ship with a figure cue and no question figure. Evaluate the merged `window.MARROW_VISUALS` and list the affected ids.
  2. After the fix: the builder fails with `marrow__MICRO_CH10_Q002: stem refers to a figure that the bank does not bind`.
  3. After the figures are released or the questions withdrawn: the builder succeeds and no question in the shipped bank has a figure cue without a `role: "question"` figure.
- Existing test to extend: `tools/test_microbiology_marrow_bank.py` already asserts figure completeness (`MICROBIOLOGY_MARROW_TEST_OK questions=726 topics=25 figures=235 incomplete={}`). Add the cue check there: for every question whose stem matches the cue, assert a question-role figure exists.
- Also worth adding to `tools/test_marrow_bank_pilot.py` for the two non-Microbiology cases.
- Regressions to re-check: the figure viewer and the explanation-figure path (an explanation-only figure must still stay out of the question slot), and the Anatomy/Biochemistry banks that legitimately have no question figures.

## Alternatives considered

Making the renderer show a visible placeholder ("This question's figure could not be loaded.") instead of silently rendering nothing would help the learner understand something is missing, but it does not make the question answerable and it hides a data defect behind a UI fix. The builder gate is the correct place: the defect is that the bank ships a question whose essential content is absent.

Renaming the six explanation-role figures to `role: "question"` would fix six of the fifteen immediately, but those figures were extracted as *explanation* images (they are the answer's supporting material, not the stem's image) and re-binding them would put the answer's evidence in front of the learner before they answer — that is exactly the failure mode the "questionUnchanged/optionsUnchanged" contract in `docs/question-completeness/review-batch-3.json` was written to avoid.

## Main-agent review

- **Verdict:** approved
- **Checked evidence:** yes
- **Checked patch:** yes
- **Notes:** Verified marrow_visual_renderer.js:10-11 (figures are filtered by role and the function returns silently when the list is empty) and the shipped runtime metadata: 15 Marrow questions have a stem that points at a picture but no question-role figure, 9 with no figure binding at all and 6 whose only figure is explanation-role, which the renderer deliberately hides until after the answer. Verified that the completeness tooling cannot see them: marrow_image_coverage.py:27 fixes SUBJECTS to the three ED8 subjects, audit_question_structure.py:131 hard-codes the same three shard prefixes, and the Microbiology figures live in a separate registry (the marrow registry holds 1,308 assets and zero Microbiology ones), so none of the 15 appear in the review queue. The builder-side cue gate is the right primary fix; the diff now uses the builder own location vocabulary (question_stem). Approved, with the sequencing note in the file kept: the coverage-tool widening depends on reconciling two registries and should follow the builder gate, not replace it.
