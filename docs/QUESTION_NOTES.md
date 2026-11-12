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

## Voice clips (2026-11-12, preview only)

**+ Add block → Voice** (after Text, Image and PDF pages) opens an inline recorder
under the blocks: **Record**, **Import audio**, and ✕. While recording it shows a
pulsing dot, `0:12 / 3:00`, **Discard** and **Stop and save**; a clip stops and
saves itself at 3 minutes. Closing the note, Escape or leaving the question while
recording keeps the clip (as closing keeps typed text). **Import audio**
(`accept="audio/*"`; M4A, MP3, WAV, OGG, WebM…) adds an existing file, also by drag
and drop, up to 3.5 MB.

Recording uses `getUserMedia({audio:{channelCount:1,…}})` and `MediaRecorder` at
`audioBitsPerSecond: 24000`, preferring `audio/webm;codecs=opus`, then
`audio/mp4;codecs=mp4a.40.2` / `audio/mp4` (Safari/iOS), then whatever
`isTypeSupported` allows (`NK_NOTE_VOICE_TYPES`). Recorded WebM often reports an
endless duration, so the block stores the measured `durationMs`. A denied
permission, a missing or busy microphone, an insecure origin or a browser without
`MediaRecorder` shows a plain inline message in the recorder and leaves **Import
audio** available; nothing is saved.

A clip renders as a compact player (play/pause, scrub, `0:12 / 0:42`) under a
mic badge and its caption (default "Voice clip"; an import uses the file name).
The ⋮ menu (or long-press) offers **Rename caption**, Move up, Move down and
Delete. Long-press does not start on the player controls. Playing one clip pauses
any other. More → My notes shows "N voice clips" on a note, and the note bar's
counts include voice clips.

Limits: up to 5 voice clips per note (`NK_NOTE_AUDIO_LIMIT`), counted apart from
the 10 images/pages and 10 text parts, which are unchanged.

Model and storage. `state.questionNotes[id].blocks` gains
`{type:'audio', assetId, durationMs, mime, caption, bytes}` (`mime` is the
container type only, e.g. `audio/webm`; `bytes` lets a removal tombstone every
chunk). Audio bytes never enter `state` or localStorage: IndexedDB
`qbank_note_media_v1` keeps a `meta` record (`kind:'audio'`, `durationMs`) and the
exact recorded bytes in `full`; there is no preview or thumb. A note with only a
voice clip is a live note (its `text` summary is empty).

Storage math. Opus speech at 24 kbps is about 3 KB/s ≈ 180 KB a minute; base64
adds a third (≈ 240 KB a minute in Firestore). A full 3-minute clip is ≈ 540 KB
≈ 720,000 base64 characters, one ≤ 800,000-character chunk. Safari/iOS may record
AAC above the requested bitrate (≈ 1–3 MB for 3 minutes); those clips simply use
the existing multi-chunk path (`noteAssets/{assetId}~{n}`). Firestore's free tier
(1 GiB stored) holds roughly 4,000 minutes of 24 kbps voice, shared with note
images.

Sync. Clip bytes reuse the image path unchanged: uploaded once after a
successful sync, downloaded lazily once per device when a note references the clip
(chunk payloads carry `kind:'audio'`, so the download stores the bytes without
decoding), tombstoned (payload cleared) when the clip is removed, cleared by
account reset. The firestore rules already allow this (owner-only
`users/{uid}/{document=**}`, payload ≤ 900,000 characters); **no rule change**.

Clip order travels in a new envelope kind, `noteVoice`
(`users/{uid}/noteVoice/{device}--{questionId}`, payload
`{clips:[{…block, at}], deleted}`), never inside `noteBlocks`. Reason: older app
versions keep only `text` and `image` blocks (`nkNoteSanitizeBlocks` silently
drops any other type, so nothing breaks or renders wrongly), but every capture
re-uploads their shortened `blocks` list with a newer timestamp. Had clips been in
`noteBlocks`, a single older client still signed in (a stale PWA tab or cached
service worker) would have erased them on every device. Now `noteBlocks` carries
exactly what older versions keep, so they never disagree with it, and newer
versions put their clips back in place when a `noteBlocks` without clips arrives
(`nkNoteKeepVoice`). An older version that edits only the text keeps the clips
too (`nkNoteBlocks` keeps images and clips when `notes` is newer than the parts).
Remaining edge: a note deleted entirely on an older version stays deleted; its
clips' bytes are not tombstoned and stay in storage.

Microphone permission. The PWA's `Permissions-Policy` header
(`tools/web_security_policy.py`) was `microphone=()`, which blocks recording
outright; it is now `microphone=(self)`. The Android shell (MainActivity) has no
`RECORD_AUDIO` permission and no `WebChromeClient.onPermissionRequest`, so the
WebView denies the microphone: recording there shows the "Microphone access is
blocked" message and **Import audio** still works through the existing file
chooser. Enabling recording in the shell needs `RECORD_AUDIO` in the manifest, a
runtime permission request, and `onPermissionRequest` granting
`RESOURCE_AUDIO_CAPTURE` for the app origin only; deliberately not done here
(the owner uses the Chrome PWA).

Verification hooks: `tools/test_question_note_voice_v1.py` (block model,
limits, `noteVoice` separation, older-version round trip without echo) and
`tools/verify_question_note_voice_browser.py` (Chromium fake microphone: record,
play, rename, import, reorder, reload, notes list, five-clip limit, delete,
denied/unsupported microphone, and two-device sync with an older-version edit
against the in-memory Firestore).

Earlier verification hooks: `tools/test_question_notes_v1.py`,
`tools/test_cross_device_sync_v1.py`, and the generated PWA browser journey in
`tools/verify_question_notes_browser.py`. The initial note slice passed
Engineering `36103198537` and full browser/PWA/APK/Android emulator
`36103201213` at `21e28e2`. The read-only card and index passed
Engineering `36113707551` and full browser/PWA/APK/Android emulator
`36113695753` at `34c5bcc`. Preview:
`https://4cc816c7.nk-qbank.pages.dev`. The user checked and accepted this
preview; physical APK review remains separate.
