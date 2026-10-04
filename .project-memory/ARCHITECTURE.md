# ARCHITECTURE.md — Current Implementation

## Production shape (do not replace)

`tools/marrow_images.py` is the Marrow image inventory, extraction, validation and
release owner. `data/marrow/images/registry.json` keeps immutable originals,
production hashes, source coordinates, asset QA and question bindings. Reused
assets require independent binding QA with their own source page/xref/region;
rejected or pending bindings never enter runtime metadata. `tools/install_marrow_images.py`
runs after Marrow content generation, installs explicit ID-based question/explanation
hooks and exposes the existing fullscreen zoom/pan viewer. PWA builds precache only
released content-hash image URLs. `tools/marrow_image_progress.py` produces the
checked deterministic rollout ledger.

`tools/marrow_image_coverage.py` keeps the immutable source audit denominator
and exact source-reference adjudications. Metadata-free cues use
`data/marrow/images/source_text_cue_reviews.json`: stable cue/question IDs,
exact provenance-page union, pinned PDF file/hash, and source evidence.
Confirmed source omissions remain explicit `NO_SOURCE_VISUAL` decisions.
True visuals declare role/page references; these add source-derived denominator
rows and clear a cue only when every linked binding is released. Source-reviewed
continuation pages must be listed explicitly in `reviewedVisualPages`. Orphan
reviews, changed source/provenance, unlisted pages and unreleased bindings fail
closed. Raw question bundles and audit metadata remain unchanged.

- Android wrapper (`app/src/main/java/com/qbank/biochemistry/MainActivity.java`,
  `AndroidManifest.xml`) + **WebView** + monolithic
  `app/src/main/assets/index.html` (~6 MB on V11 branches; 1.9 MB on stale
  `main` because single-subject + pre-generation).
- Offline-first: bundled data + PDFs + PNG cache + `localStorage` persistence;
  native code only where genuinely useful.
- Long-term direction is incremental isolation (persistence, rendering, review,
  analytics, tokens), never a big-bang rewrite.

## Imported UWorld owners and scoped continuation — 2026-10-04

- `uworld_imported_collection.py` supplies source-pinned reusable ownership for
  the two reproductive JSONL collections. Explicit registry owners pin original
  imports, normalized rows/full page OCR and complete reviewed overlays. A
  hash-pinned optional repair ledger records source-proven normalization fixes
  without mutating original imports. Existing typed presenters/media generators
  and shared study engines install them; arbitrary prepared folders are inert.
- `nkTopicPracticeContinuation(subject,bank)` resolves ordinary Practice live
  sessions/checkpoints only within the exact bank, returns saved question index,
  total and answered count, and delegates to the existing durable resume path.
  Home focus derives progress from that same saved context. Special modes,
  multi-session choice and conflict protection remain with their original owners.

## Runtime data and assets

- `uworld_collections.py` explicitly registers Biochemistry, Poisoning &
  Environmental Exposure, Ophthalmology, Male Reproductive System and Female
  Reproductive System & Breast, each with its own `UWorld · collection` namespace
  in the shared bank registry and lookup, without adding a traditional subject.
  Home/Library → My UWorld → collection → source blocks uses existing routes
  and study engines. Read-only aliases resolve legacy Biochemistry/UWorld bank
  and module scope keys without rewriting persisted records.
- `uworld_reviewed_document.py` validates per-row/PDF hashes, complete source
  page review, unchanged option labels/key, ordered paragraph/table/figure nodes,
  explicit image roles and source percentages. Collection parameters preserve
  each PDF's hash/display geometry and asset identity. Reviewed JSON batches are
  display overlays; immutable JSONLs and `uworldSource` remain untouched.
  `build_uworld_reviewed_figures.py` runs in CI after fetching the pinned LFS PDF,
  renders lossless focused crops and writes a byte inventory. Recursive PWA
  asset copying/precache and `verify_uworld_media_package.py` protect web/offline
  and APK bytes, with a combined source/asset inventory. Source PDFs are not bundled
  in the UWorld UI. Poisoning's linked pair keeps full context in each item and
  original metadata; shared free navigation and feedback remain. A–I choices
  cover the genuine nine-option source item. No other collection is auto-imported.
  Ophthalmology supplies a PDF-extracted immutable JSONL with per-page OCR audit
  text and complete ownership, then uses the same reviewed-document/media pipeline.
  Full searchable stems remain intact while display documents can interleave
  source exhibits and the final prompt without duplication.
  Collection blocks bypass the legacy subject taxonomy and use source block names.
  Search keeps references readable without starting scored sessions; it filters
  source-blocked UWorld items before batch sampling. Bank choices follow the
  selected search area, preserving a compatible choice and native control focus.
- UWorld wraps the shared question presenter, option renderer and explanation
  surface. Source-reviewed question/option images are essential media; load
  failures disable unsupported answer commits and expose Retry. Paragraphs,
  native tables, labelled choice discussions and educational objective preserve
  source order. Option percentages are inserted in the shared option renderer
  using its locked Practice/Review state, so in-place outcome feedback reveals
  them immediately while CBT stays concealed. Images reuse the shared zoom viewer.
