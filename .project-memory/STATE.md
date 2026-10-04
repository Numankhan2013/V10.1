# STATE.md — Current Project State and Handoff

> Operational state only. Resolve the live branch/commit and CI from Git before acting. Historical detail belongs in `SESSION_LOG.md` and dedicated handoffs.

## UWorld PDF-only Ophthalmology batch — 2026-10-04

- Active `feature/home-uworld-ophthalmology-20261004`, based on certified quality product67a85ee3 / docs handoff676c1b5e. User authorizes reuse of existing JSONLs/PDFs and selects Ophthalmology as the first PDF-only extraction. Only this30-question block is in this batch; other supplied packages remain queued. No production promotion is authorized.
- Original204-page/45,046,309-byte PDF at source56fe817 is pinned to SHA-256ab4aadac54fbc78c9db9fca4b561cb5d0ee0ba4ade3f72066c72bf64021843dc. Three user-authorized Luna/high source batches extract/review every page, preserving original keys, prose, percentages, objectives, tables and exhibits. Extracted rows keep original per-page OCR/provenance; source image review is required even without a supplied JSONL.
- Existing UWorld registry, typed presenter, media/package pipeline and shared study engines are reused. Full stem text remains searchable while ordered display blocks retain inline exhibit placement. Source extraction, local/browser/full CI and hosted proof are in progress; no Ophthalmology build/device/content acceptance is claimed yet. See `docs/UWORLD_OPHTHALMOLOGY_COLLECTION.md` when written.

## Certified UWorld and app-wide quality pass

- Product67a85ee3 / ready PR96 stacks on95; docs handoff676c1b5e preserves the exact artifact. Bounded78-screen Impeccable audit repairs collection footers, false block groups, singular/back labels, reference Search/batch counts, incompatible bank filters, modal disclosure focus and small builder targets; source/study engines and accepted appearance remain protected.
-102 local checks, Engineering37184200975/37184199171 and full37184199118 including Android phone/tablet emulators pass. Hosted390/820/1194/1440px UWorld and phone/tablet Search/focus pass at https://adf558ca.nk-qbank.pages.dev (HTML SHA-2568d63e6f945826062ca4a422978093b1c693fdde8b29d62478fc65f454c3d2ce9); all206 offline paths/media hashes unchanged. Initial37183638634 cancelled before delivery. Production unchanged; details/limits `docs/UWORLD_APP_QUALITY_2026-10-04.md`.

## Certified UWorld second collection

- Product795d94a9 / ready PR95 stacks on Biochemistry product424e0ca8/PR94; docs handoffb9b6f581. User accepts Biochemistry functionality, architecture, percentages/objectives; explanation aesthetics remain deferred. Poisoning33 questions/166pages and original source56fe817 are reviewed by three Luna/high batches with29 native tables/22 figures; graph D/E percentages remain null. Full independent context is preserved for linked2088/2089; existing free navigation remains.102 checks, Engineering37165147978/37165168319 and full37165147973 including Android emulators pass. Hosted four-width flows at https://1b80a731.nk-qbank.pages.dev (HTML SHA-2568df4bac9be93d1db712bc28e991caab936c9372f20df31296d98a3d44e97f9d9),206 offline paths and unchanged184 Biochemistry images pass. No new physical/clinical acceptance; `docs/UWORLD_SECOND_COLLECTION.md` owns source limits and architecture.

## Certified Biochemistry reference

- Product424e0ca80e57fc946ad96f41d38547bcbc23d089 / PR94 stacks on93 and passes full37158603961 plus both Engineering gates and101 local checks. Actual hosted four-width flows,184 offline assets and crawler headers pass at https://2f165b3a.nk-qbank.pages.dev; HTML SHA-2569bc847becbabe6eb1cf9da681deaa808da1bc4bd1bb58762ab71a6fd48022c02. Details/source limitations: `docs/UWORLD_BIOCHEMISTRY_PILOT.md`.
-132 reviewed records/729pages;131 scored questions;1244 unscored because its essential exhibit is absent. Objectives1486/1071/107111 and figure sections1369/1244 are source-clipped. Missing stats stay null; accepted17px/70ch source-native layout, objective-after-explanation and immediate option percentages remain.
- Practice mistakes only tracks unresolved ordinary Practice/test misses; FSRS-only lapses affect scheduling without creating or resurrecting ordinary mistakes. Correct answers from any flow resolve an ordinary miss. Continuous Revision/Pause/Finish remains accepted. No new installed-Android, haptic or clinical certification is claimed.

## Production promotion recovery — 2026-10-03

