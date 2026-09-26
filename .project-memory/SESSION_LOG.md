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


## 2026-09-08 — Expand Marrow to 2,115 questions across all three subjects

- User supplied three archives for immediate source-faithful ingestion and
  explicitly deferred explanation redesign:
  Anatomy Phase A Ch1–48, Biochemistry Phase A Ch1–26, Physiology Ch1–33.
- Validated the archive contents as JSONL and inventoried:
  Anatomy 819 questions / 48 chapters; Biochemistry 543 / 26;
  Physiology 753 / 33; total 2,115 questions.
- Reused the existing subject-indexed Marrow registry and every existing study
  engine. No new Practice, CBT, Review, FSRS, sync, module, persistence,
  analytics or navigation engine was created.
- Normalized the supplied records into deterministic Marrow bank envelopes and
  built manifest-verified compressed/base64 transport bundles:
  `anatomy_phase_a`, `biochemistry_phase_a`,
  `physiology_ch001_033`. Validation covers shard count, encoded/compressed/raw
  lengths, SHA-256, identity, topic/question counts, globally unique namespaced
  IDs, option/correct-answer shape and question→topic linkage.
- Kept the original 62 Anatomy and 80 Physiology pilot records as accepted
  regression/augmentation subsets rather than overwriting their behavior.
  The existing 142-question enhanced explanation map remains a subset; newly
  added questions intentionally use the source-faithful structured renderer.
- Preserved all three resolved Anatomy reconstructions:
  `ANAT_CH02_Q010` (4-2-1-3 sequence),
  `ANAT_CH03_Q004` (3-2-4-1 notochord sequence),
  `ANAT_CH04_Q013` (DCDA/MCDA/MCMA categories).
- Used small Git blob/tree writes for the generated bundles instead of a
  monolithic connector write. A transient connector staging bridge was used
  only to move generated text safely; committed shards/manifests are the sole
  repository/runtime truth.
- Updated `tools/apply_marrow_bank_pilot.py` so the expanded records replace
  the learner-facing Marrow envelope after the shared registry exists.
- Expanded `tools/test_marrow_bank_pilot.py` to assert 819/48 + 543/26 +
  753/33, 2,115 globally unique IDs, pilot-subset compatibility and resolved
  reconstructions.
- Updated Playwright browser coverage for all three subjects. The first full
  run after wiring failed at browser verification (run 402,
  `34244982211`) because the old test still asserted Biochemistry had only
  PrepLadder. That assertion was stale: two banks were now the intended
  product. The test was rewritten to enter Marrow Biochemistry, verify Chapter 1
  and its structured explanation, then return to PrepLadder.
- Found and fixed a second pilot-era assumption before final verification:
  Marrow topic grouping hard-coded every non-Physiology subject as
  `General Embryology`. Replaced it with subject-aware grouping for expanded
  Anatomy, Physiology and Biochemistry. This is navigation taxonomy only.
- Final integration checkpoint `bc500234` passed:
  Engineering Gate `34245190588` / run 193; full Android+PWA
  `34245190771` / run 403. Browser emitted
  `MARROW_BROWSER_OK registry=subject-indexed anatomy=819/48 biochemistry=543/26 physiology=753/33 total=2115`.
  Side-by-side APK and packaged product contract passed.
- Final build artifact: `V11.7-android-pwa`, artifact ID `10063767953`.
- The push-run feature deployment step was intentionally skipped by branch
  policy, so this green build was not yet the live preview. Next action is a
  feature-preview-only publish for the user's physical visual review.
- Status: expanded candidate is build/browser verified, not device-verified and
  not accepted. V11.6 `125d68b` remains the accepted rollback checkpoint.


## 2026-09-08 — Publish exact 2,115-question Marrow feature preview

- The final integration push run 403 was green but intentionally skipped
  Cloudflare deployment on `feature/marrow-bank-pilot`; the existing alias was
  therefore stale and was not handed to the user as the new candidate.
- Temporarily opened **feature-preview deployment only** in
  `.github/workflows/build-apk.yml`. Production promotion retained its explicit
  `github.ref_name != 'feature/marrow-bank-pilot'` guard throughout.
- First publish attempt (Engineering `34246776564`, build `34246776483`)
  stopped at `verify_project_memory.py`. The new STATE text preserved the
  accepted V11.6 baseline semantically but omitted the verifier's required
  literal `Accepted product commit:` field, so README/STATE alignment failed.
  Added `Accepted product commit: 125d68b`; no product code/data was changed.
- Fresh Engineering Gate `34246876859` / run 195 passed.
- Full publish run `34246876973` / run 405 passed end-to-end:
  Marrow browser verification, APK build, packaged APK verification, packaged
  product contract, reproducibility manifest, artifact upload, and Cloudflare
  feature-preview deployment.
- Published feature alias:
  `https://feature-marrow-bank-pilot.nk-qbank.pages.dev`.
  Immutable deployment:
  `https://2278b62b.nk-qbank.pages.dev`.
- Run 405 artifact `V11.7-android-pwa`: ID `10064442860`;
  screenshot artifact ID `10064414099`.
- Cloudflare **production promotion was skipped**. The temporary feature-push
  preview exception was restored immediately afterward in a `[skip ci]`
  handoff commit.
- Status remains build/browser verified only. The user now owns the physical
  PWA review and will decide the next phase from observed behavior.


## 2026-09-08 — User physically validates Marrow integration and recovered Topics/FSRS

- User opened the run-405 Marrow feature PWA and confirmed the question
  integration is successful.
- User specifically confirmed the recovered Topics journey UI/fixed Continue
  Learning tray and the dedicated FSRS customization controls are now live and
  good in this feature PWA.
- This resolves the earlier visual rejection of `6ba7ebe`; that rejection remains
  historical evidence, not the current verdict.
- The reason the older “main PWA” did not show these changes is branch/deployment
  separation: the full recovery lives on `feature/marrow-bank-pilot`, Git
  `main` is stale, and Marrow run 405 intentionally skipped Cloudflare production
  promotion. Do not rebuild the features from scratch when consolidating later.
- User identified the next Topics defect: **the major-section indexes are not
  source-true**. The visual journey itself should stay. Added
  `docs/MARROW_TOPIC_INDEX_TAXONOMY.md` with the requested Anatomy,
  Physiology and Biochemistry index order, current chapter guidance, PYQ rules,
  and explicit-review treatment for ambiguous cross-system topics.
- User identified explanations as the next major content-quality phase after the
  handoff. The Biochemistry screenshot demonstrates successful question/answer
  integration but rough raw structured/OCR prose. Added
  `docs/MARROW_EXPLANATION_FINE_TUNING.md` to preserve the existing
  142-question gold grammar while scaling source-faithful cleanup, emphasis,
  tables and wrong-option rationales through a separate augmentation layer.
- Added `docs/TOPICS_FSRS_FEATURE_HANDOFF.md` so the main agent can recover the
  exact good feature lineage and understand why production/main PWA can lag.
- No product implementation was requested in this session; documentation/memory
  only.
## 2026-09-08 — Unified-main consolidation begins

- Created `consolidation/main-unified` from the user-tested Marrow feature head.
- Audited stale `main`: its unique temporary workflow commits cancel out; the
  Review/WebView fixes are superseded or already present in the V11 lineage.
- Replaced Marrow section-number heuristics with an explicit 107-topic taxonomy,
  title assertions, canonical section order and complete-coverage tests.
- Hardened deployment so production requires an explicit `main` dispatch and
  exact full release SHA. No production deployment occurred.
- Local checks passed. Engineering run 196 and full Android/PWA run 406 passed
  at `87faccd`, including generated browser, PDF, APK and packaged contracts.
  The consolidation preview deployed; production promotion was skipped.
## 2026-09-08 — Main consolidation and explanation inventory

- PR #6 merged the verified feature lineage and explicit taxonomy into `main`.
- Canceled the first automatic main build before deployment after identifying
  that a Pages `--branch=main` preview could target the production environment.
- PR #7 made all main pushes skip Cloudflare. Main run 409 passed every build,
  browser and package gate; both Cloudflare steps were skipped.
- Added deterministic, text-free explanation triage for all 2,115 Marrow IDs and
  selected a 20-question cross-chapter Biochemistry gold sample. No source or
  learner-facing explanation was changed.


## 2026-09-08 — Marrow explanation-quality phase started

- User physically verified the newly deployed Marrow PWA, confirmed the current
  question/integration/taxonomy experience is correct, and declared that
  verification phase complete.
- User explicitly designated the existing 142 enhanced Marrow questions
  (62 Anatomy + 80 Physiology) as the gold-standard explanation reference.
- Started bounded Biochemistry quality work on
  `feature/marrow-biochem-explanation-gold-sample`.
- Added `data/marrow/explanation_biochem_gold_sample_v1.json`: the deterministic
  20-question cross-chapter sample now has takeaway, cleaned display text,
  selective emphasis and exactly three distractor rationales per question.
- Raw Marrow source bundles remain unchanged. Source ambiguity is preserved
  rather than invented, including the missing PCT lab panel and the missing
  numbered enzyme list in the vitamin-B12 combination question.
- Added a source-hash/ID/rationale contract test and wired the 20-question
  candidate through the existing Marrow renderer without changing its UI,
  FSRS footer, Practice/CBT/Review flow, source tables or navigation.
- The 142-question set remains the approved reference; the 20 Biochemistry
  questions remain candidate-human-review until visual approval.


## 2026-09-09 — Biochemistry explanation sample approved

- User physically reviewed the 20-question cross-chapter Biochemistry explanation
  sample and explicitly approved its quality: “They are good. We need that kind
  of explanation everywhere.”
- This promotes the explanation reference from 142 to **162 approved questions**
  (62 Anatomy + 80 Physiology + 20 Biochemistry).
- Full Android/PWA and Engineering Gate were green on the approved candidate.
- The remaining rollout target is **1,953 Marrow questions**, to be handled in
  deterministic chapter batches with raw source immutable and source ambiguity
  preserved rather than invented.


## 2026-09-09 — Full explanation rollout started: Biochemistry Chapter 1

- Merged the user-approved 20-question Biochemistry gold sample into `main`
  via PR #9 at merge commit `4d93f6f9`.
- Started deterministic full-bank rollout on
  `feature/marrow-explanation-rollout-biochem-ch01`.
- Added approved learner-facing augmentation for the remaining 22 questions in
  Biochemistry Chapter 1. Gold-sample Q23 already covered the chapter's final
  question, so Chapter 1 is now **23/23 enhanced**.
- Explanation inventory is now **184 enhanced / 1,931 pending**.
- Generalized the Biochemistry augmentation loader to accept future approved
  chapter batch files with collision, option/rationale, emphasis and source-ID
  checks. Raw source bundles remain unchanged.
- Added dedicated Chapter 1 rollout tests and browser coverage. Exact next content
  start after this batch: **Biochemistry Chapter 2**, skipping already-approved Q9.

## 2026-09-09 — Marrow image pipeline implementation; user-requested pause

- Updated local checkout to remote main and created `feature/marrow-image-pipeline`.
- Added PDF image audit, immutable native extraction, Ubuntu region-render fallback,
  provenance/QA registry, ID-bound inline rendering and existing zoom viewer integration.
- Initial commit `07ee53d` passed full Android/PWA CI `34311877059`; comparisons
  and microscopy viewer were inspected. Production remains unchanged.
- Expanded pilot: 18 inspected assets, 15 PASS, one SOURCE_LIMITED, two held for
  reconstruction; 16 app assets including two source-compared SVG reconstructions.
- Expanded batch registry tests pass. Pipeline ownership gate currently flags the
  read-only package checker being called once for web and once for APK; fix on resume.
- User requested a pause to preserve usage. Saved all work and resume instructions;
  expanded batch CI, physical review and full-bank classification remain unfinished.

## 2026-09-09 — Expanded Marrow image pilot build verification

- Resumed at the user's request and fixed the read-only package verifier's
  pipeline ownership classification.
- Full Android/PWA run `34328039057` passed for commit `748204b`, including
  browser rendering/zoom, web offline-cache hashes, APK asset hashes, packaged
  product contracts and artifact upload.
- Artifact `V11.7-android-pwa` ID `10094653587`; immutable preview
  `https://334bc346.nk-qbank.pages.dev`. Production promotion was skipped.
- The 18-asset audit set remains 15 PASS, one SOURCE_LIMITED and two
  REVIEW_REQUIRED. Sixteen reviewed assets are learner-facing; user/device
  approval and broader classification remain outstanding.
## 2026-09-09 — Marrow image pilot user-approved

- The user reviewed all sixteen released pilot figures in the deployed PWA and
  approved them as readable and good given the authoritative PDF sources.
- The approved pilot quality is now the minimum threshold for the wider image
  rollout; later assets may improve on it but must not regress below it.
- Authorization was given to merge the pilot, responsibly reconstruct the two
  held diagrams, and continue the image rollout in bounded QA-checked batches.
