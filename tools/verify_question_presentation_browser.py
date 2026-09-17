#!/usr/bin/env python3
"""Exercise normalized matching and structured row questions through the generated learner UI."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    web = ROOT / "build/web"
    html = (web / "index.html").read_text(encoding="utf-8")
    for marker in ("NK_QUESTION_PRESENTATION_V1_START", "nk-question-presentation-v1"):
        if marker not in html:
            raise SystemExit(f"Question presentation layer missing from built PWA: {marker}")

    state_export = "getState:()=>state,"
    if html.count(state_export) != 1:
        raise SystemExit("Expected one generated QB state export for the read-only question probe")
    html = html.replace(state_export, state_export + "__presentationQuestion:id=>BY_ID[id],", 1)

    output = ROOT / "build/ui-checks"
    output.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(web)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    origin = f"http://127.0.0.1:{server.server_port}"
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            context = browser.new_context(viewport={"width": 390, "height": 844}, service_workers="block", reduced_motion="reduce")
            page = context.new_page()
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            def serve(route):
                if route.request.url == origin + "/":
                    route.fulfill(status=200, content_type="text/html", body=html)
                elif route.request.url.startswith(origin):
                    route.continue_()
                else:
                    route.abort()
            page.route("**/*", serve)
            page.goto(origin + "/#dashboard", wait_until="domcontentloaded")
            page.wait_for_function("window.QB && window.QB.getState")

            page.locator("button.nk-v3-subject-card").filter(has_text="Physiology").click()
            page.locator("button.nk-bank-card").filter(has_text="PrepLadder").click()
            page.evaluate("window.QB.practiceOne('physiology-9-6')")
            nerve_session = page.evaluate("""() => {
                const s = window.QB.getState().activeSession;
                return {mode: s?.mode, id: s?.questionIds?.[s.index]};
            }""")
            if nerve_session != {"mode": "practice", "id": "physiology-9-6"}:
                raise SystemExit(f"Nerve-fibre Practice opened the wrong stable question: {nerve_session!r}")
            nerve_choices = [
                "1-d, 2-b, 3-c, 4-a",
                "1-a, 2-b, 3-d, 4-c",
                "1-b, 2-a, 3-c, 4-d",
                "1-c, 2-d, 3-b, 4-a",
            ]
            nerve_canonical = page.evaluate("""() => {
                const s = window.QB.getState().activeSession;
                const q = window.QB.__presentationQuestion(s.questionIds[s.index]);
                return {id: q.id, correctOption: q.correctOption,
                    letters: q.options.map(option => option.letter),
                    choices: q.options.map(option => option.text)};
            }""")
            if nerve_canonical != {"id": "physiology-9-6", "correctOption": 1,
                                   "letters": ["A", "B", "C", "D"], "choices": nerve_choices}:
                raise SystemExit(f"Nerve-fibre canonical answer contract changed: {nerve_canonical!r}")
            nerve_table = page.locator(".question-text table.nk-match-table")
            nerve_table.wait_for(state="visible")
            page.screenshot(path=str(output / "prepladder-nerve-fibre-matching.png"), full_page=True)
            nerve_headers = [" ".join(value.split()).upper() for value in nerve_table.locator("thead th").all_inner_texts()]
            if nerve_headers != ["LIST I", "LIST II"]:
                raise SystemExit(f"Nerve-fibre table must contain exactly two lists: {nerve_headers!r}")
            nerve_rows = nerve_table.locator("tbody tr")
            if nerve_rows.count() != 4:
                raise SystemExit(f"Nerve-fibre table must contain exactly four rows: {nerve_rows.count()}")
            nerve_expected = [
                [("1", "Aα"), ("a", "Preganglionic autonomic")],
                [("2", "Aβ"), ("b", "Touch")],
                [("3", "Aδ"), ("c", "Temperature")],
                [("4", "B"), ("d", "Proprioception")],
            ]
            for index, expected_row in enumerate(nerve_expected):
                cells = nerve_rows.nth(index).locator("td")
                if cells.count() != 2:
                    raise SystemExit(f"Nerve-fibre row {index + 1} must contain two cells: {cells.count()}")
                for column, (label, value) in enumerate(expected_row):
                    cell = cells.nth(column)
                    text = cell.inner_text().strip()
                    if not text or any(dash in text for dash in ("—", "–", "-")):
                        raise SystemExit(f"Nerve-fibre row {index + 1} contains a dash/empty cell: {text!r}")
                    if cell.locator("b").all_inner_texts() != [label] or cell.locator("span").all_inner_texts() != [value]:
                        raise SystemExit(f"Nerve-fibre row {index + 1}, list {column + 1} lost {(label, value)!r}: {text!r}")
            nerve_options = page.locator(".option-list button")
            if nerve_options.count() != 4 or nerve_options.locator(".option-letter").all_inner_texts() != ["A", "B", "C", "D"] or nerve_options.locator(".option-text").all_inner_texts() != nerve_choices:
                raise SystemExit("Nerve-fibre question did not preserve exactly four ordered canonical choices")
            if page.locator(".option-list .correct, .option-list .wrong").count():
                raise SystemExit("Nerve-fibre Practice leaked correctness before answering")
            nerve_options.nth(1).click()
            page.locator(".option-list .wrong").wait_for(state="visible")
            nerve_answer = page.evaluate("""() => {
                const s = window.QB.getState().activeSession;
                const id = s.questionIds[s.index];
                return {id, answer: s.answers[id], submitted: s.submitted[id]};
            }""")
            if nerve_answer != {"id": "physiology-9-6", "answer": 2, "submitted": True}:
                raise SystemExit(f"Nerve-fibre Practice did not submit the selected canonical choice: {nerve_answer!r}")
            nerve_feedback = page.locator(".option-list .option")
            if nerve_feedback.locator(".option-text").all_inner_texts() != nerve_choices:
                raise SystemExit("Nerve-fibre choices changed order after answering")
            correct_indices = nerve_feedback.evaluate_all("nodes => nodes.flatMap((node, index) => node.classList.contains('correct') ? [index + 1] : [])")
            wrong_indices = nerve_feedback.evaluate_all("nodes => nodes.flatMap((node, index) => node.classList.contains('wrong') ? [index + 1] : [])")
            if correct_indices != [nerve_canonical["correctOption"]] or wrong_indices != [2]:
                raise SystemExit(f"Nerve-fibre canonical correctOption=1 did not govern answer CSS: correct={correct_indices!r} wrong={wrong_indices!r}")
            page.screenshot(path=str(output / "prepladder-nerve-fibre-matching.png"), full_page=True)

            page.evaluate("window.QB.practiceOne('physiology-1-13')")
            table = page.locator(".question-text .nk-match-table")
            table.wait_for(state="visible")
            headers = table.locator("th").all_inner_texts()
            normalized_headers = [" ".join(value.split()).upper() for value in headers]
            if normalized_headers != ["LIST I", "LIST II"]:
                raise SystemExit(f"Matching table headers are wrong: {headers!r}")
            visible = table.inner_text()
            for expected in ("Acetylcholine (ACh)", "Raphe nuclei", "Norepinephrine (NE)", "Locus ceruleus"):
                if expected not in visible:
                    raise SystemExit(f"Matching table lost source cell {expected!r}: {visible!r}")
            options = page.locator(".option-list button")
            if options.count() != 4:
                raise SystemExit(f"Extracted table rows leaked into clickable answers: count={options.count()}")
            if page.locator(".option-letter").all_inner_texts() != ["A", "B", "C", "D"]:
                raise SystemExit("Normalized answer labels are not one A–D sequence")
            option_text = page.locator(".option-text").all_inner_texts()
            if not all("-" in value for value in option_text):
                raise SystemExit(f"Visible choices are not the actual matching answers: {option_text!r}")
            options.nth(0).click()
            if page.locator(".option-list .correct").count() != 1:
                raise SystemExit("Normalized matching answer did not use the canonical correctOption")
            page.screenshot(path=str(output / "prepladder-matching-question.png"), full_page=True)

            page.evaluate("window.QB.practiceOne('physiology-9-17')")
            ion_table = page.locator(".question-text .nk-match-table")
            ion_table.wait_for(state="visible")
            ion_headers = ion_table.locator("th").all_inner_texts()
            if [" ".join(value.split()).upper() for value in ion_headers] != ["LIST I", "LIST II"]:
                raise SystemExit(f"Equilibrium-potential matching table headers are wrong: {ion_headers!r}")
            ion_visible = ion_table.inner_text()
            for expected in ("Sodium", "Chloride", "Potassium", "Calcium", "-70", "+63", "+132", "-90"):
                if expected not in ion_visible:
                    raise SystemExit(f"Equilibrium-potential matching table lost source cell {expected!r}: {ion_visible!r}")
            ion_question = page.locator(".question-text").inner_text()
            if ion_question.count("Ion Equilibrium Potential (mV)") != 1:
                raise SystemExit(f"Duplicated source table leaked into equilibrium-potential question: {ion_question!r}")
            if page.locator(".option-list button").count() != 4:
                raise SystemExit("Equilibrium-potential matching question does not expose exactly four canonical choices")
            page.screenshot(path=str(output / "prepladder-equilibrium-potential-matching.png"), full_page=True)

            page.evaluate("window.QB.practiceOne('physiology-9-22')")
            transport_table = page.locator(".question-text .nk-match-table")
            transport_table.wait_for(state="visible")
            transport_headers = [" ".join(value.split()).upper() for value in transport_table.locator("th").all_inner_texts()]
            if transport_headers != ["STATEMENT", "TYPE", "DIRECTION", "MEDIATOR"]:
                raise SystemExit(f"Axonal-transport table headers are wrong: {transport_headers!r}")
            transport_visible = transport_table.inner_text()
            for expected in ("1", "2", "3", "4", "Anterograde", "Retrograde", "Cell body to axon terminal", "Axon terminal to cell body", "Dynein", "Kinesin"):
                if expected not in transport_visible:
                    raise SystemExit(f"Axonal-transport table lost source cell {expected!r}: {transport_visible!r}")
            if transport_visible.count("Anterograde") != 2 or transport_visible.count("Retrograde") != 2:
                raise SystemExit(f"Duplicated axonal-transport source rows leaked into learner table: {transport_visible!r}")
            transport_options = page.locator(".option-list button")
            if transport_options.count() != 4 or page.locator(".option-text").all_inner_texts() != ["1", "2", "3", "4"]:
                raise SystemExit("Axonal-transport question did not preserve its four canonical row-number choices")
            transport_options.nth(2).click()
            if page.locator(".option-list .correct").count() != 1:
                raise SystemExit("Axonal-transport table did not preserve canonical correct option 3")
            page.screenshot(path=str(output / "prepladder-axonal-transport-table.png"), full_page=True)

            page.evaluate("window.QB.practiceOne('physiology-19-12')")
            statements = page.locator(".question-text .nk-match-table")
            statements.wait_for(state="visible")
            statement_headers = statements.locator("th").all_inner_texts()
            if [" ".join(value.split()).upper() for value in statement_headers] != ["STATEMENTS"]:
                raise SystemExit(f"Combination-question labels were not presented as a statement list: {statement_headers!r}")
            statement_text = statements.inner_text()
            for expected in ("Liver", "Kidney", "Muscle", "Heart"):
                if expected not in statement_text:
                    raise SystemExit(f"Combination question lost statement {expected!r}: {statement_text!r}")
            if page.locator(".option-list button").count() != 4:
                raise SystemExit("Combination question does not expose exactly four canonical choices")

            page.evaluate("window.QB.nkOpenSubjectLibrary('Biochemistry')")
            page.locator("button.nk-bank-card").filter(has_text="PrepLadder").click()
            page.locator("button.nk-topic-row").first.wait_for(state="visible")
            page.evaluate("window.QB.practiceOne('22-8')")
            exponent_text = page.locator(".question-text sup.nk-sci-sup").all_inner_texts()
            if exponent_text != ["6", "9"]:
                raise SystemExit(f"Caret exponents did not render semantically in the question stem: {exponent_text!r}")

            page.evaluate("window.QB.practiceOne('17-1')")
            magnesium = page.locator(".option-text").nth(3)
            magnesium.locator("sup.nk-sci-sup").wait_for(state="visible")
            if magnesium.locator("sup.nk-sci-sup").inner_text() != "2+" or "■" in magnesium.inner_text():
                raise SystemExit(f"Safe ionic OCR notation was not repaired in an answer choice: {magnesium.inner_text()!r}")
            # PrepLadder explanations deliberately use original source-PDF pages;
            # exercise the native enhanced-text explanation path with Marrow.
            page.evaluate("window.QB.nkOpenSubjectLibrary('Physiology')")
            page.locator("button.nk-bank-card").filter(has_text="Marrow").click()
            page.locator("button.nk-topic-row").first.wait_for(state="visible")

            page.evaluate("window.QB.practiceOne('marrow__PHYS_CH09_Q007')")
            page.locator(".option-list button").first.click()
            page.locator(".feedback-body").wait_for(state="visible")
            feedback_superscripts = page.locator(".feedback-body sup.nk-sci-sup").all_inner_texts()
            if "2+" not in feedback_superscripts:
                raise SystemExit(f"Scientific notation did not reach the native explanation renderer: {feedback_superscripts!r}")

            page.evaluate("window.QB.nkOpenSubjectLibrary('Biochemistry')")
            page.locator("button.nk-bank-card").filter(has_text="PrepLadder").click()
            page.locator("button.nk-topic-row").first.wait_for(state="visible")
            page.evaluate("window.QB.practiceOne('28-3')")
            acid_base = page.locator(".question-text")
            acid_base_subscripts = acid_base.locator("sub.nk-sci-sub").all_inner_texts()
            acid_base_superscripts = acid_base.locator("sup.nk-sci-sup").all_inner_texts()
            if acid_base_subscripts != ["2", "3"] or acid_base_superscripts != ["−"]:
                raise SystemExit(
                    "Blood-gas notation did not render as pCO₂ / HCO₃⁻: "
                    f"sub={acid_base_subscripts!r} sup={acid_base_superscripts!r}"
                )
            if "■" in acid_base.inner_text():
                raise SystemExit("A safely recoverable OCR placeholder remained in the blood-gas stem")
            page.screenshot(path=str(output / "scientific-notation-question.png"), full_page=True)

            page.evaluate("window.QB.nkOpenSubjectLibrary('Physiology')")
            page.locator("button.nk-bank-card").filter(has_text="PrepLadder").click()
            page.locator("button.nk-topic-row").first.wait_for(state="visible")
            page.evaluate("window.QB.practiceOne('physiology-24-6')")
            page.locator(".nk-question-unavailable").wait_for(state="visible")
            if page.locator(".option-list button").count():
                raise SystemExit("Incomplete source choices remained answerable")
            if "answering is disabled" not in page.locator(".nk-question-unavailable").inner_text().lower():
                raise SystemExit("Incomplete source record lacks a clear fail-closed explanation")
            if errors:
                raise SystemExit("Browser JavaScript errors during question presentation regression: " + " | ".join(errors))
            context.close()
            browser.close()
    finally:
        server.shutdown()

    print("QUESTION_PRESENTATION_BROWSER_OK nerve_fibre_matching=true matching_table=true alternate_matching_table=true row_selection_table=true combination_list=true scientific_stem=true scientific_options=true scientific_explanations=true choices=4 incomplete_fail_closed=true")


if __name__ == "__main__":
    main()
