# DECISIONS.md — Durable Technical / Product Decisions

Record the decision + why. Date/branch/commit where useful.

## 1. Keep the WebView monolith; no rewrite, no second shell (standing)

Rejected the V11 clean-foundation shell (duplicate nav, excess chrome,
replacement shell, lost question-first hierarchy). No wholesale native Compose
rewrite. Evolve component-by-component only. Basis: `memory.md` §3, Run 170
lesson (transformation restored old Home; fixed by restoring exact accepted
composition).

## 2. Candidate states are distinct (standing)

Implemented ≠ build-verified ≠ device-verified ≠ accepted baseline.
Only explicit user physical-device approval promotes a baseline. CI + static
checks are never sufficient. Basis: `docs/ENGINEERING_BASELINE.md`, Run 220
(`73c0428`, run `34011265432`).

## 3. Source visuals are frozen infrastructure (standing)

Native raster figures at native resolution, tight crops, lossless PNG display
cache (~420: Anatomy 297 / Physiology 62 / Biochemistry 51); original PDFs stay
authoritative; exact normalized stem matching; subject-specific PDFs only; no
fuzzy cross-subject assignment; no `Question N has image` heuristics; aspect
preserved; fullscreen zoom/pan protected. Do not alter during unrelated UI work.

## 4. Subject renderer isolation (standing)

Biochemistry known-good renderer stays isolated (no global replacement).
Physiology uses source-PDF tables/diagrams/graphs; never heuristically rebuild
flattened explanations into fake tables/bullets. Anatomy changes must come from
source inspection, not heuristics.

## 5. Session / Review protection (standing)

Final question → session-review navigator (answered/unanswered + jumping +
Submit/Finish); no persistent end-of-session toast; singleton transient toasts.
Review Solutions keeps one live engine: Previous/Next fixed footer (isolated
styling), grid/navigator, jump, End Review → originating analysis, source-PDF
explanations. Generic CSS must not clip the footer; no second navigator.

## 6. Home composition and streak ownership (V11 accepted)

One cohesive Home surface (not card stacks); Today’s Focus as command area;
Home-only streak below greeting (rectangular/chiseled, Home-axis aligned,
subtle motion OK); legacy global streak injector removed
(`v102-streak-layer*` must stay absent). Canonical `currentStreak()`/state
functions reused; no duplicate persistence. Header logo removal is Home-only.

## 7. Today’s Focus: permanent Practice-20 + conditional Review-Due (2026-09-06,
   `v11.4`, `9e6abc7`)

Kept `startAllSubjectPractice()` always visible (user direction) **and**
restored `${due? startLibrary('review') : ''}` (`Review N Due`) when due>0.
Rationale: prior toggle hid Practice-20 when due>0; the “always Practice”
follow-up hid the Review action the focus title promised and broke
`test_whole_app_vision_v1.py` (runs `34034905290`/`34034904068`/`34034791899`).
Fix preserves both markers, keeps 3-button layout when no due, switches to a
4-column `:has(>button:nth-child(4))` grid only when the 4th button exists;
older WebViews degrade to wrapped layout without breakage. Verified by run
`34043059869` (`WHOLE_APP_VISION_OK`) and user device confirmation.

## 8. Deterministic pipeline + syntax last (standing)

One owner script per transform; `verify_build_pipeline.py` enforces order and
single ownership; `fix_boot_syntax.py` + `node --check` run after **all**
transforms and again on packaged `assets/index.html`; packaged APK greps +
`verify_product_contract --stage packaged` + `verify_cbt_invariants` gate
release. Lesson from WebView syntax failures (transforms after the check) and
review-footer clipping.

## 9. Accurate progress semantics (V11.2, standing)

Subject stats use `SUBJECTS.flatMap` over all records; attempt history is
`state.attempts` (`qAttempts`), not `state.answers`; Topics completion is
attempted/total (all-wrong still counts as attempted); counts use numeric-safe
formatting (no `NaN Questions/Topics`); `BY_ID` unified across subjects.
Covered by `test_study_metrics.py`, `test_whole_app_vision_v1.py`.

