# Anatomy remaining explanation refinement — 2026-10-01

**Owner:** Anatomy remaining worktree `work/luna-anatomy-remaining`, based on `d4abce86068b4221e61e541c34dd29258de61cca`.

**Source:** immutable Anatomy ED8 source bundle SHA-256 `f38dc86163ff7ca10b1cfbc72e075724abe7cff5360a8fd642671d1d4eb1d387`. The complete source and assignment were supplied read-only in `/tmp/explanation-remaining-20261001/`. The earlier source audit `.project-memory/source-audits/anatomy-ch09-q001-q018.json` is retained unchanged.

## Checkpoint 1

Authored 48 of the 914 pending actionable Anatomy IDs in seven new augmentation files:

- Ch9 Q15–18 (`explanation_anatomy_ch09_q015_q018_v1.json`)
- Ch10 Q19 (`explanation_anatomy_ch10_q019_q019_v1.json`)
- Ch11 Q11–24 (`explanation_anatomy_ch11_q011_q024_v1.json`)
- Ch11 Q25–26 (`explanation_anatomy_ch11_q025_q026_v1.json`)
- Ch12 Q1–14 (`explanation_anatomy_ch12_q001_q014_v1.json`)
- Ch12 Q15 (`explanation_anatomy_ch12_q015_q015_v1.json`)
- Ch13 Q1–12 (`explanation_anatomy_ch13_q001_q012_v1.json`)

Each file is bounded to one chapter and 14 or fewer questions, uses the exact `approved-rollout` scope and canonical base SHA, and adds new IDs only. Every four-option SBA has exactly the three source-key-matching distractor rationales and one to four case-sensitive emphasis anchors. Display text retains source details; native table and figure data remains in the untouched source record. Ch12 OCR cleanup is annotated as resolved reconstruction with the raw fragment, clean reconstruction, PDF pages and review note. Ch9 Ch12 work does not change the answer key or completeness ledger.

## Validation and status

The shared batch validator passed: `python3 /root/V10.1/tools/validate_marrow_explanation_batch.py --root /root/luna_anatomy_remaining --base-sha d4abce86068b4221e61e541c34dd29258de61cca` → `MARROW_WORKER_BATCHES_OK files=7 questions=48 source_keyed=true detail_retention=true baseline_and_gates_preserved=true`.

This checkpoint is authoring/source-review validation only. It is not a combined preview, browser, CI, APK or release certification. The remaining 866 actionable IDs still require their assigned bounded files. The 13 completeness-gated IDs remain untouched.