- Authentic medical/photo imagery remains source-preserved; reconstruction is
  restricted to faithful educational diagrams and annotation layers.

## 2026-09-09 — Marrow image rollout Batch 01 implemented

- Merged the user-approved image pilot through PR #12; production remained unchanged.
- Reconstructed the held notochord and glycolysis diagrams as source-faithful SVGs.
  Rendered source/production comparison found and corrected a false notochord lumen,
  a disconnected glycolysis branch and lost reversible-arrow semantics before PASS.
- Expanded to 28 approved assets serving 34 questions: Anatomy 12, Biochemistry 11,
  Physiology 11. Ten new native assets and six repeated-asset bindings passed review.
- Preserved exact pixels for two new muscle biopsy/histology assets; the question-time
  biopsy uses neutral alt text. No medical imagery was reconstructed or enhanced.
- Added independent binding QA/provenance. Rejected two wrong reuse candidates instead
  of attaching plausible but mismatched images. Added deterministic progress reporting,
  stricter local-marker SVG validation, and browser checks for reconstruction timing,
  fullscreen viewing and authentic question-time imagery.
- Source/local validation passes. Full Batch 01 Android/PWA/browser/package CI remains
  pending at this checkpoint; production promotion is forbidden.

## 2026-09-09 — Marrow image rollout Batch 01 build-verified

- Full Android/PWA run `34334231275` passed at product commit `44990c0`.
- CI released 28 assets to 34 questions; web and APK package verifiers confirmed
  exact content hashes, and the browser suite verified explanation-only timing,
  question-time biopsy placement, neutral alt text and fullscreen SVG viewing.
- Generated glycolysis-viewer and authentic-biopsy screenshots were inspected.
- Artifact `V11.7-android-pwa` ID `10097131223`; immutable preview
  `https://88a0ce10.nk-qbank.pages.dev`; alias
  `https://feature-marrow-image-rollout.nk-qbank.pages.dev`.
- Production promotion was skipped. This is build-verified, not a new physically
  accepted overall product baseline.

## 2026-09-09 — Marrow image rollout Batch 01 merged

- PR #13 merged the build-verified 28-asset / 34-question Batch 01 into `main`
  at merge commit `6d1b520`.
- Production remained unchanged. Full-bank image rollout is still active; Batch 02
  should prioritize unresolved stem-critical and multi-candidate figures.

## 2026-09-09 — Biochemistry Chapter 4 explanation refinement

- The user spot-checked roughly 10–15 questions from image Batch 01 and gave a
  green light to continue, then reprioritized work from images to explanations.
- Paused image Batch 02 before release. Its six native candidates are preserved
  as REVIEW_REQUIRED on `feature/marrow-image-rollout-batch-02-small` at
  checkpoint `6823d70`; none is learner-facing.
- Selected Biochemistry Chapter 4 because it has 11 questions and gold-sample Q5
  was already approved. Added source-preserving display augmentation for the
  remaining 10 questions, completing the chapter under the approved grammar.
- Added full chapter-ID, source-hash, distractor-key, emphasis and inventory
  checks plus browser coverage for the long classic-galactosemia explanation.
  Inventory is now 194 enhanced / 1,921 pending. Local verification passes 36
  checks; full generated-app/browser/APK CI is pending.


## 2026-09-09 — Reconcile Biochemistry Chapter 2 onto current explanation lineage

- Re-read the canonical Marrow explanation fine-tuning, bank integration,
  architecture, product and decision contracts before continuing.
- Recovered the previously authored 29-question Chapter 2 augmentation from the
  stale pre-image branch and rebased it as a bounded batch on top of the current
  Chapter 4 explanation lineage. Raw Marrow source remains unchanged.
- Corrected Chapter 2 batch metadata to the canonical source title
  `Glycolysis and gluconeogenesis` and current pre-batch reference count.
- Audited selective emphasis anchors and corrected exact-string mismatches so
  intended high-yield emphasis actually renders; no medical prose was rewritten.
- Restored generalized per-chapter rollout validation and added an executable
  requirement that every emphasis anchor exists in its display text.
- Added browser coverage for Chapter 2 Q1 while preserving existing Chapter 4,
  gold-sample, FSRS-footer and source-figure regressions.
- Regenerated the deterministic inventory through CI: **223 enhanced / 1,892
  pending**, with source hashes and review-flag counts unchanged.
- Exact next fresh content start after this verification batch: **Biochemistry
  Chapter 3 — Glycogen metabolism and glycogen storage disorders**.

## 2026-09-09 — Explanation rollout through Physiology Chapter 5

- Biochemistry explanation refinement reached Chapters 1–11 on the stacked
  immutable-source augmentation lineage. Chapter 11 exact candidate
  `efa9a0a61997929c052aac760e88363c61acef8b` passed Engineering Gate 257 and
  full Android/PWA run 529; production promotion was skipped.
- Switched the explanation-refinement workflow to Physiology. Existing approved
  Physiology pilot remains 80 questions across Chapters 1–4.
- Added `data/marrow/explanation_physio_ch05_v1.json` for Chapter 5 **Body
  Fluids**, 28/28 questions, preserving source figures/tables separately and
  adding source-faithful display text, selective emphasis and exactly three
  distractor rationales per SBA.
- Generalized the shared augmentation loader and deterministic inventory to
  discover `explanation_physio_ch*_v1.json`; added
  `tools/test_marrow_physio_explanation_rollout.py` and wired it into both
  Engineering Gate and full Android/PWA CI. Generalized the Biochemistry rollout
  global-count assertion so subject-local guarantees remain valid when another
  subject adds enhancement records.
- Chapter 5 exact verified candidate:
  `f170eb8517998cdaf4229240d2c2a273c6d98cf8`; PR #24; Engineering Gate 259
  **success**; full Android/PWA run 539 **success**.
- Real-browser regression: Physiology → Marrow → Body Fluids → Q17 verifies the
  permeant-urea / tonicity distinction and exactly three distractor rationales.
- Deterministic inventory after Chapter 5: **429 enhanced / 1,686 pending**,
  fingerprint
  `09989df1e8745f7338abf146fb4eb1337738ecaf4dafb1b69f9c76314e521ea8`.
- Verified preview:
  `https://3cce6bfb.nk-qbank.pages.dev`.
- Ownership handoff: primary agent will continue **source-image integration**;
  explanation refinement remains a separate workstream. If/when explanation
  work resumes, exact next target is Physiology Chapter 6 — **Physiology of
  Nerve**.



## 2026-09-09 — Marrow image rollout resumed through Batch 04

- Rebased image work on the verified explanation lineage through Biochemistry Chapters 1–11 and Physiology Chapter 5; explanation files were not altered.
- Released Batch 02's six source-compared candidates, then inspected two 30-binding native batches at native resolution against owning question metadata.
- Working totals: 79 approved assets, 94 released bindings and 87 released questions. Batch 03 and Batch 04 each released 27/30 bindings.
- Preserved native bytes for all medical/photo material. Rejected six false page-neighbor or reuse associations, including fructose-for-galactose, conductance-for-muscle-twitch, glial-chart-for-neuron, transamination-for-BH4 and two muscle-protein neighbor mismatches.
- Strengthened staging so new primary bindings carry independent QA status and exact page/xref/region, allowing valid assets to survive while wrong question ownership is rejected.
- Added browser coverage for two-stage MELAS imagery: one neutral question image before answering, then the authentic explanation panel after answering.
- Initial Batch 03 CI failed at inherited project-memory validation before product tests; restored the required accepted-baseline/product-commit/known-problems/next-step handoff fields. Full current candidate verification remains pending.

## 2026-09-09 — Marrow image rollout through Batch 07

- Continued the image-only workstream on top of the verified explanation lineage; explanation augmentations and immutable raw Marrow bundles were not changed.
- Visually source-compared 90 candidate bindings across Batches 05–07. Released 72 bindings and expanded learner coverage from 87 to 152 questions using 147 approved assets.
- Preserved authentic clinical photography, radiology, histology, microscopy and specimen assets byte-for-byte. Native educational diagrams were released only when labels, arrows, panels and question meaning met the approved baseline.
- Rejected 17 false page-neighbor/reuse mappings, including a tRNA-synthetase Rossmann image offered for LDH, prior-question muscle figures, Starling graphs offered for unrelated smooth-muscle questions, and action-potential figures offered for unrelated contraction questions.
- Held the native Golgi-tendon-organ sequence as REVIEW_REQUIRED because its dense labels are below the approved readability floor; it must be faithfully reconstructed rather than shipped blurry.
- Current deterministic totals: 150 registry assets (145 PASS, 2 SOURCE_LIMITED, 2 REJECTED, 1 REVIEW_REQUIRED), 192 bindings (166 released), and 152 released questions: Anatomy 58, Biochemistry 55, Physiology 39.
- Full Android/PWA CI passed Batches 05–07 (`34367383565`, `34367985338`, `34368514110`), including browser, offline hashes, APK packaging and exact packaged-image bytes. Latest immutable preview: `https://4d588745.nk-qbank.pages.dev`; artifact `V11.7-android-pwa` ID `10111037219`; production promotion skipped.


## 2026-09-09 — Home enhancement scoped and safely paused

- Chose a bounded Home-page enhancement as the best quality-to-usage task after
  the user deferred another large image phase. Created
  `feature/home-command-center-current` directly from the verified Batch 07 image
  branch; no product behavior or asset was changed.
- Audited the active Home renderer and ordered CI transform chain. The key build
  constraint is that Custom Study Modules modifies the V11.4 Today’s Focus panel
  after the whole-app visual transform, so the new Home transform must run after
  `apply_custom_study_modules_v1.py` and its test.
- Fixed implementation scope for the next session: retain every established Home
  action, add clearer action microcopy/accessibility/responsive layout, and use
  recommendation priority unfinished saved module → due FSRS review → Practice 20.
  This is presentation/action hierarchy only; Practice, CBT, Review, FSRS, sync,
  modules, content, and image pipelines remain protected.
- Stopped when the user reported about 15% usage remaining. Two
  `apply_patch` attempts failed at the Termux sandbox boundary before writing.
  No partial product edit exists. Resume with the deterministic transform and contract test, wire it
  after Custom Study Modules, add a Home browser screenshot/assertions, run local
  checks and full Android/PWA CI, then visually inspect the artifact.

## 2026-09-10 — Automation audit and Home command-center implementation

- Audited GitHub before resuming product work. The explanation lineage has green
  full builds through Physiology Chapter 8 (512 enhanced questions); Chapter 9
  has 27 authored records but its exact-head build fails because the deterministic
  inventory does not match. The Anatomy image automation safely staged six
  Chapter 9 candidates without releasing them, but also committed generated
  `tools/__pycache__` files, so that branch must not be merged wholesale.
- Implemented `apply_home_command_center_v1.py` after Custom Study Modules. The
  Home focus panel now exposes one explicit recommended action with deterministic
  priority saved module → due FSRS review → Practice 20, while preserving the
  remaining non-duplicate Continue Practice, Review Due, Practice 20 and Timed
  CBT actions plus the existing Study Sets section.
- Added a pure priority behavior check, exact fail-closed transform contract,
  idempotence/accessibility/responsive/reduced-motion assertions, protected build
  order, generated product markers and a 390×844 browser screenshot regression.
- `verify_local.py` passes 38 local checks. PDF generation, the generated browser
  screenshot, packaged APK checks and visual QA remain CI-only and pending.
- The first full run correctly failed the generated contract because the new
  card shortened the protected “Practice 20 Random Questions” label. Restored
  the exact learner-facing wording before rerunning the candidate.
- The next run reached the Home browser assertion; rendered `innerText` reflects
  CSS uppercase for the recommendation badge. Made that visual-text assertion
  case-insensitive without changing the UI or its source label.
- Exact product commit `3ec666c` passed Engineering Gate `34438517764` and full
  Android/PWA run `34438517773`, including generated JavaScript, real-browser,
  offline PWA, APK and packaged-contract checks. Inspected the generated 390 px
  Home screenshot: recommendation hierarchy, spacing, labels and mobile action
  layout are clear, with Study Sets and downstream sections intact. Immutable
  preview: `https://5a8a5212.nk-qbank.pages.dev`; artifact `10137126889`;
  production promotion skipped. Physical-device acceptance remains pending.


## 2026-09-12 — Biochemistry Ch2 Q6/Q7 canonical image coverage candidate

