# Marrow Content Sanitizer — Full Handoff (2026-09-13)

> Purpose: complete continuation record for the learner-facing Marrow content-hygiene/sanitizer work. This file records what was attempted, what was learned, what is currently implemented, what passed, what failed, what must **not** be assumed, and the safest next steps for the next/main agent.
>
> This is a **side-lane handoff**, not a declaration that the branch is merge-ready. Always resolve the live canonical head and current CI before acting.

## Executive status

- Repository: `Numankhan2013/V10.1`.
- Sanitizer branch: `feature/marrow-content-sanitizer-20260912`.
- Sanitizer code/product checkpoint before this memory-only handoff commit: `a3f0e3dafe5707b559beffbaf2828ff47ffed43d` (`Restore canonical source app shell after diagnostics`).
- Sole canonical Marrow/product trunk remains: `feature/marrow-canonical-full-current`.
- Canonical head observed while writing this handoff: `58bb99d5c1fc96a98b4f922a963dba16105487d1` (`Checkpoint Anatomy Ch6 Q1-Q7 exact-head certification`). **Re-resolve it before any transplant/rebase/merge because it may advance again.**
- Canonical is newer than the sanitizer side branch. Do **not** wholesale merge stale branch history into canonical.
- Latest sanitizer full build examined: GitHub Actions run `34705312875`, workflow `Build V11.7 Android + PWA`, sanitizer head `a3f0e3d...`.
- That run passed the sanitizer step, sanitizer tests, Marrow injection, post-injection sanitizer pass, image validation/install, taxonomy validation, explanation validation, final JS syntax, generated product contract, CBT guardrails, final generated-app verification, PWA artifact creation, offline image/cache checks, offline FSRS asset checks, browser dependency install, and recall-dock browser check.
- It then failed at browser step **`Verify Marrow bank selector and native explanation in browser`**.
- Because that browser gate failed, later browser checks, Android/APK packaging, build manifest/package checks, and **Cloudflare Pages preview deployment were skipped**. Therefore there is **no verified sanitizer preview URL** from this run.
- Do not bypass this gate merely to manufacture a preview. Resolve or prove the browser failure first, rerun exact-head CI, then use the normal preview deployment path.

## User intent / problem being solved

The task was to clean learner-visible Marrow content artifacts conservatively across the full corpus without rewriting or “improving” legitimate medical question content. The concrete unwanted class included serialized/encoded learner text and imported page/footer debris such as PrepLadder/QBank page markers. The important requirement was broad coverage across the generated Marrow bank while preserving medical notation and canonical source fidelity.

The solution is deliberately a **render/build-time hygiene boundary**, not a mutation of immutable canonical ED8 source bundles. It should clean what the learner sees while leaving raw imported source authoritative and untouched.

## Core design that emerged

### 1. Sanitize learner-facing fields, not canonical source bundles

`tools/question_content_hygiene_core.js` owns the learner-text behavior. For Marrow questions (`id` beginning `marrow__`) it sanitizes:

- question/stem text;
- explanation/rationale/solution;
- key takeaway/takeaway;
- option text;
- option explanation/rationale/whyWrong/whyCorrect.

For non-Marrow content, the sanitizer keeps the existing narrow stem cleanup behavior rather than broadly flattening content.

### 2. Decode only whole serialized values

`nkSanitizeMarrowText` is intentionally conservative:

- null/undefined become empty text;
- actual structured objects/arrays are flattened to learner text using preferred semantic text keys;
- strings are JSON-decoded only if the **entire trimmed string** looks like a JSON object, array, or quoted JSON string;
- decoding is bounded to two passes to handle common double serialization;
- if parsing fails, the original string is preserved;
- ordinary braces and medical notation are not treated as JSON unless the whole value qualifies.

This is important because aggressive regex cleanup would risk damaging legitimate content such as set notation or physiologic symbols.

### 3. Strip known imported footer/source debris only from stems

`nkCleanQuestionStem` removes known `PrepLadder X Qbank`/subject/page footer patterns and normalizes whitespace. It is not a general-purpose prose rewriter.

### 4. Preserve structured table/explanation behavior

The hygiene core still contains the accepted source-derived takeaway/table logic. A regression specifically protects the soluble-fibre example so the correct table column produces:

`Soluble fibre helps lower LDL cholesterol. This occurs by increasing bile acid excretion and interfering with bile acid reabsorption.`

