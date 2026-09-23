# STATE.md — Current Project State and Handoff

> Operational state only. Resolve the live branch/commit and CI from Git before acting. Historical detail belongs in `SESSION_LOG.md` and dedicated handoffs.

## Canonical lineage

- Repo: `Numankhan2013/V10.1`.
- Accepted product commit: `125d68b`.
- Accepted baseline: V11.6 remains the rollback product baseline; the Continue Practice contract below is separately user/device accepted.
- **Sole Marrow/product integration trunk:** `feature/marrow-canonical-full-current`.
- Production / `main` remains explicit and guarded; do not promote without user approval.
- Resolve the live canonical HEAD at run start; never hardcode a supposed current HEAD into automation logic.
- Latest verified canonical checkpoint before the automation-readiness handoff: `356cce4`; Engineering `35453226391` and full Android/PWA/browser/APK/package run `35453226292` succeeded on that exact commit (GitHub checked 2026-09-20). The full run deployed preview `https://1b9fe4f4.nk-qbank.pages.dev`; production was not promoted. Recheck CI on the live head after any new commit. User preview review is not blanket acceptance.
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
- Multiple paused chapters (2026-09-23, local candidate, CI pending): `normalPracticeCheckpoints` collection retains every paused chapter with legacy `normalPracticeCheckpoint` as latest-alias; starting a new chapter auto-pauses the live one instead of Resume-or-Discard; Home Continue resumes directly for one saved session and shows a Paused Practice chooser for several; per-ID discard; CBT/Review/FSRS/Wrong/Bookmarks isolation preserved; cross-device merges per session ID without `different-session` conflict. Single-pause behavior is unchanged when only one session is saved. Not yet build-verified or user-accepted.

## Mandatory Practice regression sequence

Any change touching Home, Practice, session persistence, sync, question navigation, final review, FSRS injection or build transforms must exercise the generated learner path: start a genuine multi-question Practice session; answer several questions while leaving at least one unanswered; open the final review grid and Pause; confirm Home/paused lifecycle; use the rendered Home Continue Practice control; verify same session ID, complete ordered IDs, saved/current index and preserved progress; verify no `1 / 1` collapse and no Pause-as-Skip mutation.

## Structured explanation-table invariant

- Structured text tables are explanation-owned unless the source is explicitly an image/raster table.
- Non-empty source headers/rows must render as non-empty learner-visible headers/cells in correct order; `[object Object]` is a hard failure.
- Browser regressions must verify meaningful expected cell content, not container existence.
- User physically verified the structured-table repair at `c829599050173d24408b72e8dc564ba501a156b4`.

## Matching/list and structured-question presentation — build verified, user review pending

