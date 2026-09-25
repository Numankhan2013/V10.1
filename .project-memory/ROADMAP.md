# ROADMAP.md — Planned Work and Priorities

Source: `memory.md` refinement phases R1–R9 + V11.5 docs + current handoff.
Check off only when build-verified **and** device-verified where UI is involved.
`STATE.md` holds the immediate next step.

## Immediate (next 1–2 sessions)

- [ ] Bank-aware study modules and PYQ candidate: exact subject/bank/topic
      records and frozen legacy modules passed generated browser/PWA/APK/emulator
      verification at `7b7eef2`; the user accepted the topic picker. The current
      follow-up removes the redundant Questions-step Source control so selected
      regular and PYQ topics both contribute questions; full CI passed at
      `a94b329`. Finish physical review on
      `feature/qbank-bank-aware-modules-20260924`. PrepLadder
      has 1,118 source-labelled PYQs; Marrow ED8 lacks reliable PYQ/exam/year fields.
- [ ] Study intelligence: a first increment adds question-linked personal notes
      to answered Practice and Review, with durable local storage and account
      sync. User checked and accepted the note functionality at `e623fd1`.
      The read-only saved card and compact More → My notes index/search passed
      Engineering `36113707551` and full browser/PWA/APK/emulator
      `36113695753` at `34c5bcc`; the user checked and accepted its preview.
      Quick Revision now combines mistakes/bookmarks/unseen/due in More across
      all subjects and banks; generated-app and exact-head CI are pending.
      Next add evidence-backed question facets. Build on the same bank
      registry and Practice/Review engine; do not invent PYQ/difficulty/
      high-yield labels.
- [ ] Finish the 2026-09-23 study UI audit batch on one exact canonical SHA:
      inspect the generated phone/tablet/image screenshots and pass Engineering,
      full Android/PWA/browser/APK/package, and packaged Android emulator gates.
      Then perform the in-place canonical APK check on a physical Android device,
      including saved progress and force-close/reopen. Preview spot-checks and
      emulator runs do not close physical acceptance.
- [x] V11.5 physical-device test and acceptance. User reported Custom Study
      Modules work beautifully; accepted product commit `f13d12f`, build
      `34049637559`.
- [x] Fresh-agent reconstruction audit. It recovered architecture and release
      context, but exposed stale facts, self-staling HEAD, and missing non-AGENTS
      harness discovery. Fixed with thin adapters, schema, and an integrity check.
- [x] Physically test and accept V11.6 content quality (`125d68b`, run
      `34050921180`): comparison/table takeaways and metadata cleanup.
- [x] Consolidate accepted V11.6 with the harness-neutral memory lineage on
      `v11.7-cross-device-pwa-sync` without altering either checkpoint branch.
- [ ] Deliver V11.7: responsive PWA plus conflict-safe Firebase synchronization
      while preserving the accepted Android behavior and existing local data.
- [ ] Complete the bounded Home “Today’s Focus” command center on
      `feature/home-command-center-current`: preserve saved modules, Due Review,
      Continue Practice, Practice 20 and Timed CBT; visually recommend unfinished
      module first, then due review, then Practice 20. Run after the Custom Study
      Modules transform. Exact-head full browser/APK/PWA CI and generated 390 px
      visual QA pass at `3ec666c`; physical-device acceptance remains.
- [ ] Verify and reconcile the bounded Continue Practice resume candidate:
      Pause/Submit share the existing persisted session state; Pause resumes skipped
      + unseen questions without replaying answered questions; completed topics point
      to the next canonical topic. Exact-head Engineering/full browser/PWA/APK/package
      CI and generated 320/390/768 px visual QA pass at a717563; canonical
      reconciliation and physical-device acceptance remain.

## PrepLadder source-visual quality — separate from Marrow automation

- [ ] Run the exact Linux PDF/generated-app pipeline for the new non-destructive
      full-corpus inventory and crop-safety gate. Inspect high-risk-first
      source/production sheets in bounded batches; record manual PASS only after
      axes, labels, legends, borders, panels, ownership and answer safety pass.
- [ ] Run the representative phone/tablet browser gate, APK/package checks and
      Engineering Gate on one exact canonical SHA. Physical-device acceptance
      and production promotion remain explicit user actions.
- [ ] Marrow Biochemistry automations may proceed independently from the
      PrepLadder manual source-comparison queue. Start at
      `marrow__BIOCHEM_CH04_Q011:figure:1`; current coverage has 4
      tracked-unreleased, 34 untracked and 31 text-cue references.

## Marrow expansion

- [x] Consolidate the tested feature lineage into authoritative Git `main`
      through PRs #6/#7; run 409 passed and both Cloudflare steps were skipped.

