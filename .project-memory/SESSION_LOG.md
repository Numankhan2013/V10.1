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
  promoted; the user subsequently checked the feature preview and said it works.

## 2026-09-26 — Compact handoff and post-CBT analysis candidate

- The user checked the bank-aware CBT preview and confirmed it works, then
  requested context compaction and the next phase. `STATE.md` was reduced from
  a historical log to a concise operational handoff; detailed past work stays
  in this log and the dedicated source/presentation handoffs.
- The completed CBT result now derives source-exact subject/bank/topic rows
  from the saved test's frozen question IDs and answers. It shows correct,
  incorrect, and unattempted counts, avoids implying mastery from sparse
  samples, and offers one follow-up Practice action for that test's exact
  incorrect and unattempted IDs. It reuses the existing Practice engine and
  preserves the score, Review Solutions, history, and result persistence.
- The new phase is isolated on `feature/qbank-bank-aware-modules-20260924`.
  Source behavior checks and Engineering `36215597577` pass. Full run
  `36215602991` reached the existing question-interaction browser check, then
  timed out waiting for a CBT submit to clear its active session; later checks
  were skipped. Diagnostic rerun `36216099227` showed the double-clicked Submit
  had completed CBT and its second click landed on the new follow-up action,
  immediately starting Practice. The follow-up now ignores a repeated submit
  click, while a later intentional tap remains available. Canonical and
  production remain untouched.
- A browser-check follow-up replaced an inaccessible IIFE helper with exposed
  source data and the public `window.QB` navigation API. Final product commit
  `b65ad21` passed Engineering `36216951965` and full generated browser/PWA/
  APK/Android phone+tablet emulator `36216944458`. The full browser journey
  confirmed the older double-submit invariant, source-exact mixed-bank topic
  rows, saved-result reload, and retry of only the wrong/skipped IDs. The
  full-page 390px capture was inspected; the new section is readable and the
  action is clear. Preview `https://c22cbdd0.nk-qbank.pages.dev` returns HTTP
  200. Production and canonical remain unchanged; user preview review is next.

## 2026-09-26 — All-bank QBank tracker candidate

- The user checked the post-CBT analysis preview and said it works. The next
  Marrow-level gap chosen is a clear study map: existing Topics shows one bank
  at a time and the earlier Insights recommendation was useful but limited.
  Marrow's published QBank material emphasizes progress tracking and
  consistent module practice; this increment stays within the current three
  subjects and does not add or infer source labels.
- Added `tools/qbank_coverage_core.js` with a late deterministic owner
  transform. Insights now shows overall and per-bank answer-based coverage,
  topic completion, latest misses, search/status filters and exact topic
  navigation. The old active-bank chapter list is replaced to avoid a second
  competing topic list. No persistence schema or engine changes.
- `test_qbank_coverage_v1.py` and `verify_qbank_coverage_browser.py` are wired
  to the full build, with source-level bank/status/navigation checks already
  passing. Product `220f954` passed Engineering `36218442172` and full
  generated browser/PWA/APK/Android phone+tablet emulator `36218442273`.
  The new browser check confirmed exact PrepLadder/Marrow counts, a filtered
  in-progress topic, search, topic entry, and persistence after reload. Preview
  `https://697c1da1.nk-qbank.pages.dev` returned HTTP 200. Production
  promotion was skipped, canonical remains untouched, and user review remains.
  Full-page phone and tablet Insights captures from the generated UI audit
  were visually inspected: all six bank cards, overall 5,397-question/250-topic
  totals, search and status controls, and the eight-row initial topic list are
  legible with no duplicate active-bank chapter panel.

## 2026-09-26 — Exam practice candidate

- The user chose a narrow next phase: one verified-PYQ timed-test selection in
  the existing CBT builder, strict per-question chapter timing, and a complete
  saved-test review/follow-up journey. New subjects and tracker polish stay
  later. PrepLadder source topics contain 27 verified PYQ topics/1,118
  questions; Marrow has no verified PYQ facet.
- The builder now derives eligible topics from the selected bank records and
  per-question `studyCollections`, replaces topic selection on request, reports
  exact eligible counts, preserves the draft when none exist, and labels a
  saved session “PYQ CBT” only if every chosen question carries `pyq`.
- The chapter Topic Test’s 60-second clock now commits cumulative time on
  navigation, persists its absolute active-question entry timestamp, rejects
  late answers, locks expired questions, advances to available questions and
  auto-submits after the last one. A behavior check covers navigation, reload,
  locked-question jumps and final expiry. A generated browser check covers
  exact bank subsets, PYQ and mixed CBT submission, saved history, Review
  Solutions, topic breakdown, missed-question Practice and both-bank timer
  expiry on phone/tablet. The packaged Android emulator check also walks
  PYQ selection to Review Solutions on phone/tablet.
- Local source/behavior checks passed. The final product commit `13c3cd3`
  passed Engineering `36229006243` and full browser/PWA/packaged APK/Android
  phone+tablet emulator `36229004244`. Browser checks confirmed the exact
  27/1,118 all-bank PYQ set and 10/410, 9/362, 8/346 PrepLadder subsets;
  empty Marrow-only selection preserved the draft. Both-bank strict topic
  expiry after reload, saved PYQ and mixed tests, Review Solutions, topic
  breakdown, history, and missed-question Practice passed. Packaged Android
  checked PYQ selection and Review Solutions on phone and tablet while retaining
  the existing Pause/Continue and review regressions. Generated browser phone/
  tablet captures and Android review captures were inspected. Preview
  `https://e544d753.nk-qbank.pages.dev` returned HTTP 200. Production was
  not promoted; user physical review remains.

## 2026-09-26 — PYQ selection control refinement

- The user reviewed the exam-practice preview and confirmed the flow works,
  then pointed out that the standalone PYQ action consumes unnecessary space
  and cannot be turned off by tapping it again. The intended compact control
  belongs beside Select all and Clear all in the Topics toolbar.
- The PYQ control now has a pressed state and exact eligible count in that
  existing row. On selects verified PYQ topics; off removes those topics and
  keeps any regular topics added afterward. If no verified PYQs exist for the
  selected banks, the control is disabled with an in-place explanation and
  leaves the draft unchanged. Bank changes and global Select all/Clear all
  reset the toggle state. Product `af30703` passed local 64 checks,
  Engineering `36233896258`, and full generated browser/PWA/packaged APK/
  Android phone+tablet emulator `36233894250`. The browser check asserted the
  three controls share one row at both widths and verified toggle on/off and
  the complete exam journey. Generated browser and Android phone/tablet
  captures were visually inspected. Replacement preview
  `https://87a819e1.nk-qbank.pages.dev` returned HTTP 200. Production was
  not promoted. The user later confirmed the toggle works and accepted it as
  doable for now.

## 2026-09-26 — Android Back exit warning candidate

- The user reported that an accidental Android exit/back press during Practice
  or a test immediately makes the session disappear. `MainActivity.onBackPressed`
  previously called `WebView.goBack()` or exited the Activity without checking
  the active question route.
- Added a native warning for active `#practice` and `#exam` routes. Stay leaves
  the current question untouched; Exit uses the established history boundary,
  which saves pending question timing/recall. The timed-test message states
  that its timer keeps running. The change is reapplied after secure-origin
  generation by `tools/apply_android_back_guard_v1.py`; source/product and
  build-order contracts require it. Packaged Android phone/tablet checks now
  exercise Stay and Exit in Practice and CBT. Local 64 source checks pass;
  full CI and preview were initially pending. First full run `36243605111`
  built the APK but its emulator check looked for mixed-case "Stay" while
  Android exposed all-caps "STAY"; the native dialog itself was present.
  Refinement `445fd13` matched button labels case-insensitively and captured
  the displayed dialog after it appeared. Exact-head Engineering
  `36244266344` and full generated browser/PWA/packaged APK/Android
  phone+tablet emulator `36244266405` passed. The report showed native Back
  confirmation, force-stop Practice recovery, Review/FSRS, and PYQ CBT review
  passing at both sizes. Phone and tablet dialog screenshots were inspected.
  Web preview `https://0c0be99e.nk-qbank.pages.dev` returned HTTP 200; the
  native confirmation requires the packaged APK for user review. Production
  was not promoted.

## 2026-09-26 — Web preview Back warning recovery

- The user correctly reported that the Cloudflare preview lacked the Android
  exit warning and requested a working preview immediately. The prior change
  guarded only packaged Android `onBackPressed`; a web deployment could not
  demonstrate it.
