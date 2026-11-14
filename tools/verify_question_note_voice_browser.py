#!/usr/bin/env python3
"""Record, play, rename, import, reorder and delete voice clips in My notes, then sync them.

Chromium's fake microphone (--use-fake-device-for-media-stream) feeds the real
MediaRecorder, so recording runs end to end. Firestore is the in-memory REST double
from verify_question_note_media_browser.py. A note edited by an older app version
(which drops block types it does not know) must keep its voice clips.

Pass --origin to run against an already served build instead of build/web.
"""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
import json
import math
import struct
import tempfile
import threading
import time
import wave

from playwright.sync_api import sync_playwright
from app_page import built_page
from verify_question_note_media_browser import (
    QUESTION_ID, FakeFirestore, add_from_menu, block_menu, fake_token, open_notes, open_question, wait_until,
)


ROOT = Path(__file__).resolve().parents[1]
FAKE_MIC = ["--use-fake-device-for-media-stream", "--use-fake-ui-for-media-stream", "--autoplay-policy=no-user-gesture-required"]


def make_wav(folder: Path, seconds: float = 1.0) -> Path:
    path = folder / "murmur-tip.wav"
    rate = 8000
    with wave.open(str(path), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(rate)
        out.writeframes(b"".join(struct.pack("<h", int(9000 * math.sin(2 * math.pi * 440 * n / rate))) for n in range(int(rate * seconds))))
    return path


def note_blocks(page) -> list:
    return page.evaluate("id => window.QB.getState().questionNotes[id]?.blocks || []", QUESTION_ID)


IDB_OPEN = """new Promise((resolve, reject) => {
      // Open exactly as the app does, so a check before the app's first open cannot leave a store-less database.
      const open = indexedDB.open('qbank_note_media_v1', 1);
      open.onupgradeneeded = () => ['meta', 'full', 'preview', 'thumb'].forEach(name => { if (!open.result.objectStoreNames.contains(name)) open.result.createObjectStore(name, {keyPath: 'id'}); });
      open.onsuccess = () => resolve(open.result); open.onerror = () => reject(open.error); open.onblocked = () => reject(new Error('blocked'));
    })"""


def idb_store(page, store: str) -> list:
    return page.evaluate("store => " + IDB_OPEN + ".then(db => new Promise((resolve, reject) => { const all = db.transaction(store, 'readonly').objectStore(store).getAllKeys(); all.onsuccess = () => { resolve(all.result); db.close(); }; all.onerror = () => reject(all.error); }))", store)


def idb_metas(page) -> list:
    return page.evaluate("() => " + IDB_OPEN + ".then(db => new Promise((resolve, reject) => { const all = db.transaction('meta', 'readonly').objectStore('meta').getAll(); all.onsuccess = () => { resolve(all.result); db.close(); }; all.onerror = () => reject(all.error); }))")


def players_ready(page, count: int) -> None:
    page.wait_for_function(
        "count => { const p=[...document.querySelectorAll('.nk-note-page .nk-nv-player')]; return p.length===count && p.every(x => x.classList.contains('is-ready') && (x.querySelector('audio')?.getAttribute('src')||'').startsWith('blob:')); }",
        arg=count, timeout=20000)


def add_voice(page, sheet) -> None:
    # Geist fans the add menu out with a spring; tap Voice once it has settled.
    if sheet.locator(".nk-np-add-menu").is_hidden():
        sheet.locator(".nk-np-add-btn").click()
        page.wait_for_timeout(700)
    add_from_menu(sheet, "Voice")


def open_recorder(page, sheet, where: str) -> None:
    # The add menu fans out with a spring; under a loaded runner a tap can land mid-morph
    # and miss Voice (as block_menu notes), so retry until the recorder opens. If it never
    # does, report what the page looked like so a real failure is not hidden.
    for _ in range(3):
        add_voice(page, sheet)
        try:
            sheet.locator(".nk-nb.is-recorder").wait_for(state="visible", timeout=5000)
            return
        except Exception:
            page.wait_for_timeout(400)
    raise SystemExit(where + ": the recorder never opened: " + json.dumps(page.evaluate(
        "() => ({hash: location.hash, guard: history.state && history.state.nkSessionGuard || null,"
        " session: window.QB.getState().activeSession && window.QB.getState().activeSession.mode || null,"
        " sheet: document.querySelectorAll('.nk-note-page').length,"
        " menu: !!document.querySelector('.nk-np-add-menu:not([hidden])'),"
        " blocks: [...document.querySelectorAll('.nk-note-page .nk-nb')].map(b => b.className)})")))


def record_clip(page, sheet, seconds: float, pause: bool = False) -> None:
    open_recorder(page, sheet, "record clip")
    recorder = sheet.locator(".nk-nb.is-recorder")
    recorder.get_by_role("button", name="Record", exact=True).click()
    sheet.locator(".nk-nr-stop:not([disabled])").wait_for(state="visible", timeout=10000)
    page.wait_for_function("() => /^0:0[1-9]/.test(document.querySelector('.nk-nr-time')?.textContent||'')", timeout=10000)
    if pause:
        # Pause holds the clock; Resume continues the same clip.
        sheet.get_by_role("button", name="Pause", exact=True).click()
        sheet.locator(".nk-nb.is-recorder.is-paused").wait_for(state="visible", timeout=5000)
        held = sheet.locator(".nk-nr-time").inner_text()
        page.wait_for_timeout(2200)
        assert sheet.locator(".nk-nr-time").inner_text() == held, "the clock holds while paused"
        assert [b.inner_text() for b in sheet.locator(".nk-nr-actions button").all()] == ["Discard", "Resume", "Stop and save"]
        sheet.get_by_role("button", name="Resume", exact=True).click()
        sheet.locator(".nk-nb.is-recorder.is-recording").wait_for(state="visible", timeout=5000)
    page.wait_for_timeout(int(seconds * 1000))
    sheet.get_by_role("button", name="Stop and save").click()
    sheet.locator(".nk-nb.is-recorder").wait_for(state="detached", timeout=15000)


def local_flow(browser, origin: str, wav: Path, output: Path, width: int, height: int) -> None:
    context = browser.new_context(viewport={"width": width, "height": height}, service_workers="block", has_touch=True, permissions=["microphone"])
    page = context.new_page()
    errors: list[str] = []
    prompts: list[str] = []
    page.on("pageerror", lambda error: errors.append(str(error)))

    def on_dialog(dialog):
        if dialog.type == "prompt":
            prompts.append(dialog.message)
            dialog.accept("Murmur at the apex")
        else:
            dialog.accept()
    page.on("dialog", on_dialog)
    page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(origin) else route.abort())
    page.goto(origin + "/#dashboard", wait_until="domcontentloaded")
    page.wait_for_function("window.QB && window.QB.getState")
    open_question(page)
    sheet = open_notes(page)
    menu = sheet.locator(".nk-np-add-menu")
    assert menu.get_by_role("menuitem", name="Voice", exact=True).count() == 1, "the add menu offers Voice"
    assert page.evaluate("() => [...document.querySelectorAll('.nk-np-add-menu [data-act]')].map(b => b.dataset.act)") == ["add-text", "add-image", "add-pdf", "add-voice"], "Voice sits after PDF pages"

    record_clip(page, sheet, 1.6, pause=True)
    page.wait_for_function("document.querySelectorAll('.nk-nb.is-audio').length===1", timeout=15000)
    blocks = note_blocks(page)
    assert [b["type"] for b in blocks] == ["audio"], blocks
    clip = blocks[0]
    assert clip["durationMs"] < 6000, "paused time is not counted: %s" % clip
    assert clip["durationMs"] >= 1500 and clip["mime"].startswith("audio/") and clip["bytes"] > 0, clip
    metas = {m["id"]: m for m in idb_metas(page)}
    meta = metas[clip["assetId"]]
    assert meta["kind"] == "audio" and meta["bytes"] == clip["bytes"] and not meta.get("draft"), meta
    assert clip["assetId"] in idb_store(page, "full")
    assert clip["assetId"] not in idb_store(page, "preview") + idb_store(page, "thumb"), "voice clips keep only meta + full"
    assert page.evaluate("id => !/data:|base64|blob:/.test(JSON.stringify(window.QB.getState().questionNotes[id]))", QUESTION_ID), "audio bytes must stay out of the saved state"
    assert "base64" not in page.evaluate("() => Object.values(localStorage).join('')"), "audio bytes must stay out of localStorage"

    # The compact player: play/pause, scrub, duration.
    players_ready(page, 1)
    player = sheet.locator(".nk-nv-player").first
    assert player.locator(".nk-nv-scrub").count() == 1 and "/ 0:0" in player.locator(".nk-nv-time").inner_text()
    player.locator(".nk-nv-play").click()
    page.wait_for_function("() => { const a=document.querySelector('.nk-note-page .nk-nv-player audio'); return a && (!a.paused || a.ended || a.currentTime>0); }", timeout=10000)
    page.wait_for_function("() => document.querySelector('.nk-note-page .nk-nv-player audio').currentTime > 0.2 || document.querySelector('.nk-note-page .nk-nv-player audio').ended", timeout=10000)
    player.locator(".nk-nv-play").click()
    page.screenshot(path=str(output / f"note-voice-player-{width}.png"))

    # ⋮ → Rename caption.
    block_menu(page, sheet, 0, "Rename caption")
    page.wait_for_function("id => window.QB.getState().questionNotes[id].blocks[0].caption==='Murmur at the apex'", arg=QUESTION_ID)
    assert prompts and sheet.locator(".nk-nb.is-audio .nk-nb-title").inner_text() == "Murmur at the apex"

    # An existing audio file becomes a voice block; a text block can sit between clips.
    add_from_menu(sheet, "Text")
    sheet.locator("textarea").fill("Pansystolic, radiates to the axilla.")
    sheet.get_by_role("button", name="Save", exact=True).click()
    sheet.locator("textarea").wait_for(state="detached", timeout=5000)
    sheet.locator(".nk-note-file-audio").set_input_files(str(wav))
    page.wait_for_function("document.querySelectorAll('.nk-nb.is-audio').length===2", timeout=15000)
    blocks = note_blocks(page)
    assert [b["type"] for b in blocks] == ["audio", "text", "audio"], blocks
    assert blocks[2]["mime"] == "audio/wav" and 800 <= blocks[2]["durationMs"] <= 1300 and blocks[2]["caption"] == "murmur-tip", blocks[2]
    block_menu(page, sheet, 2, "Move up")
    assert [b["type"] for b in note_blocks(page)] == ["audio", "audio", "text"]
    players_ready(page, 2)
    page.wait_for_timeout(600)  # the reorder glide
    page.screenshot(path=str(output / f"note-voice-page-{width}.png"))

    # Persistence: reload and the clips play from IndexedDB.
    sheet.get_by_role("button", name="Close notes").click()
    assert page.locator(".nk-note-bar-count").inner_text() == "3"
    page.reload(wait_until="domcontentloaded")
    page.wait_for_function("window.QB && window.QB.getState")
    sheet = open_notes(page)
    players_ready(page, 2)
    sheet.get_by_role("button", name="Close notes").click()

    # More → My notes shows the voice count.
    page.evaluate("window.QB.nav('notes')")
    page.locator(".nk-notes-item").wait_for(state="visible")
    assert page.locator(".nk-notes-item-voice").inner_text().strip() == "2 voice clips"
    page.screenshot(path=str(output / f"note-voice-index-{width}.png"), full_page=True)
    page.locator(".nk-notes-item button").click()
    page.wait_for_function("location.hash==='#practice'")
    page.locator(".option").first.click()
    page.evaluate("window.QB.submitPractice()")
    sheet = open_notes(page)

    # Five clips per note: the menu stops offering Voice.
    for _ in range(3):
        target = len([b for b in note_blocks(page) if b["type"] == "audio"]) + 1
        sheet.locator(".nk-note-file-audio").set_input_files(str(wav))
        page.wait_for_function("n => document.querySelectorAll('.nk-nb.is-audio').length===n", arg=target, timeout=15000)
    sheet.locator(".nk-np-add-btn").click()
    assert sheet.locator(".nk-np-add-menu").get_by_role("menuitem", name="Voice", exact=True).is_disabled(), "a note holds five voice clips"
    page.keyboard.press("Escape")

    # Delete: the clip leaves the note and this device.
    removed = note_blocks(page)[0]["assetId"]
    block_menu(page, sheet, 0, "Delete")
    page.wait_for_function("([id, gone]) => !window.QB.getState().questionNotes[id].blocks.some(b => b.assetId === gone)", arg=[QUESTION_ID, removed])
    wait_until(page, lambda: removed not in {m["id"] for m in idb_metas(page)}, 10, "the deleted clip to leave device storage")
    while note_blocks(page):
        count = len(note_blocks(page))
        block_menu(page, sheet, 0, "Delete")
        page.wait_for_function("([id, n]) => (window.QB.getState().questionNotes[id].blocks||[]).length===n-1", arg=[QUESTION_ID, count])
    assert sheet.locator(".nk-np-empty").is_visible()
    wait_until(page, lambda: not idb_metas(page), 10, "a deleted signed-out note to remove its clips")
    assert not errors, f"Browser errors: {errors!r}"
    context.close()


