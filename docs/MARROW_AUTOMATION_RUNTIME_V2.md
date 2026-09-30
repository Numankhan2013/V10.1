# MARROW AUTOMATION RUNTIME V2

This file is the highest-priority repository runtime contract for unattended Marrow image and explanation automations. It exists to make scheduled workers idempotent, resumable, and resistant to stale handoffs, stale branches, transient source failures, CI failures, and canonical movement.

If this file conflicts with historical project memory, old branch names, old chapter/range overrides, old pause instructions, or old corpus denominators, this file plus `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md` wins for automation control flow. Source-fidelity and medical-quality requirements from the subject-specific runbooks remain mandatory.

## 1. Worker model: stateless desired-state reconciliation

Every occurrence starts from live repository truth. A worker MUST NOT treat its previous prompt, a previous branch name, a remembered chapter, or a previous recovery attempt as authoritative current state.

At run start:

1. resolve the live HEAD of `feature/marrow-canonical-full-current`;
2. read `AGENTS.md`, `.project-memory/STATE.md`, this runtime file, and `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md`;
3. read the workstream-specific runbook/pipeline and current machine-readable inventory/coverage/progress files;
4. compute the next unresolved work item from canonical stable IDs and canonical source order;
5. inspect side branches/PRs only to determine whether there is genuinely unreconciled work for that exact stable-ID batch;
6. ignore historical branches, historical ownership notes, and stale recovery instructions when canonical already contains or supersedes their work.

The canonical trunk is the release truth. Side branches are temporary candidates, never durable scheduler state.

## 2. No hard-coded recovery state

Scheduled-task prompts MUST NOT permanently pin:

- chapter numbers;
- question ranges;
- source-reference IDs;
- batch branches;
- commit SHAs;
- PR numbers;
- inventory counts;
- image coverage counts.

Those values may be reported in handoffs, but every later occurrence must recompute them from live canonical state.

A stale task prompt or handoff cannot override live canonical evidence.

## 3. Idempotency and duplicate protection

Every logical work item has a stable identity:

- explanations: subject + stable question ID/range;
- images: subject + stable source-reference ID + owning stable question ID.

Before authoring or integrating anything, check whether the stable item is already released on canonical. If yes, do not re-author, do not create a repair branch, and do not repeat CI for an obsolete candidate; recompute the next unresolved item.

Before reconciliation, re-read canonical HEAD and the shared inventory/registry fingerprint. If canonical advanced:

- never force-push or overwrite;
- re-evaluate whether the candidate is already satisfied;
- transplant only the bounded stable-ID delta onto the live canonical lineage when still needed;
- rerun deterministic validation on that new candidate.

This is optimistic compare-and-set coordination, not a persistent lock.

## 4. Branch discipline

One logical batch gets one working branch at a time.

A validation failure, source-access failure, CI failure, or helper-script failure does NOT justify `r2`, `r3`, `r4`, etc. Repair the current logical candidate in place.

A replacement branch is allowed only when the current branch is structurally unusable or cannot be safely rebased/transplanted onto live canonical. Record the exact root cause, then create one fresh branch from live canonical and move only the bounded stable-ID work. Never create another replacement for the same unchanged root cause.

Once canonical contains the batch, all older candidate branches are historical and non-blocking.

## 5. Failure policy: fail closed on content, never on the scheduler

Workers must never disable, pause, delete, or reschedule themselves.

Transient failures are RETRYABLE, including:

- GitHub/API/auth failures;
- Library/source retrieval failures;
- corrupted embedded PDF text;
- CI infrastructure failure;
- stale generated audit/inventory files;
- canonical movement during a run;
- a single REVIEW_REQUIRED source item.

Fail closed means unsafe content is not released. It does NOT mean the worker stops operating.

For the same failure class, perform at most two bounded repair attempts in one occurrence. If still unresolved, checkpoint evidence and move to the next independent safe item when the workstream allows it. The next occurrence recomputes live state before retrying.

## 6. Quarantine, not subject-wide deadlock

