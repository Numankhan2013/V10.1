# Source-backed reproductive collections

These are active, bounded inputs for two explicit collection owners; this folder
is not scanned to import arbitrary collections. `source/` preserves the supplied
upstream archive at commit56fe817 byte-identically. `normalized.jsonl` is the
source adapter, with original row fingerprints and full owned PDF-page OCR;
`manifest.json` pins its bytes and the originals. Reviewed batches are separate
source-native display overlays checked against those pins and complete page
ownership. Companion evidence records PDF/OCR/image inspection.

Female1830 has one explicit source-backed normalization correction recorded and
hash-pinned in `source_repairs.json`; original JSONL bytes remain unchanged.
`crop_review.json` records independent root crop geometry corrections and their
confirmation. Scientific image bytes are generated from the pinned LFS PDFs by
the existing CI media owner, not committed as copied screenshots. The source
PDFs are outside the shipped UWorld UI. See `docs/UWORLD_REPRODUCTIVE_BATCH.md`
for counts, source limitations and verification boundaries.