- `nkFsrsPracticeMistake` replays active attempts independently of the existing
  FSRS mistake classification. Ordinary failures open a Practice mistake;
  correct answers from any flow resolve it; FSRS-only failures do not open it.
  Undo filtering, scheduler replay and persisted attempts are unchanged.

- Final source-completeness recovery is pinned in
  `data/question_completeness_reviews_v1.json`. Its compiler validates source
  fingerprints and generates 114 bounded display contracts for the shared
  question presentation/interaction layer: 81 source repairs and 33 scored
  answer gates for demonstrated source omissions. Native question images use
  the existing hashed Marrow registry and role/owner pipeline. Raw imports and
  PDFs remain immutable; optional archival region sheets are dispatch-only.
- Account reset/switching is owned by `tools/cross_device_sync_core.js`:
  reset generation fences remote progress before sweeping payloads with
  tombstones; per-UID local snapshots and a switch journal isolate accounts
  and recover interrupted writes. New accounts pull before sending empty
  active-session/preferences state. Sign-in UI is owned by the existing
  cross-device PWA transformer.
- `tools/apply_practice_correction_v1.py` installs
  `practice_correction_core.js`: exact missed IDs start a fresh Practice pass,
  save a separate linked result, and preserve the parent through the existing
  checkpoint/sync model. Original results are immutable.
- Timed-test recovery occupies Home Today's Focus through the existing
  timed-resume core. The Home command-center owner composes `nkHomeStreakMarkup` from existing
  `currentStreak`/`studyDayKeys`, connects only adjacent studied days in the
  current local calendar week, and applies CSS-only milestone flame motion.
  The violet linked rail flows continuously; today’s completed marker has
  an animated liquid frontier that reaches toward the next neutral dot
  without changing its studied state. Reduced motion disables trail/frontier,
  fire flicker, aura and sparks. No new persistence or animation timers.
  Home period counts use unique answered IDs, answer
  accuracy, and study time; result score/accuracy expose their denominators.
  Result actions retain repeated-tap guards without the 900 ms delay.
- All-bank question finder: `tools/apply_question_search_v1.py` installs
  `question_search_core.js` after the coverage and revision transforms. More →
  Find a question searches existing bank records and starts the shared Practice
  engine with exact IDs; it protects an active timed test. No new persisted
  question or progress model is introduced.

- `app/src/main/assets/subjects_qbank_data.js`, `qbank_data.js`,
  `pako_inflate.min.js`, `physiology_image_pages.js`
- `data/subjects_qbank_lzma.b64.part*` — source subject data parts.
- Derived at build time: `biochemistry_source_solution_map.js`,
  `subject_source_solution_maps.js`, `source_visual_metadata.js`,
  `source_visual_renderer.js`, `source_visuals/*.png` (~420).
- Bundled PDFs: `Biochemistry_QBank_Source.pdf`,
  `Physiology_QBank_Source.pdf` (`Physiology_QBank_Source.pdf` is runtime name
  for `Physiology Prepladder Version X Qbank yw.pdf`),
  `Anatomy_QBank_Source.pdf`.
- Legacy Home polish shims retained as assets: `home_polish_v1/2/3.js`
  (legacy streak layer itself is removed from the packaged app).

## Client model (key globals in `index.html`)

- `SUBJECTS`, `SUBJECT_BY_NAME`, `DATA`/`BASE_DATA`, `QUESTIONS`, `CHAPTERS`,
  `CHAPTER_BY_ID`, `BY_ID` (post-transform:
  `SUBJECTS.flatMap(...q=>[String(q.id),{...q,subject...}])`),
  `activeSubject`, `applySubject(name)` + `applySubject(activeSubject)`.
- `state` in `qbank_state_v1`: schema-v2/revisioned `attempts` (canonical
  history — never `state.answers` for progress), `bookmarks`, `reviews`,
  `tests`, `activeSession`, `questionNotes` (stable question ID keyed learner
  text/tombstone), and versioned `normalPracticeCheckpoint`;
  `qbank_active_subject_v1` for subject. State writes use the durable pending →
  primary → last-known-good transaction in `tools/durable_persistence_core.js`;
  callers receive success/failure and malformed primary state recovers visibly.
  `studyModules` (max 100, normalized; see `docs/CUSTOM_STUDY_MODULES.md`).
  Question notes use `tools/question_notes_core.js` and one independent cloud
  envelope per question; see `docs/QUESTION_NOTES.md`.
  Revision keeps its optional subject/bank/topic focus in page memory;
  `tools/revision_desk_core.js` filters question pools and passes the same
  scope to `nkFsrsQueue`, whose daily cap still counts reviews across all banks.
  The same revision owner installs primary navigation and global Home counts;
  `nkOpenRevisionHub` resets focus when entered from Home or primary navigation.
  The embedded forecast uses the existing eligible review pool and saved due
  timestamps, filters by the revision scope, and uses local calendar boundaries.
  Full FSRS and legacy `quick-revision` links remain reachable.
  `tools/insights_focus_core.js` groups all-bank questions by exact subject,
  bank, and source topic; it reads active attempts and launches the shared
  Practice engine without persisting a second analytics model.
  `tools/apply_learning_insights_v1.py` owns the final Insights renderer after
  coverage/correction transforms. `learning_insights_core.js` derives all metrics
  from effective answer events, saved results, current modules and FSRS schedules;
  period/scope UI state is transient. Legacy coverage/focus functions remain
  historical helpers, but neither section is rendered in Insights.
  The full-year calendar uses local days and continuous count/peak shade/glow.
  Completed results replace matched attempt timing; new result records include
  optional `sessionId` provenance. Existing durable state and generic result sync
  retain that additive field; no analytics collection or schema migration is added.
  Calendar/DST/Undo/edits/scopes/timing tests run in both workflows. The generated
  phone/tablet dashboard verifier replaces the retired coverage/focus UI journeys.
