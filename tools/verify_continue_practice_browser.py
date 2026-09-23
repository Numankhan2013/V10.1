#!/usr/bin/env python3
"""Exercise the single-grid Practice end flow and durable Home Pause/Continue in the built PWA."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def button_labels(locator):
    return [locator.nth(i).inner_text().strip() for i in range(locator.count())]


def main() -> None:
    web = ROOT / "build/web"
    html = (web / "index.html").read_text(encoding="utf-8")
    for marker in ("NK_CONTINUE_PRACTICE_RESUME_V1_START", "NK_PRACTICE_SINGLE_REVIEW_GRID_V1_START"):
        if marker not in html:
            raise SystemExit(f"Practice flow layer missing from built PWA: {marker}")

    output = ROOT / "build/ui-checks"
    output.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(web)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f"http://127.0.0.1:{server.server_port}"
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()

            for width, height in ((320, 844), (390, 844), (820, 1180)):
                context = browser.new_context(
                    viewport={"width": width, "height": height},
                    service_workers="block",
                    reduced_motion="reduce",
                )
                page = context.new_page()
                page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(origin) else route.abort())
                page.goto(origin + "/#dashboard", wait_until="domcontentloaded")
                page.wait_for_function("window.QB && window.QB.getState")
                page.evaluate("window.QB.practiceOne('1-1')")

                # Question screen: the session footer must be only Previous + Next.
                footer = page.locator(".nk-session-footer")
                footer.wait_for(state="visible")
                if page.locator(".nk-practice-session-controls").count():
                    raise SystemExit(f"Pause/Submit leaked back onto the question screen at {width}px")
                labels = button_labels(footer.locator(".fixed-actions-inner button"))
                if labels != ["Previous", "Next"]:
                    raise SystemExit(f"Question footer is not Previous/Next only at {width}px: {labels}")

                # Opening the grid must go straight to the one final review sheet.
                page.evaluate("window.QB.openQuestionNavigator()")
                review = page.locator("#nk-session-review")
                review.wait_for(state="visible")
                if page.locator("#qb-question-navigator").count():
                    raise SystemExit(f"Redundant Question Navigator still exists at {width}px")
                if not review.evaluate("el => el.classList.contains('nk-practice-final-review')"):
                    raise SystemExit(f"Final Practice review sheet was not normalized at {width}px")

                actions = review.locator(".nk-session-review-actions")
                action_labels = button_labels(actions.locator("button"))
                if action_labels != ["Pause", "Submit"]:
                    raise SystemExit(f"Final review actions are not exactly Pause/Submit at {width}px: {action_labels}")
                if review.get_by_role("button", name="Back to question", exact=False).count():
                    raise SystemExit("Back to question must not exist in the final Practice grid")
                if review.get_by_role("button", name="Review unanswered", exact=False).count():
                    raise SystemExit("Review unanswered must not exist in the final Practice grid")
                if footer.is_visible():
                    raise SystemExit(f"Question footer is visible over the final grid at {width}px")

                # The final sheet must retain question navigation controls beyond Pause/Submit.
                if review.locator("button").count() < 3:
                    raise SystemExit(f"Final grid lost question navigation controls at {width}px")

                review.screenshot(path=str(output / f"practice-final-review-{width}.png"))
                context.close()

            # Real Home lifecycle regression test. Start a genuine Practice 20, pause
            # it from the final grid, then click the actual visible Today’s Focus
            # Continue Practice control. The same session, all IDs, progress and
            # position must survive.
            context = browser.new_context(viewport={"width": 390, "height": 844}, service_workers="block")
            page = context.new_page()
            page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(origin) else route.abort())
            page.goto(origin + "/#dashboard", wait_until="domcontentloaded")
            page.wait_for_function("window.QB && window.QB.getState")
            page_errors = []
            page.on("pageerror", lambda error: page_errors.append(str(error)))

            # Major-navigation smoke matrix on the same final generated app.
            for target in ("fsrs", "tests", "analytics", "more", "bookmarks", "module-builder", "study-library"):
                page.evaluate("target => window.QB.nav(target)", target)
                page.wait_for_function(
                    "target => location.hash.includes(target) && document.querySelector('#app')?.innerText.trim().length > 0",
                    arg=target,
                )
                if page.locator("#modal, #qb-question-navigator, #nk-session-review").count():
                    raise SystemExit(f"Stale overlay appeared during navigation to {target}")
            page.evaluate("window.QB.nav('dashboard')")
            page.wait_for_url("**/#dashboard")
            page.evaluate("window.QB.nav('tests')")
            page.wait_for_url("**/#tests")
            page.go_back()
            page.wait_for_url("**/#dashboard")
            if page_errors:
                raise SystemExit(f"Generated app raised page errors during navigation smoke: {page_errors}")
            page.evaluate("window.QB.startAllPractice()")
            page.wait_for_function("window.QB.getState().activeSession?.questionIds?.length > 1")

            original = page.evaluate("""() => {
              const s=window.QB.getState().activeSession;
              return {id:s.id, ids:[...s.questionIds]};
            }""")
            if len(original["ids"]) < 5:
                raise SystemExit(f"Practice 20 did not create a multi-question session: {original}")
            current_id = original["ids"][4]
            answered_ids = original["ids"][:4]
            page.evaluate("id => window.QB.toggleBookmark(id)", original["ids"][2])

            page.evaluate("""({answered,current}) => {
              const s=window.QB.getState().activeSession;
              s.index=4;
              s.answers={};
              s.submitted={};
              answered.forEach((id,i)=>{s.answers[id]=i%4;s.submitted[id]=true;});
              s.questionTimes={[current]:10};
            }""", {"answered": answered_ids, "current": current_id})

            page.evaluate("window.QB.openSessionReview()")
            review = page.locator("#nk-session-review")
            review.wait_for(state="visible")
            review.get_by_role("button", name="Pause", exact=True).click()
            page.wait_for_function("window.QB.getState().activeSession?.lifecycle==='paused'")

            paused = page.evaluate("""() => {
              const s=window.QB.getState().activeSession;
              return {id:s.id, ids:s.questionIds, sessionIds:s.sessionQuestionIds, index:s.pausedIndex};
            }""")
            if paused["id"] != original["id"] or paused["ids"] != original["ids"] or paused["sessionIds"] != original["ids"] or paused["index"] != 4:
                raise SystemExit(f"Pause did not preserve the original Practice session: {paused}")

            # Simulate a fresh installed-PWA/browser process using only persisted
            # origin state. Continue must not depend on the old JS heap.
            storage = context.storage_state()
            context.close()
            context = browser.new_context(viewport={"width": 390, "height": 844}, service_workers="block", storage_state=storage)
            page = context.new_page()
            page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(origin) else route.abort())
            page.goto(origin + "/#dashboard", wait_until="domcontentloaded")
            page.wait_for_function("window.QB && window.QB.getState().activeSession?.lifecycle==='paused'")

            # The approved Home command-center owns the visible control and wires it
            # to window.QB.nkContinueRecentPractice(). Click that exact rendered path;
            # do not substitute the older Home V4 control or a direct function call.
            continue_button = page.locator("button.nk-home-focus-action")
            continue_button.wait_for(state="visible")
            onclick = continue_button.get_attribute("onclick") or ""
            if "window.QB.nkContinueRecentPractice()" not in onclick:
                raise SystemExit(f"Home Continue is wired to an unexpected handler: {onclick}")
            continue_button.click()
            page.wait_for_function("window.QB.getState().activeSession?.lifecycle==='active'")

            result = page.evaluate("""bookmarkId => {
              const s=window.QB.getState().activeSession;
              return {
                id:s.id,
                ids:s.questionIds,
                current:s.questionIds[s.index],
                index:s.index,
                submitted:s.submitted,
                sessionIds:s.sessionQuestionIds,
                bookmarked:Boolean(window.QB.getState().bookmarks[bookmarkId])
              };
            }""", original["ids"][2])
            if result["id"] != original["id"]:
                raise SystemExit(f"Home Continue created a new session instead of resuming the paused one: {result}")
            if result["ids"] != original["ids"] or len(result["ids"]) <= 1:
                raise SystemExit(f"Home Continue collapsed the paused test to a one-question session: {result}")
            if result["current"] != current_id or result["index"] != 4:
                raise SystemExit(f"Home Continue did not restore the saved question position: {result}")
            if result["sessionIds"] != original["ids"]:
                raise SystemExit(f"Visible session diverged from the canonical paused test: {result}")
            if not all(result["submitted"].get(qid) for qid in answered_ids):
                raise SystemExit(f"Answered progress was lost while resuming from Home: {result}")
            if not result["bookmarked"]:
                raise SystemExit(f"Bookmark was lost across Practice restart: {result}")

            # Persisted-state repair: a previous buggy client may have reduced only
            # questionIds. The preserved sessionQuestionIds must still rebuild all IDs
            # when the same visible Home Continue control is used again.
            page.evaluate("window.QB.openSessionReview()")
            page.locator("#nk-session-review").get_by_role("button", name="Pause", exact=True).click()
            page.wait_for_function("window.QB.getState().activeSession?.lifecycle==='paused'")
            page.evaluate("""({current}) => {
              const s=window.QB.getState().activeSession;
              s.questionIds=[current];
              s.index=0;
            }""", {"current": current_id})
            page.locator("button.nk-home-focus-action").click()
            page.wait_for_function("window.QB.getState().activeSession?.lifecycle==='active'")
            repaired = page.evaluate("""() => {
              const s=window.QB.getState().activeSession;
              return {id:s.id,ids:s.questionIds,index:s.index,current:s.questionIds[s.index]};
            }""")
            if repaired["id"] != original["id"] or repaired["ids"] != original["ids"] or repaired["index"] != 4 or repaired["current"] != current_id:
                raise SystemExit(f"Home Continue did not repair persisted one-question state: {repaired}")

            # Two different chapters may remain paused together. Starting a new
            # chapter preserves the old checkpoint; Home Continue then offers both.
            page.evaluate("window.QB.openSessionReview()")
            page.locator("#nk-session-review").get_by_role("button", name="Pause", exact=True).click()
            page.wait_for_function("window.QB.getState().activeSession?.lifecycle==='paused'")
            topic_pair = page.evaluate("""() => {
              const all=(window.SUBJECT_QBANK_DATA?.subjects||[]).flatMap(x=>x.questions||[]);
              const found=new Map();for(const q of all){const key=String(q.chapterId||'');if(key&&!found.has(key))found.set(key,{id:String(q.id),chapterId:key,title:String(q.chapter||key)});}
              return [...found.values()].slice(0,2);
            }""")
            if len(topic_pair) != 2:
                raise SystemExit("Could not find two chapters for the multi-pause regression")
            for topic in topic_pair:
                page.evaluate("id => window.QB.practiceOne(id)", topic["id"])
                page.wait_for_function("id => window.QB.getState().activeSession?.questionIds?.[0]===id", arg=topic["id"])
                page.evaluate("window.QB.openSessionReview()")
                page.locator("#nk-session-review").get_by_role("button", name="Pause", exact=True).click()
                page.wait_for_function("window.QB.getState().activeSession?.lifecycle==='paused'")
            saved_topics = page.evaluate("""() => window.QB.getState().normalPracticeCheckpoints
              .filter(cp=>cp.lifecycle==='paused'&&cp.context?.topicId)
              .map(cp=>({id:cp.sessionId,topicId:cp.context.topicId,title:cp.context.title}))""")
            topic_sessions = [next((cp for cp in saved_topics if cp["topicId"] == topic["chapterId"]), None) for topic in topic_pair]
            if any(cp is None for cp in topic_sessions) or topic_sessions[0]["id"] == topic_sessions[1]["id"]:
                raise SystemExit(f"Paused checkpoints for both chapters were not retained: {saved_topics}")
            page.locator("button.nk-home-focus-action").click()
            chooser = page.locator("#nk-practice-sessions")
            chooser.wait_for(state="visible")
            for index, (topic, saved_session) in enumerate(zip(topic_pair, topic_sessions)):
                row = chooser.locator(".nk-saved-practice-row").filter(has_text=topic["title"])
                row.get_by_role("button", name="Resume", exact=True).click()
                page.wait_for_function("id => window.QB.getState().activeSession?.id===id", arg=saved_session["id"])
                if not page.evaluate("id => window.QB.getState().normalPracticeCheckpoints.some(cp=>cp.sessionId===id&&cp.lifecycle==='paused')", topic_sessions[1-index]["id"]):
                    raise SystemExit("Resuming one chapter removed the other paused chapter")
                page.evaluate("window.QB.openSessionReview()")
                page.locator("#nk-session-review").get_by_role("button", name="Pause", exact=True).click()
                page.wait_for_function("window.QB.getState().activeSession?.lifecycle==='paused'")
                page.locator("button.nk-home-focus-action").click()
                chooser = page.locator("#nk-practice-sessions")
                chooser.wait_for(state="visible")
            print("MULTIPLE_PAUSED_CHAPTERS_OK: both saved sessions resumed independently")

            context.close()

            # Three genuine chapter sessions exercise the complete collection:
            # answer, pause, reload, choose B, enter a special mode, finish A,
            # and discard B while C remains available.
            context = browser.new_context(viewport={"width": 390, "height": 844}, service_workers="block", reduced_motion="reduce")
            page = context.new_page()
            page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(origin) else route.abort())
            page.goto(origin + "/#dashboard", wait_until="domcontentloaded")
            page.wait_for_function("window.QB && window.QB.getState")
            chapters = page.evaluate("""() => {
              const records=window.SUBJECT_QBANK_DATA?.subjects||[];
              const record=records.find(r=>r.subject==='Physiology');
              if(!record)return [];
              const groups=new Map();
              for(const q of record.questions||[]){
                const id=String(q.chapterId||'');if(!id)continue;
                if(!groups.has(id))groups.set(id,[]);groups.get(id).push(q);
              }
              return [...groups].filter(([,qs])=>qs.length>=3&&qs.slice(0,2).every(q=>Number(q.correctOption)>0&&(q.options||[]).length>=4))
                .slice(0,3).map(([id,qs])=>({subject:record.subject,bank:'PrepLadder',id,title:String(qs[0].chapter||id),
                  ids:qs.map(q=>String(q.id)),first:Number(qs[0].correctOption),second:Number(qs[1].correctOption),choices:qs[1].options.length}));
            }""")
            if len(chapters) != 3:
                raise SystemExit(f"Could not find three deterministic multi-question chapters: {chapters}")

            snapshots = {}
            for name, chapter in zip("ABC", chapters):
                page.evaluate("c => window.QB.nkOpenSubjectChapter(c.subject,c.bank,c.id)", chapter)
                page.locator(".nk-chapter-actions button.is-primary").click()
                modal = page.locator("#modal")
                modal.wait_for(state="visible")
                modal.get_by_role("button", name="Start Practice", exact=True).click()
                page.wait_for_function("ids => JSON.stringify(window.QB.getState().activeSession?.questionIds)===JSON.stringify(ids)", arg=chapter["ids"])
                session_id = page.evaluate("window.QB.getState().activeSession.id")
                if name == "A":
                    page.evaluate("id => window.QB.toggleBookmark(id)", chapter["ids"][0])
                page.evaluate("args => window.QB.selectPractice(args.id,args.option)", {"id": chapter["ids"][0], "option": chapter["first"]})
                page.evaluate("window.QB.goIndex(1)")
                wrong = chapter["second"] % chapter["choices"] + 1
                page.evaluate("args => window.QB.selectPractice(args.id,args.option)", {"id": chapter["ids"][1], "option": wrong})
                page.evaluate("window.QB.goIndex(2)")
                page.evaluate("window.QB.openSessionReview()")
                page.locator("#nk-session-review").get_by_role("button", name="Pause", exact=True).click()
                page.wait_for_function("window.QB.getState().activeSession?.lifecycle==='paused'")
                snapshots[name] = page.evaluate("""id => {
                  const s=window.QB.getState(),cp=s.normalPracticeCheckpoints.find(x=>x.sessionId===id);
                  return {checkpoint:cp,attempts:Object.fromEntries(cp.sessionQuestionIds.slice(0,2).map(qid=>[qid,s.attempts[qid]||[]]))};
                }""", session_id)
                if snapshots[name]["checkpoint"]["sessionQuestionIds"] != chapter["ids"] or snapshots[name]["checkpoint"]["position"]["index"] != 2:
                    raise SystemExit(f"{name} lost ordered membership or index on Pause")
                if not all(snapshots[name]["checkpoint"]["submitted"].get(qid) for qid in chapter["ids"][:2]):
                    raise SystemExit(f"{name} lost answered progress on Pause")
                if not all(snapshots[name]["attempts"].get(qid) for qid in chapter["ids"][:2]):
                    raise SystemExit(f"{name} lost committed FSRS attempts on Pause")

            page.reload(wait_until="domcontentloaded")
            page.wait_for_function("window.QB && window.QB.getState().normalPracticeCheckpoints?.length>=3")
            page.locator("button.nk-home-focus-action").click()
            chooser = page.locator("#nk-practice-sessions")
            chooser.wait_for(state="visible")
            if chooser.locator(".nk-saved-practice-row").count() != 3:
                raise SystemExit("Reload did not show all three paused Practice sessions")
            chooser.screenshot(path=str(output / "three-paused-practice-phone.png"))
            page.set_viewport_size({"width": 320, "height": 640})
            chooser.screenshot(path=str(output / "three-paused-practice-small-phone.png"))
            small_chooser = chooser.evaluate("""dialog => {
              const row=dialog.querySelector('.nk-saved-practice-row');
              const actions=[...row.querySelectorAll('button')].map(button=>button.getBoundingClientRect());
              return {dialogFits:dialog.scrollWidth<=dialog.clientWidth,
                pageFits:document.documentElement.scrollWidth<=innerWidth,
                actionsFit:actions.length===2 && actions.every(rect=>rect.width>=44 && rect.left>=0 && rect.right<=innerWidth)};
            }""")
            if not all(small_chooser.values()):
                raise SystemExit(f"Paused Practice chooser overflows at 320px: {small_chooser}")
            page.set_viewport_size({"width": 820, "height": 1180})
            chooser.screenshot(path=str(output / "three-paused-practice-tablet.png"))
            page.set_viewport_size({"width": 390, "height": 844})
            chooser.locator(f'.nk-saved-practice-row[data-session-id="{snapshots["B"]["checkpoint"]["sessionId"]}"]').get_by_role("button", name="Resume", exact=True).click()
            page.wait_for_function("id => window.QB.getState().activeSession?.id===id", arg=snapshots["B"]["checkpoint"]["sessionId"])
            resumed_b = page.evaluate("""() => {const s=window.QB.getState().activeSession;return {ids:s.questionIds,index:s.index,answers:s.answers,submitted:s.submitted,pending:s.pendingRating};}""")
            saved_b = snapshots["B"]["checkpoint"]
            if resumed_b["ids"] != saved_b["sessionQuestionIds"] or resumed_b["index"] != 2 or resumed_b["answers"] != saved_b["answers"] or resumed_b["submitted"] != saved_b["submitted"] or resumed_b["pending"] != saved_b["pendingFsrsRatings"]:
                raise SystemExit(f"B resumed with the wrong identity or progress: {resumed_b}")
            other_before = page.evaluate("""ids => ids.map(id=>JSON.stringify(window.QB.getState().normalPracticeCheckpoints.find(cp=>cp.sessionId===id)))""", [snapshots["A"]["checkpoint"]["sessionId"], snapshots["C"]["checkpoint"]["sessionId"]])
            page.evaluate("window.dispatchEvent(new PageTransitionEvent('pagehide'))")
            other_after = page.evaluate("""ids => ids.map(id=>JSON.stringify(window.QB.getState().normalPracticeCheckpoints.find(cp=>cp.sessionId===id)))""", [snapshots["A"]["checkpoint"]["sessionId"], snapshots["C"]["checkpoint"]["sessionId"]])
            if other_after != other_before:
                raise SystemExit("pagehide while B was active altered A or C")
            page.evaluate("window.QB.openSessionReview()")
            page.locator("#nk-session-review").get_by_role("button", name="Pause", exact=True).click()
            page.evaluate("window.QB.startLibrary('bookmarks')")
            page.wait_for_function("window.QB.getState().activeSession?.originRoute==='bookmarks'")
            page.evaluate("window.QB.endSession()")
            page.wait_for_function("window.QB.getState().activeSession===null")
            bc_before = page.evaluate("""ids => ids.map(id=>JSON.stringify(window.QB.getState().normalPracticeCheckpoints.find(cp=>cp.sessionId===id)))""", [snapshots["B"]["checkpoint"]["sessionId"], snapshots["C"]["checkpoint"]["sessionId"]])
            page.evaluate("window.QB.nav('dashboard')")
            page.locator("button.nk-home-focus-action").click()
            page.locator(f'#nk-practice-sessions .nk-saved-practice-row[data-session-id="{snapshots["A"]["checkpoint"]["sessionId"]}"]').get_by_role("button", name="Resume", exact=True).click()
            page.evaluate("window.QB.openSessionReview()")
            page.locator("#nk-session-review").get_by_role("button", name="Submit", exact=True).click()
            page.wait_for_function("window.QB.getState().activeSession===null")
            bc_after = page.evaluate("""ids => ids.map(id=>JSON.stringify(window.QB.getState().normalPracticeCheckpoints.find(cp=>cp.sessionId===id)))""", [snapshots["B"]["checkpoint"]["sessionId"], snapshots["C"]["checkpoint"]["sessionId"]])
            if bc_after != bc_before:
                raise SystemExit("Completing A changed B or C")
            page.evaluate("window.QB.nav('dashboard')")
            page.locator("button.nk-home-focus-action").click()
            page.locator(f'#nk-practice-sessions .nk-saved-practice-row[data-session-id="{snapshots["C"]["checkpoint"]["sessionId"]}"]').get_by_role("button", name="Resume", exact=True).click()
            page.wait_for_function("id => window.QB.getState().activeSession?.id===id", arg=snapshots["C"]["checkpoint"]["sessionId"])
            double_pause = page.evaluate("""() => {const first=window.QB.nkPausePractice(),before=JSON.stringify(window.QB.getState().normalPracticeCheckpoints);const second=window.QB.nkPausePractice();return {first,second,unchanged:before===JSON.stringify(window.QB.getState().normalPracticeCheckpoints)};}""")
            if double_pause != {"first": True, "second": True, "unchanged": True}:
                raise SystemExit(f"Double Pause was not idempotent: {double_pause}")
            page.locator("button.nk-home-focus-action").click()
            page.locator(f'#nk-practice-sessions .nk-saved-practice-row[data-session-id="{snapshots["B"]["checkpoint"]["sessionId"]}"]').get_by_role("button", name="Discard", exact=True).click()
            remaining = page.evaluate("""() => window.QB.getState().normalPracticeCheckpoints.filter(cp=>!['submitted','completed','discarded'].includes(cp.lifecycle)).map(cp=>cp.sessionId)""")
            if remaining != [snapshots["C"]["checkpoint"]["sessionId"]]:
                raise SystemExit(f"Discarding B changed another saved Practice: {remaining}")
            print("THREE_PAUSED_PRACTICE_BROWSER_OK reload=true resume_B=true special_mode=true complete_A=true resume_C=true discard_B=true pagehide=true double_pause=true")
            context.close()

            # Two saved chapters leave exactly one checkpoint after submitting A.
            # Opening Review Solutions for A must not trap Home Continue behind
            # the read-only review session when the learner returns to Home.
            context = browser.new_context(viewport={"width": 390, "height": 844}, service_workers="block", reduced_motion="reduce")
            page = context.new_page()
            page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(origin) else route.abort())
            page.goto(origin + "/#dashboard", wait_until="domcontentloaded")
            page.wait_for_function("window.QB && window.QB.getState")
            two_ids = []
            for chapter in chapters[:2]:
                page.evaluate("c => window.QB.nkOpenSubjectChapter(c.subject,c.bank,c.id)", chapter)
                page.locator(".nk-chapter-actions button.is-primary").click()
                page.locator("#modal").get_by_role("button", name="Start Practice", exact=True).click()
                page.wait_for_function("ids => JSON.stringify(window.QB.getState().activeSession?.questionIds)===JSON.stringify(ids)", arg=chapter["ids"])
                two_ids.append(page.evaluate("window.QB.getState().activeSession.id"))
                page.evaluate("window.QB.openSessionReview()")
                page.locator("#nk-session-review").get_by_role("button", name="Pause", exact=True).click()
                page.wait_for_function("window.QB.getState().activeSession?.lifecycle==='paused'")
            page.locator("button.nk-home-focus-action").click()
            page.locator(f'#nk-practice-sessions .nk-saved-practice-row[data-session-id="{two_ids[0]}"]').get_by_role("button", name="Resume", exact=True).click()
            page.wait_for_function("id => window.QB.getState().activeSession?.id===id", arg=two_ids[0])
            page.evaluate("window.QB.openSessionReview()")
            page.locator("#nk-session-review").get_by_role("button", name="Submit", exact=True).click()
            page.wait_for_function("window.QB.getState().activeSession===null")
            saved_after_submit = page.evaluate("""() => window.QB.getState().normalPracticeCheckpoints
              .filter(cp=>!['submitted','completed','discarded'].includes(cp.lifecycle)).map(cp=>cp.sessionId)""")
            if saved_after_submit != [two_ids[1]]:
                raise SystemExit(f"Submitting A changed the saved B checkpoint: {saved_after_submit}")
            submitted_test_id = page.evaluate("window.QB.getState().tests.at(-1).id")
            page.evaluate("window.QB.nav('dashboard')")
            page.locator("button.nk-home-focus-action").click()
            if page.evaluate("window.QB.getState().activeSession?.id") != two_ids[1]:
                raise SystemExit("Home Continue could not resume B directly after submitting A")
            page.evaluate("window.QB.openSessionReview()")
            page.locator("#nk-session-review").get_by_role("button", name="Pause", exact=True).click()
            page.wait_for_function("window.QB.getState().activeSession?.lifecycle==='paused'")
            page.evaluate("id => window.QB.reviewTest(id)", submitted_test_id)
            page.wait_for_function("window.QB.getState().activeSession?.mode==='review'")
            page.evaluate("window.QB.nav('dashboard')")
            page.locator("button.nk-home-focus-action").click()
            resumed_after_review = page.evaluate("""() => ({id:window.QB.getState().activeSession?.id,
              mode:window.QB.getState().activeSession?.mode,
              saved:window.QB.getState().normalPracticeCheckpoints.filter(cp=>!['submitted','completed','discarded'].includes(cp.lifecycle)).map(cp=>cp.sessionId)})""")
            if resumed_after_review["id"] != two_ids[1] or resumed_after_review["mode"] != "practice" or resumed_after_review["saved"] != [two_ids[1]]:
                raise SystemExit(f"Home Continue could not resume B after submitting/reviewing A: {resumed_after_review}")
            print("TWO_PAUSED_AFTER_SUBMIT_BROWSER_OK remaining_B=true direct_home_resume=true review_exit=true home_resume=true")
            context.close()

            # FSRS lifecycle regression: real answers are committed when Pause
            # leaves the question flow, while untouched questions remain unseen.
            context = browser.new_context(viewport={"width": 390, "height": 844}, service_workers="block")
            page = context.new_page()
            page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(origin) else route.abort())
            page.goto(origin + "/#dashboard", wait_until="domcontentloaded")
            page.wait_for_function("window.QB && window.QB.getState")
            page.evaluate("window.QB.startAllPractice()")
            page.wait_for_function("window.QB.getState().activeSession?.questionIds?.length > 4")
            lifecycle_ids = page.evaluate("[...window.QB.getState().activeSession.questionIds]")
            answered = lifecycle_ids[:4]
            untouched = lifecycle_ids[4:]
            lifecycle_session_id = page.evaluate("window.QB.getState().activeSession.id")
            page.evaluate("id => window.QB.toggleBookmark(id)", answered[0])
            for index, qid in enumerate(answered):
                correct = page.evaluate("""qid => {
                  const all=[...(window.QBANK_DATA?.questions||[]),...((window.SUBJECT_QBANK_DATA?.subjects||[]).flatMap(x=>x.questions||[]))];
                  return Number(all.find(q=>String(q.id)===String(qid))?.correctOption||0);
                }""", qid)
                if not correct:
                    raise SystemExit(f"Could not resolve canonical correctOption for lifecycle question {qid}")
                page.evaluate("i => window.QB.goIndex(i)", index)
                page.evaluate("args => window.QB.selectPractice(args.id,args.correct)", {"id": qid, "correct": correct})

            # Navigate past an unanswered question without creating an attempt.
            page.evaluate("window.QB.goIndex(5)")
            page.evaluate("window.QB.openSessionReview()")
            page.locator("#nk-session-review").get_by_role("button", name="Pause", exact=True).click()
            page.wait_for_function("window.QB.getState().activeSession?.lifecycle==='paused'")
            paused_fsrs = page.evaluate("""({answered,untouched}) => {
              const state=window.QB.getState();
              return {
                attempts:Object.fromEntries(answered.map(id=>[id,(state.attempts[id]||[]).length])),
                reviews:Object.fromEntries(answered.map(id=>[id,Boolean(state.reviews[id]?.schemaVersion===2)])),
                untouchedAttempts:untouched.filter(id=>(state.attempts[id]||[]).length),
                untouchedReviews:untouched.filter(id=>state.reviews[id]),
                untouchedEligible:untouched.filter(id=>state.fsrsReviewEligible?.[id])
              };
            }""", {"answered": answered, "untouched": untouched})
            if not all(count == 1 for count in paused_fsrs["attempts"].values()) or not all(paused_fsrs["reviews"].values()):
                raise SystemExit(f"Answered questions did not enter FSRS when Practice paused: {paused_fsrs}")
            if paused_fsrs["untouchedAttempts"] or paused_fsrs["untouchedReviews"] or paused_fsrs["untouchedEligible"]:
                raise SystemExit(f"Pause introduced untouched questions into FSRS: {paused_fsrs}")

            storage = context.storage_state()
            context.close()
            context = browser.new_context(viewport={"width": 390, "height": 844}, service_workers="block", storage_state=storage)
            page = context.new_page()
            page.route("**/*", lambda route: route.continue_() if route.request.url.startswith(origin) else route.abort())
            page.goto(origin + "/#dashboard", wait_until="domcontentloaded")
            page.wait_for_function("window.QB && window.QB.getState().activeSession?.lifecycle==='paused'")
            page.locator("button.nk-home-focus-action").click()
            page.wait_for_function("window.QB.getState().activeSession?.lifecycle==='active'")
            restored = page.evaluate("""id => {
              const st=window.QB.getState(),s=st.activeSession;
              return {id:s.id,ids:s.questionIds,index:s.index,bookmark:Boolean(st.bookmarks[id])};
            }""", answered[0])
            if restored != {"id": lifecycle_session_id, "ids": lifecycle_ids, "index": 5, "bookmark": True}:
                raise SystemExit(f"Real-answer lifecycle restart lost state: {restored}")
            # A stale/expired submitted flag without a selected answer must not
            # prevent final submission from recording the question as skipped.
            page.evaluate("id => window.QB.getState().activeSession.submitted[id]=true", untouched[0])
            page.evaluate("window.QB.openSessionReview()")
            page.locator("#nk-session-review").get_by_role("button", name="Submit", exact=True).click()
            page.wait_for_function("!window.QB.getState().activeSession")
            submitted_skips = page.evaluate("""untouched => {
              const state=window.QB.getState();
              return untouched.filter(id=>state.fsrsReviewEligible?.[id]?.reason==='skipped');
            }""", untouched)
            if submitted_skips != untouched:
                raise SystemExit(f"Final submission did not add every unanswered question to FSRS: {submitted_skips}")

            # Complete the daily loop through Analysis and the read-only Review
            # surface, including Previous/Next, the grid, and End Review.
            review_baseline = page.evaluate("JSON.stringify([window.QB.getState().attempts,window.QB.getState().reviews,window.QB.getState().tests,window.QB.getState().fsrsReviewEligible])")
            analysis = page.get_by_role("button", name="Review Solutions", exact=True)
            analysis.wait_for(state="visible")
            analysis.click()
            page.wait_for_function("window.QB.getState().activeSession?.mode==='review'")
            review_session_id = page.evaluate("window.QB.getState().activeSession.id")
            page.get_by_role("button", name="Next", exact=True).click()
            page.get_by_role("button", name="Previous", exact=True).click()
            if page.evaluate("window.QB.getState().activeSession.id") != review_session_id:
                raise SystemExit("Review Previous/Next replaced the read-only review session")
            page.locator("#cr-grid").click()
            navigator = page.locator("#qb-question-navigator")
            navigator.wait_for(state="visible")
            navigator.get_by_role("button", name="End Review", exact=True).click()
            page.wait_for_function("!window.QB.getState().activeSession")
            if "result" not in page.url:
                raise SystemExit(f"End Review returned to an invalid target: {page.url}")
            page.evaluate("window.QB.nav('dashboard')")
            page.wait_for_url("**/#dashboard")
            if page.evaluate("JSON.stringify([window.QB.getState().attempts,window.QB.getState().reviews,window.QB.getState().tests,window.QB.getState().fsrsReviewEligible])") != review_baseline:
                raise SystemExit("Read-only Review mutated attempts, results, or FSRS state")
            context.close()
            browser.close()
    finally:
        server.shutdown()

    print("CONTINUE_PRACTICE_BROWSER_OK viewports=320x844,390x844,820x1180 navigation_smoke=true browser_back=true single_review_grid=true footer=previous_next restart_resume=true home_continue=true real_practice_session=true saved_index=4 bookmark_persisted=true fsrs_pause_boundary=true submit_skips=true analysis_review_loop=true")


if __name__ == "__main__":
    main()
