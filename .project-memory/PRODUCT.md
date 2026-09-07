# PRODUCT.md — Goals, Principles, Intended Behavior

## What NK QBank is

Private, offline-first Android medical QBank for personal MBBS study.
Currently covers **Anatomy, Physiology, Biochemistry** (Anatomy 1068 Q,
Physiology 899 Q, Biochemistry 719 Q per build logs).

## Phase

Core/basic functionality is complete with no known regression.
Work is **refinement, polish, consistency, usability, and engineering
hardening** — not feature rescue. Avoid novelty for its own sake.

V11.5 Custom Study Modules is the accepted device-tested product baseline;
later candidates must build forward from it.
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
  Due Review (spaced queue); empty states explain how to fill them.
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