- Attempt helpers: `qAttempts(id)`, `latestAttempt(id)`, `chapterStats(id)`,
  `chapterQuestions(id)`, `totalAttempted()`, `overallAccuracy()`,
  `pendingReviewCount()`, `dueQuestions()`, `wrongQuestions()`,
  `bookmarkedQuestions()`, `currentStreak()`, `studyDayKeys()`.
- Renderers (exactly once each): `dashboard`, `topics`, `chapterPage`,
  `testsPage`, `analytics`, `morePage`, `libraryPage`, `resultPage`;
  protected question surfaces `examPage()` → `resultPage`,
  `reviewTestPage()` → `closeQuestionNavigator` (must not contain `nk-app-v114`).
- Chrome: `header` (brand `aria-label="NK QBank"`), `bottomNav` (5 tabs),
  `shell(page, active)`, `testRow(t)`, `libraryRow(q, kind)`.
- V11.4 vision (`nk-whole-app-vision-v114`, once): `nkAppSubjectMeta`,
  `nkSubjectGraphic`/`nkAppSubjectIcon` (inline Tabler outlines),
  `nkFlameGraphic`, `nkStreakMilestoneCopy`, `nkAppSubjectStats`,
  `nkAppPageHead`, `nkAppEmpty`, `nkWeekStrip`, multi-subject
  `startAllSubjectPractice`, `openMultiSubjectTestBuilder`,
  `nkMultiExamPoolIds`, `nkConfirmMultiSubjectExam`, builders
  `examBuilderMarkup`/`openSessionBuilder`/`openTestBuilder`.
- `window.QB` API: `nav`, `setSubject`/`openSubjectTopics`, `openChapter`,
  `practiceOne`, `startLibrary(kind)`, `startAllPractice`,
  `startAllSubjectPractice`, `continuePractice`, `openSessionBuilder`,
  `openTestBuilder`/`openMultiSubjectTestBuilder`, `confirmSession`,
  `nkSetMultiExamScope`, `nkUpdateMultiExamPool`, `nkSelectAllMultiTopics`,
  `nkConfirmMultiSubjectExam`, modal/search/filter/exam-scope helpers,
  session/nav/bookmark/submit/test/review/reset controls.
- Study modules (`tools/study_modules_core.js`, `NK_CUSTOM_STUDY_MODULES_V1`):
  `nkStudyModuleList`, `nkFindStudyModule`, `nkNormalizeStudyModule(s)`,
  `nkModuleValidQuestionIds`, `nkModuleProgress`, `nkSyncModuleFromSession`,
  draft/builder/persistence/resume/finish/restart + Home prioritization. The
  bank-aware candidate reads `BANKS_BY_SUBJECT`, keys scope by subject/bank/topic,
  retains legacy PrepLadder topic keys, and uses source-backed
  `studyCollections` facets to discover PYQ topics. The Topics selection alone
  determines module question scope; PrepLadder `pyq` comes from explicit source
  topic titles in `apply_marrow_bank_pilot.py`.
- Timed CBT builder (`tools/bank_aware_cbt_builder_core.js`,
  `NK_BANK_AWARE_CBT_BUILDER_V1`): the Tests entry opens a three-step full-page
  route. It uses the shared bank registry and bank-qualified topic keys to
  derive exact question IDs, then starts the existing exam engine. Topic taps
  update rows and counts in place, preserving scroll. Legacy modal builders
  remain for compatibility but are no longer the Tests entry. The verified-PYQ
  toolbar toggle replaces topic keys on activation and removes its PYQ keys on
  deactivation, retaining manually added regular topics. It uses only selected
  banks and topics whose questions all carry `studyCollections: ['pyq']`; an
  empty result leaves the draft intact. The selected question IDs determine
  the saved “PYQ CBT” title.
  The chapter Topic Test keeps cumulative per-question time and an absolute
  entry timestamp so navigation and reload cannot reset its 60-second limit.
- CBT result analysis (`tools/cbt_result_analysis_core.js`,
  `NK_CBT_RESULT_ANALYSIS_V1`) derives topic rows and missed IDs from each
  saved test's frozen `questionIds` and `answers`, resolving question metadata
  through the shared bank registry. Keys combine subject, bank, and topic ID.
  It changes the result view only; targeted follow-up enters the existing
  Practice engine. No new test or question persistence schema is introduced.
  Exact CBT retakes reuse `startSession` with a context carrying the initial
  saved test ID; `submitExam` copies that ID to the saved result's `retakeOf`.
  The result view compares the two saved answer snapshots and topic keys.
