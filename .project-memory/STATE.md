# STATE.md — Current Project State and Handoff

> Concise operational handoff. Resolve live branch HEAD from Git rather than
> hardcoding a self-staling hash. Historical detail belongs in `SESSION_LOG.md`.

## Repo / release state

- Repo: `Numankhan2013/V10.1`.
- Current product branch: `feature/home-topic-content-integration-current`.
- This branch is **preview-only** until the user explicitly accepts and promotes it.
- Accepted baseline remains **V11.6 Content Quality**.
- Accepted product commit: `125d68b`.
- Latest product release-candidate commit: `7d88c4ae31be96f3b7b2d5a329e040637a20889d`.
- Engineering Gate `34463318051`: **PASS**.
- Full Android + PWA pipeline `34463318136`: **PASS**.
- Build artifact `V11.7-android-pwa`: artifact ID `10146567237`.
- Screenshot artifact: `recall-dock-and-marrow-pilot-screenshots`, artifact ID `10146529260`.
- Cloudflare Pages immutable preview: `https://240f1d5b.nk-qbank.pages.dev`.
- Cloudflare Pages branch alias: `https://feature-home-topic-content-i.nk-qbank.pages.dev`.
- **Production promotion was skipped. Do not promote without explicit user approval.**
- Build-verified, browser-verified, device-verified, and user-accepted are distinct states.

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
  available. This fixes the old Physiology-heading/Biochemistry-topics mismatch.
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
separate Timer On/Off control remains removed.

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

Full-run contracts passed the review-only/cross-bank behavior, deterministic
replay, same-day relearning, daily cap, long-term scheduling, filters, settings
and undo behavior.

## Tests / custom modules

- Custom Module is a core feature and stays available from Tests.
- Timed custom/multi-subject modules use the global N-questions = N-minutes rule.
- Practice custom modules are non-limiting but still collect timing analytics.
- Wrong Questions and Bookmarked Questions remain valid sources.

## Marrow / protected systems

Shared architecture remains `MARROW_RECORDS → MARROW_BY_SUBJECT →
BANKS_BY_SUBJECT`; never fork question/session engines by bank or subject.

Current source-integrated Marrow ED8 learner scope verified by the green release
pipeline:
- Anatomy: **898 questions / 52 visible topics**;
- Biochemistry: **543 / 26**;
- Physiology: **1,014 / 43**;
- total: **2,455 questions / 121 visible topics**.

Current reviewed image rollout remains **147 assets / 152 released questions**.
The green pipeline revalidated those exact packaged web/APK image counts and
hash-sensitive package checks.

Explanation inventory in this build: **429 enhanced / 2,026 pending**. Raw
Marrow source remains immutable; explanation augmentation and image integration
remain separate controlled layers.

Preserve source explanations/provenance, question and Review Solutions screens,
Topics taxonomy/UI, image registry, module persistence, Android/PWA shared core,
and deterministic builds.

## Latest verification evidence

The release-candidate full run verified, among other protected gates:
- Home V3 contract and integration;
- subject → Topics routing and authoritative subject/bank selection;
- capped FSRS wrong/encountered-skip-only queue;
- global Tests timer and strict per-topic timer semantics;
- project-memory, product-contract and build-pipeline guards;
- source-PDF explanation renderer and all three source routes;
- source visual contract and 420 source visuals;
- CBT invariants and Review Solutions navigator/footer;
- cross-device PWA/sync behavior contracts;
- Marrow browser registry at 2,455 questions;
- Marrow taxonomy at 121 visible topics;
- Marrow image release at 147 assets / 152 questions;
- packaged Android APK integrity and JavaScript syntax;
- Cloudflare feature-preview deployment.

## Known problems / verification cautions

- V3 is a **release candidate**, not yet a user-accepted product baseline.
- Do not infer physical-device acceptance from green CI/browser checks.
- Do not promote the branch/preview to production until the user explicitly says
  to promote.
- Keep the old subject/bank synchronization bug as a regression target: a
  Physiology selection must never render Biochemistry topics and vice versa.
- Keep FSRS unseen-question exclusion as a permanent regression target.
- CI assertions may become stale as product labels evolve; update only obsolete
  assertions and never restore rejected UI merely to satisfy a test.
- Do not disturb Marrow image/explanation work while changing product navigation.

## Current implementation checkpoint

`tools/apply_home_command_center_v1.py` owns the current V3 Home/study/test/FSRS
integration. `tools/test_home_command_center_v1.py` owns its primary contract.
The old regression that assumed one singular bank in FSRS was corrected to
validate the intended cross-bank review-only architecture; regression coverage
was not removed or weakened.

## Next step

User should open the current Pages preview and physically inspect the release
candidate on the target device(s), especially Home, My Subjects → each subject's
Topics, FSRS, Tests, Insights and question-session transitions. Record any visual
or functional defects against this exact candidate. If the user explicitly
accepts it, decide separately whether to promote to production. Until then,
**production stays untouched**.
