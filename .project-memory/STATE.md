# STATE.md — Current Project State and Handoff

> Keep concise and current. History goes in `SESSION_LOG.md`, durable reasoning
> in `DECISIONS.md`, and future work in `ROADMAP.md`.

## Repo / branch

- Repo: `Numankhan2013/V10.1` (private)
- Active branch: `feature/marrow-bank-pilot` (isolated Marrow integration candidate; production PWA remains deliberately separate)
- Resolve live branch/HEAD with `git branch --show-current` and
  `git rev-parse HEAD`; never hardcode a self-staling current-HEAD value here.
- Accepted product parent: V11.6 `125d68b`; the V11.7 branch merged the
  harness-neutral memory lineage at `309aabb`. Resolve live HEAD with Git.
- Earlier product lineage: V11.5 `f13d12f` → V11.6 `125d68b`.
- `main` (`8bc0be4`) is stale and must not be used as the V11 baseline.

## Marrow bank pilot handoff — 2026-09-08

- User opened the Cloudflare feature preview and confirmed the new Marrow flow is working beautifully.
- Final pilot commit lineage is on `feature/marrow-bank-pilot`; latest green verification: Engineering Gate `34159542431` and full Android+PWA run `34159542436`.
- Live preview: `https://feature-marrow-bank-pilot.nk-qbank.pages.dev`; production promotion was intentionally skipped.
- Anatomy now supports a bank/source selector: PrepLadder (existing 1,068 questions / 50 topics) and Marrow (62 questions / 4 topics) using the same Practice/CBT/Review/FSRS/sync/module architecture.
- Marrow explanations are native structured text: **Key takeaway + Detailed explanation + Structured text**. PrepLadder keeps its existing PDF renderer. Do not rewrite Marrow wording during explanation polish; styling/typography/bolding/lists/tables only.
- Three incomplete-list Anatomy source questions were resolved with provenance and no learner-facing manual-review flag: `ANAT_CH02_Q010`, `ANAT_CH03_Q004`, `ANAT_CH04_Q013`.
- Critical next-step architecture: the pilot currently has one Anatomy-specific `MARROW_RECORD`. Before adding Physiology/Biochemistry or scaling Anatomy, generalize to a subject-indexed/general bank registry; do **not** copy the special case per subject.
- Canonical next-session procedure, schema, integrity rules, CI gates, and pilot lessons are in `docs/MARROW_BANK_INTEGRATION.md`.

## Marrow explanation architecture — full Anatomy rollout 2026-09-08

- User visually reviewed the 20-question gold pilot and called it near-perfect,
  approving the typography, selective bolding, tables, and concise
  **Why the other options are wrong** grammar for full Marrow Anatomy rollout.
- User requested only a *very small* additional concision pass. Implemented as a
  display-only micro-trim: suppress short lead paragraphs only when they
  substantially duplicate the Key Takeaway; suppress dead figure/image
  boilerplate when the asset is not rendered; replace source `Option A/B/C/D`
  rationale paragraphs with the standardized concise distractor section. The
  stored Marrow transcription is unchanged.
- All 62 current Marrow Anatomy questions now use the approved explanation
  architecture with selective exam-discriminator emphasis and exactly 3
  distractor rationales each (186 total). Existing structured source tables are
  preserved.
- Permanent FSRS rule remains protected: the recall dock stays fixed/floating
  above Previous/Next after answering and is not part of explanation flow.
- Full rollout verification: Engineering Gate `34163197757` success; full
  Android+PWA run `34163197772` success; real browser verified a formerly
  non-pilot question, micro-concision on PGC Q1, source-table preservation, and
  the fixed FSRS dock. Preview:
  `https://feature-marrow-bank-pilot.nk-qbank.pages.dev` (immutable
  `https://bae56103.nk-qbank.pages.dev`). Production promotion remains skipped.
- Next product step after user spot-check: generalize the temporary Anatomy-only
  `MARROW_RECORD` into a subject-indexed/general bank registry before adding
  remaining Anatomy, Physiology, and Biochemistry Marrow banks.

## Verification and accepted baseline

- Accepted baseline: **V11.6 Content Quality**. The user physically tested and
  accepted the APK on 2026-09-06.
