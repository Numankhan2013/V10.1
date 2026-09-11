# Marrow image source-coverage gate

This document closes a coverage-accounting defect discovered during physical review of the Biochemistry learner preview on 2026-09-11.

## The defect

The reviewed image registry is **not** the denominator for subject completeness. It contains only assets/bindings that the image review workflow has already staged. The original native staging helper preferentially stages one unmasked, unambiguous JPEG candidate and skips complex cases such as vector/page-content figures, zero-native-candidate figures, multiple-candidate pages, masks, hybrids, and other source visuals needing explicit region/source review.

Therefore statements such as “60 Biochemistry assets are approved” describe reviewed registry state only. They do **not** establish that every question-time or explanation-time figure in the Marrow ED8 source has been integrated.

The source-derived audit is the coverage denominator. `docs/MARROW_IMAGE_PIPELINE.md` currently records 95 Biochemistry visual references across 89 questions. Repeated figures can share one underlying asset, so source-reference count is not the same as unique-asset count; every reference still needs a learner-facing binding or an explicit evidence-backed source-metadata adjudication.

## Required commands

Generate the normal source audit first:

```sh
python3 tools/marrow_images.py audit
```

Then generate source-reference coverage:

```sh
python3 tools/marrow_image_coverage.py --subject Biochemistry
```

The report is written to `data/marrow/images/coverage.json`. Use `--check` after generation to enforce deterministic state.

Only when a subject is genuinely finished may an agent run:

```sh
python3 tools/marrow_image_coverage.py --subject SUBJECT --require-complete --check
```

That command must fail while any legitimate source-recorded visual reference is untracked or tracked-but-unreleased, or while a text-cue review backlog remains.

## Source-metadata adjudication

Raw imported Marrow records remain immutable. If direct inspection proves that a recorded figure reference is itself false—for example, the metadata says a figure exists on a page where the authoritative rendered page contains no figure—do **not** attach a neighboring figure and do not edit the raw source bundle.

Use `data/marrow/images/source_reference_adjudications.json` for an exact, evidence-backed `SOURCE_METADATA_INVALID` adjudication. Every adjudication must match the audit reference by stable reference ID, question ID, subject, role, and exact source page set; it must record the authoritative source file/hash, reason, and concrete inspection evidence. Orphaned or mismatched adjudications fail the coverage audit.

An invalid metadata reference remains visible in the raw `sourceVisualReferences` denominator and is reported separately as `invalidSourceMetadataReferences`; it is **never** counted as a released learner image. The effective learner-image denominator excludes only those explicitly adjudicated invalid references. This preserves audit history while preventing known-false metadata from forcing an invented or neighboring image into the QBank.

## Completion language

Never call a subject's image integration COMPLETE merely because:

- all currently staged registry entries were reviewed;
- a bounded six-item batch completed;
- the registry contains N approved assets;
- CI passed for the currently released subset;
- old candidate branches are historical.

A bounded batch can be COMPLETE while the **subject remains incomplete**. Always report both statuses separately.

A subject may be called learner-image complete only after the source-coverage gate proves every legitimate source-recorded visual reference is released, every explicitly invalid source reference is evidence-backed and exact, and the text-cue backlog is cleared. REVIEW_REQUIRED and REJECTED candidate bindings do not silently satisfy a legitimate source visual reference; the correct visual remains outstanding until actually released.

## Selection policy

Use coverage order, not “easy JPEG” order, as the durable backlog. Native single-candidate JPEGs remain the preferred implementation path, but complex/vector/multi-candidate references must not disappear from the queue. When the next source reference is complex:

1. inspect the full authoritative source page and owning question/explanation;
2. use the metadata crop hint only as a starting point;
3. prefer native vector/page content, otherwise render the precise region at the approved DPI;
4. reconstruct educational diagrams only under the existing source-fidelity rules;
5. preserve medical pixels;
6. leave uncertainty REVIEW_REQUIRED rather than skipping it and advancing the subject to a false-complete state;
7. if the metadata itself is demonstrably false, adjudicate that exact reference rather than substituting a neighboring image.

Question-time and explanation-time visuals are independently required. A question may legitimately need both.

## Known Biochemistry evidence

Physical learner review exposed omissions including Chapter 18 Q3/Q5/Q6 and multiple items in Chapters 19–22. The digitized source records themselves confirm, for example:

- Ch18 Q3/Q5/Q6: explanation flowchart for enzyme non-protein components;
- Ch19 Q2: question-critical reversible-reaction schematic;
- Ch19 Q11: question-time enzyme-kinetics graph **and** explanation-time inhibition graph.

Coverage recovery also found a different defect at Ch2 Q10: the canonical metadata records an explanation `glycolysis_pathway` on page 33, but the hash-verified authoritative page 33 contains explanation text only and no figure. Neighboring pages do contain glycolysis pathway figures. This exact reference is therefore adjudicated `SOURCE_METADATA_INVALID`; no neighboring pathway is attached to Q10.

These cases demonstrate why registry counts and metadata alone cannot be used as completeness evidence.

## Automation rule

Until the current Biochemistry backlog is coverage-audited and recovered, Physiology image automation should remain paused so the same discovery defect is not propagated to another subject. Biochemistry recovery should proceed in bounded batches from the source-coverage backlog, updating `STATE.md` and `SESSION_LOG.md` with both batch status and subject coverage status.
