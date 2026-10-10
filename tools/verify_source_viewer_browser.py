#!/usr/bin/env python3
"""Source-PDF viewer in the Geist UI: opens at once, sharpens, pans to every edge without drifting."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
QUESTION_ID = "physiology-9-6"


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def frame_rect(page) -> list[float]:
    return page.evaluate("(()=>{const r=document.querySelector('#source-pdf-zoom .nkv-frame').getBoundingClientRect();return [r.left,r.right,r.top,r.bottom,r.width]})()")


def drag(page, x0: float, y0: float, dx: float, dy: float) -> None:
    page.mouse.move(x0, y0)
    page.mouse.down()
    for i in range(1, 31):
        page.mouse.move(x0 + dx * i / 30, y0 + dy * i / 30)
        page.wait_for_timeout(12)
    page.wait_for_timeout(150)  # stop before release: no glide
    page.mouse.up()
    page.wait_for_timeout(350)


def main() -> None:
    web = ROOT / "build/web"
    assert "redesign/nk-viewer.js" in (web / "index.html").read_text(encoding="utf-8")
    output = ROOT / "build/ui-checks"
    output.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Quiet, directory=str(web)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f"http://127.0.0.1:{server.server_port}"
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            for width, height in ((390, 844), (820, 1180)):
                context = browser.new_context(viewport={"width": width, "height": height}, service_workers="block")
                page = context.new_page()
                errors: list[str] = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(origin) else route.abort())
                page.goto(origin + "/?ui=geist#dashboard", wait_until="domcontentloaded")
                page.wait_for_function("window.QB && window.QB.getState && document.documentElement.dataset.nkUi==='geist'")
                page.locator("button.nk-v3-subject-card").filter(has_text="Physiology").click()
                page.locator("button.nk-bank-card").filter(has_text="PrepLadder").click()
                page.evaluate("id => window.QB.practiceOne(id)", QUESTION_ID)
                page.evaluate("window.QB.nav('practice')")
                page.locator(".option").first.click()
                page.evaluate("window.QB.submitPractice()")
                segment = page.locator(".nk-web-pdf-segment").first
                segment.scroll_into_view_if_needed()
                page.wait_for_function("document.querySelector('.nk-web-pdf-segment')?.dataset.rendered==='true'", timeout=60000)

                # The viewer must be on screen within two frames of the tap, before any sharper render.
                opened = page.evaluate("""async () => {
                  const node = document.querySelector('.nk-web-pdf-segment'), t = performance.now();
                  node.click();
                  await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
                  const v = document.querySelector('#source-pdf-zoom');
                  return { ms: performance.now() - t, open: Boolean(v && v.classList.contains('is-open')), quality: v && v.dataset.quality };
                }""")
                assert opened["open"] and opened["ms"] < 400, f"viewer must open at once: {opened}"
                page.wait_for_function("document.querySelector('#source-pdf-zoom')?.dataset.quality==='high'", timeout=60000)
                assert page.locator("#source-pdf-zoom .source-pdf-zoomimg").count() == 1
                assert page.locator("#spz-reset").inner_text() == "100%"

                stage = page.locator("#source-pdf-zoom .nkv-stage").bounding_box()
                cx, cy = stage["x"] + stage["width"] / 2, stage["y"] + stage["height"] / 2
                page.locator("#spz-plus").click()
                page.wait_for_timeout(400)
                page.locator("#spz-plus").click()
                page.wait_for_timeout(400)
                assert page.locator("#spz-reset").inner_text() == "225%"
                drag(page, cx, cy, -width * 3, 0)
                left, right, top, bottom, w = frame_rect(page)
                assert abs(right - stage["width"]) < 1.5, f"must reach the right edge exactly: {right}"
                drag(page, cx, cy, width * 3, 0)
                left, right, top, bottom, w = frame_rect(page)
                assert abs(left) < 1.5, f"must reach the left edge exactly: {left}"
                if bottom - top > stage["height"]:
                    drag(page, cx, cy, 0, -height * 3)
                    assert abs(frame_rect(page)[3] - stage["height"]) < 1.5, "must reach the bottom edge"
                else:
                    assert abs((top + bottom) / 2 - cy) < 1.5, "a crop shorter than the screen stays centred"
                page.screenshot(path=str(output / f"source-viewer-{width}.png"))

                page.keyboard.press("0")
                page.wait_for_timeout(400)
                assert page.locator("#spz-reset").inner_text() == "100%"
                page.keyboard.press("Escape")
                page.locator("#source-pdf-zoom").wait_for(state="detached")
                assert page.evaluate("document.documentElement.style.overflow") in ("", "visible"), "page scroll must be restored"

                # Reopening reuses the cached sharp render.
                segment.click()
                page.wait_for_function("document.querySelector('#source-pdf-zoom')?.dataset.quality==='high'", timeout=5000)
                page.keyboard.press("Escape")
                page.locator("#source-pdf-zoom").wait_for(state="detached")
                assert not errors, f"Browser errors: {errors!r}"
                context.close()
            browser.close()
        print("SOURCE_VIEWER_BROWSER_OK instant_open=true sharpen=true edges=true reopen_cached=true")
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
