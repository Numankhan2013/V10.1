# Study clarity milestone — 2026-09-06

## Baseline
The user reported that the newly built engineering-foundation APK works like the accepted app. GitHub confirms APK run 233 at commit 43648bfff660b5929b5903a65e5552a9d3654920 succeeded. No new physical-device testing by the assistant is claimed.

## Current screenshot findings
The ten user-provided screenshots were inspected, not a live interaction audit.
- Home: NaN subject question/topic counts. Confirmed source cause: arrays passed to numeric formatter.
- Home: subject progress checked state.answers, whereas the canonical attempt history is state.attempts. Active QUESTIONS only contains the selected subject.
- Topics: completion calculation was conditional on accuracy; attempted-but-all-wrong chapters incorrectly showed 0% completion.
- Practice: justified-looking stem spacing and heavy text; preserve original wording and source renderers in a later narrowly scoped readability pass.
- Exam builder: scope headings run into descriptions.
- Topics: both dropdown and tabs repeat completion filters.
- Tests: New Test and Start timed CBT compete for the same main action.
- Insights: unattempted chapters appear as 0% accuracy; later distinguish no evidence from poor performance.
- More: sparse cards use considerable vertical space.
- Review/answer screen: preserve existing feedback, navigator and fixed footer. Screenshots do not prove keyboard, screen reader, zoom or timing behavior.

## This candidate
Only Home subject counts/progress and Topics completion are changed, in their existing owning scripts. No additional runtime patch, renderer replacement, navigation change, answer-key change or storage migration.
Executable tests run the real dashboard template in Node using synthetic fixtures, checking all subjects, empty data, unique attempts, wrong-only attempts, progress bounds and read-only behavior.

## Design direction
Use the current compact question-first layout. Improve readable left-aligned stems, hierarchy, consistent button treatment and meaningful empty states before introducing additional features. Retain source images and existing navigation.

Official reference research:
- https://www.prepladder.com/neet-pg-study-material/notifications/game-changing-qbank-4-0-is-live
- https://www.marrow.com/how-to-use-qbank-document
These support topic practice, custom modules, bookmarks and revision workflows. They are not evidence of the competitors' current mobile UI or a basis for copying medical content.

## Next milestones
1. Question readability and exam-dialog spacing, with matched before/after screenshots.
2. Explicit accuracy versus completion labels and empty-state handling.
3. Study-data backup/restore and schema validation, after inspecting the actual persistence implementation.
4. Reusable custom-module presets and clear revision queues.
Never call static marker checks regression-proof; behavioral and visual coverage remains incomplete.

<!-- V11.7_DEPLOYMENT_HANDOFF_2026-09-07 -->
## V11.7 deployment handoff — 2026-09-07

- Active candidate: `v11.7-cross-device-pwa-sync`. Physically accepted rollback baseline remains **V11.6 Content Quality** at `125d68b`; do not call V11.7 accepted until Android migration and Android↔iPad sync pass on real devices.
- Firebase/Firestore is configured and builds now report `QBANK_RUNTIME_CONFIG_OK firebase=configured`. Exact GitHub Variables: `QBANK_FIREBASE_API_KEY`, `QBANK_FIREBASE_PROJECT_ID`, `QBANK_ANATOMY_PDF_URL`. Firestore user-scoped rules and the intentionally empty composite-index set are deployed.
- Cloudflare Pages project: `nk-qbank`. Exact GitHub Secrets: `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`. Push builds create preview deployments. Manual **Build V11.7 Android + PWA** dispatch now also promotes the same artifact to production so `nk-qbank.pages.dev` is updated deliberately.
- Anatomy source PDF uses the configured public R2 object URL because it is ~46 MiB; Biochemistry and Physiology PDFs ship inside `build/web`.
- Physical iPad testing found and fixed two browser runtime bugs: `278b6c5` fixed the blank-screen sync bootstrap (`nkAuth` initialization timing); `7b047e5` fixed PDF.js canvas creation by avoiding a local `document` name that shadowed the DOM document.
- Latest hashed preview opens successfully on iPad. Before the production-promotion workflow change, the root `nk-qbank.pages.dev` still served the older blank production deployment. Source-PDF rendering, Anatomy/R2 CORS, final production URL, Android in-place upgrade, and full two-way sync still require physical verification.
- Next: wait for CI on the current branch → manually dispatch **Build V11.7 Android + PWA** once → verify `https://nk-qbank.pages.dev` → add final Pages hostname to Firebase Authentication authorized domains → ensure R2 CORS allows the exact Pages origin and Range GETs → install V11.7 APK over V11.6 without uninstalling → verify old local data → same-account Android/iPad sync, offline/reconnect, force-close/reopen, sign-out/in tests.