- Started `NKQ_BIOCHEM_COVERAGE_Q06_Q07_20260912_V3` from exact canonical SHA `e17b622b238280c127cd7c91a420dee82bdafdd9`.
- Recovered Q6 page 31/xref 1126/region `[162,110,450,326.16]` and Q7 page 31/xref 1125/region `[162,512.976,450,729.136]`. Both 600x450 native figures were source-compared; Q7 is the exact source represented by the existing PASS reconstruction and Q6 differs only by minor JPEG compression while preserving identical pathway semantics.
- Reused existing PASS asset `biochemistry-aa11f9fa6a08baea` by independent per-binding provenance; no duplicate asset was created.
- Candidate coverage: 110 raw / 109 effective / 69 released / 1 invalid / 70 resolved / 4 tracked-unreleased / 36 untracked / 31 text-cue. Subject remains INCOMPLETE.
- Next deterministic unresolved reference: `marrow__BIOCHEM_CH02_Q021:figure:1` (explanation, source pages [39], UNTRACKED_SOURCE_VISUAL). Exact-head full CI still required; no main or production promotion.

## 2026-09-12 — Biochemistry Q21 image recovery remains safely checkpointed

- Resumed CURRENT_UNFINISHED image batch `NKQ_BIOCHEM_COVERAGE_Q21_20260912` on `automation/marrow-images-biochemistry-coverage-20260912-q21`; target remains `marrow__BIOCHEM_CH02_Q021:figure:1`, explanation-only, authoritative Biochemistry ED8 page 39, composite xrefs 83/84/85, exact region `[161.491,55.671,450.509,272.328]`, with neighboring xref 86 excluded as Q22-owned.
- Recomputed the complete canonical 2,711-question source audit before mutation. Biochemistry remained 110 raw references / 109 effective / 69 released / 1 invalid-source-metadata / 70 resolved / 4 tracked-unreleased / 36 untracked / 31 text-cue review items. No completeness claim is allowed.
- The prior visual/source review remains valid for the inspected 1206×904 candidate identified by SHA-256 `07082b9d273f10881d05557827fff479dd18ed450f2ae874aa51bc460a7b03a4`; the unresolved issue is durable byte provenance, not question ownership or diagram semantics.
- Two bounded fail-closed integration attempts stopped before registry mutation: workflow `34684150752` reproduced the page/region as PNG SHA `f2a6b0691fffcbe3756d9db58d2baf28c3254f54ede9de577071b7b244bdc789`; workflow `34684256506` losslessly optimized the same current-toolchain render to SHA `8aed0451d7048ab99149fec8d3e93e9c3222a9a21f00a204ee9bbab2cbb7635a`. Neither matched the previously reviewed `07082b9d…` bytes, so neither was released.
- Per the runbook's two-attempt failure containment rule, no third same-class repair was attempted. Registry, release metadata, progress and learner-facing assets remain unchanged. Temporary one-shot integration tooling was removed.
- Safe specialist checkpoint is `e81157ca96a593975b00879fa425bd4690d3e637`; checkpoint file `data/marrow/images/recovery_checkpoints/biochem_ch02_q021_20260912.json` records both failed attempts and exact next action.
- Next image action: do not skip Q21 and do not blindly retry current encoders. Recover the exact reviewed` 07082b9d…` bytes from durable historical evidence if possible; otherwise choose one pinned deterministic encoding and perform fresh full-page/exact-region/native/phone/expanded visual QA before adopting a replacement production hash. Then integrate non-destructively, regenerate progress/coverage/release, run full image/browser/PWA/APK/package verification, and reconcile into canonical before releasing the image lane. Production remains untouched.

## 2026-09-12 — Canonical reconstruction and Continue Practice candidate

- Reconstructed the prior-day GitHub state before editing: `feature/marrow-canonical-full-current` is the sole integration trunk; the complete Marrow corpus is 2,711/134; the structured-table fix and Biochemistry Q6/Q7 images are canonical and green; Anatomy Ch6 Q1–Q7 still needs inventory/browser/full promotion. Historical stacked branches remain stable-ID evidence only.
- Created `fix/continue-practice-session-resume-20260912` from canonical, then rebased it after canonical advanced through the Q21 evidence-recovery checkpoint `a75f59c`. All newer Q21 byte-provenance findings were preserved. Main/production was not changed or promoted.
- Implemented explicit Pause/Submit controls and durable regular-Practice continuation through existing `activeSession`/test persistence: original ordered IDs and topic context survive Pause; answered correct/wrong questions are excluded; skipped/unseen remain; a completed topic advances to the next canonical topic. Wrong/Bookmarks, FSRS, Review, CBT and Custom Study Modules remain separate.
- Removed the legacy Practice mutation observer that hid a visible Submit control. Added deterministic 20→16 behavior coverage plus generated-PWA 320/390/768 px control/overlap checks and protected build/product contracts.
- Corrected local verification discovery so donor `*_core.py` and browser helper implementations are not executed as owner entrypoints. `verify_local.py` passes 41 local checks.
- Product commit `a717563` passed exact-head Engineering Gate `34684693663` and full Android/PWA/browser/APK/package/reproducibility run `34684715131`. Continue Practice browser verification passed at 320/390/768 px with exactly 16 remaining; generated screenshots were inspected and show clear, separated Pause/Submit and Previous/Next rows. Preview: `https://26c21c13.nk-qbank.pages.dev`; APK/PWA artifact `10294634822`; screenshot artifact `10294714739`; production promotion skipped. Canonical reconciliation and physical-device acceptance remain pending.

## 2026-09-12 — Biochemistry Q21 coverage recovery R2
- Canonical base: `d84a8093468c278a19e81e917bcc66da91f33574`; branch `automation/marrow-images-biochemistry-coverage-20260912-q21-r2`.
- Fresh visual QA run 34686576057 / artifact 10295084510 adopted deterministic raw 300-DPI region render SHA `f2a6b0691fffcbe3756d9db58d2baf28c3254f54ede9de577071b7b244bdc789` after the earlier non-reproducible optimized encoding was retired.
- Integrated `marrow__BIOCHEM_CH02_Q021:figure:1` explanation-only from page 39, xrefs 83/84/85; xref 86 excluded as Q22-owned. No medical/diagram detail was generated or altered.
- Coverage after release: 70 released, 4 tracked-unreleased, 35 untracked, 1 invalid metadata, 31 text-cue review items; subject incomplete.
- Next deterministic reference: `marrow__BIOCHEM_CH02_Q026:figure:1 (explanation, source pages [41], UNTRACKED_SOURCE_VISUAL)`.
- Production promotion prohibited; exact-head product CI still required before canonical reconciliation.


## 2026-09-12 — Biochemistry Q21 image recovery fully verified and reconciled

- Resumed the unfinished Ch2 Q21 explanation figure from the live canonical base `d84a8093468c278a19e81e917bcc66da91f33574` on `automation/marrow-images-biochemistry-coverage-20260912-q21-r2`.
- Fresh source comparison used authoritative Biochemistry ED8 page 39, composite xrefs 83/84/85, exact region `[161.491,55.671,450.509,272.328]`; neighboring xref 86 is Q22-owned and excluded. Full-page, exact-region, 1206x904 native, 390px phone and 768px expanded views were inspected in workflow **34686576057**, artifact **10295084510**.
- Adopted the deterministic raw 300-DPI source render SHA-256 `f2a6b0691fffcbe3756d9db58d2baf28c3254f54ede9de577071b7b244bdc789`; no reconstruction, generation, inpainting, or medical/diagram-detail alteration was used.
- Registry/release integration commit: `d7a1fc6fead85beb9354965b6621d6756cc30580`; exact-head CI handoff: `88a068182b76a0ab4730c90b93b35f30cb31ca2a`. Engineering Gate **34686820682** passed. Full Android/PWA/browser/image-comparison/APK/package/reproducibility/preview run **34686821723** passed. Production promotion was skipped.
- Post-release Biochemistry coverage: **110 raw / 109 effective / 70 released / 1 invalid source metadata / 71 resolved / 4 tracked-unreleased / 35 untracked / 31 text-cue review items**. Subject remains **INCOMPLETE**.
- The verified handoff was fast-forwarded into `feature/marrow-canonical-full-current` without a registry/progress conflict. Image writer lane released.
- Next deterministic source reference: `marrow__BIOCHEM_CH02_Q026:figure:1`, explanation, source page 41, two native candidates. Do not skip it for an easier later reference.

## 2026-09-12 — Biochemistry Q26 coverage recovery
- Canonical base: `72fa0b6a921015c2e35addaccf06c1949d938f35`; branch `automation/marrow-images-biochemistry-coverage-20260912-q26`.
- Direct QA of hash-verified ED8 page 41 established xref 92 as the Q26 explanation-owned glycolysis/gluconeogenesis figure; xref 91 is the separate neighboring pyruvate-carboxylase figure above the Q26 solution and was excluded.
- Released exact native 960x540 JPEG bytes SHA `22651a6eb0d53c783ebdaa8d967948ed3a88a2ef96669ed84c6788e18bf8645c`; no crop/reconstruction/generation/inpainting/sharpening.
- Coverage after release: 71 released, 4 tracked-unreleased, 34 untracked, 1 invalid metadata, 31 text-cue review items; subject incomplete.
- Next deterministic reference: `marrow__BIOCHEM_CH04_Q011:figure:1 (explanation, source pages [69], UNRELEASED_TRACKED)`.
- Production promotion prohibited; exact-head product CI still required before canonical reconciliation.


## 2026-09-12 — Biochemistry Q26 exact-head verification
- Q26 integration commit `36a0d000ee5268dd8fd1ca28f022cb960f503401`; exact certified product handoff `fa79b6cf4b0d8f3a81147886b8785229533aee67`.
- Engineering Gate **34692045844** passed; full Android/PWA/browser/image-comparison/APK/package/reproducibility/preview run **34692046932** passed; production promotion skipped.
- Post-release coverage remains 110 raw / 109 effective / 71 released / 1 invalid metadata / 72 resolved / 4 tracked-unreleased / 34 untracked / 31 text-cue; Biochemistry remains incomplete.
- Next deterministic reference is `marrow__BIOCHEM_CH04_Q011:figure:1` on source page 69; tracked asset PASS but binding REJECTED, so the next run must resolve that source-order item rather than skip it.

## 2026-09-12 — Biochemistry Ch4 Q11 fail-closed source-review checkpoint
- Canonical base at batch start: `36c9e1a92a3925c17f6914c2a6ffebf73948ba14`; specialist branch `automation/marrow-images-biochemistry-coverage-20260912-q11`; durable checkpoint `a3fa300a054393fd7f217580e634f481c0a7b649`.
- Fresh audit/coverage confirmed Q11 as the first deterministic Biochemistry backlog item: 110 raw / 109 effective / 71 released / 1 invalid metadata / 72 resolved / 4 tracked-unreleased / 34 untracked / 31 text-cue.
- Hash-verified ED8 source review: recorded page 69 xref 1146 is fructose metabolism, SHA `bb781d8346ed1c3677ac8faf3a5a54501d09f583509a91d1aa0d7ecf9d1198d4`; the Q11 explanation visually points to the galactose flowchart below, and page 70 xref 162 is the correct native 600x451 galactose-metabolism figure, SHA `e302242457457cdcabcca8ced492809b2f1947c049b719ff49a0be6bd6a222f6`. Historical rejected Q11/fructose binding must be preserved.
- Installer run `34694510806` failed before mutation because PDF text extraction garbled `galactose` on page 69. One bounded retry removed only that brittle assertion while retaining page/xref/region/hash/ownership gates; run `34694608472` then failed before mutation because text extraction also garbled the page-70 title. Two-attempt containment triggered; no third same-class attempt was made.
- Registry, progress, coverage and learner-facing assets remained unchanged. Temporary installer/workflow helpers were removed from the specialist branch and a durable JSON checkpoint was committed.
- Next run must resume Q11 from live canonical, trust rendered-page/native-xref/hash evidence rather than corrupted embedded text, recompute source coverage, and stop or mark REVIEW_REQUIRED if ownership cannot be proven without inference. Production untouched.

## 2026-09-12 — Biochemistry lane released; manual Physiology image Batch 01 verified and reconciled

