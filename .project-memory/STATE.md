# STATE.md — Current Project State and Handoff

> Resolve live branch, commit, and CI from Git before acting. Historical detail is in `SESSION_LOG.md` and dedicated handoffs.

## Baseline and active work

- Revision hub candidate (2026-10-01): `feature/home-revision-hub` / PR #80
  builds from combined main. Revision replaces FSRS in primary navigation;
  Home shows global due/missed counts; More retains neutral notes/search rows.
  Revision keeps all four scoped queues, embeds a seven-day scoped forecast,
  and links the existing FSRS graphs/settings. Color is limited to count/icon
  accents. Home has a liquid blue/violet connected week strip reaching toward
  the next pending day, plus animated orange flame/embers growing at
  3/7/14/30 days. Future days stay unfilled; reduced motion is static; there
  are no celebration notices. The earlier amber treatment was rejected.
  Canonical streak counting, schedules, persistence, source content, and session
  engines are unchanged. Product `d3247ca63d3db3f99fa9310be4c399dde0dd449a`
  is build-verified: all 75 local checks, Engineering `36838440726`, and full
  generated browser/PWA/APK/Android phone+tablet run `36838433115` pass,
  including Pause/Home/Continue and source hygiene. Preview:
  `https://ca26da11.nk-qbank.pages.dev`. Deployed HTML passes the full Revision/
  streak browser suite; the live URL passes Home/Revision/FSRS navigation with
  no page errors. CI Home and Android captures were inspected; local GIF/MP4
  shows six seconds of real motion. Physical/user visual review remains pending.
  Main and production are unchanged. A documentation-only `[skip ci]` handoff
  does not change the certified product. Next step: user review of the preview.

