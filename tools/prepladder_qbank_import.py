#!/usr/bin/env python3
"""Import PrepLadder Version XI from the owner's three saved web exports.

  QBank        `PrepLadder Version XI QBank.html`       (const TESTS_LIST): every lesson test in lecture
                                                         order, each topic followed by its PYQ test.
  Elite QBank  `PrepLadder Version XI Elite QBank.html` (const DATA): the revised edition of the same
                                                         questions (same IDs), regrouped by topic.
  All PYQs     `All PYQs PrepLadder.html`               (const TESTS_LIST): past papers by exam and year.

One question per PrepLadder ID, merged as follows (decided 2026-10-28, see
docs/PREPLADDER_QBANK_HTML.md):

  * lessons are the QBank tests, in order; a question listed by several tests stays in the first;
  * the text, options, key and explanation are the Elite revision where Elite has the ID, else QBank's;
    where Elite reuses an ID for a different question (stem similarity < 0.6) the earlier QBank
    question is kept as well, as `<QID>-v1`, right after it;
  * Elite-only and PYQ-only questions join the lesson of their nearest question (word overlap);
    a past-paper question joins the first PYQ lesson at or after that lesson;
  * every question in the PYQ file carries its exams ("INI-CET 2026");
  * each lesson's section is the Elite topic most of its questions belong to.

Subjects the app already has from the PDFs (Anatomy, Physiology, Biochemistry, Microbiology,
Pathology, Pharmacology) keep their banks; only questions they lack are written, each mapped to
the existing lesson that the matched questions of its test sit in.

  data/Prepladder/qbank/<slug>/source.jsonl     one question per line
  data/Prepladder/qbank/<slug>/visuals/<QID>_<q|e><n>.<ext>   original figures, never re-encoded

  python3 -I tools/prepladder_qbank_import.py <qbank.html> <elite.html> <pyq.html> [slug ...] [--no-download]
"""
from __future__ import annotations

import argparse
import collections
import concurrent.futures
import difflib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from marrow_qbank_import import NOT_FIGURES, ZERO_WIDTH, clean, fetch, sniff, tests_list  # noqa: E402
from prepladder_qbank_bank import QBANK, SUBJECTS, existing_bank  # noqa: E402

HEAD = re.compile(r"^(?:\s*<p>\s*<strong>\s*Correct answer\s*:.*?</strong>\s*</p>)+", re.S | re.I)
# A second "Correct Answer: B) ..." line repeats the pre-shuffle letter; the app shows the key itself.
HEAD2 = re.compile(r"^\s*<p>\s*<strong>\s*Correct\s+Answer\s*:?\s*[A-D]?\s*[).:-]?.*?</strong>\s*</p>", re.S | re.I)
LEAD_LABEL = re.compile(r"^\s*(?:<p>\s*(?:&nbsp;|\s)*</p>\s*)*<p>\s*<strong>\s*Explanation\s*</strong>\s*:?\s*</p>", re.I)
BOT = re.compile(r"<p>\s*@neet_pg_bot\s*</p>", re.I)
IMG_P = re.compile(r"<p>\s*(?:<img\b[^>]*>\s*)+</p>|<img\b[^>]*>", re.I)
# One blank paragraph or break at the very end; trimmed in a loop (a repeated group backtracks badly).
EMPTY_TAIL = re.compile(r"(?:<p>(?:&nbsp;|\s|<br\s*/?>)*</p>|<br\s*/?>)$", re.I)
IMG_SRC = re.compile(r"<img\b[^>]*\bsrc=\"([^\"]+)\"", re.I)
INDEXES = QBANK / "indexes.json"
ROMAN = {"i", "ii", "iii", "iv", "v", "vi"}
SMALL_WORDS = {"a", "an", "and", "as", "at", "by", "for", "in", "of", "on", "or", "the", "to", "vs", "with"}
ACRONYMS = set("""abg aids aki all aml ards asd asom aub bcg bns ckd cin cll cml cns copd cpa cpcr csf csom ct dic dsd
dvt ecg ent gerd gi gtn hcc hie hiv hpv hus ibd ibs iem ipc itp iud ivf jna malt men mi mri nacp nafld nash nec nlep
npcds nrega ntep nvbdcp obg ocd ocp pac pbc pcos pda pph psc ptsd rds rhd rmncha rta sle som std sti tb tga tia
tof ttp usg uti vbac vsd vte esi htn chf bbb dka pkd g6pd eeg sah icp ali abg puo bcls acls aha als pacg poag
nrega ncd ncds ppiud iucd dmpa mtp ctg nst bpp pcpndt hsg ivf icsi iui ohss pid tvs lh fsh hcg afp ldh psa bph
turp pcnl eswl rcc tcc mcdk pud gist fap hnpcc ercp mrcp ptc fna fnac mibg ptsd adhd asd mr cbt ect ssri snri
tca maoi gad ocd bpad mdd ptsd nmda gaba ct mri pet spect usg xray kub ivu mcu hrct dexa""".split())
# The export's own misspellings and lost punctuation, fixed in lesson titles.
TITLE_FIXES = {"Covid 19": "COVID-19", "M N Trier": "Ménétrier", "Protienosis": "Proteinosis",
               "Guillian Barre": "Guillain-Barré", "Syringomelia": "Syringomyelia", "Hepatitits": "Hepatitis",
               "Epidemology": "Epidemiology", "HIV AIDS": "HIV/AIDS", "Non Hodgkin's": "Non-Hodgkin's",
               "Anti Phospholipid": "Antiphospholipid", "Pneumocystis Jirovecii": "Pneumocystis jirovecii",
               "Sjogren": "Sjögren", "Ali I": "ALI I", "Ali II": "ALI II"}
