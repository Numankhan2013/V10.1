# Physiology remaining-explanations audit — 2026-10-01

## Checkpoint

- Canonical base: `d4abce86068b4221e61e541c34dd29258de61cca`.
- Immutable Physiology source bundle SHA-256: `f3cd6b9dccb2092743fa86de4b0bef682d61c83762e9f00fa3b04d0a355d89d6`.
- Source PDF: `data/marrow/source_pdfs/physiologyed8.pdf`; SHA-256 `03834d3e9ec9723484387cd828a6f68cd999ec5187d167213f0bab9b967e0cfe`.
- Checkpoint scope: 26 actionable questions authored in four contiguous source-order files. The initial inventory had 254 Physiology IDs enhanced and 760 pending; after the first checkpoint, 280 are source-authored and validated candidates and 734 pending IDs remain, including two blocked by shared queue gates (732 actionable). The two source-limited IDs remain withheld by the shared queue.
- The raw source bundles, completeness ledger, shared inventory, runtime wiring, workflows, and gate files were not changed.

| Batch file | IDs | Workload | Source scope |
|---|---:|---:|---|
| `explanation_physio_ch11_q019_q021_v1.json` | 3 | 6/20 | Ch11 Sensory Receptors Q19–21 |
| `explanation_physio_ch12_q001_q008_v1.json` | 8 | 15/20 | Ch12 Somatosensory Pathways Q1–8 |
| `explanation_physio_ch12_q009_q018_v1.json` | 10 | 14/20 | Ch12 Somatosensory Pathways Q9–18 |
| `explanation_physio_ch12_q019_q023_v1.json` | 5 | 8/20 | Ch12 Somatosensory Pathways Q19–23 |

All four files retain the question IDs, source options, and keyed answers. Every question has a discriminator takeaway, detailed explanation, 1–4 case-sensitive emphasis anchors, and exactly three rationales keyed to its incorrect source options. Source-specific equations, tract crossings, relay nuclei, modality distinctions, and clinically relevant qualifiers are retained in learner-facing text.

## Source review and reconstruction

The candidate source records were loaded from the canonical Physiology shard. Relevant printed question/key/solution pages were checked against source provenance; selected pages were rendered from the pinned PDF where the imported explanation contained OCR substitutions or a broad claim needing qualification.

