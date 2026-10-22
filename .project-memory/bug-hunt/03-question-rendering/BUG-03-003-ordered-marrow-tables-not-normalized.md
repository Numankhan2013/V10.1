# BUG-03-003 — Marrow ordered-block tables skip the structured-table normalizer, so object-shaped cells render as `[object Object]`

- **Area:** 03 question rendering
- **Severity:** low — the defect is real in code but does not manifest in the shipped banks (see Learner impact)
- **Confidence:** high
- **Status:** fix applied — commit pending (this commit)
- **Files:** `app/src/main/assets/index.html:1533`, `app/src/main/assets/index.html:1587`
- **Introduced by:** unknown

## What happens

Explanations rendered through the ordered-block path (`nkRenderMarrowOrdered`) emit tables with `nkRenderMarrowOrderedTable`, which stringifies each cell via `nkMarrowOrderedCell` → `String(value)`. It never runs `nkNormalizeMarrowStructuredTable`, unlike the non-ordered path which uses `nkRenderMarrowTableCompat`. If a table's columns or cells are object-shaped (e.g. `{key, label}` / `{value}`), the ordered path renders the literal text `[object Object]`.

## Evidence

Ordered path:

```js
function nkMarrowOrderedCell(value){return String(value??'').split('\n').map(part=>nkMarrowRich(part.trim())).filter(Boolean).join('<br>');}
function nkRenderMarrowOrderedTable(table){
  const cols=Array.isArray(table?.columns)?table.columns:[],rows=Array.isArray(table?.rows)?table.rows:[];
  if(!cols.length||!rows.length)return'';
  return `...${cols.map(c=>`<th>${nkMarrowOrderedCell(c)}</th>`)}...${cols.map((_,i)=>`<td>${nkMarrowOrderedCell((r||[])[i]||'')}</td>`)}...`;
}
```

Non-ordered path normalizes first:

```js
function nkRenderMarrowTableCompat(table){return nkRenderMarrowTable(nkNormalizeMarrowStructuredTable(table));}
```

`nkNormalizeMarrowStructuredTable` (line 1587) flattens object columns/cells to text via `nkMarrowTableCellText`. The ordered path bypasses it, so any object-shaped structured table in an ordered-block explanation hits the `[object Object]` failure mode the project explicitly forbids.

The defect reproduces directly against the shipped functions: an object-shaped table rendered through `nkRenderMarrowOrderedTable` produces `<th>[object Object]</th>` headers.

## Learner impact

**No shipped question shows this today.** Every structured table in the shipped banks was counted for object-shaped columns and cells:

```
microbiology: tables=235 with object columns=0 with object cells=0
pathology:    tables=343 with object columns=0 with object cells=0
pharmacology: tables=422 with object columns=0 with object cells=0
Anatomy Marrow:    tables=97  with object columns=18 with object cells=83
Biochemistry Marrow: tables=25 with object columns=0 with object cells=0
Physiology Marrow:   tables=37 with object columns=0 with object cells=0
Microbiology Marrow: tables=86 with object columns=0 with object cells=0
```

The 18 object-shaped tables are all in the Anatomy Marrow bank, and every one of them has `structuredExplanation.layout` unset, so it renders through `nkRenderMarrowExplanationBase` → `nkRenderMarrowTableCompat`, which already normalizes. The `ordered-blocks` layout — the only path that uses `nkRenderMarrowOrderedTable` — carries no object-shaped table at all:

```
Anatomy Marrow: object-shaped tables = 18; layouts: Counter({None: 18})
microbiology / pathology / pharmacology / Biochemistry Marrow /
Physiology Marrow / Microbiology Marrow: object-shaped tables = 0
```

So the learner-visible impact is latent: the two renderers disagree, and the day an ordered-block explanation gains an object-shaped table it will print `[object Object]` to the learner, which the project's structured-table invariant treats as a hard failure. The severity is recorded as low for that reason; the finding is kept because the inconsistency is real and the fix is one line.

## Root cause

The ordered renderer was added without routing through the same normalizer used by the base renderer, so the two paths disagree on how to coerce structured cells.

## Proposed fix

Normalize before rendering in the ordered path.

```diff
--- a/app/src/main/assets/index.html
+++ b/app/src/main/assets/index.html
@@ -1500,6 +1500,7 @@
   // through MARROW_VISUALS; source wording is rendered unchanged.
   function nkMarrowOrderedCell(value){return String(value??'').split('\n').map(part=>nkMarrowRich(part.trim())).filter(Boolean).join('<br>');}
   function nkRenderMarrowOrderedTable(table){
+    table=nkNormalizeMarrowStructuredTable(table);
     const cols=Array.isArray(table?.columns)?table.columns:[],rows=Array.isArray(table?.rows)?table.rows:[];if(!cols.length||!rows.length)return'';
     return `<div class="nk-marrow-table"><table>${table.title?`<caption>${nkMarrowRich(table.title)}</caption>`:''}<thead><tr>${cols.map(c=>`<th>${nkMarrowOrderedCell(c)}</th>`).join('')}</tr></thead><tbody>${rows.map(r=>`<tr>${cols.map((_,i)=>`<td>${nkMarrowOrderedCell((r||[])[i]||'')}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
   }
```

`nkNormalizeMarrowStructuredTable` is a function declaration and is hoisted, so calling it here is safe despite its later definition site.

## Verification

- Add a regression test rendering an ordered-block question whose `structuredExplanation` table uses object-shaped columns/cells and assert the output contains the flattened text and not `[object Object]`.
- Existing `tools/test_question_presentation_v1.py` and UWorld/Marrow browser verifiers should remain green.

## Alternatives considered

Changing `nkMarrowOrderedCell` to coerce objects like `nkMarrowTableCellText` would duplicate the normalization logic; routing through the existing normalizer keeps a single source of truth.

## Main-agent review

- **Verdict:** approved
- **Checked evidence:** yes
- **Checked patch:** yes
- **Notes:** The finding is correct, but the patch was wrong as first proposed and was reworked before being applied.

Verified index.html:1503-1506 (nkRenderMarrowOrderedTable reads table.columns and table.rows directly) against nkNormalizeMarrowStructuredTable (index.html:1587), the only place that converts object-valued cells to text via nkMarrowTableCellText. The ordered path bypasses it, so a table whose columns or cells are objects renders as [object Object], which the project's structured-table invariant treats as a hard failure.

The proposed patch inserted `table=nkNormalizeMarrowStructuredTable(table);` into the unrelated IIFE at index.html:27-31, inside the `qbank-question-ui-v2-script` block, where `table` is not defined and the call would throw at load. Applied as proposed, it would have broken the app on start-up. The patch now inserts the call as the first statement of nkRenderMarrowOrderedTable, which is where the object-shaped table actually arrives. `nkNormalizeMarrowStructuredTable` is a function declaration in the same scope, so the hoisting argument in the Alternative section still holds.

Approved. The corrected diff is in this file and applies cleanly.
