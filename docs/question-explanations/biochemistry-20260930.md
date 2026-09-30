# Biochemistry explanation refinement audit — 2026-09-30

## State and lineage

- Canonical base recorded at authoring: `81822e44753f5c3af7c2f2b0719d12230eed4478`.
- Raw Biochemistry source SHA-256: `919f0709b2eb833e302c6f7524b6dd2bd13bfaed638009375b5062135d3795b1`.
- Imported source bundles and the approved inventory were not edited. Both new augmentation files are `candidate-rollout`; nothing in this audit claims preview integration or release verification.
- The existing Chapter 14 Q1–Q8 file is already `approved-rollout` and contributes eight of the 670 enhanced IDs. Q9 is also already an approved reference. Open draft PR #76 proposes the same Q1–Q8 file on an older base; it is duplicate work, not an additional pending batch.

## Batch A — Chapter 13 Q17–Q20

The next pending source-order tail follows the approved Q1–Q16 augmentation. Q17–Q19 are authored in [the candidate file](../../data/marrow/explanation_biochem_ch13_q017_q019_v1.json) (3 questions; workload score 4). The explanations retain the source's ketolysis sequence, the Rothera test's positive purple ring, and the insulin-deficiency → HSL → lipolysis → β-oxidation → ketogenesis mechanism.

Q19 has `needs_manual_review` reconstruction metadata. The source key and explanation support increased fatty-acid oxidation to acetyl-CoA as the intended answer, but do not address option D (“decreased cholesterol synthesis”); its truth can vary with tissue, timing, and model. The draft rationale does not claim that cholesterol synthesis cannot decrease. The detailed pathway preserves the source's HSL disinhibition, lipolysis, β-oxidation, NADH/oxaloacetate shift, and named ketone products.

Q20 is deliberately absent from learner-facing augmentation. Its rendered question page omits numbered statements 1–4, while the combinations refer to those missing statements. The answer key and explanation identify “2, 3 and 4” and discuss mechanisms, but they cannot recover the exact number-to-statement mapping. No option rationales or reconstructed list were invented. Keep the source question gated pending recovery; it remains unrefined and is not part of the 3 authored questions.

## Batch B — Chapter 14 Q10–Q23

The next source-order range contains 14 questions, workload score 19.5. Twelve have candidate explanation entries in [the candidate file](../../data/marrow/explanation_biochem_ch14_q010_q023_v1.json). The chapter's two incomplete combination items are explicitly listed under `sourceLimitedItems` and have no invented distractor rationales:

- Q12's numbered organelle list is missing. The explanation names endoplasmic reticulum and mitochondria as the answer, but the option-to-organelle mapping cannot be verified.
- Q18's numbered intermediate list is missing. The explanation names PGG2 and PGH2 as unstable intermediates, but the displayed numeric combinations cannot be decoded safely.

Q13's printed enzyme symbol is a black square (`■9`). The source explanation explicitly uses Δ9, Δ9,12, and Δ9,12,15 notation, so the candidate restores only the well-supported `Δ9` display symbol and records the original fragment and evidence. It retains the source's NADPH statement and oxygen/mixed-function oxidase facts, then qualifies that standard mammalian SCD electron transfer is usually described through NADH-dependent cytochrome b5 reductase and cytochrome b5; broader descriptions allow NAD(P)-linked reductase systems. Q20's HTML `&amp;` option text is presented with normal “and” semantics in the explanation; the source option itself is unchanged.

The second source-detail pass restored the source's full FAS homodimer/ACP and enzyme-grouping facts (Q11), eicosanoid short-acting paracrine GPCR signaling (Q15), cyclic COX products (Q17), and primary-prostaglandin structural criteria (Q19). Q22 now distinguishes LTB4 leukocyte activation/chemotaxis from cysteinyl-leukotriene bronchoconstriction. Platelets are described as transcellular contributors with leukocytes rather than as a major autonomous 5-LOX source.

## Source and medical cross-checks

The source question, key, and explanation pages are pinned in each augmentation entry. The rendered source PDF confirmed the corrupted Q13 glyph directly. External checks used primary/authoritative literature for details that affect the teaching point:

- Human tissue distribution of SCOT/thiophorase: [PubMed 9380443](https://pubmed.ncbi.nlm.nih.gov/9380443/).
- Nitroprusside ketone test limits: [NCBI Clinical Methods: Ketonuria](https://www.ncbi.nlm.nih.gov/books/NBK247/).
- Insulin deficiency and hepatic ketogenesis: [NCBI Bookshelf: Biochemistry, Ketogenesis](https://www.ncbi.nlm.nih.gov/books/NBK493179/).
- Lung COX products and cell sources: [NCBI Bookshelf: Biologic Markers in Pulmonary Toxicology](https://www.ncbi.nlm.nih.gov/books/NBK218701/).
- Eicosanoid pathway and terminal synthase context: [Lipid Mediators review](https://pmc.ncbi.nlm.nih.gov/articles/PMC4088989/).
- Mammalian stearoyl-CoA desaturase electron transfer: [SCD biochemical review](https://pmc.ncbi.nlm.nih.gov/articles/PMC2711665/) and [mammalian SCD structure/mechanism](https://pmc.ncbi.nlm.nih.gov/articles/PMC7483794/).
- Leukotriene subclass effects and platelet/leukocyte cooperation: [NCBI leukotriene physiology](https://www.ncbi.nlm.nih.gov/books/NBK526114/) and [platelet-adherent leukocyte cysteinyl-leukotriene synthesis](https://ashpublications.org/blood/article/119/16/3790/29911/Cysteinyl-leukotriene-overproduction-in-aspirin).

## Static checks and remaining work

Both candidate JSON files parse. A source-mapping check confirmed every authored ID belongs to its declared Biochemistry chapter/range, all authored IDs remain outside the approved set, each emphasis anchor appears verbatim (1–4 per item), and each completed four-option item has exactly the three non-keyed option rationales. Ch14 Q12 and Q18 are accounted for as source-limited instead of being presented as completed refinements.

These are content-authoring checkpoints only. The candidates have not passed the repository rollout validator, learner-browser checks, exact-head Engineering, or full Android/PWA build, and have not been reconciled to canonical. Q20, Q12, Q18, and the Q19 option-D ambiguity remain explicit human/source-review work.
