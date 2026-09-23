# Anatomy explanation source-access repair — 2026-09-23

Status: `CI_FAILED_BLOCKED` (retryable tooling/source-access class; worker must remain enabled)

## Canonical resolution

- Canonical integration trunk: `feature/marrow-canonical-full-current`
- Exact canonical HEAD resolved at this run: `cc4fe355441873f6df3517c55b4819bf80cbbe5c`
- Repair branch: `feature/marrow-explanations-anatomy-20260923-source-access-repair`
- Branch created from that exact SHA.
- Anatomy explanation work remains incomplete. Last fully verified Anatomy range remains Chapter 7 Q1-Q10; next source-order item is Chapter 7 Q11.
- Raw source is immutable; no learner-facing explanation content was changed in this repair.

## Concrete blocker

The unattended runtime can read repository text through the GitHub connector, but the canonical complete Anatomy corpus is stored as concatenated base64/zlib shards. Connector file responses are truncated before the complete shard payload is available, so the runtime cannot safely concatenate/decompress the canonical bundle. The container runtime has no GitHub network/DNS access, so cloning/downloading the repository there also fails. Stable-ID/code search does not index the compressed payload and returned no result for `marrow__ANAT_CH07_Q011`.

This prevents the mandatory source audit (stem/options/key/source explanation/figure metadata/review flags) for Ch7 Q11+ and therefore makes medical authoring unsafe. It is a tooling/source-access limitation, not a permanent content blocker and not a reason to disable the worker.

## Bounded repairs attempted this run

1. GitHub-connector route: enumerated `data/marrow/` and fetched the canonical `anatomy_ch001_063.zlib.b64.part00`; the response was truncated, so a complete decompression input cannot be reconstructed safely.
2. Execution-runtime route: attempted repository access from the container; GitHub hostname resolution is unavailable in that runtime, so the repo cannot be cloned/downloaded there.

Per the scheduler invariant, do not spin on this failure class again in this occurrence.

## Exact next retry action

At the next recurrence:

1. Resolve the live canonical HEAD and authoritative explanation ownership/inventory again.
2. Prefer any newly available execution-capable GitHub/repository tool or canonical expanded/plaintext artifact.
3. If connector responses can expose complete shard bytes, concatenate every `data/marrow/anatomy_ch001_063.zlib.b64.part*` in lexical order, base64-decode, zlib-decompress, and select stable IDs beginning at `marrow__ANAT_CH07_Q011`.
4. Audit contiguous Ch7 Q11 onward and workload-score to target 16 / max 20 / max 18 questions without skipping difficult items.
5. Author only after exact stem/options/key/source explanation/figure/table/review metadata are available.
6. Continue normal static validation, deterministic 2,711-ID inventory regeneration, stable-ID browser/shared regressions, PR, exact-head Engineering + full Android/PWA/APK/package/reproducibility/preview CI, and canonical reconciliation.

Do not treat this repair branch itself as CURRENT_UNVERIFIED content ownership: it contains no Anatomy augmentation. A future content batch must start from the then-live exact canonical HEAD unless this repair is first reconciled or transplanted as memory-only evidence.
