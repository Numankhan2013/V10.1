# STATE.md — Current Project State and Handoff

> Operational state only. Resolve the live branch/commit and CI from Git before acting. Historical detail belongs in `SESSION_LOG.md` and dedicated handoffs.

## PrepLadder text banks — Microbiology (1,202 Q / 42), Pathology (1,459 Q / 90), Pharmacology (1,321 Q / 59) — 2026-10-17

- **Pathology (new Second Prof subject, PrepLadder only).** `tools/build_prepladder_pathology_bank.py import <master.jsonl> <images>` (shared pipeline `tools/prepladder_text_bank.py`, Microbiology's text/block rules); data `data/Prepladder/pathology/` (1,676 figures, 1,127 border-trimmed); IDs `pathology-<lesson>-<n>`; 27 PYQ lessons (615 Q). Checked against `pathoprep11.pdf`: all 1,450 printed keys match; 14 explanations the PDF itself omits show a plain note + review note; 9 image-only option sets (blank PDF key) stay `needs_review`. Identity: microscope icon, `--nkg-subj-pathology`, `NK_PROF_GROUP_BY_SUBJECT` Second Prof. Ledger `docs/PREPLADDER_PATHOLOGY_2025-11.md`; tests `tools/test_prepladder_pathology_bank.py`, `tools/verify_prepladder_pathology_browser.py`. Structured explanations now hold their grid column to the container (long URLs wrap). References render as their own block below figures; spaced "K -" is no longer an ion. Restructure pack for outside models: `docs/EXPLANATION_RESTRUCTURE.md` (word-for-word gate `tools/explanation_restructure.py`). All 73 restructure batches imported (1,321 restructured, 121 unchanged, 0 rejected).
- **Pharmacology (Second Prof, PrepLadder only).** `tools/build_prepladder_pharmacology_bank.py` on the shared pipeline; data `data/Prepladder/pharmacology/` (272 figures); IDs `pharmacology-<lesson>-<n>`; 16 PYQ lessons (650 Q); 4 five-option PYQs. All 1,321 keys match `pharmaprep11.pdf`; 6 source-missing explanations marked; 112 openings the PDF cut off: 74 first words restored ("ue to"→"Due to"), 38 lost labels noted. Restructure pack open: 66 batches, `restructure/pharmacology-all`. Pill icon, `--nkg-subj-pharmacology`, Second Prof. Ledger `docs/PREPLADDER_PHARMACOLOGY_2025-11.md`; tests `tools/test_prepladder_pharmacology_bank.py`, `tools/verify_prepladder_pharmacology_browser.py`. PYQ journey pin 76 topics · 2,993 Q; 6 subject cards.
- Two editions: Version X (1,042 Q, `import <master.jsonl> <images>`) plus the November 2025 edition (1,100 Q, 4 PDFs, `import-v2 <master.jsonl> <images>`). Rules `tools/prepladder_microbiology_edition.py`; per-question map `data/Prepladder/microbiology/source/edition_map.json`; ledger `docs/PREPLADDER_MICROBIOLOGY_EDITION_2025-11.md`. Matched questions keep Version X app IDs (progress carries over); 162 new are `microbiology-q<QID>`; 102 Version X-only kept, 2 exact repeats dropped; 13 answer-key changes carry review notes; options/key always from the new edition; 454 explanations from Version X (same text, or 33 blank in the new PDF). Figures 1,552 (`visuals/`, PLV2_ prefix for new). Tests `tools/test_prepladder_microbiology_bank.py`, `tools/verify_prepladder_microbiology_browser.py`. The app record is appended to `MARROW_DATA.records` with `bank:'PrepLadder'`, `explanationFormat:'structured'` (Marrow ordered-block renderer, `heading` block, `stemTables`). Second bank card beside Marrow; 6 PYQ topics (610 Q) join the PYQ journey. Detail packs are keyed `${bank}-${subject}`. Marrow Microbiology's 235 figures were border-trimmed with the same trimmer; ED8 registry images deliberately not (byte-identical contract).

## FSRS deep audit — three fixes, permanent suite, promoted — 2026-10-16

- Full-system FSRS audit (scheduler, host, persistence, sync, browser): `nkFsrsQueue` built an engine per sort comparison — now one engine + one retrievability value per card (346 ms → ~70 ms on a 2,984-due backlog, ordering unchanged); settings merge per field via `state.fsrsPreferencesAt` stamps (stamp-less payloads keep the whole-block merge); `nkFsrsRecordAttempt` heals a missing derived cache by replaying stored attempts. Permanent suite `tools/test_fsrs_audit_v1.py` (52 scenarios; `verify_local.py` 96 checks) plus real-clock browser rating-dock probes; ledger `docs/FSRS_AUDIT_2026-10-16.md` (F1–F5; dead legacy review paths and the final-review overlay footer rule recorded as non-changes). Product commit `056046a0`; main CI green (Engineering `38889903337`, PWA `38889903319`); promote `38919155135` published `https://5f78b822.nk-qbank.pages.dev` — live markers verified, the previous deployment lacked them. Physical-device checks remain open. **2026-10-17 correction:** F1's "seen today" narrowing to due cards broke the daily cap (cap 20 admitted 19 more after 20 reviews); PR #117 (`4063eca8`, promoted) restores the full scan, adds S4c (53 scenarios).

## Microbiology Marrow complete — part 07 integrated (726 questions / 25 topics / 6 sections) — 2026-10-16

- Branch `feature/microbiology-marrow`; resolve live HEAD from Git. All uploaded parts are integrated in `tools/build_microbiology_marrow_bank.py` (`PART_LAYOUT`, schema 2); split page offsets pinned by embedded page-image SHA-256 against the full 173-page Qbank (03→48, 04→74, 05→100, 06→126, 07→152). Built bank: **726 questions / 25 topics / 6 sections / 235 figures**, `incomplete={}`. Part 07's first module joins part-06's Mycology half (module 22 = Q1–35, combined title, true total 35); new topics: 23 General Parasitology & Helminthology (16), 24 Protozoology (39), 25 Applied & Clinical Microbiology (15). Parts 01–02 IDs unchanged; learner progress carries over. `source_parts()` still prints `MICROBIOLOGY_MARROW_PARTS_PENDING` for future un-integrated uploads.
- Error hunt over the earlier integration found and fixed real issues: (1) the systemic-bacteriology `plannedIndex` restarted mid-list — renumbered 01–10, synced topic `plannedSlots`, and `tools/test_marrow_topic_taxonomy.py` now locks the full chapter-to-slot map (`MICROBIOLOGY_SLOT_MAP`); (2) a display leak — `nkEmphasisHtml` runs after `nkScientificMarkup`, so an apostrophe-led bold (`'**Myeloma**` → `&#39;**Myeloma**`) hit an entity boundary the flanking rules did not know: `;` before and `&` after a marker run now count as punctuation, with one regression case per direction (source MB8721 / CH25 Q014); the emphasis test prints node stderr on failure instead of swallowing it.
- Figure audit both directions: 36 part-07 refs == 36 uploaded crops; 178 explanation figures + 57 stem figures = 235 files, zero orphans, zero misses. Quality flags are verbatim-preservation notes only; no learner-facing "Image Attribution" strings.
- Local gates green: bank/taxonomy/emphasis tests (726/25/235; 10,164 chunks), `verify_local.py` (95 checks), browser verifier `MICROBIOLOGY_BROWSER_OK topics=25 sections=6 questions=726 peer_stats=on part07=on`, probe `ALL_PROBE_CHECKS_OK`. Integration commit `72fe1a24`: Engineering Gate 38852775477 + PWA 38852765898 passed (first deploy of the 726-question bank).
- **Promoted to production 2026-10-16 (user-authorized)**: main's four SourcePDF upload commits merged into the branch, then `main` fast-forwarded to `ebd1c947`; branch CI green at that SHA (Engineering Gate `38857895703`, PWA `38857901413`). Promote dispatch `38859432309` (`build_apk=false`, `promote_production=true`, exact `release_sha`) asserted the Pages production branch `main` and published deployment `d06483c9`, verified live: `PREVIEW_CHECK_OK url=https://d06483c9.nk-qbank.pages.dev/ motion=spring bank=726 topics=25 sections=6 tiles=on pill=on strip=on questions=on`. Canonical root `https://nk-qbank.pages.dev` sits behind the owner's Cloudflare Access (email PIN / Google, owner only; `*.nk-qbank.pages.dev` previews are not covered) and serves the latest production deployment. Verify production via the promoted deployment URL or the owner's session; `main.nk-qbank.pages.dev` is a legacy alias frozen at the pre-branch single-file build and is not production. Physical-device checks remain open; the branch is merged and promoted. Follow-up Home polish promoted the same day: the UWorld entry chevron now sits on the card's right edge (3-column grid override where the Geist declutter rules hide the entry's Open action; locked by the Home contract and the UWorld verifier's flush-right assertion), deployment `4e8fe836`, live checks `PREVIEW_CHECK_OK` + `LIVE_UWORLD_OK chevron_gap=1px`.

## Microbiology Marrow subject — architecture (parts 01–02 landed 2026-10-14; history in SESSION_LOG)

- Marrow is a fourth My Subjects entry with one bank (no PrepLadder); `marrow_bank_data.app_marrow_records()` appends it after the canonical ED8 three so every 2,711-question ED8 gate is unchanged, and it runs on the same Practice/CBT/Review/FSRS/modules engines. `tools/build_microbiology_marrow_bank.py` normalizes to `marrow-bank-1.0` (hash-pinned shards `data/marrow/microbiology_marrow_qbank*`); explanations are ordered blocks rendered by `nkRenderMarrowOrdered`; figures merge into `MARROW_VISUALS` without touching the ED8 image registry; peer statistics use `nkSourceCohort`/`nkSourcePollPercent`. Display hygiene only (extractor annotations, bracketed clipped-word completions, one source-checked typo MA1527).

## Production, IndexedDB progress and faster CI — 2026-10-12

- Branch `feature/home-v12-redesign`: progress lives in IndexedDB (`app/src/main/assets/nk-store.js`, loaded before every other script). Heavy `qbank_state_*`/backup keys are served from memory, committed per task in one IndexedDB transaction, and the primary is also written synchronously to localStorage so an instant reload never loses a save. First run migrates localStorage; restore points (30 min / daily / before reset, restore, migration) are listed under More > Restore points. Checked by `tools/verify_progress_store_browser.py`.
- CI: `tools/run_browser_suite.py` runs all browser verifiers four at a time in one step (Marrow wrapper's eight scripts and four UWorld widths are separate entries); UWorld exhibit crops are cached on their inputs (browser-case helpers excluded from the key). Full green run ≈16 min (was 25–35). Geist is the only UI (the `?ui=legacy` switch is retired) and every verifier tests it. Legacy markup/CSS remain as Geist's base. `tools/prune_unreachable_css.py` (run by `build_web_dist.py`) drops CSS whose required classes/ids appear in no markup, script or data of the build (~110 KB: ~56 KB legacy inline, ~52 KB pruned from `redesign/` sources). Legacy rules Geist overrides were then removed (see Bake).
- Bake: `app/src/main/assets/index.html` is source (≈180 KB: markup and scripts, no data, no module copies, no CSS). The 62 build-time patch scripts are retired (read them with `git show eb84d7f6:tools/<name>.py`); `MainActivity.java` and `source_visual_renderer.js` hold their generated form. Script features live in `app/src/main/modules/*.js` and sit in the page as `/* @module <file> */` markers; tests read the page via `tools/app_page.py`. Data sits at `__NK_DATA_<NAME>__` tokens, filled by `tools/build_app_data.py` (output byte-identical to the old 19 MB page). All CSS is one stylesheet, `app/src/main/assets/app.css` (old Geist files first, then the former inline blocks in cascade order, each headed `/* ── <name> ── */`); declarations that always lost to a Geist rule were removed, checked by a computed-style comparison over ~380 verifier screenshots (light/dark, phone/tablet): no real differences. Do not reintroduce page-patching steps; add CSS to `app.css` under a new section header.
- Open app findings (not yet fixed): gold wrong-option label uses `esc(o.text)`, not `nkScientificMarkup`; `startAllSubjectPractice` has no button; `nkInsightsExpanded`/`nkToggleInsightsExpanded` unused; the Insights focus and coverage sections are no longer shown since learning_insights replaced `analytics()`. Restoring or removing them needs the user's call.

## Notes, PDF loader and shared viewer — 2026-10-10

- Main has question notes with images/PDF pages (#103: My notes bar, block note page, IndexedDB + chunked `noteAssets` sync, Android file chooser). Branch `ccr-47681b8d-1aikn7` adds the PDF loader/glyph repair work from `feature/home-pdf-loader` and one shared viewer (`redesign/nk-viewer.js`) for Geist source PDFs and note images: opens at once from the on-screen canvas, swaps in a cached sharp render, firm edge-to-edge panning. Details: `docs/PDF_RENDERING.md`, `docs/QUESTION_NOTES.md`.

## Previous certified production reference — 2026-10-04

- Production product `315cfcccc2a0d830aa851fbd136f3e8d14e215e8` / merged PR98 (user-authorized promotion): accepted interaction/visual/revision chain, three UWorld collections, app-wide audit repairs; all 103 local checks, Engineering `37191000202`, full run `37191000207` and release `37192960486` pass; canonical-root HTML SHA-256 `086b04f41fcf610af844b76652b7c6368392dc26d9bd8f609b258b2a6e77897b` matches `https://92774e98.nk-qbank.pages.dev`. Ophthalmology (30 q / 204 pages / 8 native tables / 77 source figure placements from source PDF `56fe817…`) and the 283-asset UWorld inventory are source/flow reviewed; audit repairs: account Back/email/contrast, Topics focus, empty FSRS actions, completed-start migration/file/private-asset boundaries, hosted frame/MIME/referrer policy. Build-verified/hosted-verified only — not physical-device or clinical acceptance; use the canonical root (older `main.` alias stale). Reports: `docs/PREPRODUCTION_AUDIT_2026-10-04.md`, `docs/UWORLD_OPHTHALMOLOGY_COLLECTION.md`.

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
