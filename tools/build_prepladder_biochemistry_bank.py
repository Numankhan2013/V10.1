#!/usr/bin/env python3
"""Build the PrepLadder Biochemistry bank (First Prof) from the 2025 edition.

The 2025 edition (biochemprep11.pdf, 821 questions in 39 lessons) replaces the
earlier PDF-page bank (app/src/main/assets/qbank_data.js, 719 questions in 28
chapters), whose attempts, reviews and saved tests point at its IDs ("1-1").
It is read from the PDF itself (tools/prepladder_prep11_pdf.py) and built by
the shared text-bank pipeline (tools/prepladder_text_bank.py), so stems,
options, keys, explanations and figures are the new edition's.

`source/edition_map.json` records, for every 2025 question, the earlier
question it continues, if any:
- A question that continues one keeps its ID, so progress carries over. The
  rest get `biochemistry-q<PrepLadder QID>`, which cannot collide.
- A match is the same stem and options, allowing for rewording (the earlier
  bank split some stems badly, so identical options with the same keyed answer
  also match). Options, order and key are always the 2025 edition's.
- Earlier questions the 2025 edition dropped stay, unchanged and with their
  PDF-page explanations, at the end of the lesson that holds most of their
  chapter's questions; an exact duplicate of a kept question is left out.

  python3 tools/build_prepladder_biochemistry_bank.py import <master.jsonl> <images-dir>
  python3 tools/build_prepladder_biochemistry_bank.py           # rebuild the shards
  python3 tools/build_prepladder_biochemistry_bank.py --check   # fail if shards are stale
  python3 tools/build_prepladder_biochemistry_bank.py release   # copy figures into the app

`import` also rewrites the edition map. The app build loads the bank with
`app_record()` and releases the figures with `release()` (tools/build_app_data.py).
"""
from __future__ import annotations

import collections
import difflib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_prepladder_microbiology_bank as micro  # noqa: E402
from prepladder_text_bank import NO_EXPLANATION, ROOT, TextBank  # noqa: E402

OLD_BANK = ROOT / "app/src/main/assets/qbank_data.js"
OLD_PDF = "Biochemistry_QBank_Source.pdf"
FOOTER = re.compile(r"Prepladder X Qbank\s*•\s*Biochemistry\s*Page \d+ of \d+")
GREEK = str.maketrans("αβγδ₀₁₂₃₄⁺⁻²³", "abgd01234+-23")
MATCH, STEM, OPTIONS = 0.80, 0.55, 0.999
# "Dermatan sulfate (Option C). However…" reads "**… (Option C):** . However…" once its
# label is bolded; the stray stop or comma goes.
LABEL_PUNCT = re.compile(r"(\):(?:\*\*)?) [.,] ")
# 2025 keys checked against the question and the 2025 explanation itself. 11-33 asks
# for the least likely cause of virilisation in a girl; the explanation describes
# 17-hydroxylase deficiency (no androgens), but the key prints 21-hydroxylase.
KEY_FIXES = {"11-33": (1, "2025 key prints B (21-hydroxylase deficiency); its own explanation and the "
                          "earlier edition give A (17-hydroxylase deficiency causes no virilisation)")}


def load_old() -> list[dict]:
    text = OLD_BANK.read_text(encoding="utf-8")
    return json.loads(text[text.index("{"):text.rindex("}") + 1])["questions"]


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", FOOTER.sub(" ", str(text)).lower().translate(GREEK))