- [x] Anatomy Marrow pilot: 62/4, source selector, native structured
      explanations, browser smoke test, side-by-side APK and feature preview;
      user physically confirmed the original Anatomy flow.
- [x] Generalize the Anatomy-only bank special case into the shared
      subject-indexed `BANKS_BY_SUBJECT` registry.
- [x] Integrate supplied Anatomy Phase A Chapters 1–48:
      **819 questions / 48 topics**, manifest/hash verified.
- [x] Integrate supplied Biochemistry Phase A Chapters 1–26:
      **543 / 26**, through the same shared registry.
- [x] Integrate supplied Physiology Chapters 1–33:
      **753 / 33**, through the same shared registry.
- [x] Final expanded bank contracts/browser/package gates:
      Engineering `34245190588`, full Android+PWA `34245190771`,
      browser total **2,115** Marrow questions.
- [x] Physical user spot-check of the expanded feature PWA: user confirmed the
      Marrow question integration succeeds and the recovered Topics/FSRS
      customization surfaces are good. This is not blanket acceptance of all
      content or production promotion.
- [x] Build/device verification of the implemented explicit Topics taxonomy from
      `data/marrow/topic_index_taxonomy.json`: the user physically verified the
      newly deployed PWA and declared the current Marrow integration/taxonomy
      verification phase complete. Approved journey UI is unchanged; four
      cross-system Anatomy placements remain internally reviewable.
- [ ] Explanation fine-tuning using
      `docs/MARROW_EXPLANATION_FINE_TUNING.md`. Raw source stays immutable and
      learner-facing improvements remain separate ID-keyed augmentation.
      Biochemistry Chapters **1–11** are complete on the current stacked lineage;
      Physiology Chapters **1–4** retain the approved 80-question pilot and
      Chapter **5 — Body Fluids (28/28)** is now complete and fully verified.
      Deterministic inventory: **429 enhanced / 1,686 pending**.
      Engineering Gate 259 and full Android/PWA run 539 verified the Physiology
      rollout loader, inventory, Q17 browser regression, APK/package contracts
      and preview deployment. When explanation work resumes, continue in source
      order from **Physiology Chapter 6 — Physiology of Nerve**.
- [ ] Image integration is an **automation-owned** workstream. Start from the live
      canonical head and the source-reference coverage ledger, not historical
      reviewed-registry counts. Biochemistry is next at
      `marrow__BIOCHEM_CH04_Q011:figure:1`; keep unresolved source corruption
      flagged and reconcile each verified bounded batch into canonical. See
      `.project-memory/IMAGE_AUTOMATION_READY_2026-09-20.md`.
- [ ] Continue later Marrow chapters beyond the supplied current scope only when
      verified source JSONL is available.
- [ ] Keep production promotion deliberate; build/browser success is not acceptance.

See `docs/MARROW_BANK_INTEGRATION.md` for the exact schema, integrity rules,
failure lessons, and required regression checklist.

## Completed smart-review milestone

- [x] FSRS v6 review scheduling is functional in the new Android APK and website/PWA.
      Keep the behavior documented in [docs/FSRS.md](../docs/FSRS.md) stable while
      the separate cross-device synchronization work continues.

## Synchronization follow-up

- [ ] Verify the sync hardening candidate on Android/PWA: explicit PWA update
      activation, preservation of edits during uploads, and late offline revision
      reconciliation. Android sync is user-confirmed successful; the historical
      HTTP 403 investigation is stopped. Owner-scoped rules and FSRS stay protected.

## R1 — Gold-standard Question Screen (highest priority per `memory.md`)

Refine typography rhythm, stem density, option spacing, selected/correct/wrong
states, bookmark/grid affordances, explanation hierarchy, source-visual
placement, long-explanation behavior, image/text relationship, sticky
Previous/Next, mobile readability, noise reduction. Preserve wording and source
renderers; use before/after screenshots; narrow scope per change.

## R2 — Home polish

Three-action + Review-Due hierarchy, streak geometry, spacing rhythm, section
alignment, subject rows, progress indicators, empty states, responsive +
reduced-motion behavior. Keep current Home architecture.

## R3 — Review consistency

Unify Practice/CBT/Test Review: header hierarchy, grid language, navigation,
state indicators, explanation surface; no duplicate implementations.

## R4 — Daily Study Loop

`Home → Continue/Practice → Review → Return Home` frictionless; Continue
Practice, unfinished recovery, Wrong/Due/Bookmarks, post-session next action.
No over-automation or Home clutter.

## R5 — Study Intelligence

Robust Wrong, persistent Bookmarks, restrained spaced-review foundation,
actionable weak-topic signals. Prioritization over gamification. V11.5 modules
are the reusable-set primitive — build on them, do not fork a second system.