- Added a Browser/PWA popstate warning in the shared question interaction
  layer for active Practice and timed-test routes. Stay restores the question
  history entry before hashchange; Exit follows the existing saved-session
  route. Packaged Android on `qbank.local` keeps its native warning without a
  duplicate web dialog. Initial generated browser run caught that an in-app
  subject change could also trigger the new warning; `f450ab7` marks app
  navigation separately and verifies that normal subject changes still work.
  Local source checks and Engineering `36248903088` passed. Full run
  `36248903102` passed generated browser, PWA, packaged APK, and Android
  phone/tablet emulator checks, then deployed the Cloudflare preview. Preview
  `https://8552f47f.nk-qbank.pages.dev` returned HTTP 200 and served the
  new Back warning code. Production was not promoted.

## 2026-09-27 — Timed CBT marked-question follow-up candidate

- The user confirmed the Browser/PWA Back preview works and directed explanation
  fine-tuning and image integration to their separate automations. For the next
  learner-facing phase, added a two-way Mark for review control to timed CBT and
  strict topic tests. Marks are independent of answers, saved through reload,
  visible in the question navigator and final review grid, and snapshotted into
  the saved test. A result action starts Practice on exactly the saved marked
  IDs, including questions answered correctly by guess.
- Product `31ac38a` preserves the shared CBT/Practice engines and source IDs.
  Local 66 checks, Engineering `36293641439`, and full generated browser/PWA/
  packaged APK/Android phone+tablet emulator run `36293641549` passed. Phone/tablet browser checks cover
  mark persistence, grids, saved history and follow-up. Cloudflare preview
  `https://da6eaa24.nk-qbank.pages.dev` returned HTTP 200 with the new code.
  User physical review is pending; production was not promoted.

## 2026-09-27 — Visible timed-test recovery after Exit

- The user confirmed the marked-question test flow works and asked to continue
  with another useful learner-facing phase. The earlier Android/browser Back
  warning retained timed-test state after Exit, but did not make that state
  discoverable. Added one Resume timed test card to Home, Tests, and the CBT
  builder, where Back from a newly started CBT actually lands.
  It shows exact answered and marked counts, reminds the learner that the timer
  continues, and returns to the same session. If time expired, the action uses
  the existing global submit or strict per-question expiry path.
- Product `78e391f` passed local 68 checks. The first packaged emulator run
  revealed that Android Back lands on `#test-builder`, beyond the initial Home
  and Tests card placements. The final transform adds the same card to the
  builder, and browser and Android checks now assert it there. Engineering
  `36298273342` and full browser/PWA/packaged APK/Android phone+tablet emulator
  run `36298273539` passed. Cloudflare preview
  `https://edd8fb9f.nk-qbank.pages.dev` returned HTTP 200 and served the
  builder card. User physical review remains pending; production was not promoted.

## 2026-09-27 — Timed-test protection when opening a saved module

- The user confirmed timed-test recovery works. They proposed integrating its
  Home notice into Today's Focus only if it could be done in under a minute
  without changing paused Practice or saved-module behavior. The Focus has
  multiple established resume branches, so that integration was deferred.
- A saved study module launched through `startStudyModule` could replace an
  active timed test because it bypassed the shared `startSession` guard. The
  module path now opens the same explicit Resume/Abandon/Cancel dialog. Cancel
  and Resume retain the test; Abandon persists the choice and then opens the
  requested module. Expired tests use their existing completion logic first.
- Product `91c59b8` with packaged Android check `2997cdb` passed local 68
  checks, Engineering `36300815881`, and full browser/PWA/packaged APK/Android
  phone+tablet emulator run `36300815905`. Cloudflare preview
  `https://e17cbb6d.nk-qbank.pages.dev` returned HTTP 200 and served the
  updated conflict dialog. User physical review is pending; production was
  not promoted.

## 2026-09-27 — PrepLadder source PDF contrast

- The user reported long-standing bleached PrepLadder explanation pages on
  Android. `docs/PDF_RENDERING_CONTRAST_INVESTIGATION.md` had previously found
  no app opacity/filter and deferred a correction pending device evidence. The
  earlier sharp fullscreen zoom repair remained intact. Baseline captures from
  full run `36300815905` showed pale text and blue at inline phone width.
- Applied a scoped display filter, `contrast(1.16) saturate(1.12)`, to source
  PDF page images/canvases and fullscreen source zoom. The first placement in
  `apply_question_experience_v1.py` was removed by a later style transform;
  generated browser run `36303495208` caught this. Product `70794a2` places
  it in the final `apply_session_experience_v2.py` style and checks the
  transform order. Original PDFs, rendered assets, and Marrow visuals are
  unchanged.
- Local 68 checks, Engineering `36303853277`, and full browser/PWA/APK/Android
  phone+tablet emulator `36303853023` passed. Browser assertions covered all
  three subjects, inline and zoom; Android checked Review Solutions. Before/
  after captures showed darker text and stronger blue with fine table lines
  visible. Preview `https://ce13d233.nk-qbank.pages.dev` returned HTTP 200
  and served the rule. Physical review is pending; production was not promoted.

## 2026-09-27 — Timed-test grid Abandon

- The user explicitly deprioritized multiple simultaneous tests and asked for an
  Abandon action inside the test grid, never on the question page. An unreleased
  multiple-test candidate was reverted before deployment. The final change adds
  confirmed Abandon to the navigator and final review grids only. Cancel or a
  failed state save keeps the test; confirmation clears the active test without
  recording attempts or a result, returns to Tests, and removes Resume.
- Product `5ea37d8` with browser-check fix `191ef61` passed local 70 checks,
  Engineering `36313958399`, and full browser/PWA/packaged APK/Android phone
  and tablet emulator `36313958394`. Preview
  `https://22a83cd1.nk-qbank.pages.dev` returned HTTP 200 and served the new
  action. The user checked the preview and said it works. Production was not
  promoted.

## 2026-09-27 — Exact CBT retake and initial/final comparison

- The user requested a higher-value exam feature after the grid Abandon fix.
  Tests already had timed wrong/bookmarked sets, so a proposed Quick Revision
  timed action would have duplicated that. Instead, completed global-timer CBT
  results now offer a one-tap exact-question retake with a fresh timer and blank
  answers. The single-active-test conflict guard remains in charge.
- The retake session carries the initial saved test ID in its context; the
  durable submission path writes `retakeOf` on the new saved result. Its result
  compares correct, accuracy, attempted, incorrect, unattempted, time,
  previously missed questions corrected, new misses, and source-exact topics
  missed in either attempt. Initial analysis can be opened directly; existing
  final-result overview, topic breakdown, Review Solutions, and missed-ID
  Practice remain available. Missing questions block an exact retake.
- Product `4a2d5af` with browser-check fix `108dfe3` passed local 70 checks,
  Engineering `36315690909`, and full browser/PWA/packaged APK/Android phone
  and tablet emulator `36315823769`. The Android comparison captures were
  inspected. Preview `https://726640e4.nk-qbank.pages.dev` returned HTTP 200
  and served the comparison; the user checked it and said it works. Production
  was not promoted.

## 2026-09-27 — UI integration and main deployment

- The user authorized integrating the secondary model's accepted UI updates into
  the accepted QBank study build, reconciling with current `main`, and promoting
  the whole production. The two code changes add per-destination identity to
  More/Quick Revision lists and metric-specific identity to completed test
  analysis tiles; they do not change question behavior or the home flow.
- Cherry-picked code commits `5e239fa` and `26b0a42`; merged `origin/main` to
  retain its current source-audit projections and runbooks. Integration branch:
  `integration/ui-canonical-main-20260927`.
- Local verification: `verify_project_memory.py` passed; `verify_local.py` passed
  70 checks; revision desk unit behavior/install passed. The whole-app vision
  unit check requires the CI generated-app transform position and is not a
  standalone local pass. Main commit `d4cf2edf4b1e4de29c0d5035c6047c684bac5fbf` passed full generated
  browser/PWA/APK/Android phone+tablet CI in run `36320714980`. The user-authorized
  exact-SHA release run `36321611129` passed its explicit SHA guard, regenerated
  and verified the app, built/verified the APK, and deployed production. Wrangler
  reported preview `https://ae11d530.nk-qbank.pages.dev` and alias
  `https://main.nk-qbank.pages.dev`; both aliases returned HTTP 200 and the
  deployed bundle contains the two UI changes. Later content comparison found
  the project root still serves its older deployment despite returning HTTP 200.
- The release run’s emulator job passed Android interaction assertions on phone
  and tablet (`ANDROID_INTERACTION_VIEWPORT_OK`, including native Back, force-stop
  resume, Practice/review/FSRS, PYQ CBT, timed-grid abandon, and CBT retake), but
  its final screenshot capture failed because the browser context closed. The
  preceding full exact-SHA run completed green on both devices. A second attempt
  hit the same post-interaction screenshot capture failure. Physical in-place APK
  upgrade/data preservation remains unverified; the `main` branch alias has
  the new PWA build, but the Pages root still needs its production branch fixed.

