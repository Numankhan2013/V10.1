# Marrow Image Automation Runbook

This is the mandatory operating contract for unattended or lightly supervised
ChatGPT agents integrating Marrow images into NK QBank. Read this file completely
before inspecting candidates or changing the repository. Also read `AGENTS.md`,
`.project-memory/STATE.md`, `docs/MARROW_IMAGE_PIPELINE.md`, and
`docs/MARROW_BANK_INTEGRATION.md` completely.

## Mission and boundaries

Work on exactly one configured subject and one bounded image batch. Do not edit
explanations, raw Marrow bundles, source PDFs, Home, Topics, FSRS, Practice, CBT,
Review, analytics, sync, navigation, or unrelated UI. Source material is
authoritative. A smaller correct batch is better than a larger uncertain batch.

Required inputs supplied by the automation prompt:

- `SUBJECT`: Anatomy, Biochemistry, or Physiology.
- `BATCH_ID`: globally unique, for example `automation-anatomy-08`.
- `TARGET_CANDIDATE_COUNT`: normally 6.
- `INTEGRATION_BASE_BRANCH`: normally
  `feature/marrow-image-rollout-current` until memory says otherwise.

Recalculate current totals; never trust copied counts as live state. Registry
asset totals and released-question totals are progress measures, **not source
coverage denominators**. A subject is not image-complete merely because every
currently tracked registry asset has been adjudicated.

## Source-PDF completeness contract — mandatory

The authoritative completeness denominator is the source PDF itself. Visual
metadata can be incomplete or can be lost during normalization. Therefore every
non-background PDF image placement occurring on a canonical question page or
explanation page must be explicitly accounted for.

Before candidate selection, always run:

```sh
python3 tools/marrow_images.py audit
python3 tools/marrow_image_coverage.py --subject SUBJECT
```

The coverage report classifies each source placement as:

- `RELEASED`: the exact page/xref/region is bound to a valid owning question and
  role, and both asset and binding are releasable;
- `REVIEW_REQUIRED`: the exact placement is in the registry but intentionally
  held;
- `REJECTED`: the exact placement/binding was inspected and rejected with
  evidence;
- `UNACCOUNTED`: the source placement has not yet been adjudicated. This is
  unfinished work, not permission to ignore the image.

`sourceImagePlacements` is the source-coverage denominator. `approvedAssets`,
`assets`, `releasedQuestions`, figure-metadata counts, native-stream counts, and
candidate counts must never be substituted for it.

A subject may be called **IMAGE_COMPLETE** only when
`unaccountedPlacements == 0`. Held/rejected placements may remain, but each must
have explicit source evidence and status. Until then report the subject as
`IMAGE_COVERAGE_INCOMPLETE`, even if a bounded batch itself is complete.

This distinction is mandatory:

- **BATCH COMPLETE** = the bounded batch has reached a safe verified stopping
  point and released/held/rejected items are fully recorded.
- **SUBJECT IMAGE_COMPLETE** = the source-PDF coverage report has zero
  unaccounted placements.

Never conflate these states in memory or user-facing reports.

PDF placements with one unambiguous page-provenance owner may be staged
normally. If a placement has multiple candidate owners, zero surviving visual
metadata, masks, forms, or other ambiguity, keep it visible in the coverage
queue and inspect the full source page, stem, solution, adjacent questions, and
candidate region. Ambiguity is review work; it must never make a candidate
silently disappear.

## Safe workload and stopping rule

Use a conservative operational budget:

- spend 3–5 minutes on preflight and state recovery;
- spend about 12–15 minutes selecting and source-comparing candidates;
- accept no new candidate after about 20 minutes;
- stop image processing by 25 minutes;
- reserve at least 5 minutes for validation, memory, commit, push, and handoff;
- obey any smaller limit shown by the running product;
- if less than 5 minutes remain, checkpoint immediately.

