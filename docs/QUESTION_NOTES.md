# Question-linked personal notes

The first study-intelligence increment adds one short learner-written note to a
question. After answering in Practice, or while viewing Review Solutions, open
**My note**, write up to 2,000 characters, and save. A saved note reappears when
that question is opened again, including through a different module route.
Clearing the text and saving removes it.

Notes live in `state.questionNotes`, keyed by stable question ID. Durable local
state preserves them through app restart and its recovery snapshots. Signed-in
accounts synchronize each note independently using the existing `notes` Firestore
collection; an empty deleted record prevents an older copy from resurrecting a
removed note. A failed local save leaves the draft visible and rolls back the
in-memory edit.

This increment adds no Home action. The note editor appears only after an answer
or in Review, outside timed CBT. Later work can add a compact saved-note index
and a unified revision queue without duplicating Practice.

Verification: `tools/test_question_notes_v1.py`,
`tools/test_cross_device_sync_v1.py`, and the generated PWA browser journey in
`tools/verify_question_notes_browser.py`. Physical Android/iPad behavior still
needs review on the preview build.
