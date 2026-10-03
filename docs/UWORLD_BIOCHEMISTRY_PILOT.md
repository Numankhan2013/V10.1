# UWorld Biochemistry reference pilot

Only Biochemistry is integrated, from `uworld-poisoning-env-block-01-20261003`
at `2cc0ea8f9ab4d2e3ac18d32b94b58b36a0f3700d`. Original canonical JSONLs,
QA material and Git LFS PDF remain unchanged. No other UWorld collection is imported.

The corpus has120 nominal and12 supplemental questions:132 stable IDs and729
assigned source pages. The supplied PDF is pinned to SHA-256
`806d95d6f09dde57d34e0d0b5fda69298a7789041bb570ce4fa6dd1c95d4fae9`.
Six high-effort Luna batches visually reviewed each question's assigned pages.
Independent text/crop checks corrected duplicated OCR, UI leakage and cropped
scientific labels. This is model-assisted source review, not clinical certification.

## Shared architecture

`uworld_biochemistry.py` adapts immutable sources to one shared bank record under
the collection namespace `UWorld · Biochemistry`. Traditional My Subjects retains
its three subjects and incumbent banks. Home → My UWorld → Biochemistry → four
original blocks provides independent collection navigation, including Supplemental.
Mixed disciplines are not recategorized as traditional Biochemistry questions.

Question IDs and complete `uworldSource` remain unchanged. The separate reviewed
layer in `data/uworld/reviewed/biochemistry` pins every original row and the PDF;
`uworld_reviewed_document.py` validates all page coverage, original answer keys,
choice labels, source percentages and explicit question/explanation/option image
roles. Ordered paragraph, native table and focused figure nodes preserve source
flow. Forty-seven originals lack reliable topic metadata; no taxonomy is invented.

Practice, CBT, Review Solutions, bookmarks, notes, modules, FSRS, history, sync and
checkpoints use the shared engines. Read-only compatibility aliases resolve old
Biochemistry/UWorld bank and module scope keys without rewriting user storage.
Four through eight source choices are supported without incumbent extraction repair.

`build_uworld_reviewed_figures.py` runs in CI after retrieving the original LFS PDF.
It creates lossless focused crops from reviewed display coordinates, deterministic
content paths and a source/byte inventory. The existing recursive web copy and
service-worker precache provide offline images; `verify_uworld_media_package.py`
checks every generated image and its PWA/APK packaging. The154MB source PDF is not
shipped to learners as the explanation UI.

## Native question experience

The user accepted the previous scrollable17px/70ch typography on phone, iPad and
desktop; it is preserved. Impeccable Operate/Read, typeset and craft guidance informs
restrained layout, source-label emphasis, table overflow, figure captions and warm
educational objectives. Screenshots of the entire source application are not used
as primary explanations. Figures use the existing fullscreen zoom/pan viewer.

Original explanations and option reasoning retain their order and completeness.
Source-labelled choice discussions form a distinct Understanding the other choices
section with quiet labels and comfortable spacing; they are not forced into Marrow
rationale cards. Educational objectives remain after explanations to avoid giving
away unanswered questions. Raw OCR and source issues are available in Source details.

Source selection percentages appear at the right of each option immediately after
a Practice answer and in Review Solutions. Reserved width prevents answer text
reflow. Correct/wrong feedback and percentages accompany the existing immediate
commit, without an extra click, disclosure or scroll. Timed CBT reveals none of
these values until submission/review. Aggregate correct percentage is a quiet
post-answer line. Zero is displayed; missing source values stay blank.

Essential stem/option image failures disable unsupported answers and offer Retry
figures. Navigation, Pause and Finish remain available. Explanation-only images
never block answer commits. No action is delayed for motion.

## Source limitations and scaling

**131 questions are available for scored practice;1244 remains an unscored reference.**
Its essential physical-examination stem exhibit is absent from the supplied PDF.
References create no attempt, score or FSRS record and are excluded from new study
pools. Source review recovers26 native tables and184 focused figure placements.

Educational objectives1486,1071 and107111 are clipped in the supplied screenshots
and stay null. The nitrogen-transport figure1369 and collagen figure1244 are
partially clipped in the source; visible scientific content is retained with notes.
A few exhibit crops retain a minimal adjacent source border where trimming would
remove scientific labels or diagram content.
Twelve aggregate percentages and66 option percentages are unavailable, including
11914 option A. Missing words, figures, values and statistics are never fabricated.

Before scaling: retain this typed-document/source-pin/role pattern; resolve source
omissions with better originals if available; inspect the final pilot on real
study sessions; check scientific symbols, tables and source choice reasoning;
budget offline assets and independent reviews per collection. Other collections
must provide their own source evidence and coordinates. Biochemistry-first remains
the recommendation and scope.

## Revision sessions and mistake provenance

Mistakes and Bookmarks use full eligible frozen queues; Due Review uses the admitted
FSRS priority queue and existing daily cap. Labels are Practice mistakes, Practice
bookmarks and Review due. Unseen retains its separate random20 action.

Pause preserves exact membership, position, answers, timing and ratings. Finish
saves answered work only; untouched questions remain eligible without fabricated
skipped attempts. Finishing with no answers creates no result. Storage rollback
and retry remain shared.

Practice mistakes derives from unresolved ordinary Practice/test misses. A correct
answer from any flow resolves one. Scheduled-review failures affect FSRS scheduling
without creating or resurrecting Practice mistakes. Undo remains respected and
persisted attempts/scheduler logic are unchanged.

## Search-engine exclusion

[Search engine exclusion](SEARCH_ENGINE_EXCLUSION.md) documents robots metadata,
robots.txt, static headers and source-worker coverage. These discourage cooperative
indexing but do not hide a public GitHub repository/history or restrict direct
access. Private source storage and server authentication are needed for access
control; obfuscation does not provide it.

## Validation status

The certified prior OCR pilot is product c7b5053, full run37128060483,
[preview](https://690495d5.nk-qbank.pages.dev) and [PR93](https://github.com/Numankhan2013/V10.1/pull/93).
The user confirmed that layout on phone/iPad/desktop and the continuous Revision
workflow. The reviewed reference refinement passes101 local checks and actual generated
390/820/1194/1440px study flows, including direct option percentages without reflow,
source figures/zoom/retry, native table cells/overflow, deferred CBT, Review
Solutions, modules and FSRS-only mistake separation. Incumbent phone/tablet
interaction checks pass. Full packaging and hosted certification are pending. Production remains unchanged. New physical-device acceptance is separate.