- Continue Practice (`tools/continue_practice_resume_core.js`,
  NK_CONTINUE_PRACTICE_RESUME_V1): regular topic Practice owns explicit
  activeSession.lifecycle, immutable original-order sessionQuestionIds, and a
  mirrored normal-Practice checkpoint with per-question revisions and
  practiceContext {subject,bank,topicId,title,questionIds}. Pause retains the active
  synced session; resume restores the complete original ordered session and saved
  position; Practice completion atomically persists a deterministic result and
  terminal checkpoint before clearing the live session. Wrong/Bookmarks, FSRS,
  Review, CBT and Custom Study Modules remain isolated from Home continuation.
- Android system Back (`tools/apply_android_back_guard_v1.py`,
  `NATIVE_BACK_SESSION_GUARD_V1`) asks the live WebView route and shared
  `activeSession` before displaying a native warning for Practice or Exam.
  Stay leaves state and route untouched; Exit follows WebView history, whose
  existing question-interaction boundary commits pending time/recall. The
  guard is applied after secure-origin generation and verified in the packaged
  Android phone/tablet journey.
- Browser/PWA system Back is guarded by the shared
  `tools/question_interaction_core.js` popstate boundary. A declined exit
  restores the question history entry before hashchange renders another route;
  accepted exit keeps the existing history and persistence path. `qbank.local`
  uses the native Android dialog, so the two warnings do not stack.
- `tools/apply_timed_abandon_grid_v1.py` installs confirmed timed-test Abandon
  inside the question navigator and final review grid after the exam review
  flags transform. It clears `activeSession` only after the learner confirms;
  failed persistence rolls state back. It creates no result or attempts.
- PrepLadder source-PDF explanation tone is adjusted only at display time:
  `apply_session_experience_v2.py` owns the final shared CSS filter on inline
  source page images/canvases and fullscreen source zoom. Earlier question
  style is replaced by this transform; PDF bytes, generated visual assets,
  mapping coordinates, and Marrow visuals are unaffected.
- Source visuals contract: per-question `visual {type:"source-pdf",
  source, page, crop{left,top,right,bottom} (PDF points, optional),
  fit: contain|width|native}`; renderer consumes metadata only.
- PrepLadder generation is owned by `build_source_visual_metadata.py`: complete
  native JPEG bytes, complete lossless native rasters with proportional safety
  canvas, or complete 288-DPI PDF-placement PNGs with a 72-pixel lossless
  safety canvas for graphs/vector labels. It emits
  `source_visual_inventory.json`. The historically named
  `improve_source_visual_assets_v1.py` is now audit-only: hashes, dimensions,
  aspect/boundary/text/answer-leak gates and eight-item comparison sheets.
  Manual PASS records in `data/prepladder_visual_reviews.json` are pinned to
  visual hash, owner, page and crop; stale/orphaned approvals fail closed. PWA
  service-worker packaging includes every released source visual; browser QA
  exercises graph, table, clinical, diagram and multi-panel representatives at
  phone/tablet sizes plus fullscreen zoom.

## Deterministic build pipeline (order enforced)

`tools/verify_build_pipeline.py` requires the protected transform order:

`fix_review_build` → `harden_review_renderer` →
`build_source_visual_metadata` → `improve_source_visual_assets_v1` →
`install_source_visual_renderer` → `cbt_canonical` →
`apply_question_ui_v2` → `apply_home_visual_redesign_v4` →
`apply_home_v5_fixes` → `remove_legacy_streak_layer` →
`apply_home_streak_and_header_v1` → `apply_home_actions_v1` →
`apply_cbt_boundary_and_toast_fix_v1` → `harden_cbt_review_footer_v1` →
`add_review_solution_grid` → `apply_question_experience_v1` →
`test_question_experience_v1` → `apply_session_experience_v2` →
`test_session_experience_v2` → `apply_whole_app_vision_v1` →
`test_whole_app_vision_v1` → `apply_custom_study_modules_v1` →
`test_custom_study_modules_v1` → `apply_home_command_center_v1` →
`test_home_command_center_v1` → `apply_continue_practice_resume_v1` →
`test_continue_practice_resume_v1` → `apply_question_content_hygiene_v1` →
Android/sync/FSRS layers → `fix_boot_syntax` → Marrow registration →
`apply_marrow_structured_table_renderer_v1` →
`apply_question_presentation_v1` → `test_question_presentation_v1` →
image installation → notes → revision → Insights →
`apply_bank_aware_cbt_builder_v1` → `test_bank_aware_cbt_builder_v1` →
`apply_cbt_result_analysis_v1` → `test_cbt_result_analysis_v1` →
`verify_product_contract --stage generated` →
`verify_cbt_invariants`.

Full `build-apk.yml` additionally runs: study-metrics test, source contract,
PDF renderers + `PyMuPDF`/`Pillow` maps (`build_biochem_solution_map`,
`repair_source_solution_renderer`, `final_hardening`), visual contract,
`cbt_final_lock`, UI polishes (V10.3.7–V10.3.11), V11.3.1 session fixes,
final `node --check` on all inline `<script>` blocks, generated-app greps,
JDK 17 + Gradle `assembleDebug`, packaged-APK checks
(APK ZIP integrity, no `v102-streak-layer`, required markers, ≥400 PNGs,
packaged JS check), packaged contract, `write_build_manifest.py`
(`NK-QBank-build-manifest.json`), artifact upload.

