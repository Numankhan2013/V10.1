#!/usr/bin/env python3
"""Home progress range and Insights period sliders: the pill never flashes to its
destination, lands on the chosen button, commits the period, survives rapid taps
and works with reduced motion, also on a 4x slower CPU (a mid-range phone)."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import threading
from playwright.sync_api import sync_playwright
from app_page import built_page

ROOT = Path(__file__).resolve().parents[1]
CASES = [("#dashboard", ".nk-home-progress-head .nkg-seg", ".nk-home-range select"),
         ("#analytics", ".nk-li-period-nav .nkg-seg", "#nk-li-period")]
STATE = """([s,nat,l])=>{const seg=document.querySelector(s),p=seg.querySelector('.nkg-seg-pill'),
  btn=[...seg.querySelectorAll('button')].find(b=>b.textContent.trim()===l),pr=btn.getBoundingClientRect(),
  sr=seg.getBoundingClientRect(),x=new DOMMatrixReadOnly(getComputedStyle(p).transform).m41,sel=document.querySelector(nat);
  return {pressed:btn.getAttribute('aria-pressed'),off:Math.abs(pr.left-sr.left-seg.clientLeft-x),
    w:Math.abs(parseFloat(p.style.width)-pr.width),val:sel.value,segs:document.querySelectorAll(s).length}}"""
TAP = """([s,l])=>{const seg=document.querySelector(s),p=seg.querySelector('.nkg-seg-pill'),
  x=()=>new DOMMatrixReadOnly(getComputedStyle(p).transform).m41,x0=x(),
  btn=[...seg.querySelectorAll('button')].find(b=>b.textContent.trim()===l),was=btn.getAttribute('aria-pressed')==='true';
  btn.click();return {was,x0,x1:x()}}"""


def main():
    web = ROOT / "build/web"
    html = built_page(web).encode()

    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path.split("?", 1)[0] in ("/", "/index.html"):
                self.send_response(200); self.send_header("Content-Type", "text/html"); self.end_headers(); self.wfile.write(html)
            else:
                super().do_GET()

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(web)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f"http://127.0.0.1:{server.server_port}"
    fails, runs = [], 0
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            for cpu, reduced in ((4, False), (1, True)):
                context = browser.new_context(viewport={"width": 390, "height": 844}, service_workers="block",
                                              reduced_motion="reduce" if reduced else "no-preference")
                page = context.new_page(); errors = []
                page.on("pageerror", lambda e: errors.append(str(e)))
                page.route("**/*", lambda r: r.continue_() if r.request.url.startswith(origin) else r.abort())
                context.new_cdp_session(page).send("Emulation.setCPUThrottlingRate", {"rate": cpu})
                settle = 1200 if cpu > 1 else 600
                for route, seg, native in CASES:
                    tag = f"{route} cpu{cpu} reduced={reduced}"
                    page.goto(origin + "/" + route)
                    page.wait_for_selector(seg + " > .nkg-seg-pill", state="attached", timeout=60000)
                    page.wait_for_timeout(1200)
                    labels = page.evaluate("s=>[...document.querySelectorAll(s+' button')].map(b=>b.textContent.trim())", seg)
                    for label in labels[::-1] + labels:
                        tap = page.evaluate(TAP, [seg, label]); runs += 1
                        # The slide owns the pill from the tap's own frame: no flash to the destination.
                        if not tap["was"] and not reduced and abs(tap["x1"] - tap["x0"]) >= 1:
                            fails.append(f"{tag} {label}: pill jumped in the tap frame {tap}")
                        page.wait_for_timeout(settle)
                        st = page.evaluate(STATE, [seg, native, label])
                        if st["pressed"] != "true" or st["off"] >= 1.5 or st["w"] >= 1.5:
                            fails.append(f"{tag} {label}: pill not on the chosen button {st}")
                        if not st["val"].lower().startswith(label.lower()[:3]):
                            fails.append(f"{tag} {label}: period not committed {st}")
                        if st["segs"] != 1:
                            fails.append(f"{tag}: {st['segs']} sliders")
                    # Fast taps 40 ms apart end on the last one.
                    seq = [labels[-1], labels[0], labels[1]]
                    for label in seq:
                        page.evaluate("([s,l])=>[...document.querySelector(s).querySelectorAll('button')].find(b=>b.textContent.trim()===l).click()", [seg, label])
                        page.wait_for_timeout(40)
                    page.wait_for_timeout(settle + 300)
                    st = page.evaluate(STATE, [seg, native, seq[-1]])
                    if st["pressed"] != "true" or st["off"] >= 1.5 or not st["val"].lower().startswith(seq[-1].lower()[:3]):
                        fails.append(f"{tag} rapid taps {seq}: {st}")
                if errors:
                    fails.append(f"cpu{cpu} reduced={reduced}: page errors {errors}")
                context.close()
            browser.close()
    finally:
        server.shutdown()
    if fails:
        raise SystemExit("SEGMENT_SLIDER_BROWSER_FAIL\n" + "\n".join(fails[:20]))
    print(f"SEGMENT_SLIDER_BROWSER_OK sliders=2 taps={runs} cpu=4x,1x reduced_motion=on,off")


if __name__ == "__main__":
    main()
