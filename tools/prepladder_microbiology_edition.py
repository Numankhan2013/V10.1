#!/usr/bin/env python3
"""Reconcile the PrepLadder Microbiology November 2025 edition with Version X.

The first extraction (Version X, 1,042 questions) is what learners have been
studying; their attempts, reviews and saved tests point at its app IDs. The
November 2025 edition (1,100 questions) repeats most of it, rewords some,
corrects some answer keys, rewrites many explanations and adds new questions.

`edition_map.json` records, for every new-edition question, the Version X
question it continues (if any), how it changed and which edition supplies its
stem and explanation. The bank builder reads only that map and the two slim
sources, so the merge is deterministic and reviewable.

Rules:
- A matched question keeps its Version X app ID, so progress carries over.
  New questions get `microbiology-q<PrepLadder QID>`, which cannot collide.
- Stem: Version X when the stem and options are unchanged, or when the new
  stem is Version X's stem plus its Match-the-following table flattened to
  text (Version X keeps the table); otherwise the new edition.
  Options, order and answer key always come from the new edition.
- Explanation: the new edition, except where its text is the same as Version
  X's (>= 90% of words, answer unchanged), where Version X's structured
  blocks (tables, lists) are kept, and where the new PDF left it blank.
- Version X questions the new edition dropped stay in their lesson; exact
  duplicates of a question that was matched are left out.
- Lessons: the new edition's 48 lessons fold into the 42 Version X topics.
  Lesson 7 (5 extra General Microbiology PYQs) joins topic 6; lessons 44-48
  (15 leftover PYQs across four sections) join their section's PYQ topic.

  python3 tools/prepladder_microbiology_edition.py   # rewrite the map from the two slim sources
  (`build_prepladder_microbiology_bank.py import-v2` also rewrites it.)
"""
from __future__ import annotations

import collections
import difflib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EDITION_MAP = ROOT / "data/Prepladder/microbiology/source/edition_map.json"
V2_LABEL = "PrepLadder November 2025 edition"
V2_PREFIX = "PLV2_"
SAME_EXPLANATION = 0.9

# Lessons 44-48 hold leftover PYQs from every section. A matched question
# follows its Version X topic; these new ones are placed by subject matter.
LEFTOVER_TOPICS = {
    "PREPLADDER_MICRO_L44_Q002": 37,  # Enterobius egg (Parasitology PYQs)
    "PREPLADDER_MICRO_L44_Q003": 37,  # nocturnal perianal itching
    "PREPLADDER_MICRO_L44_Q004": 37,  # filarial limb swelling
    "PREPLADDER_MICRO_L45_Q001": 6,   # microscope condenser (General Microbiology PYQs)
    "PREPLADDER_MICRO_L46_Q002": 6,   # incubation periods, bacteria and viruses (General Microbiology PYQs)
}

# The source PDF's font lost these characters (it prints a ■ placeholder).
# Each is restored from its context; a value the context cannot give is
# described rather than guessed.
GLYPH_FIXES = [
    (r"H■O■", "H₂O₂"), (r"CO■", "CO₂"), (r"\bN■", "N₂"), (r"SpO■", "SpO₂"), (r"CTX■", "CTXφ"),
    (r"\brF■", "rF⁻"), (r"\bF■", "F⁻"), (r"121 ■", "121 °C"), (r"at 4■", "at 4 °C"),
    (r"group B ■- hemolytic", "group B β-hemolytic"), (r"gram ■ \(", "gram-negative ("),
    (r"Occupies ■(\s*)rd of", r"Occupies 1/3rd\1of"), (r"Occupies ■(\s*)of(\s*)RBC", r"Occupies a smaller\1fraction of\2RBC"),
    (r"■r■οglοbulinemi■", "Cryoglobulinemia"), (r"glοm■r■l■■■■hritis", "glomerulonephritis"),
]
# Whatever is left is a lost icon or bullet: drop it.
GLYPH_LEFT = re.compile(r"[ \t]*■[■ \t]*")


def fix_glyphs(text: str) -> str:
    for pattern, value in GLYPH_FIXES:
        text = re.sub(pattern, value, text)
    text = GLYPH_LEFT.sub(lambda m: " " if m.start() and m.end() < len(text) and text[m.end()] != "\n" else "", text)
    return re.sub(r" +([.,;:])", r"\1", text)


def fix_record(q: dict) -> dict:
    """Restore lost characters in every learner-facing string of a slim record."""
    def walk(value, key=""):
        if isinstance(value, str):
            return value if key in ("image_id", "table_id", "id", "type") else fix_glyphs(value)
        if isinstance(value, list):
            return [walk(v, key) for v in value]
        if isinstance(value, dict):
            return {k: walk(v, k) for k, v in value.items()}
        return value
    q = dict(q)
    for field in ("question", "options", "stem_tables", "explanation_blocks"):
        q[field] = walk(q[field], field)
    return q


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(text).lower().replace("**", "")).strip()


def words(value) -> list[str]:
    out: list[str] = []

    def walk(v):
        if isinstance(v, str):
            out.append(v)
        elif isinstance(v, list):
            for item in v:
                walk(item)
        elif isinstance(v, dict):
            for k, item in v.items():
                if k not in ("type", "image_id", "table_id"):
                    walk(item)
    walk(value)
    return norm(" ".join(out)).split()


def option_set(q: dict) -> tuple:
    return tuple(sorted(norm(o["text"]) for o in q["options"]))


def answer_text(q: dict) -> str | None:
    letters = [o["id"].strip().upper() for o in q["options"]]
    key = q["correct_options_list"][0].strip().upper()
    return norm(q["options"][letters.index(key)]["text"]) if key in letters else None