## Local verification environment

Android Termux is the local development environment. `tools/verify_local.py`
runs source/behavior checks without asset generation. PyMuPDF entry points use
`verification_preflight.py` to skip Android/Termux before import or mutation.
Full Ubuntu CI uses `--require-pdf` and fails closed; PDF generation and downstream
generated-app/package checks remain mandatory there. See `docs/LOCAL_DEVELOPMENT.md`.

## Workflows and gates

- `.github/workflows/build-apk.yml` — full deterministic Android APK + PWA
  artifact build. Production promotion requires an explicit dispatch from
  `main` and an exact full-SHA match; branch-name defaults cannot promote it.
- `.github/workflows/engineering-gate.yml` — fast gate: `compileall`,
  study-metrics, source contract, pipeline order. Must stay green.
- Many historical `v10*` workflows remain; ignore unless diagnosing old runs.

## FSRS smart-review extension

- `question_interaction_core.js`, installed immediately after the FSRS core by
  `apply_fsrs_v1.py`, wraps question commands in nested transactions. Inner saves,
  rendering, navigation and success feedback are deferred until one complete state
  commit succeeds; failed actions restore the pre-action state. Option callbacks
  carry question/session identity; submitted Practice, Review and expired CBT are
  guarded at the handler boundary. History Back flushes pending recall through the
  same transaction. Explicit final submission records legacy pending selections;
  Pause retains them. Special-mode origin/context never replaces the normal
  Practice checkpoint. Content and option rendering styles are unchanged.

- `tools/apply_fsrs_v1.py` installs `tools/fsrs_scheduler_core.js` after the
  cross-device layer and loads vendored `ts-fsrs` 5.4.2 UMD plus its MIT license
  from `app/src/main/assets/vendor/ts-fsrs/`; there is no runtime CDN.
- Attempts remain synchronization truth. Rated attempts carry FSRS audit snapshots;
  schema-v2 `state.reviews` is deterministically replayed from sorted attempts. A
  one-time local backup and per-card legacy due override preserve existing due dates
  until the first post-migration rating. Preferences sync in the existing envelope.
- Rating edits are immutable `isRatingRevision` events keyed by `ratingOf`,
  stored in `state.fsrsRatingRevisions` separately from answer attempts. Existing
  `attempts` sync envelopes transport them; timestamp/ID ordering deterministically
  selects the effective grade before FSRS replay at the original retrieval time.
  Original answer events and scheduler snapshots remain audit history. Session IDs
  bind the visible dock to its retrieval; stale question/session callbacks are rejected.
  Undo of an amendment restores the preceding grade without removing the answer;
  rating edits and Undo share the durable interaction transaction.
  Checkpoint merge honors per-question pending removals and suppresses committed
  pending IDs. Mistakes and saved-result follow-up read effective answer history,
  independently of the all-answered FSRS eligibility pool.
- The combined queue asserts globally unique IDs, prioritizes due learning/relearning,
  then low-retrievability overdue reviews, then capped new cards.
- Eligibility is lifecycle-based: every active attempt (correct or incorrect)
  is in the pool; an unanswered ID becomes `reason: skipped` only at explicit
  final submission. Pause commits pending answered ratings through the navigation
  wrapper and does not synthesize events for untouched IDs.

## Shared question-presentation normalization

- `tools/apply_question_presentation_v1.py` installs
  `question_presentation_core.js` after all PrepLadder/Marrow records exist.
- It finds coherent A–D/A–E answer runs, separates extraction-owned table or
  explanation fragments, and wires one semantic stem renderer into Practice,
  CBT, and Review. Source records remain unchanged on disk.
- Records without a usable choice sequence/correct index fail closed.
- Source-backed stem-only repairs use `nkQuestionStemOverride` and presentation-owned
  `stem`, independent of table overrides. Biochemistry `4-3` requires its stable ID
  and exact raw/hygiene-normalized source fingerprint; mismatches fail closed.
  Rendering does not rewrite canonical stems, choices, answer indices or page metadata.
- The same late layer owns `nkScientificMarkup`: it escapes first, then emits
  bounded semantic `<sub>`/`<sup>` markup for explicit exponents, common
  biochemical formulae, blood-gas notation, ionic charges and a conservative set
  of unambiguous OCR-placeholder repairs. It is wired into Practice/CBT/Review
  stems and options, PrepLadder `richText`, takeaways, Marrow native tables/text,
  and the separate enhanced-explanation wrapper. Ambiguous missing glyphs remain
  visible for source-backed stable-ID cleanup rather than being guessed.

## Marrow multi-bank extension — expanded Phase A architecture

- `feature/marrow-bank-pilot` implements question-bank source as a data
  dimension inside the existing subject model. It does **not** create a second
  study engine. `activeBank` / `qbank_active_bank_v1`, the `banks` route,
  and the shared registry select data; Practice, CBT, Review, FSRS, sync,
  modules, analytics, bookmarks, persistence and revision queues remain shared.
