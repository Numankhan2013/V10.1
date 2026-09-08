# SESSION_LOG.md — Chronological Record of Substantial Sessions

Append new entries at the bottom. Keep each entry factual: branch/commit,
CI runs, what changed, verification, device status, next step.
`STATE.md` stays current; this file accumulates.

## 2026-09-06 — Run 220 accepted baseline (background)

- Branch `v11-source-visuals`, commit `73c04281696137fda712ae0b9b7079c9c4a15635`,
  run `34011265432` (`Build Home three-action refinement`) success.
- User physically tested and confirmed working; declared core features done,
  no regression. All later work builds forward from here.
- See `memory.md` §2 for the confirmed working-areas list.

## 2026-09-06 — V11.1 engineering foundation → V11.2 study clarity →
## V11.3 question experience → V11.4 whole-app vision (background)

- Hardening branches `v11.1-engineering-foundation`,
  `v11.2-study-clarity`, `v11.3-question-experience`,
  `v11.4-whole-app-vision` added deterministic transforms + tests without
  replacing the V10.3.11 question-first shell.
- V11.2 fixed subject counts/progress (`SUBJECTS.flatMap`, `state.attempts`,
  numeric-safe formatting) with `test_study_metrics.py`.
- V11.3.1 added shared Practice/CBT/Review experience
  (`nk-session-experience-v114`, docked footer, functional grid).
- V11.4 added whole-app visual system (`nk-whole-app-vision-v114`, subject
  identity, streak milestones, all-subject practice, multi-subject CBT).
- Docs added: `docs/ENGINEERING_BASELINE.md`, `docs/STUDY_CLARITY.md`,
  `docs/V11_SOURCE_VISUALS.md`, `design-qa.md` (device checks blocked in CI).

## 2026-09-06 — V11.4 vision test failure and fix (agent session)

- Commits `21c97d0` (permanent Practice-20), `f685aff` + `d0c67a1`
  (streak milestones) removed the conditional `startLibrary('review')` button
  from `tools/apply_whole_app_vision_v1.py`; `test_whole_app_vision_v1.py`
  still required it.
- Failures: Build V10.1 APK `34034905290`, `34034904068`, `34034791899`
  (`Whole-app vision markers missing: ["window.QB.startLibrary('review')"]`);
  Engineering Gate stayed green.
- Fix `9e6abc71eca192808e6fbd70d4127011c6a47ef0`
  (`Restore Due Review action alongside permanent all-subject practice`):
  Today’s Focus keeps permanent Practice-20 and adds conditional
  `Review N Due` (`startLibrary('review')`) when due>0 + 4-column
  `:has(>button:nth-child(4))` CSS with graceful fallback.
- Verification: Build V10.1 APK `34043059869` success (1m48s,
  `WHOLE_APP_VISION_OK`, packaged checks pass); Engineering Gate `34043059872`
  success. User confirmed the new APK works and UI changes are great.

## 2026-09-06 — V11.5 Custom Study Modules (build-verified candidate)

- Branch `v11.5-custom-study-modules` on top of `9e6abc7`.
- `Add persistent Custom Study Modules` + `Label V11.5 APK artifact` → HEAD
  `f13d12ff2708f518a9e6be839477623be5f471c4`.
- Added `tools/apply_custom_study_modules_v1.py`,
  `tools/study_modules_core.js`, `tools/test_custom_study_modules_v1.py`;
  extended `verify_build_pipeline.py` + `verify_product_contract.py`;
  added `docs/CUSTOM_STUDY_MODULES.md`; updated `README.md`, `memory.md`,
  workflow labels.
- CI: Build V10.1 APK `34049523411` (1m41s) + `34049637559` (1m40s) success;
  Engineering Gate `34049523425` + `34049637590` success.
- Status: **build-verified only**; awaiting physical-device test and explicit
  promotion. Do not call accepted baseline yet.

## 2026-09-06 — Harness-agnostic memory system created (this change)

- Added `AGENTS.md` (universal entry, session start/end rules, thin-adapter
  policy) + `.project-memory/` (`STATE`, `ROADMAP`, `DECISIONS`,
  `ARCHITECTURE`, `PRODUCT`, `SESSION_LOG`).
