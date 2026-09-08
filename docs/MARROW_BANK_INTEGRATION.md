# Marrow QBank Integration Runbook

> Canonical handoff for adding Marrow ED8 JSONL question banks to NK QBank.
> Read this with `AGENTS.md`, `.project-memory/STATE.md`, and
> `.project-memory/ARCHITECTURE.md` before changing bank/data behavior.

## Current accepted pilot — 2026-09-08

Branch: `feature/marrow-bank-pilot`.

The user opened and tested the deployed PWA preview and reported the new flow is
working beautifully. Treat the **PWA preview behavior** as user/device-verified.
It is not yet the production Pages deployment.

Preview:
- `https://feature-marrow-bank-pilot.nk-qbank.pages.dev`
- immutable deployment used by the final green run:
  `https://b0ea267f.nk-qbank.pages.dev`

Final verification at the current pilot milestone:
- Engineering Gate `34159542431` — success.
- Full Android + PWA run `34159542436` — success.
- Final browser Marrow selector/explanation smoke test — success.
- Side-by-side Android pilot APK — built and packaged successfully.
- Feature-branch production promotion — intentionally skipped.

## Current build-verified expansion candidate — 2026-09-08

The original Anatomy preview remains the user/device-verified reference behavior.
The current feature candidate has now ingested all JSONL supplied for this phase:

- Anatomy Marrow: **819 questions / 48 topics**.
- Biochemistry Marrow: **543 / 26**.
- Physiology Marrow: **753 / 33**.
- Combined Marrow: **2,115 questions / 107 topics**.
- Shared runtime registry remains
  `MARROW_RECORDS` → `MARROW_BY_SUBJECT` → `BANKS_BY_SUBJECT`.
- No new question/study engine exists; all banks reuse the existing Practice,
  CBT, Review, FSRS, sync, modules, analytics, bookmarks and persistence paths.
- The previous 62-question Anatomy and 80-question Physiology pilots remain
  accepted regression/augmentation subsets inside the expanded banks.
- Newly ingested explanations are deliberately source-faithful first. The
  approved enhanced explanation layer remains only on the existing 142-question
  subset until the later polish phase.
- Final verification checkpoint `bc500234`:
  Engineering Gate `34245190588` success; full Android+PWA
  `34245190771` success.
- Browser verification reports
  `anatomy=819/48 biochemistry=543/26 physiology=753/33 total=2115`,
  exercises all three Marrow bank selectors and returns to PrepLadder.
- Side-by-side APK, packaged APK verification and packaged product contract pass.
- This expanded candidate is **build/browser verified, not yet user/device
  verified and not accepted**.

The immediately earlier full run `34244982211` failed because its browser test
still asserted Biochemistry was PrepLadder-only. That requirement had changed;
the product was correct to expose Marrow. The stale assertion was updated to
test the new two-bank Biochemistry public contract.

## Product behavior that must be preserved

The subject remains the top-level study domain. When a subject has more than one
question-bank source, clicking the subject opens a source selector.

Current feature behavior:

`Anatomy → PrepLadder | Marrow`
`Biochemistry → PrepLadder | Marrow`
`Physiology → PrepLadder | Marrow`

Bank selection only swaps data/provenance. Existing PrepLadder PDF-source
rendering must remain untouched. Marrow uses the same Topics → Chapter →
Practice/Test/Review architecture and globally namespaced IDs so attempts,
bookmarks, FSRS, modules, sync and review history never collide.

Do **not** build a second question engine for Marrow. Bank selection chooses the
data/source; Practice, CBT, Review, FSRS, persistence, modules, sync, analytics,
and navigation remain the existing engines.

## Explanation contract

PrepLadder:
- Key takeaway.
- Existing source-PDF detailed explanation renderer.
- Existing source visuals/PDF behavior remains authoritative.

Marrow:
- Key takeaway.
- Native **Detailed explanation** rendered from structured JSONL text.
- Label/surface is **Structured text**, never `Original PDF`.
- Structured tables are rendered as real HTML tables where table data exists.
- Figure/image metadata is preserved for later asset integration. Missing image
  binaries are not a blocker for text-bank import.

Source wording is authoritative. Future explanation polish should change only
presentation: hierarchy, paragraph rhythm, bolding/emphasis, bullets, lists,
table styling, spacing, typography, and readability. **Do not paraphrase,
rewrite, summarize away, medically “improve,” or silently alter the source
explanation wording during visual polish.**

The shared PrepLadder takeaway heuristic may return empty for a Marrow record.
The pilot therefore adds a Marrow-only, source-derived fallback:
1. use the normal reviewed/source takeaway if present;
2. otherwise use the first meaningful sentence from the Marrow structured
   explanation;
3. only then fall back to the correct option text.
No new medical claim is invented.

## Current expanded data