## R6 — Insights / Analytics

Answer: weak at? study next? how much done? accuracy improving? time wasted?
Actionable summaries over decorative graphs; keep no-evidence vs poor
performance distinct.

## R7 — Test System refinement

Builder clarity, topic selection, counts, timing, history, results, unanswered
review, analysis — after Review stability.

## R8 — Engineering hardening

Golden/screenshot checks (Home, Topics, question, image-Q, long explanation,
Practice, CBT, Review, grid, Insights), state/data separation increments,
backup/restore + schema validation (after inspecting persistence), contract
coverage without calling static markers regression-proof.

## R9 — Final visual system

Spacing/typography tokens, icon consistency, border/radius discipline, shadow
discipline, transitions, accessibility, adaptive/tablet — only after behavior
is stable.

## Explicitly deferred

- Manual Anki export (`NK QBank::<Subject>::<Topic>`, stable IDs, and
  subject/topic/source tags); no AnkiConnect/AnkiDroid-only dependency.
- Private on-device monthly FSRS parameter optimization after at least 1,000
  rated reviews.
- Native Compose rewrite; second navigation/shell; global renderer rewrites.
- Heuristic Physiology explanation reconstruction.
- Re-cropping medically meaningful source content.
- Copying competitor medical content (reference links are workflow-only).

<!-- V11.7_DEPLOYMENT_HANDOFF_2026-09-07 -->
## V11.7 deployment handoff — 2026-09-07

- Active candidate: `v11.7-cross-device-pwa-sync`. Physically accepted rollback baseline remains **V11.6 Content Quality** at `125d68b`; do not call V11.7 accepted until Android migration and Android↔iPad sync pass on real devices.
- Firebase/Firestore is configured and builds now report `QBANK_RUNTIME_CONFIG_OK firebase=configured`. Exact GitHub Variables: `QBANK_FIREBASE_API_KEY`, `QBANK_FIREBASE_PROJECT_ID`, `QBANK_ANATOMY_PDF_URL`. Firestore user-scoped rules and the intentionally empty composite-index set are deployed.
- Cloudflare Pages project: `nk-qbank`. Exact GitHub Secrets: `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`. Push builds create preview deployments. Manual **Build V11.7 Android + PWA** dispatch now also promotes the same artifact to production so `nk-qbank.pages.dev` is updated deliberately.
- Anatomy source PDF uses the configured public R2 object URL because it is ~46 MiB; Biochemistry and Physiology PDFs ship inside `build/web`.
- Physical iPad testing found and fixed two browser runtime bugs: `278b6c5` fixed the blank-screen sync bootstrap (`nkAuth` initialization timing); `7b047e5` fixed PDF.js canvas creation by avoiding a local `document` name that shadowed the DOM document.
- Latest hashed preview opens successfully on iPad. Before the production-promotion workflow change, the root `nk-qbank.pages.dev` still served the older blank production deployment. Source-PDF rendering, Anatomy/R2 CORS, final production URL, Android in-place upgrade, and full two-way sync still require physical verification.
- Next: wait for CI on the current branch → manually dispatch **Build V11.7 Android + PWA** once → verify `https://nk-qbank.pages.dev` → add final Pages hostname to Firebase Authentication authorized domains → ensure R2 CORS allows the exact Pages origin and Range GETs → install V11.7 APK over V11.6 without uninstalling → verify old local data → same-account Android/iPad sync, offline/reconnect, force-close/reopen, sign-out/in tests.

## 2026-09-08 — User rejection and corrective handoff

Priority 0: reproduce and restore user-reported unreadable PDF explanations. Then implement faithful curved journey/glow/card proportions, an actually fixed Continue Learning tray, and a dedicated FSRS page. Preserve search, bank/subject origin and source fidelity. Detailed handoff: docs/REJECTED_TOPICS_FSRS_HANDOFF.md.


### Biochemistry image coverage recovery — Q21 R2
- Q21 source composite released on the current bounded batch; Biochemistry remains incomplete at 71/110 raw references resolved, with 31 text-cue review items.
- Continue strictly from `marrow__BIOCHEM_CH02_Q026:figure:1 (explanation, source pages [41], UNTRACKED_SOURCE_VISUAL)` after this batch is exact-head verified and reconciled into canonical.


### Biochemistry image coverage recovery — Q26
- Q26 native page-41 explanation figure released on the bounded specialist batch; Biochemistry remains incomplete at 72/110 raw references resolved, with 31 text-cue review items.
- Continue strictly from `marrow__BIOCHEM_CH04_Q011:figure:1 (explanation, source pages [69], UNRELEASED_TRACKED)` after this batch is exact-head verified and reconciled into canonical.
