#!/usr/bin/env python3
"""Record the bounded source-image inspection performed for the initial pilot.

This is a specific review record, never a general auto-approval algorithm.
"""
from marrow_images import DATA, review

def main():
    registry=DATA/'images/registry.json'
    findings={
      'anatomy-01eccba2867cc7e7':('PASS','diagram','Acrosome reaction: all membrane/granule labels, sequential sperm figures and direction arrow readable and retained.'),
      'anatomy-e583714bb71ea9df':('PASS','diagram','Implantation: epiblast, hypoblast, amnion, trophoblast layers, lacunae, cavity and maternal-vessel labels retained.'),
      'anatomy-12699b9e38a38cf2':('PASS','diagram','Blastocyst: all four labelled structures and leader endpoints retained.'),
      'anatomy-8f516b93ee9acb09':('PASS','diagram','Primitive streak: seven labels, leader lines, relative positions and colored landmarks readable.'),
      'anatomy-babc1e59001cfa88':('REVIEW_REQUIRED','diagram','Notochord: four inset stages present, but small soft labels would benefit from reconstruction. Keep out of production pending redraw.'),
      'anatomy-d51736484d580d39':('PASS','diagram','Neural tube formation: three numbered panels, arrows, tissue labels and explanatory text are readable at native size.'),
      'biochemistry-eb1f8b446eeaceb6':('PASS','hybrid','Benedict reaction: preserve both beaker photographs exactly, with existing reaction arrows and ion labels. No pixels or annotations altered.'),
      'biochemistry-aa11f9fa6a08baea':('REVIEW_REQUIRED','diagram','Glycolysis: severe vertical compression and small labels in embedded source. Reconstruction needed; do not release this raster.'),
      'biochemistry-3adf4c21da2ab956':('PASS','diagram','2,3-BPG shunt: all three molecular structures, charges, enzyme labels, reaction directions, ADP/ATP, water and phosphate retained. High native resolution is sufficient.'),
      'biochemistry-413886fdf13f4253':('PASS','diagram','Glycolysis/gluconeogenesis: both direction/color columns, all metabolite and enzyme labels, branches, oxaloacetate and pyruvate routes retained. Native tall aspect restores readability lost in page placement.'),
      'physiology-307c3998964b5d44':('PASS','diagram','Cell membrane: peripheral/integral/channel/carrier proteins and phospholipid bilayer labels readable. This asset contains only the diagram; existing structured explanation supplies its source table.'),
      'physiology-9cfa79e30a3e0785':('PASS','diagram','Vesicular transport: nucleus, rough ER, Golgi cis/trans ends, vesicles, cell membrane and exocytosis annotations preserved.'),
      'physiology-bc28e0d4fab7f80c':('PASS','diagram','Gap junction: both membranes, connexon, extracellular space and open/closed inset views preserved.'),
      'physiology-84680f6e0f6dec35':('PASS','diagram','Repeated gap junction figure: same labelled panels retained. This asset is the diagram; source intercellular table remains in structured explanation.'),
      'physiology-d916b240eeaa6b79':('PASS','diagram','G-protein receptor: both inactive/active panels, ligand, alpha/beta/gamma, GDP/GTP, bidirectional arrows and cell-response arrow retained.')}
    for asset,(status,kind,notes) in findings.items():
        review(registry,asset,status,kind,notes+' Production is the exact native JPEG; no crop or processing applied.',
               'Agent visual inspection of immutable native PDF image on 2026-09-09; source page/xref and original hash recorded in this entry.')

if __name__=='__main__':main()
