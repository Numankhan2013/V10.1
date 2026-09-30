# Manual Marrow image integration ledger

This is the shared ownership and progress ledger for manual image work on the
canonical branch, `feature/marrow-canonical-full-current`. Read the live remote
version before choosing a batch. The source-reference denominator is
`data/marrow/images/coverage.json`; a chapter claim includes every question and
explanation figure reference in that chapter, including later discovered source
visuals. Raw source and source PDFs remain unchanged.

## Claims

### Active resume ownership — 2026-09-30

This table supersedes the paused Wave 2 ownership rows below for unfinished
items. The existing Physiology Ch3–7 claim remains reserved to its separate
owner and is excluded from this resume. Canonical starting product is
`a6f2bca10228c62c8ef8fa9b837f8ccfb7d3c9fa`. Its coverage contains 1,186 released,
18 metadata-invalid, 228 unresolved source references and 59 text-cue checks.
The separate Ch3–7 claim contains 49 unresolved references and one text cue;
these four resume batches partition all other 237 outstanding items exactly.

| Batch | Exclusive source ownership | Starting unresolved refs | Starting text cues | Owner/status | Working branch |
| --- | --- | ---: | ---: | --- | --- |
| `manual-resume-anatomy-ch01-59-20260930` | Anatomy Ch1–59, all remaining refs/cues and newly discovered visuals | 69 | 0 | Luna 6 medium worker A / MERGED; canonical dual-green | `manual/resume-anatomy-ch01-59-20260930` |
| `manual-resume-anatomy-ch60-63-20260930` | Anatomy Ch60–63 completed; 29 exact Biochemistry cue questions below reserved | 52 | 29 transferred | Luna 6 medium worker B / both batches MERGED; final CI pending | `manual/resume-anatomy-ch60-63-20260930` |
| `manual-resume-physiology-ch08-14-20260930` | Physiology Ch8–14 completed; 27 exact tail cue questions below | 52 | 27 transferred | Luna 6 medium worker C / both batches MERGED; final CI pending | `manual/resume-physiology-ch08-14-20260930` |
| `manual-resume-biochem-physiology-tail-20260930` | Six source questions plus Biochemistry Ch3 Q12/Q14; coverage support; see transfers below | 6 | 2 retained | Luna 6 medium worker D / MERGED; final CI pending | `manual/resume-biochem-physiology-tail-20260930` |

Workers use fresh separate worktrees from the claim commit. The old dirty
`V10.1-wave2-anatomy-ch56-63` worktree is preserved as a read-only donor: A may
reuse its Ch56–59 candidates; B may reuse its Ch60–63 candidates after source
comparison and validation. Never overwrite or clean that donor. Existing
Anatomy Ch1–26 and Ch27–44 ignored source artifacts are also reusable evidence.
No worker edits shared learner-text manifests or another worker's branch.
Root serializes stable-ID registry/asset integration; passing branch checks do
not establish canonical preview deployment. Production remains deferred.