and does not leak the opposite-column “adds bulk / bowel movements” content.

The sanitizer must not regress the already accepted structured-table renderer or reintroduce `[object Object]` leakage.

### 5. The sanitizer must run twice in the deterministic build

This was the most important architectural discovery.

The ordinary hygiene step occurs **before** canonical Marrow data is injected into the generated app. If hygiene is applied only there, it does not guarantee that all 2,711 Marrow questions traverse the sanitizer.

Current implementation therefore makes the transform idempotent and runs it in two phases:

1. `Apply question content hygiene` runs earlier in the build.
2. `tools/apply_marrow_structured_table_renderer_v1.py`, after canonical Marrow data/renderer injection, calls `apply_question_content_hygiene()` again.

That second pass upgrades both generated bank-registration loops and makes all generated Marrow learner-facing stems/options/explanations cross the same sanitation boundary. It emits `MARROW_POST_INJECTION_CONTENT_HYGIENE_OK`.

**Do not remove the post-injection pass unless the build architecture is changed so Marrow is already present at the first pass.**

## Current implementation files

The important files on the sanitizer branch are:

- `tools/question_content_hygiene_core.js`
  - JS behavior installed into the generated learner app.
  - Contains markers `NK_QUESTION_CONTENT_HYGIENE_V1_START/END`.
  - Provides `nkStructuredText`, `nkSanitizeMarrowText`, `nkSanitizeMarrowQuestion`, `nkCleanQuestionStem`, and accepted takeaway helpers.

- `tools/apply_question_content_hygiene_v1.py`
  - Installs/refreshes the JS core at a stable subject-registry marker.
  - Is deliberately idempotent.
  - Handles pre-Marrow and post-Marrow phases.
  - Upgrades exactly the expected generated bank cleanup blocks when Marrow exists.
  - Refuses unexpected marker/count shapes instead of guessing.

- `tools/test_question_content_hygiene_v1.py`
  - Runs JS behavior tests under Node.
  - Verifies legitimate brace/medical notation survives unchanged.
  - Verifies malformed/non-whole JSON survives unchanged.
  - Verifies single and double JSON wrappers decode.
  - Verifies structured rich text and serialized text arrays flatten safely.
  - Verifies Marrow stem/option/explanation sanitation and idempotence.
  - Verifies the known source-contaminated stem count in the pre-injection source snapshot (currently 78 expected by this test).
  - Is build-phase aware: pre-Marrow expects no generated Marrow registry hooks; post-Marrow expects exactly two.

- `tools/apply_marrow_structured_table_renderer_v1.py`
  - Existing structured-table repair remains narrow/source-preserving.
  - Sanitizer branch imports `main` from `apply_question_content_hygiene_v1.py` and invokes it after Marrow data/table renderer installation.
  - This is the bridge that gives the full generated 2,711-question Marrow bank post-injection hygiene coverage.

- `.github/workflows/build-apk.yml`
  - Runs `Apply question content hygiene` followed by `Test question content hygiene` before Marrow injection.
  - Later invokes the structured-table installer, which performs the second sanitizer pass.

Temporary diagnostic workflow `.github/workflows/marrow-content-sanitizer-apply.yml` was removed after diagnosis. Do not resurrect it as permanent architecture unless there is a new bounded diagnostic need.

## Implementation / diagnostic history worth preserving

Several short-lived patches were used to discover the live generated-bank architecture rather than guessing at stale assumptions. These are history/evidence, not all transplant targets:

- `602634299d5e9ee442133aae08eeee2865f1a17b` — `Sanitize at actual Marrow bank registry boundary`.
- `f1c244660381df94178a71ef2b6f9a92488936b7` — `Align hygiene test with bank registry sanitation`.
- `da4b27ca80ca677c812c626be458102f31afd149` — `Emit live Marrow registry context before sanitation`.
- `91ee09c5235b999643b103ccf7943641abaf076b` — `Probe current generated Marrow runtime path`.
- `a1cf558dffa72dc42facca475330c94357bf336b` — `Make content hygiene idempotent across Marrow build phase`.
- `2ac21265e99b00a565ce01d6b1ec37fce83c3a7c` — `Make hygiene regression phase-aware`.
- `0cb6d61d1f5f152b67d5ef831dd2742f175f2a9b` — bot-generated app shell after applying sanitizer during diagnostic workflow.
- `c7f2b24bcc69bd85741af7fb8ea7e7c09e557421` — `Run content hygiene after Marrow injection`; connects the second pass to the structured-table stage.
- `57f3de16ef3243f2e6d2f4c35ddb389919de665d` — removes temporary diagnostic workflow.
- `a3f0e3dafe5707b559beffbaf2828ff47ffed43d` — restores canonical source app shell after diagnostics; current code/product checkpoint before this handoff commit.

