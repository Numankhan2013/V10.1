# Source-reviewed Biochemistry display layer

Six batches contain132 source-pinned display documents. Immutable originals are
in `data/uworld/automation_ingest/biochemistry/blocks_001_003`; source PDF lives
in the Git LFS source directory. SHA-256 is pinned by each batch and the compiler.
Every record pins its canonical JSON row and lists all assigned reviewed pages.

User-authorized gpt-6-luna/high agents viewed assigned source pages question by
question, transcribed readable source text, reconstructed native table relationships,
recorded actual percentages and focused scientific crop coordinates. Independent
reviews and root checks corrected source UI leakage, text overlap and clipped crops.
This is model-assisted source fidelity review, not clinical approval.

Schema1 provides question text, unchanged letter/key options, ordered paragraph /
table / figure nodes, educational objective, statistics, status and issues. Figures
use rotated PDF DISPLAY coordinates in points, explicit page and role; scientific
content must remain intact. The compiler derives asset paths, so scratch image
paths are not an input contract. Missing values use null. Blocked records remain
unscored references, never silently enter study pools.

Run `test_uworld_reviewed_document.py` for source/key/coverage/drift protections.
CI owns PDF crop generation, image inventory, offline/PWA and APK byte checks.
Further source corrections belong in these overlays, not the canonical JSONLs.
