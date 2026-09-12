# Marrow Image Automation Runbook

This is the mandatory operating contract for unattended or lightly supervised
ChatGPT agents integrating Marrow images into NK QBank. Read this file completely
before inspecting candidates or changing the repository. Also read `AGENTS.md`,
`.project-memory/STATE.md`, `docs/MARROW_IMAGE_PIPELINE.md`, and
`docs/MARROW_BANK_INTEGRATION.md` completely.

## Supervised manual two-lane workflow

This section supersedes the six-item/time-box defaults below when a human-
supervised manual run explicitly requests high-throughput processing. It does
not weaken any source, medical-pixel, ownership, role, answer-safety, status,
single-writer, canonical-lineage, or validation rule.

The sole integration trunk is `feature/marrow-canonical-full-current`. Resolve
its live head before each run and create any working branch from that exact SHA.
Before mutation and reconciliation, recheck canonical HEAD, `STATE.md`, writer
ownership, and registry/progress fingerprints. Never select one side of a real
shared-registry conflict.

### Fast lane

1. Generate the authoritative audit and coverage against the complete corpus.
2. Select the next 25–40 unresolved source references in exact coverage order.
3. Build one deterministic plan and batch-render each unique cited PDF page plus
   useful candidate-region evidence.
4. Classify every reference:
   - **A** — exact `SOURCE_METADATA_INVALID`, structured-table-only, or no
     learner visual required;
   - **B** — exact approved-asset reuse proven by content hash, stable question
     ID, independent page ownership, role, order, and answer safety;
   - **C** — clean single-candidate native extraction or precise unambiguous
     region extraction;
   - **D** — complex, ambiguous, specialist, reconstruction, hybrid, difficult
     medical imagery, uncertain crop/ownership, or possible answer leakage.
5. Integrate A–C together. Record D immediately as `REVIEW_REQUIRED` with exact
   evidence and continue source-order triage; D remains unresolved and is handled
   later in a small exhaustive specialist batch.

A references may be adjudicated from conclusive rendered-page/source evidence
without learner screenshots because they make no learner-facing change. B
bindings reuse already-approved immutable pixels; recheck the new binding but do
not re-prove the asset pixels. C extractions preserve the complete provenance and
medical/diagram rules below. Regenerate release metadata, progress, and coverage
once after the bulk mutation.

Use the proposal-only planner/evidence renderer:

```sh
python3 tools/marrow_image_fast_lane.py plan --subject SUBJECT --count 35 \
  --batch-id BATCH_ID --base-sha BASE_SHA --output build/marrow-fast-lane/plan.json
python3 tools/marrow_image_fast_lane.py render \
  --plan build/marrow-fast-lane/plan.json \
  --output build/marrow-fast-lane/evidence
python3 tools/marrow_image_fast_lane.py validate-reviewed \
  --plan data/marrow/images/review_batches/BATCH_ID.json
```

The reusable manual workflow
`.github/workflows/marrow-image-fast-lane-review.yml` performs the Linux PDF
render once and emits one source-review artifact.

After A–C integration, `.github/workflows/marrow-image-fast-lane-gate.yml`
runs deterministic registry/progress/coverage/raw-source checks, constructs only
the shared Marrow/image web surface, verifies offline runtime bytes, and renders
each changed question at 390×844. It deliberately omits Gradle/APK, deployment,
and unrelated whole-product browser suites until the canonical checkpoint.

### Specialist lane

A D decision is not a skip or a resolution. Its durable review record must cite
the page/candidates and state the exact ambiguity. Specialist batches retain the
full exhaustive comparison workflow and may resolve items independently without
blocking later source-order triage. Coverage continues to show the D reference as
unreleased.

### Validation and checkpoint cadence

Every fast batch must retain: source/stable-ID ownership, content hashes and
provenance, registry validity, progress/coverage consistency, raw-source
immutability, wrong-subject protection, role/order/answer timing, runtime/package
metadata consistency, image tests, and targeted learner rendering for every
changed question/binding.

Inspect source versus production once for each new unique asset and retain that
evidence. For reuse, inspect the new question state and binding contract without
redundant screenshots of unchanged pixels. One conclusive changed state is
preferred to repeated equivalent evidence.