## 2026-09-27 — Correct the Cloudflare Pages root alias

- The user reported that the remembered root Pages domain still showed the old
  build. Content checks confirmed `https://nk-qbank.pages.dev` differs from
  both the current `main.nk-qbank.pages.dev` and `https://ae11d530.nk-qbank.pages.dev`
  deployment aliases. The similar hostname `nkqbanks.pages.dev` does not resolve.
- Cloudflare's Pages Direct Upload project had a production branch setting that
  the previous deploy did not update. The official Pages API requires updating
  `production_branch` for Direct Upload projects. The production workflow now
  PATCHes that field to `main` before uploading the exact approved release.
- Updated the release workflow to PATCH the Pages Direct Upload project
  `production_branch` to `main` before deployment. Full main CI `36324929838`
  passed; release `36325843382` updated the branch and deployed SHA
  `d43da3dbdaa639214d676b333152654568fe5ba9`.
- Verified the root, `main` alias, and preview
  `https://37799f47.nk-qbank.pages.dev` return HTTP 200 and share the same
  SHA-256 of the generated app response. The remembered spelling
  `nkqbanks.pages.dev` does not resolve; the configured canonical domain is
  `nk-qbank.pages.dev`. Physical Android in-place upgrade remains separate.
# 2026-09-30 — Approved study-tweak promotion audit

- User authorized promoting tweaks they confirmed work to main while keeping
  current image/explanation agents undisturbed. Used a separate clone and a
  new promotion branch based on main; no donor/canonical branch was changed.
- Notes and earlier accepted study features already exist in main. Recovered
  the all-bank question-finder runtime and validation delta from
  `20cd811`. The user then explicitly confirmed all later candidates except
  tap/haptic feedback: included account reset/switching, Practice correction,
  and Home/result refinements. Excluded the bundled haptic/latency candidate
  and all content/image changes.
- Product `f9b0d0145f49aaffab7fcca6d9da78b507905048` passed all 74 local
  checks, Engineering `36733960874`, and full browser/PWA/APK/Android
  phone+tablet run `36733869611`. Notes, Continue Practice, exact-ID search,
  correction, Home/result, and packaged regressions passed. Preview:
  `https://9629afb2.nk-qbank.pages.dev`.
- Promoted through PR #78 by fast-forwarding main from `971bd55` to the
  verified product plus a documentation-only `[skip ci]` handoff. No runtime
  code changes occur after the certified product. No production dispatch,
  existing branch deletion/update, or other agent workflow cancellation.
  Physical APK upgrade/data-preservation acceptance remains separate.

## Canonical integration history retained from image trunk

## 2026-09-28 — Manual Marrow Biochemistry image batch staged

- Resumed the claimed `manual-biochem-ch25-28-20260928` batch from live canonical `14e455e`; kept the separate Physiology Ch3–7 ledger claim intact. Integrated stable source references across Ch25–28: 16 PASS, 5 held for focused review, and one Q27 Q5 source-metadata invalid adjudication; all 22 references are tracked. Coverage now reports Biochemistry 110 raw / 108 effective / 87 released / 2 invalid / 8 tracked-unreleased / 13 untracked / 31 visual text cues.
- Local image validator/release, progress and coverage checks, image tests and `verify_local.py` passed before this continuation. Exact-head CI and canonical reconciliation remain pending.
- Discovered the first staging helper had produced region crops with Poppler on Termux, contrary to the repository's Ubuntu-only `marrow_images.py render-region` rule. Added an Ubuntu build step that renders the eight exact checkpoint regions and uploads a manifest plus source crops for review. Do not call this batch complete until the bytes are replaced/adopted from that CI artifact and the full exact-head build passes. Production remains untouched.

- Follow-up: the first full run `36415735858` stopped in the new artifact wrapper due to a path-discovery assertion (no app packaging or preview). Fixed the wrapper; the exact-head Engineering run `36415941547` passed. Full build `36415941717` rendered and uploaded all eight Ubuntu crops. Inspected each crop, replaced every non-JPEG local render's original/production bytes and content-addressed ID from that artifact, and regenerated runtime metadata/progress/coverage. Exact candidate CI on the adopted image bytes is still required.


## 2026-09-28 — Biochemistry Ch25–28 image batch partially integrated

- Exact product commit `87a572486b28f1644ad7d78b51fca10ca099f6a9` passed candidate Engineering `36416657111` and full Android/PWA/browser/APK/package/emulator run `36416656845`; the exact same SHA fast-forwarded to canonical and passed canonical Engineering `36418451083` plus full run `36418451115`. The packaged phone/tablet emulator interaction regression passed. Fresh 320px, standard phone, 150% text, and tablet UI captures were inspected; Android screenshots and the eight source-region render artifact are retained in CI artifacts. Preview `https://fdfaf659.nk-qbank.pages.dev` and the feature alias returned HTTP 200. Production promotion was skipped.
- The range remains **open**: 16/22 source refs released, five tracked readability/source-fidelity holds, and one exact Q27 Q5 invalid-metadata adjudication. There are no untracked references remaining within this claimed Ch25–28 range. The separate Physiology Ch3–7 batch remains claimed and must refresh shared image state from the new canonical head before writes.

## 2026-09-28 — Resolve and release five Biochemistry image holds

- Reviewed the five former Ch25–28 holds against exact source pages, source crops, and native image tiles. All five retain original pixels and are SOURCE_LIMITED: Q25.26 has small inline labels; Q26.18's watermark crosses fine factor labels; Q27.2/Q27.3 have faint but readable expanded condition labels; Q28.27's watermark crosses some bond detail. The existing image viewer supports tap-to-expand and zoom. No source pixels or scientific labels were reconstructed or sharpened.
- Integrated product commit `ef969540171b3cb19d724a28f3adbf0fba42f5f7`. Full batch accounting: 21 source references released, Q27.5 explicitly invalid by exact metadata adjudication, no untracked or review-required references in Ch25–28. Biochemistry overall remains incomplete at 110 raw / 108 effective / 92 released / 2 invalid / 3 tracked-unreleased / 13 untracked / 31 text-cue items.
- Candidate exact-head Engineering `36425459384` and full Android/PWA/browser/APK/package/emulator run `36425386902` passed. The product SHA fast-forwarded to canonical, then canonical Engineering `36427679654` and full run `36427679667` passed on that exact SHA; packaged Android phone/tablet interactions and Marrow browser checks passed. Preview `https://27f74250.nk-qbank.pages.dev` and canonical alias returned HTTP 200. Production promotion was skipped.

## 2026-09-30 — Source-check Marrow Physiology nerve learner text

- User reported severe question/option "JSON leak" in Marrow Physiology of Nerve. Inspection of the deployed Marrow bundle and ED8 PDF pages 93–103 showed OCR debris in the stored Ch6 learner text, while the shared JSON-wrapper sanitizer and bank registration were active. The raw compressed ED8 source remains unchanged.
- Two nonoverlapping source-review passes authored fingerprinted display overrides for all Ch6 Q1–34 stems and four options. Q20 option C is corrected from imported `I` to source `II`; answer indices remain unchanged. Ch6 Q10's printed source itself has numbered choices without a matching table, which the override preserves.
- The Marrow importer now accepts the existing Ch5/Ch7 manifest and two Ch6 manifests with exact ID ranges, bundle fingerprints, and ED8 PDF hash checks. Static content tests pass over 2,711 questions / 27,898 learner fields; `verify_local.py` passed 51 checks. Full generated browser/PWA/APK and preview checks remain pending at this entry.
- A conservative symbol heuristic found residual source-review candidates concentrated in Physiology Ch9–12. Do not strip those characters globally or claim those chapters cleaned without PDF comparison.

## 2026-09-30 — Extend Physiology stem/option source cleanup to Ch9–12

- While the Ch6 canonical build ran, two workers took exclusive Ch9–10 (45 questions) and Ch11–12 (44 questions) ranges. They checked rendered ED8 pages 173–180, 198–202, 210–215 and 225–230 and produced separate fingerprint/PDF-pinned manifests, preserving source wording, choice order, and answer indices.
- Combined reviewed display coverage is now 186 questions across Ch5–7 and Ch9–12. Ch9 Q14's diagram remains image-owned; no diagram content was inferred. Workers reported no unresolved stem/option transcription ambiguity. This coverage does not establish cleanliness of the other Physiology chapters or explanation text.
- The importer, corpus test, browser verifier, and structure-audit input list explicitly include both new manifests with exact stable-ID scopes. Canonical Ch6 product `20b12fcc` passed Engineering `36662743310`; full run `36662743308` was still running while this follow-up was prepared. Full verification of the follow-up remains pending.

