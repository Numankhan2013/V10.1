#!/usr/bin/env python3
"""Real-browser layout check of the "not studied yet" flag on the app stylesheet.

Builds a page with app.css and the page's own nkSessionHeader / bookmarkButton /
navIcon / nkSessionActionBar, installs not_studied_flags.js over them the way
the page does, and checks at phone (390 px) and desktop widths, light and dark:
the header flag sits beside the bookmark without overlapping it or the grid
button, keeps a 40 px target, shows its on state, and never enters the fixed
footer; the topic grid's flag corner stays inside its cell, which still opens
the question; the topic-list badge stays inside its row; "Practice flagged"
starts the flagged set.

  python3 tools/verify_not_studied_browser.py [--shots DIR]
"""
import argparse
import json
from pathlib import Path

from js_extract import extract_function

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "app/src/main/modules/not_studied_flags.js"
CSS = ROOT / "app/src/main/assets/app.css"
HTML = ROOT / "app/src/main/assets/index.html"

PAGE = """<!doctype html><html data-nk-ui="geist" data-nk-theme="%(theme)s"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>%(css)s</style></head><body><div id="app"></div>
<script>
(function(){
  const qs=['q1','q2','q3','q4','q5','q6','q7','q8','q9','q10','q11','q12'].map((id,i)=>({id,chapterId:'c1',correctOption:1}));
  let state={notStudied:{q2:{on:true,at:1,updatedAt:1},q7:{on:true,at:1,updatedAt:1}},bookmarks:{},attempts:{},reviews:{},tests:[],fsrsReviewEligible:{},activeSession:{id:'s1',mode:'practice',questionIds:qs.map(q=>q.id),index:1,answers:{},submitted:{},startedAt:Date.now()}};
  const calls=[];
  const BY_ID=Object.fromEntries(qs.map(q=>[q.id,q])),CHAPTERS=[{id:'c1',title:'Brachial plexus and upper limb nerve injuries'},{id:'c2',title:'Thorax'}],CHAPTER_BY_ID={c1:CHAPTERS[0],c2:CHAPTERS[1]};
  const chapterQuestions=cid=>cid==='c1'?qs:[];
  const esc=v=>String(v).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'})[c]);
  const fmtNum=n=>String(n);
  function saveState(){return true} function showToast(m){calls.push(['toast',m])} function nkStrictPrevIndex(){return 0}
  function startSession(ids,mode,title){calls.push(['start',ids,mode,title]);return true;}
  let render=()=>window.__ns.paint();
  let nkFsrsRecordAttempt=()=>true,recordAttempt=nkFsrsRecordAttempt,submitPractice=()=>{},selectExam=()=>{},nkMarkSkippedFromSession=()=>{},navigate=()=>{},openSessionReview=()=>{},openQuestionNavigator=()=>{};
  %(page_functions)s
  let topics=()=>'<div class="nk-app-v114 nk-topics-v114"><section class="nk-topic-group"><div class="nk-topic-list">'+CHAPTERS.map((c,i)=>`<button class="nk-topic-row is-inprogress" onclick="window.QB.openChapter('${c.id}')"><span class="nk-topic-index">${i+1}</span><span class="nk-topic-copy"><strong>${esc(c.title)}</strong><small>8 questions left</small></span></button>`).join('')+'</div></section></div>';
  let chapterPage=cid=>`<div class="nk-app-v114 nk-chapter-v114"><section class="nk-chapter-hero"><div class="nk-chapter-title"><h1>Upper limb</h1><div class="nk-topic-library"><div class="nk-topic-map">${qs.map((q,i)=>`<button class="nk-library-row nk-topic-cell is-${i%%4===0?'c':i%%4===1?'w':i%%4===2?'k':'u'}" data-s="u" aria-label="Question ${i+1}, not attempted" onclick="window.QB.practiceOne('${q.id}')">${i+1}</button>`).join('')}</div><ul class="nk-topic-legend"><li class="is-c"><b>3</b> correct</li></ul></div></div><div class="nk-chapter-actions"><div class="nk-topic-options"><button class="nk-topic-option">${navIcon('clock',18)}<span>Timed test</span><small>12 min</small>${navIcon('chevron',16)}</button></div></div></section></div>`;
  %(module)s
  window.QB={nkToggleNotStudied,nkPracticeNotStudied,practiceOne:id=>calls.push(['one',id]),toggleBookmark:()=>{},openQuestionNavigator:()=>{},openSessionReview:()=>{},prevQ:()=>{},nextQ:()=>{},openChapter:()=>{}};
  window.__ns={calls,state:()=>state,view:'session',paint(){
    const app=document.getElementById('app'),s=state.activeSession,q=BY_ID[s.questionIds[s.index]];
    if(this.view==='session')app.innerHTML=`<main class="page fade-in qbank-session-page"><div class="nk-v114-session is-practice">${nkSessionHeader(q,s,'practice')}<div class="question-shell"><section class="question-card"><div class="question-text">Which nerve root is injured in Erb palsy?</div></section></div></div></main>`+nkSessionActionBar(s,'practice');
    else if(this.view==='topic')app.innerHTML='<main class="page fade-in">'+chapterPage('c1')+'</main>';
    else app.innerHTML='<main class="page fade-in">'+topics()+'</main>';
  }};
  window.__ns.paint();
})();
</script></body></html>"""


