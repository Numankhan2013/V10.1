# Marrow topic-index taxonomy — user-authored grouping contract

> Status: **implemented for Anatomy and Biochemistry; their future-slot metadata is authoritative**.
> Physiology remains on its previously recorded taxonomy until the user supplies its revised arrangement.
>
> This is navigation taxonomy only. It must never rewrite, merge, split, renumber, or medically alter the source question records.

## Why this exists

The Topics journey UI is visually approved, but Marrow source chapter numbers and the learner's desired index arrangement are different concepts. The app therefore keeps two layers:

1. **Source identity** — immutable Marrow topic/chapter IDs, source titles, question linkage, provenance, history, and FSRS identity.
2. **Learner index metadata** — the intended major-index order, future topic slots, current placement, and learner-facing order.

`data/marrow/topic_index_taxonomy.json` is the editable source of truth. Anatomy uses `catalogVersion: 2`, a complete `plannedIndex`, current imported `topics`, and `displayNumbering: visible-contiguous`.

### Rendering rules

- Render only topics that currently exist in the selected Marrow bank.
- Never render a blank row, disabled placeholder, spacer, or fake chapter for a planned topic that has not yet been imported.
- If planned topic B is missing while A and C are present, A and C appear adjacent to the learner.
- Major indexes with zero currently imported topics are omitted from the learner UI, while their complete intended contents remain in metadata.
- Learner-facing topic numbering follows the currently visible arranged sequence. Source IDs remain untouched in the backend. A source chapter that is internally `19` may therefore be the learner's fifth visible topic if only four arranged topics precede it.
- Combined current source chapters are not artificially split. Instead, `plannedSlots` records every future syllabus slot represented by that current source chapter.
- When later source topics arrive, integrate them against `plannedIndex` and their intended slot rather than guessing from numeric chapter IDs or title ranges.

## Anatomy — authoritative intended major-index order

1. **Embryology**
2. **Histology**
3. **Neuroanatomy**
4. **Head, neck, and face**
5. **Upper limb**
6. **Thorax**
7. **Abdomen and pelvis**
8. **Lower limb**
9. **Back**
10. **General anatomy**

### Embryology

1. Gametogenesis
2. Pre-embryonic phase of development
3. Embryonic phase of development
4. Placenta
5. Fetal membranes and twinning
6. Pharyngeal arches
7. Skeleton and muscular system
8. Cardiovascular system
9. Respiratory system
10. Elementary hepatobiliary systems and pancreas and spleen
11. Face, nose and palate
12. Eye and ear
13. Nervous system and endocrine glands
14. Urogenital system

### Histology

1. Cell structure
2. Epithelia, glands, and connective tissue
3. Bone, cartilage, and muscular tissue
4. Nervous and endocrine systems
5. Cardiovascular, lymphatic, and respiratory systems
6. Digestive, hepatobiliary, and genitourinary systems
7. Skin and special senses: eye and ear

### Neuroanatomy

1. Cranial nerves
2. Meninges and dural venous sinuses
3. Ventricular systems and supratentorial space
4. Cerebrum
5. White matter of the brain
6. Basal ganglia and limbic system
7. Diencephalon
8. Brainstem
9. Cerebellum
10. Vascular supply of brain
11. Spinal cord

### Head, neck, and face

1. Osteology
2. Scalp and face
3. Deep fascia and triangle of the neck
4. Muscle and neurovascular anatomy of head and neck
5. Glands of the head and neck
6. Tongue and palate
7. Pharynx
8. Larynx

### Upper limb

1. Upper limb bones and joints
2. Fossa and spaces of the upper limb
3. Breast
4. Brachial plexus and nerves
5. Muscle of upper limb
6. Vessels of upper limb

### Thorax

1. General anatomy of thorax
2. Thoracic wall
3. Mediastinum
4. Diaphragm
5. Heart
6. Lungs and pleura

### Abdomen and pelvis

1. Anterior abdominal wall
2. Abdominal cavity and peritoneum
3. GI tract
4. Hepatobiliary system
5. Spleen and pancreas
6. Kidneys and adrenal gland
7. Internal and external genitalia
8. Pelvis and perineum

### Lower limb

1. Bones of lower limb
2. Joints of lower limb
3. Muscles of lower limb
4. Nerves and vessels of lower limb
5. Important structures of lower limb

### Back

1. Vertebral column

### General anatomy

1. Bones, joints, and cartilage
2. Muscles and tendon
3. Cardiovascular, lymphatic, and nervous systems
4. Skin
5. Connective tissue and ligaments

## Current Marrow Anatomy Ch 1–48 placement

The current imported source records remain exactly 48 source topics and 819 questions. They are arranged as follows:

- Ch 1–10 → **Embryology**
- Ch 11–16 → **Histology**
- Ch 17–27 → **Neuroanatomy**
- Ch 28–34 → **Head, neck, and face**
- Ch 35–40 → **Upper limb**
- Ch 41–46 → **Thorax**
- Ch 47–48 → **Abdomen and pelvis**