## 2026-09-30 — Resume source-image integration during text CI

- User asked to resume image integration while learner-text CI runs. Live canonical coverage is 1,186 released / 18 metadata-invalid / 228 unresolved source references of 1,432, plus 59 text-cue checks. These are source-reference counts, not question counts or a claim that every learner question should show an image.
- Preserved the separate Physiology Ch3–7 reservation (49 unresolved references + one cue). Explicitly transferred the remaining paused Wave 2 scopes into four exclusive ledger batches: Anatomy Ch1–59 (69 refs), Anatomy Ch60–63 (52 refs), Physiology Ch8–14 (52 refs), and Biochemistry Ch1–24 plus Physiology Ch15–43 (6 refs + 58 cues). Three worker slots are available concurrently; the fourth starts when a slot opens. No extra reviewer is assigned.
- The dirty old Ch56–63 worktree remains a read-only donor of unfinished source work. Workers use fresh worktrees and validate their own scope; root serializes stable-ID registry/asset reconciliation and monitors the pending text CI. Ch6 browser text checks and build/deployment job passed; packaged Android interaction job was queued. Ch9–12 follow-up remains in full CI at `a6f2bca1`.

### Text CI integration follow-up

- Ch6 full run `36662743308` completed successfully, including packaged Android interactions and preview deployment. A fresh HTTP 200 fetch of the canonical feature alias matched all 34 reviewed Ch6 stems/options in its 2,711-question Marrow envelope.
- Ch9–12 Engineering `36663959324` passed. Full run `36663959370` stopped at the browser verifier on Ch9 Q12: reviewed source option `Cl-` renders as `Cl−` through the existing shared scientific formatter. The source content is correct; the verifier now computes its expected text through that same formatter rather than requiring the unformatted charge glyph. This is a targeted response to the reported CI failure; full retry remains required.
- Retry product `232f0182f26c891bbe459e9c9472816db7fa796f` passed Engineering `36665702451` and full generated browser/PWA/APK/package/Android phone+tablet run `36665702481`. A fresh canonical preview HTTP 200 fetch matched all 186 reviewed stems/options in its complete 2,711-question Marrow envelope. Text cleanup is build-verified and deployed to preview; production promotion and physical acceptance remain separate.

## 2026-09-30 — Resume image workers B/C integration

- Reconciled worker B `dc488f12` (Anatomy Ch60–63: 51 released / 1 invalid) and worker C `18766fd8` (Physiology Ch8–14: 19 released / 33 invalid) by stable-ID deltas; preserved unrelated text cleanup and images.
- Both workers passed release/progress/coverage and 51 local checks. Root found no conflicting registry/asset changes and regenerates shared derived files; source review was not repeated.
- Worker D started its exclusive Biochemistry Ch1–24 / Physiology Ch15–43 range after B freed a slot. A continues Anatomy Ch1–59; external Physiology Ch3–7 claim remains reserved. Canonical CI/preview verification pending; production deferred.

## 2026-09-30 — Anatomy Ch1–59 source checkpoint

- Worker A `0243a614` resolved 68 of 69 assigned refs: 64 released, four source-invalid; Ch45 Q4 is held because source marker is absent. Two corrected-page question assets are released with truthful citations.
- All local checks passed after restoring existing registry ordering and retrying the sole failed image test. Root integrates stable-ID deltas; full canonical CI pending.
- First image checkpoint `a656edd1` is live: metadata bytes matched canonical and a sampled new image matched its SHA-256; build/browser/APK packaging passed, full Android interaction run 36670768102 subsequently passed. Worker B resumes 29 unmodified Biochemistry cue questions after A frees the slot; C handles Physiology tail cues, D handles six known refs and cue architecture. Production remains deferred.

- Anatomy checkpoint `e3cef56d` passed Engineering `36673442104` and full browser/PWA/APK/Android `36673441905`; canonical preview metadata matched exactly (1,051 distinct visual-owning questions).
- D final `997f0c1f` passed normal release/progress/coverage and the targeted stale-progress retry; root merged four images, two invalid adjudications and two no-visual cue records. Combined regeneration waits for B/C cue commits. C source coverage closes 32 cue-derived refs; B reviewed 28 real cue questions plus Ch17 Q14 source omission.

## 2026-09-30 — Four-worker image phase final integration

- Integrated C tail `34b893fd` (32 source refs / 27 closed cues) and B tail `20cc85bb` (28 source refs / 29 closed cues), preserving D’s six-ref/two-cue checkpoint and all earlier text/source work. Both tail workers passed all 51 local checks; no source review was repeated by root.
- All 237 assigned items are accounted: 236 resolved, one held (Anatomy Ch45 Q4 lacks required source marker). B documents Biochemistry Ch17 Q14’s absent source teeth image as an omission. External Physiology Ch3–7 still owns 49 unresolved refs plus one cue.
- Exact source cue reviews add 60 source-derived reference rows with pinned PDF hashes/provenance; actual continuation pages remain explicit, and wrong roles/orders/pages or unreleased bindings fail closed. Root regenerates combined outputs and pushes mandatory canonical preview CI; production remains deferred.

## 2026-09-30 — Final image checkpoint verified and live

- Product `d0e76fcc` is dual-green: Engineering `36678220234`, full browser/PWA/APK/package/Android phone+tablet `36678220258`. Canonical preview metadata equals committed release bytes; new Biochemistry Ch23 Q9 union image bytes match the content-hash filename.
- Final source coverage: Anatomy 1,012 released / 15 invalid / 1 held of 1,028; Biochemistry 133 released / 5 invalid / 0 pending of 138; Physiology 239 released / 38 invalid / 49 pending of 326. Global 1,384 released / 58 invalid / 50 pending of 1,492, including 60 cue-derived refs. 58 of 59 cues reviewed; remaining cue belongs reserved Physiology Ch3–7.
- 1,107 questions carry 1,449 released bindings (347 question / 1,102 explanation). Owned 237-item phase resolved 236; source gaps remain explicit (Anatomy Ch45 Q4 marker, Biochemistry Ch17 Q14 teeth image). No additional source review, physical acceptance or production promotion.

## 2026-09-30 — User-directed full remaining image reconciliation

The cloned checkout was main with an outdated coverage ledger; the initial
1,243 outstanding-reference report was corrected after fetching canonical.
Canonical af7e0dff has 1,384 released, 58 invalid and 50 unresolved references,
plus one Physiology cue. The user explicitly directed the primary agent to
integrate all validated images and begin the unreviewed remainder without
per-batch full preview builds. Physiology Ch3–7 ownership is transferred.
34 donor references were exact-ID/hash/provenance reconciled; the Q20/page-149
proposal was excluded after direct source review found it belongs to Q19.
Fourteen ambiguous references and Q5 Q6's cue were source-reviewed; six
continuation-page corrections remain outside immutable imported source.
Q6 Q10's numbered question image is missing from source and remains held.
Ubuntu source extraction and the combined full preview/package build are
pending; no canonical or production release is claimed at this checkpoint.

Final source reconciliation: 34 historical references were accepted with exact
identity/provenance/stream checks; the excluded Q20 proposal was corrected by
direct source ownership review. Twelve of fourteen ambiguous references are
released, one duplicates an already released Q11 image, and Q6 Q10 is missing
its source question diagram and remains held. Q5 Q6 adds two exact native
source panels. Six metadata page errors have exact reviewed correction entries.
Source extraction runs 36693009335 and 36694166456 passed. All seven generated
composite/masked/Flate crops were inspected; Q3 Q13 was widened for its heading.
Totals: 1,413 released / 79 invalid / 2 held of 1,494; unresolved cues=0.
All 51 local checks passed, with the single stale-progress failure corrected
and the image invariant test rerun successfully. New phone/tablet learner
checks cover every freshly reviewed question and question/explanation timing.
Full combined canonical CI/preview remains pending; no production promotion.

## 2026-09-30 — Final bounded question-completeness pass

Parallel source review disposed of 238 unique IDs from the 5,397-question structural
scan (226 initial plus 12 supplements): 66 contextual reconstructions, 13 exact source
repairs, 126 already complete (52 ordinary/74 owned visual), and 33 underdetermined
source omissions. Integrated 79 repairs: 73 text/table/key contracts and six native
question images. Omission gates include ANAT62Q6. Source-backed text replacements
recover missing visual clues without fabricated pictures or diagnosis/answer leakage.
The accepted pinned ledger/compiler targets the shared presentation core; raw imports
remain immutable. Final missing-question-visual screening supplements the structural
queue. Gold explanation disclaimers were aligned with supported reconstructions.