## 10. Custom Study Modules reuse the Practice engine (V11.5, `f13d12f`)

Modules persist in `qbank_state_v1.studyModules` (filters, frozen IDs, answers,
timing, position, lifecycle, optional result ID); IDs frozen at creation and
never rebuilt by status changes; seeded shuffle (Mixed weighted
Wrong-heavy); cap at eligible count; dedupe by canonical ID; missing IDs
skipped. Sessions are normal Practice with `studyModuleId`; every save syncs
back; finish creates normal Practice Analysis; leave saves and returns Home;
restart clears progress but preserves frozen set + global history. Owned by
`apply_custom_study_modules_v1.py` before syntax validation; tested by
`test_custom_study_modules_v1.py`. See `docs/CUSTOM_STUDY_MODULES.md`.

## 11. Harness-agnostic memory (2026-09-06, this change)

`AGENTS.md` is the universal entry; `.project-memory/` holds operational truth
(`STATE` current, `ROADMAP` future, `DECISIONS` durable, `ARCHITECTURE` +
`PRODUCT` implementation/product, `SESSION_LOG` history). Harness files are
thin pointers only; no duplicated knowledge. Repo is source of truth; fix
memory on drift. `memory.md` + `docs/` preserved as background, not forked.

## 12. Memory discovery needs thin adapters and executable checks (2026-09-07)

No filename is automatically loaded by every possible coding harness.
Keep root `AGENTS.md` canonical, add only tiny pointers for common conventions
(Claude, Gemini, Cursor, Copilot), and reject duplicated project knowledge in
those adapters. `verify_project_memory.py` protects placement and low-drift
rules in CI. Exact live HEAD must be resolved from Git rather than committed to
`STATE.md`, because the commit containing an updated hash changes that hash.

## 13. Takeaways preserve semantic ownership (V11.6, `125d68b`)

Flattened source tables may place unrelated columns in one text stream. A key
takeaway must select the relevant column/fact, preserve comparison ownership,
and fall back to the correct answer when extraction is ambiguous. Source footer
metadata is sanitized centrally before questions reach Practice, CBT, modules,
or Review. The separate V11.6 candidate audited 719 questions and identified
78 affected stems; build `34050921180` passed, pending device acceptance.

## 12. Cross-device evolution keeps one product core (2026-09-07, V11.7)

Android and PWA consume the same deterministically generated HTML/data instead
of forking a simplified web rewrite. Question/source content stays static; only
private learner state is synchronized. Firestore uses normalized entity
collections and per-device revision envelopes: immutable records union, mutable
records use timestamp/device tie-breaking and tombstones, and same-generation
module completion merges. Android moves from `file://` to an intercepted private
HTTPS asset origin with a one-time migration bridge, avoiding both data loss and
unsafe universal file access. Cloudflare Pages hosts the PWA; the oversized
Anatomy PDF uses configurable R2 while PDF.js preserves browser source rendering.

<!-- V11.7_DEPLOYMENT_HANDOFF_2026-09-07 -->
## V11.7 deployment handoff — 2026-09-07

