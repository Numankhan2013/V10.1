#!/usr/bin/env python3
"""The web build moves explanations into on-demand packs without losing any."""
import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_web_dist as builder  # noqa: E402


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp)
        presentation = out / "presentation.js"
        presentation.write_text("const REVIEWS={\"marrow__PINNED\":{}};if(q.id==='9-9')return null;\n")
        script = out / "subjects.js"
        subjects = {"subjects": [{"subject": "Physiology", "questions": [
            {"id": "physiology-1-1", "question": "Q?", "options": [{"letter": "A", "text": "a"}], "explanation": "Because.", "sourceRef": "Solution Page 4"},
            {"id": "9-9", "question": "Pinned", "explanation": "Kept inline."},
            {"id": "physiology-1-2", "question": "No explanation"},
        ]}]}
        script.write_text("window.SUBJECT_QBANK_DATA = " + json.dumps(subjects) + ";\n")
        marrow = {"records": [{"subject": "Anatomy", "questions": [
            {"id": "marrow__A1", "question": "M?", "explanation": "E", "structuredExplanation": {"text": "E"}, "provenance": {"explanationPages": [3]}},
            {"id": "marrow__PINNED", "question": "P?", "explanation": "inline"},
        ]}]}
        gold = {"marrow__A1": {"emphasis": ["x"]}, "marrow__PINNED": {"emphasis": ["y"]}}
        page = ("<html><head></head><body><script>\n  const MARROW_DATA = " + json.dumps(marrow) + ";\n"
                "  const NK_MARROW_EXPLANATION_GOLD_V1 = " + json.dumps(gold) + ";\n</script></body></html>")
        with patch.object(builder, "PRESENTATION", presentation):
            packs = builder.DetailPacks(out)
            builder.split_script_data(script, packs)
            page, files = builder.externalize_data(page, out, packs)
            names = packs.write()

        light = json.loads(script.read_text().split("=", 1)[1].rstrip(";\n"))["subjects"][0]["questions"]
        assert "explanation" not in light[0] and light[0]["detailPack"] == 0, light[0]
        assert light[0]["question"] == "Q?" and light[0]["sourceRef"] == "Solution Page 4", "boot fields stay"
        assert light[1]["explanation"] == "Kept inline." and "detailPack" not in light[1], "pinned questions stay whole"
        assert "detailPack" not in light[2], "questions without explanations need no pack"

        loaded = {name: (out / name).read_text() for name in files}
        marrow_out = json.loads(json.loads(next(t for n, t in loaded.items() if "marrow_data" in n).split("JSON.parse(", 1)[1].rsplit(")", 1)[0]))
        gold_out = json.loads(json.loads(next(t for n, t in loaded.items() if "gold" in n).split("JSON.parse(", 1)[1].rsplit(")", 1)[0]))
        m = marrow_out["records"][0]["questions"]
        assert set(m[0]) == {"id", "question", "detailPack"}, m[0]
        assert m[1]["explanation"] == "inline"
        assert gold_out == {"marrow__PINNED": {"emphasis": ["y"]}}, gold_out

        assert len(names) == 2 and all(n.startswith("data/details/") and n.endswith(".json") for n in names), names
        physiology = json.loads((out / names[0]).read_text())
        anatomy = json.loads((out / names[m[0]["detailPack"]]).read_text())
        assert physiology["q"] == {"physiology-1-1": {"explanation": "Because."}}, physiology
        assert anatomy["q"]["marrow__A1"] == {"explanation": "E", "structuredExplanation": {"text": "E"}, "provenance": {"explanationPages": [3]}}
        assert anatomy["gold"] == {"marrow__A1": {"emphasis": ["x"]}}
    print("QUESTION_DETAIL_PACKS_OK split=true pinned_inline=true gold=true hashed=true")


if __name__ == "__main__":
    main()