Default batch: inspect up to 6 candidate bindings. A batch may reach 10 only
when every item is an unmasked, unambiguous, single-candidate native extraction.
Do exactly one reconstruction or one hybrid figure in a specialist batch, with
no other candidates. Stop expanding if two of the first four candidates are
ambiguous or wrongly associated. Never fill a quota with weak candidates.

## Single-writer coordination

`data/marrow/images/registry.json` and `progress.json` are shared across all
subjects. Only one automation may integrate at a time. Run Anatomy,
Biochemistry, and Physiology writers sequentially, each starting after the prior
batch is incorporated. Concurrent agents may perform proposal-only audits, but
must not edit the registry or production metadata.

At the start:

1. Fetch remote state and inspect Git status, current branch, recent image
   commits, registry, progress, memory, and open work.
2. Preserve unrelated and untracked user files.
3. Confirm the configured integration base has not been superseded.
4. Resolve current source-placement coverage for the configured subject.
5. If another genuinely unfinished batch owns a shared-registry mutation, stop;
   historical/completed branches are not locks.
6. If resuming the same subject's unfinished batch, resume that exact branch.
   Otherwise create `automation/marrow-images-<subject>-<batch-id>` from the
   exact authoritative base and record its SHA.

Never force-push, destructively reset, overwrite other work, merge to `main`, or
promote production. Push only the candidate branch. Build-verified, device-
verified, user-accepted, batch-complete, and subject-image-complete are distinct.

## Audit and deterministic selection

Use the existing pipeline. Inspect the implementation before invoking it:

```sh
python3 tools/marrow_images.py audit
python3 tools/marrow_images.py validate
python3 tools/marrow_image_progress.py --check
python3 tools/marrow_image_coverage.py --subject SUBJECT
```

Select the next work from the ordered `UNACCOUNTED` source placements in the
coverage report. Surviving visual metadata may prioritize or clarify ownership,
but it must not define the universe of images.

Prefer, in order:

1. stem-critical images without which the question cannot be answered;
2. explanation figures essential to understanding the answer;
3. one unmasked native JPEG candidate with exact page/xref provenance;
4. clearly owned figures where metadata, question, page, and meaning agree;
5. readable figures meeting the accepted phone-size baseline;
6. independently verified repeated-asset bindings;
7. source/audit order for reproducibility.

Skip as `REVIEW_REQUIRED` when there are multiple plausible candidates, masks,
Form XObjects, unexplained rotation, uncertain crop/ownership/role, unreadable
labels, possible answer leakage, or a need for reconstruction outside a
specialist batch. Page adjacency and plausible subject matter are not ownership.
Audit stream counts are extraction opportunities, not educational-asset counts
or quality scores. Metadata crop hints are advisory.

## Highest-quality source workflow

Use sources in this order:

1. native embedded PDF image;
2. native vector/page content;
3. precise region rendering, normally 300 DPI;
4. conservative processing of authentic medical imagery;
5. source-faithful SVG reconstruction of an educational diagram.

Use the existing commands, for example:

```sh
python3 tools/marrow_images.py extract --subject SUBJECT --page PAGE --xref XREF
python3 tools/marrow_images.py render-region --subject SUBJECT --page PAGE \
  --region X1 Y1 X2 Y2 --dpi 300
```

Region rendering requires supported Ubuntu CI. Do not try to install PyMuPDF in
Termux. Higher DPI cannot recover raster detail absent from the PDF. Preserve
every original extraction under content-addressed `originals/`; never overwrite
or discard it. Production paths are content-hashed. Record PDF hash, page, xref,
top-left-origin region, dimensions, method, original hash, and production hash.

## Medical, diagram, and hybrid safety

Classify each asset as `diagram`, `medical`, `hybrid`, `table`, or `unknown`.

Medical includes X-ray, CT/MRI, ultrasound, histology, pathology specimen,
microscopy, clinical photography, fundoscopy, endoscopy, and other diagnostic
photographic material. Preserve authentic pixels, preferably byte-identically.
Never redraw, generate, inpaint, hallucinate, or generatively sharpen medical
detail. Allow only justified crop/resize, reasonable contrast correction, mild
denoising, or mild sharpening. If the authoritative source is poor, preserve
the best authentic version and use `SOURCE_LIMITED`. A medical asset may never
use `svg-reconstruction`.