For image-data-only batches, run the targeted deterministic/image/browser gates
and reconcile the validated batch. Several such batches may share the next full
Android/PWA/APK/package/browser canonical checkpoint. Run the full suite
immediately when renderer/runtime/build/package code changes, a check suggests
cross-product impact, package-byte consistency is uncertain, or the prior
checkpoint is no longer applicable. Record which expensive gates were
amortized, and do not call accumulated work checkpoint-verified until that full
canonical checkpoint passes.

Report separately: references audited, A resolutions, B bindings, C unique
assets, D deferrals, resolved-reference delta, released-binding delta, source
work versus validation effort, validations run, and deferred checkpoint gates.

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
  `feature/marrow-canonical-full-current`.

Recalculate current totals; never trust copied counts as live state. At this
runbook's creation, the verified Batch 07 state is 147 approved assets, 166
released bindings, and 152 released questions: Anatomy 58, Biochemistry 55,
Physiology 39. The user-approved pilot is the minimum readability threshold.
Later work may exceed it but must never fall below it.

## Safe workload and stopping rule

Official OpenAI documentation does not establish a fixed wall-clock maximum for
these ChatGPT web automations. Use a conservative operational budget instead:

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
4. If another batch changed the registry or image assets, stop and request a
   rebase; never resolve a shared-registry conflict by choosing one side.
5. Create `automation/marrow-images-<subject>-<batch-id>` from the exact base and
   record its SHA.

Never force-push, destructively reset, overwrite other work, merge to `main`, or
promote production. Push only the candidate branch. Build-verified, device-
verified, and user-accepted are different statuses.

## Audit and deterministic selection

Use the existing pipeline. Inspect the implementation before invoking it:

```sh
python3 tools/marrow_images.py audit
python3 tools/marrow_images.py validate
python3 tools/marrow_image_progress.py --check
```

Filter candidates to the configured subject. Do not blindly run
`stage_marrow_image_review.py --per-subject`, because the current command stages
all three subjects. Extend it with a tested subject filter or select a
deterministic subject-only set from the audit.

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
python3 tools/marrow_images.py validate
python3 tools/marrow_image_progress.py
python3 tools/marrow_image_progress.py --check
python3 tools/test_marrow_images.py
python3 tools/verify_build_pipeline.py
python3 tools/verify_local.py
```

Inspect the entire registry diff, progress delta, new paths, bindings, subject
scope, and unexpected files. Fail closed on stale hashes/QA/progress/runtime
metadata, overwritten originals, wrong-subject bindings, unsafe SVG, medical
reconstruction, missing comparison evidence, source hash drift, raw-question
hash drift, rejected/pending runtime release, syntax failure, or package-byte
mismatch.

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

The Golgi-tendon-organ sequence is correctly associated but held because its
native labels are below the accepted threshold. Correct ownership does not make
an unreadable asset releasable. Other lessons: valid assets can have invalid
bindings; answer timing is correctness; neutral alt text is answer safety; DPI
does not restore lost detail; CI success is not user acceptance; required memory
fields and single workflow ownership must remain intact.

## Timeout-safe checkpoint and mandatory handoff

When less than five minutes remain, stop processing. Leave uncertainty as
`REVIEW_REQUIRED`, validate the registry, refresh progress only if valid, update
memory, commit, and push. Never wait for timeout with uncommitted work.

Always update `.project-memory/STATE.md` and append
`.project-memory/SESSION_LOG.md`. Update `.project-memory/ROADMAP.md` and this
pipeline document when durable totals or next steps change. Run the memory
validator. Record subject, batch ID, base/candidate commits, exact question and
asset IDs, page/xref/region, inspected/PASS/SOURCE_LIMITED/REVIEW_REQUIRED/
REJECTED counts, released totals, methods, tests, CI URLs/status, screenshots,
unresolved cases, next deterministic candidate, and whether the result is
build-verified, device-verified, accepted, or none of those.

Final response format:

```text
STATUS: COMPLETE | SAFE_CHECKPOINT | BLOCKED
Subject / batch:
Base / candidate commit:
Candidates inspected:
PASS / SOURCE_LIMITED / REVIEW_REQUIRED / REJECTED:
Released and held question IDs:
Methods and files changed:
Validation and CI:
Preview and screenshots:
Production promoted: NO
Memory updated: YES | NO
Next deterministic candidate:
Human review needed:
```

Say COMPLETE only when released items have complete visual QA, all required
checks pass, memory is updated, and work is committed. Otherwise leave a safe
checkpoint with no unverified release.
