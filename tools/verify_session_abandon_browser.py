#!/usr/bin/env python3
"""Real-browser check of Abandon session on the built app (build/web).

At phone (390 px) and desktop (1280 px), in light and dark themes:
- Practice: the review sheet ends with a quiet "Abandon session" row under
  Pause / Submit (which stay exactly two buttons), with a 44 px target inside
  the sheet; the question footer and header carry no Abandon.
- The confirmation is an in-app alert dialog (role alertdialog), Cancel is
  focused first, Escape cancels, and the dialog fits the viewport.
- Abandon ends the session: no active session, one history entry, every
  recorded answer withdrawn (undo events with reason 'abandoned'), no FSRS
  card or skip mark, no result, checkpoint terminal, nothing to resume; Insights
  "Study sessions" shows the row with the Abandoned badge.
- Timed test: "Abandon test" at the foot of the question navigator and of the
  review sheet; abandoning saves no result and the Tests "Recent" list shows it.

  python3 tools/verify_session_abandon_browser.py [--shots DIR] [--url URL]
"""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/ui-checks/session-abandon"
UA = "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Mobile Safari/537.36"


def box(page, selector):
    b = page.locator(selector).first.bounding_box()
    assert b, f"{selector} is not visible"
    return b


def inside(inner, outer, label):
    assert inner["x"] >= outer["x"] - 1 and inner["y"] >= outer["y"] - 1, label
    assert inner["x"] + inner["width"] <= outer["x"] + outer["width"] + 1, label
    assert inner["y"] + inner["height"] <= outer["y"] + outer["height"] + 1, label


def state(page, expr):
    return page.evaluate(f"(()=>{{const s=window.QB.getState();return {expr};}})()")


def open_app(browser, origin, width, theme):
    height = 844 if width < 600 else 900
    context = browser.new_context(viewport={"width": width, "height": height}, device_scale_factor=2, color_scheme=theme,
                                  is_mobile=width < 600, has_touch=width < 600, service_workers="block", user_agent=UA)
    context.add_init_script(f"try{{localStorage.setItem('nkq.theme','{theme}')}}catch(e){{}}")
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(origin + "/#dashboard", wait_until="domcontentloaded", timeout=120000)
    page.wait_for_function("window.QB && window.QB.getState", timeout=120000)
    assert page.evaluate("document.documentElement.getAttribute('data-nk-theme')") == theme
    return context, page, errors


