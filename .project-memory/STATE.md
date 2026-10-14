# STATE.md — Current Project State and Handoff

> Operational state only. Resolve the live branch/commit and CI from Git before acting. Historical detail belongs in `SESSION_LOG.md` and dedicated handoffs.

## Microbiology Marrow subject — 2026-10-14

- Branch `feature/microbiology-marrow` (from main `b064fec`) adds **Microbiology** as a fourth My Subjects entry with one bank, Marrow (no PrepLadder). Source: `data/marrow/microbiology/source/Microbiology_Marrow_Qbank_01.jsonl` (raw, immutable) cross-checked against `data/marrow/source_pdfs/Microbiology Marrow Qbank.pdf` (LFS; JSONL pages 1–26 = PDF pages 1–26). Part 01 = 102 questions / 5 modules; module 5 (Staphylococcus) holds 15 of its 30 questions — later JSONL parts append through the same builder.
- `tools/build_microbiology_marrow_bank.py` normalizes to `marrow-bank-1.0` (IDs `marrow__MICRO_CHmm_Qnnn`, MCQ ID kept as `mcqId`, `keyTakeaway` = source answer summary, explanation as ordered blocks with tables/Marrow Pearls/notes) and writes hash-pinned shards `data/marrow/microbiology_marrow_qbank*`. `marrow_bank_data.app_marrow_records()` appends it after the canonical ED8 three, so every 2,711-question ED8 gate is unchanged. Display hygiene only: extractor table annotations removed, bracketed clipped-word completions merged, one source-checked typo fix (MA1527).
- App: Marrow-only subjects join `SUBJECTS`/`SUBJECT_BY_NAME`; same Practice/CBT/Review/FSRS/modules engines. Explanation layout `ordered-blocks` renders through `nkRenderMarrowOrdered` (other banks untouched). Topics taxonomy: Immunology, Systemic bacteriology. 35 figures: `data/marrow/microbiology/visuals.json` + `tools/microbiology_visuals.py` → `marrow_visuals/<sha>.jpg` + `microbiology_visual_metadata.js` (merged into `MARROW_VISUALS`; ED8 image registry untouched). Crop review pending.
- Part 02 (2026-10-14): `Microbiology_Marrow_Qbank_02.jsonl` (98 questions, split PDF pages 1–21 = full PDF pages 27–47, new field names = schema 2) appended via `PART_LAYOUT`. Module 5 is now one 60-question module "Staphylococcus, Streptococcus, Enterococcus & Pneumococcus" (part 01 had reported 30; the source tabs run to 56–60); modules 6 Corynebacterium… (33/33) and 7 Clostridium (20/30) added. Total 200 questions / 7 modules, 71 figures (36 new, user-supplied). All 98 stems/options/poll percentages OCR-matched to PDF pages 27–47.
- Peer statistics: Microbiology questions now show the UWorld-style "% got this right" chip and per-option pick rates (hidden until answered) from `sourceStats`, via `nkSourceCohort`/`nkSourcePollPercent`; other Marrow/PrepLadder questions unchanged.
- Build-verified (part 01): Engineering 38520440355 and full PWA run 38520437818 (attempt 2; attempt 1 hit the timing-sensitive `verify_source_viewer_browser` zoom check, unrelated) pass. Preview https://feature-microbiology-marrow.nk-qbank.pages.dev. Device checks and user acceptance pending; not promoted.

## Production, IndexedDB progress and faster CI — 2026-10-12