- Accepted product commit: `125d68b`; canonical APK run: `34050921180`.
- Latest V11.5 memory-head build `34051356682` and Engineering Gate
  `34051356708` both passed at `e6a2fc7`.
- V11.6 Engineering Gate `34050921166` and full packaged build `34050921180`
  passed before physical-device acceptance. It improves comparison/table
  takeaways and removes PrepLadder/page metadata from 78 of 719 audited stems.

Labels are strict: implemented ≠ build-verified ≠ device-verified ≠ accepted
baseline. Only explicit user physical-device approval promotes a candidate.

## What currently works (V11.6 device-verified and accepted)

- Practice, Timed CBT, final-question session review, navigator/jumping,
  Submit/Finish, Practice/CBT Analysis, and Review Solutions with grid,
  Previous/Next, End Review, and source explanations.
- Home V4/V8 command center, Topics V2, Chapters, Tests, Insights, More,
  revision libraries, subject switching, and reliable scroll reset.
- All-subject random practice, multi-subject CBT, accurate subject/topic counts,
  persistent attempt history, bookmarks, wrong/due queues, and Insights.
- Source visuals: 420 packaged PNGs (Anatomy 297, Physiology 62,
  Biochemistry 51), source-PDF fallback, fullscreen zoom/pan, isolated
  Biochemistry renderer, and authoritative Physiology source PDF.
- Custom Study Modules: persistent reusable subject/topic sets using
  Unattempted/Wrong/Bookmarked/Mixed pools, frozen IDs, deduplication, seeded
  selection, resume, Home continuation, completion analysis, and unified history.
- Deterministic transforms, final and packaged JavaScript checks, product/CBT
  contracts, Gradle APK build, packaged verification, and build manifest.

## Known problems / cautions

- V11.7 is a **build-verified, not device-verified** evolution branch merging
  accepted V11.6 with the memory lineage. Product commit `1b1fc9f`; Engineering
  Gate `34076883867` and full APK/PWA run `34076883874` passed. Cloud deployment
  was correctly skipped because account credentials are not configured. Preserve
  `v11.6-content-quality` as the immutable accepted checkpoint.
- Root `AGENTS.md` placement is correct, but no filename can force every unknown
  harness to load it. Thin common-harness adapters and
  `tools/verify_project_memory.py` reduce discovery and drift risk.
- Large binaries (three PDFs, ~420 PNGs, ~6 MB source app) make full clones slow;
  prefer targeted inspection or partial clones when appropriate.
- Source visual and protected session/review infrastructure must not be changed
  casually during unrelated work.

## FSRS status — accepted functional milestone

- The source app contains the build-time-installed FSRS v6 scheduler using vendored `ts-fsrs` 5.4.2 (MIT), deterministic fuzz-off scheduling, schema-v2 card state, immutable rated attempts, migration backup/due-date preservation, all-subject daily queue, rating controls, forecast, settings, and undo.
- The new APK was installed and confirmed working by the user. The website/PWA was also opened and confirmed functional. Treat FSRS as build-verified and device/user-verified in both targets; do not describe it as pending acceptance.
- The detailed behavior and invariants are documented in `docs/FSRS.md`.

## Known problems / immediate next step

- User confirmed Android synchronization succeeds on 2026-09-07. Stop the historical 403 investigation. Finish the pending PWA update UI/reliability improvements and Termux/CI verification; preserve accepted FSRS behavior.
- Next: preserve the accepted FSRS behavior while completing the separate Android↔PWA synchronization verification. V11.6 remains the rollback checkpoint for unrelated V11.7 deployment work.

## V11.7 platform continuity

- Android app, responsive PWA, Firebase/Firestore synchronization, FSRS, update
  flow, source-PDF rendering, and the existing three PrepLadder subjects are the
  working foundation beneath the Marrow pilot.
- User has confirmed the current app/PWA are functioning and synchronized.
  Historical sync debugging and deployment chronology live in
  `.project-memory/SESSION_LOG.md`; do not re-open those investigations unless
  a fresh regression appears.
- Cloudflare project remains `nk-qbank`; feature-branch pushes may deploy
  previews, but Marrow pilot production promotion is intentionally disabled.
- Keep the V11.6 accepted commit metadata unchanged until a deliberate baseline
  promotion; it remains the rollback checkpoint required by memory contracts.
