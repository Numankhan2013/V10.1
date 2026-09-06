# NK QBank

NK QBank is a private, offline-first Android medical question bank for personal MBBS study. It currently covers Anatomy, Physiology, and Biochemistry.

## Current baseline

- Physically accepted build: V11 Run 220
- Accepted product commit: \`73c04281696137fda712ae0b9b7079c9c4a15635\`
- Accepted lineage: \`v11-source-visuals\`
- Current hardening candidate: \`v11.1-engineering-foundation\`

The compact V10.3.11 question-first architecture remains the behavioral foundation. V11 adds accepted Home, review, and source-visual improvements without replacing that architecture.

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

## Build

Run **Build V11.5 Custom Study Modules APK** in GitHub Actions. A successful candidate produces:

- the debug APK
- \`NK-QBank-build-manifest.json\` containing the commit, file sizes, and SHA-256 fingerprints

CI success means **build-verified**, not device-verified. Install the candidate APK on the physical Android device before promoting it to the accepted baseline.

## Engineering rules

See [docs/ENGINEERING_BASELINE.md](docs/ENGINEERING_BASELINE.md). The core rule is: build forward from what works, and never trade an established study workflow for a new feature.
