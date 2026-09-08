# Local development and verification

The local development environment is Android Termux. PyMuPDF cannot be built
reliably here, even with native CMake, SWIG, and Clang. Do not retry installing or
compiling it locally.

## Local checks

```sh
python3 tools/verify_local.py
```

This command does not generate or overwrite app assets. It discovers source-level
behavior tests, runs source/product, pipeline and memory contracts, compiles Python
without importing PDF dependencies, and checks JavaScript syntax. Failures are
collected and produce a nonzero exit status. Existing implementation and document
changes must remain intact.

The preflight can also be run on its own:

```sh
python3 tools/verification_preflight.py
```

On Android/Termux it prints `SKIP_PDF_TERMUX`, exits successfully, and does not
import, install, or compile PyMuPDF. The PDF entry points
`build_biochem_solution_map.py`, `build_source_visual_metadata.py`, and
`final_hardening.py` use the same guard before importing `fitz` or writing assets.
This skip means **not verified**, not passed. Do not manually continue a partial
PDF transformation chain and treat its output as a complete app.

## CI-only checks

The following need the artifacts of the ordered PDF/app pipeline; their Python
scripts may not import PyMuPDF themselves, but the required generation does:

- Question, session, and whole-app experience contracts.
- Source visual mappings and CBT invariants.
- Generated and packaged product contracts, final inline JavaScript validation,
  and APK/PWA artifact checks.

Running these against the ungenerated source checkout reports missing markers or
mapping files. The local runner labels them `CI_ONLY`. It does not weaken their
assertions or manufacture generated artifacts to make them pass.

`.github/workflows/build-apk.yml` runs on Ubuntu with Python 3.12, Node 20,
PyMuPDF and Pillow. After dependency installation it runs:

```sh
python3 tools/verification_preflight.py --require-pdf
```

This is a strict gate: missing dependencies or an Android runner fail the build.
The workflow then performs the existing PDF generation, lossless visual mapping,
ordered app transforms, generated contracts, JavaScript checks, Gradle APK build,
and packaged validation. The engineering gate tests the preflight policy too.

A successful local run is local verification only. Full verification requires the
full GitHub Actions workflow to pass on the candidate containing the changes.
An older green run does not verify uncommitted changes. Physical Android/PWA sync
acceptance additionally requires device testing.