def page(theme):
    html = HTML.read_text(encoding="utf-8")
    funcs = "\n".join(f"let {name}=" + extract_function(html, name).strip() + ";" for name in ("navIcon", "bookmarkButton", "nkSessionHeader", "nkSessionActionBar"))
    return PAGE % {"theme": theme, "css": CSS.read_text(encoding="utf-8"), "module": MODULE.read_text(encoding="utf-8"), "page_functions": funcs}


def box(pg, sel):
    b = pg.locator(sel).first.bounding_box()
    assert b, f"{sel} not visible"
    return b


def overlap(a, b):
    return not (a["x"] + a["width"] <= b["x"] + 0.5 or b["x"] + b["width"] <= a["x"] + 0.5 or a["y"] + a["height"] <= b["y"] + 0.5 or b["y"] + b["height"] <= a["y"] + 0.5)


def inside(inner, outer):
    return inner["x"] >= outer["x"] - 0.5 and inner["y"] >= outer["y"] - 0.5 and inner["x"] + inner["width"] <= outer["x"] + outer["width"] + 0.5 and inner["y"] + inner["height"] <= outer["y"] + outer["height"] + 0.5


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
                pg.route("http://notstudied.test/", lambda route: route.fulfill(status=200, content_type="text/html", body=page(theme)))
                pg.goto("http://notstudied.test/")
                pg.wait_for_timeout(80)
                # Session header: flag beside bookmark, no overlap, 40 px target, inside the viewport.
                flag, mark, grid = box(pg, ".nk-ns-toggle"), box(pg, ".bookmark-toggle"), box(pg, ".nk-grid-trigger")
                count = box(pg, ".nk-session-count")
                for other in (mark, grid, count):
                    assert not overlap(flag, other), (flag, other)
                assert flag["x"] < mark["x"], "flag sits before the bookmark"
                assert flag["height"] >= 40 and flag["width"] >= 40, flag
                assert flag["x"] >= 0 and grid["x"] + grid["width"] <= width + 0.5, "header fits the viewport"
                assert pg.locator(".nk-session-footer .nk-ns-toggle").count() == 0, "the footer stays Previous + Next"
                assert pg.locator(".nk-session-footer .fixed-actions-inner > button").count() == 2
                on = pg.evaluate("getComputedStyle(document.querySelector('.nk-ns-toggle')).color")
                assert pg.get_attribute(".nk-ns-toggle", "aria-pressed") == "true"
                if shots:
                    pg.screenshot(path=str(shots / f"ns-session-{theme}-{width}.png"), clip={"x": 0, "y": 0, "width": width, "height": 140})
                pg.click(".nk-ns-toggle")
                pg.wait_for_timeout(30)
                assert pg.get_attribute(".nk-ns-toggle", "aria-pressed") == "false", "tap clears the flag"
                off = pg.evaluate("getComputedStyle(document.querySelector('.nk-ns-toggle')).color")
                assert on != off, "on and off states look different"
                assert pg.evaluate("window.__ns.state().notStudied.q2.on") is False
                pg.click(".nk-ns-toggle")
                assert pg.evaluate("window.__ns.state().notStudied.q2.on") is True, "tap flags again"
                # Topic page grid.
                pg.evaluate("window.__ns.view='topic';window.__ns.paint()")
                cells = pg.locator(".nk-topic-cell.is-ns")
                assert cells.count() == 2, cells.count()
                for i in range(2):
                    cell = cells.nth(i).bounding_box()
                    corner = cells.nth(i).locator(".nk-ns-corner").bounding_box()
                    assert corner and inside(corner, cell), (corner, cell)
                    assert corner["width"] <= cell["width"] / 2, "corner flag stays small"
                legend = " ".join(pg.locator(".nk-topic-legend li.is-ns").inner_text().split()).lower()
                assert legend == "2 not studied", legend
                option = pg.locator(".nk-topic-option.nk-topic-ns")
                assert option.is_visible() and "Practice flagged" in option.inner_text() and "2" in option.inner_text()
                if shots:
                    pg.screenshot(path=str(shots / f"ns-topic-{theme}-{width}.png"), full_page=True)
                cells.nth(0).click()
                option.click()
                calls = pg.evaluate("window.__ns.calls")
                assert ["one", "q2"] in calls, calls
                assert ["start", ["q2", "q7"], "practice", "Brachial plexus and upper limb nerve injuries · Not studied"] in calls, calls
                # Topic list badge.
                pg.evaluate("window.__ns.view='list';window.__ns.paint()")
                badge, row = box(pg, ".nk-ns-badge"), box(pg, ".nk-topic-row")
                assert inside(badge, row), (badge, row)
                assert pg.locator(".nk-ns-badge").count() == 1 and pg.locator(".nk-ns-badge").inner_text().strip() == "2"
                if shots:
                    pg.screenshot(path=str(shots / f"ns-list-{theme}-{width}.png"))
                assert not errors, errors
                ctx.close()
        browser.close()
    print("NOT_STUDIED_BROWSER_OK")


if __name__ == "__main__":
    main()