EXAM = {"neet pg": "NEET PG", "ini cet": "INI-CET", "fmge": "FMGE", "aiims": "AIIMS"}


def words(text: str) -> set[str]:
    plain = re.sub(r"<[^>]+>", " ", ZERO_WIDTH.sub("", text or ""))
    return {w for w in re.sub(r"\W+", " ", plain).lower().split() if len(w) > 2}


def norm(text: str) -> str:
    plain = re.sub(r"<[^>]+>", " ", ZERO_WIDTH.sub("", text or ""))
    return re.sub(r"\W+", " ", plain).lower().strip()


def explanation_html(raw: str) -> str:
    body = ZERO_WIDTH.sub("", str(raw or "")).replace(" ", " ")
    body = HEAD.sub("", body, count=1)
    body = HEAD2.sub("", body, count=1)
    body = LEAD_LABEL.sub("", body, count=1)
    body = IMG_P.sub("", body)
    body = BOT.sub("", body)
    body = body.strip()
    while (tail := EMPTY_TAIL.search(body)):
        body = body[:tail.start()].rstrip()
    return body


def elite_data(html: Path) -> list[dict]:
    text = html.read_text(encoding="utf-8")
    start = text.index("const DATA =") + len("const DATA =")
    while text[start].isspace():
        start += 1
    value, _ = json.JSONDecoder().raw_decode(text, start)
    return value["questions"]


def from_qbank(q: dict) -> dict:
    options = [{"letter": clean(o["label"]).upper(), "text": clean(o["text"]), "correct": bool(o["correct"])}
               for o in q["options"]]
    return {"question": clean(q.get("raw_text") or q.get("text")), "options": options,
            "explanationHtml": explanation_html(q.get("explanation")),
            "images": [("question", u) for u in q.get("question_images") or []]
            + [("explanation", u) for u in q.get("explanation_images") or []]}


def from_elite(q: dict) -> dict:
    options = [{"letter": k, "text": clean(v), "correct": k == q["ans"]} for k, v in sorted(q["options"].items())]
    images = [("question", q["img"])] if q.get("img") else []
    images += [("explanation", u) for u in IMG_SRC.findall(q.get("expl") or "")]
    return {"question": clean(q.get("text")), "options": options,
            "explanationHtml": explanation_html(q.get("expl")), "images": images}


