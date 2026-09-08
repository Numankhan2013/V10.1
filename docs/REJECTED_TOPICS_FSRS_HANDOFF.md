# Rejected Topics/FSRS release — 2026-09-08

## User verdict and next-session priority

User explicitly rejected the deployed Topics/FSRS candidate: Topics looks unlike the supplied reference; overall UI feels unchanged; Continue Learning requires scrolling to the bottom; FSRS customization is bare minimum; explanation PDFs have become severely degraded/unreadable. Prior build/browser success is NOT visual or user acceptance. Treat PDF readability as priority zero. User has limited usage: this session is diagnosis and memory only, no speculative repair or deployment.

## Confirmed implementation causes

- tools/apply_whole_app_vision_v1.py appends Continue Learning AFTER the whole topic list and sets position:sticky; bottom:82px. This is not a viewport-fixed dock available immediately. It is also conditional on finding a resume chapter. Next implementation must reserve content space and keep the tray visible above navigation from first render, with responsive/safe-area handling.
- Topics retains the old nkAppPageHead, subject switch, compact typography, filter treatment, and overall shell. Changes were narrow row styling, not faithful reference reconstruction. The milestones sit inside the card grid instead of a distinct left journey lane; the connector is a straight 2px repeating-linear-gradient, not a curved dashed path. Milestone shadow is a canvas-colored ring and card shadows are faint; the intended lavender/blue/green luminous treatment is missing. Source reference: docs/ui-reference/topics-page-reference.jpg.
- tools/fsrs_scheduler_core.js renders customization as details/summary embedded in More, not a dedicated destination. tools/apply_fsrs_v1.py adds only minimal styles. Explicit Save works but does not satisfy the requested professional section. Next: More entry -> its own settings page, draft values, validation, Save/Cancel, understandable control descriptions, coherent visual hierarchy and theme.
- Previous Topics rewrite removed matching-question search results and the started summary, lacks an index/list affordance, and uses coarse ID ranges rather than a fully reviewed taxonomy. Restore useful existing behavior while matching the reference.
- Prior browser tests checked counts, text markers, Back route, and persistence; they did not assert first-viewport tray visibility, fidelity against the reference, glow, or PDF legibility. A passing screenshot capture is not a visual comparison. Do not call this release accepted or finished.

## PDF regression: observed by user, cause NOT established

- git diff 5a7287b..6ba7ebe shows no direct changes to web_pdf_renderer.mjs, native PDF renderer, or source PDF assets. That does not rule out generated-app CSS, packaging, source mapping, or runtime regressions.
- Existing browser renderer app/src/main/assets/web_pdf_renderer.mjs computes scale from displayed width, caps devicePixelRatio at 2, and zooms a JPEG (.94) copied from that same canvas. No high-resolution rerender on zoom/resize. These are confirmed quality limitations, NOT proof of the newly reported failure.
- Also inspect crop coordinates (top/bottom), measured width, canvas sizing, load/render errors, source PDF requests/R2, and native-vs-browser path selection. Need identify affected subject/question and Android versus PWA from next-session evidence; do not assume which target is broken.
- Compare the SAME PDF explanation and zoom state on the last user-accepted deployment/APK versus rejected candidate. Restore readable source rendering first, preserve source fidelity and fixed FSRS recall dock.

## Deployment and continuity

Rejected product commit 6ba7ebe; docs follow-up 0d19004. Local branch codex/topics-depth tracks origin/feature/marrow-bank-pilot. Full build 34203639327 and Engineering Gate 34203639427 passed; feature deployment https://7023d1b5.nk-qbank.pages.dev (alias https://feature-marrow-bank-pilot.nk-qbank.pages.dev); APK artifact 10046898472. Production root was not promoted. V11.6 125d68b remains accepted rollback checkpoint, but select the last user-accepted PDF build rather than assuming that is the right comparison for PWA.

Correct navigation intent: back through parent layers (Analysis -> Topics for topic-launched study), not a universal Home redirect. Previous assistant initially implemented the opposite and then corrected the immediate result boundary; broader origin/bank/subject/history preservation still needs review.