- **CH11 Q19:** Imported opening definition contains OCR corruption. Rendered page 223 confirms hyperalgesia is an exaggerated response to a noxious stimulus and distinguishes primary peripheral nociceptor sensitization from secondary central facilitation. The visible stem/options and answer key on pages 214–216 confirm option C (change in nociceptor threshold). The display also preserves the source’s sunburn, histamine, prostaglandin, and spinal/thalamic examples.
- **CH11 Q20:** Source key identifies TRPV3 as the channel most active at normal skin temperature. This mechanism is retained without expanding beyond the tested distinction.
- **CH11 Q21:** Rendered pages 215–216 confirm rectal temperature as the source-keyed answer for the cold-exposure scenario; page 224 contains the imported explanation’s overbroad statement that infrared tympanic thermometry is generally unreliable. The display retains rectal temperature as the best listed option while noting device/positioning conditions and possible lag during rapid temperature change. This qualification is supported by the field study using deep rectal temperature as a core reference and documenting environmental effects on tympanic measurements ([PubMed 26400226](https://pubmed.ncbi.nlm.nih.gov/26400226/)).
- **CH12 Q2–4:** Rendered pages 232–233 confirm the thalamocortical tertiary-neuron relay, spinal versus medullary decussation, and dorsal-column versus spinocerebellar/anterolateral modalities. Imported OCR damage is recorded per question with page and PDF-hash provenance.
- **CH12 Q6–10:** Rendered pages 234–236 confirm Brodmann areas 3, 1, and 2; the vertically oriented sensory homunculus; its lips/face/thumb cortical proportions; contralateral left facial loss from a right lateral postcentral lesion; and the full sensory-judgment effects of S1 lesions. Reconstruction metadata is limited to records whose imported text is OCR-damaged.
- **CH12 Q11–14:** Rendered pages 236–237 confirm the Brown–Séquard tract pattern, itch/C-fiber and Aβ gate-control description, and endogenous opioid actions. The learner text preserves the source’s specific laterality, modalities, and pathway details.
- **CH12 Q15–18:** Rendered page 238 confirms the source’s acupuncture endorphin hypothesis, fast Aδ neospinothalamic versus slow C-fiber paleospinothalamic pain, cannabinoid and norepinephrine mechanisms in stress-induced analgesia, and cerebellar tract modalities. Acupuncture is described as the classical source model, not as a sole clinical mechanism.
- **CH12 Q19–23:** Rendered pages 238–240 confirm the VPL/VPM and other thalamic relay distinctions, the crossed lateral spinothalamic tract selected for right-leg cordotomy, lemniscal pathway contents, post-crossing medial lemniscus laterality at the pons, and tactile/two-point deficits after S1 ablation. OCR reconstructions for Q19, Q20, Q22, and Q23 are pinned to the inspected printed pages.

Primary channel evidence for TRPV3 activation by innocuous warmth in keratinocytes: Peier et al., “A heat-sensitive TRP channel expressed in keratinocytes,” *Science* (2002), [PubMed 12016205](https://pubmed.ncbi.nlm.nih.gov/12016205/). The source-keyed exam distinction remains the basis of CH11 Q20.

## Reconstruction records

Records with `reconstruction.status = resolved_reconstruction` include complete `sourceProblem`, `reconstructedContent`, `evidenceBasis`, `reviewNote`, PDF path/hash, and inspected page numbers. These document actual imported OCR corruption or the CH11 Q21 overgeneralization; they do not alter or gate the raw question, options, answer, source tables, or figures. No `needs_manual_review` item is included in this checkpoint.

## Validation and handoff

The root worker batch validator passed these four files at the assigned base: 26 questions, source IDs/chapter/order matched, exact three source-keyed distractor rationales, emphasis anchors present verbatim, detail-retention or documented OCR reconstruction satisfied, and baseline/blocked IDs preserved. No preview build or integration was performed from this worktree. Continue at Chapter 13 Q1; inspect and restore the empty native table placeholder at Chapter 13 Q11 from printed pages 251–252 before finalizing that batch.


## Chapter 13 checkpoint

- Added 21 source-authored explanations across two contiguous batches; cumulative worktree output is 47 questions (26 previously committed plus 21 in this checkpoint). At that checkpoint, 713 IDs remained pending, including two blocked IDs; 711 were actionable. These are authored/validated candidate files, not preview-deployed enhancements. The later Chapter 14 checkpoint brings the cumulative candidate output to 65, with 695 original pending IDs remaining (693 actionable).

| Batch file | IDs | Workload | Source scope |
|---|---:|---:|---|
| `explanation_physio_ch13_q001_q011_v1.json` | 11 | 18.5/20 | Ch13 Special Senses Q1–11 |
| `explanation_physio_ch13_q012_q021_v1.json` | 10 | 11/20 | Ch13 Special Senses Q12–21 |

The files retain source IDs/options/keys and contain question-specific learner explanations, 1–4 verbatim emphasis anchors, and exactly three source-keyed distractor rationales each. The Q11 native comparison table, absent from the imported record, is restored in `displayTables`: X/type-X parvocellular versus Y/type-Y magnocellular input, color versus achromatic coding, cortical projections, and the listed signal functions. Printed p. 251 labels both projections as layer 4C; p. 252 resolves this as magnocellular 4Cα and parvocellular 4Cβ. This table correction is pinned to the PDF path/hash and pages 251–252; the source figure remains represented by the immutable PDF.

Selected OCR-damaged explanation pages were rendered from the pinned PDF (pp. 247–248, 250–252, 254–256). This confirms the ten retinal layers and opposing light/neural directions (Q1); rhodopsin photochemistry and 11-cis-retinaldehyde (Q2–3); amacrine cell response/transmitter descriptions and ganglion-cell action potentials (Q7–9); LGN eye-specific laminae (Q10); the X/Y pathway table and its 4C sublayer clarification (Q11–12); taste mechanisms (Q17); olfactory bulb circuitry and intensity range (Q18–19); photoreceptor counts/adaptation times and hemianopic pupil pattern (Q20–21). Reconstructed records are pinned per question to inspected source pages and the same PDF SHA-256.

CH13 Q17 is keyed to glutamate/umami. The source’s statement that sour taste uses H+ movement through ENaC is explicitly labeled outdated and corrected: ENaC is involved in salt taste while the OTOP1 proton channel contributes to sour responses, based on Teng et al., “Cellular and Neural Responses to Sour Stimuli Require the Proton Channel Otop1,” *Current Biology* 29 (2019), [doi:10.1016/j.cub.2019.08.077](https://doi.org/10.1016/j.cub.2019.08.077).

Validation: the root worker batch CLI passed all six Physiology files at the assigned canonical base: 47 questions, source-keyed rationale/option alignment, detail retention or pinned reconstruction evidence, and preserved baseline/gates.

## Chapter 14 checkpoint

- Added 18 source-authored explanations in the first contiguous Motor Physiology batch, Q1–18. Cumulative candidate output is 65 questions; 695 original pending IDs remain, including the two blocked IDs (693 actionable).
- The explanations cover intrafusal and extrafusal fibers, gamma and alpha efferents, primary Ia and secondary group II endings, spindle and tendon-organ function, stretch and inverse stretch reflexes, withdrawal and crossed extension, tone, alpha–gamma coactivation, righting/supportive reactions, and the corticospinal pyramids. Source option identities and keyed answers are retained with item-specific distractor rationales.
- Rendered printed pages 268–278 from the pinned PDF and checked the source prose, figures, and the nuclear bag/chain comparison table. CH14 Q5 restores that native table in `displayTables`, pinned to printed p. 271 and the same PDF SHA-256. Source figures remain in the immutable PDF.
- Worker batch validation passes all seven Physiology files at the assigned base: 65 questions, source-keyed rationales, verbatim emphasis, detail retention or page-pinned reconstruction, and preserved baseline/gates.
