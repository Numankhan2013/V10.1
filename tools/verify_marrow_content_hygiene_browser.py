#!/usr/bin/env python3
"""Verify tuned Physiology learner surfaces contain no serialized data/code."""

from __future__ import annotations

import http.server
import json
import socketserver
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "build/web"
OUT = ROOT / "build/marrow-ui-checks"
OVERRIDES = ROOT / "data/marrow/content_hygiene_overrides_v1.json"
LEAK_MARKERS = (
    "[object Object]",
    '{"text"',
    '{"type"',
    '"content":',
    '"attrs":',
    '"marks":',
)


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


def main() -> None:
    if not (WEB / "index.html").exists():
        raise SystemExit("Generated PWA is missing; run the ordered build first")
    OUT.mkdir(parents=True, exist_ok=True)
    handler = lambda *args, **kwargs: Quiet(*args, directory=str(WEB), **kwargs)
    with socketserver.TCPServer(("127.0.0.1", 0), handler) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 390, "height": 844})
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(
                f"http://127.0.0.1:{server.server_address[1]}/index.html",
                wait_until="networkidle",
            )

            def open_practice_question(qid: str) -> None:
                page.evaluate("id => window.QB.practiceOne(id)", qid)
                replacement = page.locator("#nk-practice-replacement")
                if replacement.count() and replacement.is_visible():
                    replacement.get_by_role(
                        "button", name="Discard and start new", exact=True
                    ).click()

            expected_overrides = json.loads(OVERRIDES.read_text(encoding="utf-8"))["questions"]
            for qid, expected_content in expected_overrides.items():
                open_practice_question(qid)
                page.wait_for_function(
                    "() => Boolean(document.querySelector('.question-text'))",
                    timeout=5000,
                )
                rendered = {
                    "question": page.locator(".question-text").inner_text().strip(),
                    "options": [
                        value.strip()
                        for value in page.locator(".option-text").all_inner_texts()
                    ],
                }
                if rendered != expected_content:
                    raise SystemExit(
                        f"{qid} learner rendering differs from reviewed cleanup: {rendered!r}"
                    )

            def open_tuned_question(
                topic: str, question_index: int, option_index: int, expected: str
            ) -> None:
                page.evaluate("window.QB.nav('dashboard')")
                page.wait_for_timeout(80)
                page.locator("button.nk-v3-subject-card").filter(has_text="Physiology").click()
                page.wait_for_function(
                    "() => document.querySelectorAll('button.nk-bank-card').length===2",
                    timeout=5000,
                )
                page.locator("button.nk-bank-card").filter(has_text="Marrow").click()
                page.wait_for_function(
                    "() => document.querySelectorAll('button.nk-topic-row').length===43",
                    timeout=5000,
                )
                page.locator("button.nk-topic-row").filter(has_text=topic).first.click()
                page.locator("button.nk-library-row").nth(question_index).click()
                replacement = page.locator("#nk-practice-replacement")
                if replacement.count() and replacement.is_visible():
                    replacement.get_by_role(
                        "button", name="Discard and start new", exact=True
                    ).click()
                page.locator(".option-list button").nth(option_index).click()
                page.wait_for_function(
                    "() => Boolean(document.querySelector('.nk-study-support'))",
                    timeout=5000,
                )
                visible = "\n".join(
                    (
                        page.locator(".question-text").inner_text(),
                        page.locator(".option-list").inner_text(),
                        page.locator(".nk-study-support").inner_text(),
                    )
                )
                if expected not in visible:
                    raise SystemExit(f"{topic} tuned explanation is missing {expected!r}")
                for marker in LEAK_MARKERS:
                    if marker in visible:
                        raise SystemExit(
                            f"{topic} leaked serialized learner content {marker!r}: {visible[:800]!r}"
                        )
                if page.locator(".nk-gold-wrong-row").count() != 3:
                    raise SystemExit(f"{topic} tuned distractor surface is incomplete")

            open_tuned_question("Body Fluids", 0, 2, "60% of body weight")
            open_tuned_question(
                "Muscle Physiology I",
                0,
                1,
                "Sarcolemma is the muscle-cell membrane",
            )
            open_tuned_question(
                "Muscle Physiology I",
                1,
                2,
                "Tropomyosin lies along the groove",
            )
            open_tuned_question(
                "Muscle Physiology I",
                34,
                1,
                "source explanation explicitly identifies statement 3 as correct",
            )
            page.screenshot(
                path=str(OUT / "physiology-ch05-ch07-content-hygiene.png"),
                full_page=True,
            )
            if errors:
                raise SystemExit("Browser errors during content hygiene QA: " + " | ".join(errors))
            browser.close()
        server.shutdown()
    print(
        "MARROW_CONTENT_HYGIENE_BROWSER_OK "
        "physiology=Ch5_Q1-Q28,Ch7_Q1-Q35 "
        "rendered=Ch5_Q1,Ch7_Q1,Q2,Q35 fields=question,options,takeaway,explanation,rationales"
    )


if __name__ == "__main__":
    main()
