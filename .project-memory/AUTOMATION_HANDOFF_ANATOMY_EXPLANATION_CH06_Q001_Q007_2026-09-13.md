# Anatomy explanation automation handoff — Ch6 Q1–Q7

Status: PR_OPEN_CI_PENDING

## Canonical state

- Subject: Anatomy
- Stable-ID scope: `marrow__ANAT_CH06_Q001..Q007`
- Canonical base observed immediately before this checkpoint: `b4305078520704ad55dfc088035513e3a841fbb0`
- The seven-question rollout was already reconciled into canonical by merge commit `7049362efa17c56775eca190a00b3d3a335ba3f0`.
- The deterministic inventory refresh produced canonical tip `b4305078520704ad55dfc088035513e3a841fbb0`.
- Inventory: 588 enhanced / 2,123 pending / 2,711 total.
- Inventory fingerprint: `87cc4e50f145cf59215dcfeb8d30fd32730747b3d964c39339b0aded8907f41d`.
- Q2 remains `needs_manual_review`; the missing numbered 1–4 source legend must not be invented.
- Raw source remains unchanged.

## Certification history

- Candidate/merge-tree Engineering Gate: success.
- Post-merge canonical Engineering Gate `34706555298`: success on `7049362efa17c56775eca190a00b3d3a335ba3f0`.
- Post-merge canonical full Android/PWA/browser/APK/package run `34706555290`: success on `7049362efa17c56775eca190a00b3d3a335ba3f0`.
- Deterministic inventory refresh `34706555305`: success and generated `b4305078520704ad55dfc088035513e3a841fbb0`.

## Current exact-head action

The inventory-generated tip had no exact-head Engineering/full-build certification. This checkpoint commit intentionally changes project-memory only so normal canonical push triggers run Engineering Gate and the full Android/PWA/browser/APK/package workflow on one new exact canonical head without re-triggering the inventory generator (its path filter excludes project-memory-only changes).

Do not start Anatomy Ch6 Q8+ or release the explanation lane until both exact-head workflows for the checkpoint commit succeed. Production promotion remains prohibited.
