#!/usr/bin/env python3
"""PrepLadder Microbiology bank: shards current, counts, PYQ lessons, clean text,
figure inventory and app wiring.

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
from build_prepladder_microbiology_bank import INVENTORY, RUNTIME, app_record, jpeg_size, sha256  # noqa: E402


def main() -> None:
    subprocess.run([sys.executable, str(ROOT / "tools/build_prepladder_microbiology_bank.py"), "--check"], check=True)
    record = app_record()
    topics, questions = record["topics"], record["questions"]
    assert record["bank"] == "PrepLadder" and record["explanationFormat"] == "structured"
    assert len(topics) == 42 and len(questions) == 1042
    pyq = [t for t in topics if t["pyq"]]
    assert [t["id"] for t in pyq] == [f"microbiology-{n}" for n in (6, 17, 26, 30, 37, 42)]
    assert all(t["title"] == "Previous Year Questions" for t in pyq)
    assert sum(t["questionCount"] for t in pyq) == 474
    assert {t["section"] for t in topics} == {"General Microbiology", "Bacteriology", "Virology", "Mycology",
                                              "Parasitology", "Immunology"}

    ids = set()
    for q in questions:
        assert q["id"] not in ids
        ids.add(q["id"])
        assert q["id"] == f"{q['chapterId']}-{q['questionNumber']}", q["id"]
        assert q["bank"] == "PrepLadder" and q["explanationFormat"] == "structured"
        assert 1 <= q["correctOption"] <= len(q["options"]) and len(q["options"]) in (4, 5), q["id"]
        assert q["structuredExplanation"]["layout"] == "ordered-blocks"
        tables = {t["table_id"] for t in q["structuredExplanation"]["tables"]}
        for block in q["structuredExplanation"]["blocks"]:
            if block["type"] == "table":
                assert block["table_id"] in tables, q["id"]
        # Extraction debris never reaches the learner.
        text = json.dumps({k: v for k, v in q.items() if k != "reviewNotes"}, ensure_ascii=False)
        for junk in ("data-hash", "data-author", "src=", "/>", "![", "(content truncated)", "<br>", "image.prepladder"):
            assert junk not in text, (q["id"], junk)
        first = (q["structuredExplanation"]["blocks"] or [{}])[0]
        assert not str(first.get("text", "")).startswith(("Correct Answer", "Answer:")), q["id"]
    assert sum(1 for q in questions if q.get("stemTables")) == 37

    by_id = {q["id"]: q for q in questions}
    # Words the PDF split across narrow table columns are mended.
    l33 = json.dumps(by_id["microbiology-33-19"]["structuredExplanation"], ensure_ascii=False)
    assert "Chorioretinitis" in l33 and "Chorioretinit is" not in l33

    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    figures = inventory["figures"]
    assert len(figures) == 849 and len({f["imageId"] for f in figures}) == 849
    for figure in figures:
        assert figure["questionId"] in by_id, figure["imageId"]
        data = (ROOT / figure["file"]).read_bytes()
        assert sha256(data) == figure["sha256"], figure["imageId"]
        assert jpeg_size(data) == (figure["width"], figure["height"]), figure["imageId"]
        assert figure["role"] in ("question", "explanation")
    runtime = RUNTIME.read_text(encoding="utf-8")
    payload = json.loads(runtime[runtime.index("{", runtime.index("Object.assign")) + 0:].split(",", 1)[1].rsplit(");", 1)[0])
    assert sum(len(v) for v in payload.values()) == 849
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