| Batch | Owner | Exclusive source scope | Starting backlog | Status | Working branch and base |
| --- | --- | --- | --- | --- | --- |
| `manual-biochem-ch25-28-20260928` | Codex, this user thread | Biochemistry Chapters 25–28, all source visuals and visual text cues | 22 references across 21 questions: Ch25 2, Ch26 5, Ch27 7, Ch28 8; 0 text-cue items | **COMPLETE / CANONICAL VERIFIED** | `feature/marrow-manual-images-20260928` from `e6fb3f813eb2c49a5220eec774ae60e551a7169f` |
| `manual-physiology-ch03-07-20260928` | ChatGPT manual lane, this user thread | Physiology Chapters 3–7, all source visuals and visual text cues | 49 unresolved references across 39 questions: Ch3 5, Ch4 2, Ch5 2, Ch6 7, Ch7 33; 0 text-cue items | **CLAIMED / IN PROGRESS** | `manual/physiology-images-ch03-07-20260928` from the canonical claim commit; refresh registry/progress/coverage from live canonical after Biochemistry integration before shared-state writes |
| `manual-wave2-anatomy-ch01-26` | Worker 1, Luna 6 medium | Anatomy Chapters 1–26, every source visual and visual text cue | 332 unresolved source references; 0 text cues | **PAUSED AT USAGE LIMIT / VALIDATED CHECKPOINT IN CANONICAL** | `manual/wave2-anatomy-ch01-26` at `b4ad582e`; five crop decisions remain |
| `manual-wave2-anatomy-ch27-44` | Worker 2, Luna 6 medium | Anatomy Chapters 27–44, every source visual and visual text cue | 321 unresolved source references; 0 text cues | **PAUSED AT USAGE LIMIT / VALIDATED CHECKPOINT IN CANONICAL** | `manual/wave2-anatomy-ch27-44` at `1ae26e10`; four union crops and one ambiguous duplicate remain |
| `manual-wave2-anatomy-ch45-55` | Worker 3, Luna 6 medium | Anatomy Chapters 45–55, every source visual and visual text cue | Original Ch45–63 claim narrowed after Ch52 checkpoint; 196 references in Ch45–55, 0 text cues | **COMPLETED / INTEGRATED** | `manual/wave2-anatomy-ch45-63` at `05fc781f`; 194 released, one held, one invalid |
| `manual-wave2-anatomy-ch56-63` | Worker 5, Luna 6 medium | Anatomy Chapters 56–63, every source visual and visual text cue | 110 untracked source references in Ch56–63; 0 text cues at transfer | **PAUSED AT USAGE LIMIT / NOT YET IN CANONICAL** | `manual/wave2-anatomy-ch56-63` has uncommitted source originals and registry work; preserve the worktree and finish validation before integration |
| `manual-wave2-biochem-physiology` | Worker 4, Luna 6 medium | Biochemistry Chapters 1–24 and Physiology Chapters 8–43, every source visual and visual text cue | 16 Biochemistry + 197 Physiology unresolved source references; 31 Biochemistry + 27 Physiology text cues | **CHECKPOINT INTEGRATED / COVERAGE REOPEN REQUIRED** | `manual/wave2-biochem-physiology` at `502b7a4`; its prior 217 released and 61 held or invalid tally did not close subject coverage; exact-head CI `36446066984` passed |

The 22 reference IDs for `manual-biochem-ch25-28-20260928` are the unresolved
`Biochemistry` / `CH25`–`CH28` rows of the canonical coverage file at claim time.
They include both roles of `marrow__BIOCHEM_CH28_Q022`; its question figure must
be safe before answering.

The 49 reference IDs for `manual-physiology-ch03-07-20260928` are every unresolved
`Physiology` / `CH03`–`CH07` source-visual row in the same canonical coverage
state. Forty of those references were already source-audited in historical
fast-lane evidence `MANUAL_FASTLANE_34700776495`; that evidence is donor/history
only and must be revalidated against live ownership before release. The remaining
nine unresolved Ch7-tail references (after Q21) require fresh authoritative source
review. No historical registry/progress mutation is transplanted wholesale.

The four Wave 2 claims partition every currently unclaimed unresolved Marrow
source reference and text cue. The earlier Physiology Ch3–7 claim remains with
its existing owner, including the one live Ch5 text cue; no Wave 2 worker may
edit it. Worker branches use separate worktrees. Each worker owns newly
discovered visual references inside its chapter ranges as well as the listed
coverage rows. The shared registry, progress and coverage files are reconciled
serially into canonical after each independent branch passes its own checks.
Wave 2 starting state: canonical `78f1ae00b25f4df3ad9f4515e5b3c8f31d0e5b59`;
registry SHA-256 `8e92e25daec03c566fdb34b66cadd28a85a8367c3081891a0e29b1c70ab5544a`;
progress SHA-256 `281549a33e54235d8d3938617952976c50dc875cc3ff5fe4a2087b57ee02b1a2`;
coverage SHA-256 `750d13c0590fadb3af158885ff605efbba9f7bfe37afaa83c74958027b74456`.

### Wave 2 canonical integration checkpoint (2026-09-29)

