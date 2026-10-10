#!/usr/bin/env python3
"""Exercise image and PDF-page notes in the generated PWA, then sync them between two devices.

Firestore is replaced by an in-memory REST double so upload, download and deletion of
note images can be checked without a real account.
"""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse
import base64
import json
import tempfile
import threading
import time

import fitz
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
QUESTION_ID = "physiology-9-6"
FIRESTORE = "https://firestore.googleapis.com/v1/projects/demo/databases/(default)/documents/"


def make_fixtures(folder: Path) -> tuple[Path, Path]:
    screenshot = folder / "goodnotes-export.png"
    image = Image.new("RGB", (1640, 2360), "white")
    draw = ImageDraw.Draw(image)
    for row in range(40):
        draw.text((60, 60 + row * 55), f"small handwriting line {row} - cardiac output = SV x HR", fill=(20, 30, 90))
    image.save(screenshot)
    pdf = folder / "reference.pdf"
    doc = fitz.open()
    for number in range(1, 4):
        page = doc.new_page(width=595, height=842)
        page.insert_text((40, 60), f"Reference page {number}", fontsize=20)
        for row in range(60):
            page.insert_text((40, 90 + row * 12), f"tiny note {number}.{row}: preload, afterload, contractility", fontsize=6)
    doc.save(pdf)
    return screenshot, pdf


class FakeFirestore:
    """Implements the REST calls QBank sync uses: runQuery, document GET and PATCH."""

    def __init__(self) -> None:
        self.docs: dict[str, dict] = {}
        self.lock = threading.Lock()

    def handle(self, route) -> None:
        request = route.request
        parsed = urlparse(request.url)
        path = unquote(parsed.path.split("/documents/", 1)[1]) if "/documents/" in parsed.path else ""
        with self.lock:
            if request.method == "POST" and path.endswith(":runQuery"):
                parent = path[: -len(":runQuery")]
                collection = json.loads(request.post_data or "{}")["structuredQuery"]["from"][0]["collectionId"]
                prefix = f"{parent}/{collection}/"
                rows = [{"document": doc} for name, doc in sorted(self.docs.items()) if name.startswith(prefix) and "/" not in name[len(prefix):]]
                route.fulfill(status=200, content_type="application/json", body=json.dumps(rows))
                return
            if request.method == "PATCH":
                exists = parse_qs(parsed.query).get("currentDocument.exists", [""])[0] == "true"
                if exists and path not in self.docs:
                    route.fulfill(status=404, content_type="application/json", body=json.dumps({"error": {"status": "NOT_FOUND", "message": "missing"}}))
                    return
                body = json.loads(request.post_data or "{}")
                doc = {"name": f"projects/demo/databases/(default)/documents/{path}", "fields": body.get("fields", {})}
                self.docs[path] = doc
                route.fulfill(status=200, content_type="application/json", body=json.dumps(doc))
                return
            if request.method == "GET" and path in self.docs:
                route.fulfill(status=200, content_type="application/json", body=json.dumps(self.docs[path]))
                return
        route.fulfill(status=404, content_type="application/json", body=json.dumps({"error": {"status": "NOT_FOUND", "message": "missing"}}))

    def kind(self, collection: str) -> dict[str, dict]:
        with self.lock:
            return {name: doc for name, doc in self.docs.items() if f"/{collection}/" in name}


def fake_token() -> str:
    claims = base64.urlsafe_b64encode(json.dumps({"aud": "demo"}).encode()).decode().rstrip("=")
    return f"header.{claims}.signature"


def open_question(page) -> None:
    page.locator("button.nk-v3-subject-card").filter(has_text="Physiology").click()
    page.locator("button.nk-bank-card").filter(has_text="PrepLadder").click()
    page.evaluate("id => window.QB.practiceOne(id)", QUESTION_ID)
    page.wait_for_function("id => window.QB.getState().activeSession?.questionIds?.[0]===id", arg=QUESTION_ID)
    page.evaluate("window.QB.nav('practice')")
    page.locator(".option").first.click()
    page.evaluate("window.QB.submitPractice()")
    page.locator(".nk-question-note").wait_for(state="visible")


