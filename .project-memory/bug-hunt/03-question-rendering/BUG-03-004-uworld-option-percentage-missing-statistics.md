# BUG-03-004 — `nkUworldOptionPercentage` throws when a reviewed UWorld document has no statistics

- **Area:** 03 question rendering
- **Severity:** medium
- **Confidence:** medium
- **Status:** fix applied — commit 8b961133
- **Files:** `app/src/main/modules/uworld_biochemistry.js:84`, `app/src/main/modules/uworld_biochemistry.js:88`
- **Introduced by:** unknown

## What happens

For a reviewed UWorld question, `nkUworldOptionPercentage` reads `q.uworldDocument.statistics.selection_percent` directly. If `statistics` (or `selection_percent`) is missing/null on a reviewed document, this dereferences `undefined` and throws `TypeError: Cannot read properties of undefined (reading 'selection_percent')`, breaking the whole question render (the option list is built by mapping over options, so one throw aborts rendering).

## Evidence

```js
function nkUworldOptionPercentage(q,o,revealed=true){
  const values=q.uworldDocument?q.uworldDocument.statistics.selection_percent:Object.fromEntries((q.uworldSource?.options||[]).map(item=>[item.label,item.selection_percent]));
  if(!Object.values(values).some(value=>value!=null))return '';
  ...
}
```

Contrast with `nkUworldStatistics` (line 97), which safely chains:

```js
const value=(q.uworldDocument?.statistics||q.uworldSource?.statistics)?.answered_correctly_percent;
```

The sibling renderer already defends against missing statistics; this one does not. `nkSourcePollPercent` (index.html) is similarly guarded via `nkSourceStats(q)?.optionPollPercent`.

## Learner impact

A single reviewed UWorld record lacking peer-statistics data makes the question unrenderable (blank/broken screen) instead of simply omitting the percentage column. Recoverable only if the record is repaired.

## Root cause

Inconsistent null-safety: the reviewed-document branch assumes `statistics` and `selection_percent` always exist, while the rest of the code treats them as optional.

## Proposed fix

Use optional chaining and fall back to the source branch (or empty) when statistics are absent.

```diff
--- a/app/src/main/modules/uworld_biochemistry.js
+++ b/app/src/main/modules/uworld_biochemistry.js
@@ -85,7 +85,7 @@
     if(discussion)out.push('</section>');return out.join('');
   }
   function nkUworldOptionPercentage(q,o,revealed=true){
-    const values=q.uworldDocument?q.uworldDocument.statistics.selection_percent:Object.fromEntries((q.uworldSource?.options||[]).map(item=>[item.label,item.selection_percent]));
-    if(!Object.values(values).some(value=>value!=null))return '';
+    const values=q.uworldDocument?(q.uworldDocument.statistics?.selection_percent||{}):Object.fromEntries((q.uworldSource?.options||[]).map(item=>[item.label,item.selection_percent]));
+    if(!values||!Object.values(values).some(value=>value!=null))return '';
     // Reserve the same quiet column before/after answering; text never rewraps
     // just because source percentages become visible.
     if(!revealed)return '<span class="nk-uworld-percent-space" aria-hidden="true"></span>';```

## Verification

- Unit-test `nkUworldOptionPercentage({bank:'UWorld',uworldDocument:{},options:[{letter:'A',text:'x'}]}, {letter:'A'})` returns `''`/space without throwing.
- Existing `tools/test_uworld_runtime_v1.py` should add a reviewed document with `statistics: null` and assert no throw.

## Alternatives considered

Returning `''` entirely when statistics are missing would collapse the reserved column width and reflow text; preserving the space (as the existing `!revealed` path does) matches the documented intent of reserving the column.

## Main-agent review

- **Verdict:** approved
- **Checked evidence:** yes
- **Checked patch:** yes
- **Notes:** The finding is correct and the patch is right.

Verified `nkUworldOptionPercentage` (app/src/main/modules/uworld_biochemistry.js:86) against its sibling `nkUworldStatistics` (line 96), which already chains through `?.`. The reviewed-document branch dereferenced `q.uworldDocument.statistics.selection_percent` with no guard, and `statistics` is optional on a reviewed document: `nkUworldStatistics` reads the same object defensively, and `nkUworldOptionPercentage` is called while mapping over the options, so one throw aborts the whole question render.

The patch is minimal and keeps the existing behaviour: `statistics?.selection_percent||{}` plus a `!values` guard. The percentage is still shown when the source carries one.

`tools/test_uworld_option_percentage_v1.py` is new and drives the shipped function with three documents: one with no `statistics` at all, one whose `statistics` carry no `selection_percent`, and one that carries percentages and must still show them. The first two throw `TypeError: Cannot read properties of undefined (reading 'selection_percent')` on the pre-fix module.