- Shared matching architecture is real and generic; the earlier partial success was **not** a one-record manual patch. The original residual failures came from a brittle wording detector plus parser limits.
- Generic repair lineage through `f0471f5b494c50e36bf7e3952be90a33ba45dea1` broadened match intent with structural gating, trims duplicate source blocks, supports A–H / i–viii labels, ignores Column/List header prose, and handles bare letter↔roman notation without inventing source content.
- Built-artifact audit found **63** PrepLadder records containing `match`/`matching`; generic semantic table renderings increased from **39 to 53**. Ordinary prose uses of “match” remain ordinary questions because structural evidence is required.
- `physiology-9-17` (“Match the ion…”) is an explicit browser regression requiring List I/List II, Sodium/Chloride/Potassium/Calcium, -70/+63/+132/-90, four canonical choices, and no duplicated source block. User physically confirmed this ion-question repair in preview.
- Commit `d111b7c6a4efcbdc09c15354072973b78fee35b2` source-fingerprint-reformed the previously listed structurally incomplete/image-dependent matching residuals (`26-13`, `physiology-10-10`, `physiology-36-7`, `anatomy-3-12`, `anatomy-14-3`, `anatomy-29-16`, `anatomy-29-33`, `anatomy-30-4`) instead of leaving flattened prose or guessing. These are no longer pending generic-parser residuals.
- User then exposed a separate structured row-selection family: `physiology-9-22` (axonal transport) is not worded as “match” but contained a duplicated flattened four-column source table with choices `1/2/3/4`.
- Commit `5352eb415e96834f3514139951a17ef7da3f368a` added reusable multi-column override-grid presentation and reformed `physiology-9-22` into **Statement / Type / Direction / Mediator** while preserving the original four choices and canonical `correctOption=3`.
- Exact-head Engineering `34855852205` passed. Full Android/PWA/browser/APK/package run `34855852211` passed, including the new axonal-transport browser regression, matching regressions, Continue Practice, APK/package/reproducibility checks, asset verification, and PWA preview deployment. Production promotion was skipped.
- Rule going forward: for duplicated/flattened source tables or list structures, use safe generic parsing first; if source structure is not safely inferable, perform a stable-ID/source-fingerprinted presentation reform from authoritative source. Do not alter the canonical answer contract and do not leave a clearly recoverable table as raw prose.
- Full handoff: `.project-memory/MATCHING_TABLE_ARCHITECTURE_HANDOFF_2026-09-14.md`.
- Status: **BUILD_VERIFIED / USER_REVIEW_PENDING** for the new axonal-transport and source-backed residual presentations; the ion-question repair itself is user-preview verified.

## Scientific notation presentation — build-verified / user review pending

- One shared, escape-first formatter now serves Practice, CBT and Review stems/options, takeaways, PrepLadder explanations/tables, Marrow native structured text/tables, and the separate enhanced-explanation wrapper. It renders explicit powers, common chemical/physiological subscripts and ionic charges, and only unambiguous OCR-placeholder repairs; raw source data remains unchanged.
- Corpus audit found notation markup in **424 PrepLadder** and **695 Marrow** learner fields. Source-backed overrides repaired `5-10`, `5-14` and two occurrences in `4-12`; seven remaining ambiguous question records require rendered-source review. Residual OCR placeholders remain in 55 PrepLadder and 1 Marrow explanation records. Do not infer missing symbols from context alone.
- All **46 available local checks** and exact-head Linux generated-app/browser/APK/package CI pass at the verified checkpoint above. Physical review remains pending.

## Learner-content hygiene

- Whole-corpus serialized JSON/code sanitizer candidate `45f6539fff535fadc6aaa6970894f9ff123422fa` passed Engineering `34738522874` and full run `34738530102` over **2,711 questions / 27,898 learner-facing fields**; raw ED8 source is unchanged.
- User preview review found residual OCR debris in Physiology Ch5/Ch7; verified follow-up `55d7ac8a89c2bbf6a01db5d305b8c975c344c1f3` added source-fingerprinted stable-ID display overrides for those two chapters. Engineering `34740460617` and full run `34740465004` passed; production skipped.
- Do not generalize Ch5/Ch7 cleanliness to unreviewed chapters; use the same source-fingerprinted override workflow for future OCR cleanup.

## Explanation lane

- FULLY_VERIFIED history: Anatomy Ch6 Q1–Q7 at certified checkpoint `58bb99d5c1fc96a98b4f922a963dba16105487d1`; Anatomy Ch6 Q8–Q18 reconciled at `420928ae4e1314cb3a23c8687801be5c7b1f0a8c` and released after canonical dual-green Engineering `34834434837` + full run `34834434831`; Physiology Ch11 Q1–Q6 at `e01cc0b9a8e62885d29b0c2e7ac6417ce8c96f05`. Biochemistry Ch12 Q1–Q10 was transplanted by stable ID, dual-green on candidate `b541a61b5b037b9f9ae27e71bed5affafc60e3f4`, reconciled through canonical merge `76c3be68b9c24bec90af0d4868f896f687bb670b`, and followed by deterministic inventory refresh to canonical `0c57fd4deb0a0ffb6ea57865bef56ac00b52c1e0`; Q7 remains `needs_manual_review` as carried by the verified donor.
- No explanation batch is currently owned by the completed Anatomy Q8–Q18 run. Do not retroactively extend it to Q19+.
- Inventory is **615 enhanced / 2,096 pending / 2,711 total**, fingerprint `2ad7006f78607d0974269e4aad0baaed9cba6124560885adb3e30f3e6651ce14`; raw source hashes unchanged. This is the deterministic canonical full-corpus inventory after the verified Biochemistry Ch12 Q1–Q10 transplant.
- Any next explanation automation must reacquire ownership from the live canonical state and start a new batch.
- Production promotion prohibited.

