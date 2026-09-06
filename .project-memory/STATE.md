# STATE.md — Current Project State and Handoff

> Keep concise and current. History goes in `SESSION_LOG.md`,
> durable reasoning in `DECISIONS.md`, future work in `ROADMAP.md`.

## Repo / branch

- Repo: `Numankhan2013/V10.1` (private)
- Active branch: `v11.5-custom-study-modules`
- HEAD: `aa6cebb54ae43d60c80cef4e93025e3e961087c7`
  (`Add harness-agnostic agent memory: .project-memory/SESSION_LOG.md`, 2026-09-06; includes `AGENTS.md` + `.project-memory/` on top of `f13d12f`)
- Parent lineage: `v11.4-whole-app-vision` fix
  `9e6abc71eca192808e6fbd70d4127011c6a47ef0`
  (`Restore Due Review action alongside permanent all-subject practice`)
- Stale branch: `main` (`8bc0be4`) — do not use as baseline; V11 work lives on
  `v11-*` branches.
- Accepted baseline (unchanged): V11 Run 220, commit
  `73c04281696137fda712ae0b9b7079c9c4a15635` on `v11-source-visuals`,
  run `34011265432` — physically tested and user-confirmed.

## Last CI (verified via `gh run list`)

- `v11.5` Build V10.1 APK `34051111714` — **success**, 1m33s
  (`Add harness-agnostic agent memory`; artifact `V11.5-custom-study-modules-debug-apk`)
- `v11.5` Build V10.1 APK `34049637559` — **success**, 1m40s
  (`Label V11.5 APK artifact`)
- `v11.5` Engineering Gate `34049637590` — **success**
- `v11.5` Build V10.1 APK `34049523411` — **success**, 1m41s
  (`Add persistent Custom Study Modules`)
- `v11.4` fix Build V10.1 APK `34043059869` — **success**, 1m48s
  (`Restore Due Review action…`); user confirmed this APK works and UI is great.
- Prior `v11.4` failures `34034905290` / `34034904068` / `34034791899` were the
  missing `window.QB.startLibrary('review')` marker; fixed, do not regress.

## What currently works (build-verified; v11.4 fix also device-confirmed by user)

- Practice, Timed CBT, session-review navigator, Submit/Finish, Practice/CBT
  Analysis, Review Solutions + grid + Previous/Next + End Review.
- Home V4/V8 command center (streak + week strip, Today’s Focus with Continue /
  Review-Due-when-due / Practice-20-always / Timed CBT, Subjects, progress,
  Quick Access, Performance, Recent).
- Topics V2 (subject switch, search/filter, counts, progress, chapter entry),
  Chapter (Practice/Timed actions, metrics, source-order library), Tests
  (multi-subject builder), Insights, More, Revision libraries.
- All-subject random practice (`startAllSubjectPractice`) + multi-subject CBT
  (`openMultiSubjectTestBuilder`, `nkMultiExamPoolIds`,
  `nkConfirmMultiSubjectExam`); subject stats fixed (`SUBJECTS.flatMap`,
  `state.attempts` as attempt history).
- Source visuals frozen: 420 PNGs, Anatomy 297 / Physiology 62 / Biochemistry 51
  mapped; source-PDF fallback + fullscreen zoom/pan; Biochemistry isolated;
  Physiology source-PDF authoritative.
- Custom Study Modules (V11.5): persistent reusable sets from subject/topic +
  Unattempted/Wrong/Bookmarked/Mixed pools, frozen IDs, seeded shuffle,
  resume via Practice engine, completion via Practice Analysis; owned by
  `tools/apply_custom_study_modules_v1.py`, tested by
  `tools/test_custom_study_modules_v1.py`.
- Deterministic pipeline: `verify_build_pipeline.py` order enforced,
  `fix_boot_syntax.py` + `node --check` after all transforms, packaged-APK
  verification + `NK-QBank-build-manifest.json` upload.

## Known problems / cautions

- `v11.5` APKs are **build-verified only**; no user physical-device confirmation
  yet. Do not call V11.5 an accepted baseline.
- Workflow display name is `Build V10.1 APK` (path
  `.github/workflows/build-apk.yml`); internal job names vary by branch
  (V11.4.1 Product Polish / V11.5 Custom Study Modules). Use run IDs, not names.
- `main` is stale; `memory.md` still lists `v11-source-visuals` as active —
  treat `.project-memory/` + `git` as current, `memory.md` as background.
- Large binaries (3 PDFs, ~420 PNGs, `index.html` ~6 MB) make full clones slow;
  prefer `gh api` file reads or partial clone for inspection.
- Agent memory (`AGENTS.md` + `.project-memory/`) is present as of this commit; fresh-harness reconstruction check still pending — correct drift when found.

## Unfinished work / next step

1. Physically test the V11.5 APK on device (Home, Topics, Modules create/resume/
   finish, Practice/CBT/Review, Insights, source visuals); promote only on
   explicit approval.
2. Then continue the planned refinement: R1 gold-standard Question Screen
   (typography/density/option states/explanation hierarchy — see `ROADMAP.md`).
3. Keep `STATE.md` updated after each substantial change.