def similarity(a, b) -> float:
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


def same_answer(old: dict, new: dict) -> bool:
    """The new key is the new option closest to Version X's keyed option, so a
    reworded option ("EI Tor" / "El Tor") is not an answer change."""
    key = answer_text(old)
    texts = [norm(o["text"]) for o in new["options"]]
    best = max(range(len(texts)), key=lambda i: similarity(key or "", texts[i]))
    return texts[best] == answer_text(new)


def match(old: list[dict], new: list[dict]) -> list[tuple]:
    """Pair each new question with at most one Version X question."""
    exact = collections.defaultdict(list)
    for o in old:
        exact[(norm(o["question"]), option_set(o))].append(o)
    used: set[str] = set()
    rows, pending = [], []
    for n in new:
        hits = [o for o in exact.get((norm(n["question"]), option_set(n)), []) if o["id"] not in used]
        if hits:
            used.add(hits[0]["id"])
            rows.append((n, hits[0], "unchanged" if same_answer(hits[0], n) else "answer_changed", 1.0))
        else:
            pending.append(n)
    # Reworded questions: stem similarity plus option overlap, best pairs first.
    candidates = []
    rest = [o for o in old if o["id"] not in used]
    for n in pending:
        stem, opts = norm(n["question"]), set(option_set(n))
        for o in rest:
            other = set(option_set(o))
            jaccard = len(opts & other) / max(1, len(opts | other))
            if jaccard < 0.34 and similarity(stem[:80], norm(o["question"])[:80]) < 0.6:
                continue
            ss = similarity(stem, norm(o["question"]))
            score = 0.6 * ss + 0.4 * jaccard
            if (jaccard == 1 and ss >= 0.45) or (ss >= 0.9 and jaccard >= 0.5) or score >= 0.8:
                candidates.append((score, n["id"], o["id"]))
    candidates.sort(reverse=True)
    by_new, by_old, done = {n["id"]: n for n in pending}, {o["id"]: o for o in old}, set()
    for score, nid, oid in candidates:
        if nid in done or oid in used:
            continue
        done.add(nid)
        used.add(oid)
        n, o = by_new[nid], by_old[oid]
        rows.append((n, o, "edited" if same_answer(o, n) else "edited_answer_changed", round(score, 3)))
    rows += [(n, None, "new", 0.0) for n in pending if n["id"] not in done]
    order = {n["id"]: i for i, n in enumerate(new)}
    return sorted(rows, key=lambda r: order[r[0]["id"]])


def topic_for(n: dict, o: dict | None) -> int:
    lesson = int(n["module_index"])
    if lesson <= 6:
        return lesson
    if lesson == 7:
        return 6
    if lesson <= 43:
        return lesson - 1
    if o:
        return int(o["module_index"])
    return LEFTOVER_TOPICS[n["id"]]


def same_stem_with_table(new: dict, old: dict) -> bool:
    """The new PDF flattens a Match-the-following table into the stem text;
    if those are the old stem's and table's words, Version X still says it."""
    if not old["stem_tables"]:
        return False
    have = collections.Counter(words([old["question"], old["stem_tables"]]))
    need = collections.Counter(norm(new["question"]).split())
    return sum((need - have).values()) <= 0.1 * sum(need.values())


def explanation_words(q: dict) -> list[str]:
    return words([b for b in q["explanation_blocks"] if b["type"] != "image"])


def build_map(old: list[dict], new: list[dict]) -> dict:
    rows = match(old, new)
    entries = []
    for n, o, status, score in rows:
        new_words = explanation_words(n)
        blank = len([w for w in new_words if re.search("[a-z]{2}", w)]) < 8
        same = similarity(explanation_words(o), new_words) if o else 0.0
        if o and blank:
            explanation = "x"
        elif o and status in ("unchanged", "edited") and same >= SAME_EXPLANATION:
            explanation = "x"
        else:
            explanation = "v2"
        entries.append({
            "v2Id": n["id"], "prepladderQid": n["prepladder_qid"], "xId": o["id"] if o else None,
            "status": status, "matchScore": score, "explanationSimilarity": round(same, 3),
            "stem": "x" if status in ("unchanged", "answer_changed") or (o and same_stem_with_table(n, o)) else "v2",
            "explanation": explanation, "v2ExplanationBlank": blank, "topic": topic_for(n, o),
        })
    matched = {e["xId"] for e in entries if e["xId"]}
    keys = collections.Counter()
    for o in old:
        if o["id"] in matched:
            keys[(norm(o["question"]), option_set(o))] += 1
    kept, duplicates = [], []
    for o in old:
        if o["id"] in matched:
            continue
        (duplicates if keys[(norm(o["question"]), option_set(o))] else kept).append(o["id"])
    return {
        "schemaVersion": 1,
        "editions": {"x": "PrepLadder Version X", "v2": V2_LABEL},
        "rules": "tools/prepladder_microbiology_edition.py",
        "counts": dict(collections.Counter(e["status"] for e in entries),
                       xOnlyKept=len(kept), xOnlyDuplicates=len(duplicates),
                       explanationFromX=sum(e["explanation"] == "x" for e in entries)),
        "questions": entries, "xOnlyKept": kept, "xOnlyDuplicates": duplicates,
    }


def main() -> None:
    sys.path.insert(0, str(ROOT / "tools"))
    from build_prepladder_microbiology_bank import load_source, load_v2_source

    value = build_map(load_source(), load_v2_source())
    EDITION_MAP.write_text(json.dumps(value, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"PREPLADDER_MICROBIOLOGY_EDITION_MAP_OK {value['counts']}")


if __name__ == "__main__":
    main()