- Re-resolved the sole integration trunk at `4f716c3a8eb2c6bc8030bb638a766580f5ddeca3`, inspected live Git/CI/writer ownership and shared fingerprints, and created `automation/marrow-images-physiology-manual-20260912-b01` from that exact SHA. Canonical registry was `7fad0b03f61d6d6faa2bcb1738fbd40be13e1c5084af04072594cf2eeb24d36c`; progress was `cf926fcffad1c1b0045e9d2f4398691c58d859105086cfd20f3052ed7617a61e`.
- Closed Biochemistry fail-closed: no live writer and no verified Q11 learner-facing result existed to reconcile. Specialist branch `automation/marrow-images-biochemistry-coverage-20260912-q11` and checkpoint `a3fa300a054393fd7f217580e634f481c0a7b649` retain provenance; Q11 remains `REVIEW_REQUIRED`, shared image state was not mutated, automated Biochemistry remains paused, and no later Biochemistry reference was started.
- Audited the complete canonical corpus and processed the first six deterministic Physiology references in order: `marrow__PHYS_CH01_Q009:figure:1`, `marrow__PHYS_CH01_Q018:figure:1`, `marrow__PHYS_CH01_Q021:figure:1`, `marrow__PHYS_CH01_Q021:figure:2`, `marrow__PHYS_CH02_Q020:figure:1`, and `marrow__PHYS_CH03_Q005:figure:2`.
- Authoritative rendered-page/native inspection in one-shot source-review workflow `34698354509` established that the first four references are table-only source-metadata false positives already represented as structured text; all four are explicitly adjudicated `SOURCE_METADATA_INVALID` without changing raw records. Q20 received PASS question-time asset/binding `physiology-f675135b3bc1c381`, a precise 300-DPI page-25 region `[161.52,55.775,450.48,272.225]` compositing native xrefs 54–57, 1204x903 PNG SHA `f675135b3bc1c3817fe0523dbef4f4d64d1c6e5463ab4358e19515d7eda1e8f9`. Q5 figure 2 received an independent PASS explanation-time binding to existing asset `physiology-95389f30f8277be3`, page 44 xref 100; neighboring xref 101 was excluded as Q7-owned. No generation, inpainting, retouching, or invented medical detail was used.
- Local registry/progress/coverage regeneration checks, source comparison, stable-ID ownership, source-visual/product/build contracts, all 42 applicable local checks, and Continue Practice unit regression passed. Product commit `719e2aa0cfbacb829781e9a7953af4717a6a6f5a` passed bridge `34699011297`, Engineering Gate `34699015727`, and full Android/PWA/browser/image-comparison/APK/package/reproducibility/preview run `34699016754`. Emitted Q20 fullscreen, Q5 post-answer, and source/production comparison images were inspected and passed. Screenshot artifact `10300255269`; APK/PWA artifact `10300085581`; preview `https://72286d5a.nk-qbank.pages.dev`; production promotion skipped.
- Immediately before reconciliation, canonical still resolved to `4f716c3a8eb2c6bc8030bb638a766580f5ddeca3` and its shared registry/progress fingerprints were unchanged. Verified commit `719e2aa0cfbacb829781e9a7953af4717a6a6f5a` was then fast-forwarded into `feature/marrow-canonical-full-current`; no registry conflict was chosen or overwritten. Working branch/base provenance is retained and the image writer is released.
- Post-batch Physiology coverage: **294 raw / 290 effective / 44 released / 4 invalid metadata / 48 resolved / 21 tracked-unreleased / 225 untracked / 28 text-cue review items**. Subject remains **INCOMPLETE**. Exact next source reference is `marrow__PHYS_CH03_Q007:figure:1`, explanation, source page 44, two native candidates, `UNTRACKED_SOURCE_VISUAL`; no second batch has begun.

## 2026-09-13 — Marrow learner-content sanitizer completed

- Investigated memory handoff `0efdd434` and substantive checkpoint `a3f0e3da`; neither was canonical or fully verified. Transplanted only the stable sanitizer scope onto sole canonical base `58bb99d5c1fc96a98b4f922a963dba16105487d1` on `fix/marrow-content-sanitizer-canonical-20260913`.
- Preserved raw ED8 source. Added conservative whole-value JSON/structured-text sanitation before and after Marrow injection across stems, options, option rationales, correct-answer text, explanations, takeaways and structured-explanation text/blocks; tables, figures and medical notation remain structured/unchanged. Full-corpus regression passed 2,711 questions and 27,898 learner-facing fields.
- The previous browser failure was caused by hidden topic-numbering coupling, not bad source taxonomy. Topic numbering is now an explicit protected workflow stage. Added a real 390x844 Physiology Ch5/Ch7 learner regression covering questions, options, post-answer support, tuned explanation and three distractor rationales.
- Exact candidate `45f6539fff535fadc6aaa6970894f9ff123422fa` passed local verification (43 checks), Engineering Gate `34738522874`, and full Android/PWA/browser/image/APK/package/reproducibility run `34738530102`. Preview `https://8d6d9366.nk-qbank.pages.dev`; production promotion skipped.
- Image audit conclusion: Batch 02 materialized on side branch (`aedfe316`) but latest targeted gate `34704088880` failed canonical wiring at `7505a7c`; it was never verified/reconciled. Canonical retains Batch 01 coverage and next reference `marrow__PHYS_CH03_Q007:figure:1`.

## 2026-09-13 — User-visible Physiology OCR/code debris corrected

- User review disproved the earlier sanitizer completion claim: the generated Ch7 screenshot itself still showed source-OCR debris such as `Perimysium Vo 2"` and `Epimysium ” x`. The former regression searched only serialized-JSON markers and therefore false-passed.
- Added a separate stable-ID display-override layer for all 28 Body Fluids (Ch5) and all 35 Muscle Physiology I (Ch7) questions. It replaces 63 learner stems, 252 option labels and displayed correct-answer text with reviewed clean text after fingerprinting the exact immutable source fields; raw ED8 bundles, correct-option indexes, explanations, images and product behavior remain unchanged.
- Strengthened browser QA to compare every one of the 315 changed learner-visible values through actual `practiceOne` rendering, then verify answer-time tuned explanations/rationales at Ch5 Q1 and Ch7 Q1, Q2 and Q35. Commit `55d7ac8a89c2bbf6a01db5d305b8c975c344c1f3`; Engineering `34740460617` passed; full Android/PWA/browser/APK/package run `34740465004` passed; preview `https://c4744474.nk-qbank.pages.dev`; production skipped.
- This closes the two reported Physiology chapters. It is not evidence that unreviewed chapters are free of OCR debris; continue the same source-fingerprinted override workflow rather than broad regex guessing.


## 2026-09-13 — Physiology Ch11 Q1–Q6 explanation batch acquired

- `FULLY_VERIFIED_HISTORY`: Anatomy Ch6 Q1–Q7 certified checkpoint `58bb99d5c1fc96a98b4f922a963dba16105487d1` is already an ancestor of canonical; stale PR #52 is historical and non-blocking.
- `CURRENT_UNVERIFIED`: Physiology Ch11 Q1–Q6 on `feature/marrow-explanation-physiology-ch11-q001-q006-20260913`, canonical base `4f943af34bb4bd49f644f2655e23459fc1534031`.
- Workload **16.0**: six base points; source figures Q1/Q2/Q5; OCR/garbling Q1/Q2/Q3/Q5/Q6; Q6 resolved reconstruction.
- Raw Physiology source SHA remains `f3cd6b9dccb2092743fa86de4b0bef682d61c83762e9f00fa3b04d0a355d89d6`; canonical corpus remains 1,014 Physiology / 2,711 global.
- Static validation passed after deterministic inventory regeneration: **594 enhanced / 2,117 pending**, fingerprint `f860fc38da57af2d20be05efa33a5594b08425008a2cbcb2f3dff0bfdd27b974`.
- Next action: add stable-ID browser regression, open/reconcile PR, and require exact-head Engineering + full Android/PWA/APK/package/reproducibility/preview success before `FULLY_VERIFIED`. Production promotion prohibited.

## 2026-09-14 — FSRS lifecycle and shared question-presentation hardening

- Audited the 2,686-question PrepLadder corpus and found eight records with extraction-owned matching/table fragments mixed into answer choices plus four records without a reliable answer contract.
- Added one runtime presentation normalizer and semantic matching/list renderer shared by Practice, CBT, and Review. It preserves immutable source data, reduces repaired questions to coherent A–D/A–E choices, and fails the four incomplete records closed.
- Correct-only attempts now enter FSRS. Pause commits pending answered work but leaves untouched IDs unseen; explicit final submission marks every remaining unanswered session ID skipped.
- Added deterministic transform/helper/full-corpus tests, generated-browser presentation coverage, and an end-to-end answer→Pause→FSRS / Submit→skipped regression on the actual Continue Practice path.
- Local checks pass; full Linux generated-app/browser/APK/package verification and physical-device review remain required. No production promotion was attempted.

## 2026-09-15 — PrepLadder visual quality pipeline implemented

- Kept stable question IDs/text ownership and replaced native-raster tight crop plus second background-color crop/resample with complete native frames. Opaque JPEG streams remain byte-identical; other rasters use a proportional lossless PNG safety canvas; graph/plot candidates use padded 288-DPI PDF regions.
- Added a complete generated inventory with PDF page/xref/coordinates, method, dimensions, hashes, question owner and risk flags. The audit-only quality stage checks hashes, size, aspect, meaningful/text boundary contact, neighboring questions and answer-revealing text, then emits high-risk-first source/production comparison sheets in batches of eight. Manual review remains explicitly pending.
- Added phone/tablet graph/table/clinical/diagram/multi-panel browser checks with fullscreen zoom, PWA offline precaching for every PrepLadder visual, APK inventory/PNG+JPEG checks, source-level regression contracts and CI artifact upload.
- Targeted presentation/FSRS/pipeline tests passed. Full local verification initially exposed two browser scripts missing from the Termux CI-only list and an overlong STATE handoff; both were corrected. Linux PDF regeneration, automated audit results, bounded sheet review, browser/APK/package CI and physical-device acceptance remain required; production was not promoted.

## 2026-09-15 — PrepLadder Linux generation cache failure isolated

- Candidate `6e4a1e989da34ba467f8340fa380b629ec891977` passed Engineering run `34994123213`, but full run `34994123200` stopped during source-visual generation before audit/browser/APK work: a failed native extraction had cached `None`, and a repeated xref attempted `dict(None)`.
- The narrow correction caches only successful native metadata and leaves failed native occurrences on the existing placement-specific PDF-region fallback. It does not change mappings, question IDs, crop policy, risk gates, structured-question behavior, or accepted Practice/FSRS flows. A source regression contract and all 46 available local checks pass; exact-head Linux verification remains required.


## 2026-09-16 — Shared scientific-notation presentation boundary

- Traced the defect to escaped plain-text rendering across all three session surfaces and a second bypass in enhanced Marrow explanations. Added one late, escape-first `nkScientificMarkup` boundary shared by Practice, timed CBT, Review, takeaways, PrepLadder explanations/tables, Marrow native structured text/tables and enhanced explanation/distractor text. Raw PrepLadder and Marrow records remain unchanged.
- The formatter emits semantic subscript/superscript markup for explicit powers, bounded biochemical/physiological formulae, blood gases, HbA1c, Greek receptor suffixes and ionic charges. It repairs only deterministic OCR losses such as Mg²■, Na■, pCO■ and HCO■■; ambiguous symbols remain visible. HTML-injection escaping remains a regression contract.
- Corpus audit: 424 PrepLadder and 695 Marrow learner fields exercise scientific markup. Remaining ambiguous surface loss is limited to seven PrepLadder records (5-10, 5-14, 14-9, physiology-9-18, physiology-20-7, physiology-23-11, physiology-26-20) and two Marrow stems (marrow__BIOCHEM_CH14_Q013, marrow__BIOCHEM_CH17_Q008). Another 55 PrepLadder and one Marrow explanation records contain residual placeholder glyphs and need source-backed per-record review rather than a global guess.
- Added generated-browser coverage for caret exponents in stems, ionic notation in choices/explanations and pCO₂/HCO₃⁻ display. All 46 available Termux checks pass. Full Linux generated-app/browser/APK/package verification and physical review remain pending; production was not promoted.

## 2026-09-17 — P0 fidelity campaign Phases 0–2

- Fetched and fast-forwarded canonical branch to required starting commit `758c0be2346d1b1459d699b1e4b40e9f90162cf3`; read all 418 campaign lines before repair. Phases 0 and 1 completed and reported. Starting Engineering run `35187611316` passed; full run `35187611321` failed at the native-explanation browser selector.
- Reproduced `physiology-9-6`, source page 253: all source rows exist; unpunctuated fibre value B was parsed as a repeated b label, dropping the fourth value and property. Options and correctOption=1 were unchanged.
- Phase 2 commit `212f632afe636304845b8cdb8b9ee06b0bc57721` adds paired structural integrity, duplicate-content validation, bounded unequal-source fingerprints, exact nerve regressions and canonical browser checks. Focused tests pass: 8 repaired option arrays, 18 invalid records, 48 semantic tables. Fourteen newly unavailable structures require Phase 3 source review, not guesses.
- Run `35198486810` passed the new nerve check, existing matching, ion, row-selection, combination and scientific-choice checks, then failed at obsolete `.feedback-body`. Correct native wrapper is the question-scoped `.nk-gold-explanation`; verifier correction retains semantic notation assertions and captures the native explanation screenshot.
- Phase 2 remains open pending new browser CI. User authorized campaign commits/pushes and requested GitHub browser verification without local installations. No production promotion, Phase 3 audit or acceptance claim.

## 2026-09-17 — PrepLadder Biochemistry 4-3 source-backed stem repair (local, uncommitted)

