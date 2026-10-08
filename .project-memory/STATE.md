# STATE.md — Current Project State and Handoff

> Operational state only. Resolve live branch/HEAD and CI from Git before acting. History lives in `SESSION_LOG.md`; the pre-cleanup 2026-10-05 snapshot of this file is `archive/STATE_2026-10-05_pre-cleanup.md`.

## Current release (verified 2026-10-05, refreshed 2026-10-08)

- Last substantive product commit on `main`: `d2e629b` (My UWorld Home + Biostatistics Block 2), promoted by `07f6e8c` ([approved-production]). `main` is the production trunk and serves the canonical root https://nk-qbank.pages.dev. Resolve live HEAD from Git.
- Web-first: default builds are PWA only; APK/emulator only with `build_apk=true` (existing APKs retained, size optimization deferred).
- Home and the study library expose one **My UWorld** entry; collections, blocks and progress live in the library. Registry: **388 UWorld questions / 12 topics / 6 collections** (Biochemistry, Poisoning, Ophthalmology, two reproductive sets, Biostatistics). Biostatistics has 60 questions (all 40 Block 1 + first 20 Block 2); **61 complete source items remain queued**.
- Reports: `docs/UWORLD_BLOCK2_HOME_2026-10-05.md`, `docs/UWORLD_HYGIENE_BIOSTATISTICS_2026-10-04.md`, `docs/UWORLD_BIOCHEMISTRY_PILOT.md`, `docs/UWORLD_OPHTHALMOLOGY_COLLECTION.md`, `docs/UWORLD_REPRODUCTIVE_BATCH.md`.
- Source rules for UWorld: original JSONL/PDF/keys/percentages immutable; reviewed documents own runtime/search prose; missing stats stay null; essential absent exhibits are unscored references.

## Verification labels (never conflate)

- **build-verified:** local checks + full Ubuntu CI (Engineering gate + PWA build, package/media/offline checks) pass.
- **device-verified:** installed/used on a physical device and confirmed by the user.
- **accepted baseline:** explicit user approval. Accepted product commit: `125d68b`. Rollback baseline = **V11.6 Content Quality**; the Continue Practice contract below is separately user/device accepted.
- Everything since V11.6 (V11.7 sync, UWorld collections, Back-warning, timed-test recovery, Revision hub, Insights) is build-verified and/or hosted-verified, with many items user-previewed, but **not physically accepted** unless stated.

## Product architecture to preserve

- Shared bank architecture: `MARROW_RECORDS → MARROW_BY_SUBJECT → BANKS_BY_SUBJECT`. Do not fork Practice, CBT, Review Solutions, FSRS, sync, modules, persistence, analytics or navigation by subject/bank.
- Primary navigation: **Home · Revision · Tests · Insights · More**; FSRS lives inside Revision.
- Study hierarchy: My Subjects → subject → bank chooser → Topics journey → topic → Practice/Topic Test; My UWorld library sits below My Subjects.
- FSRS schedules every answered question. Pause commits answered work only; final submission adds remaining unanswered session IDs as skipped; questions outside a submitted session stay unseen.
- Practice mistakes track unresolved ordinary misses only; FSRS-only lapses never create them; a correct answer from any flow resolves one.

## Accepted Practice / Continue Practice contract (user/device verified)

- Practice footer = Previous + Next only. Header grid icon and end-of-session boundary open the same final review grid (Pause + Submit only). Do not restore the intermediate navigator, `Back to question` or `Review unanswered`.
- Pause keeps the same session ID, full ordered `sessionQuestionIds`, index, answers, timing; it never marks the current question skipped. Home Continue Practice restores the complete list; a multi-question session must never collapse to `1 / 1` (rebuild from `sessionQuestionIds`).
- Special modes (CBT, Review, Wrong/Bookmarks, FSRS, Custom Study Modules) are outside this override. Docs: `PRACTICE_FLOW_POSTMORTEM_2026-09-12.md`, `CONTINUE_PRACTICE_HANDOFF.md`.
- **Mandatory regression sequence** for any change touching Home, Practice, session persistence, sync, navigation, final review, FSRS injection or build transforms: start a real multi-question Practice session, answer several leaving one unanswered, open the final grid and Pause, use Home Continue Practice, verify same session ID, ordered IDs, index, preserved progress, no `1 / 1`, no Pause-as-Skip.

## Content invariants

- Structured explanation tables: non-empty source headers/rows must render as learner-visible cells in order; `[object Object]` is a hard failure; browser checks assert cell content.
- Matching/list questions render as semantic tables through the shared layer; fragments never become choices; incomplete answer contracts fail closed. Detail: `MATCHING_TABLE_ARCHITECTURE_HANDOFF_2026-09-14.md`.
- Complete canonical Marrow ED8: Anatomy 1,115 / Biochemistry 582 / Physiology 1,014 = **2,711 questions / 134 topics**; raw source immutable. Explanations: **2,688 enhanced / 23 deferred** (incomplete source). Policy: `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md`; consolidation: `FULL_CORPUS_CONSOLIDATION.md`.
- Learner-content hygiene and completeness ledgers (`data/question_completeness_reviews_v1.json`, 254 reviewed, 33 gated underdetermined) are protected; see `docs/QUESTION_COMPLETENESS_FINAL_PASS.md`.
- Image lane: 1,502 references / 1,421 released / 79 invalid / 2 archival holds. Source-visual behavior (fullscreen zoom/pan, offline bytes) is protected.

## Anti-fragmentation rules

- Explanation and image work build from `feature/marrow-canonical-full-current` / the complete 2,711 corpus; re-read live commit and registry fingerprints first. Stale PRs/branches are evidence, not locks.
- Reconcile verified work into canonical before another conflicting batch in the same lane. Accepted product/UI fixes are protected.
- Image automation: `IMAGE_AUTOMATION_READY_2026-09-20.md`. The percentage-correct pilot branch is not integrated and not an image base.
- `feature/marrow-canonical-full-current` still needs fast-forward alignment to current `main` before further content-lane work.

## Known problems / cautions

- PrepLadder source visuals: technical gates green but **422 audit entries need manual source comparison**; not release-certified (`PREPLADDER_VISUAL_VERIFICATION_2026-09-16.md`).
- Four PrepLadder records stay non-answerable: `anatomy-22-4`, `physiology-23-38`, `physiology-24-6`, `physiology-33-33`. 23 Marrow questions stay gated; two archival image gaps remain.
- Physical-device acceptance is outstanding for V11.7 Android in-place upgrade and Android↔iPad sync (offline/reconnect, force-close, sign-out/in), Back-warning, timed-test recovery, UWorld collections and haptics.
- Axonal-transport and other source-backed structured presentations still need user physical review.
- Production promotion needs explicit user authorization each time.

## Next step

1. Source-review the remaining 61 Biostatistics items in bounded 10-question batches (native review, source pins, immutable originals); other queued UWorld packages follow.
2. Run one physical-device acceptance pass (Android in-place APK + iPad/PWA sync) to convert build-verified items to accepted.
3. Keep memory current: run `python3 tools/verify_project_memory.py` before committing.

## Memory pointers

- Roadmap/decisions/history: `ROADMAP.md`, `DECISIONS.md`, `SESSION_LOG.md`; deployment handoff for Firebase/Cloudflare/R2: `archive/V11.7_deployment_handoff_2026-09-07.md`.
- Legacy long-form note: `memory.md` (preserved, do not fork knowledge).
