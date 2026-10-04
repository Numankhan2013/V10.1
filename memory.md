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
- Cloudflare Pages project: `nk-qbank`; canonical root: `https://nk-qbank.pages.dev`. The production release workflow sets the Direct Upload project production branch to `main` before upload. Release `d43da3dbdaa639214d676b333152654568fe5ba9` was promoted in run `36325843382`; root, `main.nk-qbank.pages.dev`, and preview `https://37799f47.nk-qbank.pages.dev` serve byte-identical builds (HTTP 200).
- Anatomy source PDF uses the configured public R2 object URL because it is ~46 MiB; Biochemistry and Physiology PDFs ship inside `build/web`.
- Physical iPad testing found and fixed two browser runtime bugs: `278b6c5` fixed the blank-screen sync bootstrap (`nkAuth` initialization timing); `7b047e5` fixed PDF.js canvas creation by avoiding a local `document` name that shadowed the DOM document.
- Latest hashed preview opens successfully on iPad. Before the production-promotion workflow change, the root `nk-qbank.pages.dev` still served the older blank production deployment. Source-PDF rendering, Anatomy/R2 CORS, final production URL, Android in-place upgrade, and full two-way sync still require physical verification.
- Remaining physical checks: install the current APK over the existing Android install without uninstalling; verify local data preservation and same-account Android/iPad sync, offline/reconnect, force-close/reopen, and sign-out/in behavior. PWA production root is current.



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

## Home and Practice audit acceptance — 2026-09-24

The user accepted the repaired preview and authorized its promotion to the
canonical branch. The integrated product checkpoint `b6dd246` passed Engineering
`35967933879` and full browser/PWA/APK/Android `35967933880`, including the
two-paused-chapter submit, Review Solutions, and Home Continue sequence. Canonical
handoff and promotion status are maintained in `.project-memory/STATE.md` and
`.project-memory/SESSION_LOG.md`; production and physical in-place upgrade remain
separate.


### 2026-10-01 — Revision hub candidate

`feature/home-revision-hub` starts from combined main. Primary Revision replaces
FSRS; Home displays global due/missed counts, while the four queues and a new
embedded seven-day forecast respect the Revision focus. Existing FSRS graphs,
settings, scheduling and all-bank session behavior are preserved. Study rows
and cards are neutral, with semantic count/icon accents. Candidate validation,
user review and production promotion remain distinct; consult live branch CI.

The user then approved the Revision screenshots and requested an animated Home
streak in the same candidate. The Home owner now connects adjacent studied days,
shows gaps, and grows the flame/glow at 3/7/14/30 days. Reduced motion is static;
canonical streak/day counts are unchanged. All tier/responsive browser checks
and the required Pause/Home/Continue regression pass on the updated generated
baseline; recheck the exact combined candidate's full CI before promotion.

The user rejected the amber streak preview and requested a liquid blue/violet
week strip moving toward the next dot, with no celebratory notices. The revised
candidate has flowing completed links, a stretching/receding frontier at today,
neutral future dots, more lively flame/embers and static reduced-motion mode.
Actual six-second GIF/MP4 motion evidence is in local build/ui-checks. Local
75 checks, generated product contract, responsive/tier/real-motion/reduced-motion
browser checks and source-hygiene browser pass; exact latest full CI is pending.


Final combined product `d3247ca63d3db3f99fa9310be4c399dde0dd449a` is now
build-verified: all 75 local checks, Engineering `36838440726`, and full
browser/PWA/APK/Android phone+tablet `36838433115` passed. Preview:
`https://ca26da11.nk-qbank.pages.dev`. Deployed and direct live-browser checks
passed Revision/streak/FSRS; CI Home and Android evidence was inspected.
PR #80 is a draft; user visual review and physical acceptance remain pending.
Main/production are unchanged; documentation-only handoff keeps certification
at the product SHA above.


### 2026-10-01 — FSRS correction patch