- Preserved `memory.md`, `docs/*`, `design-qa.md`, `README.md` unchanged;
  populated new files from verified repo state (branches, commits, run IDs,
  55 tools, pipeline order, 420 visuals, subject counts).
- No harness-specific duplicates created. Next: fresh-harness reconstruction
  check, then V11.5 device test → R1 question screen.

## 2026-09-06 — V11.5 physically accepted

- User installed the V11.5 Custom Study Modules APK and reported it “works
  beautifully,” with no questions about the feature.
- Promoted `f13d12f` / build `34049637559` from build-verified candidate to the
  accepted product baseline.

## 2026-09-06 — V11.6 content-quality candidate

- Separate branch `v11.6-content-quality`, commit `125d68b`.
- Added comparison/table-aware takeaway extraction and centralized question-stem
  sanitation. Audit: 719 questions, 78 PrepLadder/page-contaminated stems.
- Engineering Gate `34050921166` and full packaged APK build `34050921180`
  passed. Artifact `V11.6-content-quality-debug-apk`; physical acceptance pending.

## 2026-09-07 — Memory reconstruction audit and hardening

- Read all canonical and legacy memory from a fresh agent context and verified
  it against Git/GitHub. Structure and root placement were sound.
- Fixed stale V11.5 acceptance/CI facts and the impossible hardcoded-current-HEAD
  pattern; documented V11.6's separate lineage.
- Added a schema README, thin Claude/Gemini/Cursor/Copilot adapters, and
  `tools/verify_project_memory.py` to enforce placement and low-drift rules.

## 2026-09-07 — V11.6 accepted; V11.7 cross-device implementation started

- User confirmed V11.6 (`125d68b`, full run `34050921180`) was physically
  device-tested and accepted. V11.6 is now the immutable product baseline.
- Created `v11.7-cross-device-pwa-sync` from V11.6 and merged the harness-neutral
  memory lineage at `309aabb`; neither accepted/checkpoint branch was altered.
- Added shared PWA assets, adaptive iPad/tablet layout, service-worker caching,
  browser PDF.js source rendering, Cloudflare artifact/deployment wiring, public
  runtime config generation, Firebase email/password + normalized Firestore sync,
  ownership rules, local outbox/cursors, tombstones, and conflict tests.
- Android now has a deterministic private HTTPS asset-origin transform and a
  one-time bridge that migrates the prior file-origin localStorage before boot.
- Final product commit `1b1fc9f`: Engineering Gate `34076883867` and full
  generated/packaged Android + PWA run `34076883874` passed; artifact
  `V11.7-android-pwa`. Cloud deployment was skipped because no account variables
  or secrets exist. V11.7 is build-verified, not device-verified or accepted.

<!-- V11.7_DEPLOYMENT_HANDOFF_2026-09-07 -->
## V11.7 deployment handoff — 2026-09-07

- Active candidate: `v11.7-cross-device-pwa-sync`. Physically accepted rollback baseline remains **V11.6 Content Quality** at `125d68b`; do not call V11.7 accepted until Android migration and Android↔iPad sync pass on real devices.
- Firebase/Firestore is configured and builds now report `QBANK_RUNTIME_CONFIG_OK firebase=configured`. Exact GitHub Variables: `QBANK_FIREBASE_API_KEY`, `QBANK_FIREBASE_PROJECT_ID`, `QBANK_ANATOMY_PDF_URL`. Firestore user-scoped rules and the intentionally empty composite-index set are deployed.
- Cloudflare Pages project: `nk-qbank`. Exact GitHub Secrets: `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`. Push builds create preview deployments. Manual **Build V11.7 Android + PWA** dispatch now also promotes the same artifact to production so `nk-qbank.pages.dev` is updated deliberately.
- Anatomy source PDF uses the configured public R2 object URL because it is ~46 MiB; Biochemistry and Physiology PDFs ship inside `build/web`.
- Physical iPad testing found and fixed two browser runtime bugs: `278b6c5` fixed the blank-screen sync bootstrap (`nkAuth` initialization timing); `7b047e5` fixed PDF.js canvas creation by avoiding a local `document` name that shadowed the DOM document.
- Latest hashed preview opens successfully on iPad. Before the production-promotion workflow change, the root `nk-qbank.pages.dev` still served the older blank production deployment. Source-PDF rendering, Anatomy/R2 CORS, final production URL, Android in-place upgrade, and full two-way sync still require physical verification.
- Next: wait for CI on the current branch → manually dispatch **Build V11.7 Android + PWA** once → verify `https://nk-qbank.pages.dev` → add final Pages hostname to Firebase Authentication authorized domains → ensure R2 CORS allows the exact Pages origin and Range GETs → install V11.7 APK over V11.6 without uninstalling → verify old local data → same-account Android/iPad sync, offline/reconnect, force-close/reopen, sign-out/in tests.