At the current import boundary, **Lower limb**, **Back**, and **General anatomy** have no imported Marrow topics and therefore must not render as empty learner-facing sections.

Some current source chapters represent more than one intended syllabus slot. Examples include Ch 4 `Placenta, Fetal Membranes and Twinning`, Ch 5 `Pharyngeal arches, Skeletal & Muscular Systems`, Ch 6 `Cardiovascular and Respiratory Systems`, Ch 8 `Face, Nose & Palate, Eye, Ear`, Ch 11 `Cell Structure, Epithelia, Glands & Connective Tissue`, and Ch 28 `Osteology, Scalp and Face`. These remain single source topics today; `plannedSlots` records their relationship to the finer intended catalog without inventing unavailable learner topics.

## Physiology — existing taxonomy retained pending user revision

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

Current Ch 1–33 mappings in `topic_index_taxonomy.json` remain unchanged until the user supplies the revised Physiology arrangement.

## Biochemistry — authoritative intended major-index order

1. **Carbohydrates**
2. **Amino acids and proteins**
3. **Lipids**
4. **Enzymes and phenylketonuria**
5. **Clinical biochemistry and nutrition**
6. **Genetics**

### Carbohydrates

1. Chemistry of carbohydrates
2. Amino sugars and mucopolysaccharides
3. Glycolysis and gluconeogenesis
4. Glycogen metabolism and glycogen storage disorders
5. HMP shunt pathway
6. Fructose and galactose metabolism
7. ETC and bioenergetics
8. Krebs cycle

### Amino acids and proteins

1. Amino acid basics
2. Amino acid metabolism
3. Amino acid metabolic disorder
4. Protein structure and function
5. Urea cycle and its disorders

### Lipids

1. Lipid basics
2. Fatty acid oxidation and ketogenesis
3. Biosynthesis of fatty acids and eicosanoids
4. Metabolism of acylglycerols and sphingolipids
5. Cholesterol synthesis, transport, and excretion

### Enzymes and phenylketonuria

1. Phenylketonuria and bile pigments
2. Enzyme mechanism of action and clinical importance
3. Enzyme kinetics and regulation of activity

### Clinical biochemistry and nutrition

1. Fats
2. Soluble vitamins
3. Energy-releasing vitamins
4. Hematopoietic and other vitamins
5. Antioxidants and minerals

### Genetics

1. Basics of genetics
2. Nucleotide metabolism and disorders
3. DNA organization, replication, and repair
4. RNA synthesis, processing, and modification
5. Regulation of gene expression
6. Molecular genetics and recombinant DNA and genomic technology

## Current Marrow Biochemistry Ch 1–26 placement

The current imported source records remain exactly 26 source topics and 543 questions. They are arranged as follows:

- Ch 1–6 → **Carbohydrates**
- Ch 7–11 → **Amino acids and proteins**
- Ch 12–16 → **Lipids**
- Ch 17–19 → **Enzymes and phenylketonuria**
- Ch 20–23 → **Clinical biochemistry and nutrition**
- Ch 24–26 → **Genetics**

The enumerated learner catalog contains 32 planned slots. Missing future slots do not render. Current combined source chapters remain single source topics: Ch 1 maps to Chemistry of carbohydrates + Amino sugars and mucopolysaccharides; Ch 4 maps to HMP shunt pathway + Fructose and galactose metabolism; Ch 20 maps to Fats + Soluble vitamins; and Ch 24 maps to Basics of genetics + Nucleotide metabolism and disorders. Genetics slots for Regulation of gene expression and Molecular genetics/recombinant DNA/genomic technology are metadata-only until corresponding source topics are imported.

Learner-facing numbering is contiguous across the currently visible arranged source topics (1–26); source chapter IDs remain unchanged underneath.

## Implementation contract

1. Keep one editable taxonomy source of truth in `data/marrow/topic_index_taxonomy.json`.
2. Preserve stable subject + Marrow source topic IDs and exact source titles for current imported records.
3. Treat planned syllabus slots as navigation metadata, never as fabricated source chapters.
4. Omit unavailable planned topics and empty planned indexes from learner-facing navigation.
5. Learner-facing numbering is contiguous in arranged visible order; backend/source IDs are never rewritten to achieve it.
6. Preserve All / In Progress / Completed / Not Started, search, Topic Index, and the fixed Continue Learning tray.
7. Preserve bank/subject context, question linkage, history, FSRS state, and Back behavior.
8. Do not rewrite medical content during taxonomy work.
9. Tests must assert exact source-topic preservation, exact intended catalog order, valid `plannedSlots`, no dropped or duplicated topics, no empty rendered groups, and no learner-facing ordering jumps in the current import.
10. Keep the user-approved journey/glow/fixed-tray visual implementation unchanged.
