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

The Anatomy preview acceptance above remains the user/device-verified reference.
A later candidate on the same feature branch has now generalized the bank
architecture and added a bounded Marrow Physiology pilot.

- Shared runtime registry: `MARROW_RECORDS` → `MARROW_BY_SUBJECT` →
  `BANKS_BY_SUBJECT`.
- Anatomy remains PrepLadder 1,068/50 + Marrow 62/4 with the accepted behavior unchanged.
- Physiology now exposes PrepLadder 899/38 + Marrow Chapters 1–4, 80 questions/4 topics.
- Biochemistry remains PrepLadder-only and is the one-source regression control.
- Physiology transport: 11 hash-verified compressed/base64 shards plus
  `physiology_pilot_manifest.json`; all 80 IDs are `marrow__PHYS_...` and
  combined Anatomy+Physiology Marrow IDs are unique.
- Registry refactor verification: Engineering Gate `34190814897`; full
  Android/PWA/browser run `34190814843`.
- Physiology candidate verification: Engineering Gate `34191865093`; full
  Android/PWA/browser run `34191865094`.
- Real browser coverage proves Physiology → PrepLadder | Marrow, Marrow topic
  count/question count, native Structured text explanation, fixed FSRS dock,
  return to all 38 PrepLadder Physiology topics, and no Biochemistry Marrow leak.
- Side-by-side APK packaging and feature-preview deployment passed; production
  promotion was intentionally skipped.
- **This Physiology candidate is build/browser verified, not yet user/device
  verified or accepted.**

## Product behavior that must be preserved

The subject remains the top-level study domain. When a subject has more than one
question-bank source, clicking the subject opens a source selector.

Current accepted Anatomy flow:

`Anatomy → PrepLadder | Marrow`

- PrepLadder enters the existing bank unchanged: 1,068 questions / 50 topics.
- Marrow enters the same Topics → Chapter → Practice/Test/Review architecture:
  62 questions / 4 topics.
- The source/bank context is visible in Topics and question context.
- Question IDs are namespaced (for example `marrow__ANAT_CH01_Q001`) so
  attempts, bookmarks, FSRS records, modules, sync, and review history do not
  collide with PrepLadder IDs.
- Existing PrepLadder PDF-source rendering must remain untouched.

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

## Pilot data

Anatomy Marrow pilot:
- Gametogenesis — 19 questions.
- Pre-Embryonic Phase of Development — 13.
- Embryonic Phase of Development — 16.
- Placenta, Fetal Membranes and Twinning — 14.
- Total — 62.

Three incomplete-list source defects were reconstructed and are normal learner
questions, not learner-facing manual-review warnings:
- `ANAT_CH02_Q010`: list reconstructed as Cavitation / Compaction /
  Implantation / Cleavage so source answer `4-2-1-3` is internally coherent.
- `ANAT_CH03_Q004`: notochord sequence list reconstructed with Primitive
  pit/blastopore, Notochordal process, Notochordal canal, Notochordal plate.
- `ANAT_CH04_Q013`: missing monozygotic-twin categories reconstructed as
  DCDA / MCDA / MCMA.

Keep reconstruction provenance internally. Do not expose a manual-review badge
when the reconstruction is resolved with high confidence.

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

Key pilot files:
- `data/marrow/anatomy_pilot.zlib.b64.part*`
- `data/marrow/anatomy_pilot_manifest.json`
- `tools/apply_marrow_bank_pilot.py`
- `tools/marrow_pilot_apply.b64.part*`
- `tools/test_marrow_bank_pilot.py`
- `tools/verify_marrow_bank_browser.py`
- `tools/configure_marrow_pilot_android.py`
- `.github/workflows/build-apk.yml`
- `.github/workflows/engineering-gate.yml`
- `tools/verify_build_pipeline.py`

The Marrow transform is deliberately late in the deterministic build chain,
after the protected UI/sync/FSRS transforms and before final JavaScript,
generated-product, CBT, PWA, browser, APK, and package verification.

## Scaling beyond the current pilot

The Anatomy-specific registry special case is now retired. Do **not** reintroduce
one-off bank records for Physiology, Biochemistry, or later subjects.

Current safe sequence:
1. user spot-checks the build-verified 80-question Physiology preview;
2. add a bounded Marrow Biochemistry pilot through the same registry and extend
   the real-browser bank/source smoke test;
3. expand remaining verified Anatomy/Physiology/Biochemistry Marrow chapters in
   bounded manifest-verified batches;
4. keep learner-visible behavior and the shared Practice/CBT/Review/FSRS/sync/
   modules/analytics engines unchanged;
5. keep feature previews isolated until the user physically verifies each major
   cross-subject milestone; production promotion remains deliberate.

Prefer one normalized Marrow schema across subjects:
- stable namespaced question ID;
- subject;
- bank/source;
- topic/chapter ID + title;
- question/stem;
- four options;
- correct option;
- explanation text;
- structured tables when present;
- key-takeaway/source-fallback fields;
- image/figure metadata;
- provenance/source pages;
- review/reconstruction provenance.

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

## Lessons from the pilot

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

