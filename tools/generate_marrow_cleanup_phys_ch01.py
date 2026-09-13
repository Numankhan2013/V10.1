#!/usr/bin/env python3
"""Generate reviewed Physiology Ch1 explanation-only display overrides.

Rendered ED8 pages 11-19 were used as the authority. This script does not touch
raw source shards or answer indexes; it writes one source-fingerprinted v2
learner-display override file.
"""
from __future__ import annotations

import base64
import hashlib
import json
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "marrow"
OUT = DATA / "content_hygiene_overrides_v2" / "physiology" / "chapter_001.json"

CLEAN = {
    "marrow__PHYS_CH01_Q001": """Homeostasis is called dynamic equilibrium because the body maintains an internal balance within fluctuating limits. It describes the maintenance of nearly constant conditions in the internal environment despite changes in the outside world.

A number of variables such as body temperature, blood sugar levels and blood pH are regulated within a range of values (homeostatic ranges), and not at fixed values.

These variables are not given equal importance. There is a hierarchy of importance so that the constancy of certain variables may be altered markedly to maintain others within their normal range. For example, respiratory or metabolic compensation helps maintain blood pH.

Disruption of homeostasis, either due to an extreme environmental challenge or a breakdown of internal homeostatic mechanisms, is termed disease.""",
    "marrow__PHYS_CH01_Q002": """Stimulus, receptor and effector are all components of a homeostatic control system.

Components of homeostasis include:
• Stimulus — a detectable change in the internal or external environment, such as a change in temperature.
• Receptor — detects environmental changes.
• Integrating centre.
• Effector — an organ or cell that acts in response to a stimulus.""",
    "marrow__PHYS_CH01_Q003": """Feedback regulation is seen in the increased heart rate in response to a decrease in blood pressure. In feedback regulation, the homeostatic response (increased heart rate) occurs after the change (decrease in blood pressure) has occurred.

In feedforward regulation, the homeostatic response takes place before the change has occurred, in anticipation of the change, to minimize fluctuations.

Examples of feedforward regulation include:
• The increased heart rate that occurs in an athlete just before a sprint begins.
• The smell of food triggering secretion of salivary and gastric juices.
• An increase in insulin before glucose absorption has raised blood glucose levels.""",
    "marrow__PHYS_CH01_Q004": """Positive feedback is seen in all of the listed processes except gastric secretion, which is under negative feedback control.

Negative feedback consists of changes that affect a deficient or excessive variable to pull it back toward a mean value and maintain homeostasis. Most processes in the body are under negative feedback. For example, an increase in gastric acid leads to a decrease in gastric secretion.

Positive feedback consists of changes that affect a variable and push it farther away from a mean value. For example, an increase in LH leads to a further increase in LH.

Important examples of positive feedback include:
• Clotting of blood
• Calcium release from the sarcoplasmic reticulum
• LH surge
• Action potential
• Shock
• Parturition""",
    "marrow__PHYS_CH01_Q005": """The gain of the feedback system in the given case is −2.

The gain of the system is calculated using:
Gain = C/E
where C is the correction achieved from the deviated value and E is the remaining error after correction.

Calculation:
• Original value = 100 mmHg.
• Deviated value = 175 mmHg.
• Corrected value = 125 mmHg.
• C = 125 − 175 = −50 mmHg.
• E = 125 − 100 = 25 mmHg.
• Gain = −50/25 = −2.

The negative sign indicates that the homeostatic mechanism acts in a direction opposite to the initial deviation.""",
    "marrow__PHYS_CH01_Q006": """The plasma membrane in eukaryotes does not contain triglycerides.

The plasma membrane is composed almost entirely of proteins and lipids. The major lipids include:
• Phospholipids: lecithin, cephalin and phosphatidylserine
• Sphingolipids: sphingomyelin
• Cholesterol""",
    "marrow__PHYS_CH01_Q007": """Membrane fluidity is increased by linoleic acid, an unsaturated fatty acid. The other listed options are saturated fatty acids.

Longer and saturated fatty-acid side chains are straight and interact more strongly with one another. Unsaturated fatty acids increase membrane fluidity because their side chains are kinked and pack less compactly.

Cholesterol also helps maintain cell-membrane fluidity.""",
    "marrow__PHYS_CH01_Q008": """Cell-surface receptors are peripheral proteins.

Proteins in the plasma membrane include:
• Integral or transmembrane proteins, which span the thickness of the membrane. Examples include the insulin receptor, pumps, transport proteins (carriers) and G-protein-coupled receptors.
• Peripheral proteins, which are present on either the inner or outer surface of the membrane. Examples include cell-surface receptors and enzymes.""",
    "marrow__PHYS_CH01_Q009": """The inner mitochondrial membrane has the highest protein content per gram of tissue, whereas myelin has the lowest.

Protein-to-lipid ratios of different membranes include:
• Myelin: 0.23
• Human RBC: 1.1
• Mitochondrial outer membrane: 1.1
• Sarcoplasmic reticulum: 2.0
• Mitochondrial inner membrane: 3.2""",
    "marrow__PHYS_CH01_Q010": """The sequence of vesicular transport in a cell is ER → cis-Golgi → trans-Golgi → cell membrane.

Rough endoplasmic reticulum (RER) is the site of protein synthesis. Proteins are taken to the Golgi apparatus through transport vesicles.

The cis end of the Golgi apparatus, also called the receiving end, is closest to the RER. The trans end, also called the releasing end, is farthest from the RER.

At the cell membrane, synthesized proteins within secretory vesicles are released into the extracellular space by exocytosis.""",
    "marrow__PHYS_CH01_Q011": """5′-Nucleotidase is an enzyme marker for the plasma membrane. The other listed options are mitochondrial enzyme markers.""",
    "marrow__PHYS_CH01_Q012": """Mature red blood cells test negative for mitochondrial markers because they do not have mitochondria.

The lack of mitochondria is the reason red blood cells rely exclusively on anaerobic glycolysis to generate ATP.""",
    "marrow__PHYS_CH01_Q013": """Catalase is the characteristic enzyme of peroxisomes. The other listed enzymes are lysosomal enzymes.""",
    "marrow__PHYS_CH01_Q014": """Gap junctions are absent in adult skeletal muscle.

Gap junctions are intercellular connections with a channel between adjacent cells. They are present in excitable tissues such as cardiac muscle, smooth muscle and neurons, but not in skeletal muscle.""",
    "marrow__PHYS_CH01_Q015": """Tight junctions are not seen in cardiac muscle.

Tight junctions form a water-tight seal between cells. They are characteristically seen in:
• Intestinal mucosa
• Renal tubules
• Choroid plexus
• Sertoli cells

Functions of tight junctions include:
• Preventing diffusion of molecules between cells
• Maintaining cell polarity
• Sealing the paracellular pathway""",
    "marrow__PHYS_CH01_Q016": """Spectrin is a cytoskeletal protein but is not a cell-adhesion molecule.

Cells attach to each other or to the basal lamina through cell-adhesion molecules (CAMs). Important classes of CAMs include:
• Integrins — heterodimers that bind to various receptors
• Immunoglobulin-superfamily CAMs
• Cadherins — calcium-dependent molecules that mediate cell-to-cell adhesion by homophilic interactions
• Selectins — molecules with lectin-like domains that bind carbohydrates

Clinical significance: cancer cells may have abnormal CAMs and therefore decreased cell adhesion, allowing individual cancer cells to detach from the parent cancer. A decrease in E-cadherin may contribute to early metastasis of numerous tumors.""",
    "marrow__PHYS_CH01_Q017": """Gap junctions are made of connexons, and connexons are in turn made of units called connexins.

Important intercellular connections and their structural units include:
• Tight junction (zona occludens): occludins, claudins and junctional adhesion molecules
• Gap junction: connexons
• Zona adherens: cadherins
• Desmosome: cadherins such as desmoglein
• Hemidesmosome: integrins""",
    "marrow__PHYS_CH01_Q018": """Integrin connects with fibronectin.

Integrins are transmembrane glycoproteins (integral proteins) that allow cells to attach to extracellular-matrix constituents such as laminin, fibronectin and collagen. They help link the intracellular cytoskeleton functionally and structurally with the outside world.""",
    "marrow__PHYS_CH01_Q019": """The force-generating proteins include dynein and kinesin.

Molecular motors are force-generating proteins that move proteins, organelles and other cell components—collectively referred to as cargo—to different parts of the cell.""",
    "marrow__PHYS_CH01_Q020": """Absent dynein arms in cilia lead to primary ciliary dyskinesia. Kartagener syndrome is a form of primary ciliary dyskinesia characterized by the classic triad of situs inversus, chronic sinusitis and bronchiectasis.

Ciliocytophoria is the degradation of ciliated cells due to viral infections. It is not seen in primary ciliary dyskinesia.""",
    "marrow__PHYS_CH01_Q021": """Tubulin constitutes the microtubules that form the mitotic spindle in a dividing cell. Ubiquitin helps in protein degradation.

Cytoskeletal elements and associated protein subunits include:
• Microfilament (smallest diameter): actin
• Intermediate filament: keratin, vimentin, desmin, lamin, etc.
• Microtubule (largest diameter): kinesin, dynein and tubulin""",
}


