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

## Bank-aware modules and next study phase — 2026-09-25

- Isolated branch: `feature/qbank-bank-aware-modules-20260924`; resolve live
  HEAD and CI before integration. Production and canonical are untouched.
- Bank-scoped modules/PYQs, restored Home focus, and the searchable full-page
  topic picker passed Engineering `36099517685` and full browser/PWA/APK/
  emulator `36099507918` at `7b7eef2`. The user confirmed the Topics flow works.
- Source cleanup at `a94b329` passed Engineering `36101824054`; full build
  `36101826646` is running. Questions has no duplicate Source control; selected
  regular and PYQ topics both contribute. Saved modules keep frozen IDs.
- Next study-intelligence candidate adds question-linked personal notes after
  answering and in Review, with durable storage and account sync. Local behavior
  checks pass; generated browser/APK/physical review is pending.
- Tests, FSRS and Insights stay dedicated; the builder retains Wrong, Unattempted,
  Bookmarked, Mixed, and source-labelled PYQ topics.
- PYQs: 1,118 PrepLadder questions in 27 labelled topics (Biochemistry 346,
  Physiology 362, Anatomy 410). Marrow ED8 has no PYQ/exam/year metadata.
- Next: exact-head notes CI and preview; no bank import or production promotion.

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
- Multiple paused Practice chapters were reconciled into canonical at `cb3f44b`; Engineering `35850509766` and full Android/PWA/browser/APK/emulator run `35850509865` passed. The user confirmed the chooser/resume flow in the UI-branch preview; physical Android acceptance of this extension remains pending.

## Mandatory Practice regression sequence

Any change touching Home, Practice, session persistence, sync, question navigation, final review, FSRS injection or build transforms must exercise the generated learner path: start a genuine multi-question Practice session; answer several questions while leaving at least one unanswered; open the final review grid and Pause; confirm Home/paused lifecycle; use the rendered Home Continue Practice control; verify same session ID, complete ordered IDs, saved/current index and preserved progress; verify no `1 / 1` collapse and no Pause-as-Skip mutation.

## Structured explanation-table invariant

- Structured text tables are explanation-owned unless the source is explicitly an image/raster table.
- Non-empty source headers/rows must render as non-empty learner-visible headers/cells in correct order; `[object Object]` is a hard failure.
- Browser regressions must verify meaningful expected cell content, not container existence.
- User physically verified the structured-table repair at `c829599050173d24408b72e8dc564ba501a156b4`.

## Matching/list and structured-question presentation — build verified, user review pending

- The shared parser safely renders matching/list structures; source-fingerprinted
  presentation reforms cover the remaining known incomplete records and the
  axonal-transport row grid. Do not alter canonical answers or guess missing
  source content. The ion-question repair is user-preview verified; later
  residual reforms are build-verified with physical review pending.
- Full evidence: `.project-memory/MATCHING_TABLE_ARCHITECTURE_HANDOFF_2026-09-14.md`.

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
- Anatomy Ch7 Q11–Q21 was reconciled through PR #67 into canonical merge `7215d8f`. Exact-merge Engineering `35885212819`, inventory refresh `35885212779`, and full Android/PWA/browser/APK/emulator run `35885212827` passed; preview `https://0e14d788.nk-qbank.pages.dev` deployed, production skipped. The 11 explanations are **BUILD_VERIFIED / physical review pending**. Handoff: `.project-memory/AUTOMATION_HANDOFF_ANATOMY_EXPLANATION_CH07_Q011_Q021_2026-09-23.md`.
- The checked-in inventory currently reports **662 enhanced-reference / 2,049 pending / 2,711 total**. The previous 646/2,065 sentence lagged behind a later inventory refresh; raw source hashes are unchanged.
- Any next explanation automation must reacquire ownership from the live canonical state and start a new batch.
- Production promotion prohibited.

## Image lane

- PrepLadder source-visual browser/APK gates passed, but 422 source-comparison
  audit items remain pending manual review. Handoff:
  `.project-memory/PREPLADDER_VISUAL_VERIFICATION_2026-09-16.md`.
- Marrow images are automation-owned. Biochemistry Q11 remains
  `REVIEW_REQUIRED` due to corrupted embedded PDF text; inspect the rendered
  source before release. Physiology coverage remains incomplete.

## Study UI audit and first defect batch — 2026-09-23

- Baseline screenshots at 320px/390px phone, larger text, and 820px tablet found CBT grid numbering/crowding, clipped question context, squeezed Analysis header, and a 320px Home action under bottom navigation. Shared fixes are in `docs/STUDY_UI_AUDIT_2026-09-23.md`. The user accepted the preview and authorized canonical promotion. Integrated product checkpoint `b6dd246` passed Engineering `35967933879` and full browser/PWA/APK/Android `35967933880`, including two saved chapters → submit one → Home Continue and Review Solutions → Home Continue. Physical in-place APK/data-preservation checks remain pending.

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

1. Complete generated and physical review of the bank-aware module/PYQ candidate
   on its exact source head, including an old saved module, Marrow-only module,
   and PrepLadder PYQ set. It is code-only at this handoff.
2. Keep the accepted Practice/Review contract, Anatomy Ch7 Q11–Q21 rollout, and
   automation-owned image/explanation content intact. Production remains guarded.
3. Image automation remains independently owned from live canonical per
   `.project-memory/IMAGE_AUTOMATION_READY_2026-09-20.md`.