def idb_metas(page) -> list:
    return page.evaluate("""() => new Promise((resolve, reject) => {
      const open = indexedDB.open('qbank_note_media_v1');
      open.onsuccess = () => { const tx = open.result.transaction('meta', 'readonly'); const all = tx.objectStore('meta').getAll();
        all.onsuccess = () => { resolve(all.result); open.result.close(); }; all.onerror = () => reject(all.error); };
      open.onerror = () => reject(open.error);
    })""")


def loaded(page, selector: str, count: int) -> None:
    page.wait_for_function(
        "([selector, count]) => { const imgs=[...document.querySelectorAll(selector)]; return imgs.length===count && imgs.every(img => (img.getAttribute('src')||'').startsWith('blob:') && img.complete && img.naturalWidth > 0); }",
        arg=[selector, count], timeout=20000)


def local_flow(browser, origin: str, screenshot: Path, pdf: Path, output: Path, width: int, height: int) -> None:
    context = browser.new_context(viewport={"width": width, "height": height}, service_workers="block", has_touch=True)
    page = context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("dialog", lambda dialog: dialog.accept())
    page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(origin) else route.abort())
    page.goto(origin + "/#dashboard", wait_until="domcontentloaded")
    page.wait_for_function("window.QB && window.QB.getState")
    open_question(page)
    note = page.locator(".nk-question-note")
    note.get_by_role("button", name="Add note").click()
    note.locator("textarea").fill("Starling curve: look at the shaded zone.")

    note.locator(".nk-note-file-image").set_input_files(str(screenshot))
    page.wait_for_function("document.querySelectorAll('.nk-note-part.is-media').length===1", timeout=20000)
    assert note.locator("textarea").input_value() == "Starling curve: look at the shaded zone.", "importing must keep typed text"

    note.locator(".nk-note-file-pdf").set_input_files(str(pdf))
    sheet = page.locator(".nk-note-sheet")
    sheet.wait_for(state="visible", timeout=20000)
    assert sheet.locator(".nk-note-pdf-page").count() == 3
    page.wait_for_function("document.querySelectorAll('.nk-note-pdf-canvas').length>=1", timeout=20000)
    sheet.get_by_role("button", name="Page 1", exact=True).click()
    sheet.get_by_role("button", name="Page 3", exact=True).click()
    assert sheet.locator(".nk-note-sheet-add").inner_text() == "Add 2 pages"
    page.screenshot(path=str(output / f"note-media-pdf-picker-{width}.png"))
    sheet.locator(".nk-note-sheet-add").click()
    page.wait_for_function("document.querySelectorAll('.nk-note-part.is-media').length===3", timeout=30000)
    labels = note.locator(".nk-note-part-label").all_inner_texts()
    assert labels == ["goodnotes-export", "reference · page 1", "reference · page 3"], labels

    # Move page 3 above page 1; the order is the order the learner reads.
    note.locator('[data-note-act="up"][data-i="3"]').click()
    assert note.locator(".nk-note-part-label").all_inner_texts()[1:] == ["reference · page 3", "reference · page 1"]
    page.screenshot(path=str(output / f"note-media-editor-{width}.png"), full_page=True)
    note.get_by_role("button", name="Save note").click()
    figures = note.locator(".nk-note-figure")
    figures.first.wait_for(state="visible")
    assert figures.count() == 3
    loaded(page, ".nk-question-note .nk-note-figure img", 3)
    assert note.locator(".nk-note-readonly").inner_text() == "Starling curve: look at the shaded zone."

    blocks = page.evaluate("id => window.QB.getState().questionNotes[id].blocks", QUESTION_ID)
    assert [b["type"] for b in blocks] == ["text", "image", "image", "image"], blocks
    assert blocks[2]["source"] == "pdf" and blocks[2]["label"] == "reference · page 3"
    stored = page.evaluate("() => Object.keys(localStorage).reduce((n,k)=>n+(localStorage.getItem(k)||'').length,0)")
    assert stored < 2_000_000 and "base64" not in page.evaluate("() => localStorage.getItem('qbank_state_v1')||''"), "image bytes must stay out of localStorage"
    metas = {m["id"]: m for m in idb_metas(page)}
    pdf_meta = metas[blocks[2]["asset"]["id"]]
    assert max(pdf_meta["w"], pdf_meta["h"]) >= 3000, f"PDF pages need high resolution for small handwriting: {pdf_meta}"
    png_meta = metas[blocks[1]["asset"]["id"]]
    assert (png_meta["w"], png_meta["h"], png_meta["mime"]) == (1640, 2360, "image/png"), f"an export that fits must keep its original pixels: {png_meta}"
    assert all(not m.get("draft") for m in metas.values() if m["id"] in {b["asset"]["id"] for b in blocks[1:]}), "saved images are no longer drafts"

    figures.nth(1).locator("button").click()
    viewer = page.locator(".nk-note-viewer")
    viewer.wait_for(state="visible")
    loaded(page, ".nk-note-viewer img", 1)
    viewer.get_by_role("button", name="Zoom in").click()
    assert "scale(1.6)" in viewer.locator("img").get_attribute("style")
    viewer.get_by_role("button", name="Next image").click()
    assert viewer.locator(".nk-note-viewer-count").inner_text() == "3 / 3"
    page.screenshot(path=str(output / f"note-media-viewer-{width}.png"))
    page.keyboard.press("Escape")
    assert viewer.count() == 0

    page.reload(wait_until="domcontentloaded")
    page.wait_for_function("window.QB && window.QB.getState")
    note.wait_for(state="visible")
    loaded(page, ".nk-question-note .nk-note-figure img", 3)
    page.screenshot(path=str(output / f"note-media-readonly-{width}.png"), full_page=True)

    page.evaluate("window.QB.nav('notes')")
    page.locator(".nk-notes-item").wait_for(state="visible")
    loaded(page, ".nk-notes-item-media img", 3)
    assert page.locator(".nk-notes-item-text").inner_text() == "Starling curve: look at the shaded zone."
    assert page.locator(".nk-notes-item button").count() == 1, "thumbnails must not add extra actions"
    page.screenshot(path=str(output / f"note-media-index-{width}.png"), full_page=True)
    page.locator(".nk-notes-item button").click()
    page.wait_for_function("location.hash==='#practice'")
    page.locator(".option").first.click()
    page.evaluate("window.QB.submitPractice()")
    note.wait_for(state="visible")

    removed = blocks[3]["asset"]["id"]
    note.get_by_role("button", name="Edit note").click()
    note.locator('[data-note-act="remove"][data-i="3"]').click()
    note.get_by_role("button", name="Save note").click()
    page.wait_for_function("([id, removed]) => !window.QB.getState().questionNotes[id].blocks.some(b => b.asset?.id === removed)", arg=[QUESTION_ID, removed])
    deadline = time.time() + 10
    while removed in {m["id"] for m in idb_metas(page)} and time.time() < deadline:
        time.sleep(0.2)
    assert removed not in {m["id"] for m in idb_metas(page)}, "a removed image must leave device storage"

    note.get_by_role("button", name="Delete note").click()
    assert page.evaluate("id => window.QB.getState().questionNotes[id].deleted", QUESTION_ID)
    deadline = time.time() + 10
    while idb_metas(page) and time.time() < deadline:
        time.sleep(0.2)
    assert not idb_metas(page), "deleting a signed-out note must remove its images"
    assert not errors, f"Browser errors: {errors!r}"
    context.close()


