# Topics + FSRS feature-branch handoff

## Current user verdict — 2026-09-08

The user physically opened the Marrow feature PWA and confirmed:

- the **recovered Topics journey UI is live and good**;
- the **fixed Continue Learning tray is live**;
- the **dedicated FSRS customization UI with explicit controls is good**;
- Marrow question integration is successful.

This supersedes the visual rejection recorded for commit `6ba7ebe`.
`docs/REJECTED_TOPICS_FSRS_HANDOFF.md` is historical failure evidence, not the
current verdict.

The remaining Topics defect is **taxonomy/grouping accuracy**, not the journey
visual design. See `docs/MARROW_TOPIC_INDEX_TAXONOMY.md`.

## Where the good implementation lives

Working/recovered code is on:

`feature/marrow-bank-pilot`

Key recovery lineage:
- `215d6954fd` — rebuild Topics journey and FSRS settings; restore sharp PWA zoom.
- `0c3bb8ef80` — harden settings tray and zoom toolbar.
- `eeab38f0f0` — keep floating controls viewport-bound and same-origin Anatomy PDF stream.
- `1c9826ae73` — browser-verification fix; green recovery checkpoint.

The current Marrow feature line includes those changes plus the 2,115-question
integration.

User-tested feature preview:
- mutable alias: `https://feature-marrow-bank-pilot.nk-qbank.pages.dev`
- immutable run-405 deployment: `https://2278b62b.nk-qbank.pages.dev`

## Why the “main PWA” did not show the changes

This is a **branch/deployment separation issue**, not evidence that the recovered
implementation failed.

- Git `main` is stale relative to the V11 product line and is not the correct
  implementation source.
- The older `v11.7-cross-device-pwa-sync` line does not contain the full recovered
  Topics fixed-tray/FSRS-settings implementation now present on the Marrow feature line.
- Marrow feature preview publishes intentionally **did not promote Cloudflare
  production**. Run 405 explicitly skipped the production-promotion step.
- Therefore the production/root PWA can legitimately lag behind the feature
  preview even while the feature implementation is correct.

Do not “fix” this by recreating the UI from memory. When the user later wants
consolidation/promotion, carry forward the exact feature-branch implementation
and its tests.

## Protected Topics behavior now

Preserve:
- left numbered journey milestones;
- soft curved/dashed path;
- completed green / in-progress blue / not-started lavender state grammar;
- no right-side hollow placeholder for not-started;
- restrained luminous glow;
- All / In Progress / Completed / Not Started;
- search;
- Topic Index;
- fixed viewport-visible Continue Learning tray above bottom navigation;
- bank/subject context;
- correct Back/history behavior.

Change next:
- **major-section taxonomy only**, using
  `docs/MARROW_TOPIC_INDEX_TAXONOMY.md`.

## Protected FSRS customization behavior now

Preserve:
- More → **FSRS customization** as a real destination;
- dedicated `#fsrs-settings` route;
- draft values;
- validation;
- explicit **Save changes** and **Cancel**;
- unsaved-change guard / Save and leave / Discard / Keep editing;
- existing FSRS scheduling semantics and immutable-attempt history;
- fixed practice recall dock.

Do not collapse it back into a bare `details/summary` section inside More.

## Consolidation rule for the main agent

Before merging/promoting anything:
1. start from the actual feature implementation, not stale `main`;
2. inspect diffs for the recovery commits and current branch;
3. preserve user-confirmed Topics/FSRS behavior exactly;
4. correct taxonomy separately;
5. run existing browser/product/FSRS/PWA/APK gates;
6. only promote production when the user explicitly asks.
