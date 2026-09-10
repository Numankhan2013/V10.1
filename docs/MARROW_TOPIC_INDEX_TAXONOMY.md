# Marrow topic-index taxonomy — user-authored grouping contract

> Status: **implemented for Anatomy, Biochemistry, and Physiology**.
>
> This is navigation taxonomy only. It must never rewrite, merge, split, renumber, or medically alter source question records.

## Two-layer model

The Topics journey deliberately separates:

1. **Source identity** — immutable Marrow topic/chapter IDs, exact source titles, question linkage, provenance, history, and FSRS identity.
2. **Learner index metadata** — intended major-index order, planned syllabus slots, current source placement, and learner-facing order/numbering.

`data/marrow/topic_index_taxonomy.json` is the editable source of truth. Each revised subject uses `catalogVersion: 2`, a complete `plannedIndex`, current imported `topics`, `plannedSlots`, and `displayNumbering: visible-contiguous`.

### Rendering rules

- Render only source topics currently present in the selected Marrow bank.
- Never render a blank row, disabled placeholder, spacer, or fake chapter for a planned topic that has not yet been imported.
- If planned topic B is unavailable while A and C are available, A and C appear adjacent.
- Hide a major index entirely when none of its planned topics currently has imported source material.
- Number learner-facing topics contiguously in the configured arranged order. Source chapter IDs stay unchanged underneath.
- A source chapter may therefore display a learner number unrelated to its source number when the major indexes are reordered.
- Keep combined/split source chapters source-faithful. `plannedSlots` records how one or more current source chapters relate to the finer planned syllabus; it never fabricates or duplicates questions.
- Future imports must be inserted using `plannedIndex` / `plannedSlots`, not guessed from source chapter numbers.

## Anatomy — authoritative intended order

1. **Embryology**
   - Gametogenesis
   - Pre-embryonic phase of development
   - Embryonic phase of development
   - Placenta
   - Fetal membranes and twinning
   - Pharyngeal arches
   - Skeleton and muscular system
   - Cardiovascular system
   - Respiratory system
   - Elementary hepatobiliary systems and pancreas and spleen
   - Face, nose and palate
   - Eye and ear
   - Nervous system and endocrine glands
   - Urogenital system
2. **Histology**
   - Cell structure
   - Epithelia, glands, and connective tissue
   - Bone, cartilage, and muscular tissue
   - Nervous and endocrine systems
   - Cardiovascular, lymphatic, and respiratory systems
   - Digestive, hepatobiliary, and genitourinary systems
   - Skin and special senses: eye and ear
3. **Neuroanatomy**
   - Cranial nerves
   - Meninges and dural venous sinuses
   - Ventricular systems and supratentorial space
   - Cerebrum
   - White matter of the brain
   - Basal ganglia and limbic system
   - Diencephalon
   - Brainstem
   - Cerebellum
   - Vascular supply of brain
   - Spinal cord
4. **Head, neck, and face**
   - Osteology
   - Scalp and face
   - Deep fascia and triangle of the neck
   - Muscle and neurovascular anatomy of head and neck
   - Glands of the head and neck
   - Tongue and palate
   - Pharynx
   - Larynx
5. **Upper limb**
   - Upper limb bones and joints
   - Fossa and spaces of the upper limb
   - Breast
   - Brachial plexus and nerves
   - Muscle of upper limb
   - Vessels of upper limb
6. **Thorax**
   - General anatomy of thorax
   - Thoracic wall
   - Mediastinum
   - Diaphragm
   - Heart
   - Lungs and pleura
7. **Abdomen and pelvis**
   - Anterior abdominal wall
   - Abdominal cavity and peritoneum
   - GI tract
   - Hepatobiliary system
   - Spleen and pancreas
   - Kidneys and adrenal gland
   - Internal and external genitalia
   - Pelvis and perineum
8. **Lower limb**
   - Bones of lower limb
   - Joints of lower limb
   - Muscles of lower limb
   - Nerves and vessels of lower limb
   - Important structures of lower limb
9. **Back**
   - Vertebral column
10. **General anatomy**
   - Bones, joints, and cartilage
   - Muscles and tendon
   - Cardiovascular, lymphatic, and nervous systems
   - Skin
   - Connective tissue and ligaments

### Current Anatomy import

Current source remains **48 topics / 819 questions**. Ch 1–10 map to Embryology; 11–16 Histology; 17–27 Neuroanatomy; 28–34 Head, neck, and face; 35–40 Upper limb; 41–46 Thorax; 47–48 Abdomen and pelvis. Lower limb, Back, and General anatomy are planned metadata only at the current import boundary and therefore do not render.

Combined source chapters remain combined; examples include Ch 4, 5, 6, 8, 11, and 28. Their `plannedSlots` preserve the finer intended placement without inventing learner topics.

## Biochemistry — authoritative intended order

1. **Carbohydrates**
   - Chemistry of carbohydrates
   - Amino sugars and mucopolysaccharides
   - Glycolysis and gluconeogenesis
   - Glycogen metabolism and glycogen storage disorders
   - HMP shunt pathway
   - Fructose and galactose metabolism
   - ETC and bioenergetics
   - Krebs cycle
2. **Amino acids and proteins**
   - Amino acid basics
   - Amino acid metabolism
   - Amino acid metabolic disorder
   - Protein structure and function
   - Urea cycle and its disorders
3. **Lipids**
   - Lipid basics
   - Fatty acid oxidation and ketogenesis
   - Biosynthesis of fatty acids and eicosanoids
   - Metabolism of acylglycerols and sphingolipids
   - Cholesterol synthesis, transport, and excretion
