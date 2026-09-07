# STATE.md — Current Project State and Handoff

> Keep concise and current. History goes in `SESSION_LOG.md`, durable reasoning
> in `DECISIONS.md`, and future work in `ROADMAP.md`.

## Repo / branch

- Repo: `Numankhan2013/V10.1` (private)
- Active branch: `v11.5-custom-study-modules`
- Resolve live branch/HEAD with `git branch --show-current` and
  `git rev-parse HEAD`; never hardcode a self-staling current-HEAD value here.
- Last substantive V11.5 product commit: `f13d12f` (`Label V11.5 APK artifact`),
  followed by harness-neutral memory-only commits; inspect live Git for the
  current tip.
- Parent lineage: `v11.4-whole-app-vision` fix `9e6abc7`.
- `main` (`8bc0be4`) is stale and must not be used as the V11 baseline.

## Verification and accepted baseline

- Accepted baseline: **V11.5 Custom Study Modules**. The user physically tested
  the APK and said it “works beautifully,” with no questions about the feature.
- Accepted product commit: `f13d12f`; canonical APK run: `34049637559`.
- Latest V11.5 memory-head build `34051356682` and Engineering Gate
  `34051356708` both passed at `e6a2fc7`.
- Separate branch `v11.6-content-quality`, commit `125d68b`: Engineering Gate
  `34050921166` and full packaged build `34050921180` passed. It improves
  comparison/table takeaways and removes PrepLadder/page metadata from 78 of
  719 audited stems. It is build-verified, not yet device-verified or accepted.

Labels are strict: implemented ≠ build-verified ≠ device-verified ≠ accepted
baseline. Only explicit user physical-device approval promotes a candidate.

## What currently works (V11.5 device-verified and accepted)

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

- V11.6 content quality is on a separate branch forked from `f13d12f`; it does
  not contain the later memory commits. Preserve both histories when
  consolidating—do not overwrite either branch.
- Root `AGENTS.md` placement is correct, but no filename can force every unknown
  harness to load it. Thin common-harness adapters and
  `tools/verify_project_memory.py` reduce discovery and drift risk.
- Large binaries (three PDFs, ~420 PNGs, ~6 MB source app) make full clones slow;
  prefer targeted inspection or partial clones when appropriate.
- Source visual and protected session/review infrastructure must not be changed
  casually during unrelated work.

## Next step

1. Physically test V11.6, especially table takeaways and cleaned stems; accept
   only after explicit user confirmation.
2. Consolidate V11.6 with this memory-system lineage without losing either set
   of commits, then continue R1 gold-standard question-screen refinement.
3. After substantial work, refresh this handoff, append `SESSION_LOG.md`, and
   run `python3 tools/verify_project_memory.py`.
