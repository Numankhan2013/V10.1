# NK QBank

NK QBank is a personal, offline-first medical question bank for MBBS study. It
ships as an installable web app (PWA) with optional cross-device sync, and as an
Android WebView build of the same app.

Subjects: Anatomy, Physiology, Biochemistry and Microbiology, with PrepLadder,
Marrow and UWorld banks where available.

## Status

- Accepted product commit: `125d68b` (V11.6 Content Quality, the rollback baseline)
- Current work and the latest production release are tracked in
  [`.project-memory/STATE.md`](.project-memory/STATE.md). The V11.7 deployment
  handoff that used to live here is recorded there.

## Project memory

Start with [`AGENTS.md`](AGENTS.md) and [`.project-memory/STATE.md`](.project-memory/STATE.md).
Canonical memory lives in `.project-memory/`; `python3 tools/verify_project_memory.py`
checks its integrity.

## Architecture

- `app/src/main/assets/index.html` is the app source; feature modules live in
  `app/src/main/modules/` and are inlined at build time.
- One stylesheet, `app/src/main/assets/app.css` (Geist design system).
- Study state is stored locally in IndexedDB with automatic snapshots; optional
  Firebase sync merges per-user records without overwriting newer device data.
- `tools/build_web_dist.py` produces the PWA in `build/web`, including the
  security headers defined in `tools/web_security_policy.py`.

## Features

- Practice and Timed CBT, with question navigation, session review and Review Solutions
- FSRS v6 smart review — see [docs/FSRS.md](docs/FSRS.md)
- Custom study modules — see [docs/CUSTOM_STUDY_MODULES.md](docs/CUSTOM_STUDY_MODULES.md)
- Saved mocks, quick tests from wrong or bookmarked questions, and test analysis
- Cross-device PWA sync — see [docs/CROSS_DEVICE_PWA.md](docs/CROSS_DEVICE_PWA.md)
- Source-faithful explanation and figure rendering

## Build and verify

GitHub Actions builds and verifies every push:

- **NK QBank Engineering Gate** runs the fast source contracts.
- **Build and verify PWA (optional APK)** builds the web app, runs the phone and
  tablet browser suite, and deploys a preview. Production promotion is a manual
  dispatch of that workflow with an exact release SHA.

CI success means build-verified, not device-verified.

Locally, `python3 tools/verify_local.py` runs the applicable checks. See
[docs/LOCAL_DEVELOPMENT.md](docs/LOCAL_DEVELOPMENT.md).

## Engineering rules

See [docs/ENGINEERING_BASELINE.md](docs/ENGINEERING_BASELINE.md). Build forward from
what works, and never trade an established study workflow for a new feature.

## Security

See [SECURITY.md](SECURITY.md) for how to report a vulnerability.