Image ledger: 1,500 references / 1,419 released / 79 invalid / two archival holds /
zero unresolved cues; runtime 1,486 bindings / 1,306 assets / 1,128 questions.
Ordinary builds now skip optional archival source-region sheets (roughly 1 GB),
with explicit workflow input retaining regeneration. Prior checkpoint 7f326e61 full
run 36695040994 failed an ambiguous Muscle Physiology I locator matching II; exact
chapter selection is fixed. Final combined CI/preview remains pending; no production
promotion or new physical-device/user acceptance is claimed.

### Final residual review supplement — 2026-09-30

Eight additional visual-cue source checks and eight notation/glyph source checks
bring the bounded pass to 254 source-reviewed questions: 74 contextual/15 exact
repairs (89 total: 81 display contracts and eight native question images), 132
already complete (53 ordinary/79 visual), and 33 source-omission gates. The 114
compiled display entries pass source checks across four variants. Current CI queue
combines structure/glyph/runtime-question-visual scans and requires reviewed
dispositions; all 197 remaining heuristic candidates have review evidence, zero
unreviewed. Anatomy45Q23 and Physiology37Q9 add native question owners; the latter
uses complete graph JPEG object1775 instead of the explanation crop containing
clipped neighboring prose. Existing explanation PNG is preserved. Expected image
coverage becomes 1,502 references/1,421 released/79 invalid/two archival holds/zero
cues, subject to final regeneration confirmation. Prior local52checks passed before
these residual additions; final combined CI remains pending. No production claim.

### 2026-09-30 — Combined completeness browser follow-up

- Product commit `abf68b0607ee78667621a049ef557df5d55b0ad4`: Engineering Gate `36727678337` passed. Full run `36727677940` passed source/generation checks, then failed the older final-image browser verifier because it attempted to answer now-gated Physiology Ch6 Q10.
- Adapted that verifier to assert the exact source-omission notice, absence of answer buttons, retained released bindings, and package checks for gated owners. Ordinary image owners retain before/after-answer and viewer checks. Added new completeness browser evidence directory to artifact collection. Rerun required before preview/build verification claims.

- Follow-up run `36729022407` on `2909a9f8bb7443817dc5d14911a44c0cf866e3c9` passed Engineering `36729022391` and all 26 final Physiology image viewport cases. It then found an old Anatomy Ch6 Q2 browser assertion expecting dotted plain-text labels; the new semantic table correctly separates labels and cell values. Updated that assertion to verify the exact four table labels/values, and fixed a pre-initialization table-variable reference in the updated glycogen browser test. Browser checks now all run independently once dependencies succeed; the Marrow entrypoint aggregates all seven regressions. Any failure still blocks packaging/deployment. Final combined run remains required.

- Run `36730588131` on `a43e13fae313ca580ac767dcf5de3bc214a6b1eb` collected the independent browser checks: all seven Marrow browser regressions, populated table, matching/glycogen, Continue Practice, interaction integrity and PrepLadder visual/fullscreen checks passed. Two assertion incompatibilities remained: hygiene expected ordinary options on four exact approved omission gates, and the new completeness verifier queried buttons after answer feedback had replaced them with static option rows. Adapted both to assert the intended semantic gate/result rows. Content repairs are unchanged; full rerun required. Confirmed regenerated source/image counts and final 52-check local pass in state/strategy; corrected historical inventory/ownership drift.

### 2026-09-30 — Final completeness release certified

- Product checkpoint `de9c415cef4915d5b20a42abc9f2299a8595b173` passed Engineering `36732893469` and full run `36732893814`, including both build and Android phone/tablet emulator jobs. Preview `https://74f04894.nk-qbank.pages.dev` deployed; production promotion skipped.
- New completeness browser: 114 accepted contracts / 228 phone-tablet runtime checks / eight recovered source images; all gates, representative tables/text/keys and real answer interactions pass. Hygiene and all seven Marrow regressions pass; final-image browser 26 cases pass; Practice/interaction/PrepLadder fullscreen, APK syntax, offline bytes and packaged product contracts pass.
- Live preview independently verified: exact released visual metadata, all 114 compiled contracts, 33 deliberate gates, and exact source SHA-256 for eight recovered native image URLs. No reviewed/recoverable images await integration. Runtime: 1,306 released assets / 1,486 bindings / 1,128 owners; source inventory: 1,502 refs / 1,421 released / 79 invalid / two archival gaps / zero unresolved cues.
- User reports substantial improvement in a Physiology chapter, accepts disabling incomplete source questions and explicitly defers recovery to later. This is scoped preview feedback, not a complete physical/source audit of every question. Bounded 254-case pass is complete: 89 repairs / 132 already complete / 33 documented underdetermined omissions.

## 2026-09-30 — Completed image promotion preparation

- User authorized promoting all completed image integrations to main. Merged
  canonical `81822e4` (verified product `de9c415`) into isolated main-based
  `feature/marrow-image-main-promotion-20260930` from main `f0073c4`.
- Preserved approved account/study features and all their regression gates.
  Excluded the independent Biochemistry Ch14 Q1–Q8 explanation batch and
  regenerated main inventory at 662 enhanced / 2,049 pending / 2,711 total.
- Completed image registry/coverage and attached source-completeness recovery
  are retained exactly. All 75 local checks passed. Fresh combined full CI
  is required before main promotion. Existing branches remain unchanged.
- Details: `docs/COMPLETED_IMAGE_MAIN_PROMOTION_2026-09-30.md`. Production
  deployment and physical APK acceptance remain separate.

## 2026-09-30 — Completed images verified and promoted to main

- Exact combined product `a7f1be5176538cecda350511dd1d2a74b1ec9955` passed
  75 local checks, Engineering `36738373712`, and full browser/PWA/APK/Android
  phone/tablet run `36738347129`. Image metadata matches final canonical
  exactly; approved main study owners remain unchanged. All 114 completeness
  contracts passed 228 runtime cases, final Physiology imagery passed 26
  viewport cases, and notes/search/correction/Continue Practice passed.
- Preview: `https://001e687e.nk-qbank.pages.dev`. PR #79 promotes main from
  `f0073c4` by fast-forward to this verified product plus a documentation-only
  `[skip ci]` handoff. No runtime change follows the certified product.
- Independent Biochemistry Ch14 Q1–Q8 explanation rollout and tap/haptic work
  remain excluded. No worker branch was changed/deleted or run cancelled.
  Production deployment and physical APK/data-preservation acceptance remain
  separate. Future content work must preserve the combined main runtime.


## 2026-10-01 — Revision navigation and count-focused visual refinement

- User requested calmer study cards, Anki-style visible due/missed counts,
  Revision replacing the FSRS tab, and preserved FSRS graphs inside Revision.
- Extended the existing revision transform/core: neutral card borders/titles,
  small semantic icon/count colors, quiet More rows, global Home counts,
  primary Revision destination, scoped review forecast, existing FSRS/settings
  links, and active Revision state throughout FSRS subpages.
- Retained the all-bank pool logic, random 20-question samples, cap/rollover
  behavior, old route, shared Practice engine and persistence/source contracts.
- Updated behavior/browser checks for global versus scoped counts, cap/rollover,
  graph scope, all four launches and responsive navigation. All 75 local checks and the generated product contract pass. The Revision
  browser and required Pause/Home/Continue regression pass against an updated
  copy of the certified main generated baseline. Full CI initially caught two
  navigation renderer templates; the revision transform now replaces the
  existing renderer and the single-navigation contract passes. Candidate CI
  still establishes full APK/PWA verification; no physical acceptance claimed.


## 2026-10-01 — Add connected Home streak and milestone fire

- During Revision review the user liked the screenshots and requested a more
  motivating animated Home streak. Added the work to the same candidate/PR.
- The existing Home owner now renders connected adjacent studied days, broken
  colored links at gaps, a clear today ring, a custom SVG flame and soft glow
  that intensify at 3/7/14/30 days. Empty streak is a quiet ember. Gentle sway,
  inner flicker and milestone sparks are CSS-only; reduced motion is static.
- Existing `currentStreak` and `studyDayKeys` remain unchanged. No new study
  counters, stored rewards, timers, or persistence/sync model.
- Milestone/connection unit behavior, all six visual states at 320/390/889px,
  reduced-motion browser assertions, generated single-nav contract and the
  required multi-question Pause/Home/Continue regression pass on the updated
  certified generated baseline. Candidate CI still establishes full build
  verification; physical review and production remain separate.


## 2026-10-01 — Replace rejected amber streak with liquid violet motion

- User rejected the amber treatment and clarified the week strip should feel
  like water moving from today toward the next dot, without celebratory notices.
- Replaced warm card/rail coloring with the app's blue/violet language, liquid
  gradient flow across studied links and a stretching/receding frontier at today.
  Future markers stay neutral and semantically upcoming. The larger flame has
  independent outer/inner/core motion, aura and rising embers; milestone scale
  and energy grow, with all motion disabled by reduced-motion preference.
