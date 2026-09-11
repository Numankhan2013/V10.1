#!/usr/bin/env python3
"""Fail closed if a canonical structured Marrow table is empty or object-stringified."""
from __future__ import annotations

import http.server
import socketserver
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "build" / "web"
OUT = ROOT / "build" / "marrow-ui-checks"
OUT.mkdir(parents=True, exist_ok=True)


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main() -> None:
    if not (WEB / "index.html").exists():
        raise SystemExit("build/web/index.html missing; run after PWA artifact generation")

    handler = lambda *a, **k: Quiet(*a, directory=str(WEB), **k)
    with socketserver.TCPServer(("127.0.0.1", 0), handler) as server:
        port = server.server_address[1]
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 390, "height": 844})
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(f"http://127.0.0.1:{port}/index.html", wait_until="networkidle")

            # Use the approved learner path, not module-scoped implementation state.
            anatomy = page.locator("button.nk-v3-subject-card").filter(has_text="Anatomy")
            if anatomy.count() != 1:
                raise SystemExit(f"Expected one Anatomy subject card, found {anatomy.count()}")
            anatomy.click()
            page.wait_for_function(
                "() => document.querySelectorAll('button.nk-bank-card').length===2",
                timeout=5000,
            )
            marrow = page.locator("button.nk-bank-card").filter(has_text="Marrow")
            if marrow.count() != 1:
                raise SystemExit("Anatomy Marrow bank card missing")
            marrow.click()
            page.wait_for_function(
                "() => document.querySelectorAll('button.nk-topic-row').length>0",
                timeout=5000,
            )

            topic = page.locator("button.nk-topic-row").filter(
                has_text="Pharyngeal arches, Skeletal & Muscular Systems"
            )
            if topic.count() != 1:
                raise SystemExit("Anatomy Chapter 5 topic row missing")
            topic.click()
            page.wait_for_function(
                "() => document.querySelectorAll('button.nk-library-row').length>=10",
                timeout=5000,
            )
            page.locator("button.nk-library-row").nth(9).click()
            page.wait_for_timeout(100)
            stem = page.locator(".question-text").inner_text().lower()
            if "raise the pitch" not in stem or "thyroidectomy" not in stem:
                raise SystemExit(f"Anatomy Ch5 Q10 did not open: {stem!r}")

            # Q10 answer A (4th arch) reveals the source structured table.
            page.locator(".option-list button").nth(0).click()
            page.wait_for_timeout(160)
            tables = page.locator(".nk-gold-explanation .nk-marrow-table")
            if tables.count() < 1:
                raise SystemExit("Anatomy Ch5 Q10 structured explanation table did not render")
            table_text = tables.first.inner_text()
            if "[object Object]" in table_text:
                raise SystemExit("Structured table leaked JavaScript object strings into learner UI")
            for expected in (
                "Pharyngeal Arch",
                "Muscle derivatives",
                "Muscles of mastication",
                "Larynx - cricothyroid",
                "All intrinsic muscles (except cricothyroid)",
            ):
                if expected not in table_text:
                    raise SystemExit(
                        f"Anatomy Ch5 Q10 rendered table missing {expected!r}: {table_text!r}"
                    )
            nonempty_lines = [line.strip() for line in table_text.splitlines() if line.strip()]
            if len(nonempty_lines) < 8:
                raise SystemExit(
                    f"Anatomy Ch5 Q10 table is visually under-populated: {nonempty_lines!r}"
                )

            page.screenshot(
                path=str(OUT / "02-anatomy-ch05-q10-structured-table.png"),
                full_page=True,
            )
            if errors:
                raise SystemExit("Browser JavaScript errors during table regression: " + " | ".join(errors))
            browser.close()
        server.shutdown()

    print("MARROW_STRUCTURED_TABLE_BROWSER_OK anatomy_ch05_q010 populated=true object_leak=false")


if __name__ == "__main__":
    main()
