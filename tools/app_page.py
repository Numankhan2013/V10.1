#!/usr/bin/env python3
"""Read the app page with its modules in place.

app/src/main/assets/index.html is the page's source. Each larger feature lives
in its own file under app/src/main/modules/ and sits in the page as a
`/* @module <file> */` marker; assemble() puts every module back where its
marker is. Tests read the page through app_page(), and build_app_data.py
writes the assembled page at build time. A page that is already assembled
has no markers, so reading it is unchanged.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"
MODULES = ROOT / "app/src/main/modules"
MARKER = re.compile(r"/\* @module ([a-z_]+\.(?:js|css)) \*/")


def assemble(page: str) -> str:
    def module(match: re.Match) -> str:
        path = MODULES / match.group(1)
        if not path.is_file():
            raise SystemExit(f"index.html names a module that does not exist: {match.group(1)}")
        return path.read_text(encoding="utf-8").strip()
    return MARKER.sub(module, page)


def app_page() -> str:
    return assemble(HTML.read_text(encoding="utf-8"))