- Captured six seconds of actual rendered movement as GIF/MP4 under local
  `build/ui-checks/`. Read Duolingo's official streak habit/milestone motion
  posts for inspiration; retained this app's own visual theme and study model.
- All 75 local checks, tier/responsive/real-motion/reduced-motion browser checks,
  generated product contract, and local source-hygiene browser pass. Earlier CI
  had a gate probe sample DOM before visibility; the probe now awaits the
  existing source-gate notice, still failing on a missing gate. Source behavior
  and content remain unchanged. Full latest candidate CI must pass before
  claiming build verification; previous emulator capture failed during a PDF
  screenshot after its underlying PWA/APK build succeeded.


## 2026-10-01 — Certify the Revision and liquid Home streak candidate

- Product `d3247ca63d3db3f99fa9310be4c399dde0dd449a` passed all 75 local
  checks, Engineering `36838440726`, and full generated browser/PWA/packaged
  APK/Android phone+tablet run `36838433115`. Pause/Home/Continue, source
  hygiene, CBT, native Back, force-stop resume and source-PDF rendering passed.
- Preview `https://ca26da11.nk-qbank.pages.dev` returned HTTP 200. Its deployed
  HTML passed the full Revision/streak browser suite; direct live-browser checks
  passed animated Home, Revision navigation, and FSRS graphs with no page errors.
  Inspected full-CI Home and Android phone/tablet evidence. Local six-second
  motion GIF/MP4 records actual rendering, using seeded demonstration days.
- PR #80 remains a draft for user visual review. Main/production are unchanged;
  physical-device acceptance remains separate. This documentation-only
  `[skip ci]` handoff retains the certified product SHA above.


## 2026-10-01 — Patch unresolved mistakes and editable FSRS ratings

- User accepted the Revision/streak preview, requested an FSRS investigation,
  then authorized the recommended patch. Reproduced 24-question Biochemistry
  Practice and timed CBT: successful follow-up correctly scheduled reviews,
  but historical-wrong filtering retained resolved mistakes. One-shot ratings
  could not be changed, and stale checkpoints restored committed pending IDs.
- Mistakes now uses the latest active answer independently of FSRS eligibility.
  Saved Practice/CBT follow-up excludes corrected original misses and shows
  correction status, retaining original scores and topic analysis.
- Correct-answer rating controls remain visible and show the saved selection.
  Immutable amendment events replay the same retrieval at its original time;
  they sync through existing attempt envelopes and live outside answer history
  to avoid extra reviews, score counts or study days. Undo restores a prior
  grade; edits/Undo retain transactional rollback on failed persistence.
- Checkpoint merging honors explicit pending removals and rejects committed
  IDs. New generated-runtime browser coverage exercises 24 questions, grade
  changes, stale merge, peer revision delivery, reload, historical scores and
  a subsequent miss. Local/generated/browser checks pass on the updated
  certified baseline; full exact candidate CI remains pending.

- Certified patch product `4a14b0cfe8f231da0026fc5d621c1ebaf26fcc84`:
  75 local checks, Engineering `36875631994`, and full generated browser/
  PWA/APK/Android phone+tablet `36875623643` (attempt 2) pass.
  Pause/Home/Continue, persisted rating edits, correction queues, saved scores,
  native Back, force-stop resume, source PDFs and packaged contracts pass.
- Preview `https://f4e2534b.nk-qbank.pages.dev` passes the full deployed-HTML
  FSRS correction regression and direct live phone/tablet rating/reload/
  Revision/FSRS checks with zero page errors. Rating screenshots were checked.
- Initial Android evidence showed a Pixel Launcher ANR overlay; rerunning only
  that job with the identical APK passed both devices. No product change was
  made for that environmental failure.
- PR #80 stays draft; main/production unchanged. Physical acceptance remains
  separate. Final documentation was written through GitHub while the local
  workspace was offline; fetch the branch before subsequent local work.



## 2026-09-30 — Parallel Luna explanation refinement wave

User authorized parallel Luna authoring at suitable effort and combined release verification. Three high-effort Luna workers audited disjoint batches; the primary recovered PR75 Anatomy Ch11 donors and reviewed source-detail retention. Restored omitted mechanisms/details and qualified unsupported absolute wording with provenance. PR76 Biochemistry Ch14 Q1–8 is already canonical/live and must not be double-counted.

Candidate source inventory rises from 670 to 753 enhanced, pending 2,041 to 1,958: 56 Anatomy / 15 Biochemistry / 12 Physiology across 11 bounded chapter batches. Nine previously approved Biochemistry entries receive emphasis-only fixes and no count increment. Four Physiology source placeholders become populated reviewed display tables, including a transmitter-row continuation on page 220. Exact PDF/hash/page metadata pins table ownership despite inaccurate imported explanation-page associations. Raw sources and 33 omission gates stay unchanged; three missing-list Biochemistry items remain excluded from enhancement. Four medical interpretation caveats remain explicit.

Added contracts for exact reviewed content/source ownership, baseline preservation, no duplicate counts, reconstruction schemas and verbatim emphasis. Browser verification compares all 92 touched runtime configs on phone/tablet and exercises representative answer/distractor/FSRS/table surfaces. Single combined full CI/preview is pending; no new build/physical acceptance or production promotion claimed at this checkpoint.

Historical image handoffs removed from current STATE after final completeness release (these pending/count statements predate verified de9c415c):

- Verified canonical source-reference coverage at d0e76fcc: Anatomy 1,012 released / 15 invalid / 1 held of 1,028; Biochemistry 133 released / 5 invalid / 0 unresolved of 138; Physiology 239 released / 38 invalid / 49 unresolved of 326. One reserved Physiology cue remains. Active 2026-09-30 ledger transfers paused Wave 2 ownership into four nonoverlapping resume batches (69, 52, 52, 64 items); Physiology Ch3–7 remains separately reserved.
- Physiology Ch3–7 ownership transferred by the user on 2026-09-30 to the primary serial writer. Final source review and reconciliation from canonical `af7e0dff` are source-verified; the single combined full canonical preview/package build remains pending. Coverage is 1,413 released / 79 invalid / 2 source-held of 1,494 references; all text cues are resolved. Exact image source extraction passed Ubuntu runs `36693009335` and crop refinement `36694166456`. Biochemistry source visuals are integrated; Ch17 Q14’s promised teeth image is absent from source. Anatomy Ch45 Q4 lacks its source marker and Physiology Ch6 Q10 lacks its numbered question figure. Anatomy Ch62 Q6 is separately missing its numbered list in the original source (direct page-1188 review confirmed); no image is withheld for that question.

Local verification: 53 checks executed; the sole failure was the 150-line STATE limit, corrected by moving superseded image handoff lines into history. The memory gate was rerun successfully; all other source/behavior/JS checks passed. Compiled runtime map independently reproduces all 753 approved IDs. Generated tracked bytecode was restored before committing. Full generated-app/browser/APK verification remains pending.

## 2026-10-01 — Explanation release certification and resumed parallel queue

Checkpoint d4abce86068b4221e61e541c34dd29258de61cca passed Engineering 36742636966 and full Android/PWA/phone-tablet run 36742637191. The 83-question wave is deployed in https://e954d103.nk-qbank.pages.dev, bringing enhancements to 753 and pending to 1,958. Earlier handoff write was blocked by environment execution/connector approval restrictions.

Permissions restored for the integrator and Biochemistry/Physiology workers. No existing worker worktrees or new saved files existed, so created isolated worktrees at the verified canonical checkpoint. The Anatomy worker retained a stale runtime restriction; replacement resumes its reviewed Q15–18 source audit/draft. User requests all remaining explanations, Luna self-source review, exception-only integrator review and one combined build. The deterministic queue has 1,935 actionable IDs (914 Anatomy, 263 Biochemistry, 758 Physiology) and 23 already gated Marrow omissions. Existing 753 explanations and all source/answer guards remain protected. Additional workers are limited by available concurrent thread slots; reassign freed slots where useful. Candidate authoring/combined verification is in progress, not complete.

### Resumed integration checkpoint

Integrated existing worker commits without reauthoring: Anatomy 59 (493639f7, 5edf20e2, 27e61bf0), Biochemistry 64 (23461895), Physiology 26 (d0ed79f5). Source-worker validation passes all 149 newly integrated entries. Candidate inventory is 902 enhanced/1,809 pending; 1,786 actionable IDs remain plus 23 pending source gates. The latest wave manifest pins the partial checkpoint and explicitly lists unprocessed actionable IDs; its completion gate deliberately blocks full CI release until all actionable IDs are accounted for. Worker authoring continues in isolated worktrees. Existing 753 augmentation fingerprints and source/gate hashes are protected. Infrastructure passed all 54 local checks; full generated/browser/APK/preview verification has not run for this candidate. Source header-alias table normalization has a passing actual-source regression fixture.

