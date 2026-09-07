# STATE.md — Current Project State and Handoff

> Keep concise and current. History goes in `SESSION_LOG.md`, durable reasoning
> in `DECISIONS.md`, and future work in `ROADMAP.md`.

## Repo / branch

- Repo: `Numankhan2013/V10.1` (private)
- Active branch: `v11.7-cross-device-pwa-sync`
- Resolve live branch/HEAD with `git branch --show-current` and
  `git rev-parse HEAD`; never hardcode a self-staling current-HEAD value here.
- Accepted product parent: V11.6 `125d68b`; the V11.7 branch merged the
  harness-neutral memory lineage at `309aabb`. Resolve live HEAD with Git.
- Earlier product lineage: V11.5 `f13d12f` → V11.6 `125d68b`.
- `main` (`8bc0be4`) is stale and must not be used as the V11 baseline.

## Verification and accepted baseline

- Accepted baseline: **V11.6 Content Quality**. The user physically tested and
  accepted the APK on 2026-09-06.
- Accepted product commit: `125d68b`; canonical APK run: `34050921180`.
- Latest V11.5 memory-head build `34051356682` and Engineering Gate
  `34051356708` both passed at `e6a2fc7`.
- V11.6 Engineering Gate `34050921166` and full packaged build `34050921180`
  passed before physical-device acceptance. It improves comparison/table
  takeaways and removes PrepLadder/page metadata from 78 of 719 audited stems.

Labels are strict: implemented ≠ build-verified ≠ device-verified ≠ accepted
baseline. Only explicit user physical-device approval promotes a candidate.

## What currently works (V11.6 device-verified and accepted)

- Practice, Timed CBT, final-question session review, navigator/jumping,
  Submit/Finish, Practice/CBT Analysis, and Review Solutions with grid,
  Previous/Next, End Review, and source explanations.
- Home V4/V8 command center, Topics V2, Chapters, Tests, Insights, More,
  revision libraries, subject switching, and reliable scroll reset.
- All-subject random practice, multi-subject CBT, accurate subject/topic counts,
  persistent attempt history, bookmarks, wrong/due queues, and Insights.
- Source visuals: 420 packaged PNGs (Anatomy 297, Physiology 62,
  Biochemistry 51), source-PDF fallback, fullscreen zoom/pan, isolated
  Biochemistry renderer, and authoritative Physiology source PDF.
- Custom Study Modules: persistent reusable subject/topic sets using
  Unattempted/Wrong/Bookmarked/Mixed pools, frozen IDs, deduplication, seeded
  selection, resume, Home continuation, completion analysis, and unified history.
- Deterministic transforms, final and packaged JavaScript checks, product/CBT
  contracts, Gradle APK build, packaged verification, and build manifest.

## Known problems / cautions

- V11.7 is a **build-verified, not device-verified** evolution branch merging
  accepted V11.6 with the memory lineage. Product commit `1b1fc9f`; Engineering
  Gate `34076883867` and full APK/PWA run `34076883874` passed. Cloud deployment
  was correctly skipped because account credentials are not configured. Preserve
  `v11.6-content-quality` as the immutable accepted checkpoint.
- Root `AGENTS.md` placement is correct, but no filename can force every unknown
  harness to load it. Thin common-harness adapters and
  `tools/verify_project_memory.py` reduce discovery and drift risk.
- Large binaries (three PDFs, ~420 PNGs, ~6 MB source app) make full clones slow;
  prefer targeted inspection or partial clones when appropriate.
- Source visual and protected session/review infrastructure must not be changed
  casually during unrelated work.

## FSRS status — accepted functional milestone

- The source app contains the build-time-installed FSRS v6 scheduler using vendored `ts-fsrs` 5.4.2 (MIT), deterministic fuzz-off scheduling, schema-v2 card state, immutable rated attempts, migration backup/due-date preservation, all-subject daily queue, rating controls, forecast, settings, and undo.
- The new APK was installed and confirmed working by the user. The website/PWA was also opened and confirmed functional. Treat FSRS as build-verified and device/user-verified in both targets; do not describe it as pending acceptance.
- The detailed behavior and invariants are documented in `docs/FSRS.md`.

## Known problems / immediate next step

- User confirmed Android synchronization succeeds on 2026-09-07. Stop the historical 403 investigation. Finish the pending PWA update UI/reliability improvements and Termux/CI verification; preserve accepted FSRS behavior.
- Next: preserve the accepted FSRS behavior while completing the separate Android↔PWA synchronization verification. V11.6 remains the rollback checkpoint for unrelated V11.7 deployment work.

<!-- V11.7_DEPLOYMENT_HANDOFF_2026-09-07 -->
## V11.7 deployment handoff — 2026-09-07

