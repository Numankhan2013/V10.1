# UWorld Ophthalmology: first PDF-only collection

The user authorizes reuse of supplied JSONLs and source PDFs, with Ophthalmology
as the first collection extracted without a supplied question JSONL. This batch
adds only its original30-question block. Existing packages for other collections
remain available for later bounded batches.

## Source and extraction

Original source branch: `uworld-poisoning-env-block-01-20261003`, commit
`56fe81724f120b5b6d5277a82e418714278c1493`.
Original path: `data/uworld/Source_pdfs/opthalmology/UW 2024 - Ophthalmology - block 1 - OCR.pdf`.
SHA-256: `ab4aadac54fbc78c9db9fca4b561cb5d0ee0ba4ade3f72066c72bf64021843dc`.
Size45,046,309 bytes;204 pages with1349.28×720.72pt display geometry.

The original LFS pointer is reused unchanged. Text extraction supplies an audit
transcript, while three user-authorized Luna/high batches inspect every original
page image and reconstruct questions, keys, source percentages, complete reasoning,
choice discussions, objectives, native tables and focused diagrams/photos.
Pages without OCR-readable question headers are assigned by their visually checked
position within the source item; the page manifest accounts for all204 pages.
No source item is inferred from clinical knowledge or another collection.

The integration creates its own immutable JSONL snapshot rather than requiring
the user to prepare one. Each row retains the original question ID, complete
searchable stem, source choices/key, source prose and per-page OCR. A separate
PDF/row-hash-pinned display document carries source ordering, tables and figures.
Source screenshot chrome and repeated viewport overlaps are excluded from display;
scientific content remains. Unknown source values remain null rather than guessed.

## Integration and design

`uworld_ophthalmology.py` supplies the existing collection registry under
`UWorld · Ophthalmology`, with `uworld_ophthalmology_block_1`. Source IDs use the
canonical `UWORLD_<original-id>` form and are checked for collisions. The existing
Practice/CBT/Review, FSRS, continuous Revision, bookmarks, modules, persistence,
sync and analytics engines remain authoritative.

Ordered source-display stem text is rendered separately from the complete
searchable stem: an inline exhibit can sit between clinical context and the final
prompt without duplicating the prompt or hiding it from Search. This is a small
extension of the existing UWorld display document, not a new question engine.
Original Biochemistry/Poisoning display content and media identities are protected.

Installed Impeccable4.5.0 Operate/Read, polish and harden guidance informs the
running audit. Preserve accepted warm study surfaces,17px source-native reading,
comfortable measure, restrained source choice discussions, immediate side-of-option
percentages, objective after reasoning, fixed question footer and existing zoom.
Native tables scroll locally when needed. No explanation makeover or new motion.

## Verification status

All 30 questions and 204 pages have completed the source-image pass. Independent
root checks confirm all 30 original answer keys and exact archival page OCR.
There are eight native tables and 77 recovered figure placements; 41 crop
repairs preserve complete scientific labels and remove source viewport chrome.
All 103 local checks pass. The running diagnostic at 390/820/1194/1440px passes
all 30 questions, graphical choices, native tables, zoom, Pause/Continue, timed
tests, modules and Search, alongside both previous UWorld collections.

Ophthalmology product4b23940 passes full37188960243 and its Engineering gates.
Final audited main product315cfcc passes Engineering37191000202 and complete
main37191000207, including production APK identity, ordered PWA/APK/package,
media/offline/browser checks and Android phone/tablet emulators. PR98 is merged;
approved release 37192960486 reuses that exact verified artifact for production.

**https://nk-qbank.pages.dev** is live. Its HTML matches the final CI-measured
SHA-256 `086b04f41fcf610af844b76652b7c6368392dc26d9bd8f609b258b2a6e77897b`. Root HTML/config/service worker/inventory
bytes match the immutable upload https://92774e98.nk-qbank.pages.dev.
Actual hosted four-width UWorld flows pass, including all 30 Ophthalmology
questions, eight tables and five graphical choices. All 283 media assets match
the packaged inventory and offline paths; all 206 previous assets are unchanged.
See `PREPRODUCTION_AUDIT_2026-10-04.md` for release and security evidence.
No physical-device or clinical certification is claimed. Biochemistry1244 remains
unscored because its essential source exhibit is missing; other documented source
clipping and null statistics remain preserved rather than invented.