- Runtime registry is subject-indexed:
  `MARROW_RECORDS` → `MARROW_BY_SUBJECT` → `BANKS_BY_SUBJECT`.
  `nkBankRecords`, `nkBankRecord`, `nkAllBankQuestions` and global
  namespaced IDs let the existing engines resolve all bank questions safely.
- Current Marrow records:
  - Anatomy: 1,115 questions / 63 topics.
  - Biochemistry: 582 / 28.
  - Physiology: 1,014 / 43.
  - Combined: 2,711 unique questions / 134 topics.
- Expanded transport is manifest-verified compressed/base64 data:
  `data/marrow/anatomy_ch001_063.zlib.b64.part*` +
  `anatomy_ch001_063_manifest.json`;
  `biochemistry_ch001_028.zlib.b64.part*` +
  `biochemistry_ch001_028_manifest.json`;
  `physiology_ch001_043.zlib.b64.part*` +
  `physiology_ch001_043_manifest.json`.
  The launcher validates shard count, base64/compressed/raw lengths, SHA-256,
  subject/bank identity, topic/question counts, unique namespaced IDs, four-option
  shape, correctOption bounds and question→topic linkage before use.
- The earlier Anatomy 62-question and Physiology 80-question pilot bundles remain
  compatibility/regression subsets. Expanded records replace the learner-facing
  Marrow envelope; approved augmentation IDs remain subsets of the expanded banks.
- Learner stem/option OCR repairs are applied only at Marrow bank generation from
  stable-ID display override manifests. Each manifest pins the immutable bundle
  question/options fingerprint; source-reviewed Physiology manifests also pin the
  ED8 PDF hash. The answer index and raw compressed source are never rewritten.
- Explanation architecture is layered and non-destructive: all Marrow uses native
  structured source text/tables. The enhanced runtime layer includes only
  `approved-reference` and `approved-rollout` batches; `candidate-rollout`
  files retain validated identity/count but are excluded from packaging and
  inventory enhancement counts. Resolve the current approved subset from the deterministic inventory; historical counts are not release status.
- `data/marrow/explanation_inventory_v1.json` is deterministic, text-free review
  metadata for all 2,711 IDs. It is regenerated from source hashes and never
  changes imported records or learner-facing explanations.
- Three resolved Anatomy reconstructions remain deterministic and provenance-marked:
  `ANAT_CH02_Q010`, `ANAT_CH03_Q004`, `ANAT_CH04_Q013`.
- Marrow topics use `data/marrow/topic_index_taxonomy.json`, an explicit mapping
  keyed by subject and stable topic ID with title assertions and canonical
  section order. The renderer does not infer Marrow sections from number ranges.
  Four cross-system Anatomy entries remain internally marked for review.
- Data commits use small shards / Git blobs rather than monolithic connector writes;
  an earlier pilot proved oversized writes can truncate. Temporary staging bridges
  are transport-only and are never runtime dependencies or sources of truth.
- The Marrow transform stays late in the deterministic pipeline, after protected
  UI/sync/FSRS transforms and before final JavaScript/product/CBT/PWA/browser/APK
  gates. Playwright covers all three subjects and returns to PrepLadder to detect
  registry leakage.
- Full runbook: `docs/MARROW_BANK_INTEGRATION.md`.

## Integration points to preserve

- `richText(text)` insertion anchor for multi-subject workflows;
  `window.QB={getState...}` export anchor (prepend, never replace tail);
  `</head>` style anchor (`...-v114` once); `nk-session-experience-v114`,
  `cr-grid`, `&scale=4` markers from session/review/PDF stages.
- Review entry attributes (`data-v102-review-cta`, `data-review-test-id`,
  `__QB_OPEN_REVIEW`), CBT footer (`review-fixed-actions`,
  `nk-cbt-review-footer-v1`, `nk-review-solution-grid-style`), toast
  (`showToast(msg,type`), root (`root.innerHTML=`), navigator
  (`openQuestionNavigator`, `closeQuestionNavigator()`), `sessionShell`,
  `qb-nav-submit`, `s.mode==='practice'`.

## Project-memory architecture

- Root `AGENTS.md` is the canonical instruction router.
- `.project-memory/README.md` defines roles and truth precedence; `STATE.md` is
  replace-in-place handoff, while `SESSION_LOG.md` is append-only history.
- Thin root/tool adapters contain no product knowledge and point to `AGENTS.md`
  plus `.project-memory/STATE.md`.
- `tools/verify_project_memory.py` checks required placement, adapter size and
  routing, local links, state length, verification vocabulary, and forbids a
  self-staling hardcoded HEAD field.
- V11.6 content-quality implementation lives on separate branch
  `v11.6-content-quality` at `125d68b`: `question_content_hygiene_core.js` plus
  its deterministic apply/test scripts. It is not present in this V11.5 tree
  until deliberately consolidated.

## V11.7 cross-device extension (implementation branch)

- One generated QBank product feeds Android and `build/web`; question content
  remains static/bundled and Firestore stores only authenticated learner state.
- Android uses a private `https://qbank.local/app/` intercepted asset origin. A
  one-time native bridge migrates prior `file://` localStorage before boot and is
  then removed; no universal file-origin network access is enabled.