## 2026-09-07 sync diagnostics
- Physical Android+iPad test showed Sync now flashing "Sync paused" and then remaining visually stuck on "Synchronizing…" with no state transfer.
- Root cause of the stuck label is confirmed in `tools/cross_device_sync_core.js`: the error render happened while `nkCloudBusy` was still true and `finally` cleared the flag without a final render. Initial auth also treated a failed first sync as success because `nkCloudSync(true)` returned false without being rethrown.
- Commit `6cd5322` fixes those control-flow defects and surfaces the actual Firebase/Firestore error text in the Sync card/toast. This is diagnostic plus correctness hardening; the underlying backend failure still needs one fresh physical test to reveal its exact message before calling sync working.

## 2026-09-07 — Firestore request-failure hardening
- User physically tested the diagnostic build on both Android and PWA. Sync no longer stays falsely stuck on “Synchronizing…”, but both targets report `Request failed` and transfer no state.
- Added runtime Firebase project-ID discovery through the public Identity Toolkit project-config endpoint and made Firestore use the discovered ID. This protects against a configured display name/stale project ID while keeping the explicit GitHub variable as fallback.
- Added stage-aware sync errors and HTTP status reporting so the next physical failure identifies whether the problem is project resolution, auth refresh, Firestore download, or upload.


## 2026-09-07 — Fix Firestore download HTTP 404
- Reproduced the deployed configuration and found `QBANK_FIREBASE_PROJECT_ID=nk_qbank`. The prior runtime discovery returned Firebase project number `174056010089`; Firestore returned 404 for that database path. The real Firebase/Firestore project ID is `nk-qbank`.
- Corrected the GitHub Actions variable to `nk-qbank` and changed sync project resolution to use the authenticated ID token's `aud`/`iss` project claim after token refresh.
- Added a regression test for JWT project resolution and updated the PWA sync documentation. Targeted local checks and Engineering Gate `34095662853` passed. Manual run `34095870813` built the APK/PWA artifact and promoted it to Cloudflare production; live Pages serves the corrected config and resolver. Physical Android↔PWA verification remains.


## 2026-09-07 — Fix Firestore upload permissions and add automatic retries
- The post-404 physical test reached Firestore downloads but upload was rejected with `Missing or insufficient permissions`. An authenticated disposable probe reproduced the failure: the REST `:batchWrite` endpoint returned HTTP 403 even with a minimal valid owner-scoped document, while an individual document `PATCH` of the identical fields returned HTTP 200 under the strict checked-in rules.
- Replaced batchWrite uploads with bounded groups of individual PATCH requests. Re-deployed and compilation-verified the strict owner-only/field-validating rules; a second authenticated probe passed, and both disposable Authentication users plus their one generated Firestore document were removed.
- Added silent signed-in synchronization every five minutes, on app foreground, and on reconnection. Existing save-triggered debounced synchronization and manual detailed errors remain.
- Engineering Gate `34100092384`, packaged push build `34100092358`, and manual production-promotion build `34100302605` passed. Live `nk-qbank.pages.dev` was verified to contain document PATCH, the five-minute timer, no batchWrite marker, and project ID `nk-qbank`.


## 2026-09-07 — Implement FSRS smart-review milestone

- Vendored pinned `ts-fsrs` 5.4.2 UMD and MIT license for Android/PWA offline use.
- Added schema-v2 scheduling, migration backup with legacy due preservation,
  deterministic attempt replay, Again/Hard/Good/Easy audit records, pending-Good
  recovery, CBT binary mapping, undo events, and synchronized FSRS preferences.
