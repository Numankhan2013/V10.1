# ROADMAP.md — Planned Work and Priorities

Source: `memory.md` refinement phases R1–R9 + V11.5 docs + current handoff.
Check off only when build-verified **and** device-verified where UI is involved.
`STATE.md` holds the immediate next step.

## Immediate (next 1–2 sessions)

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

## Marrow expansion — next session priority

- [x] Anatomy Marrow pilot: 62 questions / 4 topics, source selector, native
      structured explanations, browser smoke test, side-by-side APK, and
      Cloudflare feature preview. Final runs: Engineering Gate
      `34159542431`, full Android+PWA `34159542436`. User physically checked
      the preview and reported it works beautifully.
- [x] Generalize the temporary Anatomy-only `MARROW_RECORD` into the shared
      subject-indexed `BANKS_BY_SUBJECT` registry while keeping Anatomy behavior
      unchanged. Registry refactor passed Engineering Gate `34190814897` and
      full browser/APK/PWA run `34190814843`.
- [ ] Import remaining Marrow Anatomy chapters in bounded, manifest-verified
      batches using stable `marrow__...` IDs.
- [ ] Marrow Physiology through the shared registry: first bounded pilot is
      implemented and build/browser verified (Chapters 1–4, 80 questions /
      4 topics; Gate `34191865093`, full run `34191865094`). Await user
      preview/device spot-check before marking this UI milestone complete; then
      expand remaining verified Physiology chapters in bounded batches.
- [ ] Import Marrow Biochemistry through the same bank registry and extend the
      browser smoke test to `Biochemistry → PrepLadder | Marrow`.
- [x] Marrow Anatomy explanation architecture: user-approved typography,
      selective exam-discriminator emphasis, preserved source tables, 186
      concise wrong-option rationales across all 62 current questions, and a
      very light display-only redundancy trim while stored source wording stays
      unchanged. Full browser/APK/PWA run `34163197772` passed.
- [ ] Images/figures remain a later pass. Preserve figure metadata during text
      imports; do not block question-bank expansion on missing binaries.
- [ ] Keep all expansion builds on feature previews until regression gates pass
      and the user physically verifies them; production promotion is deliberate.

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

