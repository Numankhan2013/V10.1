# Physiology learner-visible cleanup — Batch 44

Status: CI_FAILED_BLOCKED

- Subject: Physiology
- Chapter: 5 — Body Fluids
- Source-order reviewed IDs: `marrow__PHYS_CH05_Q013` through `marrow__PHYS_CH05_Q024`.
- Authoritative rendered ED8 pages reviewed: 84–90 from the verified 817-page Library PDF `physiologyed8(3).pdf`; rendered images were used because parsed text is corrupt.
- Cleanup/canonical heads before mutation: cleanup `3db836cf368fc530247e22109b629fc9da1ae4da`; canonical `94edb3af43eb38a1ef762b08c1bdb152c15b3359`.
- Initial reviewed proposal commit: `fc9d64c68019c2f726e4ae7c6380a7f76da9683a`.
- Initial promotion workflow `34964796032` succeeded and produced promotion commit `5f3160dcf5fdb2020898ffdd1e22ce4b5f80a619`.
- During immediate source re-review, Q23 transcription was found to contain an incorrect `hypotonic/decreases` phrase inconsistent with the rendered source; it was corrected in proposal commit `ef6f341280a3a038193ac0f001fdcb224094a9e6` to the source-faithful `hypertonic/increases` wording before this run could be reported CLEANED.
- Corrective promotion workflow `34964852658`, job `104366786446`, failed closed at `Promote reviewed proposals with exact source fingerprints`; all downstream validators were skipped. Do not report this batch CLEANED until the corrected Q23 proposal is successfully promoted and the full validator suite passes.
- The recurring Physiology cleanup should remain enabled. Next run should first reconcile the already-promoted Batch 44 active override with corrected proposal Q23 through the governing source-fingerprinted v2 path, then run all mandatory validation. Do not weaken the promoter/validator.
- Last fully verified residual baseline remains Batch 43: 69 global explanation candidates = Anatomy 1, Biochemistry 6, Physiology 62; questionOptionCandidateQuestions=0.
- After corrective promotion succeeds, rebuild the live queue to determine the exact next unresolved Physiology ID; do not assume Q25 until the audit confirms it.