- Added all-subject Today queue with filters, 150/30 caps and required priority,
  counts, time estimate, seven-day forecast, lapse attention flags, and settings.
- Added pipeline/package contracts and behavior tests. Targeted local checks pass;
  full packaged build and physical upgrade/two-device acceptance remain pending.
- Explicitly paused the separate Android HTTP 403 and PWA refresh-loop sync work.

## 2026-09-07 — Confirm FSRS in APK and website

- User confirmed the new APK works with FSRS enabled and that the website/PWA
  also has functional FSRS review scheduling.
- Promoted FSRS from implemented/pending acceptance to build-verified and
  device/user-verified in project memory and documentation.
- Cross-device Firebase synchronization remains a separate verification item.


## 2026-09-07 — Resume sync after Termux access restored

- Confirmed repository writes work and preserved pre-existing documentation edits.
- Fixed upload acknowledgment races and waited for all concurrent batch requests
  before reporting failure. Failed/newer revisions stay in the outbox.
- Removed timestamp filtering from downloads: device-clock cursors miss late
  offline uploads. Full per-user reconciliation costs more reads but recovers them.
- Removed automatic service-worker skipWaiting during install and limited reload
  to an explicit Update action. Added executable lifecycle regression coverage.
- Added backend reason and upload collection/method diagnostics for the unresolved
  Android HTTP 403. No backend rules or accepted FSRS behavior changed.
- Local behavior and source/pipeline contract checks passed. An isolated generated
  build stopped at final_hardening.py because PyMuPDF (fitz) is unavailable in
  Termux; no physical acceptance or new APK build is claimed.


## 2026-09-07 — Make verification Termux-aware

- User confirmed PyMuPDF generation is CI-only; no installation/build retry made.
- Added source/behavior verification runner, tested Android/Termux detection and
  strict CI preflight, and guarded all three direct PyMuPDF generation entry points.
- Full workflow retains Ubuntu PDF/generated/packaged checks, adds Python/Node
  setup and a mandatory PDF dependency preflight. Pipeline contract enforces it.
- Ran remaining standalone generated-artifact checks against source; they reported
  missing generated UI/mappings as expected. Local runner explicitly defers these
  five checks instead of claiming passes. All 27 applicable local checks passed.
- Added expanded sync error details and collection-level download diagnostics;
  Android 403 is not fixed or reproduced. Requested fresh device error/build text.
- Preserved existing local work. Full CI verification of the candidate is pending;
  existing green runs cover the committed parent, not these working-tree changes.


## 2026-09-07 — Android sync confirmed; finish and push pending improvements

- User confirmed Android synchronization succeeds and explicitly stopped the 403
  investigation. Finish pending update UI, reliability, and verification changes.
- Before that confirmation, an Android-origin disposable-account REST probe passed
  authentication, all six collection queries, and PATCH (HTTP 200). Auth account
  deletion succeeded. One inert preferences tombstone remains under the disposable
  account path; no learner data or rules were changed. No further probing planned.
- Preserve accepted FSRS behavior and all local documentation. Push candidate and
  wait for full Linux CI, including PDF generation and packaged verification.


## 2026-09-07 — Verify pushed update/reliability candidate

- Pushed product commit `9d77dcb` on `v11.7-cross-device-pwa-sync`.
- Engineering Gate `34145834064` and full Android/PWA run `34145834079` passed.
  Linux CI executed PyMuPDF generation, source visual validation, generated UI,
  FSRS and CBT contracts, final JavaScript, Gradle APK, packaged validation and
  artifact upload. Cloudflare preview deployment passed; production was skipped.
- The candidate is build-verified. Its new update UI still needs physical testing;
  the user's successful Android sync confirmation is preserved separately.


## 2026-09-07 — Correct missed FSRS dock and sync feedback loop

- User reported the FSRS UI still did not match the supplied reference and both
  apps flickered during continuous sync. Inspected the JPG and approved dock spec.
