# BUG-06-003 — 15 Marrow questions ship a stem that points at an image the app never releases, and the completeness gate does not cover the Microbiology bank

- **Area:** 06 build, data & content
- **Severity:** medium
- **Confidence:** high
- **Status:** resolved 2026-10-22 — 13 cue false positives kept in the bank, 3 questions withdrawn at the app boundary, 1 mis-bound figure repaired (see Resolution)
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
@@ -29,6 +29,29 @@
 from pathlib import Path
 
 ROOT = Path(__file__).resolve().parents[1]
+# A stem that points at a picture is unanswerable without one: the figure must
+# be bound as a question figure, not only as an explanation figure, which the
+# renderer deliberately hides until after the answer. The cue is the one the
+# completeness queue already applies (tools/queue_question_completeness.py).
+QUESTION_FIGURE_CUE = re.compile(
+    r"\b(?:shown|depicted|illustrated)\b"
+    r"|\b(?:structure|area|region|organ|part|nerve)\s+(?:marked|labelled|labeled)\b"
+    r"|\b(?:marked|labelled|labeled)\s+(?:structure|area|region)\b"
+    r"|\b(?:image|figure|diagram|graph|photograph)\s+(?:below|above|given)\b",
+    re.I,
+)
+# These questions still ship a stem that refers to a picture the bank does not
+# release. Each one needs either the source figure released with a question
+# role or the question withdrawn from the bank; until that content work is
+# done the gate must not block the build for them. A question outside this list
+# that trips the gate fails the build.
+PENDING_QUESTION_FIGURES = {
+    "MICRO_CH05_Q004", "MICRO_CH05_Q005", "MICRO_CH06_Q022", "MICRO_CH07_Q005",
+    "MICRO_CH07_Q033", "MICRO_CH09_Q035", "MICRO_CH10_Q002", "MICRO_CH10_Q017",
+    "MICRO_CH10_Q022", "MICRO_CH10_Q038", "MICRO_CH12_Q004", "MICRO_CH22_Q021",
+    "MICRO_CH24_Q011",
+}
+
 DATA = ROOT / "data/marrow"
 SOURCE_DIR = DATA / "microbiology/source"
 PREFIX = "microbiology_marrow_qbank"
@@ -658,6 +681,22 @@
     return "\n\n".join(x for x in out if x.strip())
 
 
+def check_question_figure(qid: str, stem: str, images: list[dict]) -> None:
+    """A stem that points at a picture must have a released question figure.
+
+    The figure has to be bound as a question figure, not only as an
+    explanation figure: the renderer hides explanation figures until after
+    the answer, so an explanation-only figure leaves the question unreadable.
+    """
+    if not QUESTION_FIGURE_CUE.search(stem):
+        return
+    if any(image.get("location") == "question_stem" for image in images or []):
+        return
+    if qid in PENDING_QUESTION_FIGURES:
+        return
+    fail(f"{qid}: stem refers to a figure the bank does not bind")
+
+
 def normalize(rows: list[dict]) -> dict:
     modules: dict[int, dict] = {}
     questions: list[dict] = []
@@ -700,6 +739,8 @@
         stem = str(q.get("question_stem") or "").strip()
         if not stem or any(not str(o.get("text", "")).strip() for o in options):
             fail(f"{mcq}: blank stem or option")
+        qid = f"MICRO_CH{module_index:02d}_Q{number:03d}"
+        check_question_figure(qid, stem, q.get("images") or [])
         hygiene = Hygiene()
         blocks, tables = parse_v2(q, hygiene) if q.get("_schema") == 2 else parse_markdown(q, hygiene)
         table_map = {t["table_id"]: t for t in tables}
@@ -712,7 +753,6 @@
         for img in q.get("images") or []:
             figures.append({k: img.get(k) for k in ("image_id", "location", "type", "caption", "source_page", "bounding_box", "in_pearl", "pearl_id")})
         flags = list((q.get("provenance") or {}).get("quality_flags") or [])
