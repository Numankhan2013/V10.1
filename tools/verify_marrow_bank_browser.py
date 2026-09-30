#!/usr/bin/env python3
"""Stable entrypoint for canonical Marrow browser regressions."""
from pathlib import Path
import subprocess
import sys

failed = []

for name in (
    "verify_marrow_bank_browser_v2.py",
    "verify_phys_final_images_browser.py",
    "verify_marrow_anatomy_ch06_q002_browser.py",
    "verify_marrow_anatomy_ch06_q018_browser.py",
    "verify_marrow_anatomy_ch07_q010_browser.py",
    "verify_marrow_anatomy_ch07_q019_browser.py",
    "verify_marrow_physio_ch11_q001_q006_browser.py",
):
    target = Path(__file__).with_name(name)
    result = subprocess.run([sys.executable, str(target)], cwd=target.parent.parent)
    if result.returncode:
        failed.append(name)
if failed:
    raise SystemExit('Marrow browser regressions failed: ' + ', '.join(failed))
