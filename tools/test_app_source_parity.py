#!/usr/bin/env python3
"""The app page is source: check its modules and data tokens line up.

Each file in app/src/main/modules/ must sit in app/src/main/assets/index.html
exactly once, as a `/* @module <file> */` marker, and every marker must name a
module (tools/app_page.py). Data never lives in the page: it carries only the
__NK_DATA_*__ tokens tools/build_app_data.py fills at build time.
"""
from collections import Counter
import re
import subprocess
import sys

from app_page import HTML, MARKER, MODULES, ROOT, assemble


def main() -> None:
    page = HTML.read_text(encoding="utf-8")
    named = Counter(MARKER.findall(page))
    modules = sorted(p.name for p in MODULES.iterdir() if p.suffix in (".js", ".css"))
    unused = [name for name in modules if named[name] == 0]
    repeated = [name for name, count in named.items() if count > 1]
    if unused or repeated:
        raise SystemExit(f"each module belongs in index.html once: unused={unused} repeated={repeated}")
    assemble(page)
    if len(page.encode()) > 1024 * 1024:
        raise SystemExit("index.html must not embed question data or module code; use a token or a module")
    subprocess.run([sys.executable, str(ROOT / "tools/build_app_data.py"), "--check"], check=True)
    if re.search(r"window\.(?:SUBJECT_)?QBANK_DATA\s*=\s*\{", page):
        raise SystemExit("index.html embeds PrepLadder data; it belongs in the asset data scripts")
    print(f"APP_SOURCE_PARITY_OK modules={len(modules)} kb={len(page.encode()) / 1024:.0f}")


if __name__ == "__main__":
    main()