- Continued existing worker commits: current unpublished integration checkpoint has 312 new validated entries / 1065 candidate enhancements, 1623 actionable remaining plus 23 deferred gaps. Latest wave source hashes, old augmentation fingerprints and gate ledger pass checkpoint validation with explicit incomplete state; full CI still requires complete actionable coverage. Anatomy table/figure ownership is preserved, and Physiology Ch13 Q11 now has a populated source-page/hash-pinned table. No preview push/build has occurred.

- User milestone reached and reported at 542 newly integrated/validated explanations (1,295 candidate enhanced). Freed Biochemistry worker reassigned to 252 Anatomy tail IDs and then 261 Physiology tail IDs with separate audits; primary workers have disjoint chapter boundaries. Subsequent merged authoring totals 647 new/1,400 candidate; checkpoint validation caught an Anatomy reconstruction status label, being corrected by its author. Exception review also caught a gonadal arterial variant explicitly supported by the retained native adrenal table; worker is correcting the rationale. No combined preview build/push yet.

- 2026-10-01 continued local integration: 710 new validated explanations / 1,463 candidate enhanced; 1,225 actionable remain plus 23 existing deferred gates. Anatomy status metadata and adrenal variant rationale corrected. Released source ledger hash is now checked against the earlier certified wave even when regenerating pins. Primary Anatomy and Physiology plus reassigned Biochemistry tail worker continue; no new preview deployment yet.

- Continued chapter checkpoints integrated and validated: 790 new / 1,543 candidate enhanced, 1,145 actionable remaining. User explicitly reaffirmed completing all explanations before one combined push/build. Anatomy primary through Ch27, tail through Ch55, Physiology primary through Ch19. No new preview triggered.

- Checkpoint advanced to 860 new validated / 1,613 candidate enhanced, 1,075 actionable remaining. Anatomy primary through Ch28 and tail through Ch57; Physiology drafting respiratory graphs/equations in Ch20. Source ambiguity handling preserves printed keys while avoiding false anatomical explanations. All work remains local pending full actionable completion.

- 2026-10-01 checkpoint: 1,027 new explanations integrated/validated / 1,780 candidate enhanced; 908 actionable remaining, 23 source gates unchanged. Biochemistry263 and Anatomy tail252 complete; reassigned worker starts Physiology tail261. Primary Anatomy315/662 and primary Physiology197/497 complete. User reaffirmed single final combined push/build, no partial deployment.

- 2026-10-01 continued checkpoint: 1,206 new validated / 1,959 candidate enhanced, 729 actionable remaining plus23 source-held. Primary Anatomy338/662, primary Physiology212/497, tail Physiology141/261. Latest pins/source/gates/baseline augmentation hashes pass; no preview push/build yet.

- Balanced untouched Physiology ownership: primary stops at Ch27 (332 total,120 remaining after212 complete); freed tail worker takes Ch28–33 (165) after Ch34–43, with separate middle audit. Completed work is not restarted.

- 2026-10-01 checkpoint: 1,385 new validated / 2,138 candidate enhanced,550 actionable remain. Biochemistry worker completed Bio263,Anatomy-tail252,Physiology-tail261 and continues untouched middle165. Primary Anatomy397/662,Physiology212/332. Duplicate Anatomy emphasis anchor corrected; worker validator now catches duplicate anchors locally. No push/deployment before full completion.

- Finished Physiology middle165 integrated; primary Physiology Ch22 added20. Rebalanced untouched AnatomyCh43–50 (137) to available tail worker; primary stops42. Primary Anatomy through38 now450/525. Authored integration1623new/2376candidate,312actions remain. Exception-only review caught false pancreatic A/D ambiguity: optionA is hypertonic, not isotonic; worker correcting rationale before release.

- Final balancing of untouched Physiology25–27 (69) to Anatomy primary after Anatomy through42 complete; primary Physiology stops24 with31 remaining. Both acknowledged. Previously authored content remains untouched.

- 2026-10-01 checkpoint1,698 new validated /2,451 candidate enhanced,237 actionable remain. Anatomy primary525complete now authors untouchedPhys25–27; primaryPhys232/263; tailworker authors Anatomy43–50. Pancreatic rationale corrected after actualoptiontext review, combinedchecks pass. One final build/push remains deferred until all authoringdone.

- Integrated all actionableAnatomy; checkpoint1,835new/2,588enhanced validates. Final100Physiology split17Ch23primary,48Ch25–26Anatomyworker,35Ch24&27tailworker. All confirmuntouchedranges anddisjointseparateaudits. No previewpush yet.

- 2026-10-01 checkpoint1,887new/2,640enhanced validates;48actions remain Ch25–26. FinalPDFexceptionreview recovered Ch27Q9 five-roworganflowtablefromp492 via existing orphan tableblock withPDFhash provenance;Ch27Q13actualfigure2D/2L vsD/L explains8x, sourcecontradiction resolved. Added narrow orphanblock/pagevalidator and regression/browserowner coverage; immutablebanks/gates unchanged. Full previewbuild awaits final48.

- Final1935-actionable authoring complete:2688enhanced/23deferred/2711total,zero unprocessed IDs. All55localchecks pass; final2orphan tablesCh25Q6/Ch26Q3 now rendered displayTables withsourceIDs/pages/PDFhash,completewave revalidated aftermerge. Ten tableowners recovered in thiswave. Existing753augmentation fingerprints,rawbanks,gates unchanged. Three explicit sourcecaveats remain inenhanceditems (Bio17Q22 missinglabs,Bio26Q15capping ambiguity,Phys32Q28fiberwording). One combined canonical push/fullpreviewbuild next; no newcandidate buildverification yet.

- Combined product08ded423 pushed: Engineering36841656512 passed; fullrun36841656565 failed in explanationbrowser onPHYSIO_CH23_Q018 selectiveemphasis beforedeployment. Rootcause: presentationtransform scientificformats text(H+ ->sup), but leavesanchorplainescaped. Narrowfix scientificformatsneedle identically. Actualrendererregression checksfailingH+,escaping,all2546authored displayconfigs including1935new; early inbothCIworkflows. All56localchecks pass; replacementbuild required. No source/explanationrecords changed byfix.

## 2026-10-01 — Completed explanation release and scientific-emphasis regression

Product `9d318f79d73d6f22a3c6f508e10f1fb243aea349` passed Engineering `36870646707` and full Android/PWA run `36870646652`, including phone/tablet Android WebView interaction, hardware Back, force-stop resume, review and FSRS checks. Preview: https://ac2f50ca.nk-qbank.pages.dev. Production was not promoted; physical acceptance is not implied.

All 1,935 actionable explanations from the initial 1,958 pending are authored and integrated: 914 Anatomy,263 Biochemistry,758 Physiology. Total2,688 enhanced /23 explicitly source-held /2,711. Complete-wave checks protect old753 augmentation fingerprints,immutable raw banks and unchanged answer gates. Ten source-reviewed explanation table owners were recovered, including three omitted table objects anchored to existing table-block IDs and original explanation pages.

Initial combined full run36841656565 failed before deployment on PHYSIO_CH23_Q018 emphasis: scientific formatter converted H+ to superscript HTML while anchor matching used plain escaped text. Fixed identical scientific formatting on text/needle, and added actual-renderer regression for the exact case, escaping and all2,546 authored display-text configurations. This regression runs early in bothCI workflows; all56 local checks passed. Replacement full browser suite passed3,870 exact runtime checks and562 rendered cases across phone/tablet. Live downloaded preview matches all2,688 approved configs exactly, includes corrected renderer and three orphan table recoveries; HTML SHA-256 bdc7702f8b9b6dc68b3ae1fbd6d7cd963baf6f2b274360c2b9eb158a3751c4f2.

Three enhanced items retain explicit source caveats (Bio17Q22 absent labs,Bio26Q15 capping ambiguity,Phys32Q28 fiber wording). All23 pre-existing pending source gates are deferred at user request. No actionable explanation work remains; do not restart completed workers. This final certification is docs-only with skipCI so it does not schedule another preview build.

## 2026-10-01 — User-approved combined main release

User approved explanation previewac2f50ca and runs1375(d3247ca6 liquid streak/Revision) and1378(4a14b0cf revision/FSRS fixes);1378descends1375. Integrated latest main/home-revision-hub with complete explanation branch, preserving both feature implementations and all2688 augmentation configs. Image coverage:1421released/79invalid/twoarchival gaps/zero reviewcues; not a literal all-source-reference completion claim. Added explicit approved-production commit-marker workflow to deploy only successful full main build artifact with exact commit/currentmain/APK identity verification and Pages production_branch=main. No unapproved automatic production releases; manual exactSHA flow remains. Combined localvalidation/buildpending.

