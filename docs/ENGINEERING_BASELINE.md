# NK QBank engineering baseline

## Canonical product

- Repository: `Numankhan2013/V10.1`
- Physically accepted product: V11.5 Custom Study Modules
- Accepted product commit: `125d68b`
- Accepted lineage: `v11.5-custom-study-modules`
- Current production PWA release: `d43da3dbdaa639214d676b333152654568fe5ba9` (run `36325843382`). `https://nk-qbank.pages.dev` now serves the same build as the `main` alias.

V11.6 remains the recorded physically accepted Android baseline. Passing CI means a candidate is build-verified. PWA production publication can proceed after full CI and explicit user authorization; that does not change the physically accepted Android baseline, which still requires device testing.

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
8. Verify/package the generated PWA and publish its complete SHA-256 file manifest.
9. Build/inspect/publish an APK and its manifest only when explicitly requested (`build_apk=true`); existing APKs remain available.
10. Promote the PWA only after full CI and explicit user authorization. Promote the accepted Android baseline only after physical-device acceptance.

## Candidate states

- **Implemented:** source changes exist.
- **Build-verified (web):** source CI, generated-app/browser, media/offline and packaged-PWA checks pass. Android verification is separately reported only when requested.
- **Device-verified:** installed and tested on the physical Android device.
- **Accepted baseline:** device-verified and explicitly approved.

These labels must never be treated as interchangeable.

## Architecture direction

The existing WebView application remains the production architecture. Scalability work should progressively isolate persistence, question rendering, review, analytics, and design tokens without a big-bang rewrite.

<!-- V11.7_DEPLOYMENT_HANDOFF_2026-09-07 -->
## V11.7 deployment handoff — 2026-09-07

- Active candidate: `v11.7-cross-device-pwa-sync`. Physically accepted rollback baseline remains **V11.6 Content Quality** at `125d68b`; do not call V11.7 accepted until Android migration and Android↔iPad sync pass on real devices.
- Firebase/Firestore is configured and builds now report `QBANK_RUNTIME_CONFIG_OK firebase=configured`. Exact GitHub Variables: `QBANK_FIREBASE_API_KEY`, `QBANK_FIREBASE_PROJECT_ID`, `QBANK_ANATOMY_PDF_URL`. Firestore user-scoped rules and the intentionally empty composite-index set are deployed.
- Cloudflare Pages project: `nk-qbank`; canonical root: `https://nk-qbank.pages.dev`. The production release workflow sets the Direct Upload project production branch to `main` before upload. Release `d43da3dbdaa639214d676b333152654568fe5ba9` was promoted in run `36325843382`; root, `main.nk-qbank.pages.dev`, and preview `https://37799f47.nk-qbank.pages.dev` serve byte-identical builds (HTTP 200).
- Anatomy source PDF uses the configured public R2 object URL because it is ~46 MiB; Biochemistry and Physiology PDFs ship inside `build/web`.
- Physical iPad testing found and fixed two browser runtime bugs: `278b6c5` fixed the blank-screen sync bootstrap (`nkAuth` initialization timing); `7b047e5` fixed PDF.js canvas creation by avoiding a local `document` name that shadowed the DOM document.
- Latest hashed preview opens successfully on iPad. Before the production-promotion workflow change, the root `nk-qbank.pages.dev` still served the older blank production deployment. Source-PDF rendering, Anatomy/R2 CORS, final production URL, Android in-place upgrade, and full two-way sync still require physical verification.
- Remaining physical checks: install the current APK over the existing Android install without uninstalling; verify local data preservation and same-account Android/iPad sync, offline/reconnect, force-close/reopen, and sign-out/in behavior. PWA production root is current.

