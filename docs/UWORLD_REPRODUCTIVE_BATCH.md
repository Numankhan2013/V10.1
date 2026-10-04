# UWorld reproductive collections and Continue Practice — 2026-10-04

This batch adds **Male Reproductive System (52 questions)** and **Female
Reproductive System & Breast (81 questions)**, each retaining two original
blocks. They appear in My UWorld, with collection-specific two-tone icons in
the library, blocks and session header. Existing subjects and study engines
remain unchanged. Production promotion is not authorized for this batch.

## Source and architecture

The supplied JSONLs and PDFs at source commit
`56fe81724f120b5b6d5277a82e418714278c1493` are authoritative. Original JSONLs,
manifests, indexes and LFS pointers are archived byte-identically under
`data/uworld/prepared/<collection>/source/`. A reusable `ImportedCollection`
owner checks source hashes, original record fingerprints, contiguous page
ownership, blocks, keys and percentages before installing reviewed display
documents through the existing UWorld registry/presenter/media pipeline.
Normalized rows retain complete per-page OCR for audit; runtime data omits that
page archive. No second question engine, persistence schema or scoring path is
introduced.

Six Luna/high source-review batches cover all 876 PDF pages and all 133
questions. Native explanation prose, option discussions, objectives and choice
percentages are retained. The two collections contain 46 native tables and
306 source figure placements (Male: 20/72; Female: 26/234). Root inspection of
all crop contact sheets corrected 289 source bounds, preserving scientific
labels while removing viewer controls. Three additional essential question
crops were confirmed at full size. Original image attribution remains.

Two essential Male exhibits absent from the upstream JSONL were recovered
from the PDF (15800 gross specimen, 16001 unannotated histology). Female11652
and20083 use complete source popup exhibits rather than clipped inline captures.
Female1057 retains the complete A–D anatomy figure without duplicated options.

Female1830's original JSONL merged two choices and corrupted a karyotype.
The pinned `source_repairs.json` records original row/options and PDF pages
438–439. Normalized/display choices restore all six source options and their
reported percentages; the original import stays unchanged. Percentages that
sum to97 are retained as reported, not normalized.

## Source limitations

Male block1 contains39 observed questions; no missing Item40 is fabricated.
Female block1 contains two distinct Item40 IDs (18714 and127); both remain.
Missing choice statistics remain null (Male343,580,839,11762; Female1015).
Male1902/19020 have source explanation/choice-letter inconsistencies, and
Male15804 contains the source phrase “beta human chorionic growth hormone.”
These are recorded source editorial issues rather than silently rewritten
clinical content. Pregnancy was not added: the supposed upstream JSONL files
contain unavailable-file placeholder strings, not a usable extraction.
Existing Biochemistry1244 remains an unscored reference with an absent exhibit.

## Continue Practice and Today's Focus

The subject/bank Topics action now resolves an eligible ordinary Practice
session or durable checkpoint within that exact bank. It resumes the original
ordered question list at the saved question, retaining answers, submitted
state and progress, even after reload or while a special review occupies the
active-session slot. It never chooses a different bank's paused session.
Without a saved session, it opens a genuinely incomplete topic; completed
banks omit the misleading zero-remaining action. Source-blocked UWorld items
are excluded from fallback practice counts.

Today's Focus reads position/total from the saved ordinary Practice context,
rather than an unrelated active session. Multiple saved sessions keep the
existing chooser. Timed-test priority, FSRS/Revision/bookmark/module exclusions,
conflict protection, durable Pause and the accepted warm-paper/violet appearance
remain intact. Impeccable guidance was applied to clarity and coherent state
feedback; no animation delays were added.

## Verification

104 local source/behavior/syntax checks pass. Continue Practice browser checks
pass at320/390/820px, including multiple paused sessions, durable resume,
submission and special-mode boundaries. Targeted Topics/Today's Focus checks
pass at390/820/1440px, including reload, bank scoping, saved position and
completed banks. The local five-collection diagnostic also passes all133 new
questions at390/820/1194/1440px; its Poppler crops establish source geometry,
not packaged byte certification.

[Engineering37205213243](https://github.com/Numankhan2013/V10.1/actions/runs/37205213243)
and the complete build/package job in
[37205213240](https://github.com/Numankhan2013/V10.1/actions/runs/37205213240)
pass. An earlier timed-builder check used a case-insensitive substring that
matched both Male and Female; it now matches the exact registry subject label
and passes locally and in CI. App selection logic is unchanged.

The original full run is cancelled after Playwright's APK installer hits Node's
string limit before launch; it is not described as green. The driver now streams
the file with adb and closes the device on installation failure. Android-only
[recovery37208580256](https://github.com/Numankhan2013/V10.1/actions/runs/37208580256)
at verifier33642325 validates and reuses the exact674,756,225-byte APK for product
e9a1c15 without regeneration or deployment. Both phone and tablet pass native
Back/exit confirmation, force-stop resume, three durable paused sessions,
Practice/Review/FSRS, PYQ CBT/Review, timed-grid abandon and retake comparison.

The verified preview is **https://f0ec5f5d.nk-qbank.pages.dev**. Actual hosted
390/820/1194/1440px flows pass for all133 new questions, alongside the prior
three collections. HTML SHA-256
`d65c4ced30a2aff44cb8494fbd350fb70b11612fe3497ec87df266ef7ea8a6a5`
matches the CI browser-measured build. All589 hosted image hashes and offline
paths match the package; all283 previous media identities remain unchanged.
No large APK artifact was downloaded locally; package identity comes from CI,
exact-artifact recovery and hosted hash comparison.

Production https://nk-qbank.pages.dev retains its prior HTML SHA-256
`086b04f41fcf610af844b76652b7c6368392dc26d9bd8f609b258b2a6e77897b`
after preview upload. No production promotion is authorized. No physical-device,
live-account or clinical certification is inferred.

For the next batch, keep the explicit registry, immutable sources, pinned
normalization repairs and complete source review. Track image/APK size alongside
coverage before a substantially larger rollout; this batch exposed a real
verification transport limit. Preserve source fidelity while considering reuse
of unchanged generated figures to reduce repeated CI work.
