---
version: 1
slug: "app-src-main-assets-index-html-tests"
primary_target: "app/src/main/assets/index.html#tests"
related_targets: []
---

# Tests page (route `tests`)

Mode: operate. World: existing Geist monochrome (fixed), Phosphor icons, light + dark.

## Locked structure — "Mock shelf + Build"
1. Timed resume card stays first when a test is in progress.
2. Saved mocks: horizontal snap shelf of cards (name, Qs · min · subjects, last score or New). Newest/most recent first card inverted (ink fill). "See all" opens the existing full list/search. Tapping a card opens the existing mock details sheet (nkMockOpen). Empty: a quiet one-line hint that mocks are saved from the builder.
3. Score trend: bars of the last up-to-10 completed test percentages, oldest→newest, with average. Hidden until ≥2 completed tests.
4. Recent: up to 5 completed tests (testRow behaviour: tap opens review); older behind "All N".
5. Floating "Build a test" pill bottom-right above the tab bar (openMultiSubjectTestBuilder). Quick test (wrong / bookmarked) launches from a secondary row that opens a bottom sheet with source + count, then Start (nkSetTestSource/nkSetTestCount/nkStartConfiguredTest).

## Rules
- No new colour; ink/paper/gray tokens only. Tabular numerals for scores.
- 44px minimum targets; 16px gutters; shelf scrolls without page horizontal scroll.
- Keep every existing function reachable; no new features beyond the above.
