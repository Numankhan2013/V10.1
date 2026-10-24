# STATE.md — Current Project State and Handoff

> Operational state only. Resolve the live branch/commit and CI from Git before acting. Historical detail belongs in `SESSION_LOG.md` and dedicated handoffs.

## v12 integration — `integration/v12` — 2026-10-23 (read this first)

- **Production is still `main` `9936b0e0`** (PR #140, docs on top of `c8cf5b65`): Biochemistry 2025 was rolled back 2026-10-20 (main force-reset; promote run `39422618974`). Nothing on `integration/v12` is promoted; **promotion needs the owner's explicit approval** (they were angry that Biochemistry went live with unstructured explanations).
- `integration/v12` = `feature/firstprof-restructure-preview` (Biochemistry + Physiology 2025 editions with all restructure batches imported; CI green at `12b4f2e3`) + `bug-hunt/2026-10-19` (secondary agents' 30 fixes; its own CI was red) + Anatomy 2025. Merge conflicts: Android shell keeps Cloudflare login hosts and gains the app-origin bridge guard; data build validates batches on the canonical Biochemistry source; all PrepLadder banks rebuilt.
- Bugs the bug hunt left: its verifiers never followed its own withdrawals (Marrow Anatomy 1114, Biochemistry 581, Microbiology 725; card 1,927; refinement wave skips withdrawn IDs). Its Key-takeaway module fix restated the keyed (false) choice of negative stems ("Choose the incorrect statement…", marrow__MICRO_CH07_Q010) as the takeaway: `nkSourceTakeaway` no longer falls back to the answer, nor uses table takeaways, when the stem says except/not/false/incorrect/untrue/wrong/least (regression in `tools/test_question_content_hygiene_v1.py`). Notes-search fixture used "no match", which the word-wise search correctly matches in the question text.
- **Anatomy 2025 (PrepLadder):** `anatprep11.pdf` read by `tools/prepladder_prep11_pdf.py --glyphs anatomy` (`tools/prepladder_anatomy_glyphs.py`, ALIGN; 0 lost characters, all 1,102 keys agree with the Gemini master), built by `tools/build_prepladder_anatomy_bank.py` (EditionBank): 1,134 Q / 54 lessons / 10 regions (PDF order), 14 PYQ lessons (475 Q), 1,490 figures. 1,036 earlier `anatomy-<ch>-<n>` IDs continue, 66 new `anatomy-q<QID>`, 32 dropped-by-2025 kept + 5 with unusable 2025 explanations kept (37 earlier). 15 key changes audited: 13 genuine corrections, 2 PDF errors fixed by `key_fixes` (15-52 Thyroid, 45-16 Spleen); 2025 Q848227 (choices printed only as figure labels a-d) is linked to its earlier ID `anatomy-22-4` and its key reviewed; unlinked it shipped twice, once with blank choices. Tests `tools/test_prepladder_anatomy_bank.py`, `tools/verify_prepladder_anatomy_browser.py`; PDF loop in the Marrow core verifier now opens earlier `anatomy-29-7`; PYQ journey 102 topics · 3,293 Q.
- **Anatomy explanations are not restructured yet** (as fragmented as Biochemistry was): 55 batches `data/Prepladder/anatomy/restructure/batches/anatomy-001…055` (1,097 Q); lead prompt `docs/EXPLANATION_RESTRUCTURE_FIRSTPROF.md` (BANK=anatomy, LAST=055, base `integration/v12`, results to `restructure/anatomy-all`). Then import, rebuild, test, and only then ask the owner to promote. Until then a push to `main` ships Anatomy with PDF explanations and holds back questions without a matching old PDF explanation (DECISIONS 2026-10-24).
- Local runs need the CI-only UWorld exhibit cache and `QBANK_ANATOMY_PDF_URL`; without them `verify_uworld_biochemistry_browser.py` (diagram images) and the Marrow v2 PDF check fail locally only.

## Six-area bug hunt (secondary agents) — 2026-10-22


- Branch `bug-hunt/2026-10-19` (off `main` at `25fa6b66`); resolve live HEAD from Git. Six agents each owned one app area and the lead reviewed every proposed fix: 31 findings, 30 approved and applied, 1 withdrawn as a false positive. Every finding, its evidence and its verdict live in `.project-memory/bug-hunt/`, one file per finding with a `Main-agent review` block. The largest win: the page carried a stale inline copy of `nkSourceTakeaway` that shadowed the maintained module, so 2,354 of the 10,105 shipped questions had a wrong "Key takeaway" and 1,940 had none; fixed, with a parity guard that stops a module and the page declaring the same function.
- Also fixed, each with a regression that fails when the fix is reverted: durable-save rollback, progress-store pruning/usage/freeze/announce, Practice start corrupting a timed test, FSRS undo ignoring a pending rating, a failed resume leaving an invalid session, pending ratings lost when a tab is hidden, the source-visual viewer missing a cached image, ordered tables printing `[object Object]`, UWorld option percentages throwing, four whole-phrase search filters, the Home subject card picking a bank, a bankless topic chapter using stale data, the Android manifest allowing backup, arbitrary URI schemes in the WebView, service-worker ranges dropping security headers, the native bridge reachable from the Access login, `confirm()`/`prompt()` swallowed, the web build not checking its generated assets, the data build overwriting the source page, and the flat explanation diverging from the blocks the learner sees (2,668 questions; 357 takeaways changed).
- Figure-less Marrow questions are resolved at the shipping boundary. The 13 Microbiology IDs were a false positive of the builder cue — "Tumbling motility is shown by ___" is ordinary wording, not visual deixis — and still ship; the cue now requires a real image reference and `PENDING_QUESTION_FIGURES` is empty. `marrow__ANAT_CH45_Q004` (only an unreleased unmarked candidate), `marrow__BIOCHEM_CH17_Q014` (source has no teeth image) and `marrow__MICRO_CH18_Q013` (stem cites a chest X-ray that was never extracted) are withheld through `data/marrow/withdrawn_questions_v1.json` and `tools/marrow_bank_data.py`: the canonical shards keep the records, the app omits the 3 questions and recomputes topic counts, so it ships 3,434 Marrow questions. `marrow__PHYSIO_CH35_Q020`'s bar chart was already released but bound as explanation; it is now the question figure. Regression `tools/test_marrow_withdrawn_questions_v1.py`; `tools/build_microbiology_marrow_bank.py --check` passes. Verification: 13 new test files assert the fixed behaviour against the shipped code, and the Python suite is green except the ten UWorld tests that need `data/uworld/`, absent from this sparse checkout. The Android shell and the CI pipeline changes need a passing GitHub Actions run and a device check before they are called verified.

## v1.0.0 production and pause model — 2026-10-19

- **What is live:** `main` at merge `c8cf5b65` (PR #139: Second Prof PrepLadder study-index order + faint section labels; Android shell Drop-Q adaptive icon and `cloudflare.com` login hosts kept in-WebView). Promote run `39378028215` → `https://d7b0ca0e.nk-qbank.pages.dev`; live `verify_uworld_biochemistry_browser.py --url` and Pathology index labels passed at 390 px. Android: Google sign-in cannot run in a WebView, so the owner installs the PWA from Chrome (WebAPK) instead of the shell APK. v1.0.0 is `03e8d9b7` (PR #137; tag from GitHub Releases, the session proxy refuses tag pushes).
- **Released checks:** full build 1746 + Engineering Gate 1267 green on the head; `verify_local.py` 100 checks; click crawl of 41 pages and all session screens (light/dark, 390/820/1194) clean; text scan of all 13,073 rendered questions clean of visible leaks.
- **Pause model:** the owner makes the repo private (copyrighted source). The running app does not depend on GitHub: Cloudflare Pages (wrangler direct upload) + Cloudflare Access, Firebase progress sync (`cross_device_sync.js`), PDFs on R2. No scheduled workflows, 0 forks, so a paused private repo spends no Actions minutes. Free-plan private repos may drop branch protection — re-check rules on resume. CI pulls PDFs with LFS: private LFS bandwidth and Actions quotas apply once building resumes.
- **To resume:** read `AGENTS.md` + this file; branch from `main`; build locally (`tools/verify_local.py`); CI = `engineering-gate.yml` on PRs, `build-apk.yml` dispatched on the branch (`build_apk=false`, `promote_production=false`); promote by dispatching `build-apk.yml` on `main` with `promote_production=true`, `release_sha=<merge sha>`; verify the deployment URL at 390 px (send a browser user agent).
- **Known open items (content, not breakage):** a few rare OCR words remain in UWorld auto collections (e.g. "comfection") — extend `WORDS` in `fix_ocr_text.py`; figure labels leak into some UWorld explanation paragraphs; PrepLadder 422-entry audit backlog and 34 flattened matching tables (task #42); Biostatistics review; physical-device check of v1.0.0 on the owner's phone; stale merged branches were left in place (not deleted).

## UWorld Microbiology / Dermatology / Immunology / Ethics / ENT imported and promoted — 2026-10-19

- Five auto-extracted collections registered in `tools/uworld_collections.py`: Microbiology 300 Q (298 verified), Dermatology 100, Immunology 109, Ethics, Legal & Professional 116 (115), ENT 40 = 665 Q / 662 verified. No question ID collides across the bank (`bank_records()` fails closed otherwise).
- The PDF text layer garbles the white-on-blue header ("1163" for 11637, "15a407"), which split questions and collided IDs. `tools/uworld_auto/header_id.py` reads the digits from the screenshot against `header_digits.npz` templates; OCR is only the fallback (Ethics/ENT headers read cleanly by OCR). Grouping trusts image-read IDs (`Stub.seen`).
- Flagged (108) and unassembled (40) questions were transcribed by outside agents from `uworld-review` batches (`data/uworld/review/`, checker `tools/uworld_auto/review/check_review.py`; branch names are `uworld-review-<range>`, a slash would clash with the base branch) and applied with `apply_reviews.py --careful` / `rescue.py adopt`. Reviewers fixed wrong answer keys and choice counts; 11 packets cannot be read from the screenshots and stay unowned (Microbiology 16 pages, Immunology 5, Ethics 2, Dermatology 1).
- Figures upscaled with `upscale_figures.py` (line art only). Details: `docs/UWORLD_AUTO_PIPELINE.md`.
- PR #133 merged as `8b50a490` (CI green on the PR and on main); promoted by run `39237606258` (`build-apk.yml`, `promote_production=true`, `release_sha=8b50a490`) to `https://e52dc0b2.nk-qbank.pages.dev`; `verify_uworld_biochemistry_browser.py --url` passed live at 390 px (the hosted site 403s Python's default user agent: send a browser one).

## PrepLadder text banks — Microbiology (1,202 Q / 42), Pathology (1,459 Q / 90), Pharmacology (1,321 Q / 59) — 2026-10-17
- **Study index (2026-10-20).** Second Prof PrepLadder lessons follow the owner's study index: `index=` on `TextBank` (Pathology 22 sections, Pharmacology 13) and `INDEX` in the Microbiology builder (6). Order and section only; lesson/question ids unchanged. Topic page shows each section as a faint 12 px label on a hairline (`.nk-topic-group.is-index`). First Prof untouched.

- **Pathology (new Second Prof subject, PrepLadder only).** `tools/build_prepladder_pathology_bank.py import <master.jsonl> <images>` (shared pipeline `tools/prepladder_text_bank.py`, Microbiology's text/block rules); data `data/Prepladder/pathology/` (1,676 figures, 1,127 border-trimmed); IDs `pathology-<lesson>-<n>`; 27 PYQ lessons (615 Q). Checked against `pathoprep11.pdf`: all 1,450 printed keys match; 14 explanations the PDF itself omits show a plain note + review note; 9 image-only option sets (blank PDF key) stay `needs_review`. Identity: microscope icon, `--nkg-subj-pathology`, `NK_PROF_GROUP_BY_SUBJECT` Second Prof. Ledger `docs/PREPLADDER_PATHOLOGY_2025-11.md`; tests `tools/test_prepladder_pathology_bank.py`, `tools/verify_prepladder_pathology_browser.py`. Structured explanations now hold their grid column to the container (long URLs wrap). References render as their own block below figures; spaced "K -" is no longer an ion. Restructure pack for outside models: `docs/EXPLANATION_RESTRUCTURE.md` (word-for-word gate `tools/explanation_restructure.py`). All 73 restructure batches imported (1,321 restructured, 121 unchanged, 0 rejected).
- **Pharmacology (Second Prof, PrepLadder only).** `tools/build_prepladder_pharmacology_bank.py` on the shared pipeline; data `data/Prepladder/pharmacology/` (272 figures); IDs `pharmacology-<lesson>-<n>`; 16 PYQ lessons (650 Q); 4 five-option PYQs. All 1,321 keys match `pharmaprep11.pdf`; 6 source-missing explanations marked; 112 openings the PDF cut off: 74 first words restored ("ue to"→"Due to"), 38 lost openings written by hand (`openings.json`, applied after restructures). Restructured: 1,155 of 1,315 explanations (66 batches by in-session agents; 422 tables), 160 left as they read well. Promoted `acc898ab` (with the Pathology restructure and matching-options fix): run `39094944533`, `https://300c7f4e.nk-qbank.pages.dev`, verified live. Pill icon, `--nkg-subj-pharmacology`, Second Prof. Ledger `docs/PREPLADDER_PHARMACOLOGY_2025-11.md`; tests `tools/test_prepladder_pharmacology_bank.py`, `tools/verify_prepladder_pharmacology_browser.py`. 6 subject cards (PYQ journey pin is now 87 topics · 3,139 Q with Biochemistry).
- **Biochemistry 2025 (First Prof, 2026-10-20, branch `feature/prepladder-biochemistry-11`).** `biochemprep11.pdf` (821 Q / 39 lessons) read from the PDF by `tools/prepladder_prep11_pdf.py` (generic prep11 reader; ZapfDingbats glyphs restored by `tools/prepladder_<subject>_glyphs.py`; Gemini `master.jsonl` only supplies lesson titles/sections and must agree on QID+key) and built by `tools/build_prepladder_biochemistry_bank.py` (867 Q: 672 continue an earlier `qbank_data.js` id via `source/edition_map.json`, 149 new `biochemistry-q<QID>`, 46 earlier-only kept unchanged with PDF-page explanations; 1 exact duplicate dropped). Old qbank_data.js stays as fallback; id-keyed overrides skip structured PrepLadder questions (`nkQuestionPageBank`). 15 stem tables in `stem_tables.json`, 3 `openings.json`. Index = owner's 9 PrepLadder app sections (Introduction … Vitamins); the PDF combines some app topics into one lesson (e.g. "Fructose and Galactose Metabolism, HMP Pathway"), so lessons are not split. Mixed PYQ sets 21/35/39 sit in "Free Radicals, Antioxidants, Trace Elements and Miscellaneous". 21-29/21-58/27-5 kept earlier (2025 explanation unusable); 11-33 key fixed to A. Physiology/Anatomy next with the same reader. Follow-up: "(Option C):** . However" stray punctuation also in Pathology (98)/Pharmacology (68), fixed only for Biochemistry.
- Two editions: Version X (1,042 Q, `import <master.jsonl> <images>`) plus the November 2025 edition (1,100 Q, 4 PDFs, `import-v2 <master.jsonl> <images>`). Rules `tools/prepladder_microbiology_edition.py`; per-question map `data/Prepladder/microbiology/source/edition_map.json`; ledger `docs/PREPLADDER_MICROBIOLOGY_EDITION_2025-11.md`. Matched questions keep Version X app IDs (progress carries over); 162 new are `microbiology-q<QID>`; 102 Version X-only kept, 2 exact repeats dropped; 13 answer-key changes carry review notes; options/key always from the new edition; 454 explanations from Version X (same text, or 33 blank in the new PDF). Figures 1,552 (`visuals/`, PLV2_ prefix for new). Tests `tools/test_prepladder_microbiology_bank.py`, `tools/verify_prepladder_microbiology_browser.py`. The app record is appended to `MARROW_DATA.records` with `bank:'PrepLadder'`, `explanationFormat:'structured'` (Marrow ordered-block renderer, `heading` block, `stemTables`). Second bank card beside Marrow; 6 PYQ topics (610 Q) join the PYQ journey. Detail packs are keyed `${bank}-${subject}`. Marrow Microbiology's 235 figures were border-trimmed with the same trimmer; ED8 registry images deliberately not (byte-identical contract).

## Microbiology Marrow subject — architecture (parts 01–02 landed 2026-10-14; history in SESSION_LOG)

- Marrow is a fourth My Subjects entry with one bank (no PrepLadder); `marrow_bank_data.app_marrow_records()` appends it after the canonical ED8 three so every 2,711-question ED8 gate is unchanged, and it runs on the same Practice/CBT/Review/FSRS/modules engines. `tools/build_microbiology_marrow_bank.py` normalizes to `marrow-bank-1.0` (hash-pinned shards `data/marrow/microbiology_marrow_qbank*`); explanations are ordered blocks rendered by `nkRenderMarrowOrdered`; figures merge into `MARROW_VISUALS` without touching the ED8 image registry; peer statistics use `nkSourceCohort`/`nkSourcePollPercent`. Display hygiene only (extractor annotations, bracketed clipped-word completions, one source-checked typo MA1527).

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
- Structured PrepLadder banks render shard `stemTables`, not those overrides: fix lost tables in `data/Prepladder/<bank>/stem_tables.json` (DECISIONS "Printed stem tables are data").

## Learner-content hygiene

- Whole-corpus serialized JSON/code sanitizer candidate `45f6539fff535fadc6aaa6970894f9ff123422fa` passed Engineering `34738522874` and full run `34738530102` over **2,711 questions / 27,898 learner-facing fields**; raw ED8 source is unchanged.
- User preview review found residual OCR debris in Physiology Ch5/Ch7; verified follow-up `55d7ac8a89c2bbf6a01db5d305b8c975c344c1f3` added source-fingerprinted stable-ID display overrides for those two chapters. Engineering `34740460617` and full run `34740465004` passed; production skipped.
- Physiology Ch6 Q1–34 and Ch9–12 source text cleanup is verified at `232f0182`: Engineering `36665702451` and full browser/PWA/APK/Android run `36665702481` passed. A fresh canonical preview fetch matched all186 reviewed stems/options across Ch5–7 and Ch9–12. Browser expectations use shared scientific markup (e.g. Cl−). Raw ED8 and answer indices remain unchanged; other chapters/explanations are unreviewed.

## Explanation lane

- Released explanation checkpoint: **2,688 enhanced / 23 deferred / 2,711 total** at product `9d318f79d73d6f22a3c6f508e10f1fb243aea349`. Engineering `36870646707` and full Android/PWA/browser/APK/phone-tablet-emulator run `36870646652` passed. Preview `https://ac2f50ca.nk-qbank.pages.dev`; now included in the approved combined production release above.
- The parallel Luna continuation completed all 1,935 actionable explanations (914 Anatomy, 263 Biochemistry, 758 Physiology) in 178 bounded batches; queue/wave manifests and worker audits preserve all 753 prior augmentations, immutable source banks and existing answer gates. The first combined run `36841656565` failed before deployment because scientific H+ formatting broke emphasis matching; the released fix formats text and anchors identically, and a new actual-renderer regression covers that item, HTML escaping and all 2,546 authored display-text configurations early in both workflows (all 56 local checks pass). Browser verification passed 3,870 exact runtime-config checks and 562 rendered cases on phone/tablet, and the live preview's 2,688-entry map exactly matches approved content. Live HTML SHA-256: `bdc7702f8b9b6dc68b3ae1fbd6d7cd963baf6f2b274360c2b9eb158a3751c4f2`.
- Ten explanation table owners recovered during this continuation use source-PDF/page/hash-pinned display tables. Orphan table objects are allowed only for existing source table-block IDs and original explanation pages; browser QA checks headers/cells. Headers aliases remain supported without source mutation.
- All 23 incomplete-source Marrow questions remain deferred with existing gates. Three enhanced items retain explicit source caveats: Biochemistry Ch17 Q22 absent labs, Ch26 Q15 capping ambiguity, Physiology Ch32 Q28 dietary-fiber wording. Physical blanket acceptance remains unclaimed. Resolve live Git HEAD separately from the verified product SHA above; any later docs-only certification commit does not change the product.

## Image lane

- Source-visual owner resolution, fullscreen/zoom, multi-panel and phone/tablet browser/package checks are build-verified at `2340bd2` / full `35053564213`. PrepLadder technical validation does not replace its 422-item manual source-comparison audit (`.project-memory/PREPLADDER_VISUAL_VERIFICATION_2026-09-16.md`).
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
- Earlier OCR counts (seven question records and 56 explanation records) predate the final completeness pass below; question-essential uncertainty was included in the focused review, and the remaining explanation-wide cleanup is separate and must use pinned source evidence. Four PrepLadder source records remain intentionally non-answerable rather than recording corrupt attempts: `anatomy-22-4`, `physiology-23-38`, `physiology-24-6`, `physiology-33-33`.
- The user explicitly authorized the audited UWorld/app release; production is live after full verification. Future unrelated promotions still require authorization.
## Current priorities / Next step
3. v12 integration: see the section at the top (Anatomy restructure, CI green, owner approval before promotion). Earlier: Certified web-first product31bff68 is live on main and the canonical domain, including both reproductive collections and complete Biostatistics Block1. Next: source-review the remaining81 complete Biostatistics items in bounded batches. Preserve23 source gates, two archival image gaps, the PrepLadder audit backlog and shared study engines; APK work is on demand.
## Memory pointers
- PrepLadder visual verification handoff: `.project-memory/PREPLADDER_VISUAL_VERIFICATION_2026-09-16.md`.
- Matching/structured presentation handoff: `.project-memory/MATCHING_TABLE_ARCHITECTURE_HANDOFF_2026-09-14.md`.
- Practice postmortem: `.project-memory/PRACTICE_FLOW_POSTMORTEM_2026-09-12.md`.
- Canonical source consolidation: `.project-memory/FULL_CORPUS_CONSOLIDATION.md`.
- Automation policy: `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md`.
- Notes/PDF loader and shared viewer: `docs/PDF_RENDERING.md`, `docs/QUESTION_NOTES.md`.
