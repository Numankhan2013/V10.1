#!/usr/bin/env python3
"""Draw the markers a question asks about onto figures that print without them.

PrepLadder's PDFs print some question figures bare ("Identify the marked
structure", options 1-4) because its app draws the markers on top. The markers
live in data/Prepladder/<bank>/figure_markers.json, each placed from the
question's own explanation and labelled explanation figure. This tool draws
them onto the figure file and updates the bank's visuals.json.

  python3 tools/draw_figure_markers.py anatomy           # draw (bare figures only)
  python3 tools/draw_figure_markers.py anatomy --check   # fail unless every figure is marked

A figure is drawn only while it is the bare figure (source_sha256), so the
tool can run again after an import brings the bare figures back.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FONT = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
DOT, LINE = "#e06055", "#6fb3cf"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def draw(path: Path, spec: dict) -> bytes:
    from PIL import Image, ImageDraw, ImageFont

    image = Image.open(path).convert("RGB")
    pen = ImageDraw.Draw(image)
    unit = image.width / 1000  # strokes and type scale with the figure
    font = ImageFont.truetype(FONT, round(34 * unit))
    for label in spec.get("labels", []):
        # A leader from the point to its number, which sits left or right of it.
        (px, py), (ax, ay) = label["point"], label["at"]
        side = 1 if ax > px else -1
        pen.line([(px, py), (ax - side * 12 * unit, ay)], fill=LINE, width=max(2, round(2.5 * unit)))
        r = 6 * unit
        pen.ellipse([px - r, py - r, px + r, py + r], fill=DOT)
        pen.text((ax, ay), label["text"], font=font, fill="#111111", anchor="lm" if side > 0 else "rm")
    for arrow in spec.get("arrows", []):
        (tx, ty), (sx, sy) = arrow["tip"], arrow["tail"]
        angle, head, width = math.atan2(ty - sy, tx - sx), 22 * unit, max(3, round(5 * unit))
        base = (tx - head * math.cos(angle), ty - head * math.sin(angle))
        wing = [(base[0] + head * 0.55 * math.cos(angle + s * math.pi / 2),
                 base[1] + head * 0.55 * math.sin(angle + s * math.pi / 2)) for s in (1, -1)]
        outline = "#ffffff" if arrow["color"] != "#ffffff" else "#111111"
        pen.line([(sx, sy), base], fill=outline, width=width + round(3 * unit))
        pen.polygon([(tx, ty), *wing], fill=arrow["color"], outline=outline)
        pen.line([(sx, sy), base], fill=arrow["color"], width=width)
        pen.polygon([(tx, ty), *wing], fill=arrow["color"])
    out = io.BytesIO()
    image.save(out, "JPEG", quality=92)
    return out.getvalue()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("bank")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = ROOT / "data/Prepladder" / args.bank
    markers_path, inventory_path = data / "figure_markers.json", data / "visuals.json"
    markers, inventory = (json.loads(p.read_text(encoding="utf-8")) for p in (markers_path, inventory_path))
    figures = {f["imageId"]: f for f in inventory["figures"]}
    drawn = 0
    for image_id, spec in markers["figures"].items():
        figure = figures[image_id]
        path = ROOT / figure["file"]
        current = sha(path.read_bytes())
        if current == spec.get("sha256") and figure["sha256"] == current:
            continue
        if args.check:
            raise SystemExit(f"FIGURE_MARKERS_FAIL {image_id} is not the marked figure; run tools/draw_figure_markers.py {args.bank}")
        if current != spec.setdefault("source_sha256", current):
            raise SystemExit(f"FIGURE_MARKERS_FAIL {image_id} is neither the bare nor the marked figure")
        marked = draw(path, spec)
        path.write_bytes(marked)
        spec["sha256"] = figure["sha256"] = sha(marked)
        drawn += 1
    if drawn:
        markers_path.write_text(json.dumps(markers, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        inventory_path.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"FIGURE_MARKERS_OK bank={args.bank} figures={len(markers['figures'])} drawn={drawn}")


if __name__ == "__main__":
    main()
