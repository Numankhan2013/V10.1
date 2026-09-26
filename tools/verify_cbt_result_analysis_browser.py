#!/usr/bin/env python3
"""Exercise mixed-bank saved CBT analysis and targeted follow-up in a phone browser."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

from playwright.sync_api import expect, sync_playwright


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    web = ROOT / "build/web"
    assert "NK_CBT_RESULT_ANALYSIS_V1_START" in (web / "index.html").read_text(encoding="utf-8")
    output = ROOT / "build/ui-checks"
    output.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(web)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f"http://127.0.0.1:{server.server_port}"
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            context = browser.new_context(viewport={"width": 390, "height": 844}, service_workers="block")
            page = context.new_page()
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(origin) else route.abort())
            page.goto(origin + "/#tests", wait_until="domcontentloaded")
            page.wait_for_function("window.QB && window.QB.getState")
            ids = page.evaluate("""() => {
              const all=nkAllStudyQuestions();
              const take=(bank,subject)=>all.find(q=>q.bank===bank&&q.subject===subject&&
                Number(q.correctOption)>=1&&Number(q.correctOption)<=4);
              const prep=take('PrepLadder','Anatomy'),marrow=take('Marrow','Anatomy'),phys=take('Marrow','Physiology');
              const wrong=Number(prep.correctOption)%4+1;
              const test={id:'cbt_analysis_browser',title:'Mixed-bank analysis check',
                questionIds:[prep.id,marrow.id,phys.id],answers:{[prep.id]:wrong,[marrow.id]:Number(marrow.correctOption)},
                correct:1,incorrect:1,unattempted:1,total:3,attempted:2,totalTimeMs:40000,
                questionTimes:{[prep.id]:12000,[marrow.id]:15000,[phys.id]:13000},createdAt:Date.now()-10000,originRoute:'tests'};
              const state=window.QB.getState();state.tests.push(test);window.QB.saveState();
              navigate('result',test.id);
              return [prep.id,marrow.id,phys.id];
            }""")
            expect(page.get_by_role("heading", name="Topic breakdown")).to_be_visible()
            analysis = page.locator(".nk-cbt-analysis")
            assert analysis.locator(".nk-cbt-analysis-row").count() == 3
            analysis.locator(".nk-cbt-analysis-rest summary").click()
            assert "Anatomy · PrepLadder" in analysis.inner_text()
            assert "Anatomy · Marrow" in analysis.inner_text()
            assert "Physiology · Marrow" in analysis.inner_text()
            assert "2 questions to revisit" in analysis.inner_text()
            assert "1 incorrect · 0 unattempted" in analysis.inner_text()
            assert "0 incorrect · 1 unattempted" in analysis.inner_text()
            page.screenshot(path=str(output / "cbt-result-analysis-phone.png"), full_page=True)
            page.reload(wait_until="domcontentloaded")
            expect(page.get_by_role("heading", name="Topic breakdown")).to_be_visible()
            page.get_by_role("button", name="Practise missed questions").click()
            page.wait_for_function("location.hash==='#practice' && window.QB.getState().activeSession?.mode==='practice'")
            session = page.evaluate("window.QB.getState().activeSession")
            assert session["questionIds"] == [ids[0], ids[2]], session
            assert session["context"] == "cbt-followup"
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown()
    print("CBT_RESULT_ANALYSIS_BROWSER_OK mixedBank=true savedAnswers=true followup=true")


if __name__ == "__main__":
    main()
