#!/usr/bin/env python3
"""PrepLadder Physiology bank (2025 edition): shards current, counts, study index,
earlier IDs carried over, clean text, hand-checked keys, figure inventory and app
wiring.

  python3 tools/test_prepladder_physiology_bank.py
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
from build_prepladder_physiology_bank import BANK, INVENTORY, RUNTIME, app_record, load_old  # noqa: E402
from prepladder_physiology_glyphs import fix  # noqa: E402
from prepladder_prep11_pdf import PLACEHOLDER  # noqa: E402
from prepladder_text_bank import NO_EXPLANATION  # noqa: E402

PYQ_LESSONS = (7, 8, 9, 10, 11, 12, 14, 18, 23, 25, 26, 30, 36, 39, 40, 41, 45, 46, 47, 49)


def main() -> None:
    subprocess.run([sys.executable, str(ROOT / "tools/build_prepladder_physiology_bank.py"), "--check"], check=True)
    record = app_record()
    topics, questions = record["topics"], record["questions"]
    assert record["bank"] == "PrepLadder" and record["subject"] == "Physiology"
    assert len(topics) == 49 and len(questions) == 988
    order = [n for _, lessons in BANK.index for n in lessons]
    assert sorted(order) == list(range(1, 50))
    assert [(t["section"], t["id"]) for t in topics] == [(s, f"physiology-{n}") for s, lessons in BANK.index for n in lessons]
    pyq = [t for t in topics if t["pyq"]]
    assert sorted(int(t["id"].split("-")[1]) for t in pyq) == list(PYQ_LESSONS)
    assert all(t["title"] == "Previous Year Questions" for t in pyq)
    assert sum(t["questionCount"] for t in pyq) == 451

    # Every earlier question keeps its ID: continued by a 2025 question, kept as it
    # was, or (exact repeats) left out for the question it repeats.
    edition = json.loads((ROOT / "data/Prepladder/physiology/source/edition_map.json").read_text(encoding="utf-8"))
    assert edition["counts"] == {"new": 958, "continued": 867, "kept": 30, "duplicates": 2}, edition["counts"]
    by_id = {q["id"]: q for q in questions}
    old = {q["id"]: q for q in load_old()}
    assert len(old) == 899
    for old_id in old:
        assert old_id in by_id or edition["duplicates"].get(old_id) in by_id, old_id
    editions = {e: sum(1 for q in questions if q["edition"] == e) for e in ("2025+earlier", "2025", "earlier")}
    assert editions == {"2025+earlier": 843, "2025": 91, "earlier": 54}, editions
    # Where the 2025 edition has no usable explanation, the earlier question (same keyed
    # answer) stays with its PDF-page explanation.
    replaced = [q["id"] for q in questions if q["edition"] == "earlier" and "no usable explanation" in q["reviewNotes"][0]]
    assert len(replaced) == 24 and "physiology-23-23" in replaced, replaced
    # Keys the 2025 PDF leaves out, checked by hand.
    assert by_id["physiology-q866658"]["correctAnswerText"] == "Conduction velocity increases"
    assert by_id["physiology-q866344"]["correctAnswerText"] == "Diagram d (4)"
    # Neither edition prints the compliance-curve choices: the 2025 question continues
    # the earlier one, keeps its explanation and cannot be answered.
    assert edition["continues"]["Q843131"] == "physiology-24-6"
    assert by_id["physiology-24-6"]["options"] == [] and by_id["physiology-24-6"]["reviewStatus"] == "unavailable"
    assert [q["id"] for q in questions if q.get("reviewStatus") not in ("pass", None)] == ["physiology-24-6"]

    lost = refs = 0
    for q in questions:
        assert q["bank"] == "PrepLadder" and q["subject"] == "Physiology"
        if q["edition"] == "earlier":
            # Kept as the earlier bank had it, with its PDF-page explanation.
            assert "explanationFormat" not in q and q["id"] in old, q["id"]
            assert {k: q[k] for k in ("question", "options", "correctOption")} == \
                {k: old[q["id"]][k] for k in ("question", "options", "correctOption")}, q["id"]
            continue
        assert q["explanationFormat"] == "structured", q["id"]
        assert (q["edition"] == "2025") == q["id"].startswith("physiology-q"), q["id"]
        assert q["id"] == f"physiology-q{q['prepladderQid'][1:]}" or edition["continues"][q["prepladderQid"]] == q["id"]
        if q["id"] != "physiology-24-6":
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
        # q865273 keys a multi-part answer and opens on "Correct answers- a) Apical…", which reads whole.
        assert q["id"] == "physiology-q865273" or \
            not first.lower().startswith(("correct answer", "correct option", "correct ans", "answer:")), q["id"]
        if first == NO_EXPLANATION:
            lost += 1
        kinds = [b["type"] for b in blocks if b["type"] != "figure"]
        assert kinds.count("references") <= 1 and ("references" not in kinds or kinds[-1] == "references"), q["id"]
        refs += kinds.count("references")
    assert lost == 1, lost
    assert refs == 817, refs
    # Characters the PDF drew as placeholder glyphs, restored from context.
    P = PLACEHOLDER
    assert fix(f"PO2{P}{P} and PaCO{P}") == "PO₂ and PaCO₂"
    assert fix(f"Na{P}, K{P}, Cl{P}, HCO3{P}, Ca²{P}") == "Na⁺, K⁺, Cl⁻, HCO₃⁻, Ca²⁺"

    figures = json.loads(INVENTORY.read_text(encoding="utf-8"))["figures"]
    assert len(figures) == 463 and len({f["imageId"] for f in figures}) == 463
    for figure in figures:
        assert figure["questionId"] in by_id, figure["imageId"]
        data = (ROOT / figure["file"]).read_bytes()
        assert sha256(data) == figure["sha256"], figure["imageId"]
        assert jpeg_size(data) == (figure["width"], figure["height"]), figure["imageId"]
    runtime = RUNTIME.read_text(encoding="utf-8")
    payload = json.loads(runtime[runtime.index("{", runtime.index("Object.assign")):].split(",", 1)[1].rsplit(");", 1)[0])
    assert sum(len(v) for v in payload.values()) == 463
    for rows in payload.values():
        for row in rows:
            assert (ROOT / "app/src/main/assets" / row["src"]).exists(), row["src"]

    page = assemble((ROOT / "app/src/main/assets/index.html").read_text(encoding="utf-8"))
    for marker in (
        '<script defer src="prepladder_physiology_visual_metadata.js"></script>',
        "record.subject==='Physiology'&&TEXT_EDITION('Physiology')",
    ):
        assert page.count(marker) == 1, marker
    print(f"PREPLADDER_PHYSIOLOGY_TEST_OK questions={len(questions)} topics={len(topics)} pyq={len(pyq)} "
          f"figures={len(figures)} kept_earlier={editions['earlier']} lost_explanations={lost}")


if __name__ == "__main__":
    main()
