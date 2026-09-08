# PRODUCT.md — Goals, Principles, Intended Behavior

## What NK QBank is

Private, local-first medical QBank for personal MBBS study: accepted Android
APK plus a V11.7 responsive PWA/cross-device evolution candidate.
Currently covers **Anatomy, Physiology, Biochemistry**. PrepLadder remains
Anatomy 1,068 Q, Physiology 899 Q, Biochemistry 719 Q. The active Marrow
feature candidate additionally contains Anatomy 819/48, Biochemistry 543/26,
and Physiology 753/33 (2,115 Marrow questions total).

## Phase

Core/basic functionality is complete with no known regression.
Work is **refinement, polish, consistency, usability, and engineering
hardening** — not feature rescue. Avoid novelty for its own sake.

V11.6 Content Quality is the accepted device-tested product baseline; it includes
V11.5 Custom Study Modules. Later candidates must build forward from it.
## North star and motto

> Every screen should make the next useful learning action obvious.

Motto: **we do not break anything while we build something.**

Engineering loop: inspect → implement narrowly → build → verify → inspect
packaged APK → fix → rebuild → verify again → physical-device test.
Physical-device behavior is final; CI alone never promotes a baseline.
Prefer building over narrating.

## Intended behavior (protected)

- **Daily loop:** Home → Continue/Practice → Review → Return Home stays
  frictionless; unfinished-session recovery works.
- **Practice:** immediate feedback, source explanations, free navigation,
  bookmarks, Wrong/Due queues feed revision.
- **Timed CBT:** 60 sec/question, answers changeable, correctness only after
  submit; final-question boundary opens the session-review navigator
  (answered/unanswered + jumping), never a persistent toast; singleton
  transient toasts only.
- **Analysis / Review Solutions:** score + distribution + timing + completion;
  canonical Review Solutions entry (`data-v102-review-cta`, `__QB_OPEN_REVIEW`),
  question-first surface, fixed Previous/Next footer, grid/navigator + End
  Review returning to originating analysis; source-PDF explanations where
  applicable.
- **Home:** one cohesive surface; greeting + Home-only streak (rectangular/
  chiseled, integrated axis, restrained motion) + week strip; Today’s Focus
  (Continue Practice, Review-Due-when-due, permanent Practice-20-Random,
  Timed CBT); Subjects library with accurate counts/progress; progress
  snapshot; Quick Access; Performance/Recent; clear next action.
- **Topics:** compact subject selector, search/filter, accurate completion
  (attempted/total, not accuracy-gated), progress %, direct chapter entry,
  reliable same-route scroll reset.
- **Chapter:** Practice/Timed actions, coverage metrics, source-order library
  with Correct/Incorrect/Unattempted + PDF page.
- **Tests:** exam-mode hero + multi-subject builder (subject cards,
  All/Selected-topics scope, pool count, question count) + history.
- **Insights:** Accuracy, Avg time, Due, Completion + chapter coverage +
  recent sessions; distinguish no-evidence from poor performance.
- **Revision libraries:** Bookmarks (manual), Wrong (auto from incorrect),
  Due Review (FSRS spaced queue); empty states explain how to fill them. FSRS
  ratings, Today queue, forecast, settings, migration, and undo work in both
  the Android APK and website/PWA.
- **Custom Study Modules (V11.5):** reusable sets from subject/topic +
  Unattempted/Wrong/Bookmarked/Mixed (seeded shuffle, Mixed weighted
  Wrong-heavy); frozen IDs at creation (status changes never rebuild);
  resume via Practice engine with snapshot sync; finish creates Practice
  Analysis linked to module; restart clears progress but preserves frozen set
  and global history; missing IDs skipped safely.
- **Source faithfulness:** original PDFs are truth; exact normalized
  stem matching, subject-specific PDFs only, no fuzzy cross-subject images,
  no `Question N has image` heuristics; aspect preserved; fullscreen viewer
  with zoom/pan.
- **Content quality:** a takeaway must express one coherent fact and preserve
  ownership in comparisons; table columns must never be flattened into a false
  combined statement. Extraction footers, vendor labels, page counters, URLs,
  and similar source metadata must not appear in displayed stems. Prefer a
  concise correct-answer fallback over a confident but semantically merged
  takeaway.
## Multi-bank source behavior

- A medical subject may contain multiple question-bank sources. If so, selecting
  the subject opens a source selector before Topics.
- Current Marrow feature candidate:
  - Anatomy → PrepLadder | Marrow (819 questions / 48 Marrow topics).
  - Biochemistry → PrepLadder | Marrow (543 / 26).
  - Physiology → PrepLadder | Marrow (753 / 33).
