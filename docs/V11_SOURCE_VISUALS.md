# V11 Source Visuals

## Contract
Every question and option may independently declare an optional `visual` object. The renderer must consume metadata, never question-number heuristics.

```js
visual: {
  type: "source-pdf",
  source: "Anatomy_QBank_Source.pdf",
  page: 1852,
  crop: { left: 0, top: 0, right: 612, bottom: 792 },
  fit: "contain"
}
```

`crop` is optional and expressed in source-PDF points. `fit` is `contain`, `width`, or `native`.

## Interaction requirements
- high-resolution source rendering
- aspect-ratio preserving
- bounded pan
- focal-point pinch zoom
- double-tap zoom
- zoom +/-
- reset-to-fit
- no image loss beyond recoverable bounds
- image gestures must not fight question/page scrolling
- full-screen viewer for detailed anatomy/histology inspection

## Regeneration and audit policy

- Preserve stable question IDs and existing question ownership. The generated
  runtime metadata also records `questionId` and a stable visual `auditId`.
- Copy opaque native JPEG streams byte-for-byte. Preserve every pixel of other
  native rasters and use lossless PNG with a proportional safety canvas.
- Render graphs/plots from the complete detected PDF figure placement at 288
  DPI so vector axes and labels layered over an embedded raster are retained.
  Add a 72-pixel lossless safety canvas after rendering instead of sweeping
  surrounding question prose into the source crop.
- Never use background-color tight cropping, a second crop pass, sharpening,
  generative enhancement, inpainting, or reconstruction.
- `source_visual_inventory.json` records subject, PDF page, xref, source
  placement/comparison crop, extraction method, dimensions, hashes, owning
  question, risk flags and review state for every visual.
- `improve_source_visual_assets_v1.py` is retained as the ordered pipeline name
  but is audit-only. It fails on hash/dimension/aspect errors, unsafe content or
  detected text at a crop boundary, neighboring-question text, or
  answer-revealing source text. It emits high-risk-first comparison sheets in
  batches of eight under `build/prepladder-visual-audit/`.
- Automated technical PASS is not manual certification. Review state remains
  `PENDING_MANUAL_REVIEW` until the source/production sheets are inspected.
  Accepted reviews live in `data/prepladder_visual_reviews.json` and are
  hash/question/page/crop pinned so stale approvals fail closed.
- Browser QA covers graph, table, clinical, diagram and multi-panel examples at
  390x844 and 820x1180, including normal rendering and fullscreen zoom. All
  source-visual assets are included in the offline PWA shell and APK checks.

## Subject isolation
- Anatomy -> Anatomy source PDF
- Biochemistry -> Biochemistry source PDF
- Physiology -> Physiology source PDF

Existing explanation renderers remain isolated unless deliberately migrated.

<!-- V11.7_DEPLOYMENT_HANDOFF_2026-09-07 -->
## V11.7 deployment handoff — 2026-09-07

- Active candidate: `v11.7-cross-device-pwa-sync`. Physically accepted rollback baseline remains **V11.6 Content Quality** at `125d68b`; do not call V11.7 accepted until Android migration and Android↔iPad sync pass on real devices.
- Firebase/Firestore is configured and builds now report `QBANK_RUNTIME_CONFIG_OK firebase=configured`. Exact GitHub Variables: `QBANK_FIREBASE_API_KEY`, `QBANK_FIREBASE_PROJECT_ID`, `QBANK_ANATOMY_PDF_URL`. Firestore user-scoped rules and the intentionally empty composite-index set are deployed.
- Cloudflare Pages project: `nk-qbank`. Exact GitHub Secrets: `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`. Push builds create preview deployments. Manual **Build V11.7 Android + PWA** dispatch now also promotes the same artifact to production so `nk-qbank.pages.dev` is updated deliberately.
- Anatomy source PDF uses the configured public R2 object URL because it is ~46 MiB; Biochemistry and Physiology PDFs ship inside `build/web`.
- Physical iPad testing found and fixed two browser runtime bugs: `278b6c5` fixed the blank-screen sync bootstrap (`nkAuth` initialization timing); `7b047e5` fixed PDF.js canvas creation by avoiding a local `document` name that shadowed the DOM document.
- Latest hashed preview opens successfully on iPad. Before the production-promotion workflow change, the root `nk-qbank.pages.dev` still served the older blank production deployment. Source-PDF rendering, Anatomy/R2 CORS, final production URL, Android in-place upgrade, and full two-way sync still require physical verification.
- Next: wait for CI on the current branch → manually dispatch **Build V11.7 Android + PWA** once → verify `https://nk-qbank.pages.dev` → add final Pages hostname to Firebase Authentication authorized domains → ensure R2 CORS allows the exact Pages origin and Range GETs → install V11.7 APK over V11.6 without uninstalling → verify old local data → same-account Android/iPad sync, offline/reconnect, force-close/reopen, sign-out/in tests.
