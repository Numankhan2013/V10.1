# BUG-06-001 — The PrepLadder text banks ship an `explanation` string that no longer matches the structured blocks the app renders

- **Area:** 06 build, data & content
- **Severity:** medium
- **Confidence:** high
- **Status:** open — proposed fix, not applied
- **Files:** `tools/prepladder_text_bank.py:327`, `tools/prepladder_text_bank.py:367`, `tools/build_prepladder_microbiology_bank.py:505`, `tools/build_prepladder_microbiology_bank.py:507`, `app/src/main/assets/index.html:1448`
- **Introduced by:** unknown (the `explanation` field predates the restructure overlay)

## What happens

Every PrepLadder text-bank question (Microbiology, Pathology, Pharmacology) carries two copies of its explanation: a flat `explanation` string and an ordered `structuredExplanation` with paragraphs, bullet lists and tables. The app renders the **structured** one as the "Detailed explanation" and reads the **flat** one when it computes the "Key takeaway".

The builder fills the flat `explanation` from the blocks *before* it applies the restructure overlay, so the two copies diverge. For 1,416 of 1,459 Pathology questions and 1,309 of 1,321 Pharmacology questions the flat string is not the flat rendering of the structured blocks the learner actually sees. In 81 of them the divergence is total: the flat `explanation` still holds the original run-together PDF prose while the structured blocks hold only a table, so the Key takeaway is computed from text that is no longer on screen — and in 34 Pharmacology questions the flat string is the *only* place the original prose survives, so the learner and the takeaway are reading different documents.

## Evidence

`tools/prepladder_text_bank.py` computes the flat explanation at line 327, then applies the overlay at lines 328–331, and finally stores both at lines 366–369:

```python
327:                explanation = micro.plain_text(self.reopen(app_id, blocks, reopened) if reopened else blocks)
328:                if app_id in restructured:
329:                    blocks = self.apply_overlay(app_id, blocks, tables, restructured[app_id])
330:                if reopened:
331:                    blocks = self.reopen(app_id, blocks, reopened)
...
366:                    "explanation": explanation,
367:                    "structuredExplanation": {"layout": "ordered-blocks", "blocks": [references_block(b) for b in blocks],
368:                                              "tables": tables,
369:                                              "figures": sorted(i["image_id"] for i in stem_images + explain_images)},
```

`explanation` is captured before `apply_overlay` replaces `blocks`, so it is always the pre-restructure prose.

The Microbiology builder has the same shape (`tools/build_prepladder_microbiology_bank.py:505` and `:507`):

```python
505:                "explanation": plain_text(blocks),
...
507:                "structuredExplanation": {"layout": "ordered-blocks", "blocks": blocks, "tables": tables,
```

Reproducing against the shipped shards (`data/Prepladder/{pathology,pharmacology}/prepladder_*_qbank.zlib.b64.part*`, base64 → zlib → JSON) and re-deriving the flat text from the shipped `structuredExplanation.blocks` the way `micro.plain_text` does:

```
=== pathology questions where shipped `explanation` != plain(blocks): 1416 of 1459
=== pharmacology questions where shipped `explanation` != plain(blocks): 1309 of 1321
```

Concrete example — `pharmacology-1-2`:

```
shipped `explanation`:
  "Medication Schedule Insulin Schedule G Hepatitis B vaccine Schedule H Morphine Schedule X
   Veterinary drugs Schedule Z Schedules of drugs as per the Drugs and Cosmetics Act of India: ..."
flat text of the shipped structured blocks:
  "Schedules of drugs as per the Drugs and Cosmetics Act of India:"
```

The learner sees only "Schedules of drugs as per the Drugs and Cosmetics Act of India:" plus a table; the Key takeaway is computed from the long run-together string above.

Another — `pharmacology-2-1`:

```
shipped `explanation`:
  "Warfarin is metabolised by CYP2C9. Drugs metabolised by CYP2C19: PPI: Omeprazole (Option B) &
   lansoprazole. Amitriptyline. Citalopram. ..."
flat text of the shipped structured blocks:
  "Warfarin is metabolised by CYP2C9.\n\nDrugs metabolised by CYP2C19:\n\n• PPI: Omeprazole (Option B)
   & lansoprazole.\n• Amitriptyline.\n• Citalopram. ..."
```

Same words, but the flat copy has no line structure, so the table-aware takeaway picker (`nkTableTakeaway`, `question_content_hygiene.js:129`) sees one long run of prose and cannot pick a cell, while the structured copy is a list the learner can read.

Counting the cases where the flat text is *empty* although the structured blocks carry content — i.e. the learner sees a table but the flat copy is gone:

