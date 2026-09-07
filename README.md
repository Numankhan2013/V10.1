# NK QBank

NK QBank is a private, offline-first Android medical question bank for personal MBBS study. It currently covers Anatomy, Physiology, and Biochemistry.

## Current baseline

- Physically accepted build: V11.6 Content Quality
- Accepted product commit: `125d68b`
- Accepted APK run: `34050921180`
- Current implementation branch: `v11.7-cross-device-pwa-sync` (not yet build/device verified)

The compact V10.3.11 question-first architecture remains the behavioral foundation. V11 adds accepted Home, review, and source-visual improvements without replacing that architecture.

## Project memory

Start with [`AGENTS.md`](AGENTS.md) and [`.project-memory/STATE.md`](.project-memory/STATE.md). Canonical harness-neutral memory lives in `.project-memory/`; thin adapters cover common agent conventions, and `python3 tools/verify_project_memory.py` checks its integrity.

## Architecture

- Android WebView shell
- offline HTML/CSS/JavaScript application
- bundled subject data and source PDFs
- local study-state persistence
- native Android PDF rendering where useful
- deterministic GitHub Actions APK generation

## Protected workflows

Practice, Timed CBT, question navigation, session review, Review Solutions, subject switching, persistence, and source-faithful visual/explanation rendering are protected by build-time regression contracts.

## Custom Study Modules

Reusable study sets can combine subjects and topics with Unattempted, Wrong,
Bookmarked, or Mixed question pools. Their question IDs and progress persist
locally, and module answers feed the existing history, revision, and Insights
systems. See [docs/CUSTOM_STUDY_MODULES.md](docs/CUSTOM_STUDY_MODULES.md).

## Question content quality

Question stems are sanitized centrally to remove extraction-source footers. Key
takeaways preserve table-column ownership so comparison facts are not merged.
The behavior is protected by a full-dataset contamination audit.

## Cross-device PWA

V11.7 preserves the Android app while adding an installable responsive PWA and
optional Firebase synchronization. See [docs/CROSS_DEVICE_PWA.md](docs/CROSS_DEVICE_PWA.md)
for the data model, migration safeguards, configuration, deployment, and tests.

## Build

Run **Build V11.7 Android + PWA** in GitHub Actions. A successful candidate produces:

- the debug APK
- \`NK-QBank-build-manifest.json\` containing the commit, file sizes, and SHA-256 fingerprints

CI success means **build-verified**, not device-verified. Install the candidate APK on the physical Android device before promoting it to the accepted baseline.

## Engineering rules

See [docs/ENGINEERING_BASELINE.md](docs/ENGINEERING_BASELINE.md). The core rule is: build forward from what works, and never trade an established study workflow for a new feature.