- Bank/source selection changes content provenance, not the learning engine.
  Practice, CBT, Review, Custom Study Modules, FSRS, sync, analytics, bookmarks,
  persistence and revision queues remain shared.
- Initial cross-subject ingestion is **source-faithful first**. Newly added
  Marrow questions render their supplied structured explanation without a new
  rewrite/polish phase.
- The previously approved enhanced explanation layer remains an auditable
  augmentation subset (62 Anatomy + 80 Physiology) and must not be generalized
  by silently rewriting stored source text.
- PrepLadder explanations remain source-PDF based. Marrow uses native structured
  text/tables and must expose Key takeaway + Detailed explanation + Structured text.
- Stored Marrow wording is source-owned and remains unchanged. Later readability
  work may alter hierarchy, semantic emphasis, spacing, bullets/lists and table
  presentation without silently changing medical meaning.
- Figure metadata is preserved even when image binaries are deferred; text-bank
  integration must not be blocked by the later figure pass.

## Design language

Compact, medically serious, phone-native (~576px-class width, 44–48px targets).
Palette: primary cyan `#3FCFE8`, deep `#135262`, ink `#171A2B`, muted
`#6F7385`, success `#159A68`, error `#D64B58`, info `#3F7BE8`, amber `#D98B16`,
canvas ~`#F6F7FB`, surface `#FFFFFF`, line ~`#E4E6EF`.
Differentiate via spacing/hierarchy/density/state/restrained color, not chrome.
Figma `QBank V11 — Design Foundation` is visual reference only, not architecture.

## Non-goals

Duplicate navigation, excessive chrome, replacement app shell, wholesale native
Compose rewrite, global renderer rewrites, gamification overload, decorative
graphs over actionable summaries.

<!-- V11.7_DEPLOYMENT_HANDOFF_2026-09-07 -->
## V11.7 deployment handoff — 2026-09-07

- Active candidate: `v11.7-cross-device-pwa-sync`. Physically accepted rollback baseline remains **V11.6 Content Quality** at `125d68b`; do not call V11.7 accepted until Android migration and Android↔iPad sync pass on real devices.
- Firebase/Firestore is configured and builds now report `QBANK_RUNTIME_CONFIG_OK firebase=configured`. Exact GitHub Variables: `QBANK_FIREBASE_API_KEY`, `QBANK_FIREBASE_PROJECT_ID`, `QBANK_ANATOMY_PDF_URL`. Firestore user-scoped rules and the intentionally empty composite-index set are deployed.
- Cloudflare Pages project: `nk-qbank`. Exact GitHub Secrets: `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`. Push builds create preview deployments. Manual **Build V11.7 Android + PWA** dispatch now also promotes the same artifact to production so `nk-qbank.pages.dev` is updated deliberately.
- Anatomy source PDF uses the configured public R2 object URL because it is ~46 MiB; Biochemistry and Physiology PDFs ship inside `build/web`.
- Physical iPad testing found and fixed two browser runtime bugs: `278b6c5` fixed the blank-screen sync bootstrap (`nkAuth` initialization timing); `7b047e5` fixed PDF.js canvas creation by avoiding a local `document` name that shadowed the DOM document.
- Latest hashed preview opens successfully on iPad. Before the production-promotion workflow change, the root `nk-qbank.pages.dev` still served the older blank production deployment. Source-PDF rendering, Anatomy/R2 CORS, final production URL, Android in-place upgrade, and full two-way sync still require physical verification.
- Next: wait for CI on the current branch → manually dispatch **Build V11.7 Android + PWA** once → verify `https://nk-qbank.pages.dev` → add final Pages hostname to Firebase Authentication authorized domains → ensure R2 CORS allows the exact Pages origin and Range GETs → install V11.7 APK over V11.6 without uninstalling → verify old local data → same-account Android/iPad sync, offline/reconnect, force-close/reopen, sign-out/in tests.

## 2026-09-08 — User rejection and corrective handoff

User requires reference-faithful luminous Topics journey, a viewport-visible Continue Learning tray, and a genuine More -> FSRS customization destination with explicit Save/Cancel. The shipped candidate is rejected. PDF/source readability is a protected priority, not a polish tradeoff.


## Feature-PWA recovery status — 2026-09-08

The user physically confirmed the recovered Topics journey/fixed Continue
Learning tray and dedicated FSRS customization page are good on
`feature/marrow-bank-pilot`. Preserve that implementation exactly.

The next Topics refinement is taxonomy accuracy, not another visual redesign.
Use `docs/MARROW_TOPIC_INDEX_TAXONOMY.md`.

The next Marrow content-quality phase is explanation fine-tuning through a
separate augmentation/display layer while raw ED8 source text remains auditable.
Use `docs/MARROW_EXPLANATION_FINE_TUNING.md`.