The user accepted the Revision/streak preview and authorized the investigated
FSRS patch. Unresolved mistakes now follow the latest answer; correct retries
clear the queue while FSRS/history remain. The visible Hard/Good/Easy control
amends the same retrieval through immutable, separately stored synced rating
events. Undo and edits retain durable rollback. Stale pending ratings cannot
return through checkpoint merge. Saved-result follow-up excludes resolved
misses while keeping its original score. Certified product
`4a14b0cfe8f231da0026fc5d621c1ebaf26fcc84` passed 75 local checks,
Engineering `36875631994`, and full PWA/APK/Android phone+tablet
`36875623643` (attempt 2). Preview: `https://f4e2534b.nk-qbank.pages.dev`.
Deployed-HTML and direct live phone/tablet rating/reload/Revision/FSRS checks
pass with no page errors. Initial Android failure was a Pixel Launcher ANR
overlay; the identical APK passed on retry. PR #80 remains draft; production
and main unchanged. Physical acceptance remains separate. Final documentation
was recorded through GitHub during workspace offline; fetch before local work.



### Explanation refinement candidate — 2026-09-30

User-directed parallel Luna wave: 83 new explanations plus nine existing emphasis repairs, source inventory 753 enhanced / 1,958 pending. Latest released preview remains 670 until exact-head combined CI passes. Primary owns shared integration; immutable sources/omission gates are preserved. See canonical STATE.md, wave manifest and docs/question-explanations/ audits. Production is not promoted.

## 2026-10-01 — Verified explanation release and continued queue

Last released product d4abce86068b4221e61e541c34dd29258de61cca: 753 enhanced/1,958 pending, Engineering 36742636966 and full Android/PWA/phone-tablet 36742637191 successful, preview https://e954d103.nk-qbank.pages.dev. Production remains untouched. User requests parallel Luna refinement of all remaining actionable explanations, source self-review by workers, exception-only integrator review and one combined build. Resume queue pins existing 753 exact augmentation hashes, all immutable source hashes, 1,935 actionable IDs and 23 deferred Marrow source gates. First local source-validated integration checkpoint adds149 (59 Anatomy/64 Biochemistry/26 Physiology): candidate902 enhanced/1,809pending, 1,786 actionable remain. This candidate is unfinished and unverified by full CI; full-queue validation deliberately rejects release until complete. Consult STATE and the latest wave manifest for newer checkpoints.

- 2026-10-01 continued local integration: 710 new validated explanations / 1,463 candidate enhanced; 1,225 actionable remain plus 23 existing deferred gates. Anatomy status metadata and adrenal variant rationale corrected. Released source ledger hash is now checked against the earlier certified wave even when regenerating pins. Primary Anatomy and Physiology plus reassigned Biochemistry tail worker continue; no new preview deployment yet.

- 2026-10-01 checkpoint: 1,027 new explanations integrated/validated / 1,780 candidate enhanced; 908 actionable remaining, 23 source gates unchanged. Biochemistry263 and Anatomy tail252 complete; reassigned worker starts Physiology tail261. Primary Anatomy315/662 and primary Physiology197/497 complete. User reaffirmed single final combined push/build, no partial deployment.

- 2026-10-01 continued checkpoint: 1,206 new validated / 1,959 candidate enhanced, 729 actionable remaining plus23 source-held. Primary Anatomy338/662, primary Physiology212/497, tail Physiology141/261. Latest pins/source/gates/baseline augmentation hashes pass; no preview push/build yet.

- 2026-10-01 checkpoint: 1,385 new validated / 2,138 candidate enhanced,550 actionable remain. Biochemistry worker completed Bio263,Anatomy-tail252,Physiology-tail261 and continues untouched middle165. Primary Anatomy397/662,Physiology212/332. Duplicate Anatomy emphasis anchor corrected; worker validator now catches duplicate anchors locally. No push/deployment before full completion.

- 2026-10-01 checkpoint1,698 new validated /2,451 candidate enhanced,237 actionable remain. Anatomy primary525complete now authors untouchedPhys25–27; primaryPhys232/263; tailworker authors Anatomy43–50. Pancreatic rationale corrected after actualoptiontext review, combinedchecks pass. One final build/push remains deferred until all authoringdone.

