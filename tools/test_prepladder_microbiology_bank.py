#!/usr/bin/env python3
"""PrepLadder Microbiology bank: shards current, counts, PYQ lessons, clean text,
the edition merge (Version X IDs kept), figure inventory and app wiring.

  python3 tools/test_prepladder_microbiology_bank.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from build_app_data import assemble  # noqa: E402
from build_prepladder_microbiology_bank import (  # noqa: E402
    INDEX, INVENTORY, RUNTIME, app_record, jpeg_size, load_edition_map, load_source, plain_text, sha256, x_app_id)


def main() -> None:
    subprocess.run([sys.executable, str(ROOT / "tools/build_prepladder_microbiology_bank.py"), "--check"], check=True)
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

    assert record["bank"] == "PrepLadder" and record["explanationFormat"] == "structured"
    assert len(topics) == 42 and len(questions) == 1202
    pyq = [t for t in topics if t["pyq"]]
    assert [t["id"] for t in pyq] == [f"microbiology-{n}" for n in (6, 17, 26, 30, 37, 42)]
    assert all(t["title"] == "Previous Year Questions" for t in pyq)
    assert sum(t["questionCount"] for t in pyq) == 610
    # Lessons follow the owner's study index (build_prepladder_microbiology_bank.INDEX).
    assert [(t["section"], t["id"]) for t in topics] == [(s, f"microbiology-{n}") for s, lessons in INDEX for n in lessons]
    assert [t["title"] for t in topics if t["section"] == "Immunology"][:2] == ["Immunity", "Antigen, Antibody and Their Reactions"]

    ids = set()
    for q in questions:
        assert q["id"] not in ids
        ids.add(q["id"])
        # Version X IDs are kept (progress carries over); new ones use the QID.
        assert q["id"].startswith("microbiology-") and q["chapterId"].startswith("microbiology-"), q["id"]
        assert q["bank"] == "PrepLadder" and q["explanationFormat"] == "structured"
        assert 1 <= q["correctOption"] <= len(q["options"]) and len(q["options"]) in (4, 5), q["id"]
        assert q["structuredExplanation"]["layout"] == "ordered-blocks"
        tables = {t["table_id"] for t in q["structuredExplanation"]["tables"]}
        for block in q["structuredExplanation"]["blocks"]:
            if block["type"] == "table":
                assert block["table_id"] in tables, q["id"]
        # Extraction debris never reaches the learner.
        text = json.dumps({k: v for k, v in q.items() if k != "reviewNotes"}, ensure_ascii=False)
        for junk in ("data-hash", "data-author", "src=", "/>", "![", "(content truncated)", "<br>", "image.prepladder",
                     "■", "{{caption_text}}"):
            assert junk not in text, (q["id"], junk)
        first = (q["structuredExplanation"]["blocks"] or [{}])[0]
        assert not str(first.get("text", "")).lower().startswith(("correct answer", "answer:")), q["id"]
        assert q["structuredExplanation"]["blocks"], q["id"]
    assert sum(1 for q in questions if q.get("stemTables")) == 49  # 35 printed + 14 hand-checked (stem_tables.json)
    by_qid = {q["id"]: q for q in questions}
    assert by_qid["microbiology-33-17"]["options"][1]["text"] == "Cryptosporidium parvum"
    assert not any(o["text"].startswith("[Image") for q in questions for o in q["options"])

    # Edition merge: every Version X question keeps its app ID unless the
    # November 2025 edition repeats a matched question word for word.
    edition = load_edition_map()
    x_ids = {x_app_id(q) for q in load_source()}
    dropped = {x_app_id(q) for q in load_source() if q["id"] in edition["xOnlyDuplicates"]}
    assert len(dropped) == 2 and x_ids - ids == dropped
    new_ids = ids - x_ids
    assert len(new_ids) == 162 and all(i.startswith("microbiology-q") for i in new_ids)
    assert sum(1 for q in questions if q["edition"] == "x") == 102

    by_id = {q["id"]: q for q in questions}
    # Words the PDF split across narrow table columns are mended.
    l33 = json.dumps(by_id["microbiology-33-19"]["structuredExplanation"], ensure_ascii=False)
    assert "Chorioretinitis" in l33 and "Chorioretinit is" not in l33

    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    figures = inventory["figures"]
    assert len(figures) == 1552 and len({f["imageId"] for f in figures}) == 1552
    for figure in figures:
        assert figure["questionId"] in by_id, figure["imageId"]
        data = (ROOT / figure["file"]).read_bytes()
        assert sha256(data) == figure["sha256"], figure["imageId"]
        assert jpeg_size(data) == (figure["width"], figure["height"]), figure["imageId"]
        assert figure["role"] in ("question", "explanation")
    runtime = RUNTIME.read_text(encoding="utf-8")
    payload = json.loads(runtime[runtime.index("{", runtime.index("Object.assign")) + 0:].split(",", 1)[1].rsplit(");", 1)[0])
    assert sum(len(v) for v in payload.values()) == 1552
    for rows in payload.values():
        for row in rows:
            assert (ROOT / "app/src/main/assets" / row["src"]).exists(), row["src"]

    page = assemble((ROOT / "app/src/main/assets/index.html").read_text(encoding="utf-8"))
    for marker in (
        '<script defer src="prepladder_microbiology_visual_metadata.js"></script>',
        "function nkTextExplained(q)",
        "record.bank==='PrepLadder'&&record.subject&&!SUBJECT_BY_NAME[record.subject]",
        "if(b.type==='heading')return",
        "if(chapter?.section)return chapter.section;",
        "function nkQuestionStemTables(q)",
    ):
        assert page.count(marker) == 1, marker
    print(f"PREPLADDER_MICROBIOLOGY_TEST_OK questions={len(questions)} topics={len(topics)} pyq={len(pyq)} "
          f"figures={len(figures)} trimmed={sum(1 for f in figures if f['trimBox'])}")


if __name__ == "__main__":
    main()
