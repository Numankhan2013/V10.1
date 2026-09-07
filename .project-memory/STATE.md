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

## Next step

1. User creates/authorizes Firebase, Firestore, Cloudflare Pages, and optional
   R2, then adds the documented GitHub variables/secrets.
2. Rebuild/deploy and run the Android migration plus two-device acceptance
   checklist in `docs/CROSS_DEVICE_PWA.md`.
3. Do not promote V11.7 until Android and iPad synchronization are physically
   verified; V11.6 remains the rollback checkpoint.

<!-- V11.7_DEPLOYMENT_HANDOFF_2026-09-07 -->
## V11.7 deployment handoff — 2026-09-07

- Active candidate: `v11.7-cross-device-pwa-sync`. Physically accepted rollback baseline remains **V11.6 Content Quality** at `125d68b`; do not call V11.7 accepted until Android migration and Android↔iPad sync pass on real devices.
- Firebase/Firestore is configured and builds now report `QBANK_RUNTIME_CONFIG_OK firebase=configured`. Exact GitHub Variables: `QBANK_FIREBASE_API_KEY`, `QBANK_FIREBASE_PROJECT_ID`, `QBANK_ANATOMY_PDF_URL`. Firestore user-scoped rules and the intentionally empty composite-index set are deployed.
- Cloudflare Pages project: `nk-qbank`. Exact GitHub Secrets: `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`. Push builds create preview deployments. A manual **Build V11.7 Android + PWA** dispatch now also promotes the same artifact to production so `nk-qbank.pages.dev` is updated deliberately.
- Anatomy source PDF uses the configured public R2 object URL because it is ~46 MiB; Biochemistry and Physiology PDFs ship inside `build/web`.
- Physical iPad testing found and fixed two browser runtime bugs: `278b6c5` fixed the blank-screen sync bootstrap (`nkAuth` initialization timing); `7b047e5` fixed PDF.js canvas creation by avoiding a local `document` name that shadowed the DOM document.
- Latest hashed preview opens successfully on iPad. Before the production-promotion workflow change, the root `nk-qbank.pages.dev` still served the older blank production deployment. Source-PDF rendering, Anatomy/R2 CORS, final production URL, Android in-place upgrade, and full two-way sync still require physical verification.
- Next: wait for CI on the current branch → manually dispatch **Build V11.7 Android + PWA** once → verify `https://nk-qbank.pages.dev` → add final Pages hostname to Firebase Authentication authorized domains → ensure R2 CORS allows the exact Pages origin and Range GETs → install V11.7 APK over V11.6 without uninstalling → verify old local data → same-account Android/iPad sync, offline/reconnect, force-close/reopen, sign-out/in tests.

