# NK QBank engineering baseline

## Canonical product

- Repository: `Numankhan2013/V10.1`
- Physically accepted product: V11.5 Custom Study Modules
- Accepted product commit: `f13d12f`
- Accepted lineage: `v11.5-custom-study-modules`
- Current build-verified candidate: `v11.6-content-quality` (`125d68b`)

V11.5 is the behavioral and accepted product baseline. Passing CI means a candidate is build-verified; only a successful physical-device test and explicit user approval can promote it to the accepted baseline.

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
