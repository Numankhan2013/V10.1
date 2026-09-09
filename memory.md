# Latest feature-PWA validation and next-work handoff — 2026-09-08

2026-09-09 image-phase checkpoint: work is paused at the user's usage-limit request
on `feature/marrow-image-pipeline`. Initial image pipeline commit `07ee53d` passed
full CI `34311877059`; the expanded 18-asset pilot is saved locally and still needs
its own CI/browser/package verification. A known duplicate-owner gate issue for
the read-only image package checker must be fixed first. `.project-memory/STATE.md`
contains the authoritative resume instructions. Production was not promoted.

Accepted rollback baseline: V11.6 `125d68b`.

The user physically opened the Marrow feature PWA and confirmed: **Marrow question
integration is successful; the recovered Topics journey/fixed Continue Learning
tray is good; the dedicated FSRS customization page/buttons are good.**

These good surfaces live on `feature/marrow-bank-pilot`. Their absence from the
older “main PWA” is expected from branch/deployment separation: Git `main` is
stale and run 405 did not promote Cloudflare production. Do not recreate the UI
from scratch; preserve the feature implementation and use
`docs/TOPICS_FSRS_FEATURE_HANDOFF.md`.

The next Topics defect is taxonomy only. The visual design stays. Canonical user
index order and mapping guidance are in
`docs/MARROW_TOPIC_INDEX_TAXONOMY.md`.

The next Marrow quality phase, when explicitly started, is explanation
fine-tuning. Raw ED8 transcription remains immutable; cleanup/reconstruction,
Key Takeaway, selective emphasis, tables and concise wrong-option rationales must
live in a separate auditable layer. Use the approved 142-question grammar and
`docs/MARROW_EXPLANATION_FINE_TUNING.md`.

No implementation was requested in this handoff. V11.6 `125d68b` remains the
accepted rollback baseline.

# Latest Marrow Phase A handoff — 2026-09-08

**Accepted baseline remains V11.6 `125d68b`; the expanded Marrow candidate is not yet accepted.**
Active branch: `feature/marrow-bank-pilot`.

The candidate now contains **2,115 Marrow questions** through the existing
shared bank registry: Anatomy 819/48, Biochemistry 543/26, Physiology 753/33.
Initial ingestion is deliberately source-faithful first; explanation redesign
for newly added questions is deferred. The prior approved 62 Anatomy + 80
Physiology enhanced subset remains intact.

Integration checkpoint `bc500234` passed Engineering Gate `34245190588`
and full Android+PWA run `34245190771`. The immediately prior full run
`34244982211` failed only because its browser test still expected
Biochemistry to be PrepLadder-only; the intended new Marrow Biochemistry bank
made that assertion obsolete. The updated browser test passed all three banks.
The exact expanded candidate was subsequently republished in full run
`34246876973` / run 405, which passed and deployed only the isolated feature
preview. Live alias: `https://feature-marrow-bank-pilot.nk-qbank.pages.dev`;
immutable deployment: `https://2278b62b.nk-qbank.pages.dev`. Production
promotion was skipped. The expanded candidate remains build/browser verified,
not device-verified or accepted.

Permanent lessons: keep Marrow as a data/source dimension, never a second study
engine; use manifest/hash-verified shards rather than oversized writes; keep
stored source text separate from explanation augmentation; and update tests when
the deliberate bank matrix changes instead of treating the intended change as
a regression.

# NK QBank — Project Memory / Continuity

**Updated:** 2026-09-08
**Current accepted baseline:** V11.6 Content Quality (`125d68b`, run `34050921180`, physically tested and user-confirmed)
**Repository:** `Numankhan2013/V10.1`  
**Active branch:** `feature/marrow-bank-pilot`

## Current candidate — V11.7 Cross-device PWA + Sync

Branch: `v11.7-cross-device-pwa-sync`, based on accepted V11.6 and merged with
the harness-neutral project-memory lineage.

The goal is to preserve the accepted Android APK while adding a first-class
responsive iPad/web PWA and conflict-safe Firebase synchronization. It is build-verified at `1b1fc9f` (Engineering `34076883867`, full Android/PWA
run `34076883874`) but is not device-verified or accepted.