def practice_flow(page, width, theme, shots):
    page.evaluate("window.QB.startAllPractice()")
    page.wait_for_function("window.QB.getState().activeSession?.questionIds.length>5")
    for _ in range(3):
        page.locator(".question-card .option-list button.option").first.click()
        page.wait_for_timeout(150)
        page.evaluate("window.QB.nextQ()")
        page.wait_for_timeout(150)
    sid = state(page, "s.activeSession.id")
    assert state(page, "Object.values(s.attempts).flat().filter(a=>a.sessionId===s.activeSession.id&&!a.isUndo).length") >= 1, "Practice records answers at once"
    assert page.locator(".nk-abandon-trigger").count() == 0, "no Abandon on the question screen itself"
    page.locator(".nk-session-back").click()
    page.wait_for_selector("#nk-session-review .nk-abandon-row")
    sheet = box(page, "#nk-session-review .nk-session-review-card")
    trigger = box(page, "#nk-session-review .nk-abandon-trigger")
    inside(trigger, sheet, "the Abandon row sits inside the sheet")
    assert trigger["height"] >= 43.5, f"44 px target, got {trigger['height']}"
    actions = page.locator("#nk-session-review .nk-session-review-actions button")
    assert actions.count() == 2 and actions.nth(0).inner_text().strip() == "Pause" and actions.nth(1).inner_text().strip() == "Submit", "Pause + Submit stay the only actions"
    assert trigger["y"] >= box(page, "#nk-session-review .nk-session-review-actions")["y"] + box(page, "#nk-session-review .nk-session-review-actions")["height"], "Abandon sits below Pause / Submit"
    assert page.locator("#nk-session-review .nk-abandon-trigger").inner_text().strip() == "Abandon session"
    if shots:
        page.screenshot(path=str(shots / f"practice-sheet-{theme}-{width}.png"))
    page.locator("#nk-session-review .nk-abandon-trigger").click()
    alert = page.get_by_role("alertdialog", name="Abandon this session?")
    alert.wait_for()
    inside(box(page, ".nk-abandon-dialog"), {"x": 0, "y": 0, "width": width, "height": page.viewport_size["height"]}, "the dialog fits the viewport")
    assert page.evaluate("document.activeElement?.classList.contains('nk-abandon-cancel')"), "Cancel is focused first"
    assert "3 of" in alert.inner_text() or "answered" in alert.inner_text()
    if shots:
        page.wait_for_timeout(250)
        page.screenshot(path=str(shots / f"practice-confirm-{theme}-{width}.png"))
    page.keyboard.press("Escape")
    assert page.locator("#nk-abandon-confirm").count() == 0 and state(page, "s.activeSession?.id") == sid, "Escape cancels"
    page.locator("#nk-session-review .nk-abandon-trigger").click()
    page.get_by_role("alertdialog", name="Abandon this session?").get_by_role("button", name="Abandon", exact=True).click()
    page.wait_for_function("!window.QB.getState().activeSession")
    result = state(page, """{entries:(s.abandonedSessions||[]).map(e=>e.sessionId),
      live:Object.values(s.attempts).flat().filter(a=>!a.isUndo&&!a.isRatingRevision).filter(a=>!Object.values(s.attempts).flat().some(u=>u.isUndo&&u.undoOf===a.id)).length,
      reasons:[...new Set(Object.values(s.attempts).flat().filter(a=>a.isUndo).map(a=>a.reason))],
      reviews:Object.keys(s.reviews||{}).length,eligible:Object.keys(s.fsrsReviewEligible||{}).length,tests:s.tests.length,
      cps:(s.normalPracticeCheckpoints||[]).filter(c=>c.sessionId===%r).map(c=>c.lifecycle)}""" % sid)
    assert result["entries"] == [sid], result
    assert result["live"] == 0 and result["reasons"] == ["abandoned"], result
    assert result["reviews"] == 0 and result["eligible"] == 0 and result["tests"] == 0, result
    assert result["cps"] == ["discarded"], result
    page.evaluate("window.QB.nav('dashboard')")
    page.wait_for_timeout(300)
    assert page.evaluate(f"window.QB.nkResumePracticeById({sid!r})") is False, "an abandoned session cannot be resumed"
    page.evaluate("window.QB.nav('analytics')")
    page.wait_for_selector(".nk-session-list .nk-test-row.is-abandoned")
    row = page.locator(".nk-session-list .nk-test-row.is-abandoned").first
    assert row.locator(".nk-abandoned-badge").inner_text().strip() == "Abandoned"
    row.scroll_into_view_if_needed()
    inside(box(page, ".nk-session-list .nk-test-row.is-abandoned .nk-abandoned-badge"), box(page, ".nk-session-list .nk-test-row.is-abandoned"), "the badge stays inside its row")
    if shots and width < 600:
        page.screenshot(path=str(shots / f"insights-row-{theme}-{width}.png"))


def exam_flow(page, width, theme, shots):
    page.evaluate("window.QB.nav('tests')")
    page.evaluate("window.QB.openSessionBuilder(null,'exam')")
    page.locator("#modal").get_by_role("button", name="Start Exam", exact=True).click()
    page.wait_for_function("window.QB.getState().activeSession?.mode==='exam'")
    page.locator(".question-card .option-list button.option").first.click()
    page.evaluate("window.QB.openQuestionNavigator()")
    nav = page.locator("#qb-question-navigator")
    assert nav.get_by_role("button", name="Abandon test").count() == 1
    inside(box(page, "#qb-question-navigator .nk-abandon-trigger"), box(page, "#qb-question-navigator .qb-nav-panel"), "the navigator's Abandon row sits inside the panel")
    submit, trigger = box(page, "#qb-question-navigator .qb-nav-submit"), box(page, "#qb-question-navigator .nk-abandon-trigger")
    assert trigger["y"] >= submit["y"] + submit["height"], "Submit Test is not covering Abandon"
    if shots:
        page.screenshot(path=str(shots / f"exam-navigator-{theme}-{width}.png"))
    page.evaluate("window.QB.closeQuestionNavigator()")
    page.evaluate("window.QB.openSessionReview()")
    page.locator("#nk-session-review").get_by_role("button", name="Abandon test").click()
    page.get_by_role("alertdialog", name="Abandon this test?").get_by_role("button", name="Abandon", exact=True).click()
    page.wait_for_function("!window.QB.getState().activeSession && location.hash==='#tests'")
    assert state(page, "s.tests.length") == 0
    assert state(page, "Object.values(s.attempts).flat().filter(a=>!a.isUndo&&a.source==='exam').length") == 0
    page.wait_for_selector(".nk-test-history .nk-test-row.is-abandoned")
    page.locator(".nk-test-history").scroll_into_view_if_needed()
    if shots:
        page.screenshot(path=str(shots / f"tests-recent-{theme}-{width}.png"))