- 2026-10-01 checkpoint1,887new/2,640enhanced validates;48actions remain Ch25–26. FinalPDFexceptionreview recovered Ch27Q9 five-roworganflowtablefromp492 via existing orphan tableblock withPDFhash provenance;Ch27Q13actualfigure2D/2L vsD/L explains8x, sourcecontradiction resolved. Added narrow orphanblock/pagevalidator and regression/browserowner coverage; immutablebanks/gates unchanged. Full previewbuild awaits final48.

- Final1935-actionable authoring complete:2688enhanced/23deferred/2711total,zero unprocessed IDs. All55localchecks pass; final2orphan tablesCh25Q6/Ch26Q3 now rendered displayTables withsourceIDs/pages/PDFhash,completewave revalidated aftermerge. Ten tableowners recovered in thiswave. Existing753augmentation fingerprints,rawbanks,gates unchanged. Three explicit sourcecaveats remain inenhanceditems (Bio17Q22 missinglabs,Bio26Q15capping ambiguity,Phys32Q28fiberwording). One combined canonical push/fullpreviewbuild next; no newcandidate buildverification yet.

- Combined product08ded423 pushed: Engineering36841656512 passed; fullrun36841656565 failed in explanationbrowser onPHYSIO_CH23_Q018 selectiveemphasis beforedeployment. Rootcause: presentationtransform scientificformats text(H+ ->sup), but leavesanchorplainescaped. Narrowfix scientificformatsneedle identically. Actualrendererregression checksfailingH+,escaping,all2546authored displayconfigs including1935new; early inbothCIworkflows. All56localchecks pass; replacementbuild required. No source/explanationrecords changed byfix.

## 2026-10-01 — Completed explanation release and scientific-emphasis regression

Product `9d318f79d73d6f22a3c6f508e10f1fb243aea349` passed Engineering `36870646707` and full Android/PWA run `36870646652`, including phone/tablet Android WebView interaction, hardware Back, force-stop resume, review and FSRS checks. Preview: https://ac2f50ca.nk-qbank.pages.dev. Production was not promoted; physical acceptance is not implied.

All 1,935 actionable explanations from the initial 1,958 pending are authored and integrated: 914 Anatomy,263 Biochemistry,758 Physiology. Total2,688 enhanced /23 explicitly source-held /2,711. Complete-wave checks protect old753 augmentation fingerprints,immutable raw banks and unchanged answer gates. Ten source-reviewed explanation table owners were recovered, including three omitted table objects anchored to existing table-block IDs and original explanation pages.

Initial combined full run36841656565 failed before deployment on PHYSIO_CH23_Q018 emphasis: scientific formatter converted H+ to superscript HTML while anchor matching used plain escaped text. Fixed identical scientific formatting on text/needle, and added actual-renderer regression for the exact case, escaping and all2,546 authored display-text configurations. This regression runs early in bothCI workflows; all56 local checks passed. Replacement full browser suite passed3,870 exact runtime checks and562 rendered cases across phone/tablet. Live downloaded preview matches all2,688 approved configs exactly, includes corrected renderer and three orphan table recoveries; HTML SHA-256 bdc7702f8b9b6dc68b3ae1fbd6d7cd963baf6f2b274360c2b9eb158a3751c4f2.

Three enhanced items retain explicit source caveats (Bio17Q22 absent labs,Bio26Q15 capping ambiguity,Phys32Q28 fiber wording). All23 pre-existing pending source gates are deferred at user request. No actionable explanation work remains; do not restart completed workers. This final certification is docs-only with skipCI so it does not schedule another preview build.


### 2026-10-01 — Learning Insights dashboard

The user requested a comprehensive period-aware Insights dashboard from their
phone/tablet prototypes, then removed Study Map/Topics to revisit and required
a full-year heatmap at the top. Continuous relative count/peak shade and glow
replace fixed thresholds; year/scope changes rescale the calendar. The new
read-only dashboard includes period comparisons, outcomes, recorded timing,
topic/subject performance, FSRS, mistake recovery and module progress. Source
and active release work remain separate. See STATE.md and docs/LEARNING_INSIGHTS.md
for certification, preview and the current candidate handoff.

