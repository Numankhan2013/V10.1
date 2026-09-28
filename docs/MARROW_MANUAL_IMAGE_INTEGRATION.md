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
| `manual-biochem-ch25-28-20260928` | Codex, this user thread | Biochemistry Chapters 25–28, all source visuals and visual text cues | 22 unresolved references across 21 questions: Ch25 2, Ch26 5, Ch27 7, Ch28 8; 0 text-cue items | **CI CROPS ADOPTED / FINAL CI PENDING** | `feature/marrow-manual-images-20260928` from `e6fb3f813eb2c49a5220eec774ae60e551a7169f` |
| `manual-physiology-ch03-07-20260928` | ChatGPT manual lane, this user thread | Physiology Chapters 3–7, all source visuals and visual text cues | 49 unresolved references across 39 questions: Ch3 5, Ch4 2, Ch5 2, Ch6 7, Ch7 33; 0 text-cue items | **CLAIMED / IN PROGRESS** | `manual/physiology-images-ch03-07-20260928` from the canonical claim commit |

The 22 reference IDs for `manual-biochem-ch25-28-20260928` are the unresolved
`Biochemistry` / `CH25`–`CH28` rows of the canonical coverage file at claim time.
They include both roles of `marrow__BIOCHEM_CH28_Q022`; its question figure must
be safe before answering.

The 49 reference IDs for `manual-physiology-ch03-07-20260928` are every unresolved
`Physiology` / `CH03`–`CH07` source-visual row in the same canonical coverage
state. Forty of those references were already source-audited in historical
fast-lane evidence `MANUAL_FASTLANE_34700776495`; that evidence is donor/history
only and must be revalidated against live ownership before release. The remaining
nine unresolved Ch7-tail references (after Q21) require fresh authoritative source
review. No historical registry/progress mutation is transplanted wholesale.

Starting fingerprints for both claims: registry SHA-256
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
| 25 | 2 | 1 | 1 | 0 | Q11 released; Q26 remains tracked for phone-label review; source pages 395–402 |
| 26 | 5 | 4 | 1 | 0 | Q18 held for fine-label readability; source pages 413–417 |
| 27 | 7 | 4 | 2 | 0 | Q2/Q3 held for faint condition labels; Q5 adjudicated invalid against page 426; source pages 424–430 |
| 28 | 8 | 7 | 1 | 0 | Q27 held because source watermark crosses bond detail; Q22 question and explanation figures separately bound |

## Batch `manual-physiology-ch03-07-20260928`

| Chapter | Starting unresolved references | Released in this batch | Review required | Remaining untracked | Notes |
| --- | ---: | ---: | ---: | ---: | --- |
| 3 | 5 | 0 | 0 | 5 | Source pages 44–53; historical fast-lane donor evidence exists |
| 4 | 2 | 0 | 0 | 2 | Source pages 62–66; historical fast-lane donor evidence exists |
| 5 | 2 | 0 | 0 | 2 | Source pages 73–74; historical fast-lane donor evidence exists |
| 6 | 7 | 0 | 0 | 7 | Source pages 94–109; historical fast-lane donor evidence exists |
| 7 | 33 | 0 | 0 | 33 | Source pages 137–158; first 24 unresolved refs have historical donor evidence, final 9 require fresh review |

Batch candidate currently stages 16 PASS references, 5 REVIEW_REQUIRED references and 1 evidence-backed SOURCE_METADATA_INVALID reference; all 22 starting references are tracked. Static local image/progress/coverage checks passed. All eight region-render references now use the exact source crops from Ubuntu build run `36415941717`, inspected at native and expanded size and tied to the source PDF hash. The candidate is not complete until Engineering and full Android/PWA/browser/APK/package CI pass on the resulting exact commit, after which the batch must be reconciled to canonical.

Status is a live work log, not a claim that these images are already integrated. Each owner updates it with evidence and exact verification results as work lands.
