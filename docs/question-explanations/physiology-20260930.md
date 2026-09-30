# Physiology explanation batch — 2026-09-30

## Candidate scope

- Source-order range: Marrow Physiology Chapter 11, Sensory Receptors, Q7–Q10.
- Exact IDs: `marrow__PHYS_CH11_Q007`–`marrow__PHYS_CH11_Q010` (4 questions).
- Workload: **17.5 / 20** (target 16), one contiguous source-order block.
- Canonical base recorded in the candidate file: `81822e44753f5c3af7c2f2b0719d12230eed4478`.
- Source bundle SHA-256: `f3cd6b9dccb2092743fa86de4b0bef682d61c83762e9f00fa3b04d0a355d89d6`.
- Source PDF SHA-256: `03834d3e9ec9723484387cd828a6f68cd999ec5187d167213f0bab9b967e0cfe`.
- No question-completeness gate is recorded for these four IDs. Their source keys and source records are intact. The augmentation remains `candidate-rollout`; it is not approved or present in the live preview yet.

The four entries preserve the source's intensity coding, adaptation groups, Aδ/C-fiber comparison, algogen list and pain sensitization distinction, and TRPV1 stimulus associations. Q7 and Q8 now carry populated `displayTables` reconstructed from the inspected printed page 219, with source ownership, column labels, row labels, and cell values retained. Each question has a meaningful takeaway, 1–4 exact emphasis anchors, and exactly three rationales keyed to the three incorrect source options. Raw question bundles are unchanged.

## Per-question source audit

| ID | Source review | Refinement / status |
|---|---|---|
| `marrow__PHYS_CH11_Q007` | Question page 211; answer key page 215; solution and tonic/phasic table page 219. The scan shows frequency coding, receptor recruitment, Weber–Fechner distinction, adaptation, and the complete slow/rapid receptor lists. | Restores the corrupted, populated two-column table as `displayTables` and retains the clothing/adaptation example. `resolved_reconstruction`. |
| `marrow__PHYS_CH11_Q008` | Stem/options page 212; key page 215; solution and Aδ/C comparison table page 219. The scanned stem clearly reads “Aδ fibers do not transmit”; answer A is slow pain. | Restores Aδ notation and preserves the populated source comparison as `displayTables`, including stimuli, myelination/tract, speeds, pain components, and transmitters. `resolved_reconstruction`. |
| `marrow__PHYS_CH11_Q009` | Stem/options page 212; key page 215; solution page 220. The solution explicitly says the “most potent” ranking is controversial and cites Guyton and Hall. | Keeps bradykinin as the keyed best answer and teaches it as a potent algogen without presenting a universal potency ranking. Notes PGE2 sensitization and substance P's nociceptive role. `needs_manual_review` for the unqualified comparative superlative. |
| `marrow__PHYS_CH11_Q010` | Stem/options page 212; key page 215; solution page 220. Key D is vibration. The source solution's first sentence contradicts the question/key; choices “Heat” and “Thermal” overlap. | Corrects the explanation-layer negation: TRPV1 is not activated by vibration; heat, capsaicin, and protons are established stimuli. Records the duplicate heat/thermal choices. `resolved_reconstruction`. |

The scanned source was rendered directly from `data/marrow/source_pdfs/physiologyed8.pdf` at its printed pages before drafting. The source answer keys were checked against the imported question records. The candidate does not change or gate any source question.

## Medical references checked

