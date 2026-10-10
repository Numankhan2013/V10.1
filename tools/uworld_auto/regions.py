"""Pixel geometry for UWorld screenshots: exhibit popups, bordered tables, inline images."""
import re
import numpy as np
from collections import Counter

CONTENT_TOP, CONTENT_BOTTOM = 48, 716   # below the toolbar, above the footer (crop-space points)


def _blue(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return (b > 120) & (b - r > 70) & (b - g > 45) & (r < 110)


def _runs(mask_row, min_len):
    out, start = [], None
    for x, v in enumerate(np.append(mask_row, False)):
        if v and start is None:
            start = x
        elif not v and start is not None:
            if x - start >= min_len:
                out.append((start, x))
            start = None
    return out


def exhibit(a):
    """Return the popup window (x0, y0_content, x1, y1_frame) or None."""
    blue = _blue(a)
    h = a.shape[0]
    # Start below the viewer toolbar (its position varies with browser chrome above it).
    frac = blue.mean(axis=1)
    toolbar, y = CONTENT_TOP - 2, next((y for y in range(0, min(h, 140)) if frac[y] > .6), None)
    if y is not None:
        gap = 0
        while y < min(h, 160) and gap <= 3:   # the toolbar is one contiguous band (icons leave small gaps)
            if frac[y] > .6:
                toolbar, gap = y, 0
            else:
                gap += 1
            y += 1
    rows = [y for y in range(max(CONTENT_TOP, toolbar) + 2, min(h, 320)) if blue[y].sum() > 250]
    if not rows:
        return None
    # The title bar is the first tall band of wide blue rows.
    band = [rows[0]]
    for y in rows[1:]:
        if y == band[-1] + 1:
            band.append(y)
        else:
            if len(band) >= 10:
                break
            band = [y]
    if len(band) < 10:
        return None
    runs = _runs(blue[band[len(band) // 2]], 250)
    # A popup's title bar is inset; the viewer toolbar runs edge to edge.
    runs = [r for r in runs if r[0] >= 20 and r[1] <= a.shape[1] - 20]
    if not runs:
        return None
    x0, x1 = max(runs, key=lambda r: r[1] - r[0])
    top = band[-1] + 1
    # Frame bottom: last row below the bar where the popup's side borders are still blue.
    bottom = top
    for y in range(top, min(h, CONTENT_BOTTOM + 4)):
        if blue[y, x0:x0 + 4].any() or blue[y, x1 - 4:x1].any():
            bottom = y
    return x0, top, x1, bottom


def trim(a, box, thresh=242, pad=3):
    x0, y0, x1, y1 = box
    sub = a[y0:y1, x0:x1]
    ink = (sub.min(axis=2) < thresh)
    ys, xs = np.where(ink)
    if not len(xs):
        return None
    return [int(x0 + xs.min() - pad), int(y0 + ys.min() - pad), int(x0 + xs.max() + 1 + pad), int(y0 + ys.max() + 1 + pad)]


def exhibit_figure(a, lines):
    """Figure bounds inside a popup, excluding the viewer's zoom/reset toolbar."""
    win = exhibit(a)
    if not win:
        return None
    x0, top, x1, bottom = win
    tool = [l for l in lines if x0 < l['x0'] < x1 and top < l['y0'] < bottom and
            any(k in l['text'] for k in ('Zoom', 'Reset', 'Existing', 'Notebook'))]
    if tool:
        bottom = int(min(l["y0"] for l in tool)) - 4
    box = trim(a, (x0 + 3, top + 2, x1 - 3, bottom))
    if box:
        box = [max(box[0], x0 + 1), max(box[1], top + 1), min(box[2], x1 - 1), min(box[3], bottom)]
    return box, win


def boxes(a, y_from=CONTENT_TOP, y_to=CONTENT_BOTTOM, min_w=120, min_h=30):
    """Bordered rectangles (tables, panels): pairs of long vertical rules with a rule joining their tops."""
    y_from, y_to = int(y_from), int(y_to)
    sub = a[y_from:y_to].astype(int)
    rule = sub.min(axis=2) < 215
    h, w = rule.shape
    verts = []
    for x in range(w):
        for y0, y1 in _runs(rule[:, x], min_h):
            verts.append((x, y0, y1))
    # merge adjacent columns (1-2px thick borders)
    merged = []
    for v in sorted(verts):
        if merged and v[0] - merged[-1][0] <= 2 and abs(v[1] - merged[-1][1]) <= 3 and abs(v[2] - merged[-1][2]) <= 3:
            continue
        merged.append(v)
    out = []
    for i, (xl, t1, b1) in enumerate(merged):
        for xr, t2, b2 in merged[i + 1:]:
            if xr - xl < min_w or abs(t1 - t2) > 4 or abs(b1 - b2) > 4:
                continue
            top, bot = max(t1, t2), min(b1, b2)
            # the box must be closed at the top or bottom by a horizontal rule
            span = slice(xl + 2, xr - 1)
            closed = any(rule[y, span].mean() > .9 for y in (top, top + 1, bot - 1, bot - 2) if 0 <= y < h)
            inner = sub[top + 3:bot - 3, xl + 3:xr - 2]
            busy = (np.abs(inner - np.median(inner, axis=(0, 1))).sum(axis=2) > 45).mean() if inner.size else 1
            if closed and busy < .3:
                out.append([xl, y_from + min(t1, t2), xr + 1, y_from + max(b1, b2)])
            break
    out.sort(key=lambda b: (b[2] - b[0]) * (b[3] - b[1]), reverse=True)
    final = []
    for b in out:
        if not any(b[0] >= f[0] - 3 and b[1] >= f[1] - 3 and b[2] <= f[2] + 3 and b[3] <= f[3] + 3 for f in final):
            final.append(b)
    return final


def images(a, y_from=CONTENT_TOP, y_to=CONTENT_BOTTOM, cell=8, min_cells=40, lines=None):
    """Inline pictures: dense or colourful pixel areas that are not text lines."""
    sub = a[y_from:y_to].astype(int)
    h, w = sub.shape[0] // cell, sub.shape[1] // cell
    sub = sub[:h * cell, :w * cell]
    # The viewer paints a soft gradient; measure ink against each row's background.
    bg = np.median(sub, axis=1, keepdims=True)
    diff = np.abs(sub - bg).sum(axis=2)
    g = sub.min(axis=2)
    sat = sub.max(axis=2) - sub.min(axis=2)
    on = diff > 45
    # Prose lines are text, not pictures: blank them before looking for picture blobs.
    for l in lines or []:
        toks = l['text'].split()
        wordy = toks and sum(bool(re.fullmatch(r"[A-Za-z][a-z'’-]+[.,;:)]?|\(?[A-Za-z]{1,3}[.,)]?|\d+[%.,)]*", t)) for t in toks) / len(toks) >= .75
        if wordy and l["y1"] - l["y0"] < 24:
            y0, y1 = int(l['y0']) - y_from - 1, int(l['y1']) - y_from + 2
            on[max(0, y0):max(0, y1), max(0, int(l['x0']) - 2):int(l['x1']) + 2] = False
    ink = on.reshape(h, cell, w, cell).mean(axis=(1, 3))
    col = ((sat > 40) & on).reshape(h, cell, w, cell).mean(axis=(1, 3))
    mid = ((g > 60) & (g < 200) & on).reshape(h, cell, w, cell).mean(axis=(1, 3))
    hot = (ink > .55) | (col > .25) | (mid > .45)
    # connected components on the cell grid (4-neighbour, with 1-cell dilation)
    from collections import deque
    dil = hot.copy()
    dil[1:] |= hot[:-1]; dil[:-1] |= hot[1:]; dil[:, 1:] |= hot[:, :-1]; dil[:, :-1] |= hot[:, 1:]
    seen = np.zeros_like(dil, bool)
    out = []
    for y in range(h):
        for x in range(w):
            if dil[y, x] and not seen[y, x]:
                q = deque([(y, x)]); seen[y, x] = True; cells = []
                while q:
                    cy, cx = q.popleft(); cells.append((cy, cx))
                    for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                        if 0 <= ny < h and 0 <= nx < w and dil[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = True; q.append((ny, nx))
                hot_cells = sum(1 for c in cells if hot[c])
                ys = [c[0] for c in cells]; xs = [c[1] for c in cells]
                bh, bw = max(ys) - min(ys) + 1, max(xs) - min(xs) + 1
                if hot_cells >= min_cells and bh >= 5 and bw >= 5:
                    out.append([min(xs) * cell, y_from + min(ys) * cell, (max(xs) + 1) * cell, y_from + (max(ys) + 1) * cell])
    return out


def iou(a, b):
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0])); iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    return inter / ((a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter or 1)


def white_panel(a, top, bottom, min_h=60):
    """Bounding box of the tallest white rectangle (figure panel) between top and bottom."""
    W = a.shape[1]
    white = a.min(axis=2) >= 252
    edges = {}
    for y in range(int(top), int(bottom)):
        row = white[y]
        n = int(row.sum())
        if not 80 <= n <= W * 0.8:
            continue
        xs = np.flatnonzero(row)
        edges[y] = (int(xs.min()), int(xs.max()))
    if not edges:
        return None
    best = None
    for (x0, x1), _ in Counter(edges.values()).most_common(5):
        ys = [y for y, e in edges.items() if abs(e[0] - x0) <= 4 and abs(e[1] - x1) <= 4]
        # longest run of rows (allowing small breaks for drawn lines)
        runs, start, prev = [], ys[0], ys[0]
        for y in ys[1:]:
            if y - prev > 12:
                runs.append((start, prev)); start = y
            prev = y
        runs.append((start, prev))
        s, e = max(runs, key=lambda r: r[1] - r[0])
        if e - s >= min_h and (best is None or e - s > best[3] - best[1]):
            best = [x0, s, x1 + 1, e + 1]
    return best
