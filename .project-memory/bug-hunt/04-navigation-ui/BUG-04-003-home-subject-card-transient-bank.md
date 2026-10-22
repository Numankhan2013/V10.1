# BUG-04-003 — Home subject cards load a bank before the learner chooses one

- **Area:** 04 navigation & UI
- **Severity:** medium
- **Confidence:** medium
- **Status:** fix applied — commit 012ebc72
- **Files:** `app/src/main/assets/index.html:644-652`
- **Introduced by:** unknown

## What happens

Tapping a subject card on Home calls `nkOpenSubjectLibrary(subject)`, which immediately calls `applySubject(subject)` using whatever bank happens to be active. That switches the app's active bank/question data to that subject's first bank and schedules a cloud sync before the learner has opened a bank chooser, so the active subject/bank state can be attributed to a bank the learner never selected if they back out.

## Evidence

```
function nkOpenSubjectLibrary(subject){
  const records=typeof nkBankRecords==='function'?nkBankRecords(subject):[];
  const fallback=(SUBJECTS||[]).find(r=>r.subject===subject)||null;
  if(!records.length&&!fallback){showToast('This subject is not available.','bad');return;}
  if(typeof applySubject==='function') applySubject(subject);
  else activeSubject=subject;
  localStorage.setItem('qbank_active_subject_v1',subject);
  navigate('banks',subject);
}
```

`applySubject(name,bank=activeBank)` persists both `qbank_active_subject_v1` and `qbank_active_bank_v1` and calls `nkScheduleCloudSync()` (lines 206-220). The bank chooser page itself (`bankPage`) does not depend on `DATA`, so the eager apply is unnecessary.

## Learner impact

The active bank can be changed/synced as a side effect of browsing subjects; recovery is choosing a bank, but the transient state is still uploaded. No data loss.

## Root cause

The subject card conflates "open the bank chooser" with "apply a subject/bank", unlike `openSubjectTopics`, which only sets `activeSubject`.

## Proposed fix

```diff
--- a/app/src/main/assets/index.html
+++ b/app/src/main/assets/index.html
@@ -645,7 +645,6 @@
     const records=typeof nkBankRecords==='function'?nkBankRecords(subject):[];
     const fallback=(SUBJECTS||[]).find(r=>r.subject===subject)||null;
     if(!records.length&&!fallback){showToast('This subject is not available.','bad');return;}
-    if(typeof applySubject==='function') applySubject(subject);
-    else activeSubject=subject;
+    activeSubject=subject;
     localStorage.setItem('qbank_active_subject_v1',subject);
     navigate('banks',subject);
   }```

## Verification

- Manual: tap a subject card, then back out without choosing a bank; active bank remains the previously chosen bank and no sync payload changes.
- Existing tests: `python3 tools/test_custom_study_modules_v1.py` and `python3 tools/test_app_source_parity.py`.

## Alternatives considered

Passing a preferred bank to `applySubject` would still load data the chooser does not need and would still sync; mirroring `openSubjectTopics` is the smaller, safer change.

## Main-agent review

- **Verdict:** approved
- **Checked evidence:** yes
- **Checked patch:** yes
- **Notes:** Verified the Home subject-card path opens the bank before the learner has chosen one, so the bank selector shows a transient default. Confidence medium is right: it depends on which subject card is tapped and on the bank registry order. The fix keeps the card action to subject selection and defers the bank choice. Approved.


The finding is correct and the patch is right. `applySubject` persists `qbank_active_bank_v1` and schedules a cloud sync, and the bank chooser page does not need `DATA` at all. The patch mirrors `openSubjectTopics` (index.html:313), which sets only the active subject.

`tools/test_subject_navigation_v1.py` is new. It takes `nkOpenSubjectLibrary` out of the assembled page and asserts that tapping a subject card applies no bank, remembers the subject, does not remember a bank, and schedules no cloud sync. On the pre-fix page it fails with "tapping a subject card must not load a bank".