- Active candidate: `v11.7-cross-device-pwa-sync`. Physically accepted rollback baseline remains **V11.6 Content Quality** at `125d68b`; do not call V11.7 accepted until Android migration and Android↔iPad sync pass on real devices.
- Firebase/Firestore is configured and builds now report `QBANK_RUNTIME_CONFIG_OK firebase=configured`. Exact GitHub Variables: `QBANK_FIREBASE_API_KEY`, `QBANK_FIREBASE_PROJECT_ID`, `QBANK_ANATOMY_PDF_URL`. Firestore user-scoped rules and the intentionally empty composite-index set are deployed.
- Cloudflare Pages project: `nk-qbank`. Exact GitHub Secrets: `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`. Push builds create preview deployments. A manual **Build V11.7 Android + PWA** dispatch now also promotes the same artifact to production so `nk-qbank.pages.dev` is updated deliberately.
- Anatomy source PDF uses the configured public R2 object URL because it is ~46 MiB; Biochemistry and Physiology PDFs ship inside `build/web`.
- Physical iPad testing found and fixed two browser runtime bugs: `278b6c5` fixed the blank-screen sync bootstrap (`nkAuth` initialization timing); `7b047e5` fixed PDF.js canvas creation by avoiding a local `document` name that shadowed the DOM document.
- Latest hashed preview opens successfully on iPad. Before the production-promotion workflow change, the root `nk-qbank.pages.dev` still served the older blank production deployment. Source-PDF rendering, Anatomy/R2 CORS, final production URL, Android in-place upgrade, and full two-way sync still require physical verification.
- Next: wait for CI on the current branch → manually dispatch **Build V11.7 Android + PWA** once → verify `https://nk-qbank.pages.dev` → add final Pages hostname to Firebase Authentication authorized domains → ensure R2 CORS allows the exact Pages origin and Range GETs → install V11.7 APK over V11.6 without uninstalling → verify old local data → same-account Android/iPad sync, offline/reconnect, force-close/reopen, sign-out/in tests.

## 2026-09-07 sync diagnostics
- Physical Android+iPad test showed Sync now flashing "Sync paused" and then remaining visually stuck on "Synchronizing…" with no state transfer.
- Root cause of the stuck label is confirmed in `tools/cross_device_sync_core.js`: the error render happened while `nkCloudBusy` was still true and `finally` cleared the flag without a final render. Initial auth also treated a failed first sync as success because `nkCloudSync(true)` returned false without being rethrown.
- Commit `6cd5322` fixes those control-flow defects and surfaces the actual Firebase/Firestore error text in the Sync card/toast. This is diagnostic plus correctness hardening; the underlying backend failure still needs one fresh physical test to reveal its exact message before calling sync working.

## 2026-09-07 Firestore request-failure hardening
- Fresh physical Android + PWA test after `6cd5322` no longer hangs, but both devices report a generic Firestore `Request failed` and no data transfers.
- The sync client now resolves the real Firebase project ID from the public Identity Toolkit project-config endpoint before Firestore access, so a display-name/stale `QBANK_FIREBASE_PROJECT_ID` cannot silently point REST calls at the wrong project.
- Errors are now stage-labeled (`Firebase project`, `authentication`, `download`, `upload`) and include HTTP status. This change still requires a fresh Android/PWA build-and-test before sync can be declared working.


## 2026-09-07 sync 404 root cause and fix
- Production runtime config used `nk_qbank`; Firebase's project-config endpoint then returned numeric project number `174056010089`. Neither is the Firestore database project ID, so downloads returned HTTP 404. The authoritative project ID is `nk-qbank`.
- GitHub Actions variable `QBANK_FIREBASE_PROJECT_ID` is corrected to `nk-qbank`. The client now refreshes authentication first and derives the project ID from the ID token's `aud`/`iss` claims, preventing stale config or numeric project-number regressions.
- Targeted local checks and Engineering Gate `34095662853` passed. Manual production run `34095870813` built the APK/PWA artifact and promoted it successfully; live Pages serves `projectId: "nk-qbank"` and the token-based resolver. A physical two-device sync test remains required before V11.7 is device-verified.


## 2026-09-07 Firestore upload fix and auto-sync
- Physical testing confirmed project-routing downloads work but the client upload through REST `:batchWrite` returns `Missing or insufficient permissions`. An authenticated production probe proved identical owner-scoped data succeeds through document PATCH under the strict checked-in rules.
- Upload now uses bounded parallel PATCH requests. Strict rules were re-deployed to `nk-qbank`, compiled successfully, and passed an authenticated write probe; disposable probe accounts/data were removed. The client also retries silently every five minutes, on foreground, and on reconnect, in addition to debounced sync after saves and manual Sync now. Full build and production promotion run `34100302605` passed; live code contains PATCH, no batchWrite, and the five-minute timer. Physical two-device verification remains.


## 2026-09-07 resumed sync implementation (local candidate)

- Preserved the five integrated commits and prior FSRS acceptance documentation.
- PWA installation now waits for explicit Update; controller changes reload only
  after that action, once per page. Previously install called skipWaiting itself.
- Upload acknowledgments retain newer local edits; partial batches settle before
  retry. Downloads reconcile all revisions so late offline uploads cannot fall
  behind a cursor based on client timestamps (increased reads are the tradeoff).
- HTTP diagnostics retain backend reason codes and upload collection/method.
  User subsequently confirmed Android sync succeeds; the 403 investigation is closed at their request.
- Local sync/PWA lifecycle, FSRS, metrics, modules, content, source and pipeline
  checks pass. Termux PDF generation is intentionally CI-only; do not install or
  compile PyMuPDF locally. Run `python3 tools/verify_local.py` (27 applicable
  checks pass). Five generated-artifact checks are explicitly deferred to CI.
- Added Android/Termux preflight guards and strict Ubuntu CI PDF dependency
  validation. Full verification of this candidate is pending its Linux CI run.
- Sync error details now expose the full backend reason and failed download
  collection. Android sync is user-confirmed successful. Push the pending UI and
  reliability changes and verify full CI; broader two-device acceptance is separate.
