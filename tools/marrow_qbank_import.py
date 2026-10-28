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

ZERO_WIDTH = re.compile("[​‌‍⁠﻿­]")
HEAD = re.compile(r"^\s*<p>\s*<strong>\s*Correct answer:.*?</strong>\s*</p>", re.S | re.I)
TAIL = re.compile(r"(?:\s*<p>\s*(?:@neet_pg_bot|&nbsp;|\s)*</p>)+\s*$", re.I)
# Analytics beacons pasted into a few explanations are not figures.
NOT_FIGURES = ("datapro.website",)
AGENT = "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Mobile Safari/537.36"


def clean(text: str) -> str:
    return ZERO_WIDTH.sub("", str(text or "")).replace(" ", " ").strip()


def tests_list(html: Path) -> list[dict]:
    text = html.read_text(encoding="utf-8")
    # The first match sits in a code comment; the data is the last assignment.
    start = [m.end() for m in re.finditer(r"const TESTS_LIST\s*=\s*", text)][-1]
    value, _ = json.JSONDecoder().raw_decode(text, start)
    return value


def explanation_html(raw: str) -> str:
    body = clean(raw)
    body = HEAD.sub("", body, count=1)
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
                                   "url": url, "name": f"{qid}_{role}{n}"})
                    jobs.append((url, visuals, f"{qid}_{role}{n}"))
            rows.append({
                "qid": qid, "lesson": lesson_index, "lessonTitle": re.sub(r"\s+", " ", title).strip(),
                "testId": test["id"], "number": number,
                "question": clean(q.get("raw_text") or q.get("text")),
                "options": [{"letter": clean(o["label"]).upper(), "text": clean(o["text"]), "correct": bool(o["correct"])}
                            for o in q["options"]],
                "correctAnswer": clean(q.get("correct_answer")),
                "explanationHtml": explanation_html(q.get("explanation") or ""),
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
