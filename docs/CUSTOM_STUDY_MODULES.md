# Custom Study Modules

Custom Study Modules turn existing subjects, topics, question history, bookmarks,
practice, review, and Insights into reusable focused study sets.

## Model and persistence

Modules live in the existing `qbank_state_v1` localStorage document under
`studyModules`. A module stores its subject/topic filters, pool type, frozen
question ID list, answers, submitted IDs, timing, current position, lifecycle
timestamps, completion state, and optional result-session ID.

The selected question IDs are frozen when the module is created. Changes to a
question's Wrong, Unattempted, or Bookmarked status never rebuild an existing
module. Missing IDs are skipped safely when a module resumes.

## Selection rules

1. Reuse `SUBJECTS`, each subject's existing topics, and the unified question map.
2. Filter by selected subject and topic IDs.
3. Apply Unattempted, Wrong, Bookmarked, or Mixed eligibility.
4. Deduplicate by canonical question ID.
5. Use a seeded shuffle so selection is maintainable and testable.
6. In Mixed mode, draw with a Wrong/Wrong/Unattempted/Wrong/Unattempted/Bookmarked
   weighting, then fill from remaining eligible questions.
7. Cap the created set at the actual eligible count and persist those IDs.

## Session integration

Modules create a normal Practice session with a `studyModuleId`. Existing answer,
explanation, source-PDF, navigator, Review Solutions, attempt-history, review,
and Insights paths remain authoritative. Every save synchronizes the active
session snapshot back into its module.

Finishing creates a normal Practice Analysis record linked to the module. Leaving
an unfinished module saves progress and returns Home. Restart clears module-local
progress but deliberately preserves the frozen question set and global attempt
history.

## Build ownership

`tools/apply_custom_study_modules_v1.py` runs after the V11.4 whole-app transform
and before final WebView syntax validation. `tools/test_custom_study_modules_v1.py`
covers eligibility, count contraction, deduplication, stable IDs, persistence,
resume progress, and Home prioritization.

<!-- V11.7_DEPLOYMENT_HANDOFF_2026-09-07 -->
## V11.7 deployment handoff — 2026-09-07

- Active candidate: `v11.7-cross-device-pwa-sync`. Physically accepted rollback baseline remains **V11.6 Content Quality** at `125d68b`; do not call V11.7 accepted until Android migration and Android↔iPad sync pass on real devices.
- Firebase/Firestore is configured and builds now report `QBANK_RUNTIME_CONFIG_OK firebase=configured`. Exact GitHub Variables: `QBANK_FIREBASE_API_KEY`, `QBANK_FIREBASE_PROJECT_ID`, `QBANK_ANATOMY_PDF_URL`. Firestore user-scoped rules and the intentionally empty composite-index set are deployed.
- Cloudflare Pages project: `nk-qbank`. Exact GitHub Secrets: `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`. Push builds create preview deployments. Manual **Build V11.7 Android + PWA** dispatch now also promotes the same artifact to production so `nk-qbank.pages.dev` is updated deliberately.
- Anatomy source PDF uses the configured public R2 object URL because it is ~46 MiB; Biochemistry and Physiology PDFs ship inside `build/web`.
- Physical iPad testing found and fixed two browser runtime bugs: `278b6c5` fixed the blank-screen sync bootstrap (`nkAuth` initialization timing); `7b047e5` fixed PDF.js canvas creation by avoiding a local `document` name that shadowed the DOM document.
- Latest hashed preview opens successfully on iPad. Before the production-promotion workflow change, the root `nk-qbank.pages.dev` still served the older blank production deployment. Source-PDF rendering, Anatomy/R2 CORS, final production URL, Android in-place upgrade, and full two-way sync still require physical verification.
- Next: wait for CI on the current branch → manually dispatch **Build V11.7 Android + PWA** once → verify `https://nk-qbank.pages.dev` → add final Pages hostname to Firebase Authentication authorized domains → ensure R2 CORS allows the exact Pages origin and Range GETs → install V11.7 APK over V11.6 without uninstalling → verify old local data → same-account Android/iPad sync, offline/reconnect, force-close/reopen, sign-out/in tests.

