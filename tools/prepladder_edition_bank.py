#!/usr/bin/env python3
"""A PrepLadder text bank that replaces an earlier PDF-page bank of the same subject.

The 2025 ("prep11") editions are read from the PDF itself
(tools/prepladder_prep11_pdf.py) and built by the shared text-bank pipeline
(tools/prepladder_text_bank.py), so stems, options, keys, explanations and figures
are the new edition's. The earlier bank's attempts, reviews and saved tests point
at its IDs, so `source/edition_map.json` records, for every new question, the
earlier question it continues, if any:
- A question that continues one keeps its ID, so progress carries over. The rest
  get `<slug>-q<PrepLadder QID>`, which cannot collide.
- A match is the same stem and options, allowing for rewording (the earlier banks
  split some stems badly, so identical options with the same keyed answer also
  match). Options, order and key are always the new edition's.
- Earlier questions the new edition dropped stay, unchanged and with their PDF-page
  explanations, at the end of the lesson that holds most of their chapter's
  questions; an exact duplicate of a kept question is left out.
- Where the new edition prints no usable explanation (none, a fragment, or one
  flagged for review) and the earlier question it continues is keyed to the same
  answer, the earlier question stays as it was, with its PDF-page explanation.
- A figure-only explanation is kept when the earlier question has no explanation
  text; a source table is better than an empty solution (15-2).
"""
from __future__ import annotations

import collections
import difflib
import json
import re
import sys
from pathlib import Path
from typing import Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))

import build_prepladder_microbiology_bank as micro  # noqa: E402
from prepladder_text_bank import NO_EXPLANATION, TextBank  # noqa: E402

GREEK = str.maketrans("αβγδ₀₁₂₃₄⁺⁻²³", "abgd01234+-23")
MATCH, STEM, OPTIONS = 0.80, 0.55, 0.999
# "Dermatan sulfate (Option C). However…" reads "**… (Option C):** . However…" once its
# label is bolded; the stray stop or comma goes.
LABEL_PUNCT = re.compile(r"(\):(?:\*\*)?) [.,] ")


