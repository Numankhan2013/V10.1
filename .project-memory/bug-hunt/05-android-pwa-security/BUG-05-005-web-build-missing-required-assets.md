# BUG-05-005 — Web build succeeds while required generated assets are missing

- **Area:** 05 android-pwa-security
- **Severity:** medium
- **Confidence:** high
- **Status:** fix applied — commit pending (this commit)
- **Files:** `tools/build_web_dist.py:139-151`, `tools/build_web_dist.py:203-210`
- **Introduced by:** unknown

## What happens

`build_web_dist.py` copies whatever happens to be in `app/src/main/assets` and prints `WEB_DIST_OK` without checking that the files referenced by the shipped `index.html` actually made it into `build/web`. Two of those references — `biochemistry_source_solution_map.js` and `subject_source_solution_maps.js` — are produced by a separate generator (`tools/build_biochem_solution_map.py`). If that generator has not run, the build still succeeds, but the deployed page loads two 404 scripts and source-solution rendering is broken.

## Evidence

`app/src/main/assets/index.html:22-23`:

```html
<script src="biochemistry_source_solution_map.js"></script>
<script src="subject_source_solution_maps.js"></script>
```

Running the build in a tree where those generated files are absent still succeeds:

```text
$ python3 tools/build_web_dist.py --out /tmp/opencode/buildweb --version test
...
WEB_DIST_OK files=96 skipped_oversize=Anatomy_QBank_Source.pdf
```

Yet the outputs are missing:

```text
$ ls /tmp/opencode/buildweb/biochemistry_source_solution_map.js
ls: cannot access '/tmp/opencode/buildweb/biochemistry_source_solution_map.js': No such file or directory
```

The copy loop only skips files over the size limit and never asserts presence of referenced assets:

`tools/build_web_dist.py:139-151`:

```python
skipped = []
for source in ASSETS.rglob("*"):
    if not source.is_file():
        continue
    relative = source.relative_to(ASSETS)
    if source.stat().st_size > PAGES_FILE_LIMIT and source.name != "index.html":
        skipped.append(str(relative))
        continue
    target = out / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
```

## Learner impact

Broken secondary action on Android/PWA: source-solution views that depend on those maps fail to load in any deployment produced without the generator step. The build gives no signal that anything is wrong.

## Root cause

The packaging step treats missing generated assets as optional: it copies files if present and validates only the oversized-Anatomy-PDF case, never the set of scripts the page requires.

## Proposed fix

```diff
--- a/tools/build_web_dist.py
+++ b/tools/build_web_dist.py
@@ -202,6 +202,10 @@
     # as rules for legacy screens Geist replaced. The browser suite runs on this output.
     pruned = prune_build(out)
     print(f"UNREACHABLE_CSS_PRUNED rules={pruned.removed_rules} trimmed={pruned.trimmed_rules} kb={pruned.removed_bytes / 1024:.1f}")
+    required = ("biochemistry_source_solution_map.js", "subject_source_solution_maps.js")
+    missing = [name for name in required if not (out / name).is_file()]
+    if missing:
+        raise SystemExit(f"Required generated web assets are missing: {', '.join(missing)}")
     if "Anatomy_QBank_Source.pdf" not in skipped:
         raise SystemExit("Expected oversized Anatomy PDF to be excluded from Pages output")
     oversize = [p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file() and p.stat().st_size > PAGES_FILE_LIMIT]
```

## Verification

- Run `python3 tools/build_web_dist.py` after deleting the generated maps: it should now exit non-zero naming them.
- Run the normal pipeline (with `tools/build_biochem_solution_map.py` first): `WEB_DIST_OK` and both files present in `build/web`.
- Regressions to re-check: source-solution rendering, detail packs, service worker precache.

## Alternatives considered

Adding the two files to the service worker's required-precage list would surface the problem at install time, but it still would not fail the build; validating at build time is the smallest containment.

## Main-agent review

- **Verdict:** approved
- **Checked evidence:** yes
- **Checked patch:** yes
- **Notes:** Verified build_web_dist.py: the copy loop skips files over the size limit and the guard at the end only fails on files that landed in the output, so a required generated asset missing from the source tree passes silently. Medium/high is right: the build succeeds and ships an app that cannot load the data it needs. The fix asserts the required assets exist.


The finding is correct and the patch is right: the web build copied the assets and never checked that the two source-solution maps the page loads as scripts were actually in the output, so a missing generated file would ship a page whose script tags 404.

`tools/test_android_shell_contract_v1.py` is new and checks that the build fails when a required asset is missing. It fails on the pre-fix build with "the web build must fail when a required asset is missing".

The two required files are the generated ones the page loads as scripts (`tools/build_biochem_solution_map.py` and `tools/final_hardening.py`); the build pipeline runs both before `build_web_dist.py`, so the check holds in CI. `tools/test_crawler_exclusion.py` drives the builder against a fixture asset directory, and that fixture now carries the two files.
