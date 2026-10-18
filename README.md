# NK QBank

A personal, offline-first study app for MBBS revision. It runs as an installable
web app (PWA) with optional sync between devices, and as an Android build of the
same app.

Covers preclinical subjects such as Anatomy, Physiology, Biochemistry and
Microbiology, plus organ-system blocks for clinical revision.

## Features

- Practice mode and timed CBT-style tests, with question navigation and full
  session review
- Spaced repetition powered by FSRS v6 — see [docs/FSRS.md](docs/FSRS.md)
- Custom study modules — see [docs/CUSTOM_STUDY_MODULES.md](docs/CUSTOM_STUDY_MODULES.md)
- Saved mocks, quick tests built from wrong or bookmarked questions, and
  performance analysis
- Personal notes, bookmarks and progress tracking per subject
- Light and dark themes, built for phones and tablets first
- Cross-device sync — see [docs/CROSS_DEVICE_PWA.md](docs/CROSS_DEVICE_PWA.md)

## How it works

- `app/src/main/assets/index.html` is the app shell; feature modules in
  `app/src/main/modules/` are inlined at build time.
- One stylesheet, `app/src/main/assets/app.css`.
- Study progress stays on the device in IndexedDB with automatic snapshots.
  Optional Firebase sync merges per-user records without overwriting newer
  data from another device.
- `tools/build_web_dist.py` builds the PWA into `build/web`, with the security
  headers defined in `tools/web_security_policy.py`.

## Build and verify

GitHub Actions builds and checks every push: fast source checks, then a full
build with phone and tablet browser tests and a preview deploy. Releases are
promoted manually.

Locally, `python3 tools/verify_local.py` runs the checks that apply. See
[docs/LOCAL_DEVELOPMENT.md](docs/LOCAL_DEVELOPMENT.md).

## Contributing

Engineering rules live in [docs/ENGINEERING_BASELINE.md](docs/ENGINEERING_BASELINE.md):
build forward from what works, and never trade an established study workflow
for a new feature. Project context for contributors starts in [`AGENTS.md`](AGENTS.md).

## Security

See [SECURITY.md](SECURITY.md) to report a vulnerability.
