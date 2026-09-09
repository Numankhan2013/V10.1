# Marrow image pipeline

Source PDFs and imported question bundles remain immutable. `tools/marrow_images.py`
owns inventory, native extraction, validation and release. `tools/install_marrow_images.py`
binds approved assets to question IDs after the Marrow transform. The existing
source viewer supplies fullscreen zoom and pan.

## Commands

- Install the audit dependency: `python3 -m pip install pypdf==6.18.0`.
- Inventory: `python3 tools/marrow_images.py audit` (writes `build/marrow-images/audit.json`).
- Extract a native JPEG: `python3 tools/marrow_images.py extract --subject Biochemistry --page 10 --xref 19`.
- Validate: `python3 tools/marrow_images.py validate`.
- Package approved assets: `python3 tools/marrow_images.py release`.

The registry is `data/marrow/images/registry.json`. Original extractions are
content-addressed, immutable files under `originals/`; editable SVGs live under
`editable/`. Production assets use content-hash URLs under `marrow_visuals/`.
Only PASS and explicitly reviewed SOURCE_LIMITED entries are packaged.
PWA builds precache the released figures for offline use.

## Audit interpretation

The audit checks the hashes of all 2,115 imported questions and inspects all
2,484 PDF pages. Current metadata contains 1,082 references across 821 questions:
Anatomy 769/560, Biochemistry 95/89, Physiology 218/172.
Stem and explanation cues add 58 review candidates. This differs from the old
869-question explanation inventory because that inventory searched explanations only.

1,052 references have non-background native image candidates on a cited page.
This is extraction opportunity, not an approved mapping or a quality score.
The PDFs contain 1,101 / 204 / 448 distinct non-background image streams,
respectively. Those include material beyond imported chapters and repeated or
composite educational content; they are not the number of required assets.

Full visual classification, exact asset deduplication, reconstruction suitability
and source-limited totals remain review work. Do not report them as measured yet.
Unknown roles, ambiguous page ownership, masks, rotated pages and Form XObjects
must remain REVIEW_REQUIRED until inspected. Metadata crop hints are advisory.

## Review rules

Compare source and production at native size and intended phone/tablet display
size. Check every panel, label, arrow endpoint, legend and question-relevant detail.
Preserve the question's unanswered labels: explanation images and identifying
captions must never appear in an unanswered question. Use neutral question alt text.
Record the source PDF SHA, page, object and exact region in PDF points measured
from the top left of the unrotated MediaBox.

Medical images retain original pixels. Never synthesize or generatively sharpen
diagnostic detail. A reconstructed diagram requires a reviewed editable SVG;
the registry preserves the original alongside it. PASS does not imply physical
device acceptance. The initial microscopy figure is SOURCE_LIMITED because its
lower panel already contains compression/posterization in the authoritative PDF.

## Outstanding milestone

Expand the three-asset technical pilot to the planned representative 15–20 assets,
including Anatomy, molecular structures, multi-panel and hybrid examples. Inspect
rendered SVG comparisons before releasing reconstruction candidates. Region
rendering/compositing and full visual classification remain to be implemented.
Do not bulk approve candidates or overwrite immutable extractions.