def blocked_flow(browser, origin: str) -> None:
    """Denied and missing microphones explain themselves inline; importing still works."""
    for script, expect in (
        ("navigator.mediaDevices.getUserMedia=()=>Promise.reject(new DOMException('denied','NotAllowedError'));", "Microphone access is blocked"),
        ("delete window.MediaRecorder;", "cannot record audio"),
    ):
        context = browser.new_context(viewport={"width": 390, "height": 844}, service_workers="block")
        context.add_init_script(script)
        page = context.new_page()
        errors: list[str] = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(origin) else route.abort())
        page.goto(origin + "/#dashboard", wait_until="domcontentloaded")
        page.wait_for_function("window.QB && window.QB.getState")
        open_question(page)
        sheet = open_notes(page)
        # The add menu fans out with a spring; under a loaded runner a tap can land mid-morph
        # and miss Voice (as block_menu notes), so retry until the recorder opens.
        for _ in range(3):
            add_voice(page, sheet)
            try:
                sheet.locator(".nk-nb.is-recorder").wait_for(state="visible", timeout=5000)
                break
            except Exception:
                page.wait_for_timeout(400)
        else:
            raise SystemExit("blocked flow: the recorder never opened: " + json.dumps(page.evaluate(
                "() => ({hash: location.hash, guard: history.state && history.state.nkSessionGuard || null,"
                " session: window.QB.getState().activeSession && window.QB.getState().activeSession.mode || null,"
                " sheet: document.querySelectorAll('.nk-note-page').length,"
                " menu: !!document.querySelector('.nk-np-add-menu:not([hidden])'),"
                " blocks: [...document.querySelectorAll('.nk-note-page .nk-nb')].map(b => b.className)})")))
        record = sheet.locator(".nk-nr-record")
        if record.is_enabled():
            record.click()
        message = sheet.locator(".nk-nr-message")
        message.wait_for(state="visible", timeout=10000)
        assert expect in message.inner_text(), message.inner_text()
        assert sheet.get_by_role("button", name="Import audio").is_enabled()
        assert not note_blocks(page), "nothing is saved when recording is unavailable"
        assert not errors, errors
        context.close()


