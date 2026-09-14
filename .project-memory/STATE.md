# STATE.md — Current Project State and Handoff

> Operational state only. Resolve the live branch/commit and CI from Git before acting. Historical detail belongs in `SESSION_LOG.md` and dedicated handoffs.

## Canonical lineage

- Repo: `Numankhan2013/V10.1`.
- Accepted product commit: `125d68b`.
- Accepted baseline: V11.6 remains the rollback product baseline; the Continue Practice contract below is separately user/device accepted.
- **Sole Marrow/product integration trunk:** `feature/marrow-canonical-full-current`.
- Production / `main` remains explicit and guarded; do not promote without user approval.
- Resolve the live canonical HEAD at run start; never hardcode a supposed current HEAD into automation logic.
- Latest accepted Practice behavior was verified from checkpoint `74abb670c3ae088e06653681e85c347212222455`; full run `34695680534` succeeded and the user physically confirmed the Continue Practice flow. This behavior is build-verified, **device-verified**, and user-accepted.

## Complete canonical Marrow ED8 source

- Anatomy: **Ch1–63 / 1,115 questions / 63 source topics**.
- Biochemistry: **Ch1–28 / 582 questions / 28 source topics**.
- Physiology: **Ch1–43 / 1,014 questions / 43 source topics**.
- Global: **2,711 questions / 134 source topics**.
- Raw imported source remains immutable.
- Source handoff: `.project-memory/FULL_CORPUS_CONSOLIDATION.md`.
- Mandatory automation policy: `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md`.

## Product architecture to preserve

- Shared bank architecture: `MARROW_RECORDS → MARROW_BY_SUBJECT → BANKS_BY_SUBJECT`.
- Do not fork Practice, CBT, Review Solutions, FSRS, sync, modules, persistence, analytics or navigation by subject/bank.
- Primary navigation: **Home · FSRS · Tests · Insights · More**.
- Study hierarchy: **My Subjects → subject → bank chooser → Topics journey → topic → Practice/Topic Test**.
- FSRS schedules every answered question. Pause commits answered work only; final submission adds remaining unanswered session IDs as skipped. Questions outside a submitted session remain unseen and excluded.
- Old Wrong Questions dashboard/tab remains retired/replaced by Spaced FSRS.
- Preserve approved V3 Home/Topics/question/Review/FSRS/module/timing behavior; do not restore rank/membership UI.

## Accepted Practice / Continue Practice contract — user/device verified

- Normal Practice footer = **Previous + Next only**.
- Header grid icon and end-of-session boundary open the **same final review grid**.
- Final review action area = **Pause + Submit only**.
- Do not restore the redundant intermediate Question Navigator, `Back to question`, or `Review unanswered` actions.
- Pause preserves the same active session, full original ordered `sessionQuestionIds`, saved/current index, answers, submitted state, timing and progress.
- Pause does not mark the current unanswered question skipped merely because the learner exits.
- Home Continue Practice resumes the same session ID, restores the complete original ordered test/question list, and returns to the saved position with answered progress intact.
- If an older buggy client reduced `questionIds` to one current question, rebuild the visible session from `sessionQuestionIds`; a multi-question session must never collapse to `1 / 1`.
- Special modes (CBT, Review, Wrong/Bookmarks, FSRS, Custom Study Modules) remain outside this override unless explicitly redesigned.
- Postmortem: `.project-memory/PRACTICE_FLOW_POSTMORTEM_2026-09-12.md`; implementation handoff: `.project-memory/CONTINUE_PRACTICE_HANDOFF.md`.
- Status: **accepted / device-verified / user-verified**. Do not describe this flow as pending.

## Mandatory Practice regression sequence

Any change touching Home, Practice, session persistence, sync, question navigation, final review, FSRS injection or build transforms must exercise the generated learner path: start a genuine multi-question Practice session; answer several questions while leaving at least one unanswered; open the final review grid and Pause; confirm Home/paused lifecycle; use the rendered Home Continue Practice control; verify same session ID, complete ordered IDs, saved/current index and preserved progress; verify no `1 / 1` collapse and no Pause-as-Skip mutation.