def back_flow(page, width, theme, shots):
    """System Back (browser / installed PWA) asks to abandon; the guard never doubles Back."""
    page.evaluate("window.QB.nav('tests')")
    page.wait_for_url("**/#tests")
    before_len = page.evaluate("history.length")
    page.evaluate("window.QB.startAllPractice()")
    page.wait_for_function("window.QB.getState().activeSession?.questionIds.length>5 && history.state?.nkSessionGuard")
    sid = state(page, "s.activeSession.id")
    page.locator(".question-card .option-list button.option").first.click()
    page.wait_for_timeout(150)
    page.evaluate("history.back()")
    alert = page.get_by_role("alertdialog", name="Abandon this session?")
    alert.wait_for()
    assert alert.get_by_role("button", name="Cancel", exact=True).count() == 1 and alert.get_by_role("button", name="Abandon", exact=True).count() == 1
    if shots and width < 600:
        page.wait_for_timeout(250)
        page.screenshot(path=str(shots / f"back-confirm-{theme}-{width}.png"))
    alert.get_by_role("button", name="Cancel", exact=True).click()
    page.wait_for_timeout(150)
    assert page.evaluate("location.hash") == "#practice" and state(page, "s.activeSession?.id") == sid, "Cancel keeps the session"
    assert page.evaluate("history.state?.nkSessionGuard") == sid, "the guard is back after Cancel"
    # Submit: the guard goes first, so Results takes the session's place and one Back leaves it
    # for the page before the session, never a stale #practice entry.
    page.evaluate("window.QB.openSessionReview()")
    page.locator("#nk-session-review").get_by_role("button", name="Submit", exact=True).click()
    page.wait_for_function("!window.QB.getState().activeSession && location.hash.startsWith('#result/')")
    assert not page.evaluate("history.state?.nkSessionGuard"), "no guard left after Submit"
    assert page.evaluate("history.length") <= before_len + 2, "Submit added no entry beyond the unguarded app's"
    page.evaluate("history.back()")
    page.wait_for_function("!location.hash.startsWith('#result/')")
    page.wait_for_timeout(150)
    assert page.evaluate("location.hash") not in ("#practice", "#exam"), f"Back from Results landed on a stale session entry: {page.evaluate('location.hash')}"
    page.evaluate("window.QB.nav('tests')")
    page.wait_for_url("**/#tests")
    # Timed test: Back asks "Abandon this test?"; Abandon leaves nothing.
    page.evaluate("window.QB.openSessionBuilder(null,'exam')")
    page.locator("#modal").get_by_role("button", name="Start Exam", exact=True).click()
    page.wait_for_function("window.QB.getState().activeSession?.mode==='exam' && history.state?.nkSessionGuard")
    tests_before = state(page, "s.tests.length")
    page.evaluate("history.back()")
    exam_alert = page.get_by_role("alertdialog", name="Abandon this test?")
    exam_alert.wait_for()
    exam_alert.get_by_role("button", name="Abandon", exact=True).click()
    page.wait_for_function("!window.QB.getState().activeSession && location.hash==='#tests'")
    assert state(page, "s.tests.length") == tests_before, "abandon from Back saved no result"
    assert not page.evaluate("history.state?.nkSessionGuard"), "no guard left after Abandon"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--shots", type=Path)
    parser.add_argument("--url")
    args = parser.parse_args()
    shots = args.shots or OUT
    shots.mkdir(parents=True, exist_ok=True)
    server = None
    if args.url:
        origin = args.url.rstrip("/")
    else:
        web = ROOT / "build/web"
        assert "NK_SESSION_ABANDON_V1_START" in (web / "index.html").read_text(encoding="utf-8", errors="ignore"), "build/web has the abandon module"
        server = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(web)))
        threading.Thread(target=server.serve_forever, daemon=True).start()
        origin = f"http://127.0.0.1:{server.server_port}"
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            for width in (390, 1280):
                for theme in ("light", "dark"):
                    context, page, errors = open_app(browser, origin, width, theme)
                    practice_flow(page, width, theme, shots)
                    exam_flow(page, width, theme, shots)
                    back_flow(page, width, theme, shots)
                    assert not errors, errors
                    context.close()
                    print(f"SESSION_ABANDON_BROWSER_OK width={width} theme={theme}")
            browser.close()
    finally:
        if server:
            server.shutdown()


if __name__ == "__main__":
    main()
