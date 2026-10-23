#!/usr/bin/env python3
"""PrepLadder Anatomy bank (2025 edition): shards current, counts, study index,
earlier IDs carried over, clean text, hand-checked keys, figure inventory and app
wiring.

  python3 tools/test_prepladder_anatomy_bank.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from build_app_data import assemble  # noqa: E402
from build_prepladder_microbiology_bank import jpeg_size, sha256  # noqa: E402
from build_prepladder_anatomy_bank import BANK, INVENTORY, RUNTIME, app_record, load_old  # noqa: E402
from prepladder_prep11_pdf import PLACEHOLDER  # noqa: E402
from prepladder_text_bank import NO_EXPLANATION  # noqa: E402

PYQ_LESSONS = (6, 15, 21, 25, 29, 36, 41, 45, 46, 49, 50, 51, 52, 54)


def main() -> None:
    subprocess.run([sys.executable, str(ROOT / "tools/build_prepladder_anatomy_bank.py"), "--check"], check=True)
    record = app_record()
    topics, questions = record["topics"], record["questions"]
    assert record["bank"] == "PrepLadder" and record["subject"] == "Anatomy"
    assert len(topics) == 54 and len(questions) == 1134
    order = [n for _, lessons in BANK.index for n in lessons]
    assert sorted(order) == list(range(1, 55))
    assert [(t["section"], t["id"]) for t in topics] == [(s, f"anatomy-{n}") for s, lessons in BANK.index for n in lessons]
    pyq = [t for t in topics if t["pyq"]]
    assert sorted(int(t["id"].split("-")[1]) for t in pyq) == list(PYQ_LESSONS)
    assert all(t["title"].startswith("Previous Year Questions") for t in pyq)
    assert sum(t["questionCount"] for t in pyq) == 475

    # Every earlier question keeps its ID: continued by a 2025 question, kept as it
    # was, or (exact repeats) left out for the question it repeats.
    edition = json.loads((ROOT / "data/Prepladder/anatomy/source/edition_map.json").read_text(encoding="utf-8"))
    assert edition["counts"] == {"new": 1102, "continued": 1036, "kept": 32, "duplicates": 0}, edition["counts"]
    by_id = {q["id"]: q for q in questions}
    old = {q["id"]: q for q in load_old()}
    assert len(old) == 1068
    for old_id in old:
        assert old_id in by_id or edition["duplicates"].get(old_id) in by_id, old_id
    editions = {e: sum(1 for q in questions if q["edition"] == e) for e in ("2025+earlier", "2025", "earlier")}
    assert editions == {"2025+earlier": 1031, "2025": 66, "earlier": 37}, editions
    # Where the 2025 edition has no usable explanation, the earlier question (same keyed
    # answer) stays with its PDF-page explanation.
    replaced = [q["id"] for q in questions if q["edition"] == "earlier" and "no usable explanation" in q["reviewNotes"][0]]
    assert len(replaced) == 5 and "anatomy-29-7" in replaced, replaced
    # A key the 2025 PDF leaves out, checked by hand; two it prints against its own explanation.
    assert by_id["anatomy-22-4"]["correctAnswerText"] == "Image b (Short head of biceps femoris)"
    assert by_id["anatomy-15-52"]["correctAnswerText"] == "Thyroid"
    assert by_id["anatomy-45-16"]["correctAnswerText"] == "Spleen"
    assert [q["id"] for q in questions if q.get("reviewStatus") not in ("pass", None)] == []

    lost = refs = 0
    for q in questions:
        assert q["bank"] == "PrepLadder" and q["subject"] == "Anatomy"
        if q["edition"] == "earlier":
            # Kept as the earlier bank had it, with its PDF-page explanation.
            assert "explanationFormat" not in q and q["id"] in old, q["id"]
            assert {k: q[k] for k in ("question", "options", "correctOption")} == \
                {k: old[q["id"]][k] for k in ("question", "options", "correctOption")}, q["id"]
            continue
        assert q["explanationFormat"] == "structured", q["id"]
        assert (q["edition"] == "2025") == q["id"].startswith("anatomy-q"), q["id"]
        assert q["id"] == f"anatomy-q{q['prepladderQid'][1:]}" or edition["continues"][q["prepladderQid"]] == q["id"]
        assert len(q["options"]) == 4 and 1 <= q["correctOption"] <= 4, q["id"]
        assert [o["letter"] for o in q["options"]] == list("ABCD"), q["id"]
        blocks = q["structuredExplanation"]["blocks"]
        assert q["structuredExplanation"]["layout"] == "ordered-blocks" and blocks, q["id"]
        text = json.dumps({k: v for k, v in q.items() if k != "reviewNotes"}, ensure_ascii=False)
        for junk in ("data-hash", "data-author", "src=", "/>", "![", "<br>", "image.prepladder", "{{caption_text}}",
                     PLACEHOLDER, "Listen to Audio", "Listen (English)", "@Neet_pg_bot", "Back to this question",
                     "See Answer in Part B", "Quick Jump", " , ", " . "):
            assert junk not in text, (q["id"], junk)
        first = str(blocks[0].get("text", ""))
        # Two match-the-following answers open "Correct Option is: A-2, B-1…", which reads whole.
        assert q["id"] in ("anatomy-21-43", "anatomy-36-31") or \
            not first.lower().startswith(("correct answer", "correct option", "correct ans", "answer:")), q["id"]
        if first == NO_EXPLANATION:
            lost += 1
        kinds = [b["type"] for b in blocks if b["type"] != "figure"]
        assert kinds.count("references") <= 1 and ("references" not in kinds or kinds[-1] == "references"), q["id"]
        refs += kinds.count("references")
    assert lost == 0, lost
    assert refs == 907, refs
    figures = json.loads(INVENTORY.read_text(encoding="utf-8"))["figures"]
    assert len(figures) == 1490 and len({f["imageId"] for f in figures}) == 1490
    for figure in figures:
        assert figure["questionId"] in by_id, figure["imageId"]
        data = (ROOT / figure["file"]).read_bytes()
        assert sha256(data) == figure["sha256"], figure["imageId"]
        assert jpeg_size(data) == (figure["width"], figure["height"]), figure["imageId"]
    runtime = RUNTIME.read_text(encoding="utf-8")
    payload = json.loads(runtime[runtime.index("{", runtime.index("Object.assign")):].split(",", 1)[1].rsplit(");", 1)[0])
    assert sum(len(v) for v in payload.values()) == 1490
    for rows in payload.values():
        for row in rows:
            assert (ROOT / "app/src/main/assets" / row["src"]).exists(), row["src"]

    page = assemble((ROOT / "app/src/main/assets/index.html").read_text(encoding="utf-8"))
    for marker in (
        '<script defer src="prepladder_anatomy_visual_metadata.js"></script>',
        "(record.subject==='Physiology'||record.subject==='Anatomy')&&TEXT_EDITION(record.subject)",
    ):
        assert page.count(marker) == 1, marker
    print(f"PREPLADDER_ANATOMY_TEST_OK questions={len(questions)} topics={len(topics)} pyq={len(pyq)} "
          f"figures={len(figures)} kept_earlier={editions['earlier']} lost_explanations={lost}")


if __name__ == "__main__":
    main()
