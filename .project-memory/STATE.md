# STATE.md — Current Project State and Handoff

> Operational state only. Resolve the live branch/commit and CI from Git before acting. Historical detail belongs in `SESSION_LOG.md` and dedicated handoffs.

## Interaction responsiveness correction — 2026-10-02

- User reports first polish candidate feels slower across all controls and asks for gentler answer haptics. Canonical deployment is held; `feature/home-answer-latency` builds forward from main product a68. Root remains released1ba.
- Measured regression: shared 110 ms transitions leave the prior answer colors on the first frame after commit and animate release. Remove shared color/scale transitions and new page/question/sheet motion; keep immediate touch-down tint, cancellation, scroll/focus preservation and existing layout/colors.
- Practice outcome feedback is now a single7/9 ms browser pulse; native success/error use light CLOCK_TICK instead of CONFIRM/REJECT/LONG_PRESS. Completion remains distinct; saves/rollback and selective haptic policy are preserved.
- Faster bank indexing, leaner durable saves and in-place CBT/bookmark/FSRS/mark edits remain. Fresh first-frame/press/release checks passed at320/390/820/1194px plus reduced motion. All87 local checks and Practice/Continue/FSRS browser regressions passed. Full exact-candidate CI is required before promotion/release; physical feel remains subject to user review.
- Prior a68 passed feature full36956370295 and fast gates; it is already on main (PR83 includes PR82). Its official main full36957980864 is running, but passing it alone does not authorize releasing the user-reported regression.
- See `docs/INTERACTION_POLISH_2026-10-02.md`; preserve the analysis, mocks, Home-only header and approved streak/FSRS work.

## Current UI refinement — 2026-10-02

- Prior candidate: `feature/home-analysis-refinement`, based on released product `1ba1635428a661c4e9c152e2e90d75b441c05b0b`. Now included in certified main product a68; official packaging/canonical deployment are pending.
- Insights labels follow week/month/year; historical comparisons show dates. Donuts align with empty prior periods; visible bar groups centre on their interval labels. Preserve the comparative full-year heatmap and removed Study Map/Topics to revisit.
- Late owner `apply_refined_analysis_v1.py` follows clarity: compact score/accuracy, green/coral/amber outcomes, test-only subject/topic tabs, saved-timing distribution/cumulative charts, and existing Review/correction/marked/retake/module actions. The global subject badge is removed; the NK QBank header appears only on Home, per the latest user request.
- Named fixed-question mocks use optional `state.savedMocks`, durable snapshots and a separate sync collection with tombstones. Modules already support names, save/resume and restart. Tests remain immutable apart from explicit title edits.
- 84 local checks pass; generated responsive screenshots and result/mock journeys passed. Practice/Review/CBT/marked/FSRS/clarity regressions passed; combined full Ubuntu content/browser/APK/emulator CI passed on a68; canonical release is pending.

## Released Insights and clarity — 2026-10-02

- Previous root release is certified product `1ba1635428a661c4e9c152e2e90d75b441c05b0b`; PR81 merged. Feature full run `36947218296` and main full run `36949193523` passed content/browser/PWA/APK/package and phone/tablet emulators; both fast gates passed.
- Canonical https://nk-qbank.pages.dev serves the exact certified HTML (SHA-256 `24ad5d627b94e25c9d6f79cbdc8ff73ec759f924ea8fde533d21c5d84cfb8737`); hosted phone/tablet period/reload/relative-heatmap checks passed.
- Automatic production trigger did not start. Release branch `release/approved-production-20261002-clarity` at `cffb8ad0d9e63eab7ddb483708472cb3581350c6` pins the verified main artifact; deploy run `36951774743` succeeded without rebuilding. Main stayed unchanged for artifact identity checks.
- Owners `apply_learning_insights_v1.py` and `apply_app_clarity_v1.py` implement read-only comparative metrics, continuous year-relative shade/glow and compact app screens. Accepted Revision/liquid streak/editable FSRS and all source work remain included. Physical APK acceptance remains separate.

## Canonical lineage

- Accepted product commit: `125d68b`.
- Accepted baseline: V11.6 remains the rollback product baseline; the Continue Practice contract below is separately user/device accepted.
- **Production integration trunk:** `main`; `feature/marrow-canonical-full-current` remains the content-work lane and needs fast-forward alignment to the released Insights/clarity product before future content work. Preserve merged Revision/streak/FSRS features.
- Latest accepted Practice behavior was verified from checkpoint `74abb670c3ae088e06653681e85c347212222455`; full run `34695680534` succeeded and the user physically confirmed the Continue Practice flow. This behavior is build-verified, **device-verified**, and user-accepted.

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
3. Released Insights/clarity and all prior approved features are live together. Certify the new chart/result/mock refinement before publishing it; preserve23 source gates, two archival image gaps and PrepLadder source-comparison backlog.

## Memory pointers

- PrepLadder visual verification handoff: `.project-memory/PREPLADDER_VISUAL_VERIFICATION_2026-09-16.md`.
- Matching/structured presentation handoff: `.project-memory/MATCHING_TABLE_ARCHITECTURE_HANDOFF_2026-09-14.md`.
- Practice postmortem: `.project-memory/PRACTICE_FLOW_POSTMORTEM_2026-09-12.md`.
- Canonical source consolidation: `.project-memory/FULL_CORPUS_CONSOLIDATION.md`.
- Automation policy: `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md`.