- User authorized fixing and rerunning the latest failed production candidate on `main`. Product `d9885087e0a7f8e241d2f064a124dae0ca591110` passed the main build/browser/PWA/APK checks in run `36977682274`; its Android tablet driver disconnected during source-PDF locator screenshot capture. Production was skipped in that original run; the recovery release below is now live.
- Native Android viewport capture replaces the oversized source-PDF locator screenshot, preserving image readiness, contrast and visibility assertions. All88 local checks, Engineering run `37088358732` and full main run `37088358628` passed at `d1735d2129f9f53bccda036c08bce367d2de7542`, including phone/tablet emulators. The automatic deployment did not start; this release branch pins that exact successful artifact and checks production bytes after upload. Production run `37090193916` succeeded; canonical https://nk-qbank.pages.dev and its immutable deployment serve exact verified HTML/config/service-worker bytes. HTML SHA-256: `3fce9f7c07bf9c4721b1e58aa168bab76b0db8641cd9b2d908c46cbfe729fea9`. No physical-device acceptance is claimed.

## Impeccable interaction quality — 2026-10-03

- Impeccable4.5.0 is installed for Codex in `.agents/skills/impeccable`; `DESIGN.md` preserves accepted warm paper/violet/amber, coherent two-tone icons, immediate in-place answering and restrained feedback. Certified interaction/visual/study/return-flow PR89–92 stack on88; their full builds and hosted checks pass. User accepts the subtle aesthetics. Preserve existing haptics, reduced motion, fixed footer, storage, FSRS, navigation and question logic.
- Latest prior return-flow productaced8f38/full37109357853 passed93 checks and actual hosted390/820px flows at https://4e97ea33.nk-qbank.pages.dev. Source reports: `docs/INTERACTION_QUALITY_2026-10-03.md`, `docs/VISUAL_REFINEMENT_2026-10-03.md`, `docs/STUDY_FLOW_REFINEMENT_2026-10-03.md`, `docs/RETURN_FLOW_REFINEMENT_2026-10-03.md`. Production unchanged; physical-device/haptic acceptance is separate.

## Analysis clarity and verified PWA updates — 2026-10-03

- Certified productc4f590b / PR88 passes90 local checks, both Engineering gates and full37093986785 including Android phone/tablet; hosted390/820px checks pass at https://ee2927a6.nk-qbank.pages.dev. Preserve fixed Correct/Incorrect/Unattempted colors/counts, recorded-only timing coverage, high-contrast Review Solutions and Insights-only revision-prompt removal. Test Analysis retains practice on its missed IDs.
- PWA prompts require a waiting worker with a verified different build; matching builds and inactivity stay quiet. Later persists for the tab and active study defers the notice; only an explicit click reloads. See `docs/INTERACTION_QUALITY_2026-10-03.md` for the subsequent interaction pass. Full historical evidence remains in SESSION_LOG; production unchanged and no physical acceptance claimed.

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

## BC3 and BC4 canonical interaction hardening

- BC3 and BC4 were reconciled into canonical through `43328c1`. Canonical Engineering `35818707731` and full Android/PWA `35818707723` passed, including packaged Android 35 emulator phone/tablet and generated browser checks. Full history: `docs/BC4_QUESTION_INTERACTION_DEFECT_LEDGER_2026-09-22.md` and `SESSION_LOG.md`. Physical Android verification remains pending.
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
- Production promotion requires explicit authorization; the user authorized this Insights/clarity release after verification.
## Current priorities / Next step
1. Completed final completeness pass source-reviewed 254 unique questions (226 initial + 28 supplemental): 89 repairs (74 contextual/15 exact; 81 text/table/notation/key and eight native images), 132 already complete, 33 underdetermined source omissions gated, including ANAT62Q6. Compiled display ledger: 114 entries; source tests pass across four variants. CI queue requires all new structural/glyph/question-visual candidates reviewed (195 current residual candidates; zero unreviewed). See `docs/QUESTION_COMPLETENESS_FINAL_PASS.md` and the pinned `data/question_completeness_reviews_v1.json` ledger. Raw imports remain immutable.
2. Regenerated final image coverage: 1,502 references / 1,421 released / 79 invalid / two archival holds / zero unresolved cues; runtime 1,486 bindings / 1,306 assets / 1,128 owners. All 52 final local checks pass. Product checkpoint `de9c415cef4915d5b20a42abc9f2299a8595b173` is fully build-verified: Engineering `36732893469` and full browser/PWA/APK/package/Android-emulator run `36732893814` passed. Preview: `https://74f04894.nk-qbank.pages.dev`. All 114 contracts passed 228 runtime checks; eight recovered image URLs match exact native hashes in the live preview. Earlier image/browser assertion failures are resolved.
3. Production recovery is live; analysis/interaction/visual-icon candidates are fully certified and ready in PR88/89/90. No new production promotion is authorized. Preserve23 source gates, two archival image gaps and PrepLadder source-comparison backlog.
## Memory pointers
- PrepLadder visual verification handoff: `.project-memory/PREPLADDER_VISUAL_VERIFICATION_2026-09-16.md`.
- Matching/structured presentation handoff: `.project-memory/MATCHING_TABLE_ARCHITECTURE_HANDOFF_2026-09-14.md`.
- Practice postmortem: `.project-memory/PRACTICE_FLOW_POSTMORTEM_2026-09-12.md`.
- Canonical source consolidation: `.project-memory/FULL_CORPUS_CONSOLIDATION.md`.
- Automation policy: `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md`.
