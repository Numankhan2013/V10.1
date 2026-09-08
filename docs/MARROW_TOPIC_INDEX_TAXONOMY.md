# Marrow topic-index taxonomy — user-authored grouping contract

> Status: **specification only; not yet implemented**.
> Source of truth for the next Topics grouping correction on
> `feature/marrow-bank-pilot`.
>
> This is navigation taxonomy only. It must never rewrite, merge, split, or
> medically alter question content.

## Why this exists

The recovered Topics journey UI is now visually good and physically confirmed by
the user, but the **major index labels/grouping are not source-true**. The next
implementation must preserve the approved journey UI and replace heuristic
grouping with one explicit, centralized, reviewable
`subject + topic/chapter -> major index` mapping.

Topic order inside each major index follows Marrow source/chapter order, not
alphabetical order. PYQ / Previous Year Questions topics belong at the end of
their corresponding major index whenever present. Ambiguous cross-system topics
must be marked for review instead of silently guessed.

## Anatomy — required major-index order

1. **General Embryology**
2. **Histology**
3. **Osteology & Arthrology**
4. **Neuroanatomy**
5. **Head & Neck**
6. **Upper Limb**
7. **Lower Limb**
8. **Thorax**
9. **Abdomen**
10. **Pelvis & Perineum**
11. **Back Region**
12. **Systemic Embryology**

### User-defined content expectations

- **General Embryology**: Gametogenesis/IVF; fertilization and early embryonic
  life / first two weeks; developmental period / general embryology; then PYQs.
- **Histology**: Histology I, II, III; integumentary and special-sensory
  histology; then PYQs.
- **Osteology & Arthrology**: Osteology/arthrology I and II; then PYQs.
- **Neuroanatomy**: all neuroanatomy topics in source order; then PYQs.
- **Head & Neck**: pharyngeal arches/pouches/clefts; head-and-neck anatomy;
  skull foramina/scalp; skull bones/cranial cavity parts; cranial nerves and
  cervical plexus; scalenes/anterior neck; head/neck vasculature and lymphatic
  drainage; scalp/neck triangles/parotid; pharynx; esophagus/larynx parts;
  ear/nose/eyeball; then PYQs.
- **Upper Limb**, **Lower Limb**, **Thorax**, **Abdomen**,
  **Pelvis & Perineum**, **Back Region**: all matching regional topics in source
  order, with each section's PYQs last.
- **Systemic Embryology**: systemic-embryology source topics/PYQs not assigned to
  General Embryology or an explicitly regional section.

### Current Marrow Anatomy Ch 1–48 guidance

Locked current mappings:
- Ch 1–4 → **General Embryology**.
- Ch 11–16 → **Histology**.
- Ch 17–27 → **Neuroanatomy**.
- Ch 28–34 → **Head & Neck**.
- Ch 35–40 → **Upper Limb**.
- Ch 41–46 → **Thorax**.
- Ch 47–48 → **Abdomen**.

Current cross-system embryology chapters need explicit reviewed placement:
- Ch 5 `Pharyngeal arches / skeletal / muscular` — strongly Head & Neck.
- Ch 6 `Cardiovascular / respiratory` — review Thorax vs Systemic Embryology.
- Ch 7 `Alimentary / hepatobiliary / pancreas / spleen` — review Abdomen vs
  Systemic Embryology.
- Ch 8 `Face / nose / palate / eye / ear` — strongly Head & Neck.
- Ch 9 `Nervous / endocrine` — review Neuroanatomy vs Systemic Embryology.
- Ch 10 `Urogenital system` — review Pelvis & Perineum vs Systemic Embryology.

Do not move the existing Upper Limb bones/joints chapter into the separate
Osteology & Arthrology index merely because it contains bones/joints; keep
region-specific content regional unless the source supplies dedicated general
osteology topics.

Lower Limb, later Pelvis/Perineum, Back Region, standalone Osteology/Arthrology,
later PYQs and later systemic-embryology topics should slot into the fixed order
above when those chapters arrive.

## Physiology — required major-index order

1. **CNS Physiology**
2. **Exercise Physiology**
3. **General Physiology**
4. **Cellular Physiology**
5. **Neuromuscular Physiology**
6. **Nervous System**
7. **Cardiovascular System**
8. **Blood Physiology**
9. **Renal Physiology**
10. **Respiratory System**
11. **Gastrointestinal System**
12. **Endocrine System**
13. **Miscellaneous**
14. **Reproductive System**
15. **Recent Updates**

The user allows **Miscellaneous** and **Recent Updates** to be absorbed into a
better-fitting major index when the relationship is clear.

### Current Physiology Ch 1–33 mapping

- Ch 1 Homeostasis/cellular physiology → **General Physiology**.
- Ch 2–5 messengers/receptors; transport; membrane potentials; body fluids →
  **Cellular Physiology**.
- Ch 6–10 nerve; Muscle I/II; synapse/junction; neurotransmitters →
  **Neuromuscular Physiology**.
- Ch 11–18 sensory receptors; somatosensory pathways; special senses; motor I/II;
  basal ganglia/cerebellum; hypothalamus/limbic; higher mental functions →
  **CNS Physiology**.
- Ch 19–25 respiratory functional anatomy through regulation →
  **Respiratory System**.
- Ch 26–30 vascular/regional circulation through BP regulation →
  **Cardiovascular System**.
- Ch 31–33 GI secretion/hormones; digestion/absorption; motility →
  **Gastrointestinal System**.

Exercise, separate Nervous System, Blood, Renal, Endocrine, Reproductive,
Miscellaneous and Recent Updates are mostly later-source territory outside the
current Ch 1–33 import. Do not fabricate empty learner-facing groups unless
explicitly desired.

## Biochemistry — required major-index order

1. **Introduction**
2. **Carbohydrate Chemistry**
3. **Lipid Chemistry**
4. **Amino Acid & Protein Chemistry**
5. **Heme Synthesis**
6. **Enzymes**
7. **Free Radicals, Antioxidants, Trace Elements & Miscellaneous**
8. **Genetics**
9. **Vitamins**

### Current Biochemistry Ch 1–26 mapping

- Ch 1–6 → **Carbohydrate Chemistry**.
- Ch 7–11 → **Amino Acid & Protein Chemistry**.
- Ch 12–16 → **Lipid Chemistry**.
- Ch 17 → **Heme Synthesis**.
- Ch 18–19 → **Enzymes**.
- Ch 20–22 → **Vitamins**.
- Ch 23 → **Free Radicals, Antioxidants, Trace Elements & Miscellaneous**.
- Ch 24–26 → **Genetics**.
- **Introduction** is reserved for genuine introductory source topics; do not
  relabel carbohydrate Chapter 1 as Introduction.

Concrete correction from physical review: current heading
`Carbohydrates & Bioenergetics` is not the requested source index label.
Use **Carbohydrate Chemistry**.

## Implementation contract

1. One editable source-of-truth mapping; no scattered renderer conditions.
2. Prefer stable subject + Marrow chapter/topic IDs as keys; titles are assertions,
   not the only lookup key.
3. Preserve exact Marrow topic order within each index.
4. Preserve All / In Progress / Completed / Not Started, search, Topic Index,
   and the fixed Continue Learning tray.
5. Preserve bank/subject context and Back/history behavior.
6. Do not rewrite medical content during taxonomy work.
7. Tests must assert representative placements and that no topic is dropped or duplicated.
8. Ambiguous mappings are explicit review items, not heuristic guesses.
9. Keep the user-approved journey/glow/fixed-tray visual implementation unchanged.
