#!/usr/bin/env python3
"""PrepLadder Biochemistry bank (2025 edition): shards current, counts, study index,
earlier IDs carried over, clean text, lost explanations marked, figure inventory and
app wiring.

  python3 tools/test_prepladder_biochemistry_bank.py
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from build_app_data import assemble  # noqa: E402
from build_prepladder_biochemistry_bank import (  # noqa: E402
    BANK, INVENTORY, RUNTIME, app_record, lesson_title, load_old)
from build_prepladder_microbiology_bank import jpeg_size, sha256  # noqa: E402
from prepladder_biochemistry_glyphs import fix  # noqa: E402
from prepladder_prep11_pdf import PLACEHOLDER, drop_answer_lead, drop_key_tail  # noqa: E402
from prepladder_text_bank import NO_EXPLANATION  # noqa: E402

PYQ_LESSONS = (1, 8, 9, 10, 14, 15, 19, 20, 21, 26, 27, 29, 31, 34, 35, 36, 37, 38, 39)


def main() -> None:
    subprocess.run([sys.executable, str(ROOT / "tools/build_prepladder_biochemistry_bank.py"), "--check"], check=True)
    record = app_record()
    topics, questions = record["topics"], record["questions"]
    assert record["bank"] == "PrepLadder" and record["subject"] == "Biochemistry"
    assert len(topics) == 39 and len(questions) == 867
    order = [n for _, lessons in BANK.index for n in lessons]
    assert sorted(order) == list(range(1, 40))
    assert [(t["section"], t["id"]) for t in topics] == [(s, f"biochemistry-{n}") for s, lessons in BANK.index for n in lessons]
    pyq = [t for t in topics if t["pyq"]]
    assert sorted(int(t["id"].split("-")[1]) for t in pyq) == list(PYQ_LESSONS)
    assert all(t["title"] == "Previous Year Questions" for t in pyq)
    assert sum(t["questionCount"] for t in pyq) == 492
    assert lesson_title("Hmp Pathway And Uronic Acid Pathway") == "HMP Pathway and Uronic Acid Pathway"

    # Every earlier question keeps its ID: continued by a 2025 question, kept as it
    # was, or (one exact repeat) left out for the question it repeats.
    edition = json.loads((ROOT / "data/Prepladder/biochemistry/source/edition_map.json").read_text(encoding="utf-8"))
    assert edition["counts"] == {"new": 821, "continued": 672, "kept": 46, "duplicates": 1}, edition["counts"]
    by_id = {q["id"]: q for q in questions}
    old = {q["id"]: q for q in load_old()}
    assert len(old) == 719
    for old_id in old:
        assert old_id in by_id or edition["duplicates"].get(old_id) in by_id, old_id
    editions = {e: sum(1 for q in questions if q["edition"] == e) for e in ("2025+earlier", "2025", "earlier")}
    assert editions == {"2025+earlier": 669, "2025": 149, "earlier": 49}, editions
    # Where the 2025 edition has no usable explanation, the earlier question (same keyed
    # answer) stays with its PDF-page explanation.
    for qid in ("21-29", "21-58", "27-5"):
        assert by_id[qid]["edition"] == "earlier" and "no usable explanation" in by_id[qid]["reviewNotes"][0], qid
    # 15-2's 2025 solution is a table image, not an empty explanation, so the
    # 2025 question stays and carries the source figure instead of falling back.
    assert by_id["15-2"]["edition"] == "2025+earlier"
    assert by_id["15-2"]["structuredExplanation"]["blocks"][0] == {
        "type": "figure", "figure_id": "BIO11_L18_Q002_E1"}
    # A 2025 key its own explanation contradicts is corrected.
    assert by_id["11-33"]["correctOption"] == 1 and by_id["11-33"]["correctAnswerText"] == "17-hydroxylase deficiency"

    ids = set()
    lost = refs = 0
    for q in questions:
        assert q["id"] not in ids
        ids.add(q["id"])
        assert q["bank"] == "PrepLadder" and q["subject"] == "Biochemistry"
        assert 1 <= q["correctOption"] <= len(q["options"]), q["id"]
        if q["edition"] == "earlier":
            # Kept as the earlier bank had it, with its PDF-page explanation.
            assert "explanationFormat" not in q and q["id"] in old, q["id"]
            assert {k: q[k] for k in ("question", "options", "correctOption")} == \
                {k: old[q["id"]][k] for k in ("question", "options", "correctOption")}, q["id"]
            continue
        assert q["explanationFormat"] == "structured", q["id"]
        assert (q["edition"] == "2025") == q["id"].startswith("biochemistry-q"), q["id"]
        assert q["id"] == f"biochemistry-q{q['prepladderQid'][1:]}" or edition["continues"][q["prepladderQid"]] == q["id"]
        assert len(q["options"]) == 4, q["id"]
        assert [o["letter"] for o in q["options"]] == list("ABCDE"[:len(q["options"])]), q["id"]
        blocks = q["structuredExplanation"]["blocks"]
        assert q["structuredExplanation"]["layout"] == "ordered-blocks" and blocks, q["id"]
        text = json.dumps({k: v for k, v in q.items() if k != "reviewNotes"}, ensure_ascii=False)
        for junk in ("data-hash", "data-author", "src=", "/>", "![", "<br>", "image.prepladder", "{{caption_text}}",
                     PLACEHOLDER, "Listen to Audio", "@Neet_pg_bot", "Back to this question", "See Answer in Part B",
                     "Quick Jump", " , ", " . "):
            assert junk not in text, (q["id"], junk)
        first = str(blocks[0].get("text", ""))
        assert not first.lower().startswith(("correct answer", "correct option", "correct ans", "answer:")), q["id"]
        assert not re.match(r"[a-z][^.]{0,40}\.?$", first), q["id"]
        if first == NO_EXPLANATION:
            lost += 1
            assert any("prints no explanation" in n for n in q["reviewNotes"]), q["id"]
        kinds = [b["type"] for b in blocks if b["type"] != "figure"]
        assert kinds.count("references") <= 1 and ("references" not in kinds or kinds[-1] == "references"), q["id"]
        refs += kinds.count("references")
    # "given above" is all the PDF prints for one new question.
    assert lost == 1, lost
    assert refs == 637, refs
    assert [q["id"] for q in questions if q.get("reviewStatus") == "needs_review"] == ["biochemistry-q839906"]

    def opening(qid: str) -> str:
        first = by_id[qid]["structuredExplanation"]["blocks"][0]
        return first["items"][0]["text"] if first["type"] == "bullets" else first["text"]
    # "Correct option D Thermogenin, also…": the lead goes, the sentence stays whole.
    assert opening("biochemistry-q807672").startswith("Thermogenin, also known as uncoupling protein 1")
    assert opening("biochemistry-q799712").startswith("Heparin is a glycosaminoglycan")
    assert opening("biochemistry-q799706").startswith("Hyaluronic acid is a type of glycosaminoglycan")
    assert opening("6-4").startswith("Biotin is a crucial coenzyme for pyruvate carboxylase, which")
    # A label the PDF cut mid-word ("replication: Mismatch repair: …") goes too.
    assert opening("21-30").startswith("This option is correct. The assertion")
    assert drop_key_tail("replication: Mismatch repair: x", "DNA replication") == "Mismatch repair: x"
    assert drop_answer_lead("Correct Option D - Phenylketonuria (PKU): PKU is", {"D": "Phenylketonuria"}) == "PKU is"
    # Openings written by hand (openings.json).
    assert opening("9-7").startswith("Regulation of Ketogenesis: Hormonal Regulation")
    assert opening("21-13").startswith("Base Excision Repair (Option A): Removes")
    # Statements the PDF ran together, laid out as numbered tables.
    assert sum(1 for q in questions if q.get("stemTables")) == 15
    assert by_id["5-10"]["stemTables"][0]["rows"][1] == ["2. Glucose residues are connected by α-1,4 linkage"]
    # Characters the PDF drew as ZapfDingbats glyphs, restored from context.
    assert fix(f"CO{PLACEHOLDER} and HCO{PLACEHOLDER}{PLACEHOLDER}") == "CO₂ and HCO₃⁻"
    assert fix(f"Fe²{PLACEHOLDER} and NADP{PLACEHOLDER}") == "Fe²⁺ and NADP⁺"
    assert "α-1,4" in by_id["5-10"]["stemTables"][0]["rows"][1][0]

    figures = json.loads(INVENTORY.read_text(encoding="utf-8"))["figures"]
    assert len(figures) == 349 and len({f["imageId"] for f in figures}) == 349
    assert any(f["imageId"] == "BIO11_L18_Q002_E1" and f["questionId"] == "15-2" for f in figures)
    for figure in figures:
        assert figure["questionId"] in by_id, figure["imageId"]
        data = (ROOT / figure["file"]).read_bytes()
        assert sha256(data) == figure["sha256"], figure["imageId"]
        assert jpeg_size(data) == (figure["width"], figure["height"]), figure["imageId"]
    runtime = RUNTIME.read_text(encoding="utf-8")
    payload = json.loads(runtime[runtime.index("{", runtime.index("Object.assign")):].split(",", 1)[1].rsplit(");", 1)[0])
    assert sum(len(v) for v in payload.values()) == 349
    assert any(row["role"] == "explanation" and row["id"].endswith("BIO11_L18_Q002_E1")
               for row in payload["15-2"])
    for rows in payload.values():
        for row in rows:
            assert (ROOT / "app/src/main/assets" / row["src"]).exists(), row["src"]

    page = assemble((ROOT / "app/src/main/assets/index.html").read_text(encoding="utf-8"))
    for marker in (
        '<script defer src="prepladder_biochemistry_visual_metadata.js"></script>',
        "const TEXT_EDITION = ",
    ):
        assert page.count(marker) == 1, marker
    print(f"PREPLADDER_BIOCHEMISTRY_TEST_OK questions={len(questions)} topics={len(topics)} pyq={len(pyq)} "
          f"figures={len(figures)} kept_earlier={editions['earlier']} lost_explanations={lost}")


if __name__ == "__main__":
    main()