- `tools/cross_device_sync_core.js` is injected late by
  `apply_cross_device_pwa_v1.py`: local-first outbox, Firebase email/password
  REST auth, normalized Firestore entity collections, per-device revisions,
  immutable attempt union, tombstones, and deterministic conflict handling.
- PWA assets: manifest, service worker, responsive tablet shell, PDF.js browser
  source renderer, and `build_web_dist.py`. Pages excludes only the >25 MiB
  Anatomy PDF; its unchanged R2 URL is runtime configuration.
- Public runtime config is generated by `write_runtime_config.py`; no privileged
  credential belongs in the client. After authentication, Firestore routing uses
  the Firebase project ID from the ID token's `aud`/`iss` claims, with runtime
  config only as fallback. Firebase ID-token uploads use individual document
  PATCH requests in bounded parallel groups; the REST `:batchWrite` route is not
  used because it returned permission errors for otherwise valid owner-scoped writes.
  Upload acknowledgments only remove the revision actually sent, and each parallel
  batch settles before a retry. Downloads query all per-user revisions because
  client timestamps cannot safely cursor late offline uploads.
  Saves trigger debounced upload; signed-in clients also retry silently every five
  minutes and on foreground. Security ownership is enforced by `firestore.rules`.
  See `docs/CROSS_DEVICE_PWA.md`.

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

Observed candidate limitations: Topics continuation uses sticky positioning after the list; FSRS is inline details/summary; PWA PDF zoom reuses a width-derived raster capped at 2x density. See docs/REJECTED_TOPICS_FSRS_HANDOFF.md for file owners and diagnostic limits. No PDF regression root cause has been established.

- Recovery: `build_web_dist.py` emits a narrowly routed Pages worker for `/anatomy-source.pdf`, streaming the unchanged configured R2 PDF with Range/ETag support. The web-only config points to that same-origin path; native source rendering is unchanged. Direct R2 GET lacked CORS headers for both feature and localhost origins on 2026-09-08. Worker behavior tests preserve bytes/ranges and static asset fallback.


## Feature-line ownership for recovered Topics/FSRS — 2026-09-08

The full recovered Topics fixed-tray/journey implementation and dedicated FSRS
settings route currently live on `feature/marrow-bank-pilot`, not stale
`main`. The feature preview was physically approved; Cloudflare production was
not promoted.

When consolidating, reuse the exact feature-line implementation and tests rather
than re-creating UI behavior. See `docs/TOPICS_FSRS_FEATURE_HANDOFF.md`.

Topics major-section classification must move to one explicit source-aligned
mapping; see `docs/MARROW_TOPIC_INDEX_TAXONOMY.md`. Explanation fine-tuning
remains a separate augmentation layer; see
`docs/MARROW_EXPLANATION_FINE_TUNING.md`.

## Source-reviewed image continuation pages

Marrow image coverage may use exact continuation-page corrections from
`data/marrow/images/source_reference_page_reviews.json`. Corrections pin the
original stable source reference, owner/role/pages and PDF hash; coverage
retains original pages in its report and matches only explicitly reviewed
replacement pages. Imported bundles remain immutable. A page correction is
not an image release and cannot silently substitute a neighboring figure.

## Reviewed question-completeness contracts — 2026-09-30

Individual review evidence lives in `docs/question-completeness/`; accepted display
contracts live in `data/question_completeness_reviews_v1.json`.
`tools/build_question_completeness_reviews.py` verifies raw question fingerprints,
canonical shard hashes and source PDF hashes/pages, then compiles bounded contracts
into the shared `tools/question_presentation_core.js`. Raw imports remain immutable.
Runtime contracts fail closed on fingerprint drift; demonstrated source omissions
receive explicit incomplete-source presentation and scored-answer gates through the
shared presentation/interaction path. Heuristic flags alone do not gate questions.
Exact source-key display restoration is restricted to the two reviewed five-choice
PrepLadder tactile-receptor questions whose raw key is null; all five choices remain.
Native question images retain source-stream fingerprints and stable owner bindings.

The Android/PWA workflow's optional `render_review_regions` input regenerates
archival source-region review sheets. Ordinary builds skip those roughly 1 GB of
review artifacts while retaining PDF generation and downstream package validation.
Source-only review/compiler verification does not establish full build verification.

The completeness queue additionally scans whole-bank glyph artifacts and explicit
question-visual cues against generated runtime owner roles, merges review evidence,
and uses `--require-reviewed` in CI to reject any new unreviewed candidate. A small
queue report is retained as an artifact. Current compilation contains 114 bounded
display entries. Native source pixels may replace a previously released region crop
for QUESTION ownership when that crop includes neighboring prose; existing
explanation ownership remains intact (Physiology37Q9 is the concrete example).

## Reviewed explanation refinements — 2026-09-30