def exam_label(title: str) -> str:
    _, _, rest = title.partition(" ")
    year, _, exam = rest.partition(" ")
    return f"{EXAM.get(exam.lower().strip(), exam.strip())} {year}"


class Nearest:
    """Nearest placed question by word overlap (Jaccard), through an inverted index."""

    def __init__(self):
        self.rows: list[tuple[set[str], dict]] = []
        self.index: dict[str, list[int]] = collections.defaultdict(list)

    def add(self, row: dict) -> None:
        ws = words(row["question"])
        for w in ws:
            self.index[w].append(len(self.rows))
        self.rows.append((ws, row))

    def find(self, text: str) -> tuple[dict | None, float]:
        ws = words(text)
        votes = collections.Counter()
        for w in ws:
            hits = self.index.get(w, [])
            if len(hits) < 400:
                votes.update(hits)
        best, score = None, 0.0
        for i, _ in votes.most_common(25):
            other, row = self.rows[i]
            j = len(ws & other) / max(1, len(ws | other))
            if j > score:
                best, score = row, j
        return best, score


def merge(slug: str, qbank: list[dict], elite: list[dict], pyq: list[dict]) -> tuple[list[dict], dict]:
    cfg = SUBJECTS[slug]
    folder = cfg["folder"]
    tests = sorted((t for t in qbank if (t.get("path") or [""])[0] == folder), key=lambda t: int(t["title"].split()[0]))
    if not tests:
        raise SystemExit(f"{slug}: no QBank tests under {folder!r}")
    elite_by = {}
    for q in elite:
        if q["subject"] == folder:
            elite_by.setdefault(q["id"].rsplit("_", 1)[-1], q)
    exams = collections.defaultdict(list)
    pyq_by = {}
    for t in pyq:
        if (t.get("path") or [""])[0] != folder:
            continue
        for q in t["questions"]:
            exams[str(q["id"])].append(exam_label(t["title"]))
            pyq_by.setdefault(str(q["id"]), q)
    lessons, rows, seen = [], [], set()
    stats = collections.Counter()
    for n, test in enumerate(tests, 1):
        number, _, title = test["title"].partition(" ")
        lesson = {"lesson": n, "sourceNumber": int(number), "title": re.sub(r"\s+", " ", title).strip(),
                  "pyq": "previous year" in title.lower(), "testId": test["id"], "rows": []}
        lessons.append(lesson)
        for q in test["questions"]:
            qid = str(q["id"]).strip()
            if qid in seen:
                stats["repeatedInQbank"] += 1
                continue
            seen.add(qid)
            old = from_qbank(q)
            if qid in elite_by:
                new = from_elite(elite_by[qid])
                lesson["rows"].append({"qid": qid, "origin": "elite", **new})
                stats["elite"] += 1
                if norm(new["question"]) != norm(old["question"]):
                    stats["eliteRevisedStem"] += 1
                    ratio = difflib.SequenceMatcher(None, norm(old["question"]), norm(new["question"])).ratio()
                    if ratio < 0.6:
                        lesson["rows"].append({"qid": f"{qid}-v1", "origin": "qbank-earlier", **old})
                        stats["earlierKept"] += 1
            else:
                lesson["rows"].append({"qid": qid, "origin": "qbank", **old})
                stats["qbank"] += 1
    near = Nearest()
    for lesson in lessons:
        for row in lesson["rows"]:
            row["_lesson"] = lesson["lesson"]
            near.add(row)
    extras = [(qid, "elite", from_elite(q)) for qid, q in elite_by.items() if qid not in seen]
    extras += [(qid, "pyq", from_qbank(q)) for qid, q in pyq_by.items() if qid not in seen and qid not in elite_by]
    for qid, origin, data in extras:
        hit, score = near.find(data["question"])
        target = hit["_lesson"] if hit else lessons[-1]["lesson"]
        if origin == "pyq":
            later = [l["lesson"] for l in lessons if l["pyq"] and l["lesson"] >= target]
            target = later[0] if later else target
        lessons[target - 1]["rows"].append({"qid": qid, "origin": origin, "placement": round(score, 3), **data})
        seen.add(qid)
        stats[origin + "Only"] += 1
    parts = resolve_indexes(slug, lessons, elite_by, elite)
    out = []
    for part in parts:
        lesson = part["lesson"]
        for number, row in enumerate(part["rows"], 1):
            row.pop("_lesson", None)
            images, count = [], collections.Counter()
            for role, url in row.pop("images"):
                if any(h in url for h in NOT_FIGURES):
                    continue
                count[role] += 1
                images.append({"role": role, "order": count[role], "url": url,
                               "name": f"{row['qid']}_{role[0]}{count[role]}"})
            key = [o for o in row["options"] if o["correct"]]
            out.append({**row, "lesson": part["key"], "topicOrder": part["order"], "lessonTitle": part["title"],
                        "pyq": lesson["pyq"], "section": part["section"], "sourceNumber": lesson["sourceNumber"],
                        "testId": lesson["testId"], "number": number,
                        "correctAnswer": f"{key[0]['letter']}. {key[0]['text']}" if len(key) == 1 else "",
                        "exams": sorted(set(exams.get(row["qid"].split("-")[0], [])),
                                        key=lambda e: (-int(e.split()[-1]), e)),
                        "images": images})
    return out, dict(stats)