- Active candidate: `v11.7-cross-device-pwa-sync`. Physically accepted rollback baseline remains **V11.6 Content Quality** at `125d68b`; do not call V11.7 accepted until Android migration and Android↔iPad sync pass on real devices.
- Firebase/Firestore is configured and builds now report `QBANK_RUNTIME_CONFIG_OK firebase=configured`. Exact GitHub Variables: `QBANK_FIREBASE_API_KEY`, `QBANK_FIREBASE_PROJECT_ID`, `QBANK_ANATOMY_PDF_URL`. Firestore user-scoped rules and the intentionally empty composite-index set are deployed.
- Cloudflare Pages project: `nk-qbank`. Exact GitHub Secrets: `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`. Push builds create preview deployments. Manual **Build V11.7 Android + PWA** dispatch now also promotes the same artifact to production so `nk-qbank.pages.dev` is updated deliberately.
- Anatomy source PDF uses the configured public R2 object URL because it is ~46 MiB; Biochemistry and Physiology PDFs ship inside `build/web`.
- Physical iPad testing found and fixed two browser runtime bugs: `278b6c5` fixed the blank-screen sync bootstrap (`nkAuth` initialization timing); `7b047e5` fixed PDF.js canvas creation by avoiding a local `document` name that shadowed the DOM document.
- Latest hashed preview opens successfully on iPad. Before the production-promotion workflow change, the root `nk-qbank.pages.dev` still served the older blank production deployment. Source-PDF rendering, Anatomy/R2 CORS, final production URL, Android in-place upgrade, and full two-way sync still require physical verification.
- Next: wait for CI on the current branch → manually dispatch **Build V11.7 Android + PWA** once → verify `https://nk-qbank.pages.dev` → add final Pages hostname to Firebase Authentication authorized domains → ensure R2 CORS allows the exact Pages origin and Range GETs → install V11.7 APK over V11.6 without uninstalling → verify old local data → same-account Android/iPad sync, offline/reconnect, force-close/reopen, sign-out/in tests.



## 14. FSRS v6 schedules are derived from immutable attempts (2026-09-07)

Use pinned, offline `ts-fsrs` 5.4.2 (MIT), which implements FSRS v6, rather
than maintaining a custom interval ladder. Attempts are the synchronization and
replay truth; reviews are schema-v2 derived card caches. Disable fuzz for
Android/PWA determinism, preserve legacy due dates until each card's first new
rating, and apply preference changes only to future ratings. Default retention is
90%, maximum interval 365 days, and incorrect recall uses one 10-minute step.
Anki export and on-device parameter optimization remain separate future work.


## 15. Question-bank source is a data dimension, not a second product engine (2026-09-08)

Marrow and PrepLadder must share the existing subject/topic/session/review
architecture. A subject may expose multiple bank/source records, selected before
Topics. Bank-specific content/rendering may differ, but Practice, CBT, Review,
Custom Study Modules, FSRS, persistence, sync, bookmarks, wrong/due queues,
analytics, and navigation must not fork.

Marrow uses stable namespaced IDs and native structured explanations. PrepLadder
retains its existing source-PDF renderer. Marrow wording is source-owned:
readability work may change typography, semantic bolding, spacing, lists and
tables, but must not paraphrase or silently rewrite the explanation text.

The Anatomy pilot's single `MARROW_RECORD` is explicitly temporary. Scaling to
Physiology/Biochemistry requires a subject-indexed/general bank registry, not
copy-pasted special cases. Large imported bundles use deterministic sharding +
hash manifests, and every new bank expansion stays preview-only until browser
gates and user physical verification pass.

Rationale and executable procedure: `docs/MARROW_BANK_INTEGRATION.md`.


## 16. Topics use journey-state UI plus explicit major-section taxonomy (2026-09-08)

The accepted Topics-page direction is a mobile syllabus journey: numbered
left-side milestones connected by a soft path, with aligned topic cards. State is
communicated deliberately and minimally. Completed topics use a green-tinted
milestone plus right-side green check; paused/in-progress topics use a blue-tinted
milestone plus right-side blue pause; unattempted topics use a subtle
purple/lavender milestone treatment **and no right-side hollow-circle/placeholder
icon**.

The useful controls are All / In Progress / Completed / Not Started, search,
index/list access, and a bottom Continue Learning resume tray. Free/locked/star
commerce metadata is excluded from this professional QBank surface.

Topics are not a permanently flat list. The UI/data presentation must support a
major-section parent above child topics (Anatomy examples: General Embryology,
Histology). Because the present dataset does not expose a complete authoritative
parent mapping, classification may be derived from existing topic labels and
inspection of representative question/source content. The result must live in
one centralized, reviewable mapping; it must not rewrite source question content
or create duplicate question engines. Ambiguous assignments should remain
explicitly reviewable rather than being silently guessed.

Rationale: the user wants the topic list to communicate syllabus structure and
study progression at a glance while preserving the current QBank architecture
and avoiding decorative or paywall noise.

## 2026-09-08 — User rejection and corrective handoff