- Moved recall markup from question content into the existing fixed practice footer
  immediately before Previous/Next. Added the brain medallion, Rate recall/default
  label, three text-only pills, purple Good, and static diffuse glow. Preserve
  scheduler semantics and hide the dock until a correct answer is submitted.
- Reproduced the sync loop: pulled preferences invoked the local-save hook, which
  scheduled a new sync even with no changed envelopes. Suppress capture only during
  synchronous remote merges, seed received hashes, and schedule only actual edits.
  Update status elements in place; do not reconstruct the page for unchanged syncs.
- Added regression coverage for no echo writes/timers/renders, local edits still
  uploading, pre-answer absence, footer placement, and rating behavior. Added Linux
  browser checks and screenshot artifacts for generated app widths 320/390/768.
- Candidate will be pushed, fully CI-verified, and promoted to production PWA.


## 2026-09-08 — Marrow Anatomy multi-bank pilot accepted on PWA preview

- Created isolated branch `feature/marrow-bank-pilot` from the working V11.7
  baseline; production PWA was not overwritten.
- Added a subject-level bank selector. Anatomy now exposes existing PrepLadder
  (1,068 questions / 50 topics) and Marrow (62 questions / 4 topics) while
  reusing the same Practice, CBT, Review, FSRS, sync, module and analytics
  engines.
- Marrow data is namespaced and hash-verified. The 62-question pilot covers
  Gametogenesis (19), Pre-Embryonic (13), Embryonic (16), and
  Placenta/Fetal Membranes/Twinning (14). Three incomplete-list source defects
  were resolved with provenance: `ANAT_CH02_Q010`, `ANAT_CH03_Q004`,
  `ANAT_CH04_Q013`.
- Marrow explanations use native structured text/tables and preserve the shared
  Key takeaway surface. PrepLadder remains on the source-PDF renderer. Added a
  Marrow-only source-derived takeaway fallback so the support surface never
  disappears when the general heuristic returns empty.
- Added real-browser verification for Anatomy → bank selector → Marrow topic →
  repaired question → answered structured explanation, plus regression back to
  PrepLadder. A case-sensitive `Key takeaway` assertion was corrected after
  the UI correctly rendered `KEY TAKEAWAY`.
- Pilot packaging initially caught two non-product issues: a Gradle
  `applicationId` quote mismatch in the side-by-side APK script and an early
  oversized GitHub data write that was truncated. The final implementation uses
  reversible single-quote-aware Android identity switching and chunked,
  cryptographically verified data transport.
- Final verification: Engineering Gate `34159542431` success; full Android+PWA
  run `34159542436` success; preview deployment
  `https://feature-marrow-bank-pilot.nk-qbank.pages.dev` success; production
  promotion intentionally skipped.
- User opened the preview and reported everything works beautifully. Requested
  future explanation improvement is presentation-only (typing/typography,
  bolding, spacing, structure), not wording changes.
- Added `docs/MARROW_BANK_INTEGRATION.md` and updated canonical memory. Next
  session must generalize the temporary Anatomy-only `MARROW_RECORD` to a
  subject-indexed/general bank registry before importing additional Anatomy,
  Physiology, and Biochemistry Marrow data.


## 2026-09-08 — 20-question Marrow explanation gold-standard pilot

- User approved testing the richer explanation architecture on 20–30 questions
  before scaling and explicitly corrected one architecture point: the FSRS recall
  dock must remain fixed/floating above Previous/Next after answer submission,
  never moved into the explanation flow.
- Selected 20 Anatomy Marrow questions (5 from each of the first four topics) to
  cover short explanations, sequences, mechanisms, long clinical explanations,
  and structured tables.
- Added `data/marrow/explanation_gold_pilot.json` with selective exam-relevant
  emphasis plus 60 concise generated distractor rationales. Generated content is
  stored separately from Marrow source text for auditability/regeneration.
- Enhanced only those 20 questions at render time: stronger typography,
  selective emphasis, preserved source tables, and a **Why the other options are
  wrong** section. The other 42 pilot questions remain unchanged as comparison.
- Added regression/browser checks that the original source table survives and
  that `.nk-fsrs-rating` remains visible inside fixed
  `.nk-session-footer`.