For image integration, a source reference that cannot be verified after two bounded attempts becomes `REVIEW_REQUIRED` with:

- stable reference ID;
- stable question ID;
- source page(s);
- failure class;
- exact evidence;
- last-attempt canonical HEAD;
- retry-after condition.

The worker immediately continues to the next independent unresolved reference. A quarantined item is revisited only when source/tool state changes or after at least 20 other independent references have been attempted. It never counts as released.

For explanations, a genuinely unrecoverable source item may remain `needs_manual_review`, but that item must not cause unrelated later source-order work to be repeatedly rediscovered or rewritten. Preserve the unresolved flag and continue only where the governing explanation runbook permits safe contiguous progress.

## 7. Source retrieval is a fallback chain

Absence from the current chat or working directory is not source absence.

Use, in order where applicable:

1. canonical repository source projections/bundles and manifests;
2. canonical source-PDF artifacts available to the worker;
3. the verified user Library source named in project memory;
4. rendered-page inspection when embedded text/OCR is corrupt.

Never substitute PrepLadder, another edition, internet content, or medical memory for missing Marrow source content.

A corrupted text layer is not permission to mark the source unavailable; use rendered-page/native extraction paths defined by the image/source pipeline.

## 8. Shared-state coordination

Explanation and image workflows are separate workstreams. Within each workstream, shared files must use optimistic concurrency:

- read live canonical HEAD + shared fingerprint immediately before write;
- write only a bounded candidate branch;
- validate the bounded change;
- reconcile only if the live base is still compatible;
- if not, recompute/rebase/transplant and validate again.

No persistent global lock may survive an occurrence. A stale PR, stale branch, historical ownership note, REVIEW_REQUIRED item, or failed CI run is not a lock.

Schedules should be staggered, but correctness must not depend on timing alone.

## 9. Canonical completeness and historical documents

Canonical scope is always:

- Anatomy: Ch1–63 / 1,115 questions;
- Biochemistry: Ch1–28 / 582 questions;
- Physiology: Ch1–43 / 1,014 questions;
- Global: 2,711 questions.

Historical 2,455- or 2,115-question figures are not valid denominators.

Historical instructions that say a whole subject must remain paused because another subject is incomplete are obsolete. Subject workers may process independent bounded work concurrently, while shared registry/inventory writes remain conflict-safe under Section 8.

## 10. Progress invariant

While unresolved safe work remains, every occurrence must finish in one of these states:

- `PROGRESSED`: canonical or candidate state moved forward;
- `PROGRESSED_WITH_REVIEW_QUEUE`: safe work advanced and one or more items were quarantined;
- `RETRYABLE_BLOCKED`: no safe progress was possible because of a concrete transient/infrastructure conflict; exact evidence and next retry action recorded;
- `VERIFIED_SUBJECT_COMPLETE`: the subject completion gate proves no unresolved legitimate work remains.

Pure preflight, recreating a branch, rediscovering the same stale handoff, or repeating an already-canonical batch is not progress.

If two consecutive occurrences end `RETRYABLE_BLOCKED` for the same failure class and same stable item with no new evidence, the third occurrence MUST skip/quarantine that item when safe and attempt independent work rather than repeating the same loop.

## 11. Validation and release

Never weaken validators to make a batch pass.

Candidate work is not released until the relevant deterministic source/ownership/registry/inventory/browser/product checks pass and the verified bounded change is reconciled into `feature/marrow-canonical-full-current`.

If CI fails, keep the candidate unreleased, repair the specific failure in place when possible, and leave the scheduler enabled.

Production promotion remains prohibited unless explicitly approved by the user.

## 12. Handoff format

After every state-changing occurrence, record a compact handoff containing:

- live canonical base SHA used;
- subject + workstream;
- stable IDs/range attempted;
- candidate branch/commit/PR when any;
- inventory or coverage delta + fingerprint;
- validation/CI status;
- REVIEW_REQUIRED queue changes;
- exact blocker class when blocked;
- exact next action derived from live state.

Handoffs are evidence, not future authority. The next occurrence must still bootstrap from live canonical state.