Canonical `ce195a3f` includes the validated Worker 1 checkpoint `b4ad582e`,
Worker 2 checkpoint `1ae26e10`, and Worker 3 final checkpoint `05fc781f`.
The canonical coverage file reports Anatomy **897 released / 10 invalid / 6
tracked pending / 115 untracked of 1,028 source visual references**. The
remaining untracked references are Worker 1's five unresolved crops and Worker
5's 110-reference Ch56–63 range. Worker 2 owns five pending references; Worker
3 owns the remaining one. Worker 1 and Worker 2 reached the account usage limit
before the final crop decisions. Worker 5's Ch56–63 worktree contains
uncommitted source files and must not be merged or overwritten yet.

The Cloudflare feature preview was independently fetched after exact-head run
`36518849149`: its `marrow_visual_metadata.js` bytes match canonical
`43d3ecbb`, with 896 Anatomy source references released at that deployed SHA;
a sampled Anatomy image URL returned bytes matching its SHA-256 filename.
`ce195a3f` adds one validated Ch46 reference. Its preview build
`36540145496` deployed successfully, and the served metadata bytes match that
commit: 897 Anatomy source references are released in the live feature preview.
Production remains unpromoted.

The Biochemistry/Physiology batch above is a merged checkpoint, not a completed
subject. Current canonical coverage is Biochemistry **103 released / 3 invalid /
2 tracked pending / 2 untracked of 110** and Physiology **186 released / 5
invalid / 21 tracked pending / 82 untracked of 294**. In Worker 4's assigned
range, Physiology Ch8–43 still has 47 untracked references and 7 tracked
pending; Biochemistry Ch1–24 has 2 untracked and 2 tracked pending. The separate
Physiology Ch3–7 claim has 35 untracked and 14 tracked pending. Reopen these
owned ranges with their original owners or explicitly transfer them before a
new worker edits the same chapters; source-fidelity review remains required.

### Wave 2 resume checkpoint (2026-09-29)

Canonical `3a7420af` contains Worker 4's completed Biochemistry Ch1–24 and
Physiology Ch8–43 batch. Its exact-head build and Android interaction run
`36449078612` passed. The three Anatomy branches below remain separate and
are still exclusively owned by their original workers; none is merged yet.

| Batch | Pushed branch head at pause | Released refs | Tracked pending or invalid refs | Untracked refs | Next source work |
| --- | --- | ---: | ---: | ---: | --- |
| Anatomy Ch1–26 | `39d9a350` | 273 | 9 held | 50 | Native-candidate selection plus exact Ubuntu regions for composite/vector figures; source artifact from `36432679371` is in this worker's ignored cache. |
| Anatomy Ch27–44 | `0291137d` | 125 | 112 held | 84 | Review Ch33–44 and the final Ch29 Q11 union crop; run `36448416847` passed and its artifact is available. |
| Anatomy Ch45–63 | `a194e234` | 114 | 1 held, 1 invalid | 190 | Continue Ch52–63 and unresolved grouped figures from earlier chapters; source render/upload run `36431980518` passed. |

These counts partition the 959 Anatomy references claimed by Wave 2 at the
start: 512 released, 123 tracked pending or invalid, and 324 untracked at the pause.
They are branch-local counts; do not add their shared registry/progress/coverage
files together by copying one over another. Reconcile by stable reference and
asset IDs into the live canonical branch, then regenerate derived files and run
the repository checks. Production promotion remains deferred.

On resume, the user authorized one additional worker. Worker 3 confirmed it had
made no edits or source decisions in Ch56–63. Its original Ch45–63 range was
therefore divided at the chapter boundary: Worker 3 exclusively owns Ch45–55
(196 total references, with 80 still unresolved at the Ch52 checkpoint), and
Worker 5 exclusively owns Ch56–63 (110 untracked references at transfer).
The table above retains the original paused Ch45–63 checkpoint for audit; the
two new claims replace its ownership boundary. Do not assign either chapter
range to another worker while these claims are active.

Starting fingerprints for both claims: registry SHA-256
`799f0c3ae5753f9321f46803871032f255a0548798c4884681f297a5eaa729a2`,
progress SHA-256
`c2ecb00176b4edfd946006cd650ffb513c855b065a73af53abdbcf25b332366d`,
coverage SHA-256
`a932992616c6431916dffcc2d063710d6721a1d773f32dba4698b0532b1a63de`.

