# PrepLadder Visual Verification — 2026-09-16

## Verified checkpoint

- Product code: `2340bd201fabcc05e6d45932c7f8e5fa451e14f0` on `feature/marrow-canonical-full-current`.
- Exact-head Engineering: `35053564204` — success.
- Exact-head Android/PWA/browser/APK/package run: `35053564213` — success.
- Cloudflare Pages preview deployment succeeded.
- Production promotion was intentionally skipped. Production was not changed.

## Defect resolved

The final browser failure was not a bad crop. The multi-panel representative was Anatomy `anatomy-9-1`, a matching question with four source figures. Shared question presentation rewrites matching questions into a semantic table under `.nk-v114-session`; the source-visual renderer previously enabled stable-question-ID lookup only under `.nk-v113-question`, so it fell back to exact normalized visible-text matching after the stem had been rewritten and failed to attach the grouped visuals.

The renderer now resolves stable visual ownership from the active session question ID under either `.nk-v113-question` or `.nk-v114-session`, while retaining normalized-text fallback for other surfaces.

## Browser regression contract

`tools/verify_prepladder_visuals_browser.py` now exercises risk-selected representatives for:

- graph / plot / waveform,
- table / flowchart,
- diagnostic / clinical image,
- diagram / illustration,
- multi-panel / multiple figures.

Each category is exercised at phone `390×844` and tablet `820×1180`. The verifier requires:

- the expected stable active question ID,
- a loaded source image with useful native dimensions,
- readable rendered size,
- preserved aspect ratio,
- a real attached viewer with visible backdrop and panel,
- fullscreen backdrop coverage of at least 95% of the viewport,
- a loaded fullscreen image,
- zoom changing the image transform.

The multi-panel representative additionally must mount at least two source images and wait for all grouped images to load. `anatomy-9-1` currently supplies four grouped source figures.

## Packaging result

Full run `35053564213` passed the browser suite and continued through:

- image-comparison capture,
- JDK/Gradle setup,
- side-by-side Marrow pilot APK configuration,
- debug APK build,
- production Android source-identity restoration,
- packaged APK verification,
- packaged product contract,
- reproducibility manifest,
- packaged Marrow image-byte verification,
- artifact upload,
- Cloudflare Pages preview deployment.

Run artifacts include:

- `V11.7-android-pwa` — artifact `10430051035`,
- `prepladder-visual-audit-2340bd201fabcc05e6d45932c7f8e5fa451e14f0` — artifact `10429946824`,
- `recall-dock-and-marrow-pilot-screenshots` — artifact `10430045424`.

## Remaining certification work

The generated source-visual technical audit contains **422 total entries**, all currently `PENDING_MANUAL_REVIEW`. Technical generation, runtime mounting, browser interaction, APK/package validation and preview deployment are green, but source-visual release certification is **not complete** until those bounded source-comparison items receive manual review/acceptance.

Do not reopen the verified stable-ID/browser path merely because manual certification remains. The next PrepLadder visual task is manual audit review unless new runtime evidence shows a regression.
