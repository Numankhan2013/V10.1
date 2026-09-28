# Manual Marrow image integration ledger

This is the shared ownership and progress ledger for manual image work on the
canonical branch, `feature/marrow-canonical-full-current`. Read the live remote
version before choosing a batch. The source-reference denominator is
`data/marrow/images/coverage.json`; a chapter claim includes every question and
explanation figure reference in that chapter, including later discovered source
visuals. Raw source and source PDFs remain unchanged.

## Claims

| Batch | Owner | Exclusive source scope | Starting backlog | Status | Working branch and base |
| --- | --- | --- | --- | --- | --- |
| `manual-biochem-ch25-28-20260928` | Codex, this user thread | Biochemistry Chapters 25–28, all source visuals and visual text cues | 22 unresolved references across 21 questions: Ch25 2, Ch26 5, Ch27 7, Ch28 8; 0 text-cue items | **CLAIMED / IN PROGRESS** | `feature/marrow-manual-images-20260928` from `e6fb3f813eb2c49a5220eec774ae60e551a7169f` |

The 22 reference IDs are the unresolved `Biochemistry` / `CH25`–`CH28` rows of
the canonical coverage file at claim time. They include both roles of
`marrow__BIOCHEM_CH28_Q022`; its question figure must be safe before answering.
Starting fingerprints: registry SHA-256
`799f0c3ae5753f9321f46803871032f255a0548798c4884681f297a5eaa729a2`,
progress SHA-256
`c2ecb00176b4edfd946006cd650ffb513c855b065a73af53abdbcf25b332366d`,
coverage SHA-256
`a932992616c6431916dffcc2d063710d6721a1d773f32dba4698b0532b1a63de`.

## Coordination rule

1. Claim a separate subject/chapter range in this file on the **live canonical
   branch**, commit it and push with an ordinary fast-forward before source work.
   Check the remote branch head again immediately before the push. Never take an
   overlapping range while its claim is active, even after a restart.
2. A claim reserves source ownership, not permission for concurrent writes to
   `registry.json`, `progress.json`, `coverage.json` or production image assets.
   Agents may inspect separate ranges in parallel. Re-fetch and reconcile the
   shared image state before each integration commit; one writer publishes at a
   time. Never choose one side of a registry conflict.
3. Record each chapter's released, review-required and still-untracked counts
   here. A deferred image stays in the claimed batch until the owner explicitly
   releases or hands off that chapter. A restart resumes the claim after reading
   this ledger and live coverage; it does not create a second claim.
4. Mark a batch complete only after source review, image validation, progress
   and coverage checks, local gates, and the required exact-head CI. Reconcile
   the verified image state to canonical before releasing the claim. Production
   promotion and physical acceptance remain separate.

## Batch `manual-biochem-ch25-28-20260928`

| Chapter | Starting unresolved references | Released in this batch | Review required | Remaining untracked | Notes |
| --- | ---: | ---: | ---: | ---: | --- |
| 25 | 2 | 0 | 0 | 2 | Source pages 395–402 |
| 26 | 5 | 0 | 0 | 5 | Source pages 413–417 |
| 27 | 7 | 0 | 0 | 7 | Source pages 424–430 |
| 28 | 8 | 0 | 0 | 8 | Source pages 436–450; Q22 has question and explanation figures |

Status is a live work log, not a claim that these images are already integrated.
The owner updates it with evidence and exact verification results as work lands.
