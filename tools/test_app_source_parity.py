#!/usr/bin/env python3
"""The app page is source: keep it and the feature modules tested beside it in step.

Each tools/*_core.js and feature stylesheet is the tested copy of a block that
ships inside app/src/main/assets/index.html. Edit both together; this check fails
when one changes without the other. Data never lives in the page: it carries only
the __NK_DATA_*__ tokens tools/build_app_data.py fills at build time.
"""
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"
STYLES = ("app_clarity.css", "interaction_polish.css", "learning_insights.css",
          "refined_analysis.css", "uworld_biochemistry.css", "visual_refinement.css")


def main() -> None:
    page = HTML.read_text(encoding="utf-8")
    modules = sorted((ROOT / "tools").glob("*_core.js")) + [ROOT / "tools" / name for name in STYLES]
    drifted = [p.name for p in modules if page.count(p.read_text(encoding="utf-8").strip()) != 1]
    if drifted:
        raise SystemExit(f"index.html and these tested modules differ; edit both together: {drifted}")
    if len(page.encode()) > 3 * 1024 * 1024:
        raise SystemExit("index.html must not embed question data; use a __NK_DATA_*__ token")
    subprocess.run([sys.executable, str(ROOT / "tools/build_app_data.py"), "--check"], check=True)
    if re.search(r"window\.(?:SUBJECT_)?QBANK_DATA\s*=\s*\{", page):
        raise SystemExit("index.html embeds PrepLadder data; it belongs in the asset data scripts")
    print(f"APP_SOURCE_PARITY_OK modules={len(modules)} kb={len(page.encode()) / 1024:.0f}")


if __name__ == "__main__":
    main()
