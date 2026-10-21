# BUG-06-002 — `build_app_data.py` writes the 19 MB filled page over the source page and never restores it

- **Area:** 06 build, data & content
- **Severity:** medium
- **Confidence:** high
- **Status:** open — proposed fix, not applied
- **Files:** `tools/build_app_data.py:138`, `tools/build_app_data.py:24`, `tools/app_page.py:38`, `.github/workflows/build-apk.yml:140`, `.github/workflows/build-apk.yml:353`
- **Introduced by:** unknown

## What happens

`tools/build_app_data.py` is the only step that turns the source page into the shipped page. It assembles the modules into `app/src/main/assets/index.html` and writes the result — with all question data inlined — back to the **same file**. The source page is therefore destroyed by the build.

The build workflow runs it at line 140, and every later step reads `app/src/main/assets/index.html` expecting the *generated* page. That works in CI, but it means the repository's own source file is now a 19 MB generated artifact for the rest of the job, and the only reason nothing is committed is that the workflow never commits. A developer who follows the tool's own documented usage — `python3 tools/build_app_data.py`, printed in the module docstring at line 24 — silently overwrites the source page with generated output, and the next `git status` shows a 19 MB diff against a file the project insists is source.

The repository already knows about the hazard: `.project-memory/SESSION_LOG.md` records it twice as a "local gotcha" ("`python3 tools/build_app_data.py` without `--check` writes the filled page over `app/src/main/assets/index.html`; build in a scratch worktree, never the source tree", and "Local web build gotcha repeated"). It is a known sharp edge that has now bitten the team twice, and the fix is small.

## Evidence

`tools/build_app_data.py` reads and writes the same path:

```python
24:   python3 tools/build_app_data.py            # assemble and fill index.html in place
...
37:  ROOT = Path(__file__).resolve().parents[1]
38:  ASSETS = ROOT / "app/src/main/assets"
39:  HTML = ASSETS / "index.html"
...
136:    values = {name: build() for name, build in BUILDERS.items()}
137:    page = TOKEN.sub(lambda m: values[m.group(1)], page)
138:    HTML.write_text(page, encoding="utf-8")
```

The docstring calls this "in place" as if it were intended. `tools/app_page.py` shows the same path is the *source*:

```python
21:  ROOT = Path(__file__).resolve().parents[1]
22:  HTML = ROOT / "app/src/main/assets/index.html"
```

and `AGENTS.md` states the rule the build breaks:

> `app/src/main/assets/index.html` is source: edit its markup and scripts directly. Never add a build step that patches it

> `tools/build_app_data.py` (the single data owner) fills in CI.

The build workflow relies on the source file becoming the generated file:

```yaml
140:        run: python3 tools/build_app_data.py
...
353:          grep -q 'NK_QUESTION_PRESENTATION_V1_START' app/src/main/assets/index.html app/src/main/assets/app.css
354:          grep -q 'SOURCE_PDF_EXPLANATION_V18' app/src/main/assets/index.html app/src/main/assets/app.css
```

Both greps run against the *generated* file at the source path.

Two workarounds are already in the repository's memory, both manual:

- `.project-memory/SESSION_LOG.md` line 2584: "Local gotcha: `python3 tools/build_app_data.py` without `--check` writes the filled page over `app/src/main/assets/index.html`; build in a scratch worktree, never the source tree."
- `.project-memory/SESSION_LOG.md` line 2621: "Local web build gotcha repeated: `tools/build_app_data.py` writes the ~19 MB filled page over the source; rebuild `build/web` from a backup (`cp` → fill → `build_web_dist.py --version micro-emphasis` → restore, sha256 checked)."

And the size guard in `tools/test_app_source_parity.py` shows the source page has a hard size ceiling that the generated page blows straight through:

```python
    assemble(page)
    if len(page.encode()) > 1024 * 1024:
        raise SystemExit("index.html must not embed question data or module code; use a token or a module")
```

So after a local `build_app_data.py` run, `test_app_source_parity.py` fails with that message — the tool detects the damage, but only after the fact and only in the test, not in the build.

## Learner impact

No direct learner impact: CI produces a correct artifact, and a developer who follows the memory's "scratch worktree" advice is safe. This is a build-hygiene defect that risks shipping a generated 19 MB file as source — which would put question data into the page the project deliberately keeps data-free, and make every later source edit a 19 MB diff. `medium`: it is a broken/unsafe workflow with a workaround, not a wrong answer for a learner.

## Root cause

`build_app_data.py` has no output-path argument and no separation between "the source page" and "the built page". It resolves `HTML` once, at module scope, and both reads and writes it. Everything downstream (the workflow's greps, `build_web_dist.py`, `verify_product_contract.py --stage generated`) then reads the generated page from the source path, so the two roles are conflated in one file.

## Proposed fix

Give the tool an explicit output path, defaulting to a build directory rather than the source, and update the workflow's later steps to read the generated page from there. This keeps `index.html` source (which is the project's hard rule) and removes the need for the manual backup/restore dance the memory describes.

```diff
--- a/tools/build_app_data.py
+++ b/tools/build_app_data.py
@@ -37,5 +37,7 @@
 ASSETS = ROOT / "app/src/main/assets"
 HTML = ASSETS / "index.html"
 TOKEN = re.compile(r"__NK_DATA_([A-Z_]+?)__")
+import shutil
+BUILT = ROOT / "build/app/index.html"
 
 
 def js_json(value, ascii_only: bool = False) -> str:```