Educational diagrams, pathways, graphs, flowcharts, tables, structures, and
schematics may be reconstructed only when meaning can be preserved completely.
Prefer editable SVG. Preserve every relevant label, arrow endpoint/direction,
reversible arrow, branch, connection, order, panel, legend, proportion, axis,
unit, substrate/product/enzyme, compartment, and question-relevant detail. Do
not infer missing information, simplify away meaning, or make a different
teaching diagram. Keep the original alongside the reconstruction.

For hybrid figures, preserve the underlying authentic image and recreate only
the annotation layer. Verify every callout endpoint. Never repaint clinical
pixels.

Subject checks:

- Anatomy: orientation, laterality, layers, relations, boundaries, branches,
  embryologic order, and authentic tissue/specimen pixels.
- Biochemistry: substrate/product/enzyme ownership, cofactors, compartments,
  branches, molecular labels, inhibition points, and arrow reversibility.
- Physiology: axes, units, curve identity, phases, directional arrows, tissue or
  experimental conditions. Similar action-potential, conductance, muscle, and
  pressure curves are not interchangeable.

## Binding role and answer safety

Asset approval and binding approval are independent. Reuse never inherits
question ownership automatically. Every binding needs its own cited
page/xref/region, source comparison, status, role, order, notes, and evidence.

Use role `question` only when needed before answering. It must have neutral alt
text such as “Source question figure” and no identifying or answer-revealing
caption. Use `explanation` when it supports learning after submission; it must
remain hidden until then. Preserve multiple-figure order. Inspect the actual
stem, explanation, source page, adjacent questions, and figure rather than
trusting metadata alone.

For every item compare the full PDF page, exact region, native original,
production asset at native size, phone display, expanded/tablet display, owning
question, explanation, and adjacent source questions. Check for missing panels,
cropped labels, wrong arrows, lost reversible semantics, disconnected branches,
legend loss, changed medical detail, premature answer cues, and unreadable text.
QA notes must state concrete observations; “looks good” is not evidence.

## Status policy

- `PASS`: ownership, role, provenance, source comparison, fidelity,
  readability, timing, and hashes are all complete.
- `SOURCE_LIMITED`: the authoritative source is inherently degraded, the best
  authentic usable version is preserved, and the limitation is documented.
- `REVIEW_REQUIRED`: any uncertainty, incomplete inspection, failed tool,
  borderline readability, needed reconstruction, or expired time remains.
- `REJECTED`: demonstrably wrong, neighboring, misleading, unsafe, or invalid
  reuse. Preserve the rejection so another agent does not repeat it.

Only PASS and explicitly reviewed SOURCE_LIMITED assets can package, and their
bindings must also be releasable. Never promote uncertainty to meet a count.

Use the repository review commands with detailed notes and evidence:

```sh
python3 tools/marrow_images.py review --asset ID --status STATUS --kind KIND \
  --notes "observed findings" --evidence "source comparison reference"
python3 tools/marrow_images.py review-binding --asset ID --question QUESTION_ID \
  --status STATUS --notes "observed findings" \
  --evidence "source comparison reference"
```

Never modify raw Marrow shards/bundles, source PDFs, or runtime metadata outside
the deterministic release process. Never delete originals or erase rejections.

## Regression and release gates

Run at minimum:

```sh
git diff --check
python3 tools/marrow_images.py audit
python3 tools/test_marrow_image_source_coverage.py
python3 tools/marrow_image_coverage.py --subject SUBJECT
python3 tools/marrow_images.py validate
python3 tools/marrow_image_progress.py
python3 tools/marrow_image_progress.py --check
python3 tools/test_marrow_images.py
python3 tools/verify_build_pipeline.py
python3 tools/verify_local.py
```

If claiming **SUBJECT IMAGE_COMPLETE**, additionally run:

```sh
python3 tools/marrow_image_coverage.py --subject SUBJECT --check-complete
```

