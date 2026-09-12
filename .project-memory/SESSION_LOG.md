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
- PR #45 merged only into `feature/marrow-canonical-full-current` at `d84a8093468c278a19e81e917bcc66da91f33574`. Exact-head canonical Engineering Gate `34685236474` and full run `34685236486` passed, including the 16-question browser resume invariant and APK/package/reproducibility gates. Canonical preview: `https://fe6ec51b.nk-qbank.pages.dev`; artifact `10295367582`; production promotion skipped. Physical-device acceptance remains pending.
