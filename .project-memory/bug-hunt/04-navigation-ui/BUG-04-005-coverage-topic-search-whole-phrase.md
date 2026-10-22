# BUG-04-005 — Coverage topic search only matches the full typed phrase

- **Area:** 04 navigation & UI
- **Severity:** low
- **Confidence:** high
- **Status:** fix applied — commit 012ebc72
- **Files:** `app/src/main/modules/qbank_coverage.js:53-58`
- **Introduced by:** unknown

## What happens

In the "Your study map" tracker, the topic search box hides every topic unless the entire typed string occurs contiguously in the topic title.

## Evidence

```
const query=nkCoverageSearch.trim().toLocaleLowerCase();
const rows=bank.topics.filter(topic=>{
  const status=topic.attempted===topic.total?'complete':topic.attempted?'progress':'new';
  return (nkCoverageStatus==='all'||nkCoverageStatus===status)
    &&(!query||topic.title.toLocaleLowerCase().includes(query));
});
```

Question search and (after BUG-04-001) Revision browse tokenise their queries, so this screen is inconsistent.

## Learner impact

Multi-word topic searches return no results. No data loss.

## Root cause

Single-substring containment instead of per-word matching.

## Proposed fix

```diff
--- a/app/src/main/modules/qbank_coverage.js
+++ b/app/src/main/modules/qbank_coverage.js
@@ -50,10 +50,11 @@
   function nkCoverageListMarkup(data){
     const bank=nkCoverageSelected(data);
     if(!bank)return '<p class="nk-coverage-empty">No question banks are available yet.</p>';
-    const query=nkCoverageSearch.trim().toLocaleLowerCase();
+    const query=nkCoverageSearch.trim().toLocaleLowerCase(),terms=query.split(/\s+/).filter(Boolean);
     const rows=bank.topics.filter(topic=>{
       const status=topic.attempted===topic.total?'complete':topic.attempted?'progress':'new';
+      const title=topic.title.toLocaleLowerCase();
       return (nkCoverageStatus==='all'||nkCoverageStatus===status)
-        &&(!query||topic.title.toLocaleLowerCase().includes(query));
+        &&(!terms.length||terms.every(word=>title.includes(word)));
     });
     const visible=nkCoverageExpanded?rows:rows.slice(0,8);
     const list=visible.map(topic=>{```

## Verification

- Manual: type two words from a topic title; the topic remains visible.
- Existing test: `python3 tools/test_qbank_coverage_v1.py`.

## Alternatives considered

Filtering on the full topic metadata would require storing more search text; title-only token matching matches the current contract.

## Main-agent review

- **Verdict:** approved
- **Checked evidence:** yes
- **Checked patch:** yes
- **Notes:** Verified qbank_coverage.js applies the same whole-phrase containment as the other two browse filters, so the coverage topic search is the third instance of the same inconsistency. The diff tokenises. Approved as low: same class as BUG-04-001 and BUG-04-002.


The finding is correct and the patch is right: the coverage topic search was the third instance of the same whole-phrase containment.

`tools/test_search_filters_v1.py` also drives `nkCoverageListMarkup` from the shipped module. On the pre-fix module the assertion fails with "the coverage search must match words that are not adjacent".