Inspect the entire registry diff, progress delta, coverage delta, new paths,
bindings, subject scope, and unexpected files. Fail closed on stale hashes/QA/
progress/runtime metadata, overwritten originals, wrong-subject bindings, unsafe
SVG, medical reconstruction, missing comparison evidence, source hash drift,
raw-question hash drift, rejected/pending runtime release, syntax failure,
package-byte mismatch, or any unaccounted source placement when completeness is
claimed.

When available, require full generated-app/browser/PWA/APK CI. Verify inline
role/timing, neutral unanswered state, aspect ratio, multiple-figure order,
fullscreen zoom/pan, offline availability, and exact packaged bytes. Capture a
source-versus-production comparison for each asset plus phone and expanded-view
screenshots. If screenshots cannot be inspected, do not mark new work PASS.

## Known mistakes that must not recur

Past source comparison caught a false notochord lumen, a disconnected glycolysis
branch, and lost reversible-arrow semantics in reconstructions. Candidate
selection also proposed: an enzyme graph for the wrong question, a wrong membrane
diagram, fructose for galactose, conductance for muscle twitch, a glial chart for
a neuron question, transamination for BH4, neighboring muscle-protein figures,
a tRNA-synthetase/Rossmann image for LDH, Starling graphs for unrelated smooth
muscle questions, and action-potential figures for unrelated contraction
questions. These demonstrate that plausible resemblance, same-page location,
and topical similarity are not proof.

Coverage failure discovered 2026-09-11: bounded registry batches were incorrectly
reported as if they implied subject completeness. Biochemistry had 60 approved
assets but a source-PDF audit later found 201 relevant image placements with 135
still unaccounted. Several learner-reported figures in Chapters 18–22 had been
silently omitted because metadata was incomplete or normalization dropped visual
fields. This is the reason source-PDF placement coverage is now mandatory.

The Golgi-tendon-organ sequence is correctly associated but held because its
native labels are below the accepted threshold. Correct ownership does not make
an unreadable asset releasable. Other lessons: valid assets can have invalid
bindings; answer timing is correctness; neutral alt text is answer safety; DPI
does not restore lost detail; CI success is not user acceptance; required memory
fields and single workflow ownership must remain intact.

## Timeout-safe checkpoint and mandatory handoff

When less than five minutes remain, stop processing. Leave uncertainty as
`REVIEW_REQUIRED`, validate the registry, refresh progress only if valid, update
coverage, memory, commit, and push. Never wait for timeout with uncommitted work.

Always update `.project-memory/STATE.md` and append
`.project-memory/SESSION_LOG.md`. Update `.project-memory/ROADMAP.md` and this
pipeline document when durable totals or next steps change. Run the memory
validator. Record subject, batch ID, base/candidate commits, exact question and
asset IDs, page/xref/region, inspected/PASS/SOURCE_LIMITED/REVIEW_REQUIRED/
REJECTED counts, released totals, **sourceImagePlacements and
unaccountedPlacements**, methods, tests, CI URLs/status, screenshots, unresolved
cases, next deterministic source placement, and whether the result is
build-verified, device-verified, accepted, batch-complete, or subject-image-
complete.

Final response format:

```text
STATUS: BATCH_COMPLETE | SAFE_CHECKPOINT | BLOCKED
SUBJECT_COVERAGE: IMAGE_COMPLETE | IMAGE_COVERAGE_INCOMPLETE
Subject / batch:
Base / candidate commit:
Source placements / released / held / rejected / unaccounted:
Candidates inspected:
PASS / SOURCE_LIMITED / REVIEW_REQUIRED / REJECTED:
Released and held question IDs:
Methods and files changed:
Validation and CI:
Preview and screenshots:
Production promoted: NO
Memory updated: YES | NO
Next deterministic source placement:
Human review needed:
```

Say `BATCH_COMPLETE` only when the bounded batch is safely verified. Say
`IMAGE_COMPLETE` only when `--check-complete` passes. Otherwise preserve the
incomplete source-coverage state explicitly.
