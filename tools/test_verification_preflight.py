#!/usr/bin/env python3
"""Verify Termux skips without importing PDF dependencies; CI never skips."""

import contextlib
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch

from verification_preflight import is_termux, pdf_preflight


def main():
    assert is_termux({}, "android", "/usr/bin/python")
    assert is_termux({"TERMUX_VERSION": "0.118"}, "linux", "/usr/bin/python")
    assert is_termux({"PREFIX": "/data/data/com.termux/files/usr"}, "linux", "/usr/bin/python")
    assert is_termux({}, "linux", "/data/data/com.termux/files/usr/bin/python")
    assert not is_termux({}, "linux", "/usr/bin/python")
    with patch("verification_preflight.is_termux", return_value=True), patch("verification_preflight.importlib.import_module") as load:
        with patch.dict(os.environ, {"GITHUB_ACTIONS": "false"}), contextlib.redirect_stdout(io.StringIO()) as output:
            assert pdf_preflight() is False
            assert "SKIP_PDF_TERMUX" in output.getvalue()
        for required, ci in ((True, "false"), (False, "true")):
            with patch.dict(os.environ, {"GITHUB_ACTIONS": ci}):
                try:
                    pdf_preflight(require=required)
                except SystemExit as error:
                    assert "PDF_PREFLIGHT_FAILED" in str(error)
                else:
                    raise AssertionError("CI/full check must not silently skip")
        load.assert_not_called()
    with patch("verification_preflight.is_termux", return_value=False), patch("verification_preflight.importlib.import_module", side_effect=ImportError("missing")):
        try:
            pdf_preflight(require=True)
        except SystemExit as error:
            assert "PDF_PREFLIGHT_FAILED" in str(error)
        else:
            raise AssertionError("Missing Linux dependencies must fail")
    # Exercise real PDF entry points in an empty directory: skip must happen
    # before dependency imports, PDF reads, or writes, including on Linux CI.
    root = Path(__file__).resolve().parents[1]
    env = {**os.environ, "TERMUX_VERSION": "test", "GITHUB_ACTIONS": "false"}
    with tempfile.TemporaryDirectory() as directory:
        for name in ("build_biochem_solution_map.py", "build_source_visual_metadata.py", "final_hardening.py"):
            result = subprocess.run([sys.executable, str(root / "tools" / name)],
                                    cwd=directory, env=env, capture_output=True, text=True, check=True)
            assert "SKIP_PDF_TERMUX" in result.stdout, name
        assert not list(Path(directory).iterdir()), "Skipped generation must not write assets"
    print("VERIFICATION_PREFLIGHT_TEST_OK")


if __name__ == "__main__":
    main()
