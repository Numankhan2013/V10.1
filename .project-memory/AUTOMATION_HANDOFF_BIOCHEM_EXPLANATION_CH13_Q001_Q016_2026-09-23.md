# Biochemistry explanation Ch13 Q1–Q16 automation handoff

Status: STATIC_VALIDATED / CURRENT_UNVERIFIED

- Subject/range: Biochemistry Chapter 13 Q1–Q16 (`marrow__BIOCHEM_CH13_Q001` … `Q016`).
- Logical branch: `feature/marrow-explanations-biochem-20260923-ch13-r5` (same logical batch; no replacement branch).
- Canonical base for this logical candidate: `81333f0af6e0ab2a5e4502a90e8086c163f5dff6`; authored stable-ID content commit `562074dc171442bd2303ec632e3af7d67947bbf9`; previous checkpoint head `f15dcb224ffa101833d142e8de49370348c9a4d8`.
- Source: canonical `biochemistry_ch001_028`; recorded raw source SHA-256 `919f0709b2eb833e302c6f7524b6dd2bd13bfaed638009375b5062135d3795b1`.
- Batch workload: 16 clean contiguous questions / score 16, source-audited from the canonical projection.
- Inventory baseline: 646 enhanced / 2,065 pending / 2,711 total; fingerprint `b32859a10f0aa88af8da1d3ef34cba64be946153fff2c06fd507620306ef28b2`; expected deterministic delta remains +16 enhanced / -16 pending.
- PR: #68 (`Biochemistry Ch13 Q1-Q16 explanation augmentation`) remains open against `feature/marrow-canonical-full-current`.
- Exact-head Engineering Gate run `35908888330` on `f15dcb224ffa101833d142e8de49370348c9a4d8` PASSED. It passed project-memory/preflight/Python compilation, Marrow pilot source validation, image/source coverage, taxonomy, explanation inventory, Biochemistry gold-sample and rollout validators, Physiology/Anatomy rollout validators, content hygiene, product contract, deterministic build pipeline, and shared study/FSRS/interaction regressions. This advances the content to STATIC_VALIDATED.
- Full Android/PWA run `35901803409` on the same exact head FAILED at step 66 `Install isolated Marrow bank pilot`; all earlier shared study/FSRS/interaction transforms passed and downstream browser/APK/package/reproducibility gates were skipped.
- Precise failure evidence: `apply_marrow_bank_pilot.py` emitted `Marrow Biochemistry explanation batch identity/status mismatch: explanation_biochem_ch13_q001_016_v1.json` and exited 1 after confirming `MARROW_EXPANDED_BANKS_OK anatomy=1115/63 biochemistry=582/28 physiology=1014/43 total=2711`. The augmentation file still declares `scope.status=content-authored`, while Engineering has now independently passed the explanation validators. This is a candidate metadata/build-ingestion mismatch, not a source-ID/content correctness failure.
- Exact next action: repair the Ch13 augmentation status/ingestion contract in place on this same r5 branch (no r6/r7), preserving the 16 stable-ID payload and raw source; then rerun exact-head Engineering and full Android/PWA. If all browser/APK/package/reproducibility/preview gates pass, reconcile PR #68 into canonical before release.
- Production promotion prohibited.