def ratio(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


def numbers(question_id: str) -> tuple[int, ...]:
    return tuple(int(n) for n in re.findall(r"\d+", question_id))


def chapter(question_id: str) -> str:
    return question_id.rsplit("-", 1)[0]


class EditionBank(TextBank):
    def __init__(self, *args, load_old: Callable[[], list[dict]], old_pdf: str, footer: str,
                 key_fixes: dict[str, tuple[int, str]] | None = None, reviewed: dict[str, str] | None = None,
                 links: dict[str, str] | None = None, withdrawn: dict[str, str] | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_old, self.old_pdf = load_old, old_pdf
        # The earlier PDF's running footer, which its page-cut stems sometimes carry.
        self.footer = re.compile(footer)
        # New-edition keys checked against the question and its own explanation:
        # {app id: (correct option, note)}.
        self.key_fixes = key_fixes or {}
        # Flagged questions whose key was checked by hand: {app id: note}.
        self.reviewed = reviewed or {}
        # Pairs the matcher cannot see (the earlier stem or options are broken):
        # {PrepLadder QID: earlier app id}.
        self.links = links or {}
        # Questions neither edition prints whole (choices drawn as graphs left out of
        # the PDF): {app id: note}. They keep their explanation; answering is disabled.
        self.withdrawn = withdrawn or {}

    def norm(self, text: str) -> str:
        return re.sub(r"[^a-z0-9]+", "", self.footer.sub(" ", str(text)).lower().translate(GREEK))

    @property
    def edition_path(self) -> Path:
        return self.data / "source/edition_map.json"

    def edition(self) -> dict:
        if not hasattr(self, "_edition"):
            self._edition = json.loads(self.edition_path.read_text(encoding="utf-8"))
        return self._edition

    def build_map(self, rows: list[dict], old: list[dict]) -> dict:
        """Pair each new question with the earlier question it continues."""
        norm = self.norm
        new = [(r["prepladder_qid"], norm(r["question"]), [norm(o["text"]) for o in r["options"]],
                [o["id"] for o in r["options"]].index(r["correct_options_list"][0])) for r in rows]
        # An earlier question the source printed without a key has none (-1).
        prev = [(q["id"], norm(q["question"]), [norm(o["text"]) for o in q["options"]], (q["correctOption"] or 0) - 1)
                for q in old]

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
        continues, used = dict(self.links), set(self.links.values())
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
                same = len(n[2]) == len(o[2]) and 0 <= o[3] < len(o[2]) and n[2][n[3]] == o[2][o[3]]
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
            by_chapter[chapter(old_id)][lesson_of[qid]] += 1
        kept, duplicates = {}, {}
        signature = {o[0]: (o[1], tuple(sorted(o[2]))) for o in prev}
        for o in prev:
            if o[0] in used:
                continue
            twin = next((u for u in sorted(used) if signature[u] == signature[o[0]]), None)
            if twin:
                duplicates[o[0]] = twin
            else:
                kept[o[0]] = by_chapter[chapter(o[0])].most_common(1)[0][0]
        return {"note": "2025 PrepLadder QID -> the earlier app ID it continues; earlier IDs the 2025 edition dropped "
                        "-> the lesson they join; dropped duplicates -> the kept question they repeat. "
                        f"Written by {self.builder} import.",
                "counts": {"new": len(rows), "continued": len(continues), "kept": len(kept), "duplicates": len(duplicates)},
                "continues": dict(sorted(continues.items())), "kept": kept, "duplicates": duplicates}

    def import_source(self, master: Path, images: Path) -> None:
        rows = [{**micro.slim(raw), "prepladder_qid": raw["prepladder_qid"]}
                for raw in map(json.loads, filter(str.strip, master.read_text(encoding="utf-8").splitlines()))]
        micro.write_source(self.source, rows)
        edition = self.build_map(rows, self.load_old())
        self.edition_path.write_text(json.dumps(edition, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        self._edition = edition
        self.sync_figures(images)
        print(f"{self.tag}_IMPORT_OK questions={len(rows)} {edition['counts']}")

    def question_id(self, topic: dict, number: int, q: dict) -> str:
        return self.edition()["continues"].get(q["prepladder_qid"]) or f"{self.slug}-q{q['prepladder_qid'].lstrip('Q')}"

    def overlay_body(self, blocks: list[dict]) -> list[dict]:
        # The batches are exported after LABEL_PUNCT tidies "(Option C):** . However";
        # hash the same tidied body here so those entries are not called stale.
        def tidy(holder: dict) -> dict:
            holder = {**holder}
            if "text" in holder:
                holder["text"] = LABEL_PUNCT.sub(r"\1 ", holder["text"])
            if holder.get("items"):
                holder["items"] = [tidy(item) for item in holder["items"]]
            return holder
        return [tidy(b) for b in super().overlay_body(blocks)]

    def normalize(self, rows: list[dict], overlay: bool = True) -> tuple[dict, list[dict]]:
        record, figures = super().normalize(rows, overlay)
        for q in record["questions"]:
            q["explanation"] = LABEL_PUNCT.sub(r"\1 ", q["explanation"])
            for block in q["structuredExplanation"]["blocks"]:
                for holder in [block] + block.get("items", []):
                    if "text" in holder:
                        holder["text"] = LABEL_PUNCT.sub(r"\1 ", holder["text"])
        topics = {t["id"]: t for t in record["topics"]}
        old = {q["id"]: q for q in self.load_old()}
        new_prefix = f"{self.slug}-q"

        def earlier(q: dict, topic: dict, lesson: int, number: int, note: str) -> dict:
            return {**q, "subject": self.subject, "bank": "PrepLadder", "chapterId": topic["id"],
                    "chapter": topic["title"], "topic": topic["title"], "topicIndex": lesson,
                    "questionNumber": number, "edition": "earlier",
                    "provenance": {"sourceFile": self.old_pdf, "sourceLabel": "PrepLadder earlier edition"},
                    "reviewNotes": [note]}

        by_topic, replaced = collections.defaultdict(list), set()
        for i, q in enumerate(record["questions"]):
            q["edition"] = "2025+earlier" if not q["id"].startswith(new_prefix) else "2025"
            if q["id"] in self.key_fixes:
                key, note = self.key_fixes[q["id"]]
                q["correctOption"], q["correctAnswerText"] = key, q["options"][key - 1]["text"]
                q["reviewNotes"] = q.get("reviewNotes", []) + [note]
            if q["id"] in self.reviewed:
                q["reviewStatus"] = "pass"
                q["reviewNotes"] = q.get("reviewNotes", []) + [self.reviewed[q["id"]]]
            if q["id"] in self.withdrawn:
                # No choices: the app shows the question and explanation, answering disabled.
                q["options"], q["correctAnswerText"], q["reviewStatus"] = [], "", "unavailable"
                q["reviewNotes"] = q.get("reviewNotes", []) + [self.withdrawn[q["id"]]]
                by_topic[q["chapterId"]].append(q)
                continue
            blocks = q["structuredExplanation"]["blocks"]
            prev = old.get(q["id"])
            # A source table can be a figure and can be the whole explanation (15-2).
            # Prefer the earlier text only when the earlier question actually has
            # text; a figure is better than falling back to an empty explanation.
            figure_only = any(b["type"] == "figure" for b in blocks) and \
                all(b["type"] in ("figure", "references") for b in blocks)
            earlier_has_text = bool(prev and (prev.get("explanation") or "").strip())
            weak = q["reviewStatus"] == "needs_review" or blocks[0].get("text") == NO_EXPLANATION or \
                (figure_only and earlier_has_text)
            if weak and prev and prev["correctOption"] and \
                    self.norm(prev["options"][prev["correctOption"] - 1]["text"]) == self.norm(q["correctAnswerText"]):
                q = record["questions"][i] = earlier(
                    prev, topics[q["chapterId"]], q["topicIndex"], q["questionNumber"],
                    f"the 2025 edition ({q['prepladderQid']}) prints no usable explanation; the earlier question "
                    "is kept with its PDF-page explanation")
                replaced.add(q["id"])
            by_topic[q["chapterId"]].append(q)
        for old_id, lesson in sorted(self.edition()["kept"].items(), key=lambda kv: numbers(kv[0])):
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
