"""Read the header "Question Id" from the screenshot itself.

The PDF text layer garbles the small white-on-blue header ("Question 1163" for 11637,
"15a407", a dropped "Id"), which splits or merges questions and collides IDs across
collections. Arial digits are tabular, so the digit run after "Id:" splits into equal
cells, each matched against digit templates cut from cleanly read headers
(header_digits.npz). Callers keep the OCR value when no confident read is possible.
"""
import io, re, subprocess
from functools import lru_cache
from pathlib import Path
import numpy as np
from PIL import Image

DPI = 200
PITCH = 14.5      # digit advance at 200 dpi
CONFIDENT = 0.85


@lru_cache(maxsize=1)
def templates():
    z = np.load(Path(__file__).with_name('header_digits.npz'))
    return {k[1:]: z[k].astype(float) for k in z.files}


def strip(doc, n):
    """Binary-ish header strip right of the word 'Question' and its column runs."""
    q = None
    for l in doc.lines(n):
        if l['y0'] > 60: continue
        for w in l['words']:
            if re.match(r'Q\w*st|Ques|uest', w[4]):
                q = w; break
        if q: break
    if not q:
        return None
    s = DPI / 72
    pad = 30
    # the whole bar above the body: the text layer can place "Question" on the wrong header line
    x, y = int(q[0] * s) - 4, max(0, int(doc.yoff * s))
    W, H = int(95 * s), int((max(q[3], 50) + doc.yoff) * s) + pad - y
    png = subprocess.run(['pdftoppm', '-f', str(n), '-l', str(n), '-r', str(DPI), '-x', str(x), '-y', str(y),
                          '-W', str(W), '-H', str(H), '-gray', '-png', doc.path], capture_output=True).stdout
    a = np.asarray(Image.open(io.BytesIO(png)).convert('L')).astype(float)
    bg = np.median(a[:int(20 * s), :int(W * .9)])   # the bar, not the light body below it
    b = np.clip((a - bg) / (255 - bg + 1e-6), 0, 1)
    b[(a > bg + 60).mean(1) > 0.9] = 0          # light body below the bar
    on = (b > 0.45).sum(1) > 2
    bands, i = [], 0
    while i < H:
        if on[i]:
            j = i
            while j < H and on[j]: j += 1
            if 12 <= j - i <= 32: bands.append((abs((i + j) / 2 - H / 2), i, j))
            i = j
        else: i += 1
    out = []
    for _, lo, hi in sorted(bands):
        out.append(runs_of(b[lo:hi]))
    return out


def runs_of(b):
    m = b > 0.45
    cols = m.any(0)
    runs, i = [], 0
    while i < len(cols):
        if cols[i]:
            j = i
            while j < len(cols) and cols[j]: j += 1
            runs.append([i, j]); i = j
        else: i += 1
    return b, runs


def is_colon(b, r):
    if r[1] - r[0] > 8: return False
    prof = (b[:, r[0]:r[1]] > 0.45).any(1).astype(int)
    blobs = (np.diff(np.concatenate([[0], prof, [0]])) == 1).sum()
    return blobs == 2 and prof[:len(prof) // 5].sum() == 0


def cells(doc, n):
    for b, runs in strip(doc, n) or []:
        out = band_cells(b, runs)
        if out: return out
    return None


def band_cells(b, runs):
    ci = next((i for i, x in enumerate(runs) if is_colon(b, x)), None)
    if ci is None: return None
    dig = []
    for x in runs[ci + 1:]:
        if dig and x[0] - dig[-1][1] > 12: break
        dig.append(x)
    if not dig: return None
    x0, x1 = dig[0][0], dig[-1][1]
    k = int(round((x1 - x0 + 5) / PITCH))
    if not 2 <= k <= 6: return None
    mid = (x0 + x1) / 2
    return [(b, mid + (i - (k - 1) / 2) * PITCH) for i in range(k)]


def patch(b, c, dx=0):
    h = b.shape[0]
    lo = int(round(c - PITCH / 2 + dx))
    p = np.zeros((h, int(PITCH) + 1))
    seg = b[:, max(lo, 0):lo + p.shape[1]]
    p[:, :seg.shape[1]] = seg
    im = Image.fromarray((p * 255).astype('uint8')).resize((12, 18), Image.BILINEAR)
    v = np.asarray(im).astype(float).ravel()
    v -= v.mean()
    return v / (np.linalg.norm(v) + 1e-6)


def read(doc, n):
    """(digits, weakest digit score) of the header "Question Id", or (None, 0)."""
    T = templates()
    cs = cells(doc, n)
    if not cs: return None, 0
    out, worst = '', 1
    for b, c in cs:
        best = (-2, None)
        for dx in (-2, -1, 0, 1, 2):
            v = patch(b, c, dx)
            for d, ts in T.items():
                s = float((ts @ v).max())
                if s > best[0]: best = (s, d)
        out += best[1]; worst = min(worst, best[0])
    return out, worst
