# STATE.md — Current Project State and Handoff

> Resolve live branch, commit, and CI from Git before acting. Historical detail is in `SESSION_LOG.md` and dedicated handoffs.

## Baseline and active work

- Repo: `Numankhan2013/V10.1`. Accepted product commit: `125d68b` (V11.6 accepted baseline and rollback point). Production/`main` remains guarded.
- Sole Marrow/product integration trunk: `feature/marrow-canonical-full-current`. Its last recorded verified canonical checkpoint was `356cce4`; Engineering `35453226391` and full Android/PWA/browser/APK `35453226292` passed. Recheck the live head before any integration.
- Active isolated study branch: `feature/qbank-bank-aware-modules-20260924`. Do not promote it or production without explicit user approval.
- Current complete Marrow ED8 corpus: Anatomy 1,115 questions/63 topics; Biochemistry 582/28; Physiology 1,014/43; total **2,711/134**. Source data stays immutable. See `FULL_CORPUS_CONSOLIDATION.md` and `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md`.
- PrepLadder source-labelled PYQs: 1,118 in 27 topics (Anatomy 410, Physiology 362, Biochemistry 346). Marrow ED8 lacks trustworthy PYQ/exam/year metadata; never infer it.

## Current study experience and verification

- Bank-aware Custom Modules, PYQ topic selection, restored Home focus, full-page topic picker, saved read-only notes with More → My notes, Quick Revision, and cross-bank Insights are implemented on the isolated branch. The user physically reviewed their feature previews and accepted the working flows; the Quick Revision topic-filter visibility was deferred, and the Insights addition was judged adequate but not compelling.
- Full-page Tests → bank → topics → question count builder uses exact subject/bank/topic IDs and the shared exam engine. Product `5d585de` passed Engineering `36213112458` and full browser/PWA/APK/Android emulator `36158438170`; preview `https://2752f581.nk-qbank.pages.dev`. The user checked it and said it works. The dedicated strict per-question chapter test remains.
- Completed timed CBT results show source-exact subject/bank/topic analysis and targeted missed-ID follow-up Practice; repeated-Submit taps are guarded. Product `b65ad21` passed Engineering `36216951965` and full browser/PWA/APK/Android emulator `36216944458`; preview `https://c22cbdd0.nk-qbank.pages.dev`. The user checked it and said it works.
- Current candidate: Insights QBank tracker for all six subject/bank combinations, showing answered-once coverage and latest misses by source topic. Bank selection, search, progress filters, and topic entry reuse the existing bank registry/routes; old active-bank chapter list is replaced. Product `220f954` passed Engineering `36218442172` and full generated browser/PWA/APK/Android phone+tablet emulator `36218442273`; full-page phone/tablet Insights captures were inspected and preview `https://697c1da1.nk-qbank.pages.dev` returned HTTP 200. User review pending.
- Exam practice: product `13c3cd3` passed Engineering `36229006243` and full generated browser/PWA/APK/Android phone+tablet emulator `36229004244`; preview `https://e544d753.nk-qbank.pages.dev`. The browser journey verified 27 PrepLadder PYQ topics/1,118 questions, 10/410 Anatomy, 9/362 Physiology, 8/346 Biochemistry; mixed CBT, saved history, Review Solutions, topic breakdown, follow-up Practice, and both-bank timer expiry. The user checked the preview and said it works but found the PYQ action bulky and one-way. A compact toolbar toggle beside Select all/Clear all is now in source: on selects verified PYQ topics; off removes them while retaining manually added regular topics. Local checks pass; full generated browser/PWA/APK/emulator verification and a replacement preview are pending.
- UI previews, CI/emulator checks, and user preview acceptance do **not** establish an in-place physical APK upgrade or production acceptance.

## Product architecture to preserve

- Shared bank registry: `MARROW_RECORDS → MARROW_BY_SUBJECT → BANKS_BY_SUBJECT`. Reuse Practice, CBT, Review Solutions, FSRS, sync, modules, analytics, and navigation across banks; do not fork by subject.
- Primary navigation: **Home · FSRS · Tests · Insights · More**. Subject journey: My Subjects → bank chooser → Topics → topic → Practice/Topic Test.
- FSRS schedules answered questions. Pause commits answered work only; final submission marks remaining session IDs skipped. Globally unseen questions stay unseen.
- Raw Marrow and PrepLadder source, stable question IDs, answer keys, source visuals, and PDF mappings remain protected.

## Accepted Practice / Continue Practice contract — device-verified

- Normal Practice footer is Previous + Next. Header grid and the end boundary open the same final review grid; its actions are Pause + Submit only.
- Pause preserves the same active session and full original ordered `sessionQuestionIds`, index, answers, timing, and progress. An unanswered current question is not skipped by Pause.
- Home Continue Practice resumes that session and position; a damaged older `questionIds` array is rebuilt from `sessionQuestionIds`, so a multi-question session never collapses to `1 / 1`.
- CBT, Review, Wrong/Bookmarks, FSRS, and Modules remain outside the normal Practice override. See `PRACTICE_FLOW_POSTMORTEM_2026-09-12.md` and `CONTINUE_PRACTICE_HANDOFF.md`.
- Changes touching Home, Practice, persistence, sync, question navigation, review, FSRS, or transforms require the generated multi-question Pause → Home Continue → complete-list/progress regression path.

## Content and presentation limits

- Structured explanation tables must retain nonempty source cells in order, never `[object Object]`; user physically verified the repair. Matching/list reform and scientific notation are build-verified but later residual presentation still needs source-backed physical review. See `MATCHING_TABLE_ARCHITECTURE_HANDOFF_2026-09-14.md`.
- OCR cleanup must use rendered authoritative source and stable-ID/fingerprinted overrides. Seven ambiguous question records and 56 explanation records retain `■` loss; do not guess missing content.
- Four PrepLadder records remain intentionally non-answerable: `anatomy-22-4`, `physiology-23-38`, `physiology-24-6`, `physiology-33-33`.
- Explanation inventory last recorded **662 enhanced-reference / 2,049 pending / 2,711 total**. Anatomy Ch7 Q11–Q21 is build-verified with physical review pending. Next batch must reacquire ownership from live canonical state; see `AUTOMATION_HANDOFF_ANATOMY_EXPLANATION_CH07_Q011_Q021_2026-09-23.md`.
- PrepLadder visuals have 422 manual source-comparison items pending. Marrow Physiology image coverage is incomplete; Biochemistry Q11 remains `REVIEW_REQUIRED` due to source corruption. See `PREPLADDER_VISUAL_VERIFICATION_2026-09-16.md` and `IMAGE_AUTOMATION_READY_2026-09-20.md`.

## Known problems and next step

- Canonical physical in-place APK/data-preservation check remains pending. Production promotion requires explicit authorization.
- Finish the compact PYQ-toggle full build and share its replacement preview. Then prioritize source-backed explanations in the current three subjects through a bounded batch. Tracker UI polish and new subject integration remain later work. Do not promote production or claim physical device acceptance from CI.