def lesson_title(test_id: str) -> str:
    """'011_thermal_injuries___i' -> 'Thermal Injuries I'; the export keeps punctuation only as underscores."""
    s = re.sub(r"^\d+_", "", test_id)
    s = re.sub(r"_+(?=(?:i|ii|iii|iv|v|vi)$)", " ", s)
    s = s.replace("___", " & ").replace("__", ", ")
    s = re.sub(r"_s(?=_|$)", "'s", s).replace("_", " ")
    words_out = []
    for n, w in enumerate(s.split()):
        bare, tail = w.rstrip(","), "," if w.endswith(",") else ""
        low = bare.lower()
        if n and low in ROMAN:
            bare = low.upper()
        elif low in ACRONYMS:
            bare = low.upper()
        elif n and low in SMALL_WORDS:
            bare = low
        else:
            bare = low[:1].upper() + low[1:]
        words_out.append(bare + tail)
    text = " ".join(words_out)
    for wrong, right in TITLE_FIXES.items():
        text = re.sub(rf"\b{re.escape(wrong)}\b", right, text)
    return text


def resolve_indexes(slug: str, lessons: list[dict], elite_by: dict, elite_all: list[dict]) -> list[dict]:
    """Split the lesson tests into topics under the official app's indexes (data/Prepladder/qbank/indexes.json).

    A topic test takes the Elite index most of its questions carry. A Previous Year Questions test closes
    the index of the topics before it, as in the app. A test Elite lacks follows its neighbours. The curated
    file fixes the rest: index order and names, whole-test placements, and PYQ tests the app splits by index.
    """
    # Supplements file their questions under the app's own lessons; their indexes here only steer placement.
    cfg = json.loads(INDEXES.read_text(encoding="utf-8")).get(slug)
    curated = cfg is not None
    cfg = cfg or {}
    rename, tests, titles = (cfg.get(k, {}) for k in ("rename", "tests", "titles"))
    split = set(cfg.get("split", []))

    def name(elite_lesson: str) -> str:
        bare = re.sub(r"^\d+\s+", "", elite_lesson).strip()
        return rename.get(bare, bare)

    # Elite repeats some questions under several lessons; a split test files each under the most specific one.
    lessons_of: dict[str, list[str]] = collections.defaultdict(list)
    for q in elite_all:
        if q["subject"] == SUBJECTS[slug]["folder"]:
            qid = q["id"].rsplit("_", 1)[-1]
            if name(q["lesson"]) not in lessons_of[qid]:
                lessons_of[qid].append(name(q["lesson"]))

    def vote(rows: list[dict]) -> str | None:
        votes = collections.Counter(name(elite_by[r["qid"]]["lesson"]) for r in rows if r["qid"] in elite_by)
        return votes.most_common(1)[0][0] if votes else None

    number = {l["lesson"]: f"{l['sourceNumber']:03d}" for l in lessons}
    index: dict[int, str | None] = {}
    for l in lessons:
        n = number[l["lesson"]]
        index[l["lesson"]] = tests.get(n) or (None if l["pyq"] else vote(l["rows"]))
    for i, l in enumerate(lessons):  # tests Elite lacks follow their neighbours
        if index[l["lesson"]] or l["pyq"]:
            continue
        before = lessons[i - 1] if i else None
        if before and not before["pyq"] and index[before["lesson"]]:
            index[l["lesson"]] = index[before["lesson"]]
        else:
            index[l["lesson"]] = next((index[m["lesson"]] for m in lessons[i + 1:] if index[m["lesson"]]), None)
    last = None
    for l in lessons:  # Previous Year Questions close the index before them
        if l["pyq"] and not index[l["lesson"]]:
            index[l["lesson"]] = last
        last = index[l["lesson"]]
    order = cfg["order"] if curated else list(dict.fromkeys(i or "Other topics" for i in index.values()))
    parts = []
    for position, l in enumerate(lessons):
        n = number[l["lesson"]]
        if not l["rows"]:  # every question already sits in an earlier test
            continue
        title = titles.get(n) or ("Previous Year Questions" if l["pyq"] else lesson_title(l["testId"]))
        if n in split:
            groups: dict[str, list[dict]] = {}
            whole = index[l["lesson"]]
            for r in l["rows"]:
                specific = [x for x in lessons_of.get(r["qid"].split("-")[0], []) if x != whole]
                groups.setdefault(specific[0] if specific else whole, []).append(r)
            groups = dict(sorted(groups.items(), key=lambda g: g[0] != whole))
        else:
            groups = {index[l["lesson"]] or "Other topics": l["rows"]}
        for k, (section, rows) in enumerate(groups.items()):
            if section not in order:
                raise SystemExit(f"{slug} test {n}: index {section!r} is not in indexes.json order")
            parts.append({"lesson": l, "key": n if k == 0 else f"{n}-{k + 1}", "section": section,
                          "title": title, "rows": rows, "position": position})
    for src, dst in cfg.get("join", {}).items():  # a test the app files inside another test's topic
        moved = [p for p in parts if p["key"] == src]
        target = next((p for p in parts if p["key"] == dst), None)
        if len(moved) != 1 or target is None:
            raise SystemExit(f"{slug}: indexes.json joins {src} into {dst}, which do not both exist")
        target["rows"] += moved[0]["rows"]
        parts.remove(moved[0])
    used = {p["section"] for p in parts}
    unused = [o for o in order if o not in used]
    if unused:
        raise SystemExit(f"{slug}: indexes.json lists indexes with no topic: {unused}")
    parts.sort(key=lambda p: (order.index(p["section"]), p["position"]))
    for n, p in enumerate(parts, 1):
        p["order"] = n
    return parts




