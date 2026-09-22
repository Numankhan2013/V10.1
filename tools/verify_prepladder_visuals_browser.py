#!/usr/bin/env python3
"""Exercise risk-selected PrepLadder visuals at phone and tablet sizes."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
CATEGORIES = {
    "graph": "graph-plot-waveform",
    "table": "table-flowchart",
    "clinical": "diagnostic-medical-image",
    "diagram": "diagram-illustration",
    "multi-panel": "multi-panel-or-multiple-figures",
}


def choose_representatives(items):
    selected = {}
    for label, flag in CATEGORIES.items():
        match = next((item for item in items if flag in item.get("riskFlags", [])), None)
        if match is None:
            raise SystemExit(f"PrepLadder visual audit has no representative {label} candidate ({flag})")
        selected[label] = match
    return selected


def open_question(page, item):
    page.evaluate("([subject])=>window.QB.nav('banks',subject)", [item["subject"]])
    page.locator("button.nk-bank-card").filter(has_text="PrepLadder").click()
    page.evaluate("([id])=>window.QB.practiceOne(id)", [item["questionId"]])
    replacement = page.locator("#nk-practice-replacement")
    if replacement.count() and replacement.is_visible():
        replacement.get_by_role("button", name="Discard and start new", exact=True).click()
    page.locator(".nk-source-visual img").first.wait_for(state="visible")
    page.wait_for_function("document.querySelector('.nk-source-visual img')?.naturalWidth > 0")


def active_question_id(page):
    return page.evaluate(
        """()=>{
            const state=window.QB&&window.QB.getState?window.QB.getState():null;
            const session=state&&state.activeSession;
            return session&&Array.isArray(session.questionIds)
                ? session.questionIds[session.index]
                : null;
        }"""
    )


def exercise(page, item, label, viewport_name, output):
    open_question(page, item)
    visuals = page.locator(".nk-source-visual img")
    if label == "multi-panel":
        count = visuals.count()
        if count < 2:
            raise SystemExit(
                f"Multi-panel PrepLadder question mounted fewer than two visuals at {viewport_name}: {count}"
            )
        page.wait_for_function(
            "Array.from(document.querySelectorAll('.nk-source-visual img')).every(img=>img.naturalWidth>0)"
        )
    image = visuals.first
    geometry = image.evaluate("node=>({naturalWidth:node.naturalWidth,naturalHeight:node.naturalHeight,width:node.getBoundingClientRect().width,height:node.getBoundingClientRect().height,complete:node.complete})")
    if not geometry["complete"] or min(geometry["naturalWidth"], geometry["naturalHeight"]) < 40:
        raise SystemExit(f"{label} visual did not load at useful source dimensions: {geometry}")
    if max(geometry["width"], geometry["height"]) < 180:
        raise SystemExit(f"{label} visual is unreadably small at {viewport_name}: {geometry}")
    source_ratio = geometry["naturalWidth"] / geometry["naturalHeight"]
    display_ratio = geometry["width"] / geometry["height"]
    if abs(source_ratio / display_ratio - 1) > 0.02:
        raise SystemExit(f"{label} aspect ratio changed at {viewport_name}: {geometry}")
    owner_id = active_question_id(page)
    if owner_id != item["questionId"]:
        raise SystemExit(
            f"Stable PrepLadder owner mismatch: expected {item['questionId']}, got {owner_id!r}"
        )
    image.click()
    viewer = page.locator("#nk-source-viewer")
    viewer.wait_for(state="attached")
    backdrop = viewer.locator(".nk-sv-backdrop")
    backdrop.wait_for(state="visible")
    panel = viewer.locator(".nk-sv-panel")
    panel.wait_for(state="visible")
    viewer.locator(".nk-sv-img").wait_for(state="visible")
    page.wait_for_function("document.querySelector('#nk-source-viewer .nk-sv-img')?.naturalWidth > 0")
    surface = backdrop.evaluate("node=>({width:node.getBoundingClientRect().width,height:node.getBoundingClientRect().height})")
    viewport = page.viewport_size
    if not viewport or surface["width"] < viewport["width"] * 0.95 or surface["height"] < viewport["height"] * 0.95:
        raise SystemExit(f"Fullscreen backdrop does not cover viewport for {label} at {viewport_name}: {surface}")
    before = viewer.locator(".nk-sv-img").evaluate("node=>getComputedStyle(node).transform")
    viewer.locator('[data-z="+"]').click()
    after = viewer.locator(".nk-sv-img").evaluate("node=>getComputedStyle(node).transform")
    if before == after:
        raise SystemExit(f"Fullscreen zoom did not change transform for {label} at {viewport_name}")
    page.screenshot(path=str(output / f"{viewport_name}-{label}.png"), full_page=False)
    viewer.locator(".nk-sv-close").click()


def main():
    web = ROOT / "build/web"
    inventory = json.loads((web / "source_visual_inventory.json").read_text(encoding="utf-8"))
    items = inventory.get("items", [])
    representatives = choose_representatives(items)
    service_worker = (web / "sw.js").read_text(encoding="utf-8")
    missing_offline = [item["productionPath"] for item in items if "./" + item["productionPath"] not in service_worker]
    if missing_offline:
        raise SystemExit(f"PrepLadder visuals missing from offline service-worker shell: {missing_offline[:8]}")
    output = ROOT / "build/prepladder-visual-browser"
    output.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(web)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f"http://127.0.0.1:{server.server_port}"
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            for viewport_name, viewport in (("phone", {"width": 390, "height": 844}), ("tablet", {"width": 820, "height": 1180})):
                context = browser.new_context(viewport=viewport, service_workers="block", reduced_motion="reduce")
                page = context.new_page()
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(origin) else route.abort())
                page.goto(origin + "/#dashboard", wait_until="domcontentloaded")
                page.wait_for_function("window.QB && window.QB.getState")
                for label, item in representatives.items():
                    exercise(page, item, label, viewport_name, output)
                if errors:
                    raise SystemExit(f"PrepLadder visual browser errors at {viewport_name}: {' | '.join(errors)}")
                context.close()
            browser.close()
    finally:
        server.shutdown()
    print(f"PREPLADDER_VISUAL_BROWSER_OK categories={','.join(representatives)} viewports=phone,tablet fullscreen_zoom=true offline_shell={len(items)}")


if __name__ == "__main__":
    main()