```
pathology   : 47 questions
pharmacology: 34 questions
```

`app/src/main/assets/index.html:1448` is where the flat copy is read for the takeaway:

```javascript
1448:    let source=String(q?.explanation||'').replace(/\r/g,'\n');
```

## Learner impact

Wrong visible information. The "Key takeaway" card is derived from a version of the explanation the learner is not looking at. On the 81 questions where the two diverge completely the takeaway is drawn from text that no longer appears anywhere on the screen, and on the ~2,700 where they diverge in structure the takeaway picker cannot use the table/list layout the learner sees. The learner does not lose the explanation itself — the structured copy renders correctly — but the one-line summary of it is computed against the wrong document. This is `medium`: wrong visible information with a workaround (read the explanation), not data loss and not a wrong score.

## Root cause

The builder treats `explanation` and `structuredExplanation` as two independent renderings of one source and computes each from a different point in the pipeline. `explanation` is snapshotted at line 327, before the restructure overlay and before the hand-written-opening repair, and is never recomputed afterwards. `structuredExplanation` is built at lines 367–369 from the final `blocks`. Once the overlay moves prose into tables and lists, the two can no longer be derived from one another.

## Proposed fix

Compute the flat `explanation` from the **final** blocks, after the overlay and the opening repair, so the two copies always describe the same document. `micro.plain_text` already renders paragraphs, headings and bullet lists; the restructure overlay's tables need their cells flattened into the plain copy too, otherwise the 81 table-only questions still end up with an empty flat string.

```diff
--- a/tools/prepladder_text_bank.py
+++ b/tools/prepladder_text_bank.py
@@ -324,7 +324,6 @@
                 reopened = openings.pop(app_id, None)
                 if reopened and not opening and not reopened.get("lead"):
                     self.fail(f"{app_id}: hand-written opening for an explanation that opens whole")
-                explanation = micro.plain_text(self.reopen(app_id, blocks, reopened) if reopened else blocks)
                 if app_id in restructured:
                     blocks = self.apply_overlay(app_id, blocks, tables, restructured[app_id])
                 if reopened:
@@ -332,6 +331,9 @@
                     opening = ("source PDF explanation starts after lost words; the opening is written from the "
                                "question, its answer and the rest of the explanation" if reopened["to"] else
                                "source PDF explanation starts after lost words; what remains reads complete")
+                # The flat copy must describe the blocks the learner sees, not the
+                # pre-restructure prose: take it after the overlay and the opening.
+                explanation = micro.plain_text(blocks, tables)
                 if not stem or not all(texts):
                     self.fail(f"{q['id']}: blank stem or option")
                 if topic["startPage"] is None and q["pages"]["question_pages"]:
```

`micro.plain_text` (`tools/build_prepladder_microbiology_bank.py:388`) must also carry the table cells, or the table-only questions keep an empty flat copy:

```diff
--- a/tools/build_prepladder_microbiology_bank.py
+++ b/tools/build_prepladder_microbiology_bank.py
@@ -385,13 +385,20 @@
     return blocks, tables
 
 
-def plain_text(blocks: list[dict]) -> str:
+def plain_text(blocks: list[dict], tables: list[dict] | None = None) -> str:
+    by_id = {t.get("table_id"): t for t in (tables or [])}
     out = []
     for block in blocks:
         if block["type"] in ("paragraph", "heading"):
             out.append(block["text"])
         elif block["type"] == "bullets":
             out.append("\n".join("• " + item["text"] for item in block["items"]))
+        elif block["type"] == "table":
+            # A table-only explanation still has to read as text in the flat copy.
+            table = by_id.get(block.get("table_id"))
+            if table:
+                out.append(" ".join(str(c) for c in table.get("columns") or []))
+                out.extend(" ".join(str(c) for c in row) for row in table.get("rows") or [])
     return "\n\n".join(out)
 
 
@@ -502,7 +509,7 @@
                 "options": [{"letter": letters[i], "text": texts[i]} for i in range(len(texts))],
                 "correctOption": key,
                 "correctAnswerText": texts[key - 1],
-                "explanation": plain_text(blocks),
+                "explanation": plain_text(blocks, tables),
                 "structuredExplanation": {"layout": "ordered-blocks", "blocks": blocks, "tables": tables,
                                           "figures": sorted(i["image_id"] for i in stem_images + explain_images)},
                 "provenance": {"sourceFile": V2_PDFS if explain_from is new else SOURCE_PDF, "sourceLabel": edition_label,
```

The table flattening needs the table body, which `plain_text` does not currently receive. The smallest complete form is to pass the question's `tables` list into `plain_text` and append each table's columns and rows as text lines:

