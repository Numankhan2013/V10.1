#!/usr/bin/env python3
"""PrepLadder Pharmacology bank: shards current, counts, PYQ lessons, clean text,
explanations missing in the source marked, figure inventory and app wiring.

  python3 tools/test_prepladder_pharmacology_bank.py
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
from build_prepladder_pharmacology_bank import (  # noqa: E402
    INVENTORY, NO_EXPLANATION, RUNTIME, app_record, lesson_title)
from build_prepladder_microbiology_bank import jpeg_size, sha256  # noqa: E402

PYQ_LESSONS = (1, 5, 10, 14, 16, 21, 27, 33, 42, 44, 48, 52, 55, 56, 57, 59)
# The source prints five options (A-E) for these.
FIVE_OPTIONS = {"pharmacology-42-2", "pharmacology-42-30", "pharmacology-42-31", "pharmacology-42-99"}
SECTIONS = {"General Pharmacology", "Autonomic Nervous System", "Autacoids, NSAIDs, and Rheumatology",
            "Renal Pharmacology", "Cardiovascular Pharmacology", "Central Nervous System Pharmacology",
            "Endocrine Pharmacology", "Antimicrobials and Chemotherapy", "Respiratory Pharmacology",
            "Gastrointestinal Pharmacology", "Hematological Pharmacology",
            "Anticancer and Immunomodulator Pharmacology", "Anaesthetics and Miscellaneous Pharmacology"}


def main() -> None:
    subprocess.run([sys.executable, str(ROOT / "tools/build_prepladder_pharmacology_bank.py"), "--check"], check=True)
    record = app_record()
    topics, questions = record["topics"], record["questions"]
    assert record["bank"] == "PrepLadder" and record["subject"] == "Pharmacology"
    assert record["explanationFormat"] == "structured"
    assert len(topics) == 59 and len(questions) == 1321
    assert [t["id"] for t in topics] == [f"pharmacology-{n}" for n in range(1, 60)]
    pyq = [t for t in topics if t["pyq"]]
    assert [t["id"] for t in pyq] == [f"pharmacology-{n}" for n in PYQ_LESSONS]
    # The app tags a PYQ lesson by this exact title.
    assert all(t["title"] == "Previous Year Questions" for t in pyq)
    assert sum(t["questionCount"] for t in pyq) == 650
    assert {t["section"] for t in topics} == SECTIONS
    assert lesson_title("Ans Introduction And Cholinergic Drugs") == "ANS Introduction and Cholinergic Drugs"
    assert lesson_title("Hpa Axis And Drugs Acting On Bone And Osteoporosis") == \
        "HPA Axis and Drugs Acting on Bone and Osteoporosis"
    assert lesson_title("Parkinson'S Disease And Other Disorders") == "Parkinson's Disease and Other Disorders"
    assert lesson_title("Git Miscellaneous") == "GIT Miscellaneous"

    ids = set()
    lost = refs = cited = 0
    for q in questions:
        assert q["id"] not in ids
        ids.add(q["id"])
        assert q["id"] == f"{q['chapterId']}-{q['questionNumber']}", q["id"]
        assert q["bank"] == "PrepLadder" and q["subject"] == "Pharmacology"
        assert len(q["options"]) == (5 if q["id"] in FIVE_OPTIONS else 4), q["id"]
        assert [o["letter"] for o in q["options"]] == list("ABCDE"[:len(q["options"])]), q["id"]
        assert 1 <= q["correctOption"] <= len(q["options"]), q["id"]
        assert re.fullmatch(r"Q\d+", q["prepladderQid"]), q["id"]
        blocks = q["structuredExplanation"]["blocks"]
        assert q["structuredExplanation"]["layout"] == "ordered-blocks" and blocks, q["id"]
        # Extraction debris never reaches the learner.
        text = json.dumps({k: v for k, v in q.items() if k != "reviewNotes"}, ensure_ascii=False)
        for junk in ("data-hash", "data-author", "src=", "/>", "![", "(content truncated)", "<br>", "image.prepladder",
                     "■", "\x7f", "{{caption_text}}", ";=", ";_"):
            assert junk not in text, (q["id"], junk)
        first = str(blocks[0].get("text", ""))
        # The PDF opens many explanations "Correct Option D."; the app marks the answer itself.
        assert not first.lower().startswith(("correct answer", "correct option", "answer:")), q["id"]
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
    # Six print no explanation (a sentence tail or only references); two open
    # mid-sentence and keep the rest.
    assert lost == 6, lost
    assert sum(1 for q in questions if any("opens mid-sentence" in n for n in q.get("reviewNotes", []))) == 2
    assert refs == 1186 and cited == 1054, (refs, cited)
    assert not any(q["reviewStatus"] == "needs_review" for q in questions)

    by_id = {q["id"]: q for q in questions}
    # Openings the PDF cut off: a first word missing its first letters is restored
    # ("ue to" -> "Due to"); lost words are written by hand (openings.json).
    noted = lambda phrase: sum(1 for q in questions if any(phrase in n for n in q.get("reviewNotes", [])))
    assert (noted("restored as"), noted("opening is written"), noted("reads complete"), noted("not recoverable")) == \
        (74, 36, 2, 0), (noted("restored as"), noted("opening is written"), noted("reads complete"))
    opening = lambda qid: by_id[qid]["structuredExplanation"]["blocks"][0]["text"]
    assert opening("pharmacology-10-5").startswith("Due to alpha 1a receptors blockade")
    assert opening("pharmacology-5-10").startswith("Clarithromycin (Option B) raises rosuvastatin levels")
    assert opening("pharmacology-5-17").startswith("2M HCl: Normality")
    # The restructure pack's worked examples pass its checker.
    subprocess.run([sys.executable, str(ROOT / "tools/explanation_restructure.py"), "check",
                    str(ROOT / "data/Prepladder/pharmacology/restructure/examples/example-result.json")],
                   check=True, stdout=subprocess.DEVNULL)
    figures = json.loads(INVENTORY.read_text(encoding="utf-8"))["figures"]
    assert len(figures) == 272 and len({f["imageId"] for f in figures}) == 272
    for figure in figures:
        assert figure["questionId"] in by_id, figure["imageId"]
        data = (ROOT / figure["file"]).read_bytes()
        assert sha256(data) == figure["sha256"], figure["imageId"]
        assert jpeg_size(data) == (figure["width"], figure["height"]), figure["imageId"]
        assert figure["role"] in ("question", "explanation")
    runtime = RUNTIME.read_text(encoding="utf-8")
    payload = json.loads(runtime[runtime.index("{", runtime.index("Object.assign")):].split(",", 1)[1].rsplit(");", 1)[0])
    assert sum(len(v) for v in payload.values()) == 272
    for rows in payload.values():
        for row in rows:
            assert (ROOT / "app/src/main/assets" / row["src"]).exists(), row["src"]

    page = assemble((ROOT / "app/src/main/assets/index.html").read_text(encoding="utf-8"))
    for marker in (
        '<script defer src="prepladder_pharmacology_visual_metadata.js"></script>',
        "Pathology:'second',Pharmacology:'second'}",
        "if(key.includes('pharmacology')) return {key:'pharmacology',icon:'pill',tone:'amber'};",
    ):
        assert page.count(marker) == 1, marker
    print(f"PREPLADDER_PHARMACOLOGY_TEST_OK questions={len(questions)} topics={len(topics)} pyq={len(pyq)} "
          f"figures={len(figures)} trimmed={sum(1 for f in figures if f['trimBox'])} lost_explanations={lost}")


if __name__ == "__main__":
    main()