- Caterina MJ, et al. “The capsaicin receptor: a heat-activated ion channel in the pain pathway.” *Nature*. 1997;389:816–824. PMID [9338776](https://pubmed.ncbi.nlm.nih.gov/9338776/).
- Aneiros E, et al. “The biophysical and molecular basis of TRPV1 proton gating.” *EMBO J*. 2011;30:994–1002. PMID [21285946](https://pubmed.ncbi.nlm.nih.gov/21285946/).
- Kindgen-Milles D. “Effects of prostaglandin E2 on the intensity of bradykinin-evoked pain from skin and veins of humans.” *Eur J Pharmacol*. 1995;294(2–3):491–496. PMID [8750710](https://pubmed.ncbi.nlm.nih.gov/8750710/).
- Mizumura K, et al. “Excitation and sensitization of nociceptors by bradykinin: what do we know?” *Exp Brain Res*. 2009;196:53–65. PMID [19396590](https://pubmed.ncbi.nlm.nih.gov/19396590/).
- Otsuka M. “In vivo molecular signal transduction of peripheral mechanisms of pain.” *Jpn J Pharmacol*. 1999;79(3):263–268. PMID [10230852](https://pubmed.ncbi.nlm.nih.gov/10230852/).

## Candidate artifact

`data/marrow/explanation_physio_ch11_q007_q010_v1.json`

## Second candidate batch

- Source-order range: Marrow Physiology Chapter 11, Q11–Q18.
- Exact IDs: `marrow__PHYS_CH11_Q011`–`marrow__PHYS_CH11_Q018` (8 questions).
- Workload: **17 / 20** (target 16), one contiguous source-order block.
- Candidate file: `data/marrow/explanation_physio_ch11_q011_q018_v1.json`.
- No question-completeness gate is recorded for these eight IDs.

This batch preserves the source's thermal-receptor thresholds and fiber groups, Weber–Fechner/specific-nerve-energy/projection laws, phantom-limb cortical reorganization, allodynia/hyperalgesia distinctions, endocannabinoid and PAG/medullary pain modulation, visceral referral/convergence and fiber table, pain-insensitive structures, and TENS gate-control diagram. Q11 and Q16 use populated `displayTables` pinned to their inspected source pages. The Aδ/C table's source transmitter association remains in prose; the table contains the four rows directly visible in the comparison. Q15 clarifies an imprecise “anandamide-containing neurons” phrase while retaining keyed option C. Q17 explicitly retains bile ducts and bronchi among pain-sensitive structures.

| ID | Source review | Refinement / status |
|---|---|---|
| `marrow__PHYS_CH11_Q011` | Stem page 212; key page 215; thermal receptor table page 220. | Restores OCR-damaged °C values and receptor-fiber rows in a populated table. `resolved_reconstruction`. |
| `marrow__PHYS_CH11_Q012` | Stem page 213; key page 215; solution page 221. | Preserves the log-intensity relationship plus the source's doctrines of specific nerve energies and projection. |
| `marrow__PHYS_CH11_Q013` | Stem page 213; key page 215; solution page 221. | Reconstructs legible cortical-reorganization explanation from severe imported OCR; keeps cortical plasticity as the keyed mechanism. `resolved_reconstruction`. |
| `marrow__PHYS_CH11_Q014` | Stem page 213; key page 215; solution page 221. | Preserves allodynia vs hyperalgesia, sunburn mediators, analgesia, and causalgia distinctions. |
| `marrow__PHYS_CH11_Q015` | Stem page 213; key page 215; solution pages 221–222. | Qualifies “anandamide-containing neurons” as stimulus-associated PAG release; retains CB1/CB2 distinction, antinociception, and the source's PAG→medullary/raphe relationship with an explicit circuit qualification. `resolved_reconstruction`. |
| `marrow__PHYS_CH11_Q016` | Stem page 214; key page 215; solution/table page 222. | Restores thoracic/abdominal origin, C-fiber transmission, visceral/somatic convergence, dorsal-horn→thalamus→somatosensory-cortex sequence, heart/arm example, and populated Aδ/C comparison table. `resolved_reconstruction`. |
| `marrow__PHYS_CH11_Q017` | Stem page 214; key page 215; solution page 222. | Preserves alveoli/liver parenchyma insensitivity and liver capsule, bile duct, bronchi, arterial wall, and parietal pleura sensitivity. |
| `marrow__PHYS_CH11_Q018` | Stem page 214; key page 215; solution/figure pages 222–223. | Restores Aδ/Aβ notation and preserves large-fiber activation, inhibitory interneuron, substantia gelatinosa gate, Aδ/C nociceptive input, plus source clinical examples. `resolved_reconstruction`. |

Medical source checked for Q15:

- Walker JM, et al. “Pain modulation by release of the endogenous cannabinoid anandamide.” *Science*. 1999;283(5409):401–404. PMCID [PMC18435](https://pmc.ncbi.nlm.nih.gov/articles/PMC18435/).
- Hohmann AG, et al. “An endocannabinoid mechanism for stress-induced analgesia.” *Nature*. 2005;435:1108–1112. DOI [10.1038/nature03658](https://doi.org/10.1038/nature03658).

Next source-order question is Chapter 11 Q19. Both Chapter 11 candidates remain unapproved and absent from the runtime preview until the canonical writer completes source/cell review and the wave's exact-head verification.

Parent source-page follow-up: independently inspected rendered pages 219, 220 and 222. Restored the fifth neurotransmitter row to both Aδ/C tables: Q8 continues from page 219 onto 220, and Q16 contains it on 222. Columns/cell ownership and complete source row order are preserved; the prose qualifies these as exam associations rather than exclusive transmitter identities.

Raw provenance has inaccurate explanation-page associations for Q8 and Q11 (220/221 rather than the table start at219/220). The native table source_page and independent page inspection establish ownership. Reviewed reconstruction metadata pins the exact PDF hash and actual table/continuation sourcePages; imported provenance remains immutable.