def load_bank() -> dict:
    parts = sorted(DATA.glob("physiology_ch001_043.zlib.b64.part*"))
    if not parts:
        raise SystemExit("Physiology complete source shards missing")
    raw = zlib.decompress(base64.b64decode("".join(p.read_text(encoding="utf-8").strip() for p in parts)))
    return json.loads(raw.decode("utf-8"))


def main() -> None:
    bank = load_bank()
    source_by_id = {str(q.get("id")): q for q in bank.get("questions", [])}
    ids = set(CLEAN)
    if len(ids) != 21 or not ids.issubset(source_by_id):
        raise SystemExit(f"Physiology Ch1 reviewed ID mismatch: {len(ids)}")
    for qid in ids:
        q = source_by_id[qid]
        if str(q.get("chapterId")) != "1" or q.get("subject") != "Physiology":
            raise SystemExit(f"Physiology Ch1 scope escape: {qid}")
    source_payload = [{
        "id": qid,
        "question": source_by_id[qid].get("question"),
        "options": [o.get("text") for o in source_by_id[qid].get("options", [])],
        "explanation": source_by_id[qid].get("explanation"),
    } for qid in sorted(ids)]
    fingerprint = hashlib.sha256(json.dumps(
        source_payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")).hexdigest()
    payload = {
        "schemaVersion": 2,
        "purpose": "Source-faithful learner-display OCR cleanup; rendered ED8 pages 11-19 reviewed.",
        "subject": "Physiology",
        "chapterId": "1",
        "sourceFingerprint": fingerprint,
        "questions": {qid: {"explanation": CLEAN[qid]} for qid in sorted(ids)},
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"MARROW_PHYS_CH01_CLEANUP_OK questions=21 source={fingerprint[:12]}")


if __name__ == "__main__":
    main()
