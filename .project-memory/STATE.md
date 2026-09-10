# STATE.md — Current Project State and Handoff

> Concise operational handoff. Resolve the live branch HEAD from Git rather than
> hardcoding a self-staling commit SHA. Historical detail belongs in
> `SESSION_LOG.md`; durable architecture belongs in `DECISIONS.md`.

## Repo / active product candidate

- Repo: `Numankhan2013/V10.1`.
- Current product branch: `feature/home-approved-redesign-current`.
- This branch is **preview-only** until the user explicitly accepts and promotes it.
  Do not merge/promote production on your own.
- The current work is the **Home / Study / Test / FSRS V3 information architecture**.
  The user explicitly rejected popup-driven subject/topic practice and the old
  top-level Topics navigation model.
- Build-verified, device-verified, and user-accepted are distinct states. Do not
  claim visual acceptance from CI alone.

## Locked V3 Home composition

The Home order is now authoritative:

1. time-aware Good Morning/Afternoon/Evening greeting + sun;
2. compact weekly streak card;
3. Today's Focus with **Continue Practice**, resuming the last/current topic;
4. exactly two review shortcuts: **FSRS** and **Bookmarks**;
5. **My Subjects** — Anatomy, Biochemistry, Physiology, each with icon, topic
   count, question count, completion bar, and percentage;
6. **My Progress** — Questions Attempted, Accuracy, Study Time, filterable by
   Today / This Week / This Month / This Year;
7. quote: “Better questions. A brighter you.” / “Keep learning, keep growing.”;
8. **Strongest Chapters**;
9. **Recent Study Sessions**;
10. graphical **Today's Review** with Due / Learning / Overdue and a seven-day
    workload view. There is **no New cards metric**.

Do not restore Timed Test or Practice as Home quick-action tiles. Studying enters
through My Subjects / Continue Practice; testing has its own primary Tests tab.

## Primary navigation and subject/topic flow

Bottom navigation is:

**Home · FSRS · Tests · Insights · More**

`Topics` is deliberately removed from bottom navigation. A topic is not a
standalone top-level destination because it has to belong to a subject.

Canonical study hierarchy:

**My Subjects → selected subject → full Topics journey UI → selected topic →
Practice or Topic Test**

Rules:
- Never use a subject-picker or topic-picker popup for normal Practice.
- Subject selection must activate the correct subject **and the correct QBank
  record** before rendering Topics. Prefer the current complete Marrow record
  where available. This specifically prevents the previously observed failure
  where a Physiology heading could display Biochemistry topics.
- Preserve the approved Topics journey UI, taxonomy, search/filter controls,
  topic states, and Continue Learning tray.
- Topic/chapter page remains the decision point with **Practice** and **Timed
  Test** actions.

## Timer semantics — do not conflate the two test modes

There are two intentionally different timed-test behaviors:

### Topic-level Timed Test

Opened from a selected topic. Each question has its own **strict 60-second
budget**. If the current question reaches 60 seconds it is automatically locked /
submitted and the learner advances, even if unanswered. Returning to a timed-out
question must not allow changing its answer. Time spent on a question is
cumulative if the learner navigates away and returns.

### Tests tab / QBD / custom timed module

The Tests tab uses a **global exam budget**: `number of questions × 60 seconds`.
Example: 10 questions = 10 total minutes. The learner may spend more than one
minute on one question and less on another. The whole test auto-submits only when
the total budget expires.

### Practice

Practice has **no limiting countdown**, but question/session time is still
recorded for Practice Analysis / Insights. Do not confuse “no countdown” with
“do not track time.”

The Tests setup keeps Timed Test / Practice modes, Full Question Bank, Custom
Module, Wrong Questions, Bookmarked Questions, and question-count selection. The
separate Timer On/Off section is intentionally removed because mode already
expresses whether the session is limiting.

## FSRS — review-only product semantics

NK QBank FSRS is not an Anki-style new-card feed.

A question may enter the user-facing FSRS review pool only when it is:

- answered **incorrectly**, or
- encountered in a session and left **unanswered/skipped** when that session is
  finished/submitted.

A genuinely unseen QBank question must **never be introduced by FSRS**. New
questions are introduced only through normal QBank Practice.

FSRS is a full primary page, not a popup. It must offer **All Subjects / Anatomy /
Biochemistry / Physiology** selection and start due review from that selected
scope. User-facing FSRS/Home review summaries show Due / Learning / Overdue (or
other review-only states), never New cards.

The established offline FSRS v6 scheduling/rating engine remains the scheduler
for eligible review questions. Preserve its deterministic attempt/review history
and recall-rating behavior; change queue eligibility, not medical question
content.

## Tests / custom modules

- Custom Module remains a core QBank feature and must stay available from Tests.
- In Timed Test mode, custom/multi-subject modules use the global `N questions =
  N minutes` exam budget.
- In Practice mode, custom study modules remain normal Practice sessions and are
  untimed in the limiting sense while still collecting timing analytics.
- Wrong Questions and Bookmarked Questions remain valid test/practice sources.

## Marrow bank and content protection

Canonical shared architecture remains:
`MARROW_RECORDS → MARROW_BY_SUBJECT → BANKS_BY_SUBJECT`.
Do not fork question/session engines by subject or bank.

Current supplied Marrow ED8 scope:
- Anatomy: **819 questions / 48 topics**
- Biochemistry: **543 / 26**
- Physiology: **753 / 33**
- Total: **2,115 globally unique questions / 107 topics**

The raw imported Marrow source is authoritative and immutable. Explanation
fine-tuning and image integration remain separate from this UI/navigation pass.
The current reviewed image rollout contains **147 approved assets mapped to 152
released questions**; do not disturb it while changing Home/Study/Test/FSRS.

Preserve:
- source-faithful explanations and provenance;
- the established question screen and Review Solutions behavior;
- the approved Topics journey and explicit Marrow taxonomy;
- image registry/bindings and source-native assets;
- Custom Study Module persistence;
- Android/PWA shared product core and deterministic build pipeline.

## Current implementation checkpoint

`tools/apply_home_command_center_v1.py` is the V3 transform owner. It currently
implements the hybrid Home, My Subjects → Topics routing, FSRS review-only page,
bottom-nav replacement, timer-mode separation, skipped-question eligibility,
and the revised Tests setup. `tools/test_home_command_center_v1.py` is the V3
contract owner.

The next agent must **run/inspect CI and fix actual integration regressions before
calling this complete**. In particular verify:
- Home contains only FSRS + Bookmarks shortcuts after Today's Focus;
- My Subjects activates the matching subject/bank and renders that subject's
  Topics, including switching subjects from within Topics;
- no normal Practice subject/topic popup remains;
- bottom nav has FSRS and no Topics;
- Topic Test expires/locks each question at 60 s;
- Tests-tab Timed Test uses one global N-minute budget;
- Practice remains non-limiting but timed for analysis;
- FSRS never surfaces unseen questions;
- Marrow image/explanation/browser regressions remain green.

After CI, inspect the generated preview visually before requesting user
acceptance. Production remains untouched until explicit approval.