## Structured explanation-table invariant

- Structured text tables are explanation-owned unless the source is explicitly an image/raster table.
- Non-empty source headers/rows must render as non-empty learner-visible headers/cells in correct order; `[object Object]` is a hard failure.
- Browser regressions must verify meaningful expected cell content, not container existence.
- User physically verified the structured-table repair at `c829599050173d24408b72e8dc564ba501a156b4`.

## Matching/list question architecture — build verified, user re-review pending

- Shared architecture is real and generic; the earlier partial success was **not** a one-record manual patch. Root cause of the residual failures was a brittle hard-coded `match` wording detector plus parser limits.
- User preview review exposed the concrete miss `physiology-9-17` (“Match the ion with its equilibrium potential…”): `physiology-9-6` rendered a table, while `physiology-9-17` leaked a duplicated raw source table because its wording never entered the shared parser.
- Canonical repair lineage culminates at `f0471f5b494c50e36bf7e3952be90a33ba45dea1`. The renderer now uses broad match intent plus structural gating, trims duplicate source blocks, supports A–H / i–viii labels, skips Column/List header references, handles bare letter↔roman notation, and preserves label-only groups without inventing source text.
- Built-artifact audit: **63** PrepLadder records contain `match`/`matching`; semantic table renderings increased from **39 to 53** after the generalized repair. Ordinary prose uses of “match” remain ordinary questions because structural evidence is required.
- `physiology-9-17` is now an explicit generated-browser regression requiring List I/List II, Sodium/Chloride/Potassium/Calcium, -70/+63/+132/-90, exactly four answer choices, and no duplicated `Ion Equilibrium Potential (mV)` block.
- Exact-head Engineering `34837009703` passed. Full Android/PWA/browser/APK/package run `34837009688` passed, including the exact matching browser regression, Continue Practice, APK/package/reproducibility checks, asset verification and PWA preview deployment. Production promotion was skipped.
- Remaining genuine match-like records without enough generic text structure are `26-13`, `physiology-10-10`, `physiology-36-7`, `anatomy-3-12`, `anatomy-14-3`, `anatomy-29-16`, `anatomy-29-33`, `anatomy-30-4`; use source-image/targeted repair rather than guessing.
- Full handoff: `.project-memory/MATCHING_TABLE_ARCHITECTURE_HANDOFF_2026-09-14.md`.
- Status: **BUILD_VERIFIED / USER_REVIEW_PENDING**. Do not call the generalized matching repair user-accepted until the user rechecks the new preview across several chapters.

## Learner-content hygiene

- Whole-corpus serialized JSON/code sanitizer candidate `45f6539fff535fadc6aaa6970894f9ff123422fa` passed Engineering `34738522874` and full run `34738530102` over **2,711 questions / 27,898 learner-facing fields**; raw ED8 source is unchanged.
- User preview review found residual OCR debris in Physiology Ch5/Ch7; verified follow-up `55d7ac8a89c2bbf6a01db5d305b8c975c344c1f3` added source-fingerprinted stable-ID display overrides for those two chapters. Engineering `34740460617` and full run `34740465004` passed; preview `https://c4744474.nk-qbank.pages.dev`; production skipped.
- Do not generalize Ch5/Ch7 cleanliness to unreviewed chapters; use the same source-fingerprinted override workflow for future OCR cleanup.

## Explanation lane