- Prior read-only investigation proved packaged `Biochemistry_QBank_Source.pdf` (SHA-256 `b500494d…a865ec`) page 82 question 3 stem `Which of the following tissues is unable to transport glucose independently of insulin?` and page 83 options A Hepatocytes / B Cardiac muscle / C RBC / D Neurons; canonical `4-3` instead carried the preceding question's fragment `GLUT3 c) Erythrocytes\n4.GLUT4 d) Skeletal Muscle`. Artifact `pwa.zip` from full run `35214461049` (SHA `7eed91c`) confirmed the record unchanged and normalizer `valid:true table:null`.
- Added `nkQuestionStemOverride` plus presentation-owned `stem` in `tools/question_presentation_core.js`: stable-ID + exact raw (1923549704) and hygiene-normalized (464611166) fingerprints; mismatch fails closed, wrong-ID returns null, and canonical data is never mutated. Table overrides were not abused for a stem-only defect.
- Added corpus regression in `tools/test_question_presentation_v1.py` covering raw and hygiene startup, idempotent repeated rendering, unchanged canonical options/order/answer (B/Cardiac muscle, `correctOption=2`), absent fragment, no table, fingerprint mismatch rejection and wrong-ID negative.
- Added a narrow generated-Practice browser regression in `tools/verify_question_presentation_browser.py` for exact prompt, four clickable canonical choices and canonical answer 2. Local Playwright is absent, so it was not executed locally.
- Evidence: focused test and all 46 `python3 tools/verify_local.py` checks pass (8 option normalizations, 8 invalid, 58 semantic tables). CI latest verified `7eed91c` rechecked live; the repair awaits Linux browser/build verification and user review. Phase 3 remains OPEN. No commits/pushes made; production untouched.

## 2026-09-17 — User-directed Biochemistry 5-10 dark-block diagnosis and narrow repair

- User explicitly authorized confirming remaining dark blocks and moving next steps; this is one exact-question repair, not completion of Phase 3 or Phase 4. Prior read-only session `ses_f506f49bdffe0yHbYCqcf4eXW1` established the deployed `77206c4` defect. Reconfirmed the full local canonical record: PrepLadder Biochemistry `5-10`, glycogen structure, source pages 101–101, A `1,2` / B `2,3` / C `1,2,3` / D `1,3`, `correctOption=3`. Raw and hygiene-normalized stem retain U+25A0 in `Glucose residues are connected by ■-1,4 linkage`, including after scientific markup.
- Re-extracted actual bundled PDF pages 101 and 117 with existing PDF.js in text-only Node mode (in-memory compatibility shims; no installations or source changes). Page 101 identifies Question 10 and the same four choices; PDF.js exposes the damaged glyph as `n`, whereas the canonical extraction contains `■`. Page 117 explicitly labels `Solution for Question 10` and states `Short chains of glucose residues are linked by α-1,4 glycosidic bonds (Statement 2)`. Direct PDF viewing is unsupported locally; this was text evidence, not visual/browser verification.
- Extended only `nkQuestionStemOverride` in `tools/question_presentation_core.js`: stable ID `5-10` plus exact fingerprint `236525982` (identical for raw and hygiene source) replaces the one confirmed square with α in presentation-owned stem. Generic scientific normalization is unchanged. No source-numbering additions, other candidates, canonical records/options/order/answer/pages, source PDFs, history, FSRS or persistence edits.
- Added actual-corpus raw/hygiene startup, exact full prompt/single-character replacement, idempotence, canonical immutability, answer C/3, no target square, source mismatch fail-closed, wrong-ID rejection and generic unknown-block preservation tests. Added generated Practice regression for exact stable ID, unchanged canonical source/pages, four enabled ordered choices, restored visible linkage/no square, answer C submission/feedback and unchanged post-answer prompt.
- Focused `python3 tools/test_question_presentation_v1.py` and all 46 `python3 tools/verify_local.py` checks pass (8 option normalizations, 8 invalid, 58 semantic tables). `python3 tools/verify_project_memory.py` and `git diff --check` pass. New browser regression was NOT executed: local browser/Playwright absent; no browser or container installation attempted.
- Live GitHub reconfirmed latest verified checkpoint `77206c41fb3a85fdac44f05efdcd89bbd33f1cf2`: Engineering `35220737574` and full `35220737666` both succeeded; the first network query timed out, retry succeeded. That checkpoint covers prior 4-3 work, not this uncommitted 5-10 repair. Next: exact-candidate Linux generated-browser/build/package verification and user review when authorized; Phase 3 remains OPEN and the broad scientific forensic inventory remains pending. No commits/pushes or production promotion; preserved untracked `.project-memory/STATE.md.orig`.

## 2026-09-19 — Resume P0 campaign; reconcile stale STATE; Phase 3 triage at f5daabe

- Resumed on `feature/marrow-canonical-full-current` at `f5daabe` (clean except untracked `.project-memory/STATE.md.orig`). Live GitHub recheck: Engineering `35228932515` and full `35228932475` both succeeded for `f5daabe`, so the prior STATE text claiming 5-10 was uncommitted/unverified was stale; STATE updated to the verified checkpoint.
- Local verification: `tools/test_question_presentation_v1.py` passes (4-3/5-10 stem OK, 8 repaired, 8 invalid, 58 semantic tables); `tools/verify_local.py` passes 46/46; `tools/verify_project_memory.py` passes; `git diff --check` passes.
- Re-ran `python3 tools/audit_question_structure.py --output build/question-fidelity` at `f5daabe`: PrepLadder 444 candidates (36 complete-generic, 22 source-backed, 272 false-positive, 114 incomplete-unsafe, 8 fail-closed); Marrow 273 candidates (173 false-positive, 100 incomplete-unsafe, 0 fail-closed). Source-review-required 219, unsafe-still-answerable 206, demonstrated rendered-cell defects still answerable 0.
- Narrowed true match-family residuals: PrepLadder `anatomy-9-1`, `anatomy-14-5`, `anatomy-40-10`, `anatomy-47-2` (fail-closed image-dependent) + combination-type `7-53`; Marrow 6 image-owned marked-structure matchings plus row-selection/figure-point cases. Bulk of incomplete-unsafe is combination/row-selection/enumerated adjudication, not proven parser loss.
- Next: adjudicate fail-closed/image-owned vs combination false-positives, then Phase 4 scientific-notation forensic audit per campaign. No commits/pushes in this resume session; production untouched.

## 2026-09-19 — Phase 3 residuals adjudicated (no product change)

- Wrote `.project-memory/PHASE3_STRUCTURE_ADJUDICATION_2026-09-19.md` at `f5daabe`: fail-closed 8 all correctly answering-disabled (4 known intentional + 4 image/source-dependent); true match-family residuals are image-owned or combination-type; bulk incomplete-unsafe is combination/row-selection/enumeration adjudication, not proven parser loss; 4-3/5-10 unresolved flags are an audit artifact (pre-override stem recorded), both build-verified.
- No new demonstrated failure class; no product/test/browser edits; no commits/pushes in this step. Local 46/46 pass; memory verify pass; audit --check deterministic pass. Production untouched. Next per campaign: Phase 4 scientific-notation forensic audit.

## 2026-09-19 — P0 memory pushed; Phase 4 forensic inventory complete (read-only)

- Committed and pushed `ee5d0dc` (STATE reconciliation at f5daabe + Phase 3 adjudication). No product code in that commit.
- Phase 4 forensic (no repairs): raw PrepLadder 117 with ■ / Marrow 2; post-normalization 60 questions with ■ (stem 8, option 3, explanation 56, structured 1); � 0. Category A: 5-10 (override-verified), 5-14 option B (explanation corroborates α-1,4, needs p102 source confirm), 4-12 explanation (same family). Category B ambiguous (no guessing): 14-9, physiology-9-18/20-7/23-11/26-20, Marrow CH14_Q013/CH17_Q008, F0/F1 + fragment classes. Wrote `.project-memory/PHASE4_NOTATION_FORENSIC_2026-09-19.md`. Local 46/46 + memory verify pass. Next: Phase 5 per-record source-backed repair starting with 5-14 p102 when authorized.

## 2026-09-19 — Phase 5 first repair: Biochemistry 5-14 option override (local, CI pending)

- Source evidence: bundled PDF p102 Q14 option B carries `■-1,4` in the authoritative text layer; p123 solution states `Glycogen phosphorylase cleaves α-1,4 linkages (Option B)`; the record's own explanation corroborates. α is source-confirmed, not guessed.
- Added `nkQuestionOptionOverride` in `tools/question_presentation_core.js` (stable-ID + raw/post-repair fingerprints `1528761351`/`2762270306`; mismatch fails closed without mutation; in-memory display copy only, stored source unchanged; idempotent via post-repair fingerprint + presentation cache). Wired into `nkQuestionPresentationFor` alongside the stem override.
- Added `BIOCHEM_5_14_OPTION_OK` unit regression (raw/hygiene startup, exact α, answer 4, letters/order unchanged, stored `■` intact, 10 mismatch mutations fail closed unmutated, wrong-ID null) and a generated-Practice browser regression (fixed choices, no ■, answer D, screenshot). Corpus counts unchanged (8 repaired, 8 invalid, 58 semantic tables); local 46/46 pass.
- Caution handled: an early Python-side fingerprint (`939228177`) mismatched JS serialization (Python uses `', '`/`': '` separators); recomputed JS-side before hardcoding.
- Next: commit/push, watch Engineering + full CI, then user preview review. Remaining Phase 5 queue unchanged (4-12 + ambiguous set need per-record source work).

## 2026-09-19 — 5-14 repair build/browser-verified at f19a866

- First 5-14 candidate `5c99208` passed Engineering but failed the full run on the new browser assertion (`post-answer presentation changed`): submitted options render as `div`, not `button`, so the tag-specific selector found zero nodes. Fixed in `f19a866` with tag-agnostic `.option-list .option` / `.option-text` checks mirroring the 4-3/5-10 pattern. No product logic changed.
- Exact-head Engineering `35429941297` + full `35429941288` both succeeded, including `BIOCHEM_5_14_OPTION_OK` and `BIOCHEM_5_14_BROWSER_OK exact_alpha=true no_square=true choices=4 canonical_answer=4`. STATE checkpoint advanced to `f19a866`. Production untouched; user preview review pending. Next per campaign: per-record Phase 5 repairs from authoritative pages only.

## 2026-09-19 — Phase 5 second repair: Biochemistry 4-12 explanation verified at bf1be33

- Source evidence (pypdf text layer): PDF p101 Q10 stem carries ■-1,4 while p117 solution states "Short chains of glucose residues are linked by α-1,4 glycosidic bonds (Statement 2)"; PDF p102 Q14 option B carries ■-1,4 while p123 solution states "Glycogen phosphorylase cleaves α-1,4 linkages (Option B)". Both 4-12 explanation embeds are the same glycogen family, so α is source-confirmed, not guessed.
- Added `nkQuestionExplanationOverride` in `tools/question_presentation_core.js` (stable-ID + 7-field explanation fingerprints raw `2733095777` / repaired `1814125949`; mismatch fails closed; in-memory display copy only via `replaceAll('■-1,4','α-1,4')`; stored source unchanged) and wired it into `nkQuestionPresentationFor` alongside stem/option overrides.
- Added `BIOCHEM_4_12_EXPLANATION_OK` unit regression (raw/hygiene startup, exact 2× α, answer 3, options/order unchanged, stored ■ intact, 10 mismatch mutations fail closed unmutated, wrong-ID null). Corpus counts unchanged (8 repaired, 8 invalid, 58 semantic tables); local 46/46 pass.
- First candidate `64ce88f` passed Engineering but failed the full run: the new browser check asserted repaired TEXT inside Practice feedback, but the built app renders Biochemistry explanations from source-PDF solution images (`repair_source_solution_renderer`), so no explanation text is learner-visible there. Fixed in `bf1be33`: browser check now asserts the PDF-image surface intact, no ■ on the Practice surface, and the live display copy repaired (serves Review/takeaway surfaces) via `__presentationQuestion` probe.
- Exact-head Engineering `35451848708` + full `35451848704` both succeeded, including `BIOCHEM_4_12_BROWSER_OK exact_alpha=true no_square=true choices=4 canonical_answer=3`. STATE checkpoint advanced to `bf1be33`. Production untouched; user preview review pending.
- Known follow-up (not Phase 5 scope): 4-12's explanation tail embeds the full next-chapter glycogen dump (Q1-17 + answer table); notation fixed, content-trim needs source review. Next per campaign: per-record Phase 5 repairs from authoritative pages only (ambiguous set).

## 2026-09-19 — Phase 5 ambiguous queue adjudicated (no product change)

