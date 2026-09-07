# SESSION_LOG.md — Chronological Record of Substantial Sessions

Append new entries at the bottom. Keep each entry factual: branch/commit,
CI runs, what changed, verification, device status, next step.
`STATE.md` stays current; this file accumulates.

## 2026-09-06 — Run 220 accepted baseline (background)

- Branch `v11-source-visuals`, commit `73c04281696137fda712ae0b9b7079c9c4a15635`,
  run `34011265432` (`Build Home three-action refinement`) success.
- User physically tested and confirmed working; declared core features done,
  no regression. All later work builds forward from here.
- See `memory.md` §2 for the confirmed working-areas list.

## 2026-09-06 — V11.1 engineering foundation → V11.2 study clarity →
## V11.3 question experience → V11.4 whole-app vision (background)

- Hardening branches `v11.1-engineering-foundation`,
  `v11.2-study-clarity`, `v11.3-question-experience`,
  `v11.4-whole-app-vision` added deterministic transforms + tests without
  replacing the V10.3.11 question-first shell.
- V11.2 fixed subject counts/progress (`SUBJECTS.flatMap`, `state.attempts`,
  numeric-safe formatting) with `test_study_metrics.py`.
- V11.3.1 added shared Practice/CBT/Review experience
  (`nk-session-experience-v114`, docked footer, functional grid).
- V11.4 added whole-app visual system (`nk-whole-app-vision-v114`, subject
  identity, streak milestones, all-subject practice, multi-subject CBT).
- Docs added: `docs/ENGINEERING_BASELINE.md`, `docs/STUDY_CLARITY.md`,
  `docs/V11_SOURCE_VISUALS.md`, `design-qa.md` (device checks blocked in CI).

## 2026-09-06 — V11.4 vision test failure and fix (agent session)

- Commits `21c97d0` (permanent Practice-20), `f685aff` + `d0c67a1`
  (streak milestones) removed the conditional `startLibrary('review')` button
  from `tools/apply_whole_app_vision_v1.py`; `test_whole_app_vision_v1.py`
  still required it.
- Failures: Build V10.1 APK `34034905290`, `34034904068`, `34034791899`
  (`Whole-app vision markers missing: ["window.QB.startLibrary('review')"]`);
  Engineering Gate stayed green.
- Fix `9e6abc71eca192808e6fbd70d4127011c6a47ef0`
  (`Restore Due Review action alongside permanent all-subject practice`):
  Today’s Focus keeps permanent Practice-20 and adds conditional
  `Review N Due` (`startLibrary('review')`) when due>0 + 4-column
  `:has(>button:nth-child(4))` CSS with graceful fallback.
- Verification: Build V10.1 APK `34043059869` success (1m48s,
  `WHOLE_APP_VISION_OK`, packaged checks pass); Engineering Gate `34043059872`
  success. User confirmed the new APK works and UI changes are great.

## 2026-09-06 — V11.5 Custom Study Modules (build-verified candidate)

- Branch `v11.5-custom-study-modules` on top of `9e6abc7`.
- `Add persistent Custom Study Modules` + `Label V11.5 APK artifact` → HEAD
  `f13d12ff2708f518a9e6be839477623be5f471c4`.
- Added `tools/apply_custom_study_modules_v1.py`,
  `tools/study_modules_core.js`, `tools/test_custom_study_modules_v1.py`;
  extended `verify_build_pipeline.py` + `verify_product_contract.py`;
  added `docs/CUSTOM_STUDY_MODULES.md`; updated `README.md`, `memory.md`,
  workflow labels.
- CI: Build V10.1 APK `34049523411` (1m41s) + `34049637559` (1m40s) success;
  Engineering Gate `34049523425` + `34049637590` success.
- Status: **build-verified only**; awaiting physical-device test and explicit
  promotion. Do not call accepted baseline yet.

## 2026-09-06 — Harness-agnostic memory system created (this change)

- Added `AGENTS.md` (universal entry, session start/end rules, thin-adapter
  policy) + `.project-memory/` (`STATE`, `ROADMAP`, `DECISIONS`,
  `ARCHITECTURE`, `PRODUCT`, `SESSION_LOG`).
- Preserved `memory.md`, `docs/*`, `design-qa.md`, `README.md` unchanged;
  populated new files from verified repo state (branches, commits, run IDs,
  55 tools, pipeline order, 420 visuals, subject counts).
- No harness-specific duplicates created. Next: fresh-harness reconstruction
  check, then V11.5 device test → R1 question screen.

## 2026-09-06 — V11.5 physically accepted

- User installed the V11.5 Custom Study Modules APK and reported it “works
  beautifully,” with no questions about the feature.
- Promoted `f13d12f` / build `34049637559` from build-verified candidate to the
  accepted product baseline.

## 2026-09-06 — V11.6 content-quality candidate

- Separate branch `v11.6-content-quality`, commit `125d68b`.
- Added comparison/table-aware takeaway extraction and centralized question-stem
  sanitation. Audit: 719 questions, 78 PrepLadder/page-contaminated stems.
- Engineering Gate `34050921166` and full packaged APK build `34050921180`
  passed. Artifact `V11.6-content-quality-debug-apk`; physical acceptance pending.

## 2026-09-07 — Memory reconstruction audit and hardening

- Read all canonical and legacy memory from a fresh agent context and verified
  it against Git/GitHub. Structure and root placement were sound.
- Fixed stale V11.5 acceptance/CI facts and the impossible hardcoded-current-HEAD
  pattern; documented V11.6's separate lineage.
