# MARROW IMAGE AUTOMATION RUNBOOK

This is the unattended execution runbook for NK QBank Marrow image integration. Read `docs/MARROW_AUTOMATION_RUNTIME_V2.md` first; that runtime controls scheduling, retry, branch, concurrency, stale-state, and quarantine behavior. Then read `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md`, `docs/MARROW_IMAGE_PIPELINE.md`, and `docs/MARROW_IMAGE_COVERAGE_GATE.md` for image-specific source and validation requirements.

## Core rules

- Integration trunk: `feature/marrow-canonical-full-current`.
- Resolve live canonical HEAD at every run start; never reuse a historical SHA as a base.
- Never disable, pause, delete, or reschedule the automation from inside the worker.
- Never guess, synthesize, inpaint, or infer medical image content, labels, arrows, ownership, crops, or provenance.
- Raw imported source remains immutable.
- Prefer native embedded/vector source content; otherwise use a precise source-backed high-resolution crop.
- Rendered source pages are authoritative when embedded PDF text/OCR is corrupt.
- Every legitimate source reference remains incomplete until released or evidence-backed as `SOURCE_METADATA_INVALID`.
- One hard reference must not stall an entire subject: quarantine it as `REVIEW_REQUIRED` under Runtime V2 and continue to independent unresolved references.

## Run bootstrap

At the beginning of every occurrence:

1. read `AGENTS.md` and live `.project-memory/STATE.md`;
2. read `docs/MARROW_AUTOMATION_RUNTIME_V2.md`;
3. read `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md`;
4. read `docs/MARROW_IMAGE_PIPELINE.md` and `docs/MARROW_IMAGE_COVERAGE_GATE.md`;
5. resolve live canonical HEAD;
6. run or read current deterministic image registry/progress/coverage state;
7. compute the next unresolved, non-quarantined source reference from canonical source order.

Historical whole-subject pause instructions, historical branch ownership, or old coverage denominators are non-authoritative when they conflict with Runtime V2 or live canonical state.

## Bounded batch

Target up to 6 source references per occurrence. For each reference:

1. resolve stable reference ID and stable question ID;
2. inspect the authoritative rendered source page and owning question/explanation;
3. determine whether native extraction, vector/page-content extraction, or precise region rendering is source-faithful;
4. compare every relevant panel, label, arrow endpoint, legend, and question-critical detail;
5. bind only after ownership/provenance is verified;
6. if confidence is insufficient after two bounded attempts, record `REVIEW_REQUIRED` evidence and continue to the next independent reference.

Do not expose explanation-only identifying content in unanswered question-time visuals. Preserve source-native pixels for diagnostic/clinical images.

## Shared-state write protocol

The registry/progress/coverage files are shared state. Immediately before mutation, re-read:

- live canonical HEAD;
- registry fingerprint;
- progress fingerprint;
- coverage fingerprint.

Create or reuse one logical candidate branch for the bounded batch. Never create repeated `r2/r3/r4` repair branches for ordinary failures. Validate on the candidate. If canonical moved, re-evaluate the stable references against the new HEAD and transplant/rebase only the still-needed bounded delta. Never force overwrite newer canonical work.

## Validation

Before a batch can be reconciled, require the applicable checks from the image pipeline and coverage gate, including:

- registry validation;
- deterministic progress generation/check;
- deterministic source-reference coverage generation/check;
- stable-ID/source ownership;
- source comparison evidence;
- browser image role/timing/rendering/fullscreen/zoom checks where applicable;
- required Android/PWA/APK/package/reproducibility checks for the bounded candidate.

A failed validator or CI run leaves the candidate unreleased. Repair the specific failure in place when possible, checkpoint it otherwise, and keep the worker enabled.

## Completion

A six-item batch completing does not mean the subject is complete.

Use `VERIFIED_SUBJECT_COMPLETE` only when the source-coverage completion gate proves that every legitimate source-recorded reference is released, every invalid metadata reference is evidence-backed and exact, and the relevant text-cue review backlog is cleared.

Production promotion is prohibited without explicit user approval.
