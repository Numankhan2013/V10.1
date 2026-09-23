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

            def open_practice(question_id):
                # Presentation checks must stay hermetic: with multiple paused
                # chapters supported, repeated practiceOne calls would otherwise
                # accumulate saved sessions. Reset Practice state first so each
                # presentation check starts fresh (the multi-pause accumulation
                # behavior itself is covered by verify_continue_practice_browser).
                page.evaluate("""() => {
                    const s = window.QB.getState();
                    s.activeSession = null;
                    s.normalPracticeCheckpoints = [];
                    s.normalPracticeCheckpoint = null;
                }""")
                page.evaluate("id => window.QB.practiceOne(id)", question_id)
                replacement = page.locator("#nk-practice-replacement")
                if replacement.count() and replacement.is_visible():
                    replacement.get_by_role(
                        "button", name="Discard and start new", exact=True
                    ).click()
                page.wait_for_function(
                    """id => {
                        const session=window.QB.getState().activeSession;
                        return session?.questionIds?.[session.index]===id;
                    }""",
                    arg=question_id,
                    timeout=5000,
                )
                # Same-route session replacement updates state synchronously;
                # explicitly exercise the app's same-route render path before
                # inspecting presentation markup.
                page.evaluate("window.QB.nav('practice')")

            page.locator("button.nk-v3-subject-card").filter(has_text="Physiology").click()
            page.locator("button.nk-bank-card").filter(has_text="PrepLadder").click()
            open_practice("physiology-9-6")
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

            open_practice("physiology-1-13")
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

            open_practice("physiology-9-17")
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

            open_practice("physiology-9-22")
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

            open_practice("physiology-19-12")
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
            open_practice("4-3")
            glucose_prompt = "Which of the following tissues is unable to transport glucose independently of insulin?"
            glucose_choices = ["Hepatocytes", "Cardiac muscle", "RBC", "Neurons"]
            glucose_canonical = page.evaluate("""() => {
                const s = window.QB.getState().activeSession;
                const q = window.QB.__presentationQuestion(s.questionIds[s.index]);
                return {mode: s.mode, id: q.id, question: q.question, correctOption: q.correctOption,
                    sourcePage: q.sourcePage, sourcePageEnd: q.sourcePageEnd,
                    letters: q.options.map(option => option.letter), choices: q.options.map(option => option.text)};
            }""")
            if glucose_canonical != {"mode": "practice", "id": "4-3",
                                    "question": "GLUT3 c) Erythrocytes\n4.GLUT4 d) Skeletal Muscle",
                                    "correctOption": 2, "sourcePage": 82, "sourcePageEnd": 82,
                                    "letters": ["A", "B", "C", "D"], "choices": glucose_choices}:
                raise SystemExit(f"Biochemistry 4-3 canonical record changed: {glucose_canonical!r}")
            glucose_stem = page.locator(".question-text .nk-question-prompt")
            glucose_stem.wait_for(state="visible")
            if glucose_stem.count() != 1 or glucose_stem.inner_text() != glucose_prompt:
                raise SystemExit(f"Biochemistry 4-3 source prompt missing: {glucose_stem.all_inner_texts()!r}")
            if page.locator(".question-text table, .question-text .nk-question-unavailable").count():
                raise SystemExit("Biochemistry 4-3 invented a table or disabled valid choices")
            if any(fragment in page.locator(".question-text").inner_text() for fragment in
                   ("GLUT3", "Erythrocytes", "GLUT4", "Skeletal Muscle")):
                raise SystemExit("Biochemistry 4-3 leaked the preceding question fragment")
            glucose_options = page.locator(".option-list button")
            if glucose_options.count() != 4 or glucose_options.locator(".option-text").all_inner_texts() != glucose_choices or glucose_options.locator(".option-letter").all_inner_texts() != ["A", "B", "C", "D"]:
                raise SystemExit("Biochemistry 4-3 lost its four ordered canonical choices")
            if any(not glucose_options.nth(index).is_enabled() for index in range(4)):
                raise SystemExit("Biochemistry 4-3 choices are not enabled")
            if page.locator(".option-list .correct, .option-list .wrong").count():
                raise SystemExit("Biochemistry 4-3 leaked correctness before answering")
            glucose_options.nth(1).click()
            page.locator(".option-list .correct").wait_for(state="visible")
            glucose_answer = page.evaluate("""() => {
                const s = window.QB.getState().activeSession;
                const id = s.questionIds[s.index];
                return {id, answer: s.answers[id], submitted: s.submitted[id],
                    correctOption: window.QB.__presentationQuestion(id).correctOption};
            }""")
            if glucose_answer != {"id": "4-3", "answer": 2, "submitted": True, "correctOption": 2}:
                raise SystemExit(f"Biochemistry 4-3 answer contract changed: {glucose_answer!r}")
            correct_indices = page.locator(".option-list .option").evaluate_all(
                "nodes => nodes.flatMap((node, index) => node.classList.contains('correct') ? [index + 1] : [])")
            if correct_indices != [2] or page.locator(".option-list .wrong").count() or page.locator(".option-list .option-text").all_inner_texts() != glucose_choices or glucose_stem.inner_text() != glucose_prompt:
                raise SystemExit("Biochemistry 4-3 post-answer presentation changed")
            page.screenshot(path=str(output / "prepladder-biochemistry-4-3-stem.png"), full_page=True)
            print("BIOCHEM_4_3_BROWSER_OK exact_prompt=true choices=4 canonical_answer=2")

            open_practice("5-10")
            glycogen_raw = ("Which of the following statements is true on the structure of glycogen?\n"
                            "Arranged in 12 concentric layers Glucose residues are connected by ■-1,4 linkage\n"
                            "Branching points formed by α-1,6 linkage")
            glycogen_prompt = glycogen_raw.replace("■", "α")
            glycogen_choices = ["1,2", "2,3", "1,2,3", "1,3"]
            glycogen_canonical = page.evaluate("""() => {
                const s = window.QB.getState().activeSession;
                const q = window.QB.__presentationQuestion(s.questionIds[s.index]);
                return {mode: s.mode, id: q.id, question: q.question, correctOption: q.correctOption,
                    sourcePage: q.sourcePage, sourcePageEnd: q.sourcePageEnd,
                    letters: q.options.map(option => option.letter), choices: q.options.map(option => option.text)};
            }""")
            if glycogen_canonical != {"mode": "practice", "id": "5-10", "question": glycogen_raw,
                                     "correctOption": 3, "sourcePage": 101, "sourcePageEnd": 101,
                                     "letters": ["A", "B", "C", "D"], "choices": glycogen_choices}:
                raise SystemExit(f"Biochemistry 5-10 canonical record changed: {glycogen_canonical!r}")
            glycogen_stem = page.locator(".question-text .nk-question-prompt")
            glycogen_stem.wait_for(state="visible")
            if glycogen_stem.count() != 1 or glycogen_stem.text_content() != glycogen_prompt or "\u25a0" in glycogen_stem.inner_text():
                raise SystemExit(f"Biochemistry 5-10 linkage repair missing: {glycogen_stem.all_text_contents()!r}")
            if "Glucose residues are connected by α-1,4 linkage" not in glycogen_stem.inner_text():
                raise SystemExit("Biochemistry 5-10 restored linkage is not learner-visible")
            if page.locator(".question-text table, .question-text .nk-question-unavailable").count():
                raise SystemExit("Biochemistry 5-10 invented a table or disabled valid choices")
            glycogen_options = page.locator(".option-list button")
            if glycogen_options.count() != 4 or glycogen_options.locator(".option-text").all_inner_texts() != glycogen_choices or glycogen_options.locator(".option-letter").all_inner_texts() != ["A", "B", "C", "D"]:
                raise SystemExit("Biochemistry 5-10 lost its four ordered canonical choices")
            if any(not glycogen_options.nth(index).is_enabled() for index in range(4)):
                raise SystemExit("Biochemistry 5-10 choices are not enabled")
            if page.locator(".option-list .correct, .option-list .wrong").count():
                raise SystemExit("Biochemistry 5-10 leaked correctness before answering")
            glycogen_options.nth(2).click()
            page.locator(".option-list .correct").wait_for(state="visible")
            glycogen_answer = page.evaluate("""() => {
                const s = window.QB.getState().activeSession;
                const id = s.questionIds[s.index];
                return {id, answer: s.answers[id], submitted: s.submitted[id],
                    correctOption: window.QB.__presentationQuestion(id).correctOption};
            }""")
            if glycogen_answer != {"id": "5-10", "answer": 3, "submitted": True, "correctOption": 3}:
                raise SystemExit(f"Biochemistry 5-10 answer contract changed: {glycogen_answer!r}")
            correct_indices = page.locator(".option-list .option").evaluate_all(
                "nodes => nodes.flatMap((node, index) => node.classList.contains('correct') ? [index + 1] : [])")
            if correct_indices != [3] or page.locator(".option-list .wrong").count() or page.locator(".option-list .option-text").all_inner_texts() != glycogen_choices or glycogen_stem.text_content() != glycogen_prompt or "\u25a0" in glycogen_stem.inner_text():
                raise SystemExit("Biochemistry 5-10 post-answer presentation changed")
            page.screenshot(path=str(output / "prepladder-biochemistry-5-10-stem.png"), full_page=True)
            print("BIOCHEM_5_10_BROWSER_OK exact_prompt=true no_square=true choices=4 canonical_answer=3")

            open_practice("5-14")
            phosphorylase_raw = "Glycogen phosphorylase cleaves ■-1,4 linkages"
            phosphorylase_fixed = "Glycogen phosphorylase cleaves α-1,4 linkages"
            phosphorylase_choices = ["Glucose-6-phosphatase acts in liver", phosphorylase_fixed,
                                     "Phosphoglucomutase converts glucose-1-phosphate into glucose-6-phosphate",
                                     "Glycogenolysis is the reverse process of glycogenesis."]
            phosphorylase_stem = page.locator(".question-text .nk-question-prompt")
            phosphorylase_stem.wait_for(state="visible")
            if phosphorylase_stem.count() != 1 or "false regarding glycogenolysis" not in phosphorylase_stem.inner_text():
                raise SystemExit(f"Biochemistry 5-14 stem missing: {phosphorylase_stem.all_text_contents()!r}")
            if page.locator(".question-text table, .question-text .nk-question-unavailable").count():
                raise SystemExit("Biochemistry 5-14 invented a table or disabled valid choices")
            phosphorylase_options = page.locator(".option-list button")
            if phosphorylase_options.count() != 4 or phosphorylase_options.locator(".option-text").all_inner_texts() != phosphorylase_choices or phosphorylase_options.locator(".option-letter").all_inner_texts() != ["A", "B", "C", "D"]:
                raise SystemExit(f"Biochemistry 5-14 option repair missing: {phosphorylase_options.locator('.option-text').all_inner_texts()!r}")
            if "\u25a0" in page.locator(".option-list").inner_text():
                raise SystemExit("Biochemistry 5-14 dark-block placeholder remains learner-visible")
            if any(not phosphorylase_options.nth(index).is_enabled() for index in range(4)):
                raise SystemExit("Biochemistry 5-14 choices are not enabled")
            if page.locator(".option-list .correct, .option-list .wrong").count():
                raise SystemExit("Biochemistry 5-14 leaked correctness before answering")
            phosphorylase_options.nth(3).click()
            page.locator(".option-list .correct").wait_for(state="visible")
            phosphorylase_answer = page.evaluate("""() => {
                const s = window.QB.getState().activeSession;
                const id = s.questionIds[s.index];
                return {id, answer: s.answers[id], submitted: s.submitted[id],
                    correctOption: window.QB.__presentationQuestion(id).correctOption};
            }""")
            if phosphorylase_answer != {"id": "5-14", "answer": 4, "submitted": True, "correctOption": 4}:
                raise SystemExit(f"Biochemistry 5-14 answer contract changed: {phosphorylase_answer!r}")
            phosphorylase_correct = page.locator(".option-list .option").evaluate_all(
                "nodes => nodes.flatMap((node, index) => node.classList.contains('correct') ? [index + 1] : [])")
            if phosphorylase_correct != [4] or page.locator(".option-list .wrong").count() or page.locator(".option-list .option-text").all_inner_texts() != phosphorylase_choices:
                raise SystemExit("Biochemistry 5-14 post-answer presentation changed")
            page.screenshot(path=str(output / "prepladder-biochemistry-5-14-option.png"), full_page=True)
            print("BIOCHEM_5_14_BROWSER_OK exact_alpha=true no_square=true choices=4 canonical_answer=4")

            open_practice("4-12")
            regulator_choices = ["ATP", "Citrate", "Fructose-2,6-bisphosphate", "Acetyl-CoA"]
            regulator_stem = page.locator(".question-text .nk-question-prompt")
            regulator_stem.wait_for(state="visible")
            if regulator_stem.count() != 1 or "positive regulator" not in regulator_stem.inner_text():
                raise SystemExit(f"Biochemistry 4-12 stem missing: {regulator_stem.all_text_contents()!r}")
            if page.locator(".question-text table, .question-text .nk-question-unavailable").count():
                raise SystemExit("Biochemistry 4-12 invented a table or disabled valid choices")
            regulator_options = page.locator(".option-list button")
            if regulator_options.count() != 4 or regulator_options.locator(".option-text").all_inner_texts() != regulator_choices:
                raise SystemExit(f"Biochemistry 4-12 choices changed: {regulator_options.locator('.option-text').all_inner_texts()!r}")
            regulator_options.nth(2).click()
            page.locator(".option-list .correct").wait_for(state="visible")
            regulator_feedback = page.locator(".feedback-body")
            regulator_feedback.wait_for(state="visible")
            # Practice renders Biochemistry explanations from original source-PDF
            # solution images (repair_source_solution_renderer), not explanation
            # text, so the text repair below serves Review/takeaway surfaces.
            # Here assert the PDF-image surface is intact and no dark block is
            # learner-visible on the Practice surface.
            if page.locator(".feedback-body .source-pdf-explanation").count() != 1:
                raise SystemExit("Biochemistry 4-12 source-PDF explanation surface missing")
            if "\u25a0" in (page.locator(".question-text").inner_text() + regulator_feedback.inner_text()):
                raise SystemExit("Biochemistry 4-12 dark-block placeholder remains on Practice surface")
            regulator_live = page.evaluate("""() => {
                const q = window.QB.__presentationQuestion('4-12');
                return {id: q.id, correctOption: q.correctOption, sourcePage: q.sourcePage,
                    explanation: q.explanation};
            }""")
            if regulator_live["id"] != "4-12" or regulator_live["correctOption"] != 3 or regulator_live["sourcePage"] != 85:
                raise SystemExit(f"Biochemistry 4-12 live record changed: {regulator_live!r}")
            regulator_exp = regulator_live["explanation"] or ""
            if "connected by \u03b1-1,4 linkage" not in regulator_exp or "cleaves \u03b1-1,4 linkages" not in regulator_exp:
                raise SystemExit("Biochemistry 4-12 explanation alpha repair missing from live display copy")
            if "\u25a0-1,4" in regulator_exp:
                raise SystemExit("Biochemistry 4-12 dark-block placeholder remains in live display copy")
            page.screenshot(path=str(output / "prepladder-biochemistry-4-12-explanation.png"), full_page=True)
            print("BIOCHEM_4_12_BROWSER_OK exact_alpha=true no_square=true choices=4 canonical_answer=3")

            complete_sources = {
                "10-10": (1, [
                    ["1", "Apolipoprotein A-I", "a", "Enhances lipoprotein lipase activity, facilitating triglyceride hydrolysis."],
                    ["2", "Apolipoprotein B-100", "b", "Involved in the transport of dietary lipids from the intestine to other tissues."],
                    ["3", "Apolipoprotein C-II", "c", "Helps in reverse cholesterol transport, removing excess cholesterol from tissue back to liver."],
                    ["4", "Apolipoprotein E", "d", "Essential for binding to LDL receptors on various tissues."],
                ]),
                "10-4": (1, [
                    ["A", "Choline Deficiency", "1", "Increases NADH, hindering fatty acid oxidation and promoting triacylglycerol accumulation."],
                    ["B", "Orotic Acid Interference", "2", "Impairs VLDL secretion, resulting in triacylglycerol accumulation and a fatty liver."],
                    ["C", "Vitamin E and Selenium", "3", "Involved in pyrimidine synthesis. Disrupts VLDL glycosylation, hindering release."],
                    ["D", "Ethanol Consumption", "4", "Protect against liver damage from lipid peroxidation"],
                ]),
                "13-21": (2, [
                    ["1", "Ninhydrin test", "a", "Detects compouds containing 2 or more peptide bonds"],
                    ["2", "Xanthoproteic test", "b", "Detects aromatic amino acids"],
                    ["3", "Sakaguchi test", "c", "Detects arginine"],
                    ["4", "Biuret test", "d", "Detects alpha-amino acids"],
                ]),
            }
            for question_id, (correct_option, expected_rows) in complete_sources.items():
                open_practice(question_id)
                canonical = page.evaluate("""() => {
                    const s = window.QB.getState().activeSession;
                    const q = window.QB.__presentationQuestion(s.questionIds[s.index]);
                    return {id: q.id, correctOption: q.correctOption,
                        choices: q.options.map(option => option.text)};
                }""")
                if canonical["id"] != question_id or canonical["correctOption"] != correct_option:
                    raise SystemExit(f"Complete-source question identity/answer changed: {canonical!r}")
                source_table = page.locator(".question-text table.nk-match-table")
                source_table.wait_for(state="visible")
                actual_rows = source_table.locator("tbody tr").evaluate_all("""rows => rows.map(row =>
                    [...row.querySelectorAll('td')].flatMap(cell =>
                        [cell.querySelector('b')?.innerText || '', cell.querySelector('span')?.innerText || '']))""")
                if actual_rows != expected_rows or "—" in source_table.inner_text():
                    raise SystemExit(f"Complete-source rows changed for {question_id}: {actual_rows!r}")
                source_options = page.locator(".option-list button")
                if source_options.count() != 4 or source_options.locator(".option-text").all_inner_texts() != canonical["choices"]:
                    raise SystemExit(f"Complete-source choices changed for {question_id}")
                source_options.nth(correct_option - 1).click()
                page.locator(".option-list .correct").wait_for(state="visible")
                correct_indices = page.locator(".option-list .option").evaluate_all(
                    "nodes => nodes.flatMap((node, index) => node.classList.contains('correct') ? [index + 1] : [])")
                if correct_indices != [correct_option]:
                    raise SystemExit(f"Complete-source correctness changed for {question_id}: {correct_indices!r}")
                page.screenshot(path=str(output / f"prepladder-complete-source-{question_id}.png"), full_page=True)

            open_practice("22-8")
            exponent_text = page.locator(".question-text sup.nk-sci-sup").all_inner_texts()
            if exponent_text != ["6", "9"]:
                raise SystemExit(f"Caret exponents did not render semantically in the question stem: {exponent_text!r}")

            open_practice("17-1")
            magnesium = page.locator(".option-text").nth(3)
            magnesium.locator("sup.nk-sci-sup").wait_for(state="visible")
            if magnesium.locator("sup.nk-sci-sup").inner_text() != "2+" or "■" in magnesium.inner_text():
                raise SystemExit(f"Safe ionic OCR notation was not repaired in an answer choice: {magnesium.inner_text()!r}")
            # PrepLadder explanations deliberately use original source-PDF pages;
            # exercise the native enhanced-text explanation path with Marrow.
            page.evaluate("window.QB.nkOpenSubjectLibrary('Physiology')")
            page.locator("button.nk-bank-card").filter(has_text="Marrow").click()
            page.locator("button.nk-topic-row").first.wait_for(state="visible")

            open_practice("marrow__PHYS_CH09_Q007")
            marrow_session = page.evaluate("""() => {
                const s = window.QB.getState().activeSession;
                return {mode: s?.mode, id: s?.questionIds?.[s.index]};
            }""")
            if marrow_session != {"mode": "practice", "id": "marrow__PHYS_CH09_Q007"}:
                raise SystemExit(f"Scientific explanation Practice opened the wrong stable question: {marrow_session!r}")
            page.locator(".option-list button").first.click()
            page.screenshot(path=str(output / "marrow-scientific-explanation.png"), full_page=True)
            feedback = page.locator('[data-marrow-explanation="marrow__PHYS_CH09_Q007"] .nk-gold-explanation')
            feedback.wait_for(state="visible")
            feedback_superscripts = feedback.locator("sup.nk-sci-sup").all_inner_texts()
            if "2+" not in feedback_superscripts:
                raise SystemExit(f"Scientific notation did not reach the native explanation renderer: {feedback_superscripts!r}")

            page.evaluate("window.QB.nkOpenSubjectLibrary('Biochemistry')")
            page.locator("button.nk-bank-card").filter(has_text="PrepLadder").click()
            page.locator("button.nk-topic-row").first.wait_for(state="visible")
            open_practice("28-3")
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
            open_practice("physiology-24-6")
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