- Resumed at `4c00bd9` (product code identical to verified `bf1be33`; tree clean). Re-checked the full remaining Phase 5 queue per record against authoritative source text layers (pypdf; installed pure-python `fonttools` for Marrow CFF/Symbol fonts — environment only, untracked).
- Deterministic sweep first: corpus-wide scan for further `■-1,4` / `■-1,6` family instances found only the four already-repaired display sites (stored strings intentionally unchanged). Deterministic set is empty.
- All 7 Category-B candidates stay flagged with fresh evidence: 14-9 solution p412 carries identical ■; 9-18 solution p291 carries identical blocks (first ■ already covered by safe generic Na+ rule); 20-7 solution never renders the V symbol; 23-11 solution writes bare UV/P yet keeps bare ■; 26-20 solution p766 keeps ■ (value arithmetically 1/3 but form unknown + diagram-owned, so not reconstructed); Marrow CH14_Q013 text layer garbled with `/uni25A0` leak even with fonttools (Δ9 inferred-only, forbidden); CH17_Q008 text layers unusable.
- Wrote `.project-memory/PHASE5_AMBIGUOUS_ADJUDICATION_2026-09-19.md`; updated STATE item 6. No core/test/data edits; no commits in this step yet. Production untouched. Next: commit handoff, then Phase 6 cross-surface learner regression per campaign.

## 2026-09-20 — Canonical image-automation readiness handoff

- User clarified ownership: image integration belongs to automations, not the primary agent. The P0 campaign's temporary image priority lock is lifted only for that automation lane; remaining fidelity work and source-quality gates remain open.
- Audited canonical `feature/marrow-canonical-full-current` at `356cce4`, matching remote. Exact-head Engineering `35453226391` and full Android/PWA/browser/APK/package run `35453226292` succeeded; production was not promoted. Local 46 checks passed. Image registry validation, progress `--check`, and coverage `--check` passed without modifying image state.
- Created `.project-memory/IMAGE_AUTOMATION_READY_2026-09-20.md` with the live-base, ownership, first Biochemistry reference, rendered-page review, coverage and reconciliation contract. Corrected stale image ownership/priority instructions and scientific-notation CI status. No image assets, bindings, source data or product code were changed. New handoff commit must receive its own exact-head CI before automations treat it as build-verified.


## 2026-09-21 — Biochemistry explanation canonical-memory drift repair
- Re-read `docs/MARROW_EXPLANATION_AUTOMATION_RUNBOOK.md`, `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md`, mandatory project memory and implementation guidance from live canonical `0c57fd4deb0a0ffb6ea57865bef56ac00b52c1e0`.
- Reconciled derived `STATE.md` explanation memory with the deterministic canonical full-corpus inventory: **615 enhanced / 2,096 pending / 2,711 total**, fingerprint `2ad7006f78607d0974269e4aad0baaed9cba6124560885adb3e30f3e6651ce14`.
- Recorded Biochemistry Ch12 Q1–Q10 as FULLY_VERIFIED_HISTORY; no new explanation content was authored in this repair.
- Exact next Biochemistry source-order candidate after reacquiring a free explanation lane: Ch12 Q11–Q14. Raw source remains immutable; production promotion remains prohibited.

## 2026-09-22 — Core reliability hardening candidate

- Branched `feature/marrow-core-reliability-hardening-20260922` from freshly fetched canonical `105cf02e358d8f869d745e698fc4faa32d777c92`; preserved untracked `.project-memory/STATE.md.orig`.
- Added revisioned transactional learner-state persistence with pending journal, last-known-good recovery, visible retryable errors, and synchronous pagehide/background state + outbox capture.
- Added a versioned normal-Practice checkpoint, explicit active/paused/suspended/terminal lifecycle, Resume-or-Discard replacement gate, atomic/idempotent Practice and CBT submit, restart-safe exclusive CBT, and transient Review cleanup.
- Split normal Practice cloud sync from special sessions. Same-session progress merges per-question; different sessions and membership mismatches surface conflicts; terminal state cannot regress. Sync metadata now has journal/LKG recovery.
- Expanded unit/contracts for corruption, interrupted/quota failures, destructive-transition rollback, duplicate submit, CBT exclusivity, concurrent/offline merge behavior, outbox safety, and special-mode isolation. Expanded the generated browser loop for a fresh-context restart, bookmark persistence, major navigation/back smoke, phone/iPad viewports, Analysis and complete Review Solutions navigation.
- `python3 tools/verify_local.py` passes all 47 local checks. Full ordered Linux PDF/generated-browser/Android/PWA/APK/package CI and physical-device proof remain pending. Production was not promoted.

## 2026-09-22 — BC3 canonical reconciliation candidate

- Fetched canonical `d0a376f6e0bc687595b5b2c8f6dd73e884838e7a` and merged complete donor `db1f9ce` on `feature/marrow-bc3-reconcile-20260922`. No merge conflicts or content/image/automation changes. Regenerated explanation inventory through its owner; byte-identical to canonical.
- Donor dual-green runs: Engineering `35714734167`, Android/PWA `35714733642`. Added same-lifecycle real-answer restart/bookmark and read-only Review FSRS isolation assertions.
- Local runner now consistently classifies generated browser verifiers as CI-only, including canonical's new Anatomy Ch7 sentinel. Combined candidate CI pending; BC4 has not started.

## 2026-09-22 — BC3 canonical, BC4 started afterward

- Re-fetched canonical (still `d0a376f`), verified dual-green candidate `54f7d0fe210683e6236a00a6669f145734ae0335`, and fast-forwarded canonical to that exact SHA. Engineering `35738354092`; full Android/PWA/browser/APK/package `35738352700`; preview `https://1ece471a.nk-qbank.pages.dev`. Full Practice lifecycle, restart/bookmark, FSRS, and read-only Review isolation passed. All eight donor commits through `db1f9ce` are ancestors. Canonical content/image/automation paths remained byte-identical; inventory regenerated without differences.
- BC4 began on `feature/marrow-bc4-question-integrity-20260922` afterward. Real-handler tests reproduced ten failure cases grouped in the BC4 ledger. Shared interaction transaction and identity validation added, plus phone/tablet browser matrix. Canonical and production remain unchanged by BC4 until verification completes. Physical Android is not claimed.
- BC4 follow-up: full build adds an Android 35 emulator job using the exact uploaded APK, covering native Back and process death/restart at phone and tablet sizes. Browser runs exposed a special-mode stale modal (fixed at shared route completion) and two new test-fixture assumptions (initialized skip map/current CBT control). Final native/browser verification pending.

## 2026-09-23 — BC4 packaged Android continuation

- Resumed `feature/marrow-bc4-question-integrity-20260922` from `88febeb63192d13f2e5d5224b689d22af9f66653`; canonical remained `54f7d0fe210683e6236a00a6669f145734ae0335`. Read the BC4 ledger, prior session, commit range, workflow and Android driver before continuing. Preserved untracked `.project-memory/STATE.md.orig`.
- Original build `35763732659` failed only in the packaged Android job at the post-Pause `waitForURL('#dashboard')`; Engineering `35763733376`, regular build, and generated phone/tablet checks passed. Diagnostic `2cdb0e4` / run `35814299885` proved the packaged app was already on dashboard with lifecycle `paused`, index 1, no review overlay and visible Continue Practice. The driver had waited for a WebView document load after a same-document hash change.
- Replaced URL load waits with exact observable hash/state waits. Run `35815128443` then passed Pause, process restart, exact order/index, bookmark and attempt checks but timed out after native Back. Diagnostic `92fd7a8` / run `35816128887` proved Android Back moved `#practice` to the original empty-hash URL, where the app's router renders Home; screenshot and foreground activity confirmed it. Updated the driver to recognize that valid dashboard form while requiring rendered Home, a changed route and the same session/index. No product code or assertions were removed.
- Final substantive driver SHA `088f9906ed65f779f1dd0084459e7649973ee0a3`: local 50-check suite and 20 real-handler integrity assertions passed; Engineering `35817762986` succeeded; full Android/PWA run `35816916138` succeeded, including packaged phone and tablet APK launch, answer/bookmark, rapid Next, Pause, force-stop/reopen, native Back, double Submit, single result, Analysis → Review Solutions and read-only Review/FSRS isolation. Generated browser phone/tablet matrix, BC3 Continue Practice/CBT/Review/FSRS lifecycle, APK/package and PWA steps passed. Artifacts include Android screenshots and JSON reports. Classification: CI harness synchronization defect; no new product defect found. Physical Android device verification remains outstanding. BC4 promotion still requires exact-head candidate checks after this documentation change and a fresh canonical-head read.

## 2026-09-23 — BC4 promoted to canonical after exact-SHA gates

- Documentation-inclusive BC4 candidate `43328c12ffde4c79db2214f7a0a351b2d326b5d7` passed Engineering `35817957824` and full Android/PWA `35817948137`, including the packaged Android 35 emulator phone/tablet regression. Generated browser question-integrity and BC3 Continue Practice/CBT/Review/FSRS checks remained green.
- Re-fetched canonical at `54f7d0fe210683e6236a00a6669f145734ae0335`, confirmed it was an ancestor of the verified candidate with zero divergence, and fast-forwarded it without force to `43328c12ffde4c79db2214f7a0a351b2d326b5d7`. The canonical push itself passed Engineering `35818707731` and full Android/PWA `35818707723` on that SHA. Android job printed `ANDROID_QUESTION_INTERACTION_OK` after phone and tablet; generated browser matrix and BC3 lifecycle passed. No physical Android device was used and production was not promoted. This documentation record extends the canonical checkpoint; resolve its live SHA and exact CI in GitHub.

## 2026-09-23 — Study UI audit and first narrow fix batch

- Started from live canonical `4416250`, clean except pre-existing untracked `.project-memory/STATE.md.orig`. The exact prior Engineering and full runs were green. Android Termux could identify a physical phone but lacked input-injection and screenshot capability, so no physical APK behavior was claimed. The user reported a short preview pass for Review Solutions and CBT, with deeper testing still open.
- Added a generated-app screenshot walkthrough at 320×640, 390×844, simulated 150% larger text at 390×844, and 820×1180. The first baseline run `35821738540` captured 68 states with no page errors or document-level horizontal overflow. Inspecting those screenshots identified clipped long question context, source-question rather than session-position labels in the CBT final grid, crowded 320px status labels, and squeezed mobile Analysis metadata.
- Fixed the shared CBT/Practice grid renderer and CSS, shared question context CSS, and Analysis page header CSS. Corrected run `35822409845` captured 72 states and passed the browser assertions for grid numbering, label bounds, context bounds and CBT submission. Its build job passed; the packaged Android emulator job was still running when this entry was drafted. A follow-up adds image/viewer/explanation capture and increases grid status text size; resolve the final exact SHA and workflows before calling that follow-up build-verified. Production was not promoted.

## 2026-09-23 — Multiple paused chapters continuation (Codex handoff completed locally, CI pending)

- Took over Codex session `01a0cca4` multi-pause work from `8666d3b` (`feature/marrow-canonical-full-current`), which ended on usage-limit with 8 uncommitted files. Verified the diff preserved single-pause/BC3/BC4 contracts, FSRS pause/submit boundaries, and CBT/Review isolation before completing it.
- Implementation: `normalPracticeCheckpoints` collection + legacy `normalPracticeCheckpoint` latest-alias; `nkStartSessionReliably` auto-pauses live normal Practice (paused/suspended) instead of Resume-or-Discard; Home Continue resumes directly for one saved session and opens a Paused Practice chooser (`#nk-practice-sessions`) for several; per-ID resume/discard via `nkResumePracticeById`/`nkDiscardNormalPractice(sessionId)`; no-arg discard refuses to guess when several are saved; legacy replacement shim preserves single-session discard semantics only for the single-saved case; cross-device sync queues/merges per session ID and drops the obsolete `different-session` conflict while keeping membership-mismatch fail-closed.
- Hardening added in this pass: no-arg discard shows the chooser instead of deleting the most recent; replacement-discard path discards only the single saved ID explicitly; exported `nkPracticeSavedSessionsDialog` for testability. No question content, images, inventories, automation files, or unrelated UI touched.
- Local verification: `python3 tools/verify_local.py` 50/50 pass including `CONTINUE_PRACTICE_BEHAVIOR_OK`, `CONTINUE_PRACTICE_CONTRACT_OK multiple_paused_chapters=true`, `DURABLE_PERSISTENCE_BEHAVIOR_OK`, `CROSS_DEVICE_SYNC_BEHAVIOR_OK`; `node --check` clean; `verify_build_pipeline.py` and `verify_project_memory.py` pass. Generated-browser multi-pause regression (`MULTIPLE_PAUSED_CHAPTERS_OK`) and full Android/PWA/APK/package gates remain CI-only and pending on the exact candidate SHA. Production untouched.

## 2026-09-23 — Presentation browser isolation under multi-pause (same candidate)

- Full build `35833171312` on `0d927e0` failed twice at `verify_question_presentation_browser.py:434` (10-4 option click, element never stable) while Engineering stayed green. Parent `8666d3b` was green on the same step, so the multi-pause accumulation is the prime suspect: `open_practice` uses single-question `practiceOne`, which previously discarded the prior session via the replacement dialog but now retains every peek as a paused checkpoint.
- Fix (test setup only, no assertion weakened): `open_practice` now resets `activeSession`/`normalPracticeCheckpoints`/`normalPracticeCheckpoint` before each presentation open, restoring the hermetic single-session conditions the presentation checks were written for. Multi-pause accumulation itself remains explicitly covered by `verify_continue_practice_browser.py` (`MULTIPLE_PAUSED_CHAPTERS_OK`). No product code changed in this step.

