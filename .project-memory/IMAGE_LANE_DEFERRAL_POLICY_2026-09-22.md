# Image lane deferral policy — 2026-09-22

Authoritative liveness correction for Marrow image automations.

## Problem fixed

Biochemistry `marrow__BIOCHEM_CH04_Q011:figure:1` was `REVIEW_REQUIRED` because the embedded PDF text was corrupt and authoritative rendered-page review was still needed. The prior handoff wording said not to skip the visual and kept Physiology paused until Biochemistry coverage recovery. Because the failed attempts occurred before any shared registry/progress mutation, this created an unnecessary global image-lane starvation condition.

## Governing rule

The authoritative rule is now the `Non-blocking REVIEW_REQUIRED deferral` section of `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md` on `main` (introduced by commit `c1e4d8157a96cea274dad5816fbb4efcf4fc7ee2`).

- `REVIEW_REQUIRED` remains unresolved and unreleased; fidelity is not weakened.
- A worker may make at most two bounded attempts for the same failure class in one run.
- If no shared `data/marrow/images/registry.json` / `progress.json` mutation exists, checkpoint the unresolved item and release the writer lane.
- The same subject retries its deferred first item on later recurrences.
- Other subjects may acquire the writer lane from the live canonical head while that deferred item waits.
- Historical wording such as “Physiology remains paused until Biochemistry recovery” is superseded as a global-lock instruction. It means only that Q11 remains first in Biochemistry's retry queue.
- A genuine lock requires live unreconciled shared-state mutation or another writer actively modifying the shared registry/progress state.

## Current Biochemistry Q11 disposition

`marrow__BIOCHEM_CH04_Q011:figure:1` stays `REVIEW_REQUIRED` and remains the first Biochemistry retry target. It does **not** own the global image writer lane merely because authoritative rendered-page review is pending.

## Automation behavior

Anatomy, Biochemistry and Physiology image workers must re-read the live canonical head and this handoff before mutation. If Q11 or any future source-review item is deferred without shared-state mutation, another subject can proceed immediately on its own next recurrence.

Production promotion remains prohibited.