- Main mergef286e555 passed79localchecks and Engineering36881025618. Fullrun1379/36881025495 passed explanations,Revision,editableFSRS andstudyjourneys, but UIcapture timedout waitingforanswerbuttons afterrandom all-bankCBTstart. That fixturecanselect intentionallygatedsourceitems; noactivequestion diagnosticwas saved. Changedonlycapturefixture toMarrowBiochemistry firsttopic andaddedactivequestion/session/visibletext diagnostics. CBTbuilderbehaviourtests pass; productgates/selectionbehaviour unchanged. Productionblockeduntilreplacement fullrunpasses.


## 2026-10-01 — Learning Insights implementation

User supplied phone/tablet analysis prototypes and requested all their learning dimensions in a scrollable responsive Insights screen. Built from combined main and reconciled its deterministic CBT screenshot repair18e4cd5. New owner/core/styles implement week/month/year browsing, same-elapsed comparisons, all-subject/bank scopes, paired outcome donuts, answer bars with interval details, study-time trend, topic/subject accuracy, actual spaced-review accuracy/due forecast, corrected-mistake recovery and module progress. Optional result sessionId metadata makes future timing attribution exact; legacy result matching avoids duplicating answer and session time.

During review, user explicitly removed Study Map and Topics to revisit, then required a top-of-page full-year heatmap. Calendar tiles show daily details, month labels, rolling/calendar-year selection, totals/longest run and phone scrolling. User approved its appearance and replaced fixed intensity buckets with continuous comparative count/maximum shade and glow, recalculated for displayed year/scope. Tests prove40/60 differ, doubling workload preserves relative color, and a new peak lightens earlier days. Local81 checks and four responsive browser journeys passed before the final heatmap steering; rerun final checks/CI. Continue Practice full generated regression passed. Existing medical data/images/explanations and five-tab navigation stay protected; Insights promotion is not authorized.

## 2026-10-01 — Approved combined production release completed

Product `18e4cd58a09f14169447dd7aaf13a6cc08971ceb` passed Engineering `36883870916` and full Android/PWA run1380 / `36883871119`, including Android emulator checks. The deterministic answerable-topic screenshot fixture passed. User-approved runs1375 and1378 features and all2,688 enhancements are merged into main. Full-build workflow_run production follow-up did not appear; a dedicated release-branch push deployed the existing verified artifact without rebuilding. Production run `36888530721` verified exact current-main/artifact/APK identity, set Pages production_branch=main and published https://3bbd46cc.nk-qbank.pages.dev. Root https://nk-qbank.pages.dev is byte-identical (HTML SHA-256 `f0f9bb3ce205c6f79ae024d5025ffcce8c977a0915dc178c5307c83be5145c2a`). Entire live2,688-entry explanation map equals approved configs; liquid streak, Revision and editable-rating markers are present. Main and content integration branch are synchronized with this docs-only release handoff; no new full build is required. Preserve23 source gates, two archival image gaps and422 PrepLadder source-comparison audit entries. This is user-approved production promotion, not a claim of new physical Android testing.

## 2026-10-01 — App-wide clarity pass with comparative Insights

The user supplied phone screenshots showing repeated page kickers/subtitles, definitions under obvious Revision labels, and excessive header gaps. They requested removal of noise across the app, and authorized promotion of the combined Insights/clarity candidate to main and https://nk-qbank.pages.dev after verification. The late deterministic clarity owner trims navigation-only markup, compacts main page headers, Revision queues, Home focus, FSRS settings and builders; counts/actions, safety warnings, save/sync states, subject/bank context and source questions/explanations remain protected. Insights now starts with title/controls and Activity, removes repeated chart instructions and promotional summary, and keeps metric definitions in collapsed help. Continuous heatmap intensity remains relative to the selected year/scope peak. Screenshot inspection and browser checks cover ten screens and two builders at320/390/820; all four populated Revision queues fit above phone navigation. Existing Continue Practice, missed-question/FSRS and Revision/streak browser checks pass. The previous94e1 build passed web/PDF/APK but Android tablet attempts lost a screenshot target and then timed out reconnecting WebView; neither is a certified final candidate. Full combined CI and production delivery remain pending. Current main release handoff ecf7906 was merged, retaining verified18e4 production content and release workflow.

## 2026-10-02 — Final clarity certification follow-up

Full candidate fce4277 run36894992491 passed source gates and earlier browser checks but stopped at verify_revision_desk_browser.py:181: the test searched for “Practice 1 mistakes” after the presentation owner correctly changed it to “Practice 1 mistake”. Update singular mistake/bookmark locators, rerun the whole journey and full candidate CI. Main remains ecf7906; user authorized promotion after checks pass. Earlier failed APK/Android attempts need not be rerun independently.

## 2026-10-02 — Canonical Insights/clarity release and analysis refinement

Certified product `1ba1635428a661c4e9c152e2e90d75b441c05b0b` passed feature full run36947218296, main full run36949193523 and both Engineering gates; phone/tablet emulator interaction checks passed. PR81 merged. Automatic production workflow did not start, so release-only branch `release/approved-production-20261002-clarity` pins that exact successful main artifact. Deployment36951774743 passed manifest/APK/current-main identity checks and published canonical https://nk-qbank.pages.dev. Root HTML exactly matches certified preview SHA25624ad5d627b94e25c9d6f79cbdc8ff73ec759f924ea8fde533d21c5d84cfb8737; fresh hosted390/820 contexts verified periods, relative intensity, reload and absent rejected sections. No physical-device claim.

User then requested contextual week/month/year chart labels, aligned donuts/bar labels, a compact test analysis with calm green/coral/amber outcomes, test-only subject/topic breakdown, honest score/accuracy and timing, and named repeatable mocks. New branch `feature/home-analysis-refinement` installs one late result owner, preserves Review/marked/correction/retake/module paths, and adds saved exact mock sets through durable state and per-entity sync/tombstones. Modules already have names and save/restart. Initial84 local checks and responsive320/390/820/1194 generated result/mock/alignment journey pass; final regressions and full CI are pending, so this refinement is not production-certified yet.

Latest user steering removes the top-right active-subject icon/text from the global header, including Test Analysis and Practice. The original whole-app header owner now omits the badge; source selection remains in the library and question context is preserved. Result screenshots are recaptured and the generated browser checks assert badge absence.

The user additionally requested removing the entire NK QBank global header outside Home to lift the content. The original header owner now returns empty markup on non-dashboard routes; Home retains its existing branding. This supersedes the badge-only candidate and requires fresh screenshots/full certification.

## 2026-10-02 — Interaction latency recovery and polish

- User authorized the excluded b143242/89f949e latency/native-owner work and a
  native-feel implementation pass without redesign. Recovered compatible deltas
  and added shared cancellable presses, committed in-place question mutations,
  restrained/reduced-motion motion and sheet focus/scroll containment.
- Local baseline CBT medians ~12.4 ms → ~4 ms. Responsive failed-save, editable
  FSRS, Continue, correction, study journey and result/mock checks passed.
  Ordinary navigation is silent; Practice has one outcome pulse. Full new
  candidate CI and production promotion remain pending; no physical haptic claim.
- Analysis/header run36953970794 passed build but Android disconnected during
  source-PDF element capture; requested unchanged-c662 failed-job rerun.
  Main/root still certified1ba. See docs/INTERACTION_POLISH_2026-10-02.md.

## 2026-10-02 — Certified interaction candidate promoted to main

Product a68e9c2d6e2b8f121b747c2aba53d9cc5ffeec75 passed feature full36956370295
(first attempt), both Engineering gates36956370263/36956374578, 87 local checks
and fresh hosted phone/tablet touch/Bookmark/Pause/Insights checks. Main was
fast-forwarded to the exact certified product; PR83 and ancestor PR82 are merged.
Main full36957980864 now verifies the official Android identity and supplies
the production artifact. Canonical root remains previous1ba until that run
passes and the exact artifact deploys; preserve main identity throughout deploy.
The isolated c662 run36953970794 also passed after its unchanged Android rerun.

### 2026-10-02 — User-reported press latency / gentle answer feedback

Main a68 is build-verified from feature CI, but the user reports its new interactions feel slower across the app. Hold canonical deployment while correcting shared110 ms state/release transitions and added route/question/sheet movement. A/B computed appearance confirms old answer colors persisted on the first frame; correction makes committed colors immediate with no transition. Preserve save/indexing/in-place improvements and rollback. User additionally requests subtle answer haptics: single7/9 ms browser pulses and native CLOCK_TICK outcomes. Fresh responsive/browser/native certification pending on `feature/home-answer-latency`; root still serves1ba.
