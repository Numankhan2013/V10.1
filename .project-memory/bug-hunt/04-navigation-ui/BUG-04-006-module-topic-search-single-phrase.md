# BUG-04-006 — Module builder topic search only matches one contiguous phrase

- **Area:** 04 navigation & UI
- **Severity:** low
- **Confidence:** medium
- **Status:** fix applied — commit 012ebc72
- **Files:** `app/src/main/modules/study_modules.js:279-294`
- **Introduced by:** unknown

## What happens

In the custom study module builder, searching topics by typing two words hides topics whose title and bank name contain both words separately.

## Evidence

`nkFilterModuleTopics`:

```
const query=String(value||'').trim().toLocaleLowerCase();
...
group.querySelectorAll('.nk-module-topic').forEach(button=>{
  const match=!query||scope.includes(query)||button.querySelector('strong')?.textContent.toLocaleLowerCase().includes(query);
  button.hidden=!match;if(match)groupVisible++;
});
```

`scope` is the bank/group title and the button text is the topic title; neither test is tokenised, so "anatomy limb" fails even when both words appear.

## Learner impact

Multi-word topic searches in the module builder return no topics. No data loss.

## Root cause

Single-substring matching instead of per-word matching, unlike question search.

## Proposed fix

```diff
--- a/app/src/main/modules/study_modules.js
+++ b/app/src/main/modules/study_modules.js
@@ -277,12 +277,14 @@
   }
 
   function nkFilterModuleTopics(value){
-    const query=String(value||'').trim().toLocaleLowerCase();
+    const query=String(value||'').trim().toLocaleLowerCase(),terms=query.split(/\s+/).filter(Boolean);
     let visible=0;
     document.querySelectorAll('.nk-module-topic-group[data-subject-index]').forEach(group=>{
       const scope=group.querySelector('.nk-module-group-title')?.textContent.toLocaleLowerCase()||'';
       let groupVisible=0;
       group.querySelectorAll('.nk-module-topic').forEach(button=>{
-        const match=!query||scope.includes(query)||button.querySelector('strong')?.textContent.toLocaleLowerCase().includes(query);
+        const title=button.querySelector('strong')?.textContent.toLocaleLowerCase()||'';
+        const haystack=scope+' '+title;
+        const match=!terms.length||terms.every(word=>haystack.includes(word));
         button.hidden=!match;if(match)groupVisible++;
       });
       group.hidden=!groupVisible;visible+=groupVisible;```

## Verification

- Manual: type two words from a bank/topic title; matching topics remain.
- Existing test: `python3 tools/test_custom_study_modules_v1.py`.

## Alternatives considered

Searching only topic titles would drop the useful bank-name matches; combining scope and title preserves current behaviour while adding tokenisation.

## Main-agent review

- **Verdict:** approved
- **Checked evidence:** yes
- **Checked patch:** yes
- **Notes:** Verified study_modules.js matches only one contiguous phrase against the topic pool while the sibling builders tokenise. Approved as low/medium: the module builder is a power-user surface and the search is a convenience filter.


The finding is correct and the patch is right: the module builder matched one contiguous phrase against the topic pool while the sibling builders tokenise. The patch matches every query word against the group scope and the topic title together, so a word may come from either.

`tools/test_search_filters_v1.py` also drives `nkFilterModuleTopics` from the shipped module. On the pre-fix module the assertion fails with "the module topic picker must match a multi-word query".