-        qid = f"MICRO_CH{module_index:02d}_Q{number:03d}"
         record = {
             "id": f"marrow__{qid}",
             "sourceQuestionId": qid,
--- a/tools/test_microbiology_marrow_bank.py
+++ b/tools/test_microbiology_marrow_bank.py
@@ -20,7 +20,9 @@
     subprocess.run([sys.executable, str(ROOT / "tools/build_microbiology_marrow_bank.py"), "--check"], check=True)
     manifest = json.loads((ROOT / f"data/marrow/{MICROBIOLOGY_PREFIX}_manifest.json").read_text(encoding="utf-8"))
     # Every JSONL part, mapped onto the full PDF pages and app modules (PART_LAYOUT).
-    from build_microbiology_marrow_bank import load_source, MODULE_OVERRIDES
+    from build_microbiology_marrow_bank import (
+        load_source, MODULE_OVERRIDES, QUESTION_FIGURE_CUE, PENDING_QUESTION_FIGURES, check_question_figure,
+    )
     raw_rows = load_source()[0]
 
     record = microbiology_record()
@@ -85,6 +87,45 @@
         '<script defer src="microbiology_visual_metadata.js"></script>',
     ):
         assert page.count(marker) == 1, marker
+    # A stem that points at a picture must have a released question figure, so
+    # the learner is never asked about an image that is not there.
+    for q, raw in zip(questions, raw_rows):
+        stem = raw["question_stem"].strip()
+        if not QUESTION_FIGURE_CUE.search(stem):
+            continue
+        figures = (q.get("structuredExplanation") or {}).get("figures") or []
+        has_question_figure = any(f.get("location") == "question_stem" for f in figures)
+        if not has_question_figure:
+            assert q["sourceQuestionId"] in PENDING_QUESTION_FIGURES, (
+                f"{q['id']} points at a picture the bank does not bind and is not a known pending question"
+            )
+    # The builder must run the gate over every question it ships.
+    import build_microbiology_marrow_bank as builder
+    checked: list[str] = []
+    original_gate = builder.check_question_figure
+    builder.check_question_figure = lambda qid, stem, images: checked.append(qid)
+    try:
+        builder.normalize(raw_rows)
+    finally:
+        builder.check_question_figure = original_gate
+    assert len(checked) == len(questions), "the builder must check every question for a figure cue"
+    assert all(q["sourceQuestionId"] in checked for q in questions), "the gate must run for every question"
+
+    # The gate must fire for a question that is not on the pending list.
+    try:
+        check_question_figure("MICRO_CH99_Q999", "Tumbling motility is shown by _______.", [])
+    except SystemExit as error:
+        assert "stem refers to a figure the bank does not bind" in str(error), error
+    else:
+        raise AssertionError("the figure gate must reject a stem that points at an unbound picture")
+    # A stem with a released question figure passes, and a stem without a cue is not checked.
+    check_question_figure("MICRO_CH99_Q999", "Tumbling motility is shown by _______.",
+                          [{"image_id": "x", "location": "question_stem"}])
+    check_question_figure("MICRO_CH99_Q999", "Which organism causes cholera?", [])
+    # A pending question is reported, not blocked.
+    for qid in PENDING_QUESTION_FIGURES:
+        check_question_figure(qid, "Tumbling motility is shown by _______.", [])
+
     print(f"MICROBIOLOGY_MARROW_TEST_OK questions={len(questions)} topics={len(record['topics'])} "
           f"figures={len(visuals['figures'])} incomplete={manifest['incompleteTopics']}")
 
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
- **Notes:** The finding is correct and was measured again during review. The proposed patch was wrong in two ways and was reworked before being applied; the coverage-tool widening was deliberately left out of this change.

The evidence checks out. Merging `marrow_visual_metadata.js` with `microbiology_visual_metadata.js` and testing the cue against the shipped Marrow banks gives exactly 15 questions: 1 Anatomy, 1 Biochemistry and 13 Microbiology, with no Physiology question affected. The cue also matches 153 Anatomy, 21 Biochemistry and 20 Physiology stems that DO have a released question figure, so the cue alone is not a defect signal — what matters is the cue together with a missing question-role figure, and the builder must look at the figures it binds.

