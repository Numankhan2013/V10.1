#!/usr/bin/env python3
"""PrepLadder Pathology bank: shards current, counts, PYQ lessons, clean text,
explanations missing in the source marked, figure inventory and app wiring.

  python3 tools/test_prepladder_pathology_bank.py
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
from build_prepladder_pathology_bank import (  # noqa: E402
    BANK, INVENTORY, NO_EXPLANATION, RUNTIME, app_record, lesson_title)
from build_prepladder_microbiology_bank import plain_text  # noqa: E402
from build_prepladder_microbiology_bank import jpeg_size, sha256  # noqa: E402

PYQ_LESSONS = (5, 9, 13, 18, 25, 31, 36, 38, 43, 47, 51, 55, 58, 60, 63, 64, 66, 67, 73, 80, 82, 84, 85, 87, 88, 89, 90)


def main() -> None:
    subprocess.run([sys.executable, str(ROOT / "tools/build_prepladder_pathology_bank.py"), "--check"], check=True)
    record = app_record()
    topics, questions = record["topics"], record["questions"]
    # The flat explanation must be the flat rendering of the blocks the learner
    # sees, so the Key takeaway is computed from the same document.
    for q in questions:
        structured = q.get("structuredExplanation") or {}
        blocks = structured.get("blocks") or []
        tables = structured.get("tables") or []
        assert q["explanation"] == plain_text(blocks, tables), q["id"]
        # A table is part of the explanation the learner reads, so the flat copy
        # must carry its cells and not just its title.
        by_id = {t.get("table_id"): t for t in tables}
        for block in blocks:
            if block.get("type") != "table":
                continue
            table = by_id.get(block.get("table_id")) or {}
            for row in table.get("rows") or []:
                for cell in row:
                    if str(cell).strip():
                        assert str(cell) in q["explanation"], f"{q['id']} lost the table cell {cell!r}"
                        break
                else:
                    continue
                break

    assert record["bank"] == "PrepLadder" and record["subject"] == "Pathology"
    assert record["explanationFormat"] == "structured"
    assert len(topics) == 90 and len(questions) == 1459
    # Lessons follow the owner's study index; ids keep the extraction's lesson numbers.
    order = [n for _, lessons in BANK.index for n in lessons]
    assert sorted(order) == list(range(1, 91))
    assert [t["id"] for t in topics] == [f"pathology-{n}" for n in order]
    assert [t["section"] for t in topics] == [s for s, lessons in BANK.index for _ in lessons]
    assert [t["title"] for t in topics[:2]] == ["Cell Injury, Free Radical Injury, and ER Stress Related", "Cell Death"]
    assert next(t["section"] for t in topics if t["id"] == "pathology-86") == "Skin and Musculoskeletal"
    pyq = [t for t in topics if t["pyq"]]
    assert sorted(int(t["id"].split("-")[1]) for t in pyq) == list(PYQ_LESSONS)
    # The app tags a PYQ lesson by this exact title.
    assert all(t["title"] == "Previous Year Questions" for t in pyq)
    assert sum(t["questionCount"] for t in pyq) == 615
    assert lesson_title("Cml And Cll") == "CML and CLL"
    assert lesson_title("Hodgkin'S And Non-Hodgkin'S Lymphoma") == "Hodgkin's and Non-Hodgkin's Lymphoma"
    assert lesson_title("Pathology Of Female Genital Tract-Ii") == "Pathology of Female Genital Tract-II"

    ids = set()
    lost = refs = cited = 0
    for q in questions:
        assert q["id"] not in ids
        ids.add(q["id"])
        assert q["id"] == f"{q['chapterId']}-{q['questionNumber']}", q["id"]
        assert q["bank"] == "PrepLadder" and q["subject"] == "Pathology"
        assert 1 <= q["correctOption"] <= len(q["options"]) == 4, q["id"]
        assert re.fullmatch(r"Q\d+", q["prepladderQid"]), q["id"]
        blocks = q["structuredExplanation"]["blocks"]
        assert q["structuredExplanation"]["layout"] == "ordered-blocks" and blocks, q["id"]
        # Extraction debris never reaches the learner.
        text = json.dumps({k: v for k, v in q.items() if k != "reviewNotes"}, ensure_ascii=False)
        for junk in ("data-hash", "data-author", "src=", "/>", "![", "(content truncated)", "<br>", "image.prepladder",
                     "■", "\x7f", "{{caption_text}}", ";=", ";_"):
            assert junk not in text, (q["id"], junk)
        first = str(blocks[0].get("text", ""))
        assert not first.lower().startswith(("correct answer", "answer:")), q["id"]
        # A surviving sentence fragment is replaced by a plain note.
        assert not re.match(r"[a-z][^.]{0,40}\.$", first), q["id"]
        if first == NO_EXPLANATION:
            lost += 1
            assert any("prints no explanation" in n for n in q["reviewNotes"]), q["id"]
        # References are one block, the last text block, one item per source.
        kinds = [b["type"] for b in blocks if b["type"] != "figure"]
        assert kinds.count("references") <= 1 and ("references" not in kinds or kinds[-1] == "references"), q["id"]
        assert not any(b["type"] == "paragraph" and re.match(r"References?\s*:", b["text"]) for b in blocks), q["id"]
        for b in blocks:
            if b["type"] == "references":
                refs += 1
                assert b["items"] and all(it["rest"] or it.get("title") for it in b["items"]), q["id"]
                cited += sum(1 for it in b["items"] if it.get("title"))
    assert lost == 14
    assert refs == 1262 and cited == 1149, (refs, cited)
    # Image-only options rebuilt from the explanation stay flagged.
    assert sum(1 for q in questions if q["reviewStatus"] == "needs_review") == 9

    by_id = {q["id"]: q for q in questions}
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    figures = inventory["figures"]
    assert len(figures) == 1676 and len({f["imageId"] for f in figures}) == 1676
    for figure in figures:
        assert figure["questionId"] in by_id, figure["imageId"]
        data = (ROOT / figure["file"]).read_bytes()
        assert sha256(data) == figure["sha256"], figure["imageId"]
        assert jpeg_size(data) == (figure["width"], figure["height"]), figure["imageId"]
        assert figure["role"] in ("question", "explanation")
    runtime = RUNTIME.read_text(encoding="utf-8")
    payload = json.loads(runtime[runtime.index("{", runtime.index("Object.assign")):].split(",", 1)[1].rsplit(");", 1)[0])
    assert sum(len(v) for v in payload.values()) == 1676
    for rows in payload.values():
        for row in rows:
            assert (ROOT / "app/src/main/assets" / row["src"]).exists(), row["src"]

    # Restructured explanations: the checker accepts the worked examples, refuses
    # a changed word or a dropped figure, and the builder applies the overlay.
    import explanation_restructure as rs
    example = ROOT / "data/Prepladder/pathology/restructure/examples/example-result.json"
    subprocess.run([sys.executable, str(ROOT / "tools/explanation_restructure.py"), "check", str(example)], check=True,
                   stdout=subprocess.DEVNULL)
    source = [{"type": "paragraph", "text": "ATP depletion leads to pump failure (Option B ruled out)"},
              {"type": "figure", "figure_id": "F1"}]
    assert not rs.problems(source, [{"type": "paragraph", "text": "ATP depletion leads to pump failure"},
                                    {"type": "paragraph", "text": "(Option B ruled out)"}, source[1]])
    assert rs.problems(source, [{"type": "paragraph", "text": "ATP depletion causes pump failure (Option B ruled out)"},
                                source[1]])
    assert rs.problems(source, source[:1])
    overlay = json.loads(rs.OVERLAY.read_text(encoding="utf-8"))
    # Some restructures only split paragraphs; most gain points or tables.
    structured = sum(1 for qid in overlay
                     if {b["type"] for b in by_id[qid]["structuredExplanation"]["blocks"]} & {"bullets", "table"})
    assert len(overlay) == 1321 and structured == 1135, (len(overlay), structured)
    assert sum(len(by_id[qid]["structuredExplanation"]["tables"]) for qid in overlay) == 343
    # A lost opening written by hand applies on top of the restructure.
    assert by_id["pathology-25-19"]["structuredExplanation"]["blocks"][0]["text"].startswith("Castleman disease, also known")
    # Flattened lists laid out as tables, printed order kept (tools/prepladder_stem_tables.py).
    assert sum(1 for q in questions if q.get("stemTables")) == 46
    t = by_id["pathology-13-5"]["stemTables"][0]
    assert by_id["pathology-13-5"]["question"] == "Match the following with the appropriate disorder."
    assert t["rows"][0] == ["A. Autosomal recessive", "1. Kennedy disease"], t
    assert by_id["pathology-76-8"]["options"][1]["text"] == "Light blue top"
    assert not any(o["text"].startswith("[Image") for q in questions for o in q["options"])
    assert by_id["pathology-6-12"]["structuredExplanation"]["tables"][0]["columns"] == ["Features", "Transudate", "Exudate"]

    page = assemble((ROOT / "app/src/main/assets/index.html").read_text(encoding="utf-8"))
    for marker in (
        '<script defer src="prepladder_pathology_visual_metadata.js"></script>',
        "Microbiology:'second',Pathology:'second',Pharmacology:'second'}",
        "if(key.includes('pathology')) return {key:'pathology',icon:'microscope',tone:'amber'};",
    ):
        assert page.count(marker) == 1, marker
    print(f"PREPLADDER_PATHOLOGY_TEST_OK questions={len(questions)} topics={len(topics)} pyq={len(pyq)} "
          f"figures={len(figures)} trimmed={sum(1 for f in figures if f['trimBox'])} lost_explanations={lost}")


if __name__ == "__main__":
    main()
