#!/usr/bin/env python3
"""The filled app page must never overwrite the source page.

`app/src/main/assets/index.html` is the page's source: a template whose
`__NK_DATA_*__` tokens carry the generated question data. The tool that fills
those tokens used to write the result back over the source, so running the
build by hand quietly replaced the template with the built page.

The filled page now goes to `build/app/index.html` (or wherever `--out`
points), and the web build ships that file.
"""

from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PAGE = ROOT / "app/src/main/assets/index.html"


def load_builder():
    spec = importlib.util.spec_from_file_location("app_data_test", ROOT / "tools/build_app_data.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_web_builder():
    spec = importlib.util.spec_from_file_location("web_dist_page_test", ROOT / "tools/build_web_dist.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    builder = load_builder()

    # The tool must offer an output path and must not write the source page.
    source = (ROOT / "tools/build_app_data.py").read_text(encoding="utf-8")
    assert "--out" in source, "build_app_data.py must offer an output path"
    assert "HTML.write_text" not in source, "build_app_data.py must never write the source page"
    assert builder.BUILT == ROOT / "build/app/index.html", "the default output must be build/app/index.html"

    # Running the tool must leave the source page byte for byte as it was.
    before = digest(SOURCE_PAGE)
    with patch.object(sys, "argv", ["build_app_data.py", "--check"]), contextlib.redirect_stdout(io.StringIO()):
        builder.main()
    assert digest(SOURCE_PAGE) == before, "the source page must not change"

    # The web build must ship the filled page, not the source template.
    web = load_web_builder()
    with tempfile.TemporaryDirectory() as directory:
        base = Path(directory)
        assets = base / "assets"
        assets.mkdir()
        (assets / "index.html").write_text("<html><body>source template</body></html>")
        (assets / "sw.js").write_text("const BUILD_VERSION='dev';\nconst SHELL=['./index.html'];\n")
        # The build checks that the generated files the page loads are present.
        (assets / "biochemistry_source_solution_map.js").write_text("window.NK_BIOCHEM_SOURCE_SOLUTION_MAP={};\n")
        (assets / "subject_source_solution_maps.js").write_text("window.NK_SUBJECT_SOURCE_SOLUTION_MAPS={};\n")
        (assets / "qbank-config.js").write_text(
            "window.NK_QBANK_FIREBASE_CONFIG = " + json.dumps({"anatomyPdfUrl": ""}) + ";\n"
        )
        (assets / "Biochemistry_QBank_Source.pdf").write_bytes(b"fixture-pdf")
        with (assets / "Anatomy_QBank_Source.pdf").open("wb") as oversized:
            oversized.truncate(web.PAGES_FILE_LIMIT + 1)
        filled = base / "build" / "app" / "index.html"
        filled.parent.mkdir(parents=True)
        filled.write_text("<html><body>filled page with the question data</body></html>")
        out = base / "web"
        with patch.object(web, "ASSETS", assets), patch.object(
            sys, "argv", ["build_web_dist.py", "--out", str(out), "--page", str(filled)]
        ), contextlib.redirect_stdout(io.StringIO()):
            web.main()
        shipped = (out / "index.html").read_text(encoding="utf-8")
        assert "filled page with the question data" in shipped, (
            "the web build must ship the filled page, not the source template"
        )
        assert "source template" not in shipped, "the web build must not ship the source template"

        # Without --page the builder takes the filled page when it is there.
        out2 = base / "web2"
        with patch.object(web, "ASSETS", assets), patch.object(web, "BUILT_PAGE", filled), patch.object(
            sys, "argv", ["build_web_dist.py", "--out", str(out2)]
        ), contextlib.redirect_stdout(io.StringIO()):
            web.main()
        assert "filled page with the question data" in (out2 / "index.html").read_text(encoding="utf-8"), (
            "the web build must find the filled page on its own"
        )

    # The pipeline must write the filled page and check it, not the source.
    workflow = (ROOT / ".github/workflows/build-apk.yml").read_text(encoding="utf-8")
    assert "python3 tools/build_app_data.py --out build/app/index.html" in workflow, (
        "the pipeline must write the filled page to build/app/index.html"
    )
    assert "verify_product_contract.py --stage generated --html build/app/index.html" in workflow, (
        "the generated contract must check the filled page"
    )
    assert "build_web_dist.py --version ${{ github.sha }} --page build/app/index.html" in workflow, (
        "the web build must ship the filled page"
    )
    assert "Path('app/src/main/assets/index.html').read_text" not in workflow, (
        "the inline-JavaScript check must run on the filled page"
    )

    print("APP_DATA_OUT_OK source_page=untouched filled_page=build/app web_build=ships_filled")


if __name__ == "__main__":
    main()