## Coordination rule

1. Claim a separate subject/chapter range in this file on the **live canonical
   branch**, commit it and push with an ordinary fast-forward before source work.
   Check the remote branch head again immediately before the push. Never take an
   overlapping range while its claim is active, even after a restart.
2. A claim reserves source ownership, not permission for concurrent writes to
   `registry.json`, `progress.json`, `coverage.json` or production image assets.
   Agents may inspect separate ranges in parallel. Re-fetch and reconcile the
   shared image state before each integration commit; one writer publishes at a
   time. Never choose one side of a registry conflict.
3. Record each chapter's released, review-required and still-untracked counts
   here. A deferred image stays in the claimed batch until the owner explicitly
   releases or hands off that chapter. A restart resumes the claim after reading
   this ledger and live coverage; it does not create a second claim.
4. Mark a batch complete only after source review, image validation, progress
   and coverage checks, local gates, and the required exact-head CI. Reconcile
   the verified image state to canonical before releasing the claim. Production
   promotion and physical acceptance remain separate.

## Batch `manual-biochem-ch25-28-20260928`

| Chapter | Starting unresolved references | Released in this batch | Review required | Remaining untracked | Notes |
| --- | ---: | ---: | ---: | ---: | --- |
| 25 | 2 | 2 | 0 | 0 | Q11 and Q26 released; Q26 is SOURCE_LIMITED for small inline labels, with exact source pixels and tap-to-expand viewer; source pages 395–402 |
| 26 | 5 | 5 | 0 | 0 | Q18 is SOURCE_LIMITED: source watermark crosses fine factor labels; exact source crop is inspectable in expanded view; source pages 413–417 |
| 27 | 7 | 6 | 0 | 0 | Q2/Q3 released SOURCE_LIMITED for faint but enlarged-readable condition labels; Q5 adjudicated invalid against page 426; source pages 424–430 |
| 28 | 8 | 8 | 0 | 0 | Q27 released SOURCE_LIMITED because the source watermark crosses some bond detail; exact crop retained; Q22 question and explanation figures separately bound |

## Batch `manual-physiology-ch03-07-20260928`

| Chapter | Starting unresolved references | Released in this batch | Review required | Remaining untracked | Notes |
| --- | ---: | ---: | ---: | ---: | --- |
| 3 | 5 | 0 | 0 | 5 | Source pages 44–53; historical fast-lane donor evidence exists |
| 4 | 2 | 0 | 0 | 2 | Source pages 62–66; historical fast-lane donor evidence exists |
| 5 | 2 | 0 | 0 | 2 | Source pages 73–74; historical fast-lane donor evidence exists |
| 6 | 7 | 0 | 0 | 7 | Source pages 94–109; historical fast-lane donor evidence exists |
| 7 | 33 | 0 | 0 | 33 | Source pages 137–158; first 24 unresolved refs have historical donor evidence, final 9 require fresh review |

All five former visual holds are reviewed as SOURCE_LIMITED and included in the learner runtime: Ch25 Q26, Ch26 Q18, Ch27 Q2/Q3 and Ch28 Q27. The authentic pixels were retained unchanged; watermark and faint-label limitations are documented, and tap-to-expand zoom is available. Q27 Q5 remains an exact source-metadata-invalid adjudication. All 22 starting references are accounted for (21 released, 1 invalid; none untracked or review-required in this batch). The batch has no unresolved source-reference work; subject-wide Biochemistry coverage remains incomplete. Candidate commit `ef969540171b3cb19d724a28f3adbf0fba42f5f7` passed Engineering `36425459384` and full browser/PWA/APK/package/emulator run `36425386902`. It was fast-forward integrated at canonical product commit `ef969540171b3cb19d724a28f3adbf0fba42f5f7`; canonical Engineering `36427679654` and full run `36427679667` passed on that exact SHA. Preview `https://27f74250.nk-qbank.pages.dev` and canonical feature alias `https://feature-marrow-canonical-ful.nk-qbank.pages.dev` returned HTTP 200. Production promotion was skipped.

Status is a live work log, not a claim that these images are already integrated. Each owner updates it with evidence and exact verification results as work lands.