Do not equate passing CI or screenshot capture with reference fidelity or physical acceptance. The user rejected 6ba7ebe. Require visual comparison and initial-viewport dock checks, a dedicated settings destination, and same-question PDF legibility checks before claiming completion.


## 17. Marrow expansion is content-first and enhancement is layered (2026-09-08)

Decision: when verified Marrow JSON/JSONL is supplied, integrate the complete
source-faithful content into the shared bank registry first. Do not block data
existence on explanation redesign, figure binaries, or generated distractor work.

The stored source transcription is the authoritative layer. Presentation and
generated augmentation stay separate and auditable. The already approved
62-question Anatomy + 80-question Physiology enhancement may remain active as a
subset while newly ingested questions use the native structured source renderer.

Why:
- the user explicitly asked to make the questions exist and work first, then
  improve explanations later;
- keeping ingestion and enhancement separate prevents a broad presentation pass
  from silently changing medical source content;
- one shared registry preserves Practice/CBT/Review/FSRS/sync/modules/analytics
  behavior and avoids a subject-specific fork.

Durable implementation rules:
- manifests + compressed/raw SHA-256 + count/shape/linkage checks fail closed;
- globally namespaced IDs are mandatory;
- accepted pilot IDs must remain subsets of expanded records;
- transport/staging mechanisms are not runtime dependencies;
- browser tests must evolve with intentional bank-matrix changes.

Lesson from run 402: the product correctly added a Marrow Biochemistry bank, but
the browser regression still asserted “Biochemistry is PrepLadder-only.” A
regression test can become stale when a deliberate requirement changes; update
the assertion to the new public contract rather than treating the intended new
bank as a product failure.

Lesson from navigation wiring: the pilot-era topic-section shortcut grouped every
non-Physiology Marrow topic under General Embryology. Full cross-subject data
requires subject-aware taxonomy; presentation classification must not rewrite
question content.


## 18. Topic indexes are an explicit source taxonomy, not a runtime heuristic (2026-09-08)

The user physically approved the recovered journey UI but rejected the
medical/source accuracy of the major-section grouping. Therefore the next Topics
change must preserve the existing journey/glow/fixed-tray design and replace
grouping with one centralized, explicit, reviewable subject+topic mapping.

Required category order and current chapter guidance are canonicalized in
`docs/MARROW_TOPIC_INDEX_TAXONOMY.md`. Ambiguous cross-system topics are review
items; do not silently guess. PYQ topics stay at the end of their parent index.

## 19. Recovered Topics/FSRS live on the Marrow feature line until deliberate consolidation (2026-09-08)

The user confirmed the good Topics and FSRS customization implementations on the
Marrow feature PWA. Their absence from the older production/main PWA is explained
by branch/deployment separation: Git `main` is stale, the full recovery lives on
`feature/marrow-bank-pilot`, and run 405 skipped production promotion.

Future consolidation must carry forward the exact working feature implementation
rather than recreating it. Detailed handoff:
`docs/TOPICS_FSRS_FEATURE_HANDOFF.md`.

## 20. Explanation fine-tuning is a separate immutable-source augmentation phase (2026-09-08)

Question ingestion success does not mean learner-facing explanation quality is
finished. Raw ED8 transcription remains immutable; OCR cleanup, Key Takeaway,
selective emphasis, structured display and distractor rationales live in a
separate auditable layer. Use the approved 142-question grammar as reference and
follow `docs/MARROW_EXPLANATION_FINE_TUNING.md`.

## 21. Consolidate before further Marrow expansion (2026-09-08)

Use the tested Marrow feature line as the foundation for a restored authoritative
`main`, then continue question ingestion through the same subject-indexed bank
registry. Waiting for every future chapter would extend branch drift without
reducing architectural risk. Audit and preserve stale-main history, but resolve
conflicts in favor of the tested V11 feature implementation.

The first unified production candidate includes the explicit Topics taxonomy.
Production promotion is a separate release action requiring `main`, an explicit
boolean request, and an exact full commit SHA. V11.6 `125d68b` remains the
accepted rollback baseline until a later candidate is physically accepted.
