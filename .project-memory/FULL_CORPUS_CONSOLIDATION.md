# Canonical full Marrow corpus consolidation

Status: generated source candidate; production remains unpromoted.

Canonical source scope on `feature/marrow-canonical-full-current`:

- Anatomy: Chapters 1-63, 1,115 questions, 63 source topics.
- Biochemistry: Chapters 1-28, 582 questions, 28 source topics.
- Physiology: Chapters 1-43, 1,014 questions, 43 source topics.
- Global: 2,711 questions, 134 source topics.

The product lineage remains the approved V3/correct-index branch. The complete source data was consolidated underneath it without replacing the V3 app assets. Anatomy Chapters 49-59 came from the validated canonical JSONL handoff and fill the already-planned Abdomen/Pelvis, Lower Limb and Back taxonomy slots. Backend source chapter/question IDs remain unchanged.

Generated Anatomy bundle: `data/marrow/anatomy_ch001_063*`.

The first build started on the setup commit before the generated bundle existed and is not a candidate certification. Only workflows on this commit or a descendant containing the generated full corpus may certify the candidate.

Next: exact-head Engineering Gate + Android/PWA/browser/package/preview verification. Do not promote production until those gates pass and the user verifies the resulting preview.

## 2026-09-12 memory sync — Practice flow protection

The corpus itself was not changed by the Practice-flow repair, but future corpus/image/explanation integrations must preserve the accepted normal-Practice session contract now documented in `.project-memory/PRACTICE_FLOW_POSTMORTEM_2026-09-12.md`.

In particular, automation branches must start from the current canonical integration lineage rather than a stale donor branch, must not reintroduce the old Pause/Submit question-footer controls or remaining-only resume behavior, and must keep the exact-head Practice browser regression green. The corrected flow is device/user-verified; production promotion remains a separate explicit decision.
