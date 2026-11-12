#!/usr/bin/env python3
"""Real-browser check of explanation highlights on the source module and stylesheet.

Builds a small page with the app's stylesheet and an explanation that mixes
bold text, a list and a table, installs question_highlights.js on it the way the
page does, then drives a real selection: highlight across element boundaries,
re-render (the app replaces markup on every render), shift the text, recolour,
remove and clear, at phone and desktop widths, in light and dark themes.

  python3 tools/verify_question_highlights_browser.py [--shots DIR]
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "app/src/main/modules/question_highlights.js"
CSS = ROOT / "app/src/main/assets/app.css"

EXPLANATION = (
    '<section class="nk-key-takeaway"><span class="nk-takeaway-icon"></span><div><div class="nk-takeaway-label">Key takeaway</div>'
    '<p>Erb palsy injures the <strong>upper trunk</strong> of the brachial plexus.</p></div></section>'
    '<section class="nk-source-section is-marrow"><header><div><strong>Detailed explanation</strong></div><span>Structured text</span></header>'
    '<div data-marrow-explanation="q-demo"><div class="nk-marrow-native"><p>The <strong>upper trunk (C5–C6)</strong> is stretched when the head and shoulder are forced apart, '
    'producing the classic <em>waiter&#39;s tip</em> posture.</p><ul><li>Loss of shoulder abduction</li><li>Loss of elbow flexion</li></ul>'
    '<table><tbody><tr><td>Root</td><td>Muscle</td></tr><tr><td>C5</td><td>Deltoid</td></tr></tbody></table>'
    '<button type="button">Zoom figure</button><p>Klumpke palsy, in contrast, affects the lower trunk (C8–T1).</p></div></div></section>'
)

PAGE = """<!doctype html><html data-nk-ui="geist" data-nk-theme="%(theme)s"><head><meta name="viewport" content="width=device-width,initial-scale=1">
<style>%(css)s</style><style>body{margin:0;background:var(--nkg-bg);color:var(--nkg-fg);font-family:var(--nkg-font-sans)} .wrap{max-width:720px;margin:0 auto;padding:24px 18px 120px;font-size:16px;line-height:1.65}
.nk-source-section header{display:flex;justify-content:space-between;font-size:13px;color:var(--nkg-fg-3);margin:18px 0 8px} table{border-collapse:collapse} td{border:1px solid var(--nkg-border);padding:4px 10px}</style></head>
<body><div class="wrap"><h3 style="margin:0 0 12px">Which nerve roots are injured in Erb palsy?</h3><div id="app"></div></div>
<script>
(function(){
  let state={questionHighlights:%(saved)s};
  const esc=v=>String(v).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'})[c]);
  function saveState(){localStorage.setItem('hl_state',JSON.stringify(state.questionHighlights));return true;}
  function showToast(){}
  let nkStudySupport=function(q){return '<div class="nk-study-support">'+window.__EXPL+'</div>';};
  %(module)s
  window.__hl={state:()=>state,render:()=>{document.getElementById('app').innerHTML=nkStudySupport({id:'q-demo'});}};
})();
window.__EXPL=%(expl)s;
window.__hl.render();
</script></body></html>"""


def page(theme, saved, expl=EXPLANATION):
    return PAGE % {"theme": theme, "css": CSS.read_text(encoding="utf-8"), "saved": json.dumps(saved), "module": MODULE.read_text(encoding="utf-8"), "expl": json.dumps(expl)}


SELECT = """([startSel,startText,endSel,endText])=>{
  const find=(sel,needle)=>{const root=document.querySelector(sel);const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);let n;while((n=w.nextNode())){const i=n.nodeValue.indexOf(needle);if(i>=0)return [n,i];}throw new Error('no '+needle);};
  const [a,ai]=find(startSel,startText),[b,bi]=find(endSel,endText);
  const r=document.createRange();r.setStart(a,ai);r.setEnd(b,bi+endText.length);
  const s=getSelection();s.removeAllRanges();s.addRange(r);document.dispatchEvent(new Event('selectionchange'));
}"""


def load(pg, html):
    # A real origin, so the page has localStorage like the app.
    pg.route("http://highlights.test/", lambda route: route.fulfill(status=200, content_type="text/html", body=html))
    pg.goto("http://highlights.test/")


def marks(pg):
    return pg.evaluate("""()=>{const out={};document.querySelectorAll('mark.nk-hl').forEach(m=>{(out[m.dataset.nkHl]=out[m.dataset.nkHl]||{color:m.dataset.nkHlColor,text:''}).text+=m.textContent;});return Object.values(out).map(x=>x.color+':'+x.text).sort();}""")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--shots", default="")
    args = parser.parse_args()
    shots = Path(args.shots) if args.shots else None
    if shots:
        shots.mkdir(parents=True, exist_ok=True)
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for width, height, touch in ((390, 844, True), (1280, 860, False)):
            for theme in ("light", "dark"):
                ctx = browser.new_context(viewport={"width": width, "height": height}, has_touch=touch, is_mobile=touch, device_scale_factor=2)
                pg = ctx.new_page()
                errors = []
                pg.on("pageerror", lambda e: errors.append(str(e)))
                load(pg, page(theme, {}))
                pg.wait_for_timeout(100)
                bar = pg.locator(".nk-hl-bar")
                # 1. Across bold, from the paragraph into the list item: crosses element boundaries.
                pg.evaluate(SELECT, [".nk-marrow-native", "is stretched", ".nk-marrow-native li", "Loss of shoulder"])
                bar.wait_for(state="visible")
                assert pg.locator('.nk-hl-bar [data-nk-hl-act="remove"]').is_hidden(), "create mode offers colours only"
                if shots and theme == "light":
                    pg.screenshot(path=str(shots / f"highlight-toolbar-{width}.png"))
                pg.click('[data-nk-hl-pick="yellow"]')
                assert bar.is_hidden(), "toolbar closes after colouring"
                # 2. Across the bold run in the takeaway (second zone), green.
                pg.evaluate(SELECT, [".nk-key-takeaway p", "the ", ".nk-key-takeaway p", "trunk"])
                bar.wait_for(state="visible")
                pg.click('[data-nk-hl-pick="green"]')
                # 3. Inside the table cell and past the skipped button, blue.
                pg.evaluate(SELECT, [".nk-marrow-native p:last-of-type", "Klumpke palsy", ".nk-marrow-native p:last-of-type", "lower trunk"])
                bar.wait_for(state="visible")
                pg.click('[data-nk-hl-pick="blue"]')
                pg.wait_for_timeout(60)
                got = marks(pg)
                assert got == sorted(["yellow:is stretched when the head and shoulder are forced apart, producing the classic waiter's tip posture.Loss of shoulder", "green:the upper trunk", "blue:Klumpke palsy, in contrast, affects the lower trunk"]), got
                assert pg.evaluate("document.querySelector('.nk-source-section header mark')") is None, "section header is never tinted"
                assert pg.evaluate("document.querySelector('table > mark, tbody > mark, tr > mark, ul > mark')") is None, "no marks inside table/list structure"
                saved = pg.evaluate("localStorage.getItem('hl_state')")
                assert saved and len(json.loads(saved)["q-demo"]["items"]) == 3
                if shots:
                    pg.evaluate("getSelection().removeAllRanges()")
                    pg.screenshot(path=str(shots / f"highlights-{theme}-{width}.png"))
                # 4. Re-render replaces markup: highlights come back from state.
                pg.evaluate("window.__hl.render()")
                pg.wait_for_timeout(80)
                assert marks(pg) == got, "highlights survive a re-render"
                # 5. A fresh page with the saved state and shifted text (a word inserted earlier).
                ctx2 = browser.new_context(viewport={"width": width, "height": height}, has_touch=touch, is_mobile=touch)
                pg2 = ctx2.new_page()
                pg2.on("pageerror", lambda e: errors.append(str(e)))
                shifted = EXPLANATION.replace("<p>The <strong>", "<p>Remember: the <strong>")
                load(pg2, page(theme, json.loads(saved), shifted))
                pg2.wait_for_timeout(120)
                assert marks(pg2) == got, ("highlights re-anchor after the text shifts", marks(pg2))
                ctx2.close()
                # 6. Tap a highlight: edit mode, recolour, then remove.
                pg.locator('mark.nk-hl[data-nk-hl-color="green"]').first.click()
                bar.wait_for(state="visible")
                assert pg.locator('.nk-hl-bar [data-nk-hl-pick="green"]').get_attribute("aria-pressed") == "true"
                if shots and theme == "dark" and width == 390:
                    pg.wait_for_timeout(300)  # let the toolbar's entrance finish
                    pg.screenshot(path=str(shots / f"highlight-edit-{theme}-{width}.png"))
                pg.click('[data-nk-hl-pick="pink"]')
                assert any(m.startswith("pink:the upper trunk") for m in marks(pg)), marks(pg)
                pg.locator('mark.nk-hl[data-nk-hl-color="pink"]').first.click()
                pg.click('[data-nk-hl-act="remove"]')
                assert not any("upper trunk" in m and m.startswith("pink") for m in marks(pg)) and len(marks(pg)) == 2, marks(pg)
                # 7. Clear all needs a confirming second tap.
                pg.locator("mark.nk-hl").first.click()
                pg.click('[data-nk-hl-act="clear"]')
                assert len(marks(pg)) == 2, "first tap only arms clear-all"
                pg.click('[data-nk-hl-act="clear"]')
                assert marks(pg) == [], marks(pg)
                items = json.loads(pg.evaluate("localStorage.getItem('hl_state')"))["q-demo"]["items"]
                assert all(i.get("deleted") for i in items.values()), "removals are kept as tombstones for sync"
                assert not errors, errors
                ctx.close()
                print(f"QUESTION_HIGHLIGHTS_BROWSER_OK width={width} theme={theme}")
        browser.close()


if __name__ == "__main__":
    main()
