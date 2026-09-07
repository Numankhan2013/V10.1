#!/usr/bin/env python3
"""Route PDF generation away from local Android/Termux; fail closed in CI."""

import argparse
import importlib
import os
import sys


def is_termux(environ=None, platform=None, executable=None):
    env = os.environ if environ is None else environ
    platform = sys.platform if platform is None else platform
    executable = sys.executable if executable is None else executable
    return (platform == "android" or bool(env.get("TERMUX_VERSION"))
            or "com.termux/files/usr" in env.get("PREFIX", "")
            or "com.termux/files/usr" in executable
            or bool(env.get("ANDROID_ROOT") and env.get("ANDROID_DATA")))


def pdf_preflight(require=False):
    if is_termux():
        if require or os.environ.get("GITHUB_ACTIONS") == "true":
            raise SystemExit("PDF_PREFLIGHT_FAILED: full verification requires the Linux CI runner; Android/Termux cannot satisfy it.")
        print("SKIP_PDF_TERMUX: PyMuPDF-dependent generation and downstream generated-app checks are CI-only. Do not install or compile PyMuPDF locally. This is not full verification.")
        return False
    for name in ("fitz", "PIL.Image"):
        try:
            module = importlib.import_module(name)
            if name == "fitz" and not hasattr(module, "open"):
                raise ImportError("fitz is not PyMuPDF")
        except ImportError as error:
            raise SystemExit(f"PDF_PREFLIGHT_FAILED: {name} unavailable ({error}); full verification must run in GitHub Actions.") from error
    print("PDF_PREFLIGHT_OK: PyMuPDF and Pillow available")
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-pdf", action="store_true", help="Fail instead of skipping; required by the full CI workflow")
    args = parser.parse_args()
    pdf_preflight(require=args.require_pdf)


if __name__ == "__main__":
    main()
