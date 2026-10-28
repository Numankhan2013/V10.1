#!/usr/bin/env python3
"""Import Marrow QBank subjects from the saved Marrow web export (marrowqbank.html).

The export carries every test as `const TESTS_LIST = [...]`: one test per
lesson, with each question's clean stem (`raw_text`), options with the key,
the explanation as HTML, and the original image URLs. This tool keeps only
what the bank needs and writes, per subject (tools/marrow_qbank_bank.py SUBJECTS):

  data/marrow/qbank/<slug>/source.jsonl     one question per line, lesson order
  data/marrow/qbank/<slug>/visuals/<QID>_<q|e><n>.<ext>
                                            figures, byte-for-byte as served

Images are never re-encoded: the file is the original download. The text is
cleaned of the export's zero-width watermark characters only; the leading
"Correct answer: ..." line and the trailing bot signature are dropped from the
explanation (the app shows the key itself).

  python3 -I tools/marrow_qbank_import.py <marrowqbank.html> [slug ...]
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import sys
import threading
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from marrow_qbank_bank import QBANK, SUBJECTS  # noqa: E402

CONTROL = re.compile("[\x00-\x08\x0b\x0c\x0e-\x1f\x7f\u2028\u2029]")
ZERO_WIDTH = re.compile("[​‌‍⁠﻿­]")
HEAD = re.compile(r"^\s*<p>\s*<strong>\s*Correct answer:.*?</strong>\s*</p>", re.S | re.I)
TAIL = re.compile(r"(?:\s*<p>\s*(?:@neet_pg_bot|&nbsp;|\s)*</p>)+\s*$", re.I)
# Analytics beacons pasted into a few explanations are not figures.
NOT_FIGURES = ("datapro.website",)
# The export moved every explanation figure to the end. Where one sat it left an empty captioned
# figure (its caption a "{{caption_text}}" template), a paragraph with nothing at all in it, or an
# empty centred paragraph; a paragraph holding only a space is the author's spacing.
FIGURE_SPOT = re.compile(
    r"(?P<caption>(?P<wrap><div style=\"text-align:\s*center;?\">\s*)?<figure class=\"caption_element\"[^>]*>(?:(?!\[\[figure-).)*?</figure>"
    r"(?(wrap)\s*</div>))|(?P<bare><p(?:\s+style=\"[^\"]*\")?></p>)"
    r"|(?P<centre><p style=\"text-align:\s*center;?\">(?:[ \t\n]|&nbsp;|<br\s*/?>)*</p>)", re.S | re.I)
# Where a figure goes in the explanation; marrow_qbank_bank.place_figures turns it into a figure block.
FIGURE_MARK = "<p>[[figure-{}]]</p>"
AGENT = "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Mobile Safari/537.36"


def clean(text: str) -> str:
    text = ZERO_WIDTH.sub("", str(text or "")).replace("\xa0", " ")
    # Control characters (NUL padding, a stray \x02) and line separators the export carries.
    return CONTROL.sub(lambda m: " " if m.group(0) in "\u2028\u2029" else "", text).strip()


def tests_list(html: Path) -> list[dict]:
    text = html.read_text(encoding="utf-8")
    # The first match sits in a code comment; the data is the last assignment.
    start = [m.end() for m in re.finditer(r"const TESTS_LIST\s*=\s*", text)][-1]
    value, _ = json.JSONDecoder().raw_decode(text, start)
    return value


def is_figure(url: str) -> bool:
    # SVGs in the export are PrepLadder's own interface icons (24 px "expand" arrows).
    return not any(h in url for h in NOT_FIGURES) and not url.split("?")[0].lower().endswith(".svg")


def mark_figure_spots(body: str, figures: int) -> str:
    """Mark the spot of each explanation figure, in order, where the export's empty spots match them one to one.

    Captioned spots are the surest sign and centred paragraphs the weakest: when the surer kinds alone match
    the figures, the others are only spacing. Figures without a matched spot are placed by the builder (before the references)."""
    spots = list(FIGURE_SPOT.finditer(body))
    tiers = (spots, [s for s in spots if not s.group("centre")], [s for s in spots if s.group("caption")])
    chosen = next((tier for tier in tiers if len(tier) == figures), [])
    marks = {s.start(): FIGURE_MARK.format(n) for n, s in enumerate(chosen, 1)}
    # Unmatched captioned spots are dropped (their caption is only the template); empty paragraphs stay as spacing.
    return FIGURE_SPOT.sub(lambda s: marks.get(s.start(), "" if s.group("caption") else s.group(0)), body)


def explanation_html(raw: str, figures: int = 0) -> str:
    body = clean(raw)
    body = HEAD.sub("", body, count=1)
    body = mark_figure_spots(body, figures).replace("{{caption_text}}", "")
    body = TAIL.sub("", body)
    return body.strip()


def sniff(data: bytes) -> str:
    if data[:3] == b"\xff\xd8\xff":
        return "jpg"
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return "png"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return "gif"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    raise ValueError("not an image")


# Wikimedia answers bursts with 429, so its few files go one at a time.
SLOW_HOSTS = ("wikimedia.org",)
SLOW = threading.Lock()


def fetch(url: str) -> bytes:
    slow = any(host in url for host in SLOW_HOSTS)
    tries = 3 if slow else 7
    for attempt in range(tries):
        try:
            if slow:
                with SLOW:
                    time.sleep(3)
                    return _get(url)
            return _get(url)
        except Exception:
            if attempt == tries - 1:
                raise
            time.sleep(min(60, 2 ** attempt * (5 if slow else 1)))
    raise AssertionError


def _get(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        data = response.read()
    sniff(data)
    return data


def import_subject(slug: str, tests: list[dict]) -> None:
    cfg = SUBJECTS[slug]
    lessons = [t for t in tests if (t.get("path") or [""])[0] == cfg["folder"]]
    if not lessons:
        raise SystemExit(f"{slug}: no tests under {cfg['folder']!r}")
    lessons.sort(key=lambda t: int(str(t["title"]).split()[0]))
    out = QBANK / slug
    visuals = out / "visuals"
    visuals.mkdir(parents=True, exist_ok=True)
    rows, jobs = [], []
    for lesson_index, test in enumerate(lessons, 1):
        number_text, _, title = str(test["title"]).partition(" ")
        if int(number_text) != lesson_index:
            raise SystemExit(f"{slug}: lesson numbers are not contiguous at {test['title']!r}")
        for number, q in enumerate(test["questions"], 1):
            qid = str(q["id"]).strip()
            images = []
            for role, key in (("q", "question_images"), ("e", "explanation_images")):
                urls = [u for u in q.get(key) or [] if not any(host in u for host in NOT_FIGURES)]
                for n, url in enumerate(urls, 1):
                    images.append({"role": "question" if role == "q" else "explanation", "order": n,
                                   "url": url, "name": f"{qid}_{role}{n}"} | ({"spot": n} if role == "e" else {}))
                    jobs.append((url, visuals, f"{qid}_{role}{n}"))
            rows.append({
                "qid": qid, "lesson": lesson_index, "lessonTitle": title.strip(),  # lesson_title reads its spacing
                "testId": test["id"], "number": number,
                "question": clean(q.get("raw_text") or q.get("text")),
                "options": [{"letter": clean(o["label"]).upper(), "text": clean(o["text"]), "correct": bool(o["correct"])}
                            for o in q["options"]],
                "correctAnswer": clean(q.get("correct_answer")),
                "explanationHtml": explanation_html(q.get("explanation") or "",
                                                    sum(1 for i in images if i["role"] == "explanation")),
                "images": images,
            })
    existing = {p.stem: p for p in visuals.iterdir()}

    def download(job):
        url, folder, name = job
        if name in existing:
            return name, existing[name].suffix[1:], False
        try:
            data = fetch(url)
        except Exception as error:  # reported below; the bank builder refuses a missing file
            return name, None, error
        ext = sniff(data)
        (folder / f"{name}.{ext}").write_bytes(data)
        return name, ext, True

    ext_of, fetched, missing = {}, 0, []
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
        for (url, _, _), (name, ext, new) in zip(jobs, pool.map(download, jobs)):
            if ext is None:
                missing.append(f"{name} {url} ({new})")
                continue
            ext_of[name] = ext
            fetched += new is True
    for row in rows:
        for image in row["images"]:
            name = image.pop("name")
            # A pending download keeps the URL's extension until it arrives.
            guess = Path(image["url"].split("?")[0]).suffix.lower().lstrip(".").replace("jpeg", "jpg") or "jpg"
            image["file"] = f"{name}.{ext_of.get(name, guess)}"
    with (out / "source.jsonl").open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    print(f"MARROW_QBANK_IMPORT_OK {slug} lessons={len(lessons)} questions={len(rows)} "
          f"images={len(jobs)} downloaded={fetched} pending={len(missing)}")
    for line in missing:
        print("  PENDING", line)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("html", type=Path)
    parser.add_argument("slugs", nargs="*")
    args = parser.parse_args()
    tests = tests_list(args.html)
    for slug in args.slugs or list(SUBJECTS):
        import_subject(slug, tests)


if __name__ == "__main__":
    main()