```python
def plain_text(blocks: list[dict], tables: list[dict] | None = None) -> str:
    by_id = {t.get("table_id"): t for t in (tables or [])}
    out = []
    for block in blocks:
        if block["type"] in ("paragraph", "heading"):
            out.append(block["text"])
        elif block["type"] == "bullets":
            out.append("\n".join("• " + item["text"] for item in block["items"]))
        elif block["type"] == "table":
            table = by_id.get(block.get("table_id"))
            if table:
                out.append(" ".join(str(c) for c in table.get("columns") or []))
                out.extend(" ".join(str(c) for c in row) for row in table.get("rows") or [])
    return "\n\n".join(out)
```

Both call sites then pass the tables they already have:

```diff
--- a/tools/prepladder_text_bank.py
+++ b/tools/prepladder_text_bank.py
@@ -324,7 +324,6 @@
                 reopened = openings.pop(app_id, None)
                 if reopened and not opening and not reopened.get("lead"):
                     self.fail(f"{app_id}: hand-written opening for an explanation that opens whole")
-                explanation = micro.plain_text(self.reopen(app_id, blocks, reopened) if reopened else blocks)
                 if app_id in restructured:
                     blocks = self.apply_overlay(app_id, blocks, tables, restructured[app_id])
                 if reopened:
@@ -332,6 +331,9 @@
                     opening = ("source PDF explanation starts after lost words; the opening is written from the "
                                "question, its answer and the rest of the explanation" if reopened["to"] else
                                "source PDF explanation starts after lost words; what remains reads complete")
+                # The flat copy must describe the blocks the learner sees, not the
+                # pre-restructure prose: take it after the overlay and the opening.
+                explanation = micro.plain_text(blocks, tables)
                 if not stem or not all(texts):
                     self.fail(f"{q['id']}: blank stem or option")
                 if topic["startPage"] is None and q["pages"]["question_pages"]:
```

## Verification

- Reproduce, then verify the fix:
  1. Before: run the comparison in Evidence — the flat `explanation` differs from `plain(blocks)` for 1,416 Pathology and 1,309 Pharmacology questions.
  2. Rebuild the banks: `python3 tools/build_prepladder_pathology_bank.py` and `python3 tools/build_prepladder_pharmacology_bank.py` (and `…_microbiology_bank.py`).
  3. After: the comparison reports 0 differences and the 81 table-only questions have a non-empty flat copy.
  4. `python3 tools/build_prepladder_pathology_bank.py --check` and the pharmacology/microbiology equivalents must still pass (the shards and manifest must be regenerated and committed together with the builder change).
- Existing tests to extend: `tools/test_prepladder_pathology_bank.py` and `tools/test_prepladder_pharmacology_bank.py` already assert on `structuredExplanation`; add an assertion that `q["explanation"]` equals the flat rendering of `q["structuredExplanation"]["blocks"]`, so the two copies cannot drift again.
- Regressions to re-check: the "Key takeaway" card in Practice and Review Solutions (it is now computed from the structured text), the PrepLadder text-bank explanations themselves, and `tools/test_question_content_hygiene_v1.py`, which asserts on `nkSourceTakeaway` output.

## Alternatives considered

Keeping the flat copy as the pre-restructure prose and making the takeaway read the structured blocks instead would also work, but it moves the fix into the renderer and leaves the data contract broken — any other consumer of `q.explanation` (search, notes, export) would still read the wrong document. Deriving the flat copy from the final blocks keeps one source of truth in the data.

## Main-agent review

- **Verdict:** needs-work
- **Checked evidence:** yes
- **Checked patch:** no
- **Notes:** The finding is real and measured: the shipped explanation string is captured at prepladder_text_bank.py:327, before apply_overlay (line 329) and before the opening repair (line 331), while structuredExplanation is built from the final blocks at lines 367-369. Reproduced: 1,416 of 1,459 Pathology and 1,309 of 1,321 Pharmacology questions have a flat copy that is not the flat rendering of the shipped blocks, and 81 questions have an empty flat copy where the learner sees only a table. The patch needs rework before it can be applied. First, the diff shows two mutually exclusive edits to the same line: the first hunk replaces line 327 with a new line and the second hunk then replaces the same line again with a version that passes tables; the hunks must be merged so the diff applies cleanly. Second, the plain_text table-flattening patch references a TABLES_BY_ID global that does not exist: the helper has no access to the tables list, so the shown code cannot run as written. Third, the implementer must decide and state the table-flattening format, because the takeaway picker scores candidate lines against the answer words and a flattened table changes which line wins. Rework to a single coherent diff, then re-review. The diagnosis and the impact counts are accepted.
