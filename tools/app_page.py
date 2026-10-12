#!/usr/bin/env python3
"""Read the app page with its modules in place, and its stylesheet.

app/src/main/assets/index.html is the page's source. Each larger feature lives
in its own file under app/src/main/modules/ and sits in the page as a
`/* @module <file> */` marker; assemble() puts every module back where its
marker is. Tests read the page through app_page(), and build_app_data.py
writes the assembled page at build time. A page that is already assembled
has no markers, so reading it is unchanged.

All of the page's CSS lives in one stylesheet, app/src/main/assets/app.css,
in cascade order; each former style block starts with a `/* ── <id> ── */`
header. app_source() is the page followed by the stylesheet, for tests that
check markup, scripts and styles together.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "app/src/main/assets/index.html"
MODULES = ROOT / "app/src/main/modules"
CSS = ROOT / "app/src/main/assets/app.css"
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


def app_css() -> str:
    return CSS.read_text(encoding="utf-8")


def app_source() -> str:
    return app_page() + "\n" + app_css()


def css_section(name: str) -> str:
    """The stylesheet text that came from one former <style id=...> block."""
    css = app_css()
    head = f"/* ── {name} ── */"
    if css.count(head) != 1:
        raise SystemExit(f"app.css has no single section {name}")
    start = css.index(head) + len(head)
    end = css.find("/* ── ", start)
    return css[start:end if end >= 0 else len(css)].strip()


def built_page(web: Path) -> str:
    """index.html of a built folder (build/web) with app.css inlined at its <link>.

    The result is a complete page, so verifiers can serve it or search it."""
    web = Path(web)
    page = (web / "index.html").read_text(encoding="utf-8")
    sheet = web / "app.css"
    link = '<link rel="stylesheet" href="app.css">'
    if sheet.is_file() and link in page:
        page = page.replace(link, "<style>\n" + sheet.read_text(encoding="utf-8") + "\n</style>", 1)
    return page