def supplement(slug: str, rows: list[dict]) -> tuple[list[dict], dict]:
    """Rows of a subject the app already has: keep the questions it lacks, mapped to its lessons."""
    bank = existing_bank(slug)
    have = {str(q.get("prepladderQid") or "").lstrip("Q") for q in bank["questions"]}
    topic_of = {str(q.get("prepladderQid") or "").lstrip("Q"): q["chapterId"] for q in bank["questions"]}
    known = Nearest()
    for q in bank["questions"]:
        # Earlier-edition questions carry only the keyed option number.
        keyed = int(q.get("correctOption") or 0) - 1
        answer = q.get("correctAnswerText") or (q["options"][keyed]["text"] if 0 <= keyed < len(q["options"]) else "")
        known.add({"question": q["question"], "answer": norm(answer), "topic": q["chapterId"]})
    by_test = collections.defaultdict(collections.Counter)
    for r in rows:
        if r["qid"] in topic_of:
            by_test[r["testId"]][topic_of[r["qid"]]] += 1
    out, stats = [], collections.Counter()
    for r in rows:
        if r["qid"].split("-")[0] in have:
            stats["inApp"] += 1
            continue
        hit, score = known.find(r["question"])
        key = next((o["text"] for o in r["options"] if o["correct"]), "")
        if hit and score >= 0.85 and hit["answer"] == norm(key):
            stats["sameAsAppQuestion"] += 1  # the PDF bank has it under another number
            continue
        votes = by_test.get(r["testId"])
        if votes:
            topic = votes.most_common(1)[0][0]
        elif hit:
            topic = hit["topic"]
        elif out:  # no shared words at all (an image-only stem): the lesson of the question before it
            topic = out[-1]["topicId"]
            stats["placedByOrder"] += 1
        else:
            raise SystemExit(f"{slug}: no lesson for {r['qid']}")
        out.append({**r, "topicId": topic})
        stats["added"] += 1
    counts = collections.Counter(r["topicId"] for r in out)
    order = {t["id"]: i for i, t in enumerate(bank["topics"])}
    out.sort(key=lambda r: (order[r["topicId"]], r["topicOrder"], r["number"]))
    seq = collections.Counter()
    for r in out:
        seq[r["topicId"]] += 1
        r["number"] = seq[r["topicId"]]
    stats["topics"] = len(counts)
    return out, dict(stats)


