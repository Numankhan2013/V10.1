# BUG-04-002 — Notes search only matches the full typed phrase

- **Area:** 04 navigation & UI
- **Severity:** low
- **Confidence:** high
- **Status:** fix applied — commit 012ebc72
- **Files:** `app/src/main/modules/question_notes.js:92-102`
- **Introduced by:** unknown

## What happens

On the "My notes" screen, typing two or more words hides every note even when each word appears in the note/question text, because the filter tests the whole phrase as one substring.

## Evidence

`nkFilterNotes`:

```
const term=nkNotesQuery.trim().toLowerCase();
let shown=0;
document.querySelectorAll('.nk-notes-item').forEach(item=>{
  item.hidden=Boolean(term)&&!item.dataset.noteSearch.includes(term);
  if(!item.hidden)shown++;
});
```

`data-note-search` is built from `${subject} ${bank} ${topic} ${q?.question} ${text}` (line 84), so individual words are present but the phrase test fails for multi-word queries.

## Learner impact

Multi-word searches on saved notes return no results until the learner reduces the query to one word. No data loss.

## Root cause

The same single-substring filter pattern as the Revision browse screen; question search already tokenises.

## Proposed fix

```diff
--- a/app/src/main/modules/question_notes.js
+++ b/app/src/main/modules/question_notes.js
@@ -91,9 +91,10 @@
 
   function nkFilterNotes(value){
     nkNotesQuery=String(value||'');
-    const term=nkNotesQuery.trim().toLowerCase();
+    const term=nkNotesQuery.trim().toLowerCase(),terms=term.split(/\s+/).filter(Boolean);
     let shown=0;
     document.querySelectorAll('.nk-notes-item').forEach(item=>{
-      item.hidden=Boolean(term)&&!item.dataset.noteSearch.includes(term);
+      const haystack=item.dataset.noteSearch||'';
+      item.hidden=Boolean(terms.length)&&!terms.every(word=>haystack.includes(word));
       if(!item.hidden)shown++;
     });
     const empty=document.querySelector('.nk-notes-no-match');```

## Verification

- Manual: open More → My notes, type two words that each appear in a note; matching notes remain.
- Existing test: `python3 tools/test_question_notes_v1.py` should gain a multi-word assertion.

## Alternatives considered

Keeping the phrase test and adding a separate "advanced" mode would leave the default broken; tokenising matches the question-search behaviour.

## Main-agent review

- **Verdict:** approved
- **Checked evidence:** yes
- **Checked patch:** yes
- **Notes:** Verified the notes filter applies the same whole-phrase containment as the revision browse filter. The diff tokenises. Approved as low severity: a search-filter convenience issue with a one-word workaround.


The finding is correct and the patch is right: the notes filter applied the same whole-phrase containment as the revision browse filter.

`tools/test_search_filters_v1.py` also drives `nkFilterNotes` from the shipped module. On the pre-fix module the multi-word assertion fails.
