# Marrow automation ingest

This directory is the stable handoff point for canonical JSONL files produced by the Marrow digitization automations.

- Branch: `feature/marrow-bank-pilot`
- Repository: `Numankhan2013/V10.1`
- Anatomy: `data/marrow/automation_ingest/anatomy/`
- Physiology: `data/marrow/automation_ingest/physiology/`
- Biochemistry: `data/marrow/automation_ingest/biochemistry/`

Each successful digitization run should:
1. Finish source-faithful validation and write the canonical chapter JSONL to the project Library first.
2. Push the exact validated canonical JSONL to the matching subject folder here.
3. Preserve the canonical filename and never overwrite a different validated chapter artifact.
4. Treat a GitHub push failure as a handoff failure only: do not invalidate the completed digitization, do not disable the recurring automation, and retry on the next run.
5. Never push source PDFs, OCR scratch files, manifests, review reports, or joint validation reports here unless explicitly requested.

Codex/integration agents should scan the relevant subject folder for zero-padded chapter files and ingest any validated chapter not yet integrated.
