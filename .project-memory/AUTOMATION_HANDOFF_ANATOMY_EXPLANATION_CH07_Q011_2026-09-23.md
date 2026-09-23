# Anatomy explanation automation — Chapter 7 Q11+ — 2026-09-23

Status: PREAUDITED / CURRENT_UNVERIFIED ownership acquired; content authoring pending.

- Subject: Anatomy.
- Sole integration trunk: `feature/marrow-canonical-full-current`.
- Exact canonical base at acquisition: `832d11ffbcb8de18927cb006f7ddb4e2eafacb01`.
- Batch branch: `feature/marrow-explanations-anatomy-20260923-ch07-q011`.
- Verified history boundary: Anatomy Ch7 Q1-Q10 is already canonical; next incomplete source-order question is Ch7 Q11.
- Canonical source scope: Anatomy 63 chapters / 1,115 questions; global 2,711 questions.
- Raw Anatomy SHA-256: `f38dc86163ff7ca10b1cfbc72e075724abe7cff5360a8fd642671d1d4eb1d387` (immutable).
- Inventory at acquisition: 635 enhanced-reference / 2,076 pending / 2,711 total.
- No content-bearing Anatomy side branch was found for Q11+; the older `feature/marrow-explanations-anatomy-20260922-ch07-q011-next` points only to historical canonical `54f7d0fe...` and is stale evidence, not ownership.
- Reconstruction status: not yet adjudicated for Q11+; source audit must decide per question.
- CI: not applicable yet; no learner-facing candidate commit exists.
- Production: prohibited / untouched.

Failure classification for this run: SOURCE_EXTRACTION_TOOLING_GAP. The authoritative complete Anatomy corpus is stored as compressed sharded bundles; the current GitHub connector can read repository text but cannot execute the repository decoder/generator to expose Ch7 Q11+ records, and code search does not index those compressed records. Two bounded source-discovery attempts were made (stable-ID code search and canonical tree/source-manifest inspection). Do not infer stems/options/keys or author from medical memory.

Exact next action: on the next recurrence, first re-read live canonical HEAD/STATE/inventory/ownership. If this branch still contains only this handoff and canonical advanced, replace/reacquire from exact live canonical rather than treating this branch as a lock. Use an execution-capable repo environment or a newly available canonical expanded-text artifact to decode `data/marrow/anatomy_ch001_063.zlib.b64.part*`, audit contiguous Ch7 Q11 onward, workload-score toward 16 (max 20 / 18 questions), then author one bounded batch and continue static validation/CI. Keep the worker enabled while Anatomy is incomplete.