```diff
--- a/tools/build_app_data.py
+++ b/tools/build_app_data.py
@@ -125,6 +125,8 @@
     args = parser.parse_args()
     page = assemble(HTML.read_text(encoding="utf-8"))
     found = TOKEN.findall(page)
+    parser.add_argument("--out", type=Path, default=BUILT,
+                        help="where to write the filled page; the source page is never overwritten")
     unknown = sorted(set(found) - set(BUILDERS))
     missing = sorted(set(BUILDERS) - set(found))
     if unknown or missing:
@@ -135,6 +137,7 @@
     release_marrow_figures()
     values = {name: build() for name, build in BUILDERS.items()}
     page = TOKEN.sub(lambda m: values[m.group(1)], page)
-    HTML.write_text(page, encoding="utf-8")
+    args.out.parent.mkdir(parents=True, exist_ok=True)
+    args.out.write_text(page, encoding="utf-8")
     print(f"APP_DATA_OK tokens={len(found)} kb={len(page.encode()) / 1024:.0f}")
 
 ```

The workflow then writes and reads the built page:

```diff
--- a/.github/workflows/build-apk.yml
+++ b/.github/workflows/build-apk.yml
@@ -137,6 +137,6 @@
       - name: Check the app page against its tested modules
         run: python3 tools/test_app_source_parity.py
       - name: Write question data into the app page
-        run: python3 tools/build_app_data.py
+        run: python3 tools/build_app_data.py --out build/app/index.html
       - name: Install PDF mapping dependency
         run: python3 -m pip install --disable-pip-version-check PyMuPDF Pillow
       - name: Render claimed Biochemistry batch regions on Ubuntu```

```diff
--- a/.github/workflows/build-apk.yml
+++ b/.github/workflows/build-apk.yml
@@ -350,6 +350,6 @@
         run: python3 tools/verify_cbt_invariants.py
       - name: Verify final generated app
         run: |
-          grep -q 'NK_QUESTION_PRESENTATION_V1_START' app/src/main/assets/index.html app/src/main/assets/app.css
+          grep -q 'NK_QUESTION_PRESENTATION_V1_START' build/app/index.html app/src/main/assets/app.css
           grep -q 'SOURCE_PDF_EXPLANATION_V18' app/src/main/assets/index.html app/src/main/assets/app.css
           grep -q 'BIOCHEM_SOURCE_SOLUTIONS' app/src/main/assets/index.html app/src/main/assets/app.css
           grep -q 'SUBJECT_SOURCE_SOLUTIONS' app/src/main/assets/index.html app/src/main/assets/app.css```

Every later step that reads `app/src/main/assets/index.html` for generated content must be repointed at `build/app/index.html`. Before applying, enumerate them:

```
$ grep -n "app/src/main/assets/index.html" .github/workflows/build-apk.yml
335:          s=Path('app/src/main/assets/index.html').read_text(encoding='utf-8')
353:          grep -q 'NK_QUESTION_PRESENTATION_V1_START' app/src/main/assets/index.html app/src/main/assets/app.css
...
```

The `node --check` step at line 335 (which checks the *filled* page's inline scripts) and every `grep` from line 353 onward are the ones that must move. `tools/build_web_dist.py` must then be pointed at the built page as well.

If changing the workflow is judged too large, the minimal containment is to keep the current behaviour but make the tool refuse to overwrite the source without an explicit flag, so the accidental local run fails loudly instead of destroying the file:

```diff
--- a/tools/build_app_data.py
+++ b/tools/build_app_data.py
@@ -133,5 +133,7 @@
         print("APP_DATA_TOKENS_OK " + " ".join(f"{name}x{found.count(name)}" for name in BUILDERS))
         return
     release_marrow_figures()
+    if not args.in_place:
+        raise SystemExit("build_app_data.py writes the filled page; pass --in-place to overwrite the source page")
     values = {name: build() for name, build in BUILDERS.items()}
     page = TOKEN.sub(lambda m: values[m.group(1)], page)
     HTML.write_text(page, encoding="utf-8")```

## Verification

- Reproduce: `python3 tools/build_app_data.py` in a clean checkout, then `git status --short` → `app/src/main/assets/index.html` shows a ~19 MB modification; `python3 tools/test_app_source_parity.py` fails with "index.html must not embed question data or module code".
- After the fix: `python3 tools/build_app_data.py` writes `build/app/index.html` and leaves `git status --short` clean; `python3 tools/test_app_source_parity.py` still passes.
- Existing test to extend: `tools/test_app_source_parity.py` already asserts the source page stays under 1 MB. Add an assertion that `app/src/main/assets/index.html` still carries its `__NK_DATA_*__` tokens after a build, so the source page can never silently become the generated page.
- Regressions to re-check: the whole CI build order (`tools/verify_build_pipeline.py` enforces the order of `tools/test_app_source_parity.py` → `tools/build_app_data.py` → … → `tools/build_web_dist.py` → `tools/run_browser_suite.py`), the packaged-page checks (`verify_product_contract.py --stage packaged`), and the local web build path (`tools/build_web_dist.py --version <sha>`).

## Alternatives considered

Writing the generated page to `build/app/index.html` and leaving the workflow alone is impossible — later steps read the source path. Copying the source back after the build (`shutil.copy` of a saved original) was the manual workaround the team already uses and is what the `--out` change replaces; it is strictly more fragile than naming the output.

## Main-agent review

- **Verdict:** approved
- **Checked evidence:** yes
- **Checked patch:** yes
- **Notes:** Verified build_app_data.py:24, 37-39 and 138: the tool reads and writes the same path, and the source page is the path AGENTS.md and tools/app_page.py treat as source. The repository memory records the same hazard twice as a local gotcha, which is evidence that the current shape is a real trap rather than a designed behaviour. The --out change is the right fix and the workflow hunks correctly identify the steps that must be repointed. Approved, with the implementer note that the full list of workflow steps reading app/src/main/assets/index.html for generated content (the node --check step at line 335 and every grep from line 353 onward) must be enumerated and moved, not just the two shown.