## Image lane

- PrepLadder source-visual engineering is now exact-head build verified at product code `2340bd201fabcc05e6d45932c7f8e5fa451e14f0`: Engineering `35053564204` and full Android/PWA/browser/APK/package run `35053564213` both succeeded.
- Stable source-visual ownership resolves by active stable question ID across both `.nk-v113-question` and shared `.nk-v114-session` wrappers, with text fallback retained. This specifically fixes matching/table presentations such as Anatomy `anatomy-9-1`, whose visible stem is semantically rewritten before visual mounting.
- Browser coverage is green for graph, table, diagnostic/clinical image, diagram and multi-panel representatives on phone (`390×844`) and tablet (`820×1180`). The verifier requires stable owner identity, loaded source pixels, preserved aspect ratio/readable size, a real visible fullscreen backdrop/panel covering ≥95% of the viewport, functional zoom, and ≥2 mounted images for the multi-panel representative.
- APK build, packaged product contract, reproducibility manifest, packaged Marrow image-byte checks, artifact upload and Cloudflare preview deployment all passed in run `35053564213`. Production promotion was intentionally skipped.
- Technical source-visual audit remains **422 total / 422 PENDING_MANUAL_REVIEW**. Technical/browser validation is green, but source-visual release certification is **not complete** until those bounded comparison items receive manual review/acceptance.
- Dedicated handoff: `.project-memory/PREPLADDER_VISUAL_VERIFICATION_2026-09-16.md`.
- Marrow image integration is owned by the user's automations. Canonical registry, progress and source-reference coverage checks pass; this certifies the current ledger, not subject completeness. Biochemistry is the next bounded lane: 110 raw / 109 effective / 71 released / 1 invalid / 4 tracked-unreleased / 34 untracked / 31 text-cue items. Next source-order reference is `marrow__BIOCHEM_CH04_Q011:figure:1`. Ch4 Q11 remains `REVIEW_REQUIRED`: two attempts failed before shared-state mutation because embedded PDF text was corrupted. Require authoritative rendered-page review; do not infer or skip the visual. Physiology automation remains paused until Biochemistry coverage recovery.
- Batch 02 on historical branch `manual/marrow-physiology-fastlane-20260912-b02` is unverified evidence only: 40 refs audited, 14 metadata-invalid, 12 new assets, 14 specialist deferrals; targeted run `34704088880` failed canonical wiring and was never reconciled.
- Canonical Physiology coverage remains 294 raw / 290 effective / 44 released / 4 invalid metadata / 48 resolved / 21 tracked-unreleased / 225 untracked / 28 text-cue. Next canonical reference: `marrow__PHYS_CH03_Q007:figure:1`.

## BC3 and BC4 canonical interaction hardening

- BC3 and BC4 were reconciled into canonical through `43328c1`. Canonical Engineering `35818707731` and full Android/PWA `35818707723` passed, including packaged Android 35 emulator phone/tablet and generated browser checks. Full history: `docs/BC4_QUESTION_INTERACTION_DEFECT_LEDGER_2026-09-22.md` and `SESSION_LOG.md`. Physical Android verification remains pending.

