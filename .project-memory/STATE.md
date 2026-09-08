# STATE.md — Current Project State and Handoff

> Keep concise and current. History goes in `SESSION_LOG.md`, durable reasoning
> in `DECISIONS.md`, and future work in `ROADMAP.md`.

## Repo / branch

- Repo: `Numankhan2013/V10.1` (private).
- Active candidate branch: `feature/marrow-bank-pilot`.
- Resolve live branch/HEAD with Git; never hardcode a self-staling current-HEAD field here.
- Accepted product baseline remains **V11.6 Content Quality** at `125d68b`,
  canonical APK run `34050921180`. Do not promote the Marrow candidate without
  explicit physical user acceptance.
- Accepted product commit: `125d68b`.
- `main` is stale relative to the V11 line and must not be used as the product baseline.

## Marrow Phase A expansion — 2026-09-08

- The shared subject-indexed bank registry remains the only bank architecture:
  `MARROW_RECORDS` → `MARROW_BY_SUBJECT` → `BANKS_BY_SUBJECT`.
  No second Practice/CBT/Review/FSRS/sync/module/analytics engine was created.
- Supplied Marrow ED8 content now exists in the candidate as:
  - **Anatomy:** 819 questions / 48 topics.
  - **Biochemistry:** 543 questions / 26 topics.
  - **Physiology:** 753 questions / 33 topics.
  - **Total Marrow:** 2,115 globally unique namespaced questions / 107 topics.
- PrepLadder remains unchanged in parallel:
  Anatomy 1,068/50; Biochemistry 719; Physiology 899/38.
- Expanded data is transported in deterministic zlib/base64 shards with
  manifest counts, byte lengths and SHA-256 validation. Runtime loader fails
  closed on corruption, count drift, identity mismatch, duplicate IDs, bad
  option shape, or question→topic linkage mismatch.
- Expanded bundle names:
  `anatomy_phase_a`, `biochemistry_phase_a`,
  `physiology_ch001_033`.
- The original accepted 62-question Anatomy pilot and 80-question Physiology
  pilot remain regression/augmentation subsets. Their existing learner behavior
  was not downgraded.
- Three Anatomy reconstructed questions remain preserved with provenance:
  `ANAT_CH02_Q010`, `ANAT_CH03_Q004`, `ANAT_CH04_Q013`.

## Explanation status

- Initial ingestion was deliberately **content-first** per user instruction.
  Newly added questions use the supplied source-faithful structured explanation
  surface without a new explanation rewrite phase.
- The already-approved enhanced layer remains only on the existing 142-question
  subset (62 Anatomy + 80 Physiology), with 426 stored distractor rationales.
- Stored Marrow source transcription remains authoritative and unchanged.
- Explanation improvement for the remaining questions is a later, separate phase.
- FSRS remains protected: the rating dock stays fixed/floating above Previous/Next.

## Verification / workflow status

- Earlier full run `34244982211` (run 402) failed at the Marrow browser test
  because the test still expected **Biochemistry = PrepLadder only**. The product
  correctly exposed the newly integrated Marrow bank; this was a stale test
  assumption, not a product/data failure.
- The browser test was updated to exercise Biochemistry → PrepLadder | Marrow,
  Chapter 1, source-faithful explanation, and return-to-PrepLadder regression.
- Final integration checkpoint `bc500234`:
  - Engineering Gate `34245190588` / run 193 — **success**.
  - Full Android + PWA run `34245190771` / run 403 — **success**.
  - Browser result: `anatomy=819/48 biochemistry=543/26 physiology=753/33 total=2115`.
  - Side-by-side Marrow APK built; packaged APK/product contracts passed.
  - Artifact `V11.7-android-pwa` ID `10063767953` uploaded successfully.
- The exact expanded candidate was republished through full run `34246876973`
  / run 405 — **success**, including memory verification, Marrow browser gate,
  side-by-side APK, packaged product contract, artifact upload, and Cloudflare
  feature-preview deployment.
- Live mutable feature alias: `https://feature-marrow-bank-pilot.nk-qbank.pages.dev`.
  Immutable deployment for this publish: `https://2278b62b.nk-qbank.pages.dev`.
- Run 405 artifact `V11.7-android-pwa`: ID `10064442860`.
- Production promotion was **skipped**; `nk-qbank.pages.dev` production was not
  changed by this Marrow preview publish.

## User physical review — 2026-09-08

- User physically opened the run-405 Marrow feature PWA and confirmed the
  **question integration is successful**.
- User also confirmed the recovered **Topics journey/fixed Continue Learning UI**
  and **dedicated FSRS customization controls are live and good** on this feature PWA.
- These recovered features are on `feature/marrow-bank-pilot`; the production/root
  PWA was not promoted in run 405, and stale Git `main` is not the V11 source.
  Missing features on the older “main PWA” are therefore a branch/deployment
  separation issue, not a reason to rebuild them from scratch.
- Exact lineage/deployment handoff: `docs/TOPICS_FSRS_FEATURE_HANDOFF.md`.

## Navigation / taxonomy

- The journey visual design is now user-approved, but the **major index taxonomy
  is wrong**. Do not change the approved journey/glow/fixed-tray treatment.
- Replace heuristic grouping with one explicit source-aligned mapping using
  `docs/MARROW_TOPIC_INDEX_TAXONOMY.md`.
- Required source index families are recorded there for Anatomy, Physiology and
  Biochemistry, including the user's exact order and PYQ rules.
- Taxonomy is navigation-only; never rewrite medical content.

## Status discipline

- The expanded feature candidate remains **build-verified** by run 405.
- The user has now physically spot-checked the expanded feature PWA and confirmed
  successful Marrow question integration plus the recovered Topics/FSRS surfaces.
- Those tested surfaces are **device-verified**; this is not blanket verification
  of every one of the 2,115 questions and not promotion of the overall product.
- V11.6 `125d68b` remains the **accepted baseline** / rollback checkpoint until
  the user explicitly promotes a later candidate.

## Known problems / cautions

- Topics major-index grouping is currently inaccurate despite the approved visual
  journey. The next Topics change is taxonomy-only.
- New explanations intentionally have not received the approved full-bank polish.
  The Biochemistry physical screenshot shows raw structured/OCR text quality that
  belongs in a separate display/augmentation phase.
- Figure/image binaries remain a later pass; preserved metadata must not be lost.
- Large connector/Git writes are unsafe; keep shard + manifest + hash validation.
- Protected PrepLadder renderers, source PDFs, Practice/CBT/Review, FSRS, sync,
  modules, persistence and navigation must not be modified casually.

## Next step

1. **No implementation in this handoff commit.**
2. Next Topics implementation: correct only the source index taxonomy using
   `docs/MARROW_TOPIC_INDEX_TAXONOMY.md`; preserve the user-approved journey and
   FSRS customization exactly.
3. Next explanation phase, when explicitly started: follow
   `docs/MARROW_EXPLANATION_FINE_TUNING.md` and scale the approved 142-question
   grammar source-faithfully across the remaining Marrow questions.
4. Remaining Marrow chapters/questions and figure binaries are separate later work.
5. Keep V11.6 `125d68b` as the immutable accepted rollback checkpoint.

Canonical integration procedure and detailed failure lessons:
`docs/MARROW_BANK_INTEGRATION.md`.
