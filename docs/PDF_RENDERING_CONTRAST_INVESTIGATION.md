# PrepLadder source PDF contrast

Status: display adjustment build-verified on 2026-09-27; physical review pending.

The learner reported that PrepLadder explanation pages looked bleached on Android:
black text appeared grey and source colors dull. This was already noticeable in
older versions. The earlier source-zoom repair (`215d695`) is still present; it
improved sharpness but did not change page tone. The previous investigation in
this file had found no opacity or filter in the app and deferred a contrast
change until device evidence was available. The learner's report and same-crop
before/after captures supplied that evidence.

The PDF rendering path remains intact: PDF.js creates opaque, high-resolution
inline canvases and a fresh lossless fullscreen raster; packaged Android uses
its native PDF renderer. The final shared session style in
`tools/apply_session_experience_v2.py` applies `contrast(1.16) saturate(1.12)`
to `.source-pdf-page > img`, `.source-pdf-page > canvas`, and
`.source-pdf-zoomimg`. This is a display adjustment for source PDF explanation
pages only. It does not alter source PDFs, generated page images, Marrow visuals,
question keys, or source coordinates. The selected gain darkens fine text and
restores colored headings and tables, though it also makes pale fills lighter.

Before/after browser captures for all three subjects were inspected at phone
width, and Physiology was compared at tablet width. Fine table strokes remained
visible. Generated browser checks asserted the computed filter on inline and
zoomed pages in Anatomy, Physiology, and Biochemistry. The packaged Android
phone and tablet emulator checks asserted the same style in Review Solutions;
the phone image capture showed a colored Anatomy diagram. Engineering run
`36303853277` and full browser/PWA/APK/Android run `36303853023` passed for
product commit `70794a2`. The Cloudflare preview is
`https://ce13d233.nk-qbank.pages.dev` (HTTP 200). Real Android and iPad
appearance still require learner review; CI captures are not physical approval.

Build order matters: `apply_question_experience_v1.py` inserts an earlier style
that `apply_session_experience_v2.py` later replaces. An initial placement in
the earlier style failed the generated browser check, so the rule and a source
contract were moved to the final shared session style.
