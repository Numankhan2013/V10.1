# ARCHITECTURE.md — Current Implementation

## Production shape (do not replace)

- Android wrapper (`app/src/main/java/com/qbank/biochemistry/MainActivity.java`,
  `AndroidManifest.xml`) + **WebView** + monolithic
  `app/src/main/assets/index.html` (~6 MB on V11 branches; 1.9 MB on stale
  `main` because single-subject + pre-generation).
- Offline-first: bundled data + PDFs + PNG cache + `localStorage` persistence;
  native code only where genuinely useful.
- Long-term direction is incremental isolation (persistence, rendering, review,
  analytics, tokens), never a big-bang rewrite.

## Runtime data and assets

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
- `state` in `qbank_state_v1`: `attempts` (canonical history — never
  `state.answers` for progress), `bookmarks`, `reviews`, `tests`,
  `activeSession`; `qbank_active_subject_v1` for subject;
  `studyModules` (max 100, normalized; see `docs/CUSTOM_STUDY_MODULES.md`).
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
  draft/builder/persistence/resume/finish/restart + Home prioritization.
- Source visuals contract: per-question `visual {type:"source-pdf",
  source, page, crop{left,top,right,bottom} (PDF points, optional),
  fit: contain|width|native}`; renderer consumes metadata only.

## Deterministic build pipeline (order enforced)

`tools/verify_build_pipeline.py` requires this order (31 protected steps):

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
`test_custom_study_modules_v1` → `fix_boot_syntax` →
`verify_product_contract --stage generated` → `verify_cbt_invariants`.

Full `build-apk.yml` additionally runs: study-metrics test, source contract,
PDF renderers + `PyMuPDF`/`Pillow` maps (`build_biochem_solution_map`,
`repair_source_solution_renderer`, `final_hardening`), visual contract,
`cbt_final_lock`, UI polishes (V10.3.7–V10.3.11), V11.3.1 session fixes,
final `node --check` on all inline `<script>` blocks, generated-app greps,
JDK 17 + Gradle `assembleDebug`, packaged-APK checks
(APK ZIP integrity, no `v102-streak-layer`, required markers, ≥400 PNGs,
packaged JS check), packaged contract, `write_build_manifest.py`
(`NK-QBank-build-manifest.json`), artifact upload.

## Workflows and gates

- `.github/workflows/build-apk.yml` — full deterministic Android APK + PWA
  artifact build, with optional Cloudflare Pages deployment when authorized.
- `.github/workflows/engineering-gate.yml` — fast gate: `compileall`,
  study-metrics, source contract, pipeline order. Must stay green.
- Many historical `v10*` workflows remain; ignore unless diagnosing old runs.

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
  config only as fallback. Security ownership is enforced by `firestore.rules`.
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