## 2026-10-01 — Approved combined production release completed

Product `18e4cd58a09f14169447dd7aaf13a6cc08971ceb` passed Engineering `36883870916` and full Android/PWA run1380 / `36883871119`, including Android emulator checks. The deterministic answerable-topic screenshot fixture passed. User-approved runs1375 and1378 features and all2,688 enhancements are merged into main. Full-build workflow_run production follow-up did not appear; a dedicated release-branch push deployed the existing verified artifact without rebuilding. Production run `36888530721` verified exact current-main/artifact/APK identity, set Pages production_branch=main and published https://3bbd46cc.nk-qbank.pages.dev. Root https://nk-qbank.pages.dev is byte-identical (HTML SHA-256 `f0f9bb3ce205c6f79ae024d5025ffcce8c977a0915dc178c5307c83be5145c2a`). Entire live2,688-entry explanation map equals approved configs; liquid streak, Revision and editable-rating markers are present. Main and content integration branch are synchronized with this docs-only release handoff; no new full build is required. Preserve23 source gates, two archival image gaps and422 PrepLadder source-comparison audit entries. This is user-approved production promotion, not a claim of new physical Android testing.

## 2026-10-01 — App-wide clarity pass with comparative Insights

The user supplied phone screenshots showing repeated page kickers/subtitles, definitions under obvious Revision labels, and excessive header gaps. They requested removal of noise across the app, and authorized promotion of the combined Insights/clarity candidate to main and https://nk-qbank.pages.dev after verification. The late deterministic clarity owner trims navigation-only markup, compacts main page headers, Revision queues, Home focus, FSRS settings and builders; counts/actions, safety warnings, save/sync states, subject/bank context and source questions/explanations remain protected. Insights now starts with title/controls and Activity, removes repeated chart instructions and promotional summary, and keeps metric definitions in collapsed help. Continuous heatmap intensity remains relative to the selected year/scope peak. Screenshot inspection and browser checks cover ten screens and two builders at320/390/820; all four populated Revision queues fit above phone navigation. Existing Continue Practice, missed-question/FSRS and Revision/streak browser checks pass. The previous94e1 build passed web/PDF/APK but Android tablet attempts lost a screenshot target and then timed out reconnecting WebView; neither is a certified final candidate. Full combined CI and production delivery remain pending. Current main release handoff ecf7906 was merged, retaining verified18e4 production content and release workflow.

### 2026-10-02 interaction polish continuation

User authorized latency recovery and native-feel polish. Implementation/local
responsive checks on feature/home-interaction-polish retain c662 analysis/header
work; new exact-head full CI is pending. Root/main still serve1ba. STATE and
docs/INTERACTION_POLISH_2026-10-02.md own current facts. No physical haptic claim.

Interaction candidate a68e9c2 passed feature full36956370295 and both fast gates;
PR83/PR82 are merged through exact-SHA main fast-forward. Official main full
36957980864 is running; canonical root remains1ba pending verified-artifact
deployment. Keep main at a68 during the production identity guard.

### 2026-10-02 — User-reported press latency / gentle answer feedback

Main a68 is build-verified from feature CI, but the user reports its new interactions feel slower across the app. Hold canonical deployment while correcting shared110 ms state/release transitions and added route/question/sheet movement. A/B computed appearance confirms old answer colors persisted on the first frame; correction makes committed colors immediate with no transition. Preserve save/indexing/in-place improvements and rollback. User additionally requests subtle answer haptics: single7/9 ms browser pulses and native CLOCK_TICK outcomes. Fresh responsive/browser/native certification pending on `feature/home-answer-latency`; root still serves1ba.

