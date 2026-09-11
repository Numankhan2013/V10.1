#!/usr/bin/env python3
"""Idempotently document connector-readable Marrow source audit access."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNBOOK = ROOT / "docs" / "MARROW_EXPLANATION_AUTOMATION_RUNBOOK.md"
MARKER = "### Connector-readable source audit views"
ANCHOR = "Never rewrite these bundles to improve learner-facing wording.\n"
MANDATORY_ANCHOR = "- `tools/inventory_marrow_explanations.py`\n"
MANDATORY_LINE = "- `tools/export_marrow_source_audit.py` when source audit views are used;\n"

SECTION = r'''

### Connector-readable source audit views

Compression of the immutable `*.zlib.b64.part*` bundles is **not**, by itself, a
source-access blocker. The repository maintains deterministic, read-only chapter
projections on authoritative `main` for connector-only workers:

- manifest: `data/marrow/source_audit/manifest.json`
- Anatomy: `data/marrow/source_audit/anatomy/chapter_<NNN>.json`
- Biochemistry: `data/marrow/source_audit/biochemistry/chapter_<NNN>.json`
- Physiology: `data/marrow/source_audit/physiology/chapter_<NNN>.json`

These files are generated only from the immutable source bundles by
`tools/export_marrow_source_audit.py`. They are **derived audit views**, not a
replacement source of truth, and must never be hand-edited to change medical
content.

For a source audit when the repository interface cannot locally decompress the
shards:

1. read `data/marrow/source_audit/manifest.json` from authoritative `main`;
2. identify the exact subject/chapter file and read the required contiguous
   question objects from that file;
3. verify its `subject`, `chapterId`, `questionCount`, `immutableSourcePrefix`
   and `sourceRawSha256` against the manifest;
4. verify the same subject raw SHA-256 against the current explanation lineage's
   deterministic inventory/source hash when available;
5. use the projected question objects for exact stem/options/key/explanation/
   table/figure/provenance/review-flag audit;
6. continue normal authoring on the resolved explanation lineage — do not write
   explanation work to `main` merely because the audit view lives there.

If a derived audit view is missing, stale, internally inconsistent, or its raw
SHA-256 does not match the current immutable source, treat that as a retryable
source-access infrastructure failure. Regenerate from the immutable bundle or
use the local `load_sharded` decoding path. **Do not** declare source inaccessible
merely because GitHub exposes the underlying bundle as Base64/zlib shards, and
do not invent source content.
'''


def main() -> None:
    text = RUNBOOK.read_text(encoding="utf-8")
    changed = False

    if MANDATORY_LINE not in text:
        if MANDATORY_ANCHOR not in text:
            raise SystemExit("mandatory implementation anchor not found")
        text = text.replace(MANDATORY_ANCHOR, MANDATORY_ANCHOR + MANDATORY_LINE, 1)
        changed = True

    if MARKER not in text:
        if ANCHOR not in text:
            raise SystemExit("source bundle anchor not found")
        text = text.replace(ANCHOR, ANCHOR + SECTION, 1)
        changed = True

    if changed:
        RUNBOOK.write_text(text, encoding="utf-8")
        print("MARROW_EXPLANATION_RUNBOOK_SOURCE_ACCESS_PATCHED")
    else:
        print("MARROW_EXPLANATION_RUNBOOK_SOURCE_ACCESS_ALREADY_PRESENT")


if __name__ == "__main__":
    main()