## 1. Project identity and north star

NK QBank is a personal Android medical QBank intended to become a dependable daily study tool.

The current phase has changed: **core/basic functionality is now considered complete and working without known regression.** Development should therefore move from feature rescue/build-out toward careful refinement, polish, consistency, usability, and engineering hardening.

**Motto:** **We do not break anything while we build something.**

Engineering loop:

> Inspect → implement narrowly → build → verify → inspect packaged APK → fix → rebuild → verify again → physical-device test.

Physical Android-device behavior is the final authority. CI success or static inspection alone is never sufficient to call a UI change accepted.

The user's preference is **more building and less narrating**. Execute safe, concrete work rather than producing long speculative plans.

---

## 2. Current accepted state — V11.6 Content Quality

V11.6 is the current accepted baseline. The user physically tested and accepted
the APK. Accepted product commit: `125d68b`; canonical successful APK run:
`34050921180`. It includes V11.5 Custom Study Modules plus comparison-aware key
takeaways and centralized removal of leaked source metadata from question stems.

Run 220 remains the earlier foundational acceptance record:
- Run number: `220`
- Run ID: `34011265432`
- Head commit: `73c04281696137fda712ae0b9b7079c9c4a15635`
- Commit message: `Build Home three-action refinement`
- CI conclusion: `success`
- Historical branch: `v11-source-visuals`

The workflow passed:
- source/visual generation
- Home V4/V5 transformations
- streak/header transformation
- Home three-action hierarchy
- CBT boundary/review flow
- review footer
- Review Solutions grid
- final JS syntax validation
- CBT regression guardrails
- final generated-app verification
- Gradle build
- packaged APK verification
- artifact upload

### User-confirmed working areas

- Practice sessions.
- Timed CBT.
- Final-question boundary opens the session-review grid rather than leaving a persistent end-of-session toast.
- Session-review grid with answered/unanswered state and question jumping.
- Submit/Finish flow.
- Test Analysis / Review Solutions.
- Review Solutions Previous/Next.
- Review Solutions question navigator/grid and End Review flow.
- Home.
- Topics.
- Tests.
- Insights.
- More.
- Subject switching.
- Scroll reset.
- Persistence/state behavior.
- Source-visual question rendering.
- Source-visual full-screen viewing, zoom and pan.
- Biochemistry renderer.
- Physiology source-PDF visual/explanation pipeline.
- Anatomy source visuals already integrated.
- Home streak.
- Home-only removal of the old QBank top header/logo.

**Important:** The user has physically tested the latest build and reported that it works. Do not claim any additional physical behavior beyond what the user has confirmed.

---

## 3. Trusted architectural baseline

The compact V10.3.11 question-first product architecture remains the behavioral/design baseline.

A previous V11 clean-foundation attempt was rejected because it introduced:
- duplicate persistent navigation
- excessive chrome
- a replacement application shell
- loss of the compact question-first hierarchy
- visual layering inconsistent with the proven product

Do **not** revive that architecture.

Do not perform a wholesale native Compose rewrite.

Current broad architecture:
- Android wrapper
- WebView
- monolithic `app/src/main/assets/index.html`
- local/bundled data
- localStorage persistence
- native Android code only where genuinely useful
- offline-first core QBank operation
- GitHub Actions for deterministic APK generation

Long-term native evolution may happen component-by-component, but it is not the current task.

---

## 4. Source Visual Renderer — frozen foundation

The source visual system is effectively complete and should be treated as protected infrastructure.

Original subject PDFs remain the source of truth.

Current derived display assets:
- native embedded raster figures extracted at native resolution
- tightly cropped to meaningful figure content
- saved as lossless PNGs
- rendered responsively
- source-PDF fallback remains available

Current coverage:
- Anatomy: 297 mapped questions
- Physiology: 62 mapped questions
- Biochemistry: 51 mapped questions
- 420 source-visual PNGs retained in the packaged APK

Rules:
- exact normalized question-stem matching
- no fuzzy cross-subject image assignment
- subject-specific PDFs only
- no heuristic “Question N has image” logic
- preserve aspect ratio
- never crop medically meaningful content
- full-screen viewer with zoom/pan remains protected
- do not alter this pipeline during unrelated UI work

Source visual assets are a display cache; the original PDFs remain authoritative.

---

## 5. Subject/source rules

### Physiology
Authoritative source:
`Physiology Prepladder Version X Qbank yw.pdf`

Repository/runtime asset:
`app/src/main/assets/Physiology_QBank_Source.pdf`

The PDF contains the genuine tables, diagrams, graphs, figures, and structured explanations.

Use source-PDF rendering for Physiology where appropriate.

Do not reconstruct flattened explanations heuristically into fake tables/bullets.

### Biochemistry
The existing renderer is known-good and must remain isolated.

Do not globally replace the Biochemistry renderer.

### Anatomy
Anatomy is integrated and source visuals are working.

Further Anatomy explanation/content refinement can happen later, but should be driven by inspection of the actual source material rather than heuristic reconstruction.

---

## 6. Home — current state

Home V8/V4 composition is accepted.

Core Home principles:
- one cohesive application surface rather than floating card stacks
- compact identity/header
- Today’s Focus as the primary command area
- Subjects as the central study library
- compact progress snapshot
- quick access
- performance/recent sections
- clear next action

### Home streak

The streak is now present below the greeting and is owned by Home only.

The old global streak injector is removed.

Current implementation uses the existing canonical streak/state functions rather than creating duplicate persistence.

The user has specifically refined the desired aesthetic:
- streak should align with the rectangular/chiseled geometry of the rest of Home
- avoid unnecessary rounded-card treatment
- avoid unexplained empty space
- keep it visually integrated with the Home axis
- subtle animation/graphic motion is acceptable when it improves polish and remains restrained

### Home action hierarchy

The intended Today’s Focus action order is:

1. **Continue Practice**
2. **Practice 20 Random Questions**
3. **Timed CBT**

`Continue Practice` should not sit beside `Good morning`; it belongs inside Today’s Focus with the other study actions.

All three actions should be visually distinct while remaining part of the same cohesive system.

Do not make them three visually unrelated buttons. Distinction should come from hierarchy, fill/border treatment, iconography, and restrained semantic color use.

### Home top header

The old QBank top logo/header was removed from Home only.

Do not remove or alter shared navigation/chrome on other routes unless explicitly requested.

---

## 7. Topics / navigation

Topics V2 behavior remains the working foundation, but the user has now approved
a specific visual/hierarchy refinement for the Topics surface.

### Approved Topics direction — 2026-09-08

Use a mobile **learning-journey/path** composition:
- numbered topic milestones/serials on the left
- a soft curved/dashed connector path between milestones
- one aligned topic card per milestone
- green milestone hue + right green check for completed
- blue milestone hue + right blue pause for paused/in-progress
- subtle purple/lavender milestone hue for unattempted/not-started
- **no right-side hollow circle/hole/placeholder on unattempted cards**
- concise topic title + progress/count text
- top filters: **All / In Progress / Completed / Not Started**
- keep search and the index/list affordance
- bottom **Continue Learning** tray for direct resume/jump-in
- remove Free/locked/star/rating/paywall metadata from the Topics page

The topic list also needs a real syllabus hierarchy instead of remaining flat.
Topics should render beneath major subject section headers. Anatomy examples
include **General Embryology** and **Histology**.

There is no complete authoritative parent-group mapping already supplied for
every existing topic. The implementing agent should create one centralized,
explicit, editable topic→major-section taxonomy by inspecting current topic
names and, where needed, representative question/source content. This is a
presentation/navigation classification only: do not rewrite medical source
content or duplicate the question engine. Ambiguous classifications should be
marked for review rather than silently assigned arbitrarily.

Preserve the existing working principles:
- compact subject selector
- search/filter
- accurate topic counts
- progress/percentage
- direct chapter/topic opening
- unified subject navigation
- reliable same-route scroll reset

Do not replace this with a new shell.

---

## 8. CBT / Review architecture

Current session-review system is protected.

### Active sessions

Final question → open session-review navigator.

Navigator:
- answered/unanswered state
- question jumping
- review unanswered
- Submit Test / Finish Session

The persistent “End of session reached.” toast regression is fixed.

Toast behavior is singleton/transient rather than stacking.

### Review Solutions