- Engineering Gate `34161682358` and full Android+PWA run `34161682378`
  passed. Browser checks passed, APK packaged, and feature preview deployed:
  `https://feature-marrow-bank-pilot.nk-qbank.pages.dev`
  (immutable `https://ce68af84.nk-qbank.pages.dev`). Production promotion
  intentionally skipped.
- Next: user visually reviews the 20-question pilot; refine the explanation
  grammar before any full-bank rollout.


## 2026-09-08 — Full 62-question Marrow Anatomy explanation rollout

- User physically reviewed the 20-question gold explanation pilot and described
  it as near-perfect. Typography, selective high-yield bolding, source-table
  treatment, and concise wrong-option rationales were accepted for full rollout.
- User requested only a *very, very small* increase in concision. Implemented
  without rewriting the source: the renderer suppresses only a short
  Key-Takeaway-duplicate lead paragraph, short dead image/figure boilerplate
  when no asset is rendered, and legacy source Option A/B/C/D paragraphs that
  are replaced by the standardized concise distractor section.
- Expanded `data/marrow/explanation_gold_pilot.json` from 20 to all 62 current
  Marrow Anatomy questions. The schema-v2 map now carries selective
  exam-discriminator emphasis and 186 generated distractor rationales. Generated
  rationales remain separate from the unchanged Marrow source transcription.
- Existing structured tables remain rendered as real tables. No bulletization
  is forced when paragraph prose is more appropriate.
- Hardened contracts so augmentation IDs exactly equal the 62 Marrow IDs,
  rationale keys equal the three incorrect option letters, rationales stay
  concise, and emphasis stays selective.
- Browser verification checks a question that was outside the original pilot,
  verifies micro-concision on PGC Q1 without losing migration nuance, preserves
  the prenatal-development table, and reasserts that the FSRS dock remains fixed
  above Previous/Next.
- Engineering Gate `34163197757` and full Android+PWA run `34163197772`
  passed. Side-by-side APK packaged and Cloudflare preview deployed:
  `https://feature-marrow-bank-pilot.nk-qbank.pages.dev` (immutable
  `https://bae56103.nk-qbank.pages.dev`). Production promotion was skipped.
- Next: user spot-checks the full rollout. Then generalize the temporary
  Anatomy-only `MARROW_RECORD` to a multi-subject bank registry before adding
  remaining Anatomy, Physiology and Biochemistry Marrow data.


## 2026-09-08 — Generalize Marrow registry and add bounded Physiology pilot

- Replaced the generated Anatomy-only `MARROW_RECORD` special case with the
  subject-indexed `MARROW_RECORDS` / `MARROW_BY_SUBJECT` /
  `BANKS_BY_SUBJECT` registry. Existing bank selection and all shared Practice,
  CBT, Review, FSRS, sync, module, persistence and analytics engines were reused.
- Added static protection against the old singular registry and a real-browser
  public-UI regression test. An initial browser assertion incorrectly called the
  internal `nkBankRecords()` helper from `window`; this was a test-only failure
  and was corrected to verify the learner-visible bank selector instead.
- Registry refactor passed Engineering Gate `34190814897` and full
  Android+PWA/browser/package run `34190814843`.
- Built a bounded Marrow Physiology pilot from verified ED8 JSONL Chapters 1–4:
  80 questions / 4 topics (21, 21, 24, 14). IDs are globally namespaced
  `marrow__PHYS_...`; structured source text/tables/figure metadata and
  provenance are preserved.
- Transport uses 11 compressed/base64 shards with manifest SHA-256 and strict
  length/count/identity validation. Data was added atomically through Git
  objects to avoid the earlier Anatomy oversized-write truncation failure.
- The loader converts the existing Anatomy payload plus Physiology pilot into
  `MARROW_DATA.records` before the generic registry stage. PrepLadder renderers
  and all existing question engines remain unchanged.
- The first extended data test exposed only backward compatibility with the
  older Anatomy manifest, which lacks the newer optional raw/compressed byte
  length fields. Validation now keeps those lengths optional for old manifests
  while retaining mandatory cryptographic hashes.