User-directed parallel content workers own disjoint chapter files; one integrator
owns shared state and a combined verification build. The refinement-wave manifest
pins exact reviewed augmentation/source hashes, prior approved IDs, raw bundle
hashes and the complete source-omission ledger. Source checks reject duplicate
IDs, invalid emphasis and source-key/rationale drift. The wave browser checks
every new runtime config on phone/tablet and real representative answer surfaces.
`displayTables` is an approved-explanation-only display override for source-page-
reviewed table reconstructions with provenance, leaving imported metadata intact.
Explicitly recovered `orphanTableIds` may restore omitted table objects only when their IDs already exist in native source blocks and their pages match original explanation provenance; PDF hashes and complete cells remain required. The shared compatibility renderer owns both native and reviewed display tables. It also adapts populated source `headers` lists to the renderer's `columns` contract without changing source records (Physiology Ch42 Q8 is the regression fixture).

Approved production releases may use `.github/workflows/deploy-approved-main.yml`: only a successful full Android/PWA workflow for a main push whose commit message contains `[approved-production]` qualifies. The follow-up downloads that exact run artifact, verifies its commit against current main and its packaged APK hashes, sets Pages production_branch to main, then deploys without rebuilding. Ordinary main pushes remain unpromoted; existing manual exact-SHA dispatch remains available.

The 2026-10-01 production promotion used the dedicated `release/approved-production-20261001` push trigger because the workflow_run follow-up did not appear. Its fallback pins successful build36883871119 and product18e4cd58, with the same exact-current-main/APK safeguards. This release-specific trigger cannot deploy a later unrelated commit; future releases must select their own verified artifact or use the existing exact-SHA manual dispatch. Do not assume the workflow_run trigger has been operationally verified.

The final `apply_app_clarity_v1.py` presentation owner follows learning Insights and wraps navigation renderers only. It removes known redundant copy without changing queue/scheduler/storage APIs; clarity CSS targets navigation headers/cards. Independent scope-card updates use the same formatter. Metric definitions remain in collapsed Insights help.

## Compact result analysis and named mocks

`apply_refined_analysis_v1.py` runs after app clarity. It replaces only result markup and wraps the existing CBT builder/Tests renderers. The shared Practice/CBT/Review engines, immutable original results, FSRS, marked-question follow-up and retake lineage stay authoritative. Test breakdowns aggregate exact subject/bank/topic identities; Practice omits breakdowns. Time histograms read only finite saved question times and expose missing timing.

Optional `state.savedMocks` stores names and ordered fixed question IDs. Durable state normalization preserves it; the existing sync envelope/winner/tombstone system adds a `savedMocks` collection, including reset and account isolation. Starting a mock validates every saved question and uses the protected timed-session entry point; it never silently shortens an unavailable set. A repeated exact set uses the existing initial-test/retake comparison. Modules retain their existing separate naming and restart flow.

## Shared interaction system — 2026-10-02

Final apply_interaction_polish_v1.py follows refined analysis and routes committed
question paints through the shared renderer. In-place CBT/recall/bookmark/mark
updates preserve source DOM and rollback. Presses cancel on gestures; short
motion respects reduced motion. apply_android_haptics_v1.py follows Activity
regeneration. Ordinary navigation is silent. Ownership and verification:
docs/INTERACTION_POLISH_2026-10-02.md.

## Analysis and PWA update identity — 2026-10-03

`refined_analysis_core.js` owns fixed outcome segments and labeled counts plus
saved-timing distributions/running totals. `learning_insights_core.js` keeps
period-scoped rankings/denominators with a consistent accuracy fill and omits
its revision prompt card. Result-specific missed/marked/correction APIs remain.
`pwa_update_core.js` is injected by the existing cross-device owner. Web packaging
adds `nk-qbank-build` metadata; the service worker replies to `NK_QBANK_VERSION`
through MessageChannel. Only a verified different waiting worker gets a notice;
Later is tab/build-scoped and active study defers it. Activation/reload remains
explicit. Real browser lifecycle checks run in the full packaging workflow.

## UWorld and Revision integration — 2026-10-03

The source-reviewed collection/document/media architecture is described under
Runtime data and assets above. `uworld_source_text.py` remains the auditable raw
OCR fallback; reviewed source documents provide the main presentation. Pools
exclude blocked references before sampling; individual references use the
existing modal/focus model without changing study state.
See `docs/UWORLD_BIOCHEMISTRY_PILOT.md` for source limits and scale requirements.

The Revision owner includes `revision_session_core.js`: explicitly tagged full
eligible Mistakes/Bookmarks/Due snapshots use the existing checkpoint collection
and restore exact membership/position. Due keeps scheduler priority and daily
cap. Finish records answered work only. No new persistence schema is introduced.

Web packaging applies crawler exclusion to HTML, robots.txt, static response
headers and all same-origin source-worker responses. Public repository content
and direct asset access remain public; this is not authentication.

### Preproduction response and Android boundaries

`tools/web_security_policy.py` supplies one response policy for static Pages
headers and the source-streaming Worker, including frame denial, MIME protection
and a restricted cross-origin referrer. Search exclusion, source bytes/ranges,
validators and offline caching retain their existing owners.
`apply_android_secure_origin_v1.py` restricts the migration bridge/file access to
the one-time file-origin migration; completion removes both. Private-origin
missing/rejected assets return local404; HTTPS API requests retain their normal
network path. The Android driver checks those boundaries on initial/repeated
launches while preserving native haptics and existing resume/state checks.
