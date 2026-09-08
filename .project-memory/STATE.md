# STATE.md — Current Project State and Handoff

> Keep concise and current. History goes in `SESSION_LOG.md`, durable reasoning
> in `DECISIONS.md`, and future work in `ROADMAP.md`.

## Repo / branch

- Repo: `Numankhan2013/V10.1`.
- Git `main` is the authoritative unified product line after PRs #6–#8.
  Current explanation-quality branch:
  `feature/marrow-biochem-explanation-gold-sample`.
  Production remains unchanged.
- Resolve live branch/HEAD with Git; never hardcode a self-staling current-HEAD field here.
- Accepted product baseline remains **V11.6 Content Quality** at `125d68b`,
  canonical APK run `34050921180`. Do not promote the Marrow candidate without
  explicit physical user acceptance.
- Accepted product commit: `125d68b`.

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
- The already-approved enhanced layer remains the canonical gold-standard
  reference: 142 questions (62 Anatomy + 80 Physiology), with 426 stored
  distractor rationales.
- The explanation-quality phase is now active. A bounded 20-question,
  cross-chapter Biochemistry candidate is stored in
  `data/marrow/explanation_biochem_gold_sample_v1.json` and uses the same
  takeaway / structured explanation / selective emphasis / three-distractor
  grammar. It remains a candidate until the user visually reviews it.
- Stored Marrow source transcription remains authoritative and unchanged; the
  Biochemistry candidate is augmentation/display-only. Two source-omission or
  ambiguity cases remain explicitly flagged rather than reconstructed.
- FSRS remains protected: the rating dock stays fixed/floating above Previous/Next.

## Verification / workflow status

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
- Unified consolidation checkpoint `87faccd`:
  - Engineering Gate `34255508094` / run 196 — **success**.
  - Full Android + PWA `34255508119` / run 406 — **success**.
  - Generated browser, FSRS, Marrow, PDF, APK and packaged contracts passed.
  - Preview: `https://consolidation-main-unified.nk-qbank.pages.dev`
    (immutable `https://e0d1385c.nk-qbank.pages.dev`).
  - Production promotion was skipped by the new explicit release guard.
- Authoritative-main `e42a076`: Engineering run 201 and full Android/PWA run
  409 succeeded; both Cloudflare steps were skipped, proving the release guard.

## User physical review — 2026-09-08

- User physically opened the run-405 Marrow feature PWA and confirmed the
  **question integration is successful**.
- User also confirmed the recovered **Topics journey/fixed Continue Learning UI**
  and **dedicated FSRS customization controls are live and good** on the deployed PWA.
- On 2026-09-08 the user explicitly verified the newly deployed Marrow PWA again,
  confirmed the questions and current experience are correct, and declared the
  integration/taxonomy verification phase complete. Treat those current surfaces
  as device-verified; this does not imply line-by-line review of all 2,115 source
  explanations.
- Exact lineage/deployment handoff: `docs/TOPICS_FSRS_FEATURE_HANDOFF.md`.

## Navigation / taxonomy

- The approved journey/glow/fixed-tray treatment remains unchanged.
- The explicit source-aligned 107-topic taxonomy in
  `data/marrow/topic_index_taxonomy.json` is implemented and the user has now
  physically verified the newly deployed PWA. The four cross-system Anatomy
  placements remain internally reviewable, but are not blocking the current
  explanation-quality phase.
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

- The remaining 1,973 non-reference explanations have not yet received the
  approved full-bank polish. The first 20-question Biochemistry candidate is now
  being used to validate the grammar before scaling.
- Source ambiguity must stay visible: especially missing numbered lists/lab
  panels and graph-dependent questions. Do not invent absent source evidence.
- Figure/image binaries remain a later pass; preserved metadata must not be lost.
- Large connector/Git writes are unsafe; keep shard + manifest + hash validation.
- Protected PrepLadder renderers, source PDFs, Practice/CBT/Review, FSRS, sync,
  modules, persistence and navigation must not be modified casually.

## Next step

1. Build-verify the 20-question Biochemistry explanation candidate on
   `feature/marrow-biochem-explanation-gold-sample`, including source-hash,
   ID/rationale, browser, packaged-app and FSRS regression checks.
2. Publish only a feature preview and visually review the 20 questions. The
   existing 142 questions remain the approved gold-standard reference until the
   user explicitly accepts the Biochemistry sample.
3. After sample approval, scale the same source-faithful augmentation grammar in
   deterministic chapter batches across the remaining Marrow questions; preserve
   raw source, native tables, figure metadata, uncertainty and reconstruction
   provenance.
4. Production promotion still requires an explicit release action and exact SHA;
   do not promote merely because CI passes.
5. Keep V11.6 `125d68b` as the immutable accepted rollback checkpoint until
   the user explicitly promotes a later baseline.

Canonical integration procedure and detailed failure lessons:
`docs/MARROW_BANK_INTEGRATION.md`.
