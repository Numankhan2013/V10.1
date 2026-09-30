# Approved study tweak promotion — 2026-09-30

The user requested promotion to main of tweaks they confirmed work, while
existing agents continue image and explanation integration independently.
This audit uses a separate clone based on main `971bd55` and changes neither
the canonical integration trunk nor any existing feature branch.

| Feature | Evidence | Action |
| --- | --- | --- |
| Personal notes after an answer / Review, More → My notes | `docs/QUESTION_NOTES.md` records accepted preview; transformer and CI gates already in main | Preserve existing implementation |
| Bank-aware modules, PYQ builder, revision, marked CBT, timed resume, Abandon, retake comparison | Main STATE records preview acceptance; implementations already in main | Preserve existing implementations |
| More → Find a question | Donor SESSION_LOG's Practice correction entry records the user calling the finder "decent" and requesting the next phase; donor Engineering `36369902329` and full build `36369902634` passed | Recover only runtime and validation delta from `20cd811` |
| Account-wide reset and account switching | Explicit user approval in this session | Promote runtime and validation delta |
| Practice correction passes | Explicit user approval in this session | Promote runtime and validation delta |
| Tap latency and haptic feedback | User explicitly excluded this candidate | Leave donor branch unchanged |
| Later Home Focus and result metric/touch refinements | Explicit user approval in this session | Promote runtime and validation delta |
| Images and explanation augmentation | Owned by active agents | Excluded from this promotion |

The question finder depends on the bank registry, revision desk, and notes
already present in main. Account/reset changes are separately included under the user's explicit approval.
It searches existing source records without revealing correctness, starts
Practice with exact IDs, and prevents replacement of an active timed test.

Source and behavior checks plus a full generated browser/PWA/APK/Android CI run
are required on the isolated promotion head. Donor CI is historical evidence,
not certification of the recovered main-based candidate. Main promotion uses
a normal merge without rewriting history or deleting donor branches.

Main promotion does not deploy the production PWA: production requires the
separate explicit `promote_production` workflow input and matching release SHA.
Physical APK upgrade and data-preservation acceptance remain separate.

## User confirmation and exact scope

The user confirmed: "All of them except tap/haptic feedback are approved."
The approved recovery includes account reset/switching (`77e9b00`, `c0e6275`,
`9ba9f3d`), question finder (`20cd811`), correction passes (`96e5ec2`,
`78f649d`, `55cf5ef`, `50a8f5d`), and Home/result refinements (`74da667`,
`813fdee`, `0891dea`). Only their runtime and verification changes are
transplanted; donor memory is not overwritten onto main. The bundled tap
latency/haptic candidate (`b143242` and follow-up commits) is excluded.

Historical full donor runs: account switching `36332561262`, question finder
`36369902634`, correction `36375712395`, and study journey `36408465858`.
The combined main-based candidate requires fresh full verification.
