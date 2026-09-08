# NK QBank engineering baseline

## Canonical product

- Repository: `Numankhan2013/V10.1`
- Physically accepted product: V11.5 Custom Study Modules
- Accepted product commit: `125d68b`
- Accepted lineage: `v11.5-custom-study-modules`
- Current build-verified candidate: `v11.6-content-quality` (`125d68b`)

V11.6 is the behavioral and accepted product baseline. Passing CI means a candidate is build-verified; only a successful physical-device test and explicit user approval can promote it to the accepted baseline.

## Protected product contract

The following must not regress during unrelated work:

- offline Android WebView operation
- one persistent application navigation system
- Practice and Timed CBT
- session review and unanswered-question navigation
- Review Solutions, Previous/Next, question grid, and End Review
- local study-state persistence
- Home, Topics, Tests, Insights, More, and subject switching
- source-faithful Biochemistry, Physiology, and Anatomy rendering
- full-screen source visuals with zoom and pan
- compact mobile information density

## Change policy

1. Start from the latest physically accepted lineage.
2. Make one narrow product change per milestone.
3. Do not replace the application shell or add a second navigation system.
4. Do not globally rewrite subject renderers.
5. Run source contract checks before transformation.
6. Run generated-app checks after every transformation.
7. Validate JavaScript after the final transformation.
8. Build and inspect the packaged APK.
9. Publish the APK together with its SHA-256 build manifest.
10. Promote a build only after physical-device acceptance.

## Candidate states

- **Implemented:** source changes exist.
- **Build-verified:** CI, generated-app, and packaged-APK checks pass.
- **Device-verified:** installed and tested on the physical Android device.
- **Accepted baseline:** device-verified and explicitly approved.

These labels must never be treated as interchangeable.

## Architecture direction

The existing WebView application remains the production architecture. Scalability work should progressively isolate persistence, question rendering, review, analytics, and design tokens without a big-bang rewrite.

<!-- V11.7_DEPLOYMENT_HANDOFF_2026-09-07 -->
## V11.7 deployment handoff — 2026-09-07

- Active candidate: `v11.7-cross-device-pwa-sync`. Physically accepted rollback baseline remains **V11.6 Content Quality** at `125d68b`; do not call V11.7 accepted until Android migration and Android↔iPad sync pass on real devices.
- Firebase/Firestore is configured and builds now report `QBANK_RUNTIME_CONFIG_OK firebase=configured`. Exact GitHub Variables: `QBANK_FIREBASE_API_KEY`, `QBANK_FIREBASE_PROJECT_ID`, `QBANK_ANATOMY_PDF_URL`. Firestore user-scoped rules and the intentionally empty composite-index set are deployed.
- Cloudflare Pages project: `nk-qbank`. Exact GitHub Secrets: `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`. Push builds create preview deployments. Manual **Build V11.7 Android + PWA** dispatch now also promotes the same artifact to production so `nk-qbank.pages.dev` is updated deliberately.
- Anatomy source PDF uses the configured public R2 object URL because it is ~46 MiB; Biochemistry and Physiology PDFs ship inside `build/web`.
- Physical iPad testing found and fixed two browser runtime bugs: `278b6c5` fixed the blank-screen sync bootstrap (`nkAuth` initialization timing); `7b047e5` fixed PDF.js canvas creation by avoiding a local `document` name that shadowed the DOM document.
- Latest hashed preview opens successfully on iPad. Before the production-promotion workflow change, the root `nk-qbank.pages.dev` still served the older blank production deployment. Source-PDF rendering, Anatomy/R2 CORS, final production URL, Android in-place upgrade, and full two-way sync still require physical verification.
- Next: wait for CI on the current branch → manually dispatch **Build V11.7 Android + PWA** once → verify `https://nk-qbank.pages.dev` → add final Pages hostname to Firebase Authentication authorized domains → ensure R2 CORS allows the exact Pages origin and Range GETs → install V11.7 APK over V11.6 without uninstalling → verify old local data → same-account Android/iPad sync, offline/reconnect, force-close/reopen, sign-out/in tests.