### Resume B/C canonical integration — 2026-09-30

Root reconciled source-validated worker commits `dc488f12` (Anatomy Ch60–63)
and `18766fd8` (Physiology Ch8–14) by stable registry/adjudication IDs. No
conflicting asset edits were found. Worker B completed 51 released references
and one source-metadata-invalid reference of 52; Worker C completed 19
released and 33 source-metadata-invalid references of 52. Both workers passed
release/progress/coverage checks and all 51 local checks. Exact evidence is in
the source-reference adjudications; root did not repeat source review. Shared
runtime metadata, progress and coverage are regenerated from the combined
registry. Canonical CI/preview verification is pending for this checkpoint.
Worker A continues Anatomy Ch1–59; worker D now owns the reserved Biochemistry
Ch1–24 / Physiology Ch15–43 range. Separate Physiology Ch3–7 ownership remains.

### Tail source-review ownership transfer — 2026-09-30

Worker D confirmed no cue decisions or edits before this transfer. To keep
source reviews parallel, completed worker C resumes the 27 Physiology
metadata-free cue questions below in branch
`manual/resume-physiology-tail-cues-20260930`, based on canonical `a656edd1`.
D now owns Biochemistry Ch1–24 (four source refs and 31 cues), plus Physiology
Ch34 Q4 and Ch37 Q24 (two source refs). C exclusively owns every source visual
and cue for the following questions; D excludes them. C also retains its
completed Ch8–14 batch. No question belongs to both workers.

- Physiology Ch20 Q11/Q12/Q16/Q18; Ch21 Q6/Q9/Q12; Ch22 Q8/Q10/Q13.
- Physiology Ch23 Q3/Q4/Q8/Q12/Q14/Q15/Q16; Ch25 Q5/Q9; Ch26 Q16.
- Physiology Ch27 Q13; Ch28 Q10/Q26; Ch31 Q1; Ch32 Q4; Ch33 Q17; Ch38 Q1.

D owns the minimal shared coverage support for source-reviewed cue decisions.
C records source evidence/assets in existing conventions and coordinates that
format directly with D; root reconciles only their disjoint stable IDs.

### Biochemistry cue transfer to completed worker B — 2026-09-30

D confirmed only Ch3 Q12/Q14 were source-reviewed and all other 29 Biochemistry
cues are unmodified. D retains those two cue questions, Biochemistry Ch7 Q5/Q6,
Ch8 Q3, Ch10 Q14, and Physiology Ch34 Q4 / Ch37 Q24, plus shared cue coverage
support. Worker B resumes the remaining 29 Biochemistry cue questions below
after a concurrency slot opens, on a new branch in its preserved worktree;
its completed Anatomy Ch60–63 commit remains unchanged. B owns all visuals
and cues for these exact questions; D excludes every one of them.

- Biochemistry Ch12 Q5; Ch15 Q6/Q19/Q20; Ch17 Q3/Q4/Q14; Ch18 Q15.
- Biochemistry Ch19 Q11/Q12/Q19; Ch20 Q6; Ch21 Q8/Q9/Q10/Q12.
- Biochemistry Ch22 Q2/Q4/Q5/Q6/Q7/Q8/Q10; Ch23 Q9.
- Biochemistry Ch24 Q1/Q3/Q10/Q12/Q16.

This transfer keeps four worker agents total and preserves disjoint question
ownership. No source review is duplicated; root integrates committed deltas.

### Anatomy Ch1–59 final worker checkpoint — 2026-09-30

Worker A committed `0243a614`: 64 released raw references, four invalid
metadata references, and one explicit hold of its 69 assigned references.
Two corrected-page question images also ship: Ch23 Q9 (p395/xref1104) and
Ch25 Q7 figure2 (p425/xref1187). Their incorrect raw page mappings remain
invalidated. Ch25 Q13’s missing/wrong explanation figure and Ch35 Q5’s
nonexistent second image are source-invalid. Ch45 Q4 stays held: its source
image has no required visible mark. No marker was invented.

