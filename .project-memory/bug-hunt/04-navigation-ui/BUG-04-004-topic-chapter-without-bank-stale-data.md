# BUG-04-004 — Opening a topic chapter without a bank uses stale chapter data

- **Area:** 04 navigation & UI
- **Severity:** medium
- **Confidence:** medium
- **Status:** open — proposed fix, not applied
- **Files:** `app/src/main/assets/index.html:653-657`
- **Introduced by:** unknown

## What happens

`nkOpenSubjectChapter(subject,bank,topicId)` falls back to `openSubjectTopics(subject)` when `bank` is missing, but then unconditionally schedules `openChapter(topicId)` in a timeout. `openChapter` navigates using the previous subject/bank's `CHAPTERS`/`CHAPTER_BY_ID`, so it can open the wrong chapter or fall back to the Topics page.

## Evidence

```
function nkOpenSubjectChapter(subject,bank,topicId){
  if(typeof openBank==='function'&&bank)openBank(subject,bank);else if(typeof openSubjectTopics==='function')openSubjectTopics(subject);
  setTimeout(()=>{if(typeof openChapter==='function')openChapter(topicId);},0);
}
```

`openSubjectTopics` only sets `activeSubject` and navigates to the bank chooser; it does not call `applySubject`, so `CHAPTERS` still belongs to the previous bank.

## Learner impact

A caller that omits the bank (or a future caller) can land on a chapter from another bank or a "Topics" fallback instead of the requested topic. Current callers usually pass a bank, so the bug is latent but reachable.

## Root cause

The timeout assumes the preceding branch loaded the requested bank's chapters, which is only true for the `openBank` branch.

## Proposed fix

Resolve a bank before opening the chapter; if none exists, open the bank chooser and do not attempt the chapter navigation.

```diff
--- a/app/src/main/assets/index.html
+++ b/app/src/main/assets/index.html
@@ -651,8 +651,9 @@
     navigate('banks',subject);
   }
   function nkOpenSubjectChapter(subject,bank,topicId){
+    if(!bank&&typeof nkPreferredRecord==='function')bank=nkPreferredRecord(subject)?.bank;
     if(typeof openBank==='function'&&bank)openBank(subject,bank);else if(typeof openSubjectTopics==='function')openSubjectTopics(subject);
-    setTimeout(()=>{if(typeof openChapter==='function')openChapter(topicId);},0);
+    if(bank)setTimeout(()=>{if(typeof openChapter==='function')openChapter(topicId);},0);
   }
   function nkSubjectCardV3(name){
     const s=nkSubjectStatsV3(name),m=nkAppSubjectMeta(name);
```

## Verification

- Manual: call `nkOpenSubjectChapter('Anatomy','','1')` with no bank; it should open the Anatomy bank chooser instead of a stale chapter.
- Existing tests: `python3 tools/test_insights_focus_v1.py`, `python3 tools/test_qbank_coverage_v1.py`.

## Alternatives considered

Always calling `openBank(subject, bank||'PrepLadder')` would apply a possibly nonexistent bank; resolving through `nkPreferredRecord` matches the subject's actual banks.

## Main-agent review

- **Verdict:** approved
- **Checked evidence:** yes
- **Checked patch:** yes
- **Notes:** Verified the chapter path falls back to the currently cached chapter data when no bank is supplied, so a stale chapter can be shown. Confidence medium is appropriate: the trigger depends on the entry point into a chapter. The diff requires an explicit bank. Approved.
/root/bug-hunt/base/.project-memory/bug-hunt/04-navigation-ui/BUG-04-005-coverage-open-no-bank-stale.md