Review Solutions is now considered working and protected.

Current behavior:
- completed test opens review
- question-first review interface
- Previous/Next fixed footer
- question grid/navigator
- jump between reviewed questions
- End Review
- ending review returns to the originating Test Analysis/result view
- source-PDF-based explanations where applicable

Do not regress or replace the existing navigator with a second implementation.

---

## 9. Workflow / build hardening

`.github/workflows/build-apk.yml` currently applies deterministic transformations and then verifies the packaged result.

Important order:
1. Source/CBT/UI transformations.
2. Home V4/V5.
3. Remove legacy streak layer.
4. Home streak/header.
5. Home three-action hierarchy.
6. CBT end-of-session behavior.
7. Review footer.
8. Review Solutions grid.
9. WebView syntax repair after all transformations.
10. Final inline-JS syntax validation.
11. CBT regression guardrails.
12. Final generated-app checks.
13. Gradle build.
14. Packaged APK verification.
15. Artifact upload.

Packaged verification must continue to protect:
- Home V4/V5 markers
- Topics V2
- subject navigation/scroll reset
- no legacy streak injector
- CBT session-review
- fixed review footer
- Review Solutions grid
- valid packaged JS
- source visual assets (currently at least 400; expected 420)
- APK ZIP integrity

The final packaged APK matters more than source-only checks.

---

## 10. Historical failures — permanent lessons

### Failed V11 shell
Do not return to the duplicate-navigation/excessive-chrome shell.

### Run 170
A transformation accidentally restored old Home UI. Recovery required restoring the exact accepted Home composition rather than approximating it.

### WebView syntax failures
Home transformations previously introduced malformed inline JS after an earlier syntax check.

Therefore:
- syntax repair/check must occur after all transformations
- packaged `index.html` must also be syntax checked

### Review footer regression
Generic CSS once clipped/misaligned Review Solutions Previous/Next.

Keep review footer styling isolated.

### Persistent end-session toast
Do not reintroduce persistent boundary messaging. The final-question boundary is a navigator transition.

### Heuristic Physiology explanation reconstruction
Rejected because it produced semantically unreliable and visually poor results.

Source PDFs remain authoritative.

---

## 11. New development phase — Refinement, not feature rescue

**Core features are now done.** The next work should be judged by whether it makes the existing product:
- clearer
- faster
- more coherent
- more professional
- more visually consistent
- easier to study with
- more robust

Avoid adding complexity merely to make the version number larger.

### Refinement roadmap

#### Phase R1 — Gold-standard Question Screen
Highest priority.

Refine:
- typography rhythm
- question/stem density
- option spacing
- selected/correct/wrong states
- bookmark/grid affordances
- explanation hierarchy
- source visual placement
- long explanation behavior
- image/text relationship
- sticky Previous/Next
- mobile readability
- reduced visual noise

The question screen remains the measuring stick for product quality.

#### Phase R2 — Home polish
Refine:
- three-action hierarchy
- streak geometry
- spacing rhythm
- section alignment
- subject rows
- progress indicators
- empty states
- responsive behavior
- subtle transitions

Keep the current Home architecture.

#### Phase R3 — Review consistency
Make Practice Review, CBT Review, and Test Review feel like one system:
- same header hierarchy
- same grid language
- same navigation behavior
- same state indicators
- same explanation surface
- no duplicate implementations

#### Phase R4 — Daily Study Loop
Make:
`Home → Continue/Practice → Review → Return Home`
feel deliberate and frictionless.

Improve:
- Continue Practice
- unfinished-session recovery
- Wrong Questions
- Due Review
- Bookmarks
- post-session next action

Do not over-automate or clutter the Home screen.

#### Phase R5 — Study Intelligence
Build carefully:
- robust Wrong Questions
- persistent Bookmarks
- restrained Spaced Review foundation
- actionable weak-topic signals

The goal is useful prioritization, not gamification overload.

#### Phase R6 — Insights / Analytics
Make analytics answer:
- What am I weak at?
- What should I study next?
- How much have I done?
- Is accuracy improving?
- Where am I wasting time?

Prefer actionable summaries over decorative graphs.