def sync_flow(browser, origin: str, wav: Path, output: Path) -> None:
    store = FakeFirestore()
    auth = json.dumps({"uid": "learner", "email": "learner@example.com", "idToken": fake_token(), "refreshToken": "refresh", "expiresAt": int(time.time() * 1000) + 3_600_000})
    config = "window.NK_QBANK_FIREBASE_CONFIG={apiKey:'test-key',projectId:'demo',anatomyPdfUrl:''};"

    def device():
        context = browser.new_context(viewport={"width": 820, "height": 1180}, service_workers="block", permissions=["microphone"])
        context.add_init_script(f"if(!localStorage.getItem('qbank_firebase_auth_v1'))localStorage.setItem('qbank_firebase_auth_v1',{json.dumps(auth)});")
        page = context.new_page()
        errors: list[str] = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("dialog", lambda dialog: dialog.accept())
        page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(origin) else route.abort())
        page.route("**/qbank-config.js*", lambda route: route.fulfill(status=200, content_type="application/javascript", body=config))
        page.route("https://firestore.googleapis.com/**", store.handle)
        page.goto(origin + "/#dashboard", wait_until="domcontentloaded")
        page.wait_for_function("window.QB && window.QB.getState")
        return context, page, errors

    def payload(doc) -> dict:
        text = doc["fields"]["payload"]["stringValue"]
        return json.loads(text) if text else {}

    ipad, page_a, errors_a = device()
    open_question(page_a)
    sheet = open_notes(page_a)
    add_from_menu(sheet, "Text")
    sheet.locator("textarea").fill("Synced cue")
    sheet.get_by_role("button", name="Save", exact=True).click()
    sheet.locator("textarea").wait_for(state="detached", timeout=5000)
    record_clip(page_a, sheet, 1.2)
    page_a.wait_for_function("document.querySelectorAll('.nk-nb.is-audio').length===1", timeout=15000)
    clip = note_blocks(page_a)[1]
    assert clip["type"] == "audio", note_blocks(page_a)
    wait_until(page_a, lambda: bool(store.kind("noteAssets") and store.kind("noteVoice")), 40, "voice clip and its chunks to upload")
    chunks = store.kind("noteAssets")
    assert all(len(doc["fields"]["payload"]["stringValue"]) <= 900000 for doc in chunks.values()), "chunks must fit the Firestore rule"
    first = payload(next(doc for name, doc in chunks.items() if name.endswith(f"{clip['assetId']}~0")))
    assert first["kind"] == "audio" and first["bytes"] == clip["bytes"] and first["count"] == 1, {k: v for k, v in first.items() if k != "data"}
    blocks_doc = payload(next(iter(store.kind("noteBlocks").values())))
    assert [b["type"] for b in blocks_doc["blocks"]] == ["text"], "noteBlocks carries only what older versions keep"
    voice_doc = payload(next(iter(store.kind("noteVoice").values())))
    assert [(c["assetId"], c["at"]) for c in voice_doc["clips"]] == [(clip["assetId"], 1)], voice_doc
    assert not errors_a, errors_a

    print("voice notes: first device uploaded", flush=True)
    android, page_b, errors_b = device()
    page_b.wait_for_function("id => (window.QB.getState().questionNotes?.[id]?.blocks||[]).map(b=>b.type).join()==='text,audio'", arg=QUESTION_ID, timeout=40000)
    page_b.evaluate("window.QB.nav('notes')")
    page_b.locator(".nk-notes-item-voice").wait_for(state="visible")
    wait_until(page_b, lambda: any(m["id"] == clip["assetId"] and m["bytes"] == clip["bytes"] and m.get("kind") == "audio" for m in idb_metas(page_b)), 40, "the second device to download the exact clip bytes")
    page_b.locator(".nk-notes-item button").click()
    page_b.wait_for_function("location.hash==='#practice'")
    page_b.locator(".option").first.click()
    page_b.evaluate("window.QB.submitPractice()")
    sheet_b = open_notes(page_b)
    players_ready(page_b, 1)
    page_b.screenshot(path=str(output / "note-voice-synced-device.png"))
    sheet_b.get_by_role("button", name="Close notes").click()

    print("voice notes: second device plays the clip", flush=True)
    # An older app version edits the text: its noteBlocks has no clips and is newer. The clip stays.
    old_at = int(time.time() * 1000) + 5000
    with store.lock:
        for kind, body in (("notes", {"text": "Edited on the old app", "deleted": False}), ("noteBlocks", {"blocks": [{"type": "text", "text": "Edited on the old app"}], "deleted": False})):
            # Each device writes its own documents ({device}--{question}); add the older device's copy.
            mine = next(name for name in store.docs if f"/{kind}/" in name)
            name = mine.rsplit("/", 1)[0] + f"/android-old--{QUESTION_ID}"
            fields = {"kind": {"stringValue": kind}, "entityId": {"stringValue": QUESTION_ID}, "ownerDevice": {"stringValue": "android-old"}, "updatedAt": {"integerValue": str(old_at)}, "deleted": {"booleanValue": False}, "payload": {"stringValue": json.dumps(body, separators=(",", ":"))}, "schemaVersion": {"integerValue": "1"}}
            store.docs[name] = {"name": store.docs[mine]["name"].rsplit("/", 1)[0] + f"/android-old--{QUESTION_ID}", "fields": fields}
    page_a.reload(wait_until="domcontentloaded")
    page_a.wait_for_function("id => { const b=window.QB.getState().questionNotes?.[id]?.blocks||[]; return b[0]?.text==='Edited on the old app'; }", arg=QUESTION_ID, timeout=40000)
    assert [b["type"] for b in note_blocks(page_a)] == ["text", "audio"], note_blocks(page_a)

    print("voice notes: older-version edit kept the clip", flush=True)
    # Deleting on the second device tombstones the clip's chunks and removes it everywhere.
    page_b.reload(wait_until="domcontentloaded")
    page_b.wait_for_function("id => window.QB.getState().questionNotes?.[id]?.blocks?.[0]?.text==='Edited on the old app'", arg=QUESTION_ID, timeout=40000)
    open_question(page_b)
    sheet_b = open_notes(page_b)
    block_menu(page_b, sheet_b, 1, "Delete")
    wait_until(page_b, lambda: all(doc["fields"]["deleted"]["booleanValue"] and not doc["fields"]["payload"]["stringValue"] for doc in store.kind("noteAssets").values()), 40, "the removed clip's cloud copy to clear")
    wait_until(page_b, lambda: any(payload(doc).get("clips") == [] for doc in store.kind("noteVoice").values()), 40, "the clip removal to sync")
    page_a.reload(wait_until="domcontentloaded")
    page_a.wait_for_function("id => (window.QB.getState().questionNotes?.[id]?.blocks||[]).map(b=>b.type).join()==='text'", arg=QUESTION_ID, timeout=40000)
    assert not errors_b, errors_b
    ipad.close()
    android.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--origin", help="an already served build (default: serve build/web)")
    args = parser.parse_args()
    output = ROOT / "build/ui-checks"
    output.mkdir(parents=True, exist_ok=True)
    server = None
    origin = args.origin
    if not origin:
        web = ROOT / "build/web"
        assert "nkNoteVoiceStart" in built_page(web)
        server = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(web)))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        origin = f"http://127.0.0.1:{server.server_port}"
    try:
        with tempfile.TemporaryDirectory() as folder, sync_playwright() as playwright:
            wav = make_wav(Path(folder))
            browser = playwright.chromium.launch(args=FAKE_MIC)
            for width, height in ((390, 844), (820, 1180)):
                local_flow(browser, origin, wav, output, width, height)
                print(f"voice notes: local flow ok at {width}px", flush=True)
            blocked_flow(browser, origin)
            print("voice notes: blocked microphone ok", flush=True)
            sync_flow(browser, origin, wav, output)
            browser.close()
        print("QUESTION_NOTE_VOICE_BROWSER_OK record=true player=true rename=true import=true reload=true index=true limit=true delete=true blocked=true sync=true old_app_edit=true")
    finally:
        if server:
            server.shutdown()


if __name__ == "__main__":
    main()
