#!/usr/bin/env python3
"""Trim extraction borders (frame lines, black bars, padding) from figure JPEGs.

From each side inward: cross the outer white/black margin, then at most one thin
frame line, then any black bar right inside it, and stop. Whitespace inside a frame
is the figure's own and stays. Without a frame, white margin is cut down to PAD px.

Used when importing extracted QBank figures (tools/build_prepladder_microbiology_bank.py
and the Marrow Microbiology visuals). Committed figures are already trimmed; the app
build never re-trims.

  python3 tools/figure_trim.py <file.jpg>...   # print the crop box each file would get
"""
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image

TOL = 22          # per-channel distance from the line median that still counts as uniform
SHARE = 0.985     # share of a line's pixels that must be uniform
INSET = 0.10      # ignore this share at each end of a line (rounded frame corners)
MAX_TRIM = 0.30   # never cut more than this share of a side
PAD = 6           # white margin kept around frameless content
FRAME = 4         # thickest line run treated as a frame
INK = 90          # a deviation this strong is a mark, never JPEG noise


def kind(med):
    if med.min() >= 238 and med.max() - med.min() <= 12: return "white"
    if med.max() <= 45 and med.max() - med.min() <= 20: return "black"
    if med.max() - med.min() <= 20: return "neutral"
    return "colour"


def line_kinds(a, side, limit):
    h, w = a.shape[:2]
    out = []
    for i in range(limit):
        if side == "t": px = a[i, :]
        elif side == "b": px = a[h - 1 - i, :]
        elif side == "l": px = a[:, i]
        else: px = a[:, w - 1 - i]
        m = len(px); lo = int(m * INSET); px = px[lo:m - lo]
        med = np.median(px, axis=0)
        dev = np.abs(px - med).max(axis=1)
        # Any strong ink (a letter stroke in a tall white column) makes the line content.
        uniform = (dev <= TOL).mean() >= SHARE and dev.max() <= INK
        out.append(kind(med) if uniform else "content")
    return out + ["content"]


def cut_side(a, side):
    n = a.shape[0] if side in "tb" else a.shape[1]
    limit = int(n * MAX_TRIM)
    ks = line_kinds(a, side, limit)
    i = 0
    while ks[i] in ("white", "black"):
        i += 1
    margin_end = i
    j = i
    while ks[j] in ("neutral", "colour"):
        j += 1
    run = j - i
    if 0 < run <= FRAME and ks[j] != "content":
        i = j  # crossed a frame line that has space inside it
        while ks[i] == "black":
            i += 1
        return i if i < limit else 0
    if margin_end >= limit:
        return 0  # a plain field to the limit is content, not margin
    # Frameless (or a thin grey line hugging content, which is the figure's own
    # edge): keep PAD px of white margin, cut black margin entirely.
    keep = 0
    while keep < PAD and margin_end - keep - 1 >= 0 and ks[margin_end - keep - 1] == "white":
        keep += 1
    return margin_end - keep


def trim_box(img):
    a = np.asarray(img.convert("RGB")).astype(np.int16)
    h, w = a.shape[:2]
    c = {side: cut_side(a, side) for side in "tblr"}
    box = (c["l"], c["t"], w - c["r"], h - c["b"])
    if box[2] - box[0] < w * 0.4 or box[3] - box[1] < h * 0.4:
        return (0, 0, w, h)
    return box


def trim_file(src: Path, dst: Path) -> tuple[int, int, int, int] | None:
    """Write the trimmed figure to dst; an untouched figure is copied byte for byte."""
    with Image.open(src) as img:
        img.load()
        box = trim_box(img)
        if box == (0, 0, img.width, img.height):
            shutil.copyfile(src, dst)
            return None
        img.convert("RGB").crop(box).save(dst, "JPEG", quality=92, optimize=True)
        return box


if __name__ == "__main__":
    for name in sys.argv[1:]:
        with Image.open(name) as img:
            print(name, img.size, trim_box(img))
