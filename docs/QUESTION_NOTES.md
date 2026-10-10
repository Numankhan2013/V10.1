# Question-linked personal notes

The study-intelligence increment adds a learner-written note to a question.
After answering in Practice, or while viewing Review Solutions, the **My
notes** bar opens the note page (see Images and PDF pages below). A saved note
reappears when that question is opened again, including through a different
module route.

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

## Images and PDF pages (2026-10-10)

A note is an ordered list of blocks: text, images and PDF pages, in any order.
Handwriting is written in GoodNotes (or any app) and brought in as an export,
screenshot, paste or drag; the app does not draw ink itself.

After answering (or in Review), the question shows a compact **My notes** bar
with the first line of text and a block count. Tapping it opens a full-screen
notes page (`.nk-note-page`) where blocks flow as a document: text blocks,
framed images with captions, and PDF pages under a PDF badge and title. Every
block has a ⋮ button, and long-press or right-click opens the same menu: Edit
(text) or View full screen (images), Move up, Move down and Delete. A floating
**+ Add block** button offers Text, Image and PDF pages; an empty note opens
with that menu expanded. Changes save immediately; text saves with Save, and
closing the page with unsaved non-empty text saves it. Image frames show a
shimmer skeleton until the picture has decoded, and imports show a skeleton
block while they are processed. A PDF opens a page picker with lazy
thumbnails; a one-page PDF is added directly. Tapping an image opens a
full-screen viewer with pinch, drag, double-tap and button zoom, plus
previous/next. More → My notes shows up to four thumbnails per note.

Limits: 10 images or pages per note (and per PDF import), 10 text parts of up
to 2,000 characters each. Images that already fit (JPG/PNG/WebP, ≤3,200 px long
edge, ≤3.5 MB) keep their exact original bytes. Larger images and PDF pages are
rendered at 3,200 px on the long edge (≈270 dpi for A4) so small handwriting
stays legible when zoomed, then JPEG-compressed until under 3.5 MB.

Storage and speed. Image bytes never enter `state` or localStorage. IndexedDB
`qbank_note_media_v1` keeps per asset a `meta` record plus `full`, `preview`
(1,400 px, shown inline) and `thumb` (360 px, lists) variants; the viewer alone
decodes the full image. `state.questionNotes[id]` gains `blocks` and
`blocksAt`; `text` stays a ≤2,000-character summary of the text parts, so
older app versions still read and search it.

Sync. `notes` envelopes are unchanged. A new `noteBlocks` envelope carries the
ordered parts (asset IDs and dimensions only). Image bytes go to
`users/{uid}/noteAssets/{assetId}~{n}` as base64 chunks of at most 800,000
characters (the Firestore rule allows 900,000). They are not part of the
five-minute envelope pull: each asset uploads once after a successful sync and
downloads once per device when a note references it, one asset at a time. An
image removed from a note is tombstoned (payload cleared) because rules forbid
deletes. If an older app version edits only the text, the newer `notes`
timestamp wins and the images are kept. Account reset also clears
`noteAssets`. Free-tier Firestore (1 GiB stored) holds roughly 800–2,500 note images, since base64 adds a third to each image.

Android needs a native file chooser for `<input type=file>`:
`tools/apply_android_file_picker_v1.py` installs it on the generated activity.

Verification hooks: `tools/verify_question_note_media_browser.py` (generated
PWA at phone and iPad widths: image and PDF import, ordering, viewer, reload,
notes list, removal, and two-device sync against an in-memory Firestore),
`tools/test_question_notes_v1.py`, `tools/test_cross_device_sync_v1.py` and
`tools/test_android_file_picker_v1.py`.

Earlier verification hooks: `tools/test_question_notes_v1.py`,
`tools/test_cross_device_sync_v1.py`, and the generated PWA browser journey in
`tools/verify_question_notes_browser.py`. The initial note slice passed
Engineering `36103198537` and full browser/PWA/APK/Android emulator
`36103201213` at `21e28e2`. The read-only card and index passed
Engineering `36113707551` and full browser/PWA/APK/Android emulator
`36113695753` at `34c5bcc`. Preview:
`https://4cc816c7.nk-qbank.pages.dev`. The user checked and accepted this
preview; physical APK review remains separate.
