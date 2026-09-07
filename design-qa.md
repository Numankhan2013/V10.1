# V11.4 Whole-App Vision Design QA

## Visual target

The user-selected PrepLadder-inspired dashboard, topics, and analysis references, harmonized with the accepted V11.3.1 Calm Study Canvas question experience. The app should feel compact, medically serious, source-faithful, and phone-native, with one obvious next learning action on each screen.

## Implemented scope

- Shared compact white header and five-tab bottom navigation.
- Home command center with streak, focus actions, accurate subject counts/progress, learning metrics, revision shortcuts, strongest chapters, and recent sessions.
- Subject and Topic navigation with medically recognizable subject icons, search, supported progress filters, accurate completion, and direct chapter entry.
- Chapter overview with Practice/CBT actions, coverage metrics, source-order question library, and attempt states.
- Timed CBT landing page, focused builder modal, scope/topic selection, question count, and test history.
- Practice and CBT result analysis with score, answer distribution, timing, completion, and canonical Review Solutions entry.
- Insights with accuracy, timing, completion, spaced review, chapter coverage, and recent sessions.
- Revision libraries and More reorganized into compact, descriptive lists and reliable empty states.

## Protected behavior

V11.3.1 Practice, CBT question answering, Review Solutions, the anytime navigator, bookmarks, exact source-PDF renderer, source-image handling, offline persistence, test history, and subject-specific datasets are not replaced by this visual layer.

## Automated checks

- Every non-question route has one canonical V11.4 renderer.
- Primary actions retain their existing window.QB behavior.
- Review Solutions retains its canonical entry attributes.
- The V11.3.1 session UI, Review grid contract, and 4x source PDF markers remain present.
- JavaScript syntax, product contracts, CBT invariants, deterministic build ordering, Gradle, packaged APK, and reproducibility checks run in GitHub Actions.

## Blocking visual checks

The Android WebView cannot be visually captured in this environment. Physical-device verification is required at 576px-class phone width for Home, all three subjects, Topics filters/search, a long chapter name, chapter question states, Test builder scrolling, empty and populated histories, Insights, More, Practice analysis, CBT analysis, and bottom safe-area behavior.

Final result: blocked

<!-- V11.7_DEPLOYMENT_HANDOFF_2026-09-07 -->
## V11.7 deployment handoff — 2026-09-07

- Active candidate: `v11.7-cross-device-pwa-sync`. Physically accepted rollback baseline remains **V11.6 Content Quality** at `125d68b`; do not call V11.7 accepted until Android migration and Android↔iPad sync pass on real devices.
- Firebase/Firestore is configured and builds now report `QBANK_RUNTIME_CONFIG_OK firebase=configured`. Exact GitHub Variables: `QBANK_FIREBASE_API_KEY`, `QBANK_FIREBASE_PROJECT_ID`, `QBANK_ANATOMY_PDF_URL`. Firestore user-scoped rules and the intentionally empty composite-index set are deployed.
- Cloudflare Pages project: `nk-qbank`. Exact GitHub Secrets: `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`. Push builds create preview deployments. Manual **Build V11.7 Android + PWA** dispatch now also promotes the same artifact to production so `nk-qbank.pages.dev` is updated deliberately.
- Anatomy source PDF uses the configured public R2 object URL because it is ~46 MiB; Biochemistry and Physiology PDFs ship inside `build/web`.
- Physical iPad testing found and fixed two browser runtime bugs: `278b6c5` fixed the blank-screen sync bootstrap (`nkAuth` initialization timing); `7b047e5` fixed PDF.js canvas creation by avoiding a local `document` name that shadowed the DOM document.
- Latest hashed preview opens successfully on iPad. Before the production-promotion workflow change, the root `nk-qbank.pages.dev` still served the older blank production deployment. Source-PDF rendering, Anatomy/R2 CORS, final production URL, Android in-place upgrade, and full two-way sync still require physical verification.
- Next: wait for CI on the current branch → manually dispatch **Build V11.7 Android + PWA** once → verify `https://nk-qbank.pages.dev` → add final Pages hostname to Firebase Authentication authorized domains → ensure R2 CORS allows the exact Pages origin and Range GETs → install V11.7 APK over V11.6 without uninstalling → verify old local data → same-account Android/iPad sync, offline/reconnect, force-close/reopen, sign-out/in tests.