## Study UI audit and first defect batch — 2026-09-23

- Baseline screenshots at 320px/390px phone, larger text, and 820px tablet found three defects (CBT grid numbering/crowding, clipped question context, squeezed Analysis header); shared fixes plus generated capture/image checks are in `docs/STUDY_UI_AUDIT_2026-09-23.md`. Local 50-check suite passed; exact final CI, in-place APK upgrade, data preservation, force-close/reopen and sync remain physical acceptance items.

## Anti-fragmentation rules

- Explanation and image work build from `feature/marrow-canonical-full-current` and the complete 2,711-question corpus.
- Re-read canonical `STATE.md`, live commit, inventory/registry fingerprints and current ownership before editing.
- A stale PR/branch is historical evidence, not a lock or merge target; transplant only stable-ID/content-scoped work after ownership and duplicate checks.
- Reconcile verified work into canonical before starting another conflicting batch in the same lane.
- Accepted product/UI fixes are protected canonical behavior for subsequent content/image/explanation work.
- Automation start and reconciliation instructions: `.project-memory/IMAGE_AUTOMATION_READY_2026-09-20.md`. The historical percentage-correct pilot branch is not integrated and must not be used as an image base.

## Known problems / cautions

- PrepLadder source-visual technical/browser gates are green, but **422 audit entries still require manual source-comparison review**; do not label that lane release-certified yet.
- New axonal-transport and source-backed residual structured presentations are build-verified but still need user physical preview review before acceptance.
- Future flattened table/list questions may exist outside literal `match` wording; treat them as structured-presentation defects, not ordinary prose cleanup.
- Seven remaining ambiguous question records and 56 explanation records retain `■` OCR loss after safe scientific rendering; resolve them from rendered authoritative source with stable-ID/fingerprinted cleanup rather than guessing globally.
- Physiology image coverage remains incomplete; Biochemistry Q11 remains unresolved/paused.
- Four PrepLadder source records remain intentionally non-answerable rather than recording corrupt attempts: `anatomy-22-4`, `physiology-23-38`, `physiology-24-6`, `physiology-33-33`.
- Production promotion remains prohibited unless explicitly requested.

## Current priorities / Next step

1. Finish the multiple-paused-chapters candidate on `feature/marrow-canonical-full-current` (local 50/50 green; exact-SHA Engineering + full Android/PWA/browser/APK/package CI pending). Verify Home chooser, per-chapter resume/discard, CBT/Review/FSRS isolation, and cross-device per-ID merge; then request user preview acceptance. Do not promote production.
2. Complete the study UI batch by inspecting the final image screenshots and exact-SHA Engineering/full Android/PWA/browser/APK/package results. If green, retain the accepted Practice/Review behavior and continue narrow evidence-led UI checks. Physical canonical APK verification remains outstanding; production promotion remains separately guarded.
3. Image automation remains independently owned from live canonical per `.project-memory/IMAGE_AUTOMATION_READY_2026-09-20.md`; P0 Phase 3 has 219 source-review candidates (not proven defects) with Phase 6 sign-off and user acceptance pending.

## Memory pointers

- Memory schema: `.project-memory/README.md`.
- PrepLadder visual verification handoff: `.project-memory/PREPLADDER_VISUAL_VERIFICATION_2026-09-16.md`.
- Matching/structured presentation handoff: `.project-memory/MATCHING_TABLE_ARCHITECTURE_HANDOFF_2026-09-14.md`.
- Chronological work/CI history: `.project-memory/SESSION_LOG.md`.
- Accepted Practice handoff: `.project-memory/CONTINUE_PRACTICE_HANDOFF.md`.
- Practice postmortem: `.project-memory/PRACTICE_FLOW_POSTMORTEM_2026-09-12.md`.
- Canonical source consolidation: `.project-memory/FULL_CORPUS_CONSOLIDATION.md`.
- Automation policy: `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md`.
