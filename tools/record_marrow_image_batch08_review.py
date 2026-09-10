#!/usr/bin/env python3
"""Record the bounded human-equivalent review of Anatomy image Batch 08."""

from marrow_images import DATA, review, review_binding


BATCH = "NKQ_ANATOMY_20260910"
EVIDENCE = (
    "Automation source-page/native-candidate comparison plus primary-agent "
    "inspection at original resolution and owning-question metadata audit on "
    "2026-09-10; exact source page, xref, region and hashes remain in registry."
)


FINDINGS = {
    "anatomy-d3f9220198201a07": (
        "marrow__ANAT_CH09_Q005", "diagram",
        "All four brain flexures, six neural-tube region labels, leader endpoints and sequence are crisp and complete. Native JPEG retained without processing.",
        "Figure occurs in the Q5 solution and directly supports the metencephalon–myelencephalon pontine-flexure explanation; release after answer only.",
    ),
    "anatomy-3baaad0ddf8e32e3": (
        "marrow__ANAT_CH09_Q008", "medical",
        "Authentic sagittal gross-brain specimen and its source annotation layer are readable; native JPEG bytes retained exactly.",
        "Figure occurs in the Q8 solution and labels the anterior/posterior commissures and corpus callosum used by the commissural-development explanation; release after answer only.",
    ),
    "anatomy-267154fe7beac514": (
        "marrow__ANAT_CH09_Q009", "medical",
        "Authentic axial brain specimen, green A pointer, hemispheres, choroid plexus and lateral-ventricle labels are clear; native JPEG bytes retained exactly.",
        "Image is embedded in the Q9 stem and the A marker is required to identify the structure; release at question time with neutral alt text.",
    ),
    "anatomy-1ea13802a456a2f9": (
        "marrow__ANAT_CH09_Q010", "medical",
        "Authentic sagittal gross-brain specimen preserves corpus callosum, septum pellucidum, fornix and adjacent labels; native JPEG bytes retained exactly.",
        "Figure occurs in the Q10 solution and supports the septum-pellucidum relationship without being required to answer the text-only stem; release after answer only.",
    ),
    "anatomy-390f89119b18e515": (
        "marrow__ANAT_CH09_Q012", "medical",
        "Authentic newborn clinical photograph clearly preserves the occipital mass and surrounding anatomy; native JPEG bytes retained exactly with no enhancement or recreation.",
        "Image is embedded in the Q12 identification stem and is necessary to answer it; release at question time with neutral alt text.",
    ),
    "anatomy-e0c1ff1656105c71": (
        "marrow__ANAT_CH09_Q013", "medical",
        "Authentic clinical photograph clearly preserves the cranial defect and body context; native JPEG bytes retained exactly with no enhancement or recreation.",
        "Image is embedded in the Q13 identification stem and is necessary to answer it; release at question time with neutral alt text.",
    ),
}


def main() -> None:
    registry = DATA / "images/registry.json"
    for asset, (question, kind, asset_notes, binding_notes) in FINDINGS.items():
        review(registry, asset, "PASS", kind, asset_notes, EVIDENCE)
        review_binding(registry, asset, question, "PASS", binding_notes, EVIDENCE)
    print(f"MARROW_IMAGE_BATCH08_REVIEW_OK batch={BATCH} assets={len(FINDINGS)}")


if __name__ == "__main__":
    main()