Supplied/verified scope currently integrated:
- Anatomy Chapters 1–48 — 819 questions.
- Biochemistry Chapters 1–26 — 543 questions.
- Physiology Chapters 1–33 — 753 questions.

Historic accepted pilot subsets remain useful regression fixtures:
- Anatomy Ch1–4 — 62 questions.
- Physiology Ch1–4 — 80 questions.

Three Anatomy source defects remain deterministically reconstructed and carry
internal provenance:
- `ANAT_CH02_Q010`: Cavitation / Compaction / Implantation / Cleavage,
  coherent with source answer `4-2-1-3`.
- `ANAT_CH03_Q004`: Primitive pit / Notochordal process / Notochordal canal /
  Notochordal plate, coherent with `3-2-4-1`.
- `ANAT_CH04_Q013`: DCDA / MCDA / MCMA monozygotic categories.

## Data transport / integrity

Large JSON/JSONL-derived bundles must not be pasted as one huge GitHub text
write. A connector write truncated an early compressed payload during this
pilot.

Use the established safe pattern:
- normalize source data;
- serialize deterministically;
- compress;
- split into small base64 shards;
- commit shards;
- validate every shard and the reconstructed bundle by cryptographic hash;
- store a manifest with raw/compressed hashes, counts, shard count, and repaired
  question IDs;
- fail closed if any length/hash/count differs.

Do repository mutations sequentially when branch-head ordering matters. During
the pilot, simultaneous independent writes could compete for the branch head.

## Current implementation files

Expanded bank transport:
- `data/marrow/anatomy_phase_a.zlib.b64.part*`
- `data/marrow/anatomy_phase_a_manifest.json`
- `data/marrow/biochemistry_phase_a.zlib.b64.part*`
- `data/marrow/biochemistry_phase_a_manifest.json`
- `data/marrow/physiology_ch001_033.zlib.b64.part*`
- `data/marrow/physiology_ch001_033_manifest.json`

Compatibility/regression pilot data remains under `data/marrow/*pilot*`.

Core implementation/tests:
- `tools/apply_marrow_bank_pilot.py`
- `tools/marrow_pilot_apply.b64.part*`
- `tools/test_marrow_bank_pilot.py`
- `tools/verify_marrow_bank_browser.py`
- `tools/configure_marrow_pilot_android.py`
- `.github/workflows/build-apk.yml`
- `.github/workflows/engineering-gate.yml`
- `tools/verify_build_pipeline.py`

The Marrow transform remains deliberately late in the deterministic build chain,
after protected UI/sync/FSRS transforms and before final JS, product, CBT, PWA,
browser, APK and package verification.

## Scaling beyond the current supplied phase

The Anatomy-specific registry special case is retired. Do not reintroduce
one-off subject implementations.

Current safe sequence:
1. physically inspect this 2,115-question expanded feature preview across all
   three subjects;
2. record source/content/navigation defects separately from explanation polish;
3. improve explanations only after the user chooses that phase, keeping stored
   source text immutable and generated augmentation separate;
4. integrate later verified chapters through the same normalized schema and
   manifest/hash gates;
5. preserve learner-visible behavior and all shared study engines;
6. keep production promotion deliberate until the user explicitly accepts it.

Prefer one normalized Marrow schema across subjects:
stable namespaced ID, subject, bank, topic/chapter ID/title, stem, four options,
correct option, explanation, structured tables, figure metadata, provenance and
review/reconstruction metadata.

## Regression gates required for every expansion

Before calling a new subject/chunk integrated:
1. source bundle hash/count validation passes;
2. all IDs are globally unique and bank-namespaced;
3. existing PrepLadder subject/topic/question counts are unchanged;
4. Marrow topic/question counts equal the source manifests;
5. no Marrow topic leaks into PrepLadder and vice versa;
6. subject → bank selector → topic → question works in a real browser;
7. answered Marrow question renders Key takeaway + Detailed explanation +
   Structured text and never Original PDF;
8. Practice, Timed CBT, Review Solutions, Custom Study Modules, FSRS, sync,
   bookmarks, wrong/due queues, and Insights still pass their existing tests;
9. final inline JavaScript syntax passes;
10. generated PWA contract passes;
11. side-by-side pilot APK builds and packaged contract passes;
12. deploy only to a feature preview until the user physically checks it.

Do not promote a feature branch to `nk-qbank.pages.dev` production
automatically. Production promotion remains deliberate.

## Lessons from the pilot and full Phase A ingestion

- Full cross-subject data invalidated an old browser assumption that
  Biochemistry was the one-source control. Run 402 failed on that stale test,
  not on the product. Regression tests must follow deliberate public-contract
  changes.
- The pilot-era topic grouping shortcut treated every non-Physiology Marrow
  topic as General Embryology. Expanded Anatomy/Biochemistry/Physiology require
  subject-aware major-section taxonomy; this remains presentation only.