- User-authorized production: PR #109 merged as `39cc716166f1551175d7703af44c16aa747683e1`; dispatch run 38201928452 verified and promoted it (Pages production branch `main`). The production domain is behind Cloudflare Access (email PIN / Google, owner only); `*.nk-qbank.pages.dev` previews are not covered by that Access app.
- Branch `feature/home-v12-redesign` continues after the release: progress lives in IndexedDB (`app/src/main/assets/nk-store.js`, loaded before every other script). Heavy `qbank_state_*`/backup keys are served from memory, committed per task in one IndexedDB transaction, and the primary is also written synchronously to localStorage so an instant reload never loses a save. First run migrates localStorage; restore points (30 min / daily / before reset, restore, migration) are listed under More > Restore points. Checked by `tools/verify_progress_store_browser.py`.
- CI: `tools/run_browser_suite.py` runs all browser verifiers four at a time in one step (Marrow wrapper's eight scripts and four UWorld widths are separate entries); UWorld exhibit crops are cached on their inputs (browser-case helpers excluded from the key). Full green run ≈16 min (was 25–35). Geist is the only UI (the `?ui=legacy` switch is retired) and every verifier tests it. Legacy markup/CSS remain as Geist's base. `tools/prune_unreachable_css.py` (run by `build_web_dist.py`) drops CSS whose required classes/ids appear in no markup, script or data of the build (~110 KB: ~56 KB legacy inline, ~52 KB pruned from `redesign/` sources). Legacy rules Geist overrides were then removed (see Bake).
- Bake: `app/src/main/assets/index.html` is source (≈180 KB: markup and scripts, no data, no module copies, no CSS). The 62 build-time patch scripts are retired (read them with `git show eb84d7f6:tools/<name>.py`); `MainActivity.java` and `source_visual_renderer.js` hold their generated form. Script features live in `app/src/main/modules/*.js` and sit in the page as `/* @module <file> */` markers; tests read the page via `tools/app_page.py`. Data sits at `__NK_DATA_<NAME>__` tokens, filled by `tools/build_app_data.py` (output byte-identical to the old 19 MB page). All CSS is one stylesheet, `app/src/main/assets/app.css` (old Geist files first, then the former inline blocks in cascade order, each headed `/* ── <name> ── */`); declarations that always lost to a Geist rule were removed, checked by a computed-style comparison over ~380 verifier screenshots (light/dark, phone/tablet): no real differences. Do not reintroduce page-patching steps; add CSS to `app.css` under a new section header.
- Open app findings (not yet fixed): gold wrong-option label uses `esc(o.text)`, not `nkScientificMarkup`; `startAllSubjectPractice` has no button; `nkInsightsExpanded`/`nkToggleInsightsExpanded` unused; the Insights focus and coverage sections are no longer shown since learning_insights replaced `analytics()`. Restoring or removing them needs the user's call.

## Notes, PDF loader and shared viewer — 2026-10-10

- Main has question notes with images/PDF pages (#103: My notes bar, block note page, IndexedDB + chunked `noteAssets` sync, Android file chooser). Branch `ccr-47681b8d-1aikn7` adds the PDF loader/glyph repair work from `feature/home-pdf-loader` and one shared viewer (`redesign/nk-viewer.js`) for Geist source PDFs and note images: opens at once from the on-screen canvas, swaps in a cached sharp render, firm edge-to-edge panning. Details: `docs/PDF_RENDERING.md`, `docs/QUESTION_NOTES.md`.
- Build-verified notes on main (full run 38057009229). Viewer branch: local checks and local browser checks (`verify_source_viewer_browser`, notes media) pass; CI, production promotion and iPad/Android device checks pending. Production promotion was user-authorized on 2026-10-10 after this viewer work.

## Previous certified production reference — 2026-10-04

- Production product315cfcccc2a0d830aa851fbd136f3e8d14e215e8 / merged PR98 includes the accepted interaction/visual/revision feature chain, all three UWorld collections and the app-wide audit repairs. The user explicitly authorizes promotion accessible through https://nk-qbank.pages.dev. A separate docs-only handoff records certification without advancing the verified main product.
- All 103 local checks, Engineering37191000202 and complete main37191000207 pass, including production APK identity/package/media/offline/browser and Android phone/tablet emulators. Approved release 37192960486 verifies/reuses that exact artifact, sets Pages production branch main and succeeds. The canonical root matches the CI-measured HTML SHA-256086b04f41fcf610af844b76652b7c6368392dc26d9bd8f609b258b2a6e77897b; HTML/config/service worker/inventory/robots bytes match https://92774e98.nk-qbank.pages.dev.
- Ophthalmology30 questions/204 pages/8 native tables/77 source figure placements is source-reviewed from original56fe817 PDF SHA-256ab4aadac54fbc78c9db9fca4b561cb5d0ee0ba4ade3f72066c72bf64021843dc. Three user-authorized Luna/high batches plus independent root checks preserve original keys, prose, percentages, objectives and page provenance;41 crop repairs retain scientific labels. Only this PDF-only block is added; other supplied packages remain queued.
- Actual main-domain390/820/1194/1440px UWorld flows,320/390/820/1440px audit repairs and phone/tablet Search/focus pass. All 283 UWorld assets match their packaged inventory hashes and offline paths; the prior206 media identities remain unchanged. Streamed source-PDF ranges and security/crawler response headers pass; cross-origin framing is rejected. Shared study engines, scoring, FSRS, stored data, native haptics and accepted appearance remain protected.
- Audit repairs: account Back/email/contrast, narrow Topics controls/focus, empty FSRS actions, completed-start Android migration/file/private-asset boundaries and hosted frame/MIME/referrer policy. This is build-verified/hosted-verified, not new physical-device or clinical acceptance. Preserve known source gates and public-content/search-exclusion limits. Use the canonical root; the older main preview alias is stale. Reports: `docs/PREPRODUCTION_AUDIT_2026-10-04.md`, `docs/UWORLD_OPHTHALMOLOGY_COLLECTION.md`.

## Certified Biochemistry reference

- Product424e0ca80e57fc946ad96f41d38547bcbc23d089 / PR94 stacks on93 and passes full37158603961 plus both Engineering gates and101 local checks. Actual hosted four-width flows,184 offline assets and crawler headers pass at https://2f165b3a.nk-qbank.pages.dev; HTML SHA-2569bc847becbabe6eb1cf9da681deaa808da1bc4bd1bb58762ab71a6fd48022c02. Details/source limitations: `docs/UWORLD_BIOCHEMISTRY_PILOT.md`.
-132 reviewed records/729pages;131 scored questions;1244 unscored because its essential exhibit is absent. Objectives1486/1071/107111 and figure sections1369/1244 are source-clipped. Missing stats stay null; accepted17px/70ch source-native layout, objective-after-explanation and immediate option percentages remain.
- Practice mistakes only tracks unresolved ordinary Practice/test misses; FSRS-only lapses affect scheduling without creating or resurrecting ordinary mistakes. Correct answers from any flow resolve an ordinary miss. Continuous Revision/Pause/Finish remains accepted. No new installed-Android, haptic or clinical certification is claimed.

## Canonical lineage

- Accepted product commit: `125d68b`. Accepted baseline: V11.6 remains the rollback product baseline; the Continue Practice contract below is separately user/device accepted.
- **Production integration trunk:** `main`; `feature/marrow-canonical-full-current` remains the content-work lane and needs fast-forward alignment to the released Insights/clarity product before future content work. Preserve merged Revision/streak/FSRS features.

## Complete canonical Marrow ED8 source

- Anatomy: **Ch1–63 / 1,115 questions / 63 source topics**.
- Biochemistry: **Ch1–28 / 582 questions / 28 source topics**.
- Physiology: **Ch1–43 / 1,014 questions / 43 source topics**.
- Global: **2,711 questions / 134 source topics**.
- Raw imported source remains immutable.
- Source handoff: `.project-memory/FULL_CORPUS_CONSOLIDATION.md`.
- Mandatory automation policy: `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md`.

## Product architecture to preserve

- Impeccable interaction, return-flow, source-search, analysis and PWA-update behavior remains protected (certifications in SESSION_LOG). BC3/BC4 interaction hardening is reconciled at `43328c1`; history in `docs/BC4_QUESTION_INTERACTION_DEFECT_LEDGER_2026-09-22.md`.
- Shared bank architecture: `MARROW_RECORDS → MARROW_BY_SUBJECT → BANKS_BY_SUBJECT`.
- Do not fork Practice, CBT, Review Solutions, FSRS, sync, modules, persistence, analytics or navigation by subject/bank.
- Primary navigation: **Home · Revision · Tests · Insights · More**; FSRS remains inside the approved Revision study hub.
- Study hierarchy: **My Subjects → subject → bank chooser → Topics journey → topic → Practice/Topic Test**.
- FSRS schedules every answered question. Pause commits answered work only; final submission adds remaining unanswered session IDs as skipped. Questions outside a submitted session remain unseen and excluded.
- Preserve approved V3 Home/Topics/question/Review/FSRS/module/timing behavior; do not restore rank/membership UI.

## Accepted Practice / Continue Practice contract — user/device verified

- Normal Practice footer = **Previous + Next only**.
- Header grid icon and end-of-session boundary open the **same final review grid**.
- Final review action area = **Pause + Submit only**.
- Do not restore the redundant intermediate Question Navigator, `Back to question`, or `Review unanswered` actions.
- Pause preserves the same active session, full original ordered `sessionQuestionIds`, saved/current index, answers, submitted state, timing and progress.
- Pause does not mark the current unanswered question skipped merely because the learner exits.
- Home Continue Practice resumes the same session ID, restores the complete original ordered test/question list, and returns to the saved position with answered progress intact.
- If an older buggy client reduced `questionIds` to one current question, rebuild the visible session from `sessionQuestionIds`; a multi-question session must never collapse to `1 / 1`.
- Special modes (CBT, Review, Wrong/Bookmarks, FSRS, Custom Study Modules) remain outside this override unless explicitly redesigned.
- Postmortem: `.project-memory/PRACTICE_FLOW_POSTMORTEM_2026-09-12.md`; implementation handoff: `.project-memory/CONTINUE_PRACTICE_HANDOFF.md`.
- Status: **accepted / device-verified / user-verified**. Do not describe this flow as pending.
- Multiple paused Practice chapters were reconciled into canonical at `cb3f44b`; Engineering `35850509766` and full Android/PWA/browser/APK/emulator run `35850509865` passed. The user confirmed the chooser/resume flow in the UI-branch preview; physical Android acceptance of this extension remains pending.

## Mandatory Practice regression sequence

Any change touching Home, Practice, session persistence, sync, question navigation, final review, FSRS injection or build transforms must exercise the generated learner path: start a genuine multi-question Practice session; answer several questions while leaving at least one unanswered; open the final review grid and Pause; confirm Home/paused lifecycle; use the rendered Home Continue Practice control; verify same session ID, complete ordered IDs, saved/current index and preserved progress; verify no `1 / 1` collapse and no Pause-as-Skip mutation.

## Structured explanation-table invariant

- Structured text tables are explanation-owned unless the source is explicitly an image/raster table.
- Non-empty source headers/rows must render as non-empty learner-visible headers/cells in correct order; `[object Object]` is a hard failure.
- Browser regressions must verify meaningful expected cell content, not container existence.
- User physically verified the structured-table repair at `c829599050173d24408b72e8dc564ba501a156b4`.

## Matching/list and structured-question presentation

- Shared structural parsing and source-fingerprinted reform preserve canonical
  choices/keys across Practice/CBT/Review. Structured ion question `physiology-9-17`
  is user-preview verified. Axonal transport `physiology-9-22` and source-backed
  residuals passed full run `34855852211`; physical acceptance remains separate.
- Full details and residual identities: `.project-memory/MATCHING_TABLE_ARCHITECTURE_HANDOFF_2026-09-14.md`.

## Learner-content hygiene

- Whole-corpus serialized JSON/code sanitizer candidate `45f6539fff535fadc6aaa6970894f9ff123422fa` passed Engineering `34738522874` and full run `34738530102` over **2,711 questions / 27,898 learner-facing fields**; raw ED8 source is unchanged.
- User preview review found residual OCR debris in Physiology Ch5/Ch7; verified follow-up `55d7ac8a89c2bbf6a01db5d305b8c975c344c1f3` added source-fingerprinted stable-ID display overrides for those two chapters. Engineering `34740460617` and full run `34740465004` passed; production skipped.
- Physiology Ch6 Q1–34 and Ch9–12 source text cleanup is verified at `232f0182`: Engineering `36665702451` and full browser/PWA/APK/Android run `36665702481` passed. A fresh canonical preview fetch matched all186 reviewed stems/options across Ch5–7 and Ch9–12. Browser expectations use shared scientific markup (e.g. Cl−). Raw ED8 and answer indices remain unchanged; other chapters/explanations are unreviewed.

## Explanation lane

- Released explanation checkpoint: **2,688 enhanced / 23 deferred / 2,711 total** at product `9d318f79d73d6f22a3c6f508e10f1fb243aea349`. Engineering `36870646707` and full Android/PWA/browser/APK/phone-tablet-emulator run `36870646652` passed. Preview `https://ac2f50ca.nk-qbank.pages.dev`; now included in the approved combined production release above.
- The parallel Luna continuation completed all 1,935 actionable explanations (914 Anatomy, 263 Biochemistry, 758 Physiology) in 178 bounded batches. Queue/wave manifests and separate worker audits preserve all 753 prior augmentations, immutable source banks and existing answer gates; zero actionable IDs remain.
- Initial combined run `36841656565` at `08ded423` failed before deployment because scientific H+ formatting broke emphasis matching. The released fix formats text and anchors identically. New actual-renderer regression covers the exact failing item, HTML escaping and all 2,546 authored display-text configurations early in both workflows; all 56 local checks pass.
- Full explanation browser verification passed 3,870 exact runtime-config checks and 562 rendered cases on phone/tablet. The live preview's entire 2,688-entry explanation map exactly matches approved content and includes the renderer fix. Live HTML SHA-256: `bdc7702f8b9b6dc68b3ae1fbd6d7cd963baf6f2b274360c2b9eb158a3751c4f2`.
- Ten explanation table owners recovered during this continuation use source-PDF/page/hash-pinned display tables. Orphan table objects are allowed only for existing source table-block IDs and original explanation pages; browser QA checks headers/cells. Headers aliases remain supported without source mutation.
- All 23 incomplete-source Marrow questions remain deferred with existing gates. Three enhanced items retain explicit source caveats: Biochemistry Ch17 Q22 absent labs, Ch26 Q15 capping ambiguity, Physiology Ch32 Q28 dietary-fiber wording. Physical blanket acceptance remains unclaimed. Resolve live Git HEAD separately from the verified product SHA above; any later docs-only certification commit does not change the product.

## Image lane

- Source-visual owner resolution, fullscreen/zoom, multi-panel and phone/tablet
  browser/package checks are build-verified at `2340bd2` / full `35053564213`.
- PrepLadder technical validation does not replace its 422-item manual source
  comparison audit: `.project-memory/PREPLADDER_VISUAL_VERIFICATION_2026-09-16.md`.
- Marrow image work is complete at the final checkpoint/counts in Current
  priorities below. Two archival source gaps remain. Historical batches and
  invalid metadata adjudications are in SESSION_LOG and the image handoffs.

## Anti-fragmentation rules
- Explanation and image work build from `feature/marrow-canonical-full-current` and the complete 2,711-question corpus.
- Re-read canonical `STATE.md`, live commit, inventory/registry fingerprints and current ownership before editing.
- A stale PR/branch is historical evidence, not a lock or merge target; transplant only stable-ID/content-scoped work after ownership and duplicate checks.
- Reconcile verified work into canonical before starting another conflicting batch in the same lane.
- Accepted product/UI fixes are protected canonical behavior for subsequent content/image/explanation work.
- Automation start and reconciliation instructions: `.project-memory/IMAGE_AUTOMATION_READY_2026-09-20.md`. The historical percentage-correct pilot branch is not integrated and must not be used as an image base.
## Known problems / cautions
- PrepLadder source-visual technical/browser gates are green, but **422 audit entries still require manual source-comparison review**; do not label that lane release-certified yet.
- New axonal-transport and source-backed residual structured presentations are build-verified but still need user physical preview review before acceptance.
- Future flattened table/list questions may exist outside literal `match` wording; treat them as structured-presentation defects, not ordinary prose cleanup.
- Earlier OCR counts (seven question records and 56 explanation records) predate the final completeness pass below. Question-essential uncertainty was included in the focused review; remaining explanation-wide cleanup is separate and must use pinned source evidence.
- Four PrepLadder source records remain intentionally non-answerable rather than recording corrupt attempts: `anatomy-22-4`, `physiology-23-38`, `physiology-24-6`, `physiology-33-33`.
- The user explicitly authorized the audited UWorld/app release; production is live after full verification. Future unrelated promotions still require authorization.
## Current priorities / Next step
1. Completed final completeness pass source-reviewed 254 unique questions (226 initial + 28 supplemental): 89 repairs (74 contextual/15 exact; 81 text/table/notation/key and eight native images), 132 already complete, 33 underdetermined source omissions gated, including ANAT62Q6. Compiled display ledger: 114 entries; source tests pass across four variants. CI queue requires all new structural/glyph/question-visual candidates reviewed (195 current residual candidates; zero unreviewed). See `docs/QUESTION_COMPLETENESS_FINAL_PASS.md` and the pinned `data/question_completeness_reviews_v1.json` ledger. Raw imports remain immutable.
2. Regenerated final image coverage: 1,502 references / 1,421 released / 79 invalid / two archival holds / zero unresolved cues; runtime 1,486 bindings / 1,306 assets / 1,128 owners. All 52 final local checks pass. Product checkpoint `de9c415cef4915d5b20a42abc9f2299a8595b173` is fully build-verified: Engineering `36732893469` and full browser/PWA/APK/package/Android-emulator run `36732893814` passed. Preview: `https://74f04894.nk-qbank.pages.dev`. All 114 contracts passed 228 runtime checks; eight recovered image URLs match exact native hashes in the live preview. Earlier image/browser assertion failures are resolved.
3. Certified web-first product31bff68 is live on main and the canonical domain, including both reproductive collections and complete Biostatistics Block1. Next: source-review the remaining81 complete Biostatistics items in bounded batches. Preserve23 source gates, two archival image gaps, the PrepLadder audit backlog and shared study engines; APK work is on demand.
4. Preview-only candidate `feature/home-geist-redesign` (2026-10-08, from main07f6e8c): user-approved neutral Geist redesign as a presentation layer in `app/src/main/assets/redesign/` (tokens, generated legacy colour map `tools/redesign_generate_theme_css.py`, component CSS, Phosphor/Geist vendored offline, theme Light/Dark/System, additive local Profile at `#profile`). Gated on `html[data-nk-ui="geist"]`; `?ui=legacy` restores the old look and browser automation (navigator.webdriver) keeps legacy so existing contract suites are unchanged. No logic/renderer edits; not accepted, not for main/production. Report: `docs/GEIST_REDESIGN_PREVIEW_2026-10-08.md`. Stacked polish candidate `feature/home-geist-polish-20261008`: system pass `redesign/nk-polish.css`, interaction layer `redesign/nk-feel.js` (vendored Motion 12.23.12, layered haptics), user-approved prototype concepts 01/02/03/05/06/07/10 integrated, 08/09/11/12 reworked per user feedback; 108 local checks pass; Full PWA 37805280869 + Engineering 37805281108 pass at aa65e83e; preview https://feature-home-geist-polish-20.nk-qbank.pages.dev. Logic/FSRS audit on the same branch (Anki-style due/learn-ahead/ordering/fuzz, unanswerable-question gates, Continue Practice loop, streak/accuracy undo leaks, legacy list routes): `docs/LOGIC_AUDIT_2026-10-08.md`; physical review pending. Report: `docs/GEIST_POLISH_2026-10-08.md`.
## Memory pointers
- PrepLadder visual verification handoff: `.project-memory/PREPLADDER_VISUAL_VERIFICATION_2026-09-16.md`.
- Matching/structured presentation handoff: `.project-memory/MATCHING_TABLE_ARCHITECTURE_HANDOFF_2026-09-14.md`.
- Practice postmortem: `.project-memory/PRACTICE_FLOW_POSTMORTEM_2026-09-12.md`.
- Canonical source consolidation: `.project-memory/FULL_CORPUS_CONSOLIDATION.md`.
- Automation policy: `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md`.