def sync_flow(browser, origin: str, screenshot: Path, output: Path) -> None:
    store = FakeFirestore()
    auth = json.dumps({"uid": "learner", "email": "learner@example.com", "idToken": fake_token(), "refreshToken": "refresh", "expiresAt": int(time.time() * 1000) + 3_600_000})
    config = "window.NK_QBANK_FIREBASE_CONFIG={apiKey:'test-key',projectId:'demo',anatomyPdfUrl:''};"

    def device():
        context = browser.new_context(viewport={"width": 820, "height": 1180}, service_workers="block")
        context.add_init_script(f"if(!localStorage.getItem('qbank_firebase_auth_v1'))localStorage.setItem('qbank_firebase_auth_v1',{json.dumps(auth)});")
        page = context.new_page()
        errors: list[str] = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("dialog", lambda dialog: dialog.accept())
        page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(origin) else route.abort())
        page.route("**/qbank-config.js", lambda route: route.fulfill(status=200, content_type="application/javascript", body=config))
        page.route("https://firestore.googleapis.com/**", store.handle)
        page.goto(origin + "/#dashboard", wait_until="domcontentloaded")
        page.wait_for_function("window.QB && window.QB.getState")
        return context, page, errors

    ipad, page_a, errors_a = device()
    open_question(page_a)
    note = page_a.locator(".nk-question-note")
    note.get_by_role("button", name="Add note").click()
    note.locator("textarea").fill("Synced cue")
    note.locator(".nk-note-file-image").set_input_files(str(screenshot))
    page_a.wait_for_function("document.querySelectorAll('.nk-note-part.is-media').length===1", timeout=20000)
    note.get_by_role("button", name="Save note").click()
    asset = page_a.evaluate("id => window.QB.getState().questionNotes[id].blocks[1].asset", QUESTION_ID)
    deadline = time.time() + 30
    while time.time() < deadline and not (store.kind("noteAssets") and store.kind("noteBlocks")):
        time.sleep(0.25)
    chunks = store.kind("noteAssets")
    assert chunks and store.kind("noteBlocks"), "note parts and image chunks must upload"
    assert all(len(doc["fields"]["payload"]["stringValue"]) <= 900000 for doc in chunks.values()), "chunks must fit the Firestore rule"
    assert all(asset["id"] in name for name in chunks), chunks.keys()
    assert not any("base64" in doc["fields"]["payload"]["stringValue"][:200] for doc in store.kind("notes").values())
    assert not errors_a, errors_a

    android, page_b, errors_b = device()
    page_b.wait_for_function("id => window.QB.getState().questionNotes?.[id]?.blocks?.length===2", arg=QUESTION_ID, timeout=30000)
    page_b.evaluate("window.QB.nav('notes')")
    page_b.locator(".nk-notes-item").wait_for(state="visible")
    loaded(page_b, ".nk-notes-item-media img", 1)
    metas = idb_metas(page_b)
    assert any(m["id"] == asset["id"] and m["bytes"] == asset["bytes"] for m in metas), "the second device must hold the exact image bytes"
    page_b.screenshot(path=str(output / "note-media-synced-device.png"), full_page=True)

    page_b.locator(".nk-notes-item button").click()
    page_b.wait_for_function("location.hash==='#practice'")
    page_b.locator(".option").first.click()
    page_b.evaluate("window.QB.submitPractice()")
    note_b = page_b.locator(".nk-question-note")
    note_b.get_by_role("button", name="Edit note").click()
    note_b.locator('[data-note-act="remove"][data-i="1"]').click()
    note_b.get_by_role("button", name="Save note").click()
    deadline = time.time() + 30
    while time.time() < deadline and not all(doc["fields"]["deleted"]["booleanValue"] for doc in store.kind("noteAssets").values()):
        time.sleep(0.25)
    assert all(doc["fields"]["deleted"]["booleanValue"] and not doc["fields"]["payload"]["stringValue"] for doc in store.kind("noteAssets").values()), "removing an image must clear its cloud copy"

    page_a.reload(wait_until="domcontentloaded")
    page_a.wait_for_function("id => window.QB.getState().questionNotes?.[id]?.blocks?.length===1", arg=QUESTION_ID, timeout=30000)
    assert not errors_b, errors_b
    ipad.close()
    android.close()


def main() -> None:
    web = ROOT / "build/web"
    html = (web / "index.html").read_text(encoding="utf-8")
    assert "NK_NOTE_MEDIA_V1_START" in html
    output = ROOT / "build/ui-checks"
    output.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(web)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f"http://127.0.0.1:{server.server_port}"
    try:
        with tempfile.TemporaryDirectory() as folder, sync_playwright() as playwright:
            screenshot, pdf = make_fixtures(Path(folder))
            browser = playwright.chromium.launch()
            for width, height in ((390, 844), (820, 1180)):
                local_flow(browser, origin, screenshot, pdf, output, width, height)
            sync_flow(browser, origin, screenshot, output)
            browser.close()
        print("QUESTION_NOTE_MEDIA_BROWSER_OK image=true pdf_pages=true viewer=true reload=true index=true sync=true deletion=true")
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
