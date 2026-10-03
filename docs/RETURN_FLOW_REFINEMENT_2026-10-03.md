# Study return-flow refinement — 2026-10-03

This bounded follow-up preserves the user-approved warm-paper, violet/amber palette, two-tone icons and immediate answer interactions. The certified previous batch remains at https://cd257e5f.nk-qbank.pages.dev. No production promotion or physical-device acceptance is implied.

## Audit and direction

The installed official Impeccable skill-v4.5.0 guided the audit, hardening and final craft checks. Its context was loaded once earlier in this session; the committed Operate/preservation direction governs this batch. Real phone/tablet screenshots and working controls established the following defects before editing:

- Revision → View all bookmarks → Open question returned analysis to Topics, discarded the search filter, and generated an unrelated normal-Practice checkpoint.
- Checkpoint-only recovery of Search practice lost its original return destination although answers, membership and position survived.
- Submitting an empty test name silently did nothing. The 13px field lacked inline validation; failed saves did not restore the previous `updatedAt` metadata or explain recovery.
- Keyboard removal of a saved mock lost focus to the page body; its target was only36px wide.

The direction is continuity and explicit state feedback. No new animation, artificial delay, icon dependency, storage schema, confirmation modal or architectural layer was introduced. The existing question engine, FSRS attempt source, review queues, scores, source content, haptics and production release remain protected.

## Changes

Revision browse retains separate in-memory search queries for Mistakes and Bookmarks, resets them on account change, and applies filtering during rendering. Search uses the shared drawn icon and16px input. Individual browse sessions use the existing wrong/bookmarked context, carry their original browse destination and return through the normal navigation dispatcher. One-off reviews no longer become ordinary chapter checkpoints. Timed-test guards and revision queue sampling are unchanged.

Existing checkpoint context optionally stores a return hint for non-default destinations. Recovery accepts the existing Notes, Search, Home and Study Library routes, with Topics as the legacy/unknown fallback. Ordinary chapter checkpoint shape, ordered membership, position, submitted flags, answer/timing data and pending FSRS ratings are unchanged. No migration or new persistent store is needed.

Test rename now has an inline required-name error, keeps the typed value after failed persistence, and rolls back both title and `updatedAt`. Successful save restores focus to Rename. Its field and primary Save button share the approved palette and typography. Saved-mock removal keeps its immediate behavior while restoring keyboard focus to the next mock or the page heading, preserving scroll and announcing success. Its target is44×44px.

## Validation

Before publishing,93 local source/behavior/syntax checks passed. Expanded source tests protect legacy recovery, all allowed/unknown origin hints,20-question membership/position/answers/timing/ratings, durable context normalization, account fences, timed-test guards, blank-name no-write behavior, failed-save metadata rollback/retry and failed mock-removal rollback.

Supplementary return-flow checks also passed at320/1194px; earlier study-flow, Revision, interaction/reduced-motion and visual regressions passed.

The permanent generated-app `verify_return_flow_browser.py` exercises genuine Revision entry paths at390/820px, bookmark and mistake round-trips, checkpoint-only recovery, legacy fallback, rename validation/failure/retry and keyboard removal including the final item. It runs in the full build workflow beside the earlier study-flow, visual and interaction checks. Phone/tablet screenshots show the inline error and retained filtered list fitting the established identity. The focused Impeccable detector reported no findings for the five changed UI/core files; this supplements visual judgment rather than replacing it.

Full generated-app/PWA/APK/Android and exact hosted verification are pending for this candidate. Physical phone/tablet and actual haptic acceptance remain separate.