The proposed patch had two problems. Its cue check was nested inside the `if not stem or any(blank option)` branch, so it could only ever run for a question that was already failing for another reason. And it introduced `QUESTION_FIGURE_CUE` in the prose without adding it to the file, so the diff did not compile.

The applied change:

- `tools/build_microbiology_marrow_bank.py` gains `QUESTION_FIGURE_CUE` and `check_question_figure(qid, stem, images)`, which fails the build when a stem that points at a picture has no image bound with `location: "question_stem"`. The check is called for every question the builder normalizes, outside the blank-stem branch.
- The 13 Microbiology questions that ship today are listed in `PENDING_QUESTION_FIGURES` with a comment saying what has to happen to each of them. Without that list the gate would fail the build on the 13 questions that are already shipped, which would break `tools/test_microbiology_marrow_bank.py` and therefore CI, so the gate cannot simply be switched on. The list keeps the build green while making the debt explicit and bounded: any question outside the list that trips the gate fails the build.
- `tools/test_microbiology_marrow_bank.py` checks the bank for cue-without-figure questions, asserts the builder runs the gate over every question, asserts the gate rejects an unknown question, and asserts a pending question is reported rather than blocked.

**The learner-facing defect is not fixed by this change.** The 15 questions still ship with a stem that refers to a picture that is not there. Releasing the source figures with a question role, or withdrawing the questions, is content work that needs the source PDFs and the image registry, and it is recorded as the next step rather than done here. The widening of `tools/marrow_image_coverage.py` and `tools/audit_question_structure.py` to cover Microbiology is also left for after that, because it depends on reconciling the two figure registries.

So this change installs the gate that stops the class of defect from growing and names the 15 that still need attention; it does not make those 15 answerable.


## Resolution — 2026-10-22

The reported count of 15 was a cue problem plus two genuine gaps, not 15 unanswerable questions.

- **13 Microbiology stems were false positives.** "Tumbling motility is shown by ___", "Kanagawa phenomenon is shown by ___" and the rest use "shown by" as ordinary question wording, not as an image reference. The original cue matched the bare verb `shown`. The builder cue now requires visual deixis (`shown below`, `the image shows`, `the region marked`, `in the figure`, ...). All 13 questions are answerable without a figure and still ship. `PENDING_QUESTION_FIGURES` is empty and `tools/test_microbiology_marrow_bank.py` asserts both that the gate rejects a real visual stem without a figure and that a verbal "shown by" stem passes.
- **Three questions are genuinely unanswerable and are withheld.** `marrow__ANAT_CH45_Q004` (only the unreleased unmarked page-816 candidate exists), `marrow__BIOCHEM_CH17_Q014` (source review confirms no teeth image was ever printed) and `marrow__MICRO_CH18_Q013` (the cited chest X-ray was never extracted; only the GMS stain exists). The authoritative ledger is `data/marrow/withdrawn_questions_v1.json`; `tools/marrow_bank_data.py` removes those IDs from `app_marrow_records()` and recomputes topic counts, while the canonical shards and audits keep the records.
- **One released figure was in the wrong slot, not missing.** `marrow__PHYSIO_CH35_Q020` ("The following picture shows the composition of solute in the urine and plasma sample of 3 patients") had its bar chart released as `physiology-region-ff76eff3b68bd593` but bound with role `explanation`. The registry binding is now role `question` and the runtime metadata was regenerated.
- **Counts:** the app now ships 3,434 Marrow questions (Anatomy 1,114 / Biochemistry 581 / Physiology 1,014 / Microbiology 725). The canonical ED8 source remains 2,711.
- **Regression:** `tools/test_marrow_withdrawn_questions_v1.py` asserts the ledger entries, their absence from the app, untouched source records, exact topic counts, that the 13 false positives still ship, and that the Physiology asset is mounted as a question figure. `tools/build_app_data.py` validates Biochemistry explanation batches against the canonical source, not the filtered app record.
- **Not done here:** the shared coverage/structural tooling still enumerates only the three ED8 subjects. Widening it to Microbiology still needs the two figure registries reconciled, as the original finding says.