A notable correction made during the work: the sanitizer was initially coupled to a stale topic-numbering patch. Commit `4f71cfa343ee3ac3aed6941357a4912207b2dcf6` deliberately decoupled content hygiene from that stale topic patch. **Keep content sanitation independent of topic-numbering/order repair unless there is a separately verified reason to connect them.**

## What the latest full CI proves

For run `34705312875` on `a3f0e3d...`, the following relevant stages completed successfully before the failure:

- source product contract and deterministic pipeline;
- existing UI/session/Continue Practice transforms and tests;
- `Apply question content hygiene`;
- `Test question content hygiene`;
- cross-device/PWA and FSRS transforms/tests;
- Marrow bank injection;
- canonical structured-table repair **plus post-injection hygiene**;
- Marrow image registry/bindings/progress validation;
- reviewed image installation;
- Marrow bank pilot verification;
- explicit topic taxonomy validation;
- Marrow explanation inventory validation;
- Biochemistry explanation gold/rollout validation;
- Physiology explanation rollout validation;
- final JavaScript syntax;
- generated product contract;
- CBT regression guardrails;
- final generated-app verification;
- Cloudflare PWA artifact **build** (artifact construction only, not deployment);
- Marrow image bytes/offline cache;
- offline FSRS assets;
- generated recall dock browser verification.

This strongly suggests the sanitizer implementation itself is compatible with the deterministic build and generated-data validations through that point. It does **not** establish merge readiness because the learner browser gate still failed.

## Blocking browser failure

Latest run `34705312875` fails at step 82:

`Verify Marrow bank selector and native explanation in browser`

During investigation, the generated Physiology topic cards were observed in a non-sequential visual order resembling:

`1–9, 31–33, 26–30, ...`

rather than a straightforward visual `1–43` sequence expected by the browser assertion.

Important uncertainty:

- I previously described this as a pre-existing ordering problem before proving that claim against an accepted/successful canonical run. That statement was premature and was corrected.
- **Do not assume the failure is pre-existing.**
- **Do not assume the sanitizer caused it either.**
- Establish causality by comparing the same browser test/generated DOM/order on the current accepted canonical head and on a clean rebase/transplant of only the sanitizer scope.

The taxonomy validator itself passed immediately before browser work, which means this is specifically a learner/browser ordering/assertion issue rather than proof that source taxonomy validation is broken.

Because step 82 failed:

- structured-table browser verification was skipped;
- Continue Practice browser pause/resume verification was skipped;
- Marrow image-comparison capture was skipped;
- JDK/Gradle/APK build and package verification were skipped;
- reproducibility manifest was skipped;
- Cloudflare Pages preview deployment was skipped;
- production promotion was skipped.

Therefore **there is currently no verified preview URL for the sanitizer side branch**.

## Lessons / mistakes to avoid

1. **Do not infer generated runtime architecture from the source shell.** The source shell before Marrow injection does not contain the full generated Marrow registry. Probe or inspect the post-transform artifact before choosing hooks.

2. **Do not sanitize only before Marrow injection.** That gives false confidence because the full Marrow bank arrives later. Preserve the post-injection idempotent pass.

3. **Do not rewrite canonical ED8 data for presentation cleanup.** Keep raw imported source immutable; clean learner-facing generated values.

4. **Do not parse every string containing braces as JSON.** Only whole-value candidates should be decoded. Medical/set notation must remain unchanged.

5. **Do not silently swallow malformed JSON.** If it is not valid whole serialized content, preserve the original learner string rather than guessing.

6. **Do not rely on a generated `index.html` diagnostic commit as the source of truth.** The deterministic transforms are the durable implementation. The source app shell was restored after diagnostics.

7. **Do not couple the sanitizer to unrelated topic-numbering/order patches.** That stale coupling was intentionally removed.

8. **Do not call a browser failure “pre-existing” without reproducing the same assertion on an accepted canonical checkpoint.** This was my main reasoning mistake during the final preview investigation.

