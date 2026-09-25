# Question-linked personal notes

The study-intelligence increment adds one short learner-written note to a
question. After answering in Practice, or while viewing Review Solutions, tap
**Add note**, write up to 2,000 characters, and save. The note becomes a
read-only card with **Edit** and **Delete** at its top right. Edit opens the
textarea; Cancel leaves the saved text intact. A saved note reappears when
that question is opened again, including through a different module route.

**More → My notes** lists saved notes from every subject and bank, newest first.
Search matches the note, question, topic, subject, and bank. Each available
question has a Practice question action that opens the existing Practice
engine; an in-progress normal Practice session is checkpointed first. The
index stays read-only. Missing question IDs remain visible without a launch
action so their notes are not hidden or discarded.

Notes live in `state.questionNotes`, keyed by stable question ID. Durable local
state preserves them through app restart and its recovery snapshots. Signed-in
accounts synchronize each note independently using the existing `notes` Firestore
collection; an empty deleted record prevents an older copy from resurrecting a
removed note. A failed local save leaves the draft visible and rolls back the
in-memory edit.

This increment adds no Home action. The note card appears only after an answer
or in Review, outside timed CBT. The next study-intelligence step is a unified
revision queue without duplicating Practice.

Verification hooks: `tools/test_question_notes_v1.py`,
`tools/test_cross_device_sync_v1.py`, and the generated PWA browser journey in
`tools/verify_question_notes_browser.py`. The initial note slice passed
Engineering `36103198537` and full browser/PWA/APK/Android emulator
`36103201213` at `21e28e2`; the read-only card and index require a new
exact-head build and physical review.
