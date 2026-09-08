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

## Marrow multi-bank handoff — 2026-09-08

- Active candidate remains `feature/marrow-bank-pilot`; production PWA remains deliberately separate.
- The user previously opened the Anatomy feature preview and confirmed that accepted Anatomy Marrow flow works beautifully.
- The temporary Anatomy-only `MARROW_RECORD` has now been replaced by the shared subject-indexed registry: `MARROW_RECORDS` → `MARROW_BY_SUBJECT` → `BANKS_BY_SUBJECT`. No second question engine was introduced.
- Registry-only refactor was fully build/browser verified before adding a second subject: Engineering Gate `34190814897`, full Android+PWA run `34190814843`.
- Current bank state in the latest candidate:
  - Anatomy → PrepLadder (1,068 / 50 topics) | Marrow (62 / 4 topics).
  - Physiology → PrepLadder (899 / 38 topics) | Marrow pilot (80 / 4 topics; Chapters 1–4).
  - Biochemistry → PrepLadder only.
- Physiology pilot data is normalized from the verified MARROW ED8 JSONL output, uses stable namespaced `marrow__PHYS_...` IDs, and is transported as 11 compressed/base64 shards with fail-closed byte/count/SHA-256 validation.
- Latest Physiology candidate verification: Engineering Gate `34191865093` success and full Android+PWA run `34191865094` success. The real browser test passed Physiology → bank selector → Marrow topic → question → Structured text explanation → fixed FSRS dock → PrepLadder regression; the side-by-side APK packaged and the feature preview deployed. Production promotion was skipped.
- **Status discipline:** Anatomy preview behavior is user/device-verified; the new Physiology pilot is build/browser verified but is **not yet user/device-verified or accepted**.
- Live feature preview: `https://feature-marrow-bank-pilot.nk-qbank.pages.dev`.
- Immediate next product checkpoint: user spot-checks the Physiology Marrow preview. If it passes, continue the same registry with a bounded Biochemistry pilot and then expand remaining verified Marrow chapters without changing navigation/engines.
- Canonical procedure, schema, integrity rules, CI gates, and pilot lessons are in `docs/MARROW_BANK_INTEGRATION.md`.

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
- The accepted Anatomy explanation grammar remains the reference presentation
  contract. Physiology currently uses the shared native Marrow structured
  explanation surface without changing the stored source wording.


## Topics page target — 2026-09-08

- Approved: mobile **journey/path** Topics UI with numbered left milestones on a soft curved/dashed path; refine Topics only, not the app shell.
- State grammar: **green milestone + right green check = completed**; **blue milestone + right blue pause = paused/in-progress**; **purple/lavender milestone = unattempted/not-started, with NO right-side hollow circle/hole/icon**.
- Keep **All / In Progress / Completed / Not Started**, search, index/list access, and the bottom **Continue Learning** direct-resume tray. Remove Free/lock/star/rating noise.
- Group topics under major syllabus indexes/section headers (Anatomy examples: **General Embryology**, **Histology**) instead of one flat list.
- Build one centralized editable topic→major-section taxonomy from topic names and, when needed, representative source/question content; ambiguous mappings stay flagged for review instead of guessed. Do not rewrite medical question content.
- Durable rationale/details: .project-memory/DECISIONS.md §16 and memory.md §7.

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

- No current Marrow architecture blocker is known. The registry and 80-question Physiology pilot are fully build/browser verified.
- The Physiology pilot still needs the user's physical preview spot-check before it can be labeled device-verified or accepted.
- After that check, continue with a bounded Marrow Biochemistry pilot through the same registry; do not create another subject-specific bank implementation.
- V11.6 `125d68b` remains the immutable accepted rollback checkpoint for unrelated platform work.

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