def download(slug: str, rows: list[dict]) -> None:
    visuals = QBANK / slug / "visuals"
    visuals.mkdir(parents=True, exist_ok=True)
    existing = {p.stem: p for p in visuals.iterdir()}
    jobs = [(i["url"], i["name"]) for r in rows for i in r["images"]]

    def get(job):
        url, name = job
        if name in existing:
            return name, existing[name].suffix[1:], False
        try:
            data = fetch(url)
        except Exception as error:  # reported; the builder refuses a missing file
            return name, None, error
        ext = sniff(data)
        (visuals / f"{name}.{ext}").write_bytes(data)
        return name, ext, True

    ext_of, missing, fetched = {}, [], 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
        for (url, _), (name, ext, new) in zip(jobs, pool.map(get, jobs)):
            if ext is None:
                missing.append(f"{name} {url} ({new})")
                continue
            ext_of[name] = ext
            fetched += new is True
    for r in rows:
        for image in r["images"]:
            name = image.pop("name")
            guess = Path(image["url"].split("?")[0]).suffix.lower().lstrip(".").replace("jpeg", "jpg") or "jpg"
            image["file"] = f"{name}.{ext_of.get(name, guess)}"
    print(f"  figures={len(jobs)} downloaded={fetched} pending={len(missing)}")
    for line in missing:
        print("  PENDING", line)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("qbank", type=Path)
    parser.add_argument("elite", type=Path)
    parser.add_argument("pyq", type=Path)
    parser.add_argument("slugs", nargs="*")
    parser.add_argument("--no-download", action="store_true")
    args = parser.parse_args()
    qbank, elite, pyq = tests_list(args.qbank), elite_data(args.elite), tests_list(args.pyq)
    for slug in args.slugs or list(SUBJECTS):
        rows, stats = merge(slug, qbank, elite, pyq)
        if SUBJECTS[slug].get("supplement"):
            rows, extra = supplement(slug, rows)
            stats.update(extra)
        if args.no_download:
            for r in rows:
                for image in r["images"]:
                    image["file"] = image.pop("name") + ".jpg"
        else:
            download(slug, rows)
        folder = QBANK / slug
        folder.mkdir(parents=True, exist_ok=True)
        with (folder / "source.jsonl").open("w", encoding="utf-8") as handle:
            for r in rows:
                handle.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n")
        print(f"PREPLADDER_QBANK_IMPORT_OK {slug} questions={len(rows)} {json.dumps(stats, sort_keys=True)}")


if __name__ == "__main__":
    main()
