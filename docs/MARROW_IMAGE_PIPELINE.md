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
- Render a precise region on Ubuntu: `python3 tools/marrow_images.py render-region --subject Biochemistry --page 10 --region 162 56 450 272 --dpi 300`.
- Stage a bounded review batch: `python3 tools/stage_marrow_image_review.py --per-subject 6 --batch-id rollout-02`.
- Record an asset review: `python3 tools/marrow_images.py review --asset ID --status PASS --kind diagram --notes 'Observed comparison findings' --evidence 'Comparison artifact reference'`.
- Record a repeated-image binding review: `python3 tools/marrow_images.py review-binding --asset ID --question QUESTION_ID --status PASS --notes 'Ownership/role findings' --evidence 'Source comparison'`.
- Package approved assets: `python3 tools/marrow_images.py release`.
- Refresh/check deterministic progress: `python3 tools/marrow_image_progress.py` then `python3 tools/marrow_image_progress.py --check`.

The registry is `data/marrow/images/registry.json`. Original extractions are
content-addressed, immutable files under `originals/`; editable SVGs live under
`editable/`. Production assets use content-hash URLs under `marrow_visuals/`.
Only PASS and explicitly reviewed SOURCE_LIMITED assets are eligible for packaging.
Repeated-asset bindings have their own status and cited page/xref/region; rejected
or unreviewed bindings are excluded even when the underlying asset is approved.
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

## Current rollout milestone

The user reviewed all sixteen released pilot figures in the PWA on 2026-09-09
and approved their readability and quality as the minimum release threshold. The
pilot merged through PR #12; production was not promoted.

Batch 01 expands the registry to 28 approved assets and 34 released question
bindings: Anatomy 12, Biochemistry 11 and Physiology 11. The formerly held
notochord and glycolysis figures are now clean, rendered, source-compared SVGs.
Ten additional native assets passed inspection, including two authentic muscle
biopsy/histology images whose bytes are unchanged. Six repeated-asset bindings
passed independent ownership/role review. Two tempting matches were rejected:
Biochemistry Ch2 Q10 (wrong enzyme graph) and Physiology Ch1 Q9 (wrong membrane
diagram). They remain intentionally imageless until their correct source content
is resolved.

Full-bank visual classification remains outstanding. The page-level audit is
complete; educational asset counts and quality/type totals outside reviewed
registry entries must not be inferred from image-stream counts. Region rendering
is available on Ubuntu; multi-candidate, masked and complex hybrid figures require
an explicit asset-specific reviewed implementation.
