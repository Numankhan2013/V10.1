# BUG-06-002 — `build_app_data.py` writes the 19 MB filled page over the source page and never restores it

- **Area:** 06 build, data & content
- **Severity:** medium
- **Confidence:** high
- **Status:** fix applied — commit 5a2d2fae
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
@@ -21,8 +21,12 @@
 collections, Marrow figures). Every token must be replaced; any token left over
 fails the build.
 
-  python3 tools/build_app_data.py            # assemble and fill index.html in place
+  python3 tools/build_app_data.py            # assemble and fill the page into build/app/
   python3 tools/build_app_data.py --check    # list the tokens without writing
+  python3 tools/build_app_data.py --out PATH # write the filled page somewhere else
+
+The source page is never overwritten: it is a template with data tokens, and
+the filled page is what ships.
 """
 from __future__ import annotations
 
@@ -36,6 +40,7 @@
 ROOT = Path(__file__).resolve().parents[1]
 ASSETS = ROOT / "app/src/main/assets"
 HTML = ASSETS / "index.html"
+BUILT = ROOT / "build/app/index.html"
 TOKEN = re.compile(r"__NK_DATA_([A-Z_]+?)__")
 
 
@@ -122,6 +127,8 @@
 def main() -> None:
     parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
     parser.add_argument("--check", action="store_true", help="report the tokens in index.html without writing")
+    parser.add_argument("--out", type=Path, default=BUILT,
+                        help="where to write the filled page; the source page is never overwritten")
     args = parser.parse_args()
     page = assemble(HTML.read_text(encoding="utf-8"))
     found = TOKEN.findall(page)
@@ -135,8 +142,10 @@
     release_marrow_figures()
     values = {name: build() for name, build in BUILDERS.items()}
     page = TOKEN.sub(lambda m: values[m.group(1)], page)
-    HTML.write_text(page, encoding="utf-8")
-    print(f"APP_DATA_OK tokens={len(found)} kb={len(page.encode()) / 1024:.0f}")
+    out = args.out if args.out.is_absolute() else ROOT / args.out
+    out.parent.mkdir(parents=True, exist_ok=True)
+    out.write_text(page, encoding="utf-8")
+    print(f"APP_DATA_OK tokens={len(found)} kb={len(page.encode()) / 1024:.0f} out={out}")
 
 
 if __name__ == "__main__":
--- a/tools/build_web_dist.py
+++ b/tools/build_web_dist.py
@@ -17,6 +17,9 @@
 ROOT = Path(__file__).resolve().parents[1]
 ASSETS = ROOT / "app/src/main/assets"
 DEFAULT_OUT = ROOT / "build/web"
+# The page the app ships is the one build_app_data.py filled; the source page is
+# only a template with data tokens.
+BUILT_PAGE = ROOT / "build/app/index.html"
 PAGES_FILE_LIMIT = 25 * 1024 * 1024
 ROBOTS_DIRECTIVES = "noindex, nofollow, noarchive, nosnippet, noimageindex"
 
@@ -131,7 +134,12 @@
     parser = argparse.ArgumentParser()
     parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
     parser.add_argument("--version", default="dev")
+    parser.add_argument("--page", type=Path, default=None,
+                        help="the filled app page to ship; defaults to build/app/index.html when it exists")
     args = parser.parse_args()
+    page_source = args.page if args.page else (BUILT_PAGE if BUILT_PAGE.is_file() else ASSETS / "index.html")
+    if not Path(page_source).is_file():
+        raise SystemExit(f"the app page to ship is missing: {page_source}")
     out = args.out if args.out.is_absolute() else ROOT / args.out
     if out.exists():
         shutil.rmtree(out)
@@ -140,15 +148,19 @@
     for source in ASSETS.rglob("*"):
         if not source.is_file():
             continue
+        if source == ASSETS / "index.html":
+            # The filled page ships instead of the source template.
+            continue
         relative = source.relative_to(ASSETS)
-        # index.html carries the inline question data until externalize_data
-        # moves it out; the output check below covers what it leaves behind.
-        if source.stat().st_size > PAGES_FILE_LIMIT and source.name != "index.html":
+        if source.stat().st_size > PAGES_FILE_LIMIT:
             skipped.append(str(relative))
             continue
         target = out / relative
         target.parent.mkdir(parents=True, exist_ok=True)
         shutil.copy2(source, target)
+    # The filled page carries the inline question data until externalize_data
+    # moves it out; the output check below covers what it leaves behind.
+    shutil.copy2(page_source, out / "index.html")
     config_path=out / "qbank-config.js"
     config=json.loads(re.search(r"=\s*(\{.*\})\s*;",config_path.read_text()).group(1))
     anatomy_url=config.get("anatomyPdfUrl", "")
--- a/.github/workflows/build-apk.yml
+++ b/.github/workflows/build-apk.yml
@@ -137,7 +137,9 @@
       - name: Check the app page against its tested modules
         run: python3 tools/test_app_source_parity.py
       - name: Write question data into the app page
-        run: python3 tools/build_app_data.py
+        run: |
+          python3 tools/build_app_data.py --out build/app/index.html
+          cp app/src/main/assets/app.css build/app/app.css
       - name: Install PDF mapping dependency
         run: python3 -m pip install --disable-pip-version-check PyMuPDF Pillow
       - name: Render claimed Biochemistry batch regions on Ubuntu
@@ -332,7 +334,7 @@
           python3 - <<'PY'
           from pathlib import Path
           import re, subprocess, tempfile
-          s=Path('app/src/main/assets/index.html').read_text(encoding='utf-8')
+          s=Path('build/app/index.html').read_text(encoding='utf-8')
           scripts=re.findall(r'<script(?:[^>]*)>(.*?)</script>', s, re.S|re.I)
           with tempfile.TemporaryDirectory() as td:
               checked=0
@@ -345,68 +347,68 @@
           print(f'INLINE_JS_SYNTAX_OK={checked}')
           PY
       - name: Verify generated product contract
-        run: python3 tools/verify_product_contract.py --stage generated
+        run: python3 tools/verify_product_contract.py --stage generated --html build/app/index.html
       - name: Enforce CBT regression guardrails
         run: python3 tools/verify_cbt_invariants.py
       - name: Verify final generated app
         run: |
-          grep -q 'NK_QUESTION_PRESENTATION_V1_START' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'SOURCE_PDF_EXPLANATION_V18' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'BIOCHEM_SOURCE_SOLUTIONS' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'SUBJECT_SOURCE_SOLUTIONS' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'anatomy-' app/src/main/assets/index.html app/src/main/assets/app.css
+          grep -q 'NK_QUESTION_PRESENTATION_V1_START' build/app/index.html app/src/main/assets/app.css
+          grep -q 'SOURCE_PDF_EXPLANATION_V18' build/app/index.html app/src/main/assets/app.css
+          grep -q 'BIOCHEM_SOURCE_SOLUTIONS' build/app/index.html app/src/main/assets/app.css
+          grep -q 'SUBJECT_SOURCE_SOLUTIONS' build/app/index.html app/src/main/assets/app.css
+          grep -q 'anatomy-' build/app/index.html app/src/main/assets/app.css
           grep -q 'NK_THIN_SHELL_V1' app/src/main/java/com/qbank/biochemistry/MainActivity.java
-          grep -q 'qbank-question-ui-v2' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'qbank-practice-analysis-v1' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'qbank-ui-polish-v1' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'qbank-ui-polish-v2' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'qbank-home-insights-polish-v1' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'qbank-option-feedback-polish-v1' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'qbank-practice-cleanup-v1' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'qbank-option-hole-cleanup-v1' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'nk-home-v4' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'nk-home-v4-style' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'NK_HOME_V5_FIXES' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'nk-topics-v2' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'openSubjectTopics' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'resetScrollPosition' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'requestAnimationFrame(() => window.scrollTo(0,0)' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'nk-home-streak-header-v1' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'nk-home-streak' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'currentStreak()' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'body:has(.nk-home-v4) .topbar' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'nk-home-actions-v1' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'Continue Practice' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'Build a test' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'Quick test' app/src/main/assets/index.html app/src/main/assets/app.css
-          ! grep -q 'id="v102-streak-layer-script"' app/src/main/assets/index.html app/src/main/assets/app.css
-          ! grep -q 'id="v102-streak-layer"' app/src/main/assets/index.html app/src/main/assets/app.css
+          grep -q 'qbank-question-ui-v2' build/app/index.html app/src/main/assets/app.css
+          grep -q 'qbank-practice-analysis-v1' build/app/index.html app/src/main/assets/app.css
+          grep -q 'qbank-ui-polish-v1' build/app/index.html app/src/main/assets/app.css
+          grep -q 'qbank-ui-polish-v2' build/app/index.html app/src/main/assets/app.css
+          grep -q 'qbank-home-insights-polish-v1' build/app/index.html app/src/main/assets/app.css
+          grep -q 'qbank-option-feedback-polish-v1' build/app/index.html app/src/main/assets/app.css
+          grep -q 'qbank-practice-cleanup-v1' build/app/index.html app/src/main/assets/app.css
+          grep -q 'qbank-option-hole-cleanup-v1' build/app/index.html app/src/main/assets/app.css
+          grep -q 'nk-home-v4' build/app/index.html app/src/main/assets/app.css
+          grep -q 'nk-home-v4-style' build/app/index.html app/src/main/assets/app.css
+          grep -q 'NK_HOME_V5_FIXES' build/app/index.html app/src/main/assets/app.css
+          grep -q 'nk-topics-v2' build/app/index.html app/src/main/assets/app.css
+          grep -q 'openSubjectTopics' build/app/index.html app/src/main/assets/app.css
+          grep -q 'resetScrollPosition' build/app/index.html app/src/main/assets/app.css
+          grep -q 'requestAnimationFrame(() => window.scrollTo(0,0)' build/app/index.html app/src/main/assets/app.css
+          grep -q 'nk-home-streak-header-v1' build/app/index.html app/src/main/assets/app.css
+          grep -q 'nk-home-streak' build/app/index.html app/src/main/assets/app.css
+          grep -q 'currentStreak()' build/app/index.html app/src/main/assets/app.css
+          grep -q 'body:has(.nk-home-v4) .topbar' build/app/index.html app/src/main/assets/app.css
+          grep -q 'nk-home-actions-v1' build/app/index.html app/src/main/assets/app.css
+          grep -q 'Continue Practice' build/app/index.html app/src/main/assets/app.css
+          grep -q 'Build a test' build/app/index.html app/src/main/assets/app.css
+          grep -q 'Quick test' build/app/index.html app/src/main/assets/app.css
+          ! grep -q 'id="v102-streak-layer-script"' build/app/index.html app/src/main/assets/app.css
+          ! grep -q 'id="v102-streak-layer"' build/app/index.html app/src/main/assets/app.css
           ! grep -q 'home_polish_v3.js' app/src/main/java/com/qbank/biochemistry/MainActivity.java
-          grep -q 'NK_SOURCE_VISUALS_V11' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'closeQuestionNavigator();' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'sessionShell' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'qb-nav-submit' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q "s.mode==='practice'" app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'nk-session-review' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'nk-cbt-review-footer-v1' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'review-fixed-actions' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'nk-review-solution-grid-style' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'nk-session-experience-v114' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'nk-whole-app-vision-v114' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'startAllSubjectPractice' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'openMultiSubjectTestBuilder' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'aria-label="NK QBank"' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'nk-flame-svg' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'nk-custom-study-modules-v1' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'openStudyModuleBuilder' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'nkSelectModuleQuestionIds' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q "route.page==='module-builder'" app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q '&scale=4' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'id="cr-grid"' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'window.QB.openQuestionNavigator()' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'showToast(msg,type' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'root.innerHTML=' app/src/main/assets/index.html app/src/main/assets/app.css
-          grep -q 'NK_MARROW_STRUCTURED_TABLE_RENDERER_V1' app/src/main/assets/index.html app/src/main/assets/app.css
+          grep -q 'NK_SOURCE_VISUALS_V11' build/app/index.html app/src/main/assets/app.css
+          grep -q 'closeQuestionNavigator();' build/app/index.html app/src/main/assets/app.css
+          grep -q 'sessionShell' build/app/index.html app/src/main/assets/app.css
+          grep -q 'qb-nav-submit' build/app/index.html app/src/main/assets/app.css
+          grep -q "s.mode==='practice'" build/app/index.html app/src/main/assets/app.css
+          grep -q 'nk-session-review' build/app/index.html app/src/main/assets/app.css
+          grep -q 'nk-cbt-review-footer-v1' build/app/index.html app/src/main/assets/app.css
+          grep -q 'review-fixed-actions' build/app/index.html app/src/main/assets/app.css
+          grep -q 'nk-review-solution-grid-style' build/app/index.html app/src/main/assets/app.css
+          grep -q 'nk-session-experience-v114' build/app/index.html app/src/main/assets/app.css
+          grep -q 'nk-whole-app-vision-v114' build/app/index.html app/src/main/assets/app.css
+          grep -q 'startAllSubjectPractice' build/app/index.html app/src/main/assets/app.css
+          grep -q 'openMultiSubjectTestBuilder' build/app/index.html app/src/main/assets/app.css
+          grep -q 'aria-label="NK QBank"' build/app/index.html app/src/main/assets/app.css
+          grep -q 'nk-flame-svg' build/app/index.html app/src/main/assets/app.css
+          grep -q 'nk-custom-study-modules-v1' build/app/index.html app/src/main/assets/app.css
+          grep -q 'openStudyModuleBuilder' build/app/index.html app/src/main/assets/app.css
+          grep -q 'nkSelectModuleQuestionIds' build/app/index.html app/src/main/assets/app.css
+          grep -q "route.page==='module-builder'" build/app/index.html app/src/main/assets/app.css
+          grep -q '&scale=4' build/app/index.html app/src/main/assets/app.css
+          grep -q 'id="cr-grid"' build/app/index.html app/src/main/assets/app.css
+          grep -q 'window.QB.openQuestionNavigator()' build/app/index.html app/src/main/assets/app.css
+          grep -q 'showToast(msg,type' build/app/index.html app/src/main/assets/app.css
+          grep -q 'root.innerHTML=' build/app/index.html app/src/main/assets/app.css
+          grep -q 'NK_MARROW_STRUCTURED_TABLE_RENDERER_V1' build/app/index.html app/src/main/assets/app.css
           test -s app/src/main/assets/biochemistry_source_solution_map.js
           test -s app/src/main/assets/subject_source_solution_maps.js
           test -s app/src/main/assets/source_visual_metadata.js
@@ -419,11 +421,11 @@
           test -f app/src/main/assets/Anatomy_QBank_Source.pdf
           test -s app/src/main/assets/vendor/ts-fsrs/ts-fsrs-5.4.2.umd.js
           test -s app/src/main/assets/vendor/ts-fsrs/LICENSE
-          grep -q 'NK_FSRS_V6_START' app/src/main/assets/index.html app/src/main/assets/app.css
+          grep -q 'NK_FSRS_V6_START' build/app/index.html app/src/main/assets/app.css
       - name: Test unreachable CSS pruning
         run: python3 tools/test_prune_unreachable_css.py
       - name: Build Cloudflare Pages PWA artifact
-        run: python3 tools/build_web_dist.py --version ${{ github.sha }}
+        run: python3 tools/build_web_dist.py --version ${{ github.sha }} --page build/app/index.html
       - name: Verify Marrow image bytes and offline cache
         run: python3 tools/check_marrow_image_package.py
       - name: Verify focused UWorld exhibit bytes and offline cache
```

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
- **Notes:** The finding is correct, and the patch was reworked twice during review before being applied.

The finding: `build_app_data.py` read and wrote the same path, and that path is the source page. `tools/app_page.py` and AGENTS.md both treat `app/src/main/assets/index.html` as source, and the repository memory records the overwrite as a local gotcha more than once, so the current shape is a trap rather than a design.

The patch as proposed could not have worked. Its first hunk called `parser.add_argument("--out", ...)` *after* `parser.parse_args()`, so argparse would have rejected `--out` as an unknown argument; its second hunk changed the write to `args.out.write_text(...)` while a third, contradictory hunk introduced an `--in-place` flag and wrote back to `HTML`; and the workflow hunks moved only two of the steps that read the page for generated content.

The applied fix:

- `tools/build_app_data.py` gains `--out`, defaulting to `build/app/index.html`. The argument is registered before `parse_args()`, and the tool never writes the source page again.
- `tools/build_web_dist.py` gains `--page`, defaulting to `build/app/index.html` when it exists and the source page otherwise. The source page is skipped when the assets are copied and the filled page is shipped instead, so the web build can no longer pick up the unfilled template.
- The pipeline writes the filled page and copies `app.css` beside it, checks the inline JavaScript of the filled page, verifies the generated contract against the filled page (`--html build/app/index.html`, which is where `marrow__ANAT_CH01_Q001` and the other data markers live), repoints all 56 greps of the "Verify final generated app" step at the filled page, and ships it to Pages.

`tools/test_build_app_data_out_v1.py` is new. It asserts that the tool never writes the source page and that running it leaves the source page byte for byte unchanged, drives the web builder against a fixture to show that it ships the filled page and not the template, and checks the pipeline's four repointed steps. Each assertion fails when its fix is reverted.

The full pipeline cannot be run here, so the change must be confirmed by a passing GitHub Actions run before it is called verified.
