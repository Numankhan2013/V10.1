# STATE.md — Current Project State and Handoff

> Concise operational handoff. Resolve live branch HEAD from Git rather than
> hardcoding a self-staling hash. Historical detail belongs in `SESSION_LOG.md`.

## Repo / release state

- Repo: `Numankhan2013/V10.1`.
- Current product branch: `feature/home-approved-redesign-current`.
- This branch is preview-only until the user explicitly accepts and promotes it.
- Accepted baseline remains **V11.6 Content Quality**.
- Accepted product commit: `125d68b`.
- Build-verified, device-verified, and accepted baseline are distinct states.
  Never claim visual acceptance from CI alone.
- Current work is the **Home / Study / Test / FSRS V3 information architecture**.

## Locked V3 Home composition

Home order is authoritative:
1. time-aware Good Morning/Afternoon/Evening greeting + sun;
2. compact weekly streak;
3. Today's Focus with **Continue Practice** for the current/recent topic;
4. exactly two shortcuts: **FSRS** and **Bookmarks**;
5. **My Subjects** — Anatomy, Biochemistry, Physiology with icon, topic count,
   question count, completion bar, and percentage;
6. **My Progress** — Questions Attempted, Accuracy, Study Time with Today / This
   Week / This Month / This Year filtering;
7. “Better questions. A brighter you.” / “Keep learning, keep growing.”;
8. **Strongest Chapters**;
9. **Recent Study Sessions**;
10. graphical **Today's Review** with Due / Learning / Overdue and seven-day load.

There is no New-cards metric. Do not restore Timed Test or Practice as Home
quick-action tiles. Studying enters through My Subjects / Continue Practice;
testing has its own Tests tab.

## Primary navigation and study hierarchy

Bottom navigation is **Home · FSRS · Tests · Insights · More**. `Topics` is
intentionally not a top-level tab.

Canonical study hierarchy:
**My Subjects → selected subject → full Topics journey UI → selected topic →
Practice or Topic Test**.

Rules:
- Never use subject/topic popups for normal Practice.
- Subject selection must activate the matching subject **and matching QBank
  record** before Topics renders. Prefer the complete Marrow record where
  available. This prevents the observed Physiology-heading/Biochemistry-topics
  mismatch.
- Preserve the approved Topics journey, taxonomy, filters/search, state colors,
  and Continue Learning tray.
- Topic/chapter page is the Practice / Timed Test decision point.

## Timer semantics

### Topic Timed Test
Each current question has its own strict **60-second** budget. At 60 seconds it
locks/auto-submits and advances even if unanswered. Returning to an expired
question cannot change its answer. Time spent is cumulative across revisits.

### Tests tab / QBD / custom timed module
Timed Test has one global budget: **question count × 60 seconds**. Ten questions
means ten total minutes; a learner may spend five minutes on one question and
use the remaining five on the others. The whole test auto-submits only at total
expiry.

### Practice
Practice has no limiting countdown, but question/session time is still recorded
for Practice Analysis and Insights.

Tests setup keeps Timed Test / Practice, Full Question Bank, Custom Module,
Wrong Questions, Bookmarked Questions, and question-count selection. The
separate Timer On/Off control is deliberately removed.

## FSRS — review-only product semantics

NK QBank FSRS is not an Anki-style new-card feed. A question may enter the
user-facing FSRS pool only when it was:
- answered **incorrectly**, or
- encountered and left **unanswered/skipped** when its session ended/submitted.

A genuinely unseen QBank question must never be introduced by FSRS. New
questions come only through ordinary QBank Practice.

FSRS is a full primary page, not a popup. It offers **All Subjects / Anatomy /
Biochemistry / Physiology** selection and starts due review from that scope.
User-facing FSRS/Home review summaries show review-only states such as Due /
Learning / Overdue, never New cards. Preserve the existing offline FSRS v6
scheduler and recall ratings for eligible questions.

## Tests / custom modules

- Custom Module is a core feature and stays available from Tests.
- Timed custom/multi-subject modules use the global N-questions = N-minutes rule.
- Practice custom modules are non-limiting but still collect timing analytics.
- Wrong Questions and Bookmarked Questions remain valid sources.

## Marrow / protected systems

Shared architecture remains `MARROW_RECORDS → MARROW_BY_SUBJECT →
BANKS_BY_SUBJECT`; never fork question/session engines by bank or subject.
Current Marrow ED8 scope: Anatomy **819/48**, Biochemistry **543/26**,
Physiology **753/33** = **2,115 questions / 107 topics**.

Raw Marrow data is immutable. Explanation fine-tuning and image integration are
separate from this UI pass. Current reviewed image rollout remains **147 assets /
152 released questions**. Preserve source explanations/provenance, question and
Review Solutions screens, Topics taxonomy/UI, image registry, module persistence,
Android/PWA shared core, and deterministic builds.

## Known problems / verification cautions

- V3 is an implementation candidate, not yet an accepted baseline.
- The old top-level Topics route exposed a subject/bank synchronization bug; V3
  must prove subject cards and in-Topics subject switching load the matching data.
- The legacy FSRS core historically exposed unseen “new cards”; V3 user-facing
  queues must be verified to exclude those completely.
- CI/browser contracts may still encode superseded Home labels; update only stale
  assertions, never reintroduce rejected UI merely to make CI green.
- Do not disturb Marrow image/explanation work while fixing product navigation.

## Current implementation checkpoint

`tools/apply_home_command_center_v1.py` owns V3: hybrid Home, My Subjects →
Topics routing, FSRS review-only page, bottom nav, timer separation, skipped-item
eligibility, and revised Tests setup. `tools/test_home_command_center_v1.py`
owns the V3 contract.

## Next step

Run and inspect Engineering Gate and the complete Android/PWA pipeline. Fix real
integration failures until green. Explicitly verify: Home has only FSRS +
Bookmarks after Today's Focus; My Subjects and in-Topics switching load the
matching subject/bank; no normal-Practice picker popup remains; bottom nav has
FSRS/no Topics; Topic Test locks each question at 60 s; Tests Timed Test uses one
global N-minute budget; Practice remains non-limiting but timed for analytics;
FSRS never surfaces unseen questions; and Marrow browser/image/explanation gates
stay green. Then inspect the generated preview visually before asking the user
for device acceptance. Production stays untouched without explicit approval.