The first latency correction's full run36959307370 caught a real pre-existing race exposed by faster clicks: a stale250 ms CBT cleanup closed a newly opened Review navigator. Reproduced locally, fenced cleanup to its submitted exam, removed legacy panel animation and added source ownership / generated300 ms Review survival checks. PYQ/mixed/history/Review/follow-up now pass on phone/tablet; fresh full certification is required. Superseded maina68 Android failed at WebView rediscovery after app reset, after its Pause/Back/multi-Pause paths passed.

## UWorld reference refinement — 2026-10-03

Active reference refinement follows certified PR93. User accepts prior pilot
phone/iPad/desktop typography and continuous Revision; requests a Luna source
pass, independent My UWorld collection hierarchy and no FSRS-only Practice misses.
All132 reviewed documents preserve immutable originals;131 are practice-ready,
1244 is held for an absent essential exhibit. Native tables/focused figures and
source-labelled choice reasoning preserve UWorld flow; option percentages appear
beside answers immediately after answering and stay hidden in CBT. See canonical
STATE and docs/UWORLD_BIOCHEMISTRY_PILOT.md for live certification and limits.
Production remains unchanged; no medical certification is claimed.

The UWorld reference refinement is now certified at424e0ca8:101 local checks,
both Engineering gates and full37158603961 including Android phone/tablet.
Actual hosted390/820/1194/1440px flows pass at https://2f165b3a.nk-qbank.pages.dev.
PR94 stacks on93; production is unchanged. See canonical STATE and the pilot
report for exact hashes and remaining source limitations. This handoff is docs-only.


The user accepts the Biochemistry reference architecture and authorizes the second
UWorld collection on October4: Poisoning & Environmental Exposure (33questions).
Explanation aesthetics are deferred. Shared engines and source-native documents
remain; canonical STATE and docs/UWORLD_SECOND_COLLECTION.md track current
verification and source review. Production is unchanged.

Second collection certified at795d94a9:33 Poisoning & Environmental Exposure
questions,29 native tables,22 focused figures;102 local checks, both Engineering
gates and full37165147973 including Android phone/tablet emulators pass.
Actual hosted four-width flows and206 offline media paths pass at
https://1b80a731.nk-qbank.pages.dev; all184 Biochemistry image hashes are unchanged.
PR95 is ready, stacked on94. Canonical STATE and UWORLD_SECOND_COLLECTION.md
record exact hashes/provenance; production is unchanged. This handoff is docs-only.

October4 follow-up: user confirms the second UWorld preview works and requests
card-footer removal and an app-wide Impeccable quality pass. Active quality branch
fixes block taxonomy, reference-only search/batches, incompatible native bank
filters, modal disclosure focus and small builder targets.102 local checks and
bounded rendered flows pass. Product67a85ee3, both Engineering gates and full
37184199118 including Android phone/tablet emulators pass. Actual hosted UWorld
four-width/Search/focus checks pass at https://adf558ca.nk-qbank.pages.dev; all206
media hashes/offline paths remain unchanged. PR96 is ready, stacked on95. The
docs-only certified handoff preserves that product artifact; production unchanged.
Canonical STATE and docs/UWORLD_APP_QUALITY_2026-10-04.md own current details.

October4 next batch: user authorizes reuse of supplied JSONLs/PDFs and chooses
Ophthalmology as the first PDF-only extraction. Active Ophthalmology branch uses
the pinned30-question/204-page source56fe817, three Luna/high source batches and
existing UWorld registry/display/media/study engines. Verification is in progress;
canonical STATE and docs/UWORLD_OPHTHALMOLOGY_COLLECTION.md own current detail.
Production and prior certified artifacts remain unchanged.

2026-10-04: The user explicitly authorizes the preproduction UI/UX/function/security
audit and promotion accessible from https://nk-qbank.pages.dev. Ophthalmology
30 questions/204 pages/8 tables/77 figures joins the existing UWorld registry.
The audit branch repairs account Back/contrast, narrow topic controls/focus,
empty FSRS actions, Android migration/file/private-asset boundaries and hosted
frame/MIME/referrer headers. Final main CI, Android and exact production-domain
proof remain required; consult STATE and the preproduction audit report.