- Final candidate: Engineering Gate `34191865093` success; full Android+PWA
  run `34191865094` success. Real browser verified Physiology → bank selector
  → Marrow topic → first question → Structured text explanation → fixed FSRS
  dock → PrepLadder 38-topic regression; Biochemistry remains PrepLadder-only.
  Side-by-side APK packaging and feature-preview deployment passed; production
  promotion was skipped.
- Status: build/browser verified only. The user has not yet physically
  spot-checked or accepted the new Physiology pilot.
- Next: user checks the feature preview Physiology Marrow flow; if accepted,
  continue with a bounded Biochemistry pilot through the same registry, then
  expand remaining verified Marrow chapters in batches.

## 2026-09-08 — Topics depth, layered Back, and explicit FSRS save

- Implemented the approved Topics journey in the owning V11.4 transform, with editable section taxonomy and state-driven milestone treatment.
- Corrected completed session history to Analysis over Topics, matching the requested parent layer.
- Reframed FSRS controls as a dedicated More subsection and removed change-on-input persistence in favor of explicit save.
- Renamed the hidden Topics reference image to docs/ui-reference/topics-page-reference.jpg.
- Python/JavaScript syntax, FSRS behavior, product contracts, build-order checks, and project-memory checks pass locally. Ordered generated-app/browser checks remain Linux CI work.\n

## 2026-09-08 — Publish candidate and repair pre-existing build failure

- User authorized push, Cloudflare feature PWA deployment, and APK build.
- Corrected Analysis Back destination to Topics and restored the Marrow transform's required Topics heading anchor.
- Fixed Marrow gold-renderer installation guard: a symbol reference must not count as the installed declaration.
- Added browser coverage for grouped Topics, native Back after completion, and FSRS explicit save plus reload persistence.
- Deployment and build verification are pending the candidate CI run; no physical acceptance is implied.

- Publishing outcome: `6ba7ebe` pushed to feature/marrow-bank-pilot; Engineering Gate 34203639427 and full build 34203639327 succeeded. Browser regressions and packaged APK checks passed. Cloudflare deployment https://7023d1b5.nk-qbank.pages.dev updates the feature alias. APK/PWA artifact 10046898472 is available. Live markup was independently fetched and verified.

## 2026-09-08 — User rejection and corrective handoff

User rejected deployed candidate: unchanged-looking/unfaithful Topics, missing glow, below-list Continue Learning, inadequate FSRS controls, severely degraded PDF explanations. Quick source inspection confirmed sticky-after-list layout and inline details settings; PDF quality limitations identified but regression cause unconfirmed. Recorded exact evidence and next steps in docs/REJECTED_TOPICS_FSRS_HANDOFF.md. No product edits or deployment in this feedback session.

## 2026-09-08 — recovery implementation
Implemented approved recovery in existing transform owners: Topics separate path/glow/fixed tray/index/search; FSRS dedicated route with draft validation, save/cancel and unsaved departure; PDF crop-only density-aware lossless raster and fresh fullscreen raster; correct high-density fit; session-origin completion. Local checks pass; Linux build/browser/visual verification pending. Feature push deploy held until manual dispatch after screenshot review. No acceptance claim.


## 2026-09-08 — Marrow recovery CI fix and next integration scope

- Diagnosed the latest full-run failure at Marrow browser verification: the generated PWA correctly referenced the same-origin `/anatomy-source.pdf` route, but the plain CI static server did not execute the Cloudflare Pages worker and returned 404.
- Fixed only the browser test server by mapping that same route to the exact committed `app/src/main/assets/Anatomy_QBank_Source.pdf`; production PDF routing, Marrow data, and learner behavior were not changed.
- Substantive fix commit: `1c9826ae`.
- Verification: Engineering Gate `34241919403` success; full Android+PWA run `34241919548` success. The previously failing Marrow browser/PDF step passed, followed by side-by-side APK build, packaged APK verification, packaged product contract, reproducibility manifest, and artifact upload. Push deployment remained intentionally skipped.
- User's next integration instruction: when chunked Marrow JSON/JSONL is supplied, integrate the content into the existing shared bank registry and existing study engines first, source-faithfully and without explanation redesign. Explanation polish will be a later phase.