def ratio(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


def build_map(rows: list[dict], old: list[dict]) -> dict:
    """Pair each 2025 question with the earlier question it continues."""
    new = [(r["prepladder_qid"], norm(r["question"]), [norm(o["text"]) for o in r["options"]],
            [o["id"] for o in r["options"]].index(r["correct_options_list"][0])) for r in rows]
    prev = [(q["id"], norm(q["question"]), [norm(o["text"]) for o in q["options"]], q["correctOption"] - 1) for q in old]

    def score(n, o):
        stem = ratio(n[1], o[1])
        options = sum(max(ratio(a, b) for b in o[2]) for a in n[2]) / max(len(n[2]), 1)
        return 0.6 * stem + 0.4 * options, stem, options

    def grams(t):
        return {t[i:i + 8] for i in range(max(len(t) - 7, 1))}

    old_grams = [grams(o[1]) for o in prev]
    pairs = []
    # First pass: the 15 earlier stems sharing most 8-letter runs with each new one.
    for n in new:
        g = grams(n[1])
        for i in sorted(range(len(prev)), key=lambda i: -len(g & old_grams[i]) / (len(old_grams[i]) or 1) ** 0.5)[:15]:
            total, stem, options = score(n, prev[i])
            if stem >= 0.5 and (total >= MATCH or options >= OPTIONS and stem >= STEM):
                pairs.append((total, n[0], prev[i][0]))
    continues, used = {}, set()
    for total, qid, old_id in sorted(pairs, reverse=True):
        if qid not in continues and old_id not in used:
            continues[qid] = old_id
            used.add(old_id)
    # Second pass, over everything left: identical options keyed to the same answer.
    second = []
    for n in new:
        if n[0] in continues:
            continue
        for o in prev:
            if o[0] in used:
                continue
            total, stem, options = score(n, o)
            same = len(n[2]) == len(o[2]) and o[3] < len(o[2]) and n[2][n[3]] == o[2][o[3]]
            if options >= 0.98 and same or total >= 0.78:
                second.append((total, n[0], o[0]))
    for total, qid, old_id in sorted(second, reverse=True):
        if qid not in continues and old_id not in used:
            continues[qid] = old_id
            used.add(old_id)
    # Dropped questions join the lesson holding most of their chapter's matched questions.
    lesson_of = {r["prepladder_qid"]: int(r["module_index"]) for r in rows}
    by_chapter = collections.defaultdict(collections.Counter)
    for qid, old_id in continues.items():
        by_chapter[old_id.split("-")[0]][lesson_of[qid]] += 1
    kept, duplicates = {}, {}
    signature = {o[0]: (o[1], tuple(sorted(o[2]))) for o in prev}
    for o in prev:
        if o[0] in used:
            continue
        twin = next((u for u in sorted(used) if signature[u] == signature[o[0]]), None)
        if twin:
            duplicates[o[0]] = twin
        else:
            kept[o[0]] = by_chapter[o[0].split("-")[0]].most_common(1)[0][0]
    return {"note": "2025 PrepLadder QID -> the earlier app ID it continues; earlier IDs the 2025 edition dropped "
                    "-> the lesson they join; dropped duplicates -> the kept question they repeat. "
                    "Written by tools/build_prepladder_biochemistry_bank.py import.",
            "counts": {"new": len(rows), "continued": len(continues), "kept": len(kept), "duplicates": len(duplicates)},
            "continues": dict(sorted(continues.items())), "kept": kept, "duplicates": duplicates}


class BiochemistryBank(TextBank):
    @property
    def edition_path(self) -> Path:
        return self.data / "source/edition_map.json"

    def edition(self) -> dict:
        if not hasattr(self, "_edition"):
            self._edition = json.loads(self.edition_path.read_text(encoding="utf-8"))
        return self._edition

    def import_source(self, master: Path, images: Path) -> None:
        rows = [{**micro.slim(raw), "prepladder_qid": raw["prepladder_qid"]}
                for raw in map(json.loads, filter(str.strip, master.read_text(encoding="utf-8").splitlines()))]
        micro.write_source(self.source, rows)
        edition = build_map(rows, load_old())
        self.edition_path.write_text(json.dumps(edition, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        self._edition = edition
        self.sync_figures(images)
        print(f"{self.tag}_IMPORT_OK questions={len(rows)} {edition['counts']}")

    def question_id(self, topic: dict, number: int, q: dict) -> str:
        return self.edition()["continues"].get(q["prepladder_qid"]) or f"biochemistry-q{q['prepladder_qid'].lstrip('Q')}"

    def normalize(self, rows: list[dict], overlay: bool = True) -> tuple[dict, list[dict]]:
        record, figures = super().normalize(rows, overlay)
        for q in record["questions"]:
            q["explanation"] = LABEL_PUNCT.sub(r"\1 ", q["explanation"])
            for block in q["structuredExplanation"]["blocks"]:
                for holder in [block] + block.get("items", []):
                    if "text" in holder:
                        holder["text"] = LABEL_PUNCT.sub(r"\1 ", holder["text"])
        topics = {t["id"]: t for t in record["topics"]}
        old = {q["id"]: q for q in load_old()}

        def earlier(q: dict, topic: dict, lesson: int, number: int, note: str) -> dict:
            return {**q, "subject": self.subject, "bank": "PrepLadder", "chapterId": topic["id"],
                    "chapter": topic["title"], "topic": topic["title"], "topicIndex": lesson,
                    "questionNumber": number, "edition": "earlier",
                    "provenance": {"sourceFile": OLD_PDF, "sourceLabel": "PrepLadder earlier edition"},
                    "reviewNotes": [note]}

        by_topic, replaced = collections.defaultdict(list), set()
        for i, q in enumerate(record["questions"]):
            q["edition"] = "2025+earlier" if not q["id"].startswith("biochemistry-q") else "2025"
            if q["id"] in KEY_FIXES:
                key, note = KEY_FIXES[q["id"]]
                q["correctOption"], q["correctAnswerText"] = key, q["options"][key - 1]["text"]
                q["reviewNotes"] = q.get("reviewNotes", []) + [note]
            # Where the 2025 edition prints no usable explanation (none, a fragment, or one
            # flagged for review), the earlier question it continues, keyed to the same
            # answer, stays as it was with its PDF-page explanation.
            blocks = q["structuredExplanation"]["blocks"]
            weak = q["reviewStatus"] == "needs_review" or blocks[0].get("text") == NO_EXPLANATION
            prev = old.get(q["id"])
            if weak and prev and norm(prev["options"][prev["correctOption"] - 1]["text"]) == norm(q["correctAnswerText"]):
                q = record["questions"][i] = earlier(
                    prev, topics[q["chapterId"]], q["topicIndex"], q["questionNumber"],
                    f"the 2025 edition ({q['prepladderQid']}) prints no usable explanation; the earlier question "
                    "is kept with its PDF-page explanation")
                replaced.add(q["id"])
            by_topic[q["chapterId"]].append(q)
        for old_id, lesson in sorted(self.edition()["kept"].items(), key=lambda kv: tuple(map(int, kv[0].split("-")))):
            topic = topics[self.topic_id(lesson)]
            number = topic["questionCount"] + 1
            by_topic[topic["id"]].append(earlier(
                old[old_id], topic, lesson, number,
                "not in the 2025 edition; kept from the earlier edition with its PDF-page explanation"))
            topic["questionCount"] = topic["sourceQuestionTotal"] = number
        record["questions"] = [q for t in record["topics"] for q in by_topic[t["id"]]]
        figures = [f for f in figures if f["questionId"] not in replaced]
        ids = [q["id"] for q in record["questions"]]
        if len(ids) != len(set(ids)):
            self.fail("duplicate question IDs")
        return record, figures


BANK = BiochemistryBank(
    slug="biochemistry",
    subject="Biochemistry",
    source_pdfs="biochemprep11.pdf",
    expected={"questions": 867, "topics": 39},
    acronyms={"hmp": "HMP", "pdh": "PDH", "glut": "GLUT", "epp": "EPP", "dna": "DNA", "rna": "RNA", "pcr": "PCR",
              "crispr": "CRISPR"},
    # The owner's study index. Previous-year lessons sit with the section whose topics
    # they ask about; 27 (heme, iron, 2,3-BPG) joins Heme Metabolism; the mixed sets
    # 1, 21, 35, 37 and 39 are Miscellaneous.
    index=[
        ("Carbohydrate Chemistry and Metabolism", [2, 3, 4, 5, 6, 7, 8, 9, 10]),
        ("Lipid Chemistry and Metabolism", [11, 12, 13, 14, 15]),
        ("Proteins and Amino Acid Metabolism", [16, 17, 18, 19, 20]),
        ("Molecular Biology and Genetics", [22, 23, 24, 25, 26, 36]),
        ("Enzymes", [28, 29]),
        ("Heme Metabolism and Porphyrias", [30, 31, 27]),
        ("Vitamins, Minerals and Nutrition", [32, 33, 34, 38]),
        ("Miscellaneous", [1, 21, 35, 37, 39]),
    ],
)

INVENTORY, RUNTIME, OVERLAY = BANK.inventory_path, BANK.runtime, BANK.overlay
app_record, release, load_source, normalize, lesson_title = (
    BANK.app_record, BANK.release, BANK.load_source, BANK.normalize, BANK.lesson_title)

if __name__ == "__main__":
    BANK.main(__doc__)
