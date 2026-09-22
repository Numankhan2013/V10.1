#!/usr/bin/env python3
"""Stable-ID browser regression for Physiology Ch11 Q1-Q6 explanation rollout."""
from __future__ import annotations

import http.server
import socketserver
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "build" / "web"
OUT = ROOT / "build" / "marrow-ui-checks"
Q1 = "marrow__PHYS_CH11_Q001"
Q6 = "marrow__PHYS_CH11_Q006"


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def open_ch11(page):
    page.evaluate("window.QB.nkOpenSubjectLibrary('Physiology')")
    page.wait_for_function("() => document.querySelectorAll('button.nk-bank-card').length===2", timeout=5000)
    marrow = page.locator("button.nk-bank-card").filter(has_text="Marrow")
    if marrow.count() != 1:
        raise SystemExit("Physiology Marrow bank card missing")
    marrow.click(timeout=5000)
    page.wait_for_function("() => document.querySelectorAll('button.nk-topic-row').length===43", timeout=5000)
    topic = page.locator("button.nk-topic-row").filter(has_text="Sensory Receptors")
    if topic.count() != 1:
        raise SystemExit(f"Physiology Ch11 topic count={topic.count()}")
    topic.click()
    page.wait_for_function("() => document.querySelectorAll('button.nk-library-row').length===21", timeout=5000)


def check_question(page, index: int, stable_id: str, option_index: int, markers: tuple[str, ...], shot: str):
    page.locator("button.nk-library-row").nth(index).click()
    replacement = page.locator("#nk-practice-replacement")
    if replacement.count() and replacement.is_visible():
        replacement.get_by_role("button", name="Discard and start new", exact=True).click()
    page.wait_for_function("() => document.querySelectorAll('.option-list button').length===4", timeout=5000)
    page.locator(".option-list button").nth(option_index).click()
    page.wait_for_timeout(140)
    support = page.locator(".nk-study-support").inner_text().lower()
    for marker in markers:
        if marker.lower() not in support:
            raise SystemExit(f"{stable_id} learner explanation missing {marker!r}")
    if page.locator(".nk-gold-wrong-row").count() != 3:
        raise SystemExit(f"{stable_id} must render exactly three distractor rationales")
    if not page.locator(".nk-fsrs-rating").is_visible():
        raise SystemExit(f"{stable_id} lost the shared FSRS recall dock")
    page.screenshot(path=str(OUT / shot), full_page=True)


def main() -> None:
    index = WEB / "index.html"
    if not index.exists():
        raise SystemExit("Generated PWA is missing; build_web_dist must run first")
    generated = index.read_text(encoding="utf-8")
    for stable_id in (Q1, Q6):
        if stable_id not in generated:
            raise SystemExit(f"Stable ID {stable_id} missing from generated PWA")

    OUT.mkdir(parents=True, exist_ok=True)
    handler = lambda *a, **k: Quiet(*a, directory=str(WEB), **k)
    with socketserver.TCPServer(("127.0.0.1", 0), handler) as server:
        port = server.server_address[1]
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 390, "height": 844})
            errors: list[str] = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.goto(f"http://127.0.0.1:{port}/index.html", wait_until="networkidle")

            open_ch11(page)
            check_question(
                page, 0, Q1, 0,
                ("key takeaway", "receptive field", "spatial region", "motor unit", "dermatome", "sensory neuron"),
                "physiology-ch11-q001-stable-id.png",
            )

            open_ch11(page)
            check_question(
                page, 5, Q6, 0,
                ("key takeaway", "different axes", "mechanoreceptor", "exteroceptor", "best available option", "interoceptors", "photoreceptors", "telereceptors"),
                "physiology-ch11-q006-stable-id.png",
            )

            if errors:
                raise SystemExit(f"Browser errors while rendering Physiology Ch11 rollout: {errors}")
            browser.close()
        server.shutdown()

    print("MARROW_PHYSIO_CH11_Q001_Q006_BROWSER_OK stable_ids=2 rationales=3 reconstruction=resolved shared_fsrs=present")


if __name__ == "__main__":
    main()