- FULLY_VERIFIED history: Anatomy Ch6 Q1–Q7 at certified checkpoint `58bb99d5c1fc96a98b4f922a963dba16105487d1`; Anatomy Ch6 Q8–Q18 reconciled at `420928ae4e1314cb3a23c8687801be5c7b1f0a8c` and released after canonical dual-green Engineering `34834434837` + full run `34834434831`; Physiology Ch11 Q1–Q6 at `e01cc0b9a8e62885d29b0c2e7ac6417ce8c96f05`.
- No explanation batch is currently owned by the completed Anatomy Q8–Q18 run. Do not retroactively extend it to Q19+.
- Inventory remains **605 enhanced / 2,106 pending / 2,711 total**, fingerprint `995717a6ac450e2b6a530e0521d58a43e67d4e980401989c69b544c38de98300`; raw source hashes unchanged.
- Any next explanation automation must reacquire ownership from the live canonical state and start a new batch.
- Production promotion prohibited.

## Image lane

- Automated Biochemistry image integration is paused. Ch4 Q11 remains `REVIEW_REQUIRED`; two recovery attempts failed before shared registry/progress mutation because embedded PDF text was corrupted. No verified Q11 learner-facing result exists.
- Verified manual Physiology Batch 01 product commit `719e2aa0cfbacb829781e9a7953af4717a6a6f5a` is canonical; Engineering `34699015727` and full run `34699016754` passed; production skipped.
- Batch 02 on historical branch `manual/marrow-physiology-fastlane-20260912-b02` is unverified evidence only: 40 refs audited, 14 metadata-invalid, 12 new assets, 14 specialist deferrals; targeted run `34704088880` failed canonical wiring and was never reconciled.
- Canonical Physiology coverage remains 294 raw / 290 effective / 44 released / 4 invalid metadata / 48 resolved / 21 tracked-unreleased / 225 untracked / 28 text-cue. Next canonical reference: `marrow__PHYS_CH03_Q007:figure:1`.

## Anti-fragmentation rules

- Explanation and image work build from `feature/marrow-canonical-full-current` and the complete 2,711-question corpus.
- Re-read canonical `STATE.md`, live commit, inventory/registry fingerprints and current ownership before editing.
- A stale PR/branch is historical evidence, not a lock or merge target; transplant only stable-ID/content-scoped work after ownership and duplicate checks.
- Reconcile verified work into canonical before starting another conflicting batch in the same lane.
- Accepted product/UI fixes are protected canonical behavior for subsequent content/image/explanation work.

## Known problems / cautions

- Matching/list architecture is now build-verified but still awaits user physical re-review on the new preview; eight structurally incomplete/image-dependent match records remain targeted/manual candidates.
- Physiology image coverage remains incomplete; Biochemistry Q11 remains unresolved/paused.
- Four PrepLadder source records remain intentionally non-answerable rather than recording corrupt attempts: `anatomy-22-4`, `physiology-23-38`, `physiology-24-6`, `physiology-33-33`.
- Production promotion remains prohibited unless explicitly requested.

## Current priorities / Next step

1. **Physical review:** user should inspect the newly deployed preview across multiple matching questions, especially `physiology-9-17`, before accepting the generalized architecture.
2. **Residual matching cases:** if failures map to the eight incomplete/image-dependent IDs, use source-fidelity targeted repair rather than broad parser guessing.
3. **Explanation lane:** any Q19+ work must begin as a new owned batch from the live canonical head.
4. **Image lane:** resume from live canonical after fresh ownership/fingerprint checks; keep automated Biochemistry paused at Q11.
5. Production promotion remains prohibited unless the user explicitly asks for it.

## Memory pointers

- Memory schema: `.project-memory/README.md`.
- Matching architecture handoff: `.project-memory/MATCHING_TABLE_ARCHITECTURE_HANDOFF_2026-09-14.md`.
- Chronological work/CI history: `.project-memory/SESSION_LOG.md`.
- Accepted Practice handoff: `.project-memory/CONTINUE_PRACTICE_HANDOFF.md`.
- Practice postmortem: `.project-memory/PRACTICE_FLOW_POSTMORTEM_2026-09-12.md`.
- Canonical source consolidation: `.project-memory/FULL_CORPUS_CONSOLIDATION.md`.
- Automation policy: `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md`.