#### Phase R7 — Test System refinement
After review stability:
- test builder clarity
- topic selection
- question count
- timing
- history
- results
- unanswered review
- analysis

#### Phase R8 — Engineering hardening
Introduce regression protection:
- golden/screenshot checks for Home
- Topics
- question screen
- image questions
- long explanations
- Practice
- CBT
- Review
- Review Grid
- Insights

Improve state/data separation incrementally.

#### Phase R9 — Final visual system
Only after behavior is stable:
- spacing tokens
- typography tokens
- icon consistency
- border/radius consistency
- shadow discipline
- transitions
- accessibility
- adaptive/tablet layouts

---

## 12. Design language

Figma remains a visual foundation, not an architectural mandate.

Figma file:
**QBank V11 — Design Foundation**

Design principle:
**Every screen should make the next useful learning action obvious.**

Current intended palette:
- Primary cyan: `#3FCFE8`
- Deep companion: `#135262`
- Ink: `#171A2B`
- Muted: `#6F7385`
- Success: `#159A68`
- Error: `#D64B58`
- Info: `#3F7BE8`
- Amber: `#D98B16`
- Background: approximately `#F6F7FB`
- Surface: `#FFFFFF`
- Line: approximately `#E4E6EF`

Do not scatter raw colors unnecessarily.

Visual differentiation should primarily come from:
- spacing
- hierarchy
- placement
- density
- state
- restrained color
- consistent geometry

Mobile target:
- readable
- compact
- professional
- enough content visible
- not cramped
- not giant
- not unnecessarily scroll-heavy

Touch targets should generally remain around 44–48 px where practical.

---

## 13. Architecture direction

Do not perform a wholesale rewrite.

Use architectural principles incrementally:
- single source of truth for study state
- unidirectional state flow where practical
- small reusable UI components
- isolated feature responsibilities
- shared core utilities
- screenshot/golden regression tests
- adaptive layouts

Potential long-term organization:

```text
app
├── core
│   ├── question-engine
│   ├── source-visuals
│   ├── persistence
│   ├── analytics
│   └── ui
└── features
    ├── home
    ├── practice
    ├── timed-test
    ├── review
    ├── analysis
    ├── bookmarks
    └── spaced-repetition
```

This is a direction, not a command to modularize now.

---

## 14. Working rules for future assistants

1. Treat V11.6 Content Quality (`125d68b`) as the current physically accepted baseline.
2. Preserve every working core feature.
3. Do not revive the failed V11 shell.
4. Do not replace WebView architecture just for convenience.
5. Do not touch source visuals casually.
6. Keep Biochemistry isolated.
7. Keep Review Solutions and Question Navigator protected.
8. Make changes narrowly and deterministically.
9. Prefer one clear owner/script per build-time change.
10. Run syntax checks after all transformations.
11. Inspect the packaged APK.
12. Never claim physical testing unless the user confirms it.
13. For visual changes, compare against the existing accepted product, not a generic design ideal.
14. Prefer small measurable improvements over large redesigns.
15. Do not add features merely for novelty.
16. Keep the app fast and medically serious.
17. The physical device is the final judge.

---

## 15. Current decision

**The foundational build phase is finished.**

The product is now in the **fine-tuning / refinement phase**.

The next major goal is not “make more features.”

It is:

> **Make the existing QBank feel exceptionally polished without changing what already works.**

Priority order for the next cycle:

**Question screen → Home → Review consistency → Daily study loop → Intelligence → Analytics → Test refinement → Engineering hardening → final visual system.**

---

## 16. Golden rule

> **Build forward from what already works; never make the user pay for a new feature with a regression in an old one.**

---

## 17. Harness-neutral project memory

Root `AGENTS.md` is the universal instruction router. Canonical role-separated
memory lives in `.project-memory/`; `STATE.md` is current handoff and
`SESSION_LOG.md` is append-only history. Common Claude, Gemini, Cursor, and
Copilot files are thin pointers only. Live Git/repository state overrides written
memory, and current HEAD must be resolved rather than hardcoded. Run
`python3 tools/verify_project_memory.py` after memory changes.

<!-- V11.7_DEPLOYMENT_HANDOFF_2026-09-07 -->
## V11.7 deployment handoff — 2026-09-07

