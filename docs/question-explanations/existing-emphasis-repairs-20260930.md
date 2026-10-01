# Existing Biochemistry emphasis repairs — 2026-09-30

These nine records were already approved and counted in the 670 enhanced IDs. Only their `emphasis` arrays changed; the display text, takeaways, rationales, source/status fields, and inventory were left untouched. Each replacement was checked as an exact substring of that record's existing `displayText`, then checked against its source-backed teaching point.

| Existing stable ID | Previous anchors | Repaired verbatim anchors |
|---|---|---|
| `marrow__BIOCHEM_CH13_Q007` | `one FADH2`; `one NADH`; `acetyl-CoA`; `shortened by two carbons` | `acyl-CoA dehydrogenase produces FADH2`; `β-hydroxyacyl-CoA dehydrogenase produces NADH`; `Thiolysis then releases acetyl-CoA`; `shortened by two carbons` |
| `marrow__BIOCHEM_CH13_Q010` | `fetal long-chain 3-hydroxyacyl-CoA dehydrogenase`; `LCHAD`; `long-chain fatty-acid metabolites`; `maternal hepatic mitochondrial toxicity` | `defect of long-chain 3-hydroxyacyl-CoA dehydrogenase (LCHAD)`; `fetal/placental long-chain fatty-acid metabolites`; `maternal hepatic mitochondrial toxicity`; `particularly late in pregnancy` |
| `marrow__BIOCHEM_CH13_Q011` | `MCAD deficiency`; `hypoketotic hypoglycemia`; `ω-oxidation`; `dicarboxylic acids` | `blocks mitochondrial β-oxidation of medium-chain fatty acids`; `hypoketotic hypoglycemia and seizures`; `ω-oxidation`; `medium-chain dicarboxylic acids` |
| `marrow__BIOCHEM_CH13_Q012` | `Zellweger spectrum disorder`; `peroxisomal β-oxidation`; `very-long-chain fatty acids`; `H2O2` | `Zellweger spectrum disorder`; `Peroxisomal β-oxidation normally shortens very-long-chain fatty acids`; `transfers electrons ultimately to oxygen`; `generating H2O2` |
| `marrow__BIOCHEM_CH10_Q033` | `tertiary structure is the three-dimensional`; `Denaturation disrupts secondary and tertiary structure`; `without hydrolyzing the peptide bonds of primary structure`; `disulfide bonds` | `Tertiary structure is the three-dimensional arrangement of these elements into a functional fold`; `Denaturation disrupts secondary and tertiary structure`; `without hydrolyzing the peptide bonds of primary structure`; `disulfide bonds are important in tertiary structure` |
| `marrow__BIOCHEM_CH18_Q009` | `do not catalyze drug carboxylation`; `Cytochrome P450`; `monooxygenases`; `hydroxylation` | `Cytochrome P450 enzymes are heme-containing monooxygenases`; `endoplasmic reticulum of the liver and intestine`; `hydroxylation reactions involved in drug modification and degradation`; `Monooxygenases incorporate one oxygen atom into the substrate` |
| `marrow__BIOCHEM_CH19_Q019` | `graph A`; `option B`; `high-energy transition state`; `reduce activation energy` | `graph A as the valid Gibbs free-energy profile`; `high-energy transition state`; `Enzymes reduce activation energy`; `overall ΔG of the reaction remains unchanged` |
| `marrow__BIOCHEM_CH22_Q006` | `methionine synthase`; `methylmalonyl-CoA mutase`; `1 and 4`; `homocysteine to methionine` | `Methionine synthase (homocysteine methyltransferase) converts homocysteine to methionine`; `Methylmalonyl-CoA mutase converts methylmalonyl-CoA to succinyl-CoA`; `items 1 and 4`; `Vitamin B12 deficiency can therefore disturb methionine/folate handling and methylmalonyl-CoA metabolism` |
| `marrow__BIOCHEM_CH14_Q003` | `hexose monophosphate (HMP) shunt`; `cytosolic NADPH`; `major hepatic source`; `malic enzyme` | `hexose monophosphate (HMP) shunt`; `generates cytosolic NADPH and ribose`; `NADPH can be used directly for lipogenesis`; `malic enzyme provide smaller additional amounts` |

## Verification

- Parsed all three approved augmentation JSON files.
- Confirmed all nine stable IDs remain in the approved enhanced-ID set; the deterministic enhanced total remains **670**.
- Confirmed each replacement array has 1–4 anchors and every anchor is a verbatim substring of its existing display text.
- Compared each targeted record with the pre-change `HEAD`: only `emphasis` differs. No question was added, removed, or reclassified, so this repair does not increment the enhanced count.