9. **Do not bypass a failed learner-facing browser gate to obtain a preview.** A PWA artifact existing is not the same thing as a validated/deployed preview.

10. **Do not wholesale merge this old side branch into current canonical.** Canonical advanced after the sanitizer branch diverged. Re-resolve current ownership and transplant/rebase only the intended sanitizer scope.

11. **Keep sanitizer tests phase-aware and idempotence-aware.** The same transform is intentionally invoked twice; a test that assumes only one build phase will create false failures or false confidence.

12. **Preserve accepted Practice/Continue Practice and structured-table invariants.** This lane is content hygiene, not permission to redesign session behavior, navigation, explanations, or tables.

## Recommended next-agent sequence

1. Read `.project-memory/STATE.md`, this handoff, and `docs/MARROW_CANONICAL_AUTOMATION_POLICY.md` in full.
2. Resolve live `feature/marrow-canonical-full-current` head; do not use the `58bb99d...` observation as a hardcoded base.
3. Inventory the sanitizer-only durable changes against live canonical. Prefer a clean transplant/rebase of the minimal relevant files/patches, not branch-wide merge history.
4. Preserve the architecture:
   - hygiene core;
   - idempotent installer;
   - behavior/phase-aware tests;
   - build step before Marrow;
   - post-injection call after Marrow/table installation.
5. Run focused sanitizer behavior tests and data-only Marrow tests.
6. Run the deterministic generated app and inspect that all three subjects / 2,711 Marrow questions are present and post-injection hooks are exactly as expected.
7. Reproduce the Physiology ordering/browser assertion on **current canonical without sanitizer** using the same browser test.
8. If canonical also fails, repair the canonical browser/order contract as a separate, minimal lane and prove no content-sanitation coupling.
9. If canonical passes and sanitizer transplant fails, bisect only the sanitizer delta to identify the regression. Start with generated DOM/topic ordering before changing source taxonomy.
10. Once the browser bank-selector/native-explanation check passes, run the remaining structured-table and Continue Practice browser checks.
11. Run complete Android/PWA/APK/package/image checks on the exact candidate head.
12. Only after full exact-head success, allow normal Cloudflare preview deployment and give the user that preview for physical review.
13. Do not promote to production/main without explicit user approval.
14. After user acceptance, reconcile the verified minimal patch into canonical and update `STATE.md` with exact commit/run/preview evidence.

## Suggested focused verification commands

These are repository commands for the next agent to use/adapt; the authoritative workflow remains CI and current runbooks:

```bash
python3 tools/apply_question_content_hygiene_v1.py
python3 tools/test_question_content_hygiene_v1.py
python3 tools/test_marrow_bank_pilot.py --data-only
python3 tools/test_marrow_topic_taxonomy.py
python3 tools/verify_product_contract.py --stage source
git diff --check
```

For the real candidate, run the repository's complete deterministic build/CI so that Marrow is injected and the second sanitizer pass is exercised. A pre-injection-only local test is insufficient certification.

## Evidence / useful links

- Sanitizer branch: `https://github.com/Numankhan2013/V10.1/tree/feature/marrow-content-sanitizer-20260912`
- Sanitizer code/product checkpoint: `https://github.com/Numankhan2013/V10.1/commit/a3f0e3dafe5707b559beffbaf2828ff47ffed43d`
- Latest examined failed full build: `https://github.com/Numankhan2013/V10.1/actions/runs/34705312875`
- Canonical trunk: `https://github.com/Numankhan2013/V10.1/tree/feature/marrow-canonical-full-current`
- Hygiene core: `tools/question_content_hygiene_core.js`
- Installer: `tools/apply_question_content_hygiene_v1.py`
- Regression suite: `tools/test_question_content_hygiene_v1.py`
- Post-injection bridge: `tools/apply_marrow_structured_table_renderer_v1.py`

## Bottom line

The durable sanitizer approach is sound enough to have passed all deterministic/data/generated/PWA checks reached before the learner browser failure, and its most important architectural feature is the **idempotent post-Marrow second pass**. However, this branch is **not yet certified or preview-ready** because the Physiology bank/topic browser assertion failed and prevented the rest of the release pipeline from running. The next agent should preserve the sanitizer design, rebase/transplant it onto live canonical, independently establish the cause of the topic-order/browser failure, and require a fully green exact-head build before preview or canonical integration.