Registry validation/release, progress/coverage generation and checks, memory
and diff checks passed. The local suite passed every check except a registry
ordering-sensitive mutation test; restoring the original array order fixed
that failure and its targeted retry passed. Root merges stable-ID deltas and
regenerates combined derived files; canonical CI/preview verification follows.
B/C canonical checkpoint `a656edd1` passed Engineering `36670768116` and full browser/PWA/APK/Android phone/tablet run `36670768102`; live metadata and sampled image bytes match. Worker B now resumes its 29 reserved Biochemistry cues in a new branch in
the preserved Anatomy Ch60–63 worktree.

### Worker D final integration checkpoint — 2026-09-30

Worker D completed six source refs and two retained cues at `997f0c1f`:
Biochemistry Ch7 Q5/Q6 and Physiology Ch34 Q4 / Ch37 Q24 are released;
Biochemistry Ch8 Q3 / Ch10 Q14 have exact invalid-metadata adjudications;
Ch3 Q12/Q14 have pinned-source no-visual evidence. Its source cue coverage
support is committed through `e0502485` (earlier `db17e740`, `13bea5f6`).
Release, progress/coverage checks, cue tests, memory and diff checks passed.
The one local-suite failure was stale derived progress before regeneration;
the targeted image test passed after regeneration. Root merged the four
asset IDs, two adjudications and two cue reviews without conflicts. Combined
derived output/CI will be refreshed with the B/C cue checkpoints.

Anatomy canonical checkpoint `e3cef56d` is dual-green: Engineering
`36673442104`, full browser/PWA/APK/Android `36673441905`. Live preview
metadata bytes match its committed release exactly (1,051 visual-owning
questions across the bank). Production remains unpromoted.

### Worker C tail cue integration checkpoint — 2026-09-30

C committed `6fbbcdda` / `34b893fd`: 32 cue-derived source refs across 24
Physiology cue questions, backed by 31 exact native JPEG assets. All linked
refs are released; Ch23 Q8 / Ch25 Q9 / Ch38 Q1 are source-reviewed no-visual
cases. All 27 assigned cues are closed. Explicit continuation pages and global
figure ordering were corrected after coverage caught them. Image release,
progress/coverage generation and checks, all 51 local checks, and memory
verification passed. Root merged the disjoint stable IDs without conflicts.
B’s 29 Biochemistry cue questions are the last checkpoint pending checks.

### Worker B cue integration / combined final checkpoint — 2026-09-30

B committed `20cc85bb`: all 29 Biochemistry cue questions are reviewed, with
28 released cue-derived refs (11 question / 17 explanation). Ch17 Q14 is a
confirmed source omission: its prompt refers to a teeth image absent from
source pages 265/277. It is explicitly not visually complete; no replacement
was invented. Release, progress/coverage checks, all 51 local checks, memory
and diff checks passed. Its two prior Anatomy candidate JPGs remain untouched.

Root merged D `997f0c1f`, C tail `34b893fd` and B tail `20cc85bb` by disjoint
stable IDs with no registry/asset conflicts. Original resume workload: 179
source refs + 58 cues = 237 items. Workers resolved 178 source refs and all
58 cues; Anatomy Ch45 Q4 remains held for absent source marker. The separate
Physiology Ch3–7 claim remains reserved (49 refs + one cue). Cue reviews added
60 source-derived refs (Biochemistry 28, Physiology 32); immutable raw audits
and source bundles were retained. Combined full CI/preview verification follows.

Combined release caught a portability issue in D’s four region assets: eight
original/production path fields referenced the worker’s absolute worktree.
Root normalized only these paths to repository-relative paths, verified
unchanged SHA-256 against copied files, and retained the strict containment
validator. Pixel content, source citations and QA evidence remain unchanged.

Combined regeneration confirmed: Anatomy 1,012 released / 15 invalid / one
held of 1,028; Biochemistry 133 released / five invalid / none unresolved of
138; Physiology 239 released / 38 invalid / 49 unresolved of 326. Across
1,492 source refs, 1,384 are released, 58 invalid and 50 unresolved. Sixty
refs were discovered through cue review; one reserved Physiology cue remains.
Runtime contains 1,107 visual-owning questions and 1,449 released bindings
(347 question / 1,102 explanation). These are distinct denominators. Root’s
lightweight integration sanity passed; canonical full CI/preview is pending.