## 2026-09-23 — Multi-pause browser diagnosis and reliability continuation

- Run `35835052983` on `5f5a756` still failed at the exact 10-4 Playwright click after fixture isolation, so accumulation was not the root cause. Diagnostic runs `35844859167` and `35845434978` showed the option fixed at top 704.40625 px before click, no active button animation, and a 1 px 704.40625 ↔ 703.40625 shift during pointer movement with scroll position fixed. The pre-existing `.option:hover{transform:translateY(-1px)}` moves the hit target under a pointer left by the preceding presentation check; the removed replacement dialog made that pointer state reachable. A narrow question-option hover override now keeps the hit target stationary; all original browser assertions remain.
- Three-session tests exposed a separate product issue: starting/resuming another session rewrote an already paused checkpoint's timestamp. Skip re-saving already paused sessions, skip paused elapsed accrual on pagehide, preserve terminal sync tombstones beyond 100 entries, and honor a newer legacy alias when normalizing by ID. Reject stale direct resume of terminal sessions and duplicate rapid starts. Extend the browser path with three actual chapter sessions, answers/FSRS, reload, chooser resume, special-mode isolation, completion/discard isolation, pagehide, double Pause and phone/tablet chooser captures. Focused Practice and sync tests pass locally; final CI and packaged Android checks still pending.
- First consolidated candidate `14f5c94` failed Engineering `35846603048` on Node 20 in a same-millisecond alias test: B and A had equal `updatedAt`, so the latest alias still pointed to A. The full run `35846591959` stopped at the same early gate before browser/APK steps. Fixed local checkpoint revision times to advance past the collection maximum, made latest-alias ties deterministic, and froze the test clock to cover that case. Ordered membership is now compared directly during cloud merge, including a forged matching-hash regression. These changes require fresh exact-SHA gates.
- Candidate `df2517a` passed Engineering `35846986087`, but full run `35846984426` still failed at the 10-4 click. The first hover override targeted the older V11.3 question wrapper; the generated browser renders V11.4 `.nk-v114-session` from `apply_session_experience_v2.py`. Moved the stationary-hover rule to that active renderer, removed the ineffective older override, and added a generated-app contract assertion. The browser click and correctness assertions remain intact. Fresh exact-SHA gates are required.
- Candidate `fabfabe` passed Engineering `35847651721` and the previously failing presentation browser step in full run `35847643848`. The run then reached Continue Practice and exposed a new three-session fixture error: it looked for Biochemistry inside `SUBJECT_QBANK_DATA`, which contains only Physiology and Anatomy. Candidate `2482d17` uses three real Physiology chapters, opens their Practice builder, passed Engineering `35848537504`, and passed the Continue Practice browser step in full run `35848530206` (remaining build/Android steps pending at this writing). The packaged Android extension had the same subject-bank fixture mistake and is corrected in the next candidate. Home now displays the saved-session count and offers the chooser even while one of several saved sessions is active; a focused regression covers that route.

## 2026-09-23 — Anatomy candidate build gate repair

- The newest failed full build, `35872090777` on `efd2ca3`, stopped in canonical explanation wiring: Anatomy Ch7 Q11–Q21 was authored as `candidate-rollout`, which inventory correctly excluded, while the runtime wiring rejected the file. Source-slice audit `35872090779` passed. The candidate is still unapproved and remains outside the 635 enhanced runtime explanations.
- Updated `apply_canonical_bank_explanation_wiring_v1.py` to validate candidate identity/count but skip candidate packaging. Unknown statuses and malformed batches still fail closed. Focused isolation/status checks passed; `python3 tools/verify_local.py` passed 50/50. Exact-head Engineering and full CI are required before calling this branch build-verified. Next: source/content validation, approved rollout test and inventory refresh, then exact-head gates and canonical reconciliation. Production was not promoted.
- That fix was committed as `2507aeb`. Engineering `35880772345` and full Android/PWA/browser/APK/emulator run `35880725166` passed on that exact SHA; preview `https://05ffd6d3.nk-qbank.pages.dev` deployed and production was skipped.

## 2026-09-23 — Anatomy Ch7 Q11–Q21 approval candidate

- Rechecked the unchanged canonical base and branch ownership. Audited all 11 canonical source IDs, stems/options/keys, explanations, figure metadata, and `pass` review statuses. The authored takeaways, display text, emphasis and three keyed distractor rationales passed source-aligned static validation. External embryology references supported the key discriminators; no source or answer data changed.
- Changed only this batch from `candidate-rollout` to `approved-rollout`; extended the Anatomy rollout validator to Q21; added a generated-browser Q19 pancreatic-divisum regression to the Marrow browser entrypoint; regenerated inventory to **646 enhanced / 2,065 pending / 2,711** with fingerprint `b32859a10f0aa88af8da1d3ef34cba64be946153fff2c06fd507620306ef28b2` and unchanged source/flag counts. Full handoff is `.project-memory/AUTOMATION_HANDOFF_ANATOMY_EXPLANATION_CH07_Q011_Q021_2026-09-23.md`. Exact-head content CI and canonical reconciliation remain pending; no physical-device claim or production promotion.
- Content commit `858c808` passed Engineering `35882922040`; full run `35882880054` reached the new Q19 browser regression and showed the manual FSRS dock absent after selecting wrong option A. That is the existing FSRS contract: wrong answers receive automatic Again, while the manual dock follows a correct answer. The regression now selects canonical correct option B while retaining all explanation and dock assertions; fresh exact-head full CI is required.
- Final batch head `43b1839` passed Engineering `35883623729` and full Android/PWA/browser/APK/emulator run `35883618689`, including the Q19 browser regression. PR #67 was reconciled into canonical as merge commit `7215d8f`. Canonical inventory refresh `35885212779`, Engineering `35885212819`, and full run `35885212827` all passed on that merge SHA. Preview `https://0e14d788.nk-qbank.pages.dev` deployed; production promotion was skipped. The batch is build-verified and reconciled; physical Android review remains separate.

## 2026-09-23 — Home UI integration audit candidate

- Canonical `81333f0` already includes the verified multiple-paused-chapters implementation at `cb3f44b`; the previous statement that canonical lacked it was incorrect. Merged the separate Home/Analysis UI branch into an isolated audit candidate based on current canonical, retaining the Anatomy explanation rollout and all automation-owned content. The user found a blocker: after two saved Practices, resuming and submitting one can make Home Continue Practice say to exit or submit the previous test. Promotion is stopped until this sequence and adjacent lifecycle paths pass generated browser and packaged Android checks.
- Root cause in the continuation guard: Review Solutions persists a read-only `activeSession` with mode `review`, and Home Continue rejected it as an unfinished interactive session. Resuming saved Practice now replaces that read-only review transactionally while timed CBT and interactive special modes remain guarded. A stale submitted/completed/discarded Practice `activeSession` is excluded from continuation and cannot be re-paused. Added focused unit checks and a generated-browser path with exactly two saved chapters, submit A, direct Home resume B, pause B, open A's Review Solutions, return Home, and resume B again. Exact-head CI is pending.
- Product commit `b36aa00b374c16d0e9946928061881ce8cc4fe80` passed Engineering `35898871319` and full Android/PWA `35898871311`. The generated browser printed `TWO_PAUSED_AFTER_SUBMIT_BROWSER_OK`, `THREE_PAUSED_PRACTICE_BROWSER_OK`, and `CONTINUE_PRACTICE_BROWSER_OK`; the packaged APK ran phone/tablet emulator multi-pause, force-stop/reopen, native Back and question-interaction regressions. All build, source, sync, FSRS, CBT, Review, content, packaged-contract, and preview-deploy steps passed. Preview: `https://a3be6b63.nk-qbank.pages.dev` (branch alias `https://feature-home-polish-canonica.nk-qbank.pages.dev`). Diff against canonical contains no `data/marrow`, workflow, or canonical explanation-wiring changes. User review, canonical reconciliation, physical in-place APK/data-preservation and real-device sync remain outstanding; production untouched.
- Before the documentation-only follow-up finished, live canonical advanced from `81333f0` to `13f5b7f` with Anatomy Ch8/Ch9 and Biochemistry Ch13 explanation batches. Canceled stale audit run `35967509289`, merged live canonical into the isolated audit branch without conflict, and preserved all automation-owned content. Re-run local and exact-head CI on the integration commit before recommending acceptance.
- Integrated checkpoint `b6dd246d2e1b81c5dfd3d848108008871cb5984f` passed 51 local checks, Engineering `35967933879`, and full run `35967933880` (build plus packaged Android phone/tablet emulator). Browser reported `TWO_PAUSED_AFTER_SUBMIT_BROWSER_OK`, `THREE_PAUSED_PRACTICE_BROWSER_OK`, and `CONTINUE_PRACTICE_BROWSER_OK`; packaged APK JS/product checks and 84 responsive UI captures passed. Emulator reported `ANDROID_MULTI_PAUSE_OK` on phone/tablet and `ANDROID_QUESTION_INTERACTION_OK`. Preview `https://60a1e660.nk-qbank.pages.dev`; artifacts `study-ui-audit`, `android-question-interaction`, `V11.7-android-pwa` on run `35967933880`. Canonical was still `13f5b7f` at final check. This final note changes only memory; no canonical or production push occurred. Physical in-place APK/data-preservation and real-device sync remain unverified.

## 2026-09-24 — User acceptance and canonical promotion

- The user confirmed the repaired preview works and explicitly requested promotion. Promote the clean audit branch by fast-forward from canonical `13f5b7f`, keeping production untouched. Product checkpoint `b6dd246` passed Engineering `35967933879` and full Android/PWA/browser/APK run `35967933880`; subsequent audit commits changed only memory. Recheck the live canonical head before push and require canonical-head CI after push. Physical in-place APK/data-preservation and real-device sync remain separate.

## 2026-09-24 — Bank-aware module and source-backed PYQ candidate

- The user approved the Marrow-like QBank workflow plan and prioritized a bank
  architecture that future question sources can use. A separate worktree/branch
  was created from the locally known canonical ref so active UI and automation
  worktrees stay untouched.
- Source inspection found 27 PrepLadder topics explicitly titled Previous Year
  Questions (1,118 questions: 346 Biochemistry, 362 Physiology, 410 Anatomy).
  The current Marrow ED8 import has no PYQ-labelled topics or exam/year fields.
- The candidate module builder now reads the shared bank registry, stores exact
  subject/bank/topic scope keys, keeps legacy frozen modules readable, supports
  All questions and source-backed PYQ filtering, and offers a PYQ topic shortcut.
  The PrepLadder registry adapter derives the `pyq` collection only from the
  explicit source topic title; raw question imports stay unchanged.
- This is an implementation candidate only. No generated build, CI, or physical
  device verification was run in this session; do not call it released.

## 2026-09-25 — QBank flow clutter audit and cleanup candidate

- The user physically reviewed the bank-aware custom module/PYQ preview and
  confirmed it works, then identified duplicate actions as the next priority.
  No canonical or production promotion was authorized.
- Fresh browser captures from run `36042991236` and click-handler tracing found
  repeated Home module/FSRS/test/history actions, a Tests Practice/Timed mode
  overlap, two timed sources opening the same builder, repeated More navigation,
  an overly long Insights topic list, and a duplicate result Review action.
  Evidence and step-by-step findings are in
  `docs/audits/qbank-flow-2026-09-25/`.
- Candidate changes conditionally show Home Continue only for real work, keep
  one module entry, use one subject/topic timed builder, retain separate
  wrong/bookmarked quick tests, remove repeat More links, collapse Insights
  topics behind Show all, and keep the chapter Practice/Timed Test distinction.
  Local and exact-head generated CI plus physical review are required before
  accepting this cleanup.
- Engineering run `36047623132` passed at `5409aff`. Build run `36047635922`
  stopped in the new More audit assertion because it assumed `libraryPage`
  followed `morePage` after all transformations. The assertion now bounds the
  next function generically; rerun the full build on the new exact head.
- At `8ab9f7e`, Engineering `36048520277` passed and build `36048498843`
  reached generated product contract verification. That contract still expected
  the old Tests labels “Full Question Bank” and “Question Source”; update it to
  protect “Choose subjects and topics” and “Quick test” in the new flow.
- At `c1ba435`, Engineering `36049571030` passed and build `36049552630`
  reached the final generated-app check. The workflow also contained stale
  grep checks for those two old labels in generated and packaged assets;
  both now assert the new Tests labels.
- At `4542160`, Engineering `36050418627` passed and build `36050395851`
  reached browser capture. The 320px Home first study action overlapped the
  bottom navigation in fresh state. Move study sets and subjects ahead of the
  streak card, increase the create action to 44px, and retain a coordinate
  assertion for the next capture run.
