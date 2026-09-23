# Biochemistry explanation handoff — 2026-09-23

Status: **PREAUDITED / CURRENT_UNVERIFIED**

- Subject: Biochemistry
- Next source-order work: Chapter 13, beginning Q1.
- Canonical base branch: `feature/marrow-canonical-full-current`
- Exact base SHA at acquisition: `ce3cab59e750977bee3a78fb01e64861e9de3e17`
- Batch branch: `feature/marrow-explanations-biochem-20260923-ch13-r2`
- Current content/repair commit: `0bd9f430c6e270df18e1ebf6029b9e131512cfce`
- Canonical executable corpus: Anatomy 1115 + Biochemistry 582 + Physiology 1014 = 2711.
- Canonical explanation inventory at acquisition: 635 enhanced / 2076 pending; fingerprint `4f2f313f29f8cd726eaa0e6bc7765590299d4c74415875b0121edb3cb53a3c1b`.
- Biochemistry canonical source raw SHA256: `919f0709b2eb833e302c6f7524b6dd2bd13bfaed638009375b5062135d3795b1`.
- Reconstruction status: none authored yet.

## State transition in this run

The repeated connector-readable Chapter 13 projection problem was repaired in repository code rather than treated as a blocker. `tools/extract_marrow_chapter_projection.py` now reads the immutable complete-corpus sharded bundle (`biochemistry_ch001_028`) and emits a chapter projection without mutating raw source. This removes the need to rely on stale Phase-A audit denominators/projections for source ownership.

## Exact next action

1. Re-read canonical HEAD, `STATE.md`, explanation inventory/fingerprint and live ownership before the next write.
2. If no genuine cross-subject explanation lock exists, run the new extractor for Biochemistry Ch13, audit Q1-forward source objects, and score the contiguous workload block to target 16 / max 20 / max 18 questions.
3. Author only that one bounded Ch13 augmentation batch; preserve source tables/figures/provenance and use reconstruction metadata where required.
4. Run static/source-ID/duplicate/answer-rationale validation, regenerate the deterministic 2711-ID inventory, then advance through exact-head Engineering + full Android/PWA/APK/package/browser CI.

No production promotion. `FULLY_VERIFIED_HISTORY` is unchanged by this checkpoint.