- The first side-by-side Android identity script failed because Gradle uses
  single quotes around `applicationId`; the script now matches the actual
  file and restores production identity after APK compilation.
- The first browser explanation failure was a genuine requirement gap:
  a Marrow question could have no takeaway. That was fixed with the
  source-derived fallback described above.
- A later browser failure was test-only: CSS typography displayed
  `KEY TAKEAWAY` while the test expected case-sensitive `Key takeaway`.
  Browser assertions should validate semantics, not cosmetic casing.
- Static marker tests are not enough. The Playwright flow caught the explanation
  surface and must remain in the gate.
- User feedback on the accepted pilot: functionality/source separation is
  excellent; next explanation improvement is **typographic/structural polish
  only, with wording preserved**.

## Safe next-session sequence

1. Read this runbook + canonical project memory.
2. Resolve live branch/HEAD and inspect latest green CI.
3. Confirm the shared bank registry and existing Anatomy regression tests remain green.
4. For a new subject, add a bounded manifest/hash-verified Marrow bundle to the
   existing registry; never fork navigation or question engines.
5. Extend the real-browser test to the new subject and back to its PrepLadder bank.
6. Build side-by-side APK + feature preview and inspect generated/package contracts.
7. Require user physical verification before calling the cross-subject UI milestone
   accepted or before any production promotion.


## Approved Anatomy explanation architecture — full rollout 2026-09-08

The 20-question gold pilot was physically reviewed by the user. The user called
the result near-perfect and approved its typography, selective high-yield
emphasis, preserved tables, and **Why the other options are wrong** grammar for
all current Marrow Anatomy questions.

The only requested refinement was *very slight* additional concision. Treat that
word literally: this is not permission to summarize or rewrite Marrow.

Current full-rollout contract:
- all 62 current Marrow Anatomy questions use the enhanced renderer;
- each question has selective exam-discriminator emphasis;
- each question has exactly three concise incorrect-option rationales (186
  total), stored separately from the Marrow transcription;
- existing structured source tables remain intact;
- the source transcription remains stored unchanged and auditable.

### Micro-concision rule

`nkGoldConciseText` performs display-only de-duplication. It may:
1. suppress a short first paragraph only when token overlap shows it
   substantially duplicates the already-visible Key Takeaway;
2. suppress short dead `image/figure/flowchart ... below` boilerplate when the
   corresponding asset is not being rendered;
3. suppress source paragraphs beginning `Option A/B/C/D:` (including grouped
   option labels) because the standardized concise distractor section replaces
   them.

It must **not**:
- paraphrase source sentences;
- delete unique mechanism/timing/derivative nuance;
- flatten or remove a source table;
- convert every paragraph into bullets;
- over-bold generic anatomical nouns.

The original source text remains in the imported Marrow record. Concision is a
render decision, not a data mutation.

### Distractor rationale layer

`data/marrow/explanation_gold_pilot.json` now covers all 62 questions. The
historic filename is retained to avoid unnecessary pipeline churn, but its
schema-v2 purpose is the approved full-bank augmentation map.

Rationales should normally be one compact exam discriminator:
- explain the single fact that makes the option wrong;
- prefer NEET-PG / INI-CET / FMGE / USMLE-relevant distinctions;
- do not add a mini-textbook paragraph;
- do not invent uncertainty;
- generated rationale text remains separate from Marrow source text.

Tests enforce:
- augmentation IDs exactly equal the 62 current Marrow question IDs;
- exactly three rationale keys per question, matching the three incorrect
  option letters;
- concise rationale length bounds;
- 1–4 selective emphasis spans per question.

### Permanent FSRS rule

The FSRS recall dock is **not part of the explanation document flow**.
After answer submission it remains in the existing fixed/floating session footer
above Previous/Next. Explanation work must never move, restyle, or couple the
FSRS dock to the detailed explanation.

### Verification

Full rollout verification:
- Engineering Gate `34163197757` — success.
- Full Android + PWA run `34163197772` — success.
- Browser verification proved:
  - a question outside the original 20-question pilot now uses the full grammar;
  - PGC Q1 removes only its redundant lead repeat while retaining migration
    nuance;
  - the `Stages of prenatal development` structured source table survives;
  - every tested answer still exposes three distractor rows;
  - the FSRS rating remains inside fixed `.nk-session-footer`.
- Side-by-side pilot APK packaged successfully.
- Cloudflare preview deployed:
  `https://feature-marrow-bank-pilot.nk-qbank.pages.dev`
  (immutable `https://bae56103.nk-qbank.pages.dev`).
- Production promotion remains intentionally skipped.

Next expansion work should reuse this explanation contract after first
generalizing the temporary Anatomy-only bank record into the multi-subject bank
registry described above.