- Added a schema README, thin Claude/Gemini/Cursor/Copilot adapters, and
  `tools/verify_project_memory.py` to enforce placement and low-drift rules.

## 2026-09-07 — V11.6 accepted; V11.7 cross-device implementation started

- User confirmed V11.6 (`125d68b`, full run `34050921180`) was physically
  device-tested and accepted. V11.6 is now the immutable product baseline.
- Created `v11.7-cross-device-pwa-sync` from V11.6 and merged the harness-neutral
  memory lineage at `309aabb`; neither accepted/checkpoint branch was altered.
- Added shared PWA assets, adaptive iPad/tablet layout, service-worker caching,
  browser PDF.js source rendering, Cloudflare artifact/deployment wiring, public
  runtime config generation, Firebase email/password + normalized Firestore sync,
  ownership rules, local outbox/cursors, tombstones, and conflict tests.
- Android now has a deterministic private HTTPS asset-origin transform and a
  one-time bridge that migrates the prior file-origin localStorage before boot.
- Final product commit `1b1fc9f`: Engineering Gate `34076883867` and full
  generated/packaged Android + PWA run `34076883874` passed; artifact
  `V11.7-android-pwa`. Cloud deployment was skipped because no account variables
  or secrets exist. V11.7 is build-verified, not device-verified or accepted.

<!-- V11.7_DEPLOYMENT_HANDOFF_2026-09-07 -->
## V11.7 deployment handoff — 2026-09-07

- Active candidate: `v11.7-cross-device-pwa-sync`. Physically accepted rollback baseline remains **V11.6 Content Quality** at `125d68b`; do not call V11.7 accepted until Android migration and Android↔iPad sync pass on real devices.
- Firebase/Firestore is configured and builds now report `QBANK_RUNTIME_CONFIG_OK firebase=configured`. Exact GitHub Variables: `QBANK_FIREBASE_API_KEY`, `QBANK_FIREBASE_PROJECT_ID`, `QBANK_ANATOMY_PDF_URL`. Firestore user-scoped rules and the intentionally empty composite-index set are deployed.
- Cloudflare Pages project: `nk-qbank`. Exact GitHub Secrets: `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`. Push builds create preview deployments. Manual **Build V11.7 Android + PWA** dispatch now also promotes the same artifact to production so `nk-qbank.pages.dev` is updated deliberately.
- Anatomy source PDF uses the configured public R2 object URL because it is ~46 MiB; Biochemistry and Physiology PDFs ship inside `build/web`.
- Physical iPad testing found and fixed two browser runtime bugs: `278b6c5` fixed the blank-screen sync bootstrap (`nkAuth` initialization timing); `7b047e5` fixed PDF.js canvas creation by avoiding a local `document` name that shadowed the DOM document.
- Latest hashed preview opens successfully on iPad. Before the production-promotion workflow change, the root `nk-qbank.pages.dev` still served the older blank production deployment. Source-PDF rendering, Anatomy/R2 CORS, final production URL, Android in-place upgrade, and full two-way sync still require physical verification.
- Next: wait for CI on the current branch → manually dispatch **Build V11.7 Android + PWA** once → verify `https://nk-qbank.pages.dev` → add final Pages hostname to Firebase Authentication authorized domains → ensure R2 CORS allows the exact Pages origin and Range GETs → install V11.7 APK over V11.6 without uninstalling → verify old local data → same-account Android/iPad sync, offline/reconnect, force-close/reopen, sign-out/in tests.

## 2026-09-07 sync diagnostics
- Physical Android+iPad test showed Sync now flashing "Sync paused" and then remaining visually stuck on "Synchronizing…" with no state transfer.
- Root cause of the stuck label is confirmed in `tools/cross_device_sync_core.js`: the error render happened while `nkCloudBusy` was still true and `finally` cleared the flag without a final render. Initial auth also treated a failed first sync as success because `nkCloudSync(true)` returned false without being rethrown.
- Commit `6cd5322` fixes those control-flow defects and surfaces the actual Firebase/Firestore error text in the Sync card/toast. This is diagnostic plus correctness hardening; the underlying backend failure still needs one fresh physical test to reveal its exact message before calling sync working.

## 2026-09-07 — Firestore request-failure hardening
- User physically tested the diagnostic build on both Android and PWA. Sync no longer stays falsely stuck on “Synchronizing…”, but both targets report `Request failed` and transfer no state.
- Added runtime Firebase project-ID discovery through the public Identity Toolkit project-config endpoint and made Firestore use the discovered ID. This protects against a configured display name/stale project ID while keeping the explicit GitHub variable as fallback.
- Added stage-aware sync errors and HTTP status reporting so the next physical failure identifies whether the problem is project resolution, auth refresh, Firestore download, or upload.


## 2026-09-07 — Fix Firestore download HTTP 404
- Reproduced the deployed configuration and found `QBANK_FIREBASE_PROJECT_ID=nk_qbank`. The prior runtime discovery returned Firebase project number `174056010089`; Firestore returned 404 for that database path. The real Firebase/Firestore project ID is `nk-qbank`.
- Corrected the GitHub Actions variable to `nk-qbank` and changed sync project resolution to use the authenticated ID token's `aud`/`iss` project claim after token refresh.
- Added a regression test for JWT project resolution and updated the PWA sync documentation. Targeted local checks and Engineering Gate `34095662853` passed. Manual run `34095870813` built the APK/PWA artifact and promoted it to Cloudflare production; live Pages serves the corrected config and resolver. Physical Android↔PWA verification remains.