- Active candidate: `v11.7-cross-device-pwa-sync`. Physically accepted rollback baseline remains **V11.6 Content Quality** at `125d68b`; do not call V11.7 accepted until Android migration and Android↔iPad sync pass on real devices.
- Firebase/Firestore is configured and builds now report `QBANK_RUNTIME_CONFIG_OK firebase=configured`. Exact GitHub Variables: `QBANK_FIREBASE_API_KEY`, `QBANK_FIREBASE_PROJECT_ID`, `QBANK_ANATOMY_PDF_URL`. Firestore user-scoped rules and the intentionally empty composite-index set are deployed.
- Cloudflare Pages project: `nk-qbank`. Exact GitHub Secrets: `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`. Push builds create preview deployments. Manual **Build V11.7 Android + PWA** dispatch now also promotes the same artifact to production so `nk-qbank.pages.dev` is updated deliberately.
- Anatomy source PDF uses the configured public R2 object URL because it is ~46 MiB; Biochemistry and Physiology PDFs ship inside `build/web`.
- Physical iPad testing found and fixed two browser runtime bugs: `278b6c5` fixed the blank-screen sync bootstrap (`nkAuth` initialization timing); `7b047e5` fixed PDF.js canvas creation by avoiding a local `document` name that shadowed the DOM document.
- Latest hashed preview opens successfully on iPad. Before the production-promotion workflow change, the root `nk-qbank.pages.dev` still served the older blank production deployment. Source-PDF rendering, Anatomy/R2 CORS, final production URL, Android in-place upgrade, and full two-way sync still require physical verification.
- Next: wait for CI on the current branch → manually dispatch **Build V11.7 Android + PWA** once → verify `https://nk-qbank.pages.dev` → add final Pages hostname to Firebase Authentication authorized domains → ensure R2 CORS allows the exact Pages origin and Range GETs → install V11.7 APK over V11.6 without uninstalling → verify old local data → same-account Android/iPad sync, offline/reconnect, force-close/reopen, sign-out/in tests.



## Marrow multi-bank pilot handoff — 2026-09-08

- Active implementation branch: `feature/marrow-bank-pilot`.
- User physically checked the Anatomy PrepLadder/Marrow selector and initial
  Marrow flow, then visually reviewed the 20-question explanation pilot and
  approved its explanation grammar for full rollout.
- Current Marrow Anatomy pilot: 62 questions / 4 topics with namespaced IDs,
  native structured explanations, three resolved reconstruction cases, and the
  approved explanation architecture on all 62 questions.
- Full explanation layer: selective exam-discriminator emphasis, preserved
  source tables, 186 separate concise wrong-option rationales, and a *very
  light* display-only redundancy trim. Stored Marrow source transcription is
  unchanged.
- Full rollout verification: Engineering Gate `34163197757`; full Android+PWA
  `34163197772`; preview
  `https://feature-marrow-bank-pilot.nk-qbank.pages.dev` (immutable
  `https://bae56103.nk-qbank.pages.dev`). Production promotion was skipped.
- FSRS recall UI is a permanent fixed/floating dock above Previous/Next after
  answering; explanation work must never move it into document flow.
- Next expansion must first generalize the temporary Anatomy-only
  `MARROW_RECORD` to a subject-indexed/general bank registry, then add
  remaining Anatomy + Physiology + Biochemistry Marrow data in bounded,
  hash-verified batches.
- Canonical schema, explanation contract, procedure, failure lessons and
  regression checklist: `docs/MARROW_BANK_INTEGRATION.md`. Canonical live
  handoff remains `.project-memory/STATE.md`.


## Marrow image rollout — 2026-09-09

The user approved the 16-question image pilot as the minimum quality threshold.
PR #12 merged the pilot without production promotion. Batch 01 then expanded the
reviewed registry to 28 approved assets serving 34 questions, completed faithful
SVG reconstructions of the held notochord and glycolysis figures, preserved new
authentic biopsy/histology pixels exactly, and added per-binding provenance/QA so
deduplicated assets cannot be silently attached to the wrong question. Two such
false matches were explicitly rejected. Canonical live detail remains in
`.project-memory/STATE.md` and `docs/MARROW_IMAGE_PIPELINE.md`.