- Completed image promotion (2026-09-30): main combines the finished image
  integration with every approved account/study feature (PR #79). Certified
  product `a7f1be5176538cecda350511dd1d2a74b1ec9955` passed all 75 local
  checks, Engineering `36738373712`, and full browser/PWA/APK/Android phone
  and tablet `36738347129`. Preview: `https://001e687e.nk-qbank.pages.dev`.
  Coverage: 1,502 references / 1,421 released / 79 invalid / two archival
  source gaps / zero unresolved cues. Runtime: 1,486 bindings / 1,306 assets /
  1,128 owners. All 114 source-completeness contracts passed 228 runtime
  checks; final Physiology images passed 26 viewport cases. Notes, Continue
  Practice, search, correction, Home/result, packaged bytes and Android passed.
  The independent Biochemistry Ch14 Q1–Q8 explanation batch and tap/haptic
  changes remain excluded; main inventory is 662 enhanced / 2,049 pending.
  Source imports/PDFs and worker branches are unchanged. A later `[skip ci]`
  handoff changes documentation only; certification stays at the product SHA.
  Production remains the September 27 deployment. Future content integration
  must preserve this combined main runtime. See
  `docs/COMPLETED_IMAGE_MAIN_PROMOTION_2026-09-30.md`.
- Approved study-tweak promotion (2026-09-30): `main` includes account
  reset/switching, all-bank question search, Practice correction passes, and
  Home/result refinements from the user-reviewed donor commits (PR #78).
  Exact product `f9b0d0145f49aaffab7fcca6d9da78b507905048` passed 74 local
  checks, Engineering `36733960874`, and full browser/PWA/APK/Android phone
  and tablet run `36733869611`. Preview: `https://9629afb2.nk-qbank.pages.dev`.
  Notes passed Practice/reload/Review/deletion browser checks and remain in
  main. Tap/haptic feedback and its bundled latency changes are unapproved and
  excluded; image/explanation agents and donor branches remain untouched.
  A later documentation-only `[skip ci]` handoff does not change the certified
  product. Production PWA remains the September 27 release. After explicit
  user acceptance, promote verified tweaks to main without bundling unapproved
  work; production deployment remains separate. See
  `docs/APPROVED_STUDY_TWEAK_PROMOTION_2026-09-30.md`.
- Repo: `Numankhan2013/V10.1`. Accepted product commit: `125d68b` (V11.6 accepted baseline and rollback point). The user explicitly authorized integrating the accepted study candidate and UI changes into `main` and promoting production on 2026-09-27; release only the exact SHA after full CI passes. Physical Android acceptance remains distinct.
- Sole Marrow/product integration trunk: `feature/marrow-canonical-full-current`. Its last recorded verified canonical checkpoint was `356cce4`; Engineering `35453226391` and full Android/PWA/browser/APK `35453226292` passed. Recheck the live head before any integration.
- Integrated production release: `main` product SHA `d43da3dbdaa639214d676b333152654568fe5ba9` combines the accepted study build, two reviewed UI updates, and current `main` source-audit files. Full main CI `36324929838` and production release `36325843382` passed. The release set Cloudflare Pages Direct Upload production branch to `main`; root `https://nk-qbank.pages.dev`, alias `https://main.nk-qbank.pages.dev`, and preview `https://37799f47.nk-qbank.pages.dev` return HTTP 200 and serve byte-identical builds.
- Current complete Marrow ED8 corpus: Anatomy 1,115 questions/63 topics; Biochemistry 582/28; Physiology 1,014/43; total **2,711/134**. Source data stays immutable. See `FULL_CORPUS_CONSOLIDATION.md` and `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md`.
- PrepLadder source-labelled PYQs: 1,118 in 27 topics (Anatomy 410, Physiology 362, Biochemistry 346). Marrow ED8 lacks trustworthy PYQ/exam/year metadata; never infer it.

## Current study experience and verification

- Bank-aware Custom Modules, PYQ topic selection, restored Home focus, full-page topic picker, saved read-only notes with More → My notes, Quick Revision, and cross-bank Insights are already integrated into `main`. The user physically reviewed their feature previews and accepted the working flows; the Quick Revision topic-filter visibility was deferred, and the Insights addition was judged adequate but not compelling.
- Full-page Tests → bank → topics → question count builder uses exact subject/bank/topic IDs and the shared exam engine. Product `5d585de` passed Engineering `36213112458` and full browser/PWA/APK/Android emulator `36158438170`; preview `https://2752f581.nk-qbank.pages.dev`. The user checked it and said it works. The dedicated strict per-question chapter test remains.
- Completed timed CBT results show source-exact subject/bank/topic analysis and targeted missed-ID follow-up Practice; repeated-Submit taps are guarded. Product `b65ad21` passed Engineering `36216951965` and full browser/PWA/APK/Android emulator `36216944458`; preview `https://c22cbdd0.nk-qbank.pages.dev`. The user checked it and said it works.
- Current candidate: Insights QBank tracker for all six subject/bank combinations, showing answered-once coverage and latest misses by source topic. Bank selection, search, progress filters, and topic entry reuse the existing bank registry/routes; old active-bank chapter list is replaced. Product `220f954` passed Engineering `36218442172` and full generated browser/PWA/APK/Android phone+tablet emulator `36218442273`; full-page phone/tablet Insights captures were inspected and preview `https://697c1da1.nk-qbank.pages.dev` returned HTTP 200. User review pending.
- Exam practice: product `af30703` puts the compact two-way PYQ toggle beside Select all/Clear all. Local 64 checks, Engineering `36233896258`, and full generated browser/PWA/APK/Android phone+tablet emulator `36233894250` passed; preview `https://87a819e1.nk-qbank.pages.dev`. The user confirmed it works and accepted it as doable for now.
- Active candidate: Android system Back on a Practice or timed-test question now asks "Do you want to exit?" in a native warning. Stay retains route/question/session; Exit uses existing saved-session history navigation, and timed tests disclose that their timer keeps running. The native change is owned by `tools/apply_android_back_guard_v1.py` after secure-origin generation. Product `e33dbab` plus emulator-check refinement `445fd13` passed local 64 checks, Engineering `36244266344`, and full generated browser/PWA/packaged APK/Android phone+tablet emulator `36244266405`. Both native dialog captures and the emulator report were inspected. Web preview `https://0c0be99e.nk-qbank.pages.dev` returned HTTP 200, but the native Back warning is reviewable only in the packaged Android app. User physical review remains pending.
- The user expected the exit warning in the Cloudflare phone preview and found it absent. Browser/PWA Back warning is now in source via the shared `question_interaction_core.js` popstate boundary: Stay restores the question route; Exit follows browser history. App-initiated navigation is distinguished from Back so a normal subject change does not prompt. `qbank.local` retains its native dialog. Product `f450ab7` passed Engineering `36248903088` and full generated browser/PWA/APK/Android phone+tablet emulator run `36248903102`; Cloudflare preview `https://8552f47f.nk-qbank.pages.dev` returned HTTP 200 and served the warning code.
- The user opened the Browser/PWA Back preview and confirmed the warning works. They assigned Marrow explanation fine-tuning and image integration to separate job automations and requested another learner-facing phase. Timed CBT now has a two-way Mark for review control; marks survive reload, appear in the navigator and final review grid, and are saved with the test for exact-ID Practice follow-up, including correct guesses. Product `31ac38a` passed local 66 checks, Engineering `36293641439`, and full generated browser/PWA/packaged APK/Android phone+tablet emulator run `36293641549`. Cloudflare preview `https://da6eaa24.nk-qbank.pages.dev` returned HTTP 200 and served the new code. User physical review is pending.
- The user confirmed marked-question CBT works. Active timed tests now appear as a Resume card on Home, Tests, and the CBT builder after Exit, with answered/marked progress and a running-timer reminder. Resuming retains the same saved session; an expired timer uses existing completion logic. Product `78e391f` passed local 68 checks, Engineering `36298273342`, and full browser/PWA/packaged APK/Android phone+tablet emulator run `36298273539`. Cloudflare preview `https://edd8fb9f.nk-qbank.pages.dev` returned HTTP 200 and served the builder card. The user confirmed it works.
- The user asked to merge the timed-test notice into Today's Focus only if it was a sub-minute change; the existing Focus handles paused Practice and saved modules, so this integration was deferred. A concrete next reliability gap was found: starting a saved module directly could overwrite an active timed test. Product `91c59b8` and packaged Android check `2997cdb` route that action through the existing Resume/Abandon/Cancel conflict flow. Local 68 checks, Engineering `36300815881`, and full browser/PWA/packaged APK/Android phone+tablet emulator run `36300815905` passed. Cloudflare preview `https://e17cbb6d.nk-qbank.pages.dev` returned HTTP 200 and served the updated dialog. User physical review is pending.
- The user then prioritized washed-out PrepLadder source PDF explanations. The earlier sharp-zoom repair was intact, so product `70794a2` added a scoped `contrast(1.16) saturate(1.12)` display adjustment to inline and fullscreen source PDF pages in the final shared session style. It leaves PDFs, generated images, Marrow visuals, and mappings unchanged. Before/after browser captures showed darker text and stronger blues with table strokes visible; browser checks covered all three subjects and zoom, and packaged Android phone/tablet checks covered Review Solutions. Local 68 checks, Engineering `36303853277`, and full browser/PWA/APK/Android run `36303853023` passed. Preview `https://ce13d233.nk-qbank.pages.dev` returned HTTP 200 with the rule. Physical Android/iPad review is pending; see `docs/PDF_RENDERING_CONTRAST_INVESTIGATION.md`.
- The user reconsidered simultaneous timed tests and explicitly deprioritized them. The multiple-test candidate was reverted before deployment. A confirmed **Abandon test** action now lives inside both timed-test question grids (navigator and final review), with no action on the question page. Cancel and failed save keep the test; successful abandon discards its unfinished answers, stops the timer, creates no result/attempts, and returns to Tests. Product `5ea37d8` with browser-check fix `191ef61` passed local 70 checks, Engineering `36313958399`, and full browser/PWA/packaged APK/Android phone+tablet emulator `36313958394`. Preview `https://22a83cd1.nk-qbank.pages.dev` returned HTTP 200 and served the action; the user checked it and said it works.
- A completed global-timer CBT can be retaken with its exact saved question IDs, blank answers, and a fresh timer. The saved retake links to the initial test through `retakeOf`, and its result compares correct, accuracy, attempted, incorrect, unattempted, time, recovered/new misses, and missed topics side by side while retaining the existing result analysis and Review Solutions. Product `4a2d5af` with browser-check fix `108dfe3` passed local 70 checks, Engineering `36315690909`, and full browser/PWA/packaged APK/Android phone+tablet emulator `36315823769`. Preview `https://726640e4.nk-qbank.pages.dev` returned HTTP 200 and served the comparison; the user checked it and said it works. Android phone/tablet comparison captures were inspected.
- UI previews, CI/emulator checks, and user preview acceptance do **not** establish an in-place physical APK upgrade or production acceptance.

## Product architecture to preserve

- Shared bank registry: `MARROW_RECORDS → MARROW_BY_SUBJECT → BANKS_BY_SUBJECT`. Reuse Practice, CBT, Review Solutions, FSRS, sync, modules, analytics, and navigation across banks; do not fork by subject.
- Primary navigation in the Revision candidate: **Home · Revision · Tests · Insights · More**; FSRS is nested in Revision. Subject journey: My Subjects → bank chooser → Topics → topic → Practice/Topic Test.
- FSRS schedules answered questions. Pause commits answered work only; final submission marks remaining session IDs skipped. Globally unseen questions stay unseen.
- Raw Marrow and PrepLadder source, stable question IDs, answer keys, source visuals, and PDF mappings remain protected.

## Accepted Practice / Continue Practice contract — device-verified

- Normal Practice footer is Previous + Next. Header grid and the end boundary open the same final review grid; its actions are Pause + Submit only.
- Pause preserves the same active session and full original ordered `sessionQuestionIds`, index, answers, timing, and progress. An unanswered current question is not skipped by Pause.
- Home Continue Practice resumes that session and position; a damaged older `questionIds` array is rebuilt from `sessionQuestionIds`, so a multi-question session never collapses to `1 / 1`.
- CBT, Review, Wrong/Bookmarks, FSRS, and Modules remain outside the normal Practice override. See `PRACTICE_FLOW_POSTMORTEM_2026-09-12.md` and `CONTINUE_PRACTICE_HANDOFF.md`.
- Changes touching Home, Practice, persistence, sync, question navigation, review, FSRS, or transforms require the generated multi-question Pause → Home Continue → complete-list/progress regression path.

## Content and presentation limits

- Structured explanation tables must retain nonempty source cells in order, never `[object Object]`; user physically verified the repair. Matching/list reform and scientific notation are build-verified but later residual presentation still needs source-backed physical review. See `MATCHING_TABLE_ARCHITECTURE_HANDOFF_2026-09-14.md`.
- OCR cleanup must use rendered authoritative source and stable-ID/fingerprinted overrides. The final source-completeness ledger records recoverable source repairs and 33 underdetermined source omissions; explanation-wide cleanup remains separate and source-grounded.
- The source-completeness pass restores two source-confirmed PrepLadder keys
  (`physiology-23-38`, `physiology-33-33`). Thirty-three demonstrated source
  omissions remain gated against scored answers through the pinned ledger;
  original imports remain immutable.
- Explanation inventory last recorded **662 enhanced-reference / 2,049 pending / 2,711 total**. Anatomy Ch7 Q11–Q21 is build-verified with physical review pending. Next batch must reacquire ownership from live canonical state; see `AUTOMATION_HANDOFF_ANATOMY_EXPLANATION_CH07_Q011_Q021_2026-09-23.md`.
- PrepLadder visuals still have a separate 422-item manual source-comparison
  audit. All recoverable Marrow images are integrated; two archival source
  gaps remain documented, with no unresolved visual text cues. This does not
  establish physical APK/data-preservation acceptance.

## Known problems and next step

- Main now contains completed image integration and the approved study/account
  refinements. Production has not been redeployed. Physical in-place APK,
  data-preservation, and real-device sync checks remain separate.
- Preserve the two archival source-image gaps and 33 incomplete-source gates;
  recovery is deferred pending authoritative source material. The independent
  Biochemistry explanation batch needs its own promotion approval. PrepLadder's
  separate 422-item manual visual audit is not certified by this image release.
- Before another content batch, its owner should reconcile the accepted main
  runtime into the canonical integration trunk so future work retains notes,
  account isolation, search, correction, and Home/result behavior. Existing
  worker branches were left intact. Tap/haptic changes remain unapproved.
