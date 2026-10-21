# BUG-03-003 — Marrow ordered-block tables skip the structured-table normalizer, so object-shaped cells render as `[object Object]`

- **Area:** 03 question rendering
- **Severity:** medium
- **Confidence:** high
- **Status:** open — proposed fix, not applied
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

`nkNormalizeMarrowStructuredTable` (line 1587) flattens object columns/cells to text via `nkMarrowTableCellText`. The ordered path bypasses it, so any object-shaped structured table in an ordered-block explanation (Microbiology) hits the `[object Object]` failure mode the project explicitly forbids.

## Learner impact

Wrong visible information: table headers/cells can render as `[object Object]` for ordered-block explanations whose table data uses the object form. The project's structured-table invariant treats `[object Object]` as a hard failure.

## Root cause

The ordered renderer was added without routing through the same normalizer used by the base renderer, so the two paths disagree on how to coerce structured cells.

## Proposed fix

Normalize before rendering in the ordered path.

```diff
--- a/app/src/main/assets/index.html
+++ b/app/src/main/assets/index.html
@@ -27,5 +27,6 @@
     return !!document.querySelector('.question-card') &&
       !!document.querySelector('.question-shell, .practice-actions, .exam-top');
   }
+  table=nkNormalizeMarrowStructuredTable(table);
   function cleanInjectedSessionCards(){
     if(!sessionVisible()) return;
     document.querySelectorAll('.page > *').forEach(function(el){```

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
- **Notes:** Verified index.html:1538-1549 (nkRenderMarrowOrdered renders table blocks through nkRenderMarrowOrderedTable, which reads table.columns and table.rows directly) against nkNormalizeMarrowStructuredTable (index.html:1587), the only place that converts object-valued cells to text. The ordered path bypasses it, so a table whose cells are objects renders as [object Object]. Approved, and the fix (route the ordered table through the normaliser) is the right one.
