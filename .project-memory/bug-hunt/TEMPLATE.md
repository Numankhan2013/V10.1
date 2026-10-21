# Bug file template and evidence rules

Every finding is one Markdown file in its area directory. Use the template
below exactly. The main agent reviews each file and fills the final block.

## Naming

`BUG-<area>-<NNN>-<kebab-slug>.md`, for example
`BUG-01-003-restore-point-freeze-without-reload.md`.
`<area>` is `01`…`06`. Numbers are unique inside an area.

## Required content

```markdown
# BUG-01-003 — Short title in plain language

- **Area:** 01 persistence & sync
- **Severity:** high | medium | low
- **Confidence:** high | medium
- **Status:** open — proposed fix, not applied
- **Files:** `path:line`, `path:line`
- **Introduced by:** commit/subject if known, otherwise "unknown"

## What happens

One short paragraph a non-engineer can follow. Name the screen and the action.

## Evidence

Exact code excerpt with line numbers, or a command and its real output.
Evidence must be reproducible from this checkout. Do not paste guesses.

## Learner impact

What the learner loses or sees. State whether it is data loss, a wrong answer,
a stuck screen, a privacy issue, or cosmetic.

## Root cause

The mechanism, not a restatement of the symptom.

## Proposed fix

A minimal unified diff against the files named above. Keep the surrounding
style. If the correct fix needs a product decision, say so and give the
smallest safe option.

```diff
--- a/path
+++ b/path
@@ ...
```

## Verification

- Exact command or manual steps that prove the bug and then the fix.
- Which existing test should be extended, and the assertion to add.
- Regressions to re-check (name the protected flows).

## Alternatives considered

One or two lines. Why the proposed fix is safer than the obvious alternative.

## Main-agent review

- **Verdict:** pending
- **Checked evidence:** no
- **Checked patch:** no
- **Notes:**
```

## Rules

1. **Evidence first.** A finding without a code reference and a concrete
   trigger is deleted, not softened.
2. **One bug per file.** Do not bundle "and also". Split it.
3. **No style, naming, formatting, or speculative performance findings.**
   Performance is allowed only with a measured number.
4. **Do not re-report known issues** already recorded in
   `.project-memory/STATE.md` or `docs/` unless the record is factually wrong;
   then cite the record and say what is wrong.
5. **Do not report sparse-checkout artifacts.** Some large data/PDF files are
   intentionally absent. Environment failures from missing PDFs are not bugs.
6. **Fix must be minimal.** No refactors, no new dependencies, no rewrites of
   protected flows. If the right fix is large, propose the smallest containment
   and mark severity accordingly.
7. **Do not apply the fix.** Product code stays untouched on this branch; the
   diff is reviewed before anyone applies it.
8. **Severity:**
   - `high` — data loss/corruption, wrong scored answer, security/privacy,
     account crossover, or a flow that cannot be completed.
   - `medium` — wrong visible information, a recoverable stuck state, a broken
     secondary action, or a regression with a workaround.
   - `low` — misleading copy, a rare edge case, or a small accessibility gap.
9. **Confidence:** `high` only when you reproduced it or traced every branch.
   Otherwise `medium` and say what is unverified.
10. **Review block stays `pending`.** The main agent owns the verdict.