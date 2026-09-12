# Continue Practice + Image Recovery Handoff — 2026-09-12

This handoff records the user's current product model and the repository findings from the 2026-09-12 review. It is intentionally implementation-facing so the next coding pass does not reinterpret the behavior.

## Canonical lineage

- Repo: `Numankhan2013/V10.1`.
- Sole Marrow integration trunk: `feature/marrow-canonical-full-current`.
- Production / `main` remains guarded and must not be promoted without explicit user approval.
- All new image/explanation/product work must resolve the current canonical HEAD before mutation and must not build new work from historical rollout branches.

## Biochemistry image recovery status

- The **NK QBank Biochemistry** image-recovery automation was re-enabled on 2026-09-12.
- Its configured integration base is `feature/marrow-canonical-full-current`.
- It must completely read `docs/MARROW_IMAGE_AUTOMATION_RUNBOOK.md` and `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md`; the canonical policy overrides old wording that refers to the historical `feature/marrow-image-rollout-current` branch.
- It must recompute live Biochemistry source-reference/image coverage against the complete canonical corpus each run and remain enabled until the authoritative Biochemistry `--require-complete --check` coverage gate genuinely passes.
- Historical image branches/PRs are evidence only. Verified assets may be transplanted only by stable question ID + content hash + provenance after duplicate/ownership checks; never wholesale-merge stale history.
- Previously reviewed verified Biochemistry work checked during this review is already represented in canonical, including the Ch1 Q4 D-glucose/D-mannose figure asset and the Ch2 Q13 glycolysis explanation binding. No additional already-verified stranded batch was identified during this review.
- The automation is responsible for finding and repairing remaining missing/incorrect Biochemistry figure integrations instead of assuming that the old registry was complete.

## Continue Practice — root cause found

The current canonical behavior is not a real resume flow. The existing Continue Practice implementation effectively finds a globally unattempted question and creates a new one-question Practice session. That explains the observed failure where Continue Practice may show only one question or otherwise fail to return to the learner's actual interrupted topic/session.

The fix must be made in the shared Practice/session architecture. Do **not** create a Marrow-only, subject-only, or topic-only duplicate engine. CBT, Review, FSRS, modules, persistence, sync, analytics and navigation must remain coherent with the shared architecture.

## User-approved mental model for Practice session controls

### UI contract

For the session-level finish/leave controls, expose **two clear options only**:

1. **Submit**
2. **Pause**

Both controls must remain visible, reachable and correctly laid out on the supported Android/PWA/iPad viewports. No clipping below the viewport, invisible control, overlap, off-screen placement, or footer collision is acceptable.

### Pause semantics

`Pause` is the resumable exit.

When the learner pauses:

- persist the exact topic/session identity;
- persist the ordered question set and current position;
- persist which questions were answered correctly;
- persist which questions were answered incorrectly;
- persist which questions were intentionally or unintentionally skipped;
- preserve unseen questions as pending;
- do **not** mark the topic/session completed merely because it was paused.

When the learner later chooses **Continue Practice**:

- reopen the same paused topic/session rather than creating a fresh Practice set;
- return to the learner's paused progress context;
- questions already answered **correctly or incorrectly are finished for that session and must not be served again**;
- questions that were **skipped remain attemptable**;
- questions that were **never reached remain attemptable**;
- Continue Practice must therefore continue the remaining work, not recycle wrong answers and not reduce the resume to a one-question session.

Example: for a 20-question topic session where 3 were correct, 1 was wrong, 1 was skipped and 15 were never reached, Pause → Continue Practice leaves **16 attemptable questions** (the skipped question + 15 unseen). The 4 already answered questions are not served again in that resumed session.

### Completed-topic semantics

A topic/session that is genuinely completed receives the normal completed/green state. Once it is completed, there is no paused session to resume for that topic.

After that completed/green state, **Continue Practice points to the direct next topic in canonical topic order**. Selecting it takes the learner to that next topic rather than reopening the completed topic or constructing a synthetic one-question session.

`Pause` and genuine completion are therefore mutually distinct states:

- **Paused:** Continue Practice resumes the same session and its remaining skipped/unseen questions.
- **Completed/green:** Continue Practice advances to the next topic.

For a subject with no study history, the presence of Continue Practice is not currently a priority bug; however it must never manufacture the broken one-question resume behavior.

## Implementation constraints

- Preserve the approved Topics journey UI and completion state semantics.
- Store resume state through the existing learner-state/session persistence path so Android/PWA and sync behavior do not diverge.
- Wrong answers may still feed Wrong/FSRS/analytics according to their existing contracts, but they are **not** pending questions inside the resumed Practice session.
- Skipped questions must not be treated as answered merely because the learner viewed them.
- Do not infer completion from the current index alone; completion and pause must be explicit session lifecycle states.
- Continue Practice must resolve a durable session/topic state, not `firstUnattemptedQuestion()` globally.

## Implementation status — local candidate

A bounded implementation now exists on `fix/continue-practice-session-resume-20260912`. It is installed after the Home command-center transform and before sync/FSRS, so it extends shared session functions instead of forking them. It persists `lifecycle`, `sessionQuestionIds` and `practiceContext` inside existing `activeSession`/completed-test state, removes the legacy mutation observer that hid Practice Submit controls, and explicitly excludes Wrong/Bookmarks, FSRS, Review, CBT and Custom Study Modules.

Deterministic behavior covers the 16-of-20 resume invariant, same-session ordering, answered-question exclusion, partial-topic continuation and completed-topic advancement. A generated-PWA Playwright regression checks Pause/Submit reachability and footer separation at 320, 390 and 768 px. Local owner checks pass; exact-head Engineering/full CI, generated visual inspection and canonical reconciliation are still pending, so this is not shipped or device-verified.

## Verification required before reconciliation

The candidate includes deterministic tests for:

- Pause after a mixed correct/wrong/skipped/unseen set, then resume with exactly skipped + unseen remaining.
- Correct and wrong questions do not reappear after resume.
- A skipped question remains answerable after resume.
- Resume returns to the same topic/session and preserves ordering/progress.
- A completed/green topic causes Continue Practice to target the immediately next topic.
- No global-first-unattempted / one-question fallback is used when a paused session exists.
- Submit/Pause controls are both visible and reachable in representative Android and PWA/iPad viewport regressions.
- Existing CBT, Review, FSRS and Custom Study Module behavior does not regress.

## Next coding step

Resolve live canonical again, reconcile the candidate if canonical advanced, run exact-head Engineering and full Android/PWA/browser/APK/package CI, inspect the generated viewport screenshots, and merge only into `feature/marrow-canonical-full-current` after verification. Do not promote production without explicit user approval.