4. **Enzymes and phenylketonuria**
   - Phenylketonuria and bile pigments
   - Enzyme mechanism of action and clinical importance
   - Enzyme kinetics and regulation of activity
5. **Clinical biochemistry and nutrition**
   - Fats
   - Soluble vitamins
   - Energy-releasing vitamins
   - Hematopoietic and other vitamins
   - Antioxidants and minerals
6. **Genetics**
   - Basics of genetics
   - Nucleotide metabolism and disorders
   - DNA organization, replication, and repair
   - RNA synthesis, processing, and modification
   - Regulation of gene expression
   - Molecular genetics and recombinant DNA and genomic technology

### Current Biochemistry import

Current source remains **26 topics / 543 questions** and displays 1–26. Ch 1–6 map to Carbohydrates; 7–11 Amino acids and proteins; 12–16 Lipids; 17–19 Enzymes and phenylketonuria; 20–23 Clinical biochemistry and nutrition; 24–26 Genetics. The intended learner catalog contains 32 planned slots. Missing future slots remain metadata-only.

Current combined source chapters stay intact: Ch 1 maps to the first two carbohydrate slots; Ch 4 maps to HMP + fructose/galactose; Ch 20 maps to Fats + Soluble vitamins; Ch 24 maps to Basics of genetics + Nucleotide metabolism and disorders.

## Physiology — authoritative intended order

1. **General physiology**
   - Homeostasis and cellular physiology
   - Cellular messengers and receptors
   - Transport across the cell membrane
   - Membrane potentials
   - Body fluids
2. **Nerve and muscle physiology**
   - Physiology of nerve
   - Muscle physiology
   - Synapse and junctional transmission
3. **Gastrointestinal system**
   - Gastrointestinal secretion
   - Gastrointestinal hormones
   - Digestion and absorption
   - GI peristalsis and motility
4. **Cardiovascular system**
   - Vascular system and regional circulation
   - Cardiac cycle and cardiac output
   - Electrophysiology of the heart
   - Blood pressure and regulation
5. **Respiratory system**
   - Functional anatomy
   - Lung mechanics
   - Alveolar gas exchange
   - Gas transport in the lung volumes and lung function tests
   - Respiratory adaptations in hypoxia, anemia, and pressure changes
   - Regulations of respiration
6. **Renal physiology**
   - Glomerular filtration rate, renal blood flow, and renal clearance
   - Renal tubular functions, urine concentration and dilution, and acid-base physiology
   - Renal hormones and maturation reflex
7. **Endocrine physiology**
   - Pituitary and thyroid
   - The pancreas
   - The adrenals
   - Calcium homeostasis
8. **Reproductive physiology**
   - Male reproductive physiology
   - Female reproductive physiology
9. **Central nervous system**
   - Neurotransmitters
   - Sensory receptors
   - Somatosensory pathways
   - Special senses
   - Motor physiology
   - Basal ganglia
   - Cerebellum
   - Hypothalamus
   - Limbic system
   - Higher mental functions
10. **Integrated physiology**
   - Exercise physiology

### Current Physiology import and arranged learner order

Current source remains exactly **33 topics / 753 questions**. Source chapter IDs are deliberately not renumbered. The learner-facing order is instead derived from the new major-index sequence:

- General physiology: source Ch 1–5
- Nerve and muscle physiology: source Ch 6–9
- Gastrointestinal system: source Ch 31–33
- Cardiovascular system: source Ch 26–30
- Respiratory system: source Ch 19–25
- Central nervous system: source Ch 10–18

Therefore the current arranged source-ID sequence is:
`1–9, 31–33, 26–30, 19–25, 10–18`, while the learner sees contiguous display numbers **1–33**.

**Renal physiology, Endocrine physiology, Reproductive physiology, and Integrated physiology currently have no imported source chapters in the Ch 1–33 bundle, so they remain in `plannedIndex` but do not render.**

Source splits/combinations are represented only through `plannedSlots`:
- Muscle Physiology I + II (Ch 7–8) both map to planned **Muscle physiology**.
- Motor Physiology 1 + 2 (Ch 14–15) both map to planned **Motor physiology**.
- Ch 16 maps to planned **Basal ganglia** + **Cerebellum**.
- Ch 17 maps to planned **Hypothalamus** + **Limbic system**.
- Vascular System I + II (Ch 26–27) both map to planned **Vascular system and regional circulation**.
- Gas Transport in Blood (Ch 22) + Lung Volumes/Lung Function Tests (Ch 23) both map to the supplied combined respiratory slot.
- Ch 31 maps to planned **Gastrointestinal secretion** + **Gastrointestinal hormones**.

## Implementation contract

1. Keep one editable taxonomy source of truth in `data/marrow/topic_index_taxonomy.json`.
2. Preserve stable subject + source topic IDs, exact source titles, question linkage, source provenance, history, and FSRS identity.
3. Treat planned slots as learner-navigation metadata, never fabricated source chapters.
4. Omit unavailable planned topics and empty indexes from learner-facing navigation.
5. Number visible learner topics contiguously in configured arranged order; never mutate backend/source IDs to achieve this.
6. Preserve All / In Progress / Completed / Not Started, search, Topic Index, and the fixed Continue Learning tray.
7. Preserve bank/subject context, question linkage, Practice/CBT/Review, sync, persistence, and Back behavior.
8. Do not rewrite medical content during taxonomy work.
9. Tests must assert source-topic preservation, exact intended catalog order, valid `plannedSlots`, no drops/duplicates, no empty rendered groups, and contiguous learner numbering.
10. Keep the user-approved Topics journey/glow/fixed-tray visuals unchanged.
