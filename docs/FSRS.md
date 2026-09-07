# FSRS smart review

NK QBank includes a functional offline FSRS v6 review system in both the Android APK and the responsive website/PWA. Both targets use the same generated HTML and the same pinned scheduler assets, so review behavior stays consistent across platforms.

## Runtime behavior

- `ts-fsrs` 5.4.2 is vendored under `app/src/main/assets/vendor/ts-fsrs/` with its MIT license; the app never depends on a runtime CDN.
- The scheduler uses FSRS v6 with fuzz disabled for deterministic Android/PWA results, 90% desired retention, a 365-day maximum interval, and 10-minute learning and relearning steps.
- Existing `state.reviews` entries migrate to schema v2. A local migration backup is created, and each legacy due date is preserved until that card receives its first new FSRS rating.
- Immutable attempts are the replay and synchronization truth. Schema-v2 review cards are derived from sorted attempts, with audit snapshots on rated attempts.
- Practice ratings support Again, Hard, Good, and Easy. CBT answers map to binary Again/Good outcomes, and a pending Good rating can be recovered if a session closes between answer submission and navigation.
- The all-subject Today queue prioritizes due learning/relearning cards, applies the 150-card daily and 30-new-card limits, supports subject/topic filters, shows counts and estimates, and provides a seven-day forecast plus lapse attention flags.
- Settings change future ratings without rewriting past attempt history. Undo records a reversible event rather than deleting synchronized history.

## Build and verification

The deterministic pipeline installs FSRS after cross-device integration and verifies the generated source, web artifact, and packaged APK assets. `tools/test_fsrs_v1.py` covers migration, replay, ratings, queue caps and filters, preferences, undo, pending-rating recovery, and the offline vendor assets.

FSRS acceptance status as of 2026-09-07: the new APK was installed and confirmed working, and the website/PWA was opened and confirmed functional. The separate Firebase cross-device synchronization acceptance remains tracked in the project memory and deployment handoff.