- `c863f1f` passed Engineering `36051479141` and full browser/PWA/APK/Android
  `36051447529`; preview is `https://6ac240e8.nk-qbank.pages.dev`. Fresh Home,
  320px Home, and Tests after captures are linked from the audit report. A
  capture-only condition was then fixed so the PYQ screenshot avoids a toast
  caused by toggling the already selected PrepLadder bank. Physical review of
  the cleaned flow and a saved-module state are outstanding.
- The user rejected the clean Home visual at `fcd9869`: Today's Focus supplied
  the Home feeling, and the streak belongs at the top. They accepted the
  remaining navigation cleanup. Official Marrow QBank and PrepLadder QBank/
  streak references were inspected. Restore the streak above a persistent
  Today’s Focus card; give fresh users an honest subject jump, resume active
  Practice or unfinished modules when present, and suppress a duplicated
  Continue button on the focused saved-module card. Keep Tests, More and
  Insights simplification intact. Capture both fresh and saved-module Home.
- `8339764` passed Engineering `36078896597` and full browser/PWA/APK/Android
  `36078893896`; preview is `https://eaa6041b.nk-qbank.pages.dev`. Fresh,
  320px and saved-module Home captures confirm the top streak and persistent
  Focus hierarchy, a visible 320px action, and one module Continue button.
  The user has not yet physically accepted this revised Home.

## 2026-09-25 — Custom module topic picker refinement

- The user confirmed the restored Home flow works, then reported that the
  custom module topic step is hard to use: a small nested scroll area, tiny
  rows, and a jump to the top after selecting a deep topic.
- Fresh phone/tablet captures at `d34ce8c` from full run `36095684713`
  confirmed a 390px list pane, 50px rows, 10.5px topic titles, and a Continue
  action below the initial phone viewport. The tap handler called `render()`.
- The candidate replaces the inner pane with normal page scroll, adds topic
  search and per-bank selection, enlarges row targets and builder text, keeps
  a selected-count Continue action above the bottom nav, and updates topic
  selection in place. The duplicate bottom Back controls were removed; the
  top Back control remains. Bank/topic IDs and pool logic are unchanged.
- Local source checks passed (`verify_local.py`: 51 checks, PDF pipeline skipped
  on Termux). Exact-head CI, after screenshots, and physical review are next.
- `bb341b6` passed Engineering `36097427788`, but its first capture showed
  Continue below the viewport on long phone lists and a half-width tablet
  list. `b48b45c` fixed the phone action; its browser run `36098059617`
  failed the new tablet-width assertion because a later PWA stylesheet forced
  two topic-group columns. `08b9e37` overrode that rule with builder scope.
- Browser capture on `08b9e37` passed at 320px, 390px, larger text, and tablet,
  including deep-row selection without a scroll jump, search, full-width
  tablet rows, and fixed phone Continue. Before/after evidence is in
  `docs/audits/custom-module-topics-2026-09-25/`.
- Final interaction cleanup hides the per-bank group action when just one bank
  is selected; with two banks, each group can still select its own topics.
  Exact-head full CI for this last cleanup and device review remain pending.

## 2026-09-25 — PYQ topic scope and Questions-step cleanup

- The user confirmed the revised Topics step works, then found that the
  Questions-step Source All/PYQ choice was redundant and misleading. Adding
  PYQ topics had secretly set a PYQ-only filter, so regular topics selected
  alongside them contributed no questions.
- The candidate removes that Source control and hidden draft filter. Selected
  regular and source-labelled PYQ topics now both contribute to the eligible
  question pool. The PYQ quick action still preselects the source-labelled
  topics across available banks; saved modules retain frozen question IDs.
- Node behavior checks cover mixed regular/PYQ scope and absence of the Source
  control. The generated browser capture now exercises a mixed selection.
  Engineering `36101824054` passed at `a94b329`; full browser/PWA/APK/emulator
  run `36101826646` is pending. Physical review remains.

## 2026-09-25 — Question-linked personal notes candidate

- Official Marrow QBank guidance emphasizes learner-written notes, bookmarks,
  custom modules, and revision. The first study-intelligence increment adds a
  compact note editor after answering in Practice and in Review Solutions.
- Notes use stable question IDs, durable local state, and one sync envelope per
  note, including a removal tombstone. Saving does not rerender the question,
  preserving reading position. No Home action was added.
- Local behavior, persistence/sync, and build-order checks pass. Generated
  browser and full APK/PWA/emulator verification are still pending.
- First generated browser run `36102658065` reached the note journey: save,
  reload, and Review controls worked, but an answered Practice reload reported
  `window.sourceSubjectV14 is not a function`. The source-PDF helper was
  installed in a later body script than initial Practice rendering. The
  renderer now derives its subject directly from the question's existing
  subject/ID/source reference; the browser check requires the note to appear
  immediately after reload with no manual navigation. Rerun full CI.
- `21e28e2` passed Engineering `36103198537` and full browser/PWA/APK/Android
  emulator `36103201213`. The generated browser journey passed note save,
  immediate reload, Review display, and removal. The preview
  `https://d3efc7b0.nk-qbank.pages.dev` serves the final note marker and has no
  Source control. Phone captures were inspected and saved in
  `docs/audits/study-scope-and-notes-2026-09-25/`. Physical device acceptance
  and production promotion remain open.

## 2026-09-25 — Read-only saved notes and the next notes page

- User checked the preview and accepted the existing notes functionality,
  then requested Save to close the editor and display a non-editable card with
  Edit and Delete in the top right.
- The question note surface now has explicit empty, editing, and saved states.
  Save returns to read-only text; Cancel preserves the stored note; Delete
  writes the existing sync tombstone. Failed saves keep the draft visible.
- More → My notes is a searchable cross-bank index of saved recall cues with
  direct Practice entry for available questions. It adds no Home action.
- The existing generated browser journey was updated for save, reload,
  edit/cancel, notes index/search, cross-bank entry, Review and delete. Local
  source verification passed; exact-head generated CI and physical review
  are pending.
- Engineering `36113070427` passed at `39a544a`. Full run `36113073510`
  reached the new index and stopped because the browser check counted cards
  immediately after hash navigation, before the page rendered. The check now
  waits for the card and for a new Practice session before continuing. Rerun
  exact-head full CI.
- The exact-head rerun at `34c5bcc` passed Engineering `36113707551` and
  full browser/PWA/APK/Android phone and tablet emulator `36113695753`.
  The browser journey covered the read-only card, reload, edit/cancel, index
  search and question launch, Review and deletion. Preview
  `https://4cc816c7.nk-qbank.pages.dev` serves the new notes markers;
  production was not promoted. Physical device review remains.
- User checked the preview and confirmed the notes changes work.

## 2026-09-25 — All-bank Quick Revision desk

- The next study-intelligence phase replaces the separate More Wrong and
  Bookmarks launch rows with one Quick revision entry. The page explicitly
  covers all subjects and question banks, with Mistakes, Bookmarks, Unseen,
  and Due counts.
- Mistakes/bookmarks/unseen start random sets of up to 20. Searchable full
  lists preserve browse and single-question access for mistakes/bookmarks.
  Due reuses the shared FSRS queue and its priority/daily-cap rules, starting
  at most 20 cards. Unseen excludes active attempts and submitted skips.
- The core and transform behavior check pass locally. The generated browser
  journey now checks global bank scope, full-list search/launch, four queue
  starts, 20-question sampling, and FSRS Due behavior. Exact-head CI is next.
- Engineering `36137989615` passed at `f31c38e`. Full run
  `36137993203` reached the new browser journey and found its correct
  bookmarked fixture was unintentionally due because no future schedule date
  was set. The fixture now gives that attempt a future FSRS date; rerun exact
  head before sharing the preview.
- Corrected the browser scope assertion to normalize layout whitespace while
  still requiring the exact all-subject/all-bank label. Exact-head Engineering
  `36139455865` and full generated browser/PWA/APK/phone+tablet emulator run
  `36139466345` passed at `a5f2380`. Preview `https://9907728f.nk-qbank.pages.dev`
  returns HTTP 200 with the Quick Revision markers. Production promotion was
  disabled. Physical user preview review remains pending.

- User checked the Quick Revision preview and liked the addition. The next
  candidate adds a collapsed subject/bank/topic focus within Quick Revision.
  All four counts and practice sets, plus the searchable full lists, share
  this scope. FSRS gained an optional bank filter before its queue cap, while
  the daily review cap remains global. Local behavior checks pass; generated
  browser/PWA/APK/emulator verification and physical preview review are next.
- First focused-revision full run `36146304612` reached the browser journey;
  it counted a focused Mistakes list immediately after navigation, before the
  route rendered. The check now waits for the Mistakes heading, then verifies
  the scoped list. Engineering `36146300092` passed; rerun full CI.
- The rerun at `1d3b32e` passed Engineering `36146934888` and full
  browser/PWA/APK/Android emulator `36146938774`. Its browser journey verified
  the subject, bank, and topic controls, scoped counts and Mistakes list, and
  clearing the focus. Preview `https://f9090829.nk-qbank.pages.dev` returns
  HTTP 200 and serves the focus markers. Production was not promoted; physical
  user review of the controls is pending.

## 2026-09-25 — Insights study-next candidate

- User accepted the Quick Revision focus preview. They could not find the topic
  filter and chose to leave that refinement for later.
- Added an Insights “Topics to revisit” section across all subjects and banks.
  It uses the latest active answer per distinct question, shows current misses
  and answered sample size, recommends topics with at least three answered
  and two still missed, and opens a Practice set of up to 20 current misses.
  No-evidence and no-current-weak-topic states are distinct.
- New deterministic transform, behavior check, and generated browser journey
  are wired into Engineering and full build. Local checks pass; generated
  browser/PWA/APK/emulator verification and physical preview review are next.
- Candidate `d8e50e0` passed Engineering `36149901357` and full generated
  browser/PWA/APK/Android emulator `36149908749`. The browser journey verified
  no-evidence state, a three-answer Anatomy Marrow recommendation, direct
  two-question Practice, and removal after an improved answer. Preview
  `https://221f15a2.nk-qbank.pages.dev` returns HTTP 200 with the Insights
  markers. Production was not promoted; physical user review remains.

## 2026-09-25 — Bank-aware timed CBT builder candidate

- User called Insights useful enough to move on and asked that the next
  selection UI receive the same full-page topic treatment as Create Module.
- The Tests multi-subject popup used only `SUBJECTS`, excluding Marrow. Added a
  late, bank-aware transform and three-step Tests builder: bank cards, spacious
  searchable topic rows with group/select/clear controls, then question count.
  Topics are keyed by exact subject, bank, and topic ID; the existing exam
  engine, timing, Review Solutions, and chapter-specific strict timed test
  remain shared. The Tests builder starts from all available banks/topics and
  lets the learner narrow the scope.
- Source behavior and generated-JavaScript syntax checks pass. Generated
  browser/PWA/APK/emulator CI and user preview review are pending. Production
  and canonical remain untouched.
- First full run `36153754707` reached the new browser journey, where its
  immediate bank-card count raced hash navigation. The check now waits for the
  rendered cards; rerun the full build. Engineering `36153754830` passed.
- Second full run `36154572326` passed the new Marrow selection/scroll/exam
  browser journey. It then hit the older screenshot audit's `#modal` assumption.
  The audit now captures the full-page bank, topic, and count steps and starts
  its CBT from that same new builder before continuing its question checks.
- Third full run `36155392291` passed generated browser checks, the updated
  screen-size audit, PWA packaging, and APK build. Phone/tablet captures showed
  roomy topic rows and an accurately scoped pool; the count screen's bank list
  was overly tall. Grouped bank names by subject and fixed the Start action
  above mobile navigation. The Android emulator job failed before launch while
  downloading the Google APIs system-image ZIP (unknown archive), not in app
  interaction; rerun the exact new candidate after the UI polish.
- Fourth full run `36156614322` reached the new browser journey and failed its
  stricter mobile geometry assertion after filling the custom count. The fixed
  action bar now sits 20px higher and the check reports measured bounds; rerun
  the exact candidate before claiming preview/build verification.
- Fifth full run `36157405503` measured the count-step Start button at
  y=839–887 while bottom navigation began at y=768. This points to fixed
  positioning inside the page transform on the longer count step. The builder
  now disables the page transform, as the full-page Topics flow already does;
  the next browser check will report computed position and transform if needed.
- Product commit `5d585de` passed Engineering `36213112458` and full
  browser/PWA/APK/Android emulator run `36158438170`. Its browser journey covered bank-exact Marrow Anatomy CBT,
  topic-tap scroll stability, accurate count/timing, and button clearance;
  the screen-size audit covered 320px/390px/larger-text/tablet. The final
  phone/tablet screenshots were inspected. Preview
  `https://2752f581.nk-qbank.pages.dev` returns HTTP 200. Production was not
  promoted; physical user verdict is pending.
