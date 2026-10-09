"""Deterministic UWorld screenshot-PDF extractor.

Each question is a run of screenshots: an unanswered page, an answered page,
scrolled explanation pages and "Exhibit Display" popups. The answered and
scrolled pages are views of one scrolling document, so they are aligned on
shared OCR lines into a single canvas. Text is read once (from the view where
the line is furthest from the clipped edges) and any text inside a table,
picture or popup is dropped: that is the OCR leakage the manual review removed.
Pictures and tables ship as source crops; popups give full-size exhibits.
"""
from collections import Counter, defaultdict
import re
import numpy as np
from difflib import SequenceMatcher
from regions import exhibit_figure, boxes, images

QID_RE = re.compile(r'Question\s*[Il1|]\s*[dD]\W{0,3}(\d{2,6})')
ITEM_RE = re.compile(r'[Il1|]tem[\W_]{0,3}(\d{1,3})\s*[o0]\s*[rfl1]\s*(\d{1,3})')
OPT_RE = re.compile(r'(?:^|\s)([A-J8])\s*[.,]\s+(.*)$')
PCT_RE = re.compile(r'\(\s*(\d{1,3})\s*%\s*\)?\s*$')
JUNK_RE = re.compile(r'[»«{}\\~^¥§¤©®|]|(?:\s[^\sA-Za-z0-9(\[\-–—•"“‘\'<>=≥≤±%/+.,]{2,}\s)|\b(?:[b-hj-z]\s){3,}')


def norm(s):
    return re.sub(r'[^a-z0-9]+', '', s.lower())


def bands(a):
    """Content band between the blue toolbar and the blue footer (crop-space y)."""
    g = a.astype(int)
    blue = (g[..., 2] > 120) & (g[..., 2] - g[..., 0] > 70)
    frac = blue.mean(axis=1)
    top = 48
    for y in range(0, 90):
        if frac[y] > .5:
            top = y + 1
    bottom = a.shape[0]
    for y in range(300, a.shape[0] - 15):
        if frac[y:y + 15].min() > .5:   # the footer is a tall solid bar, not a rule
            bottom = y
            break
    return top + 2, bottom - 2


class Page:
    def __init__(self, doc, n):
        self.n = n
        self.a = np.asarray(doc.image(n)).astype(np.int16)
        self.lines = doc.lines(n)
        self.top, self.bottom = bands(self.a)
        head = ' '.join(l['text'] for l in self.lines if l['y0'] < self.top + 4)
        m = QID_RE.search(head)
        self.qid = m.group(1) if m else None
        m = ITEM_RE.search(head)
        self.item = (int(m.group(1)), int(m.group(2))) if m else None
        self.exhibit = exhibit_figure(self.a, self.lines)
        for l in self.lines:
            l['text'] = re.sub(r'\s?[°º0o]\s?/\s?[o0]\b|%[o0]\b', '%', l['text'])
            l['text'] = re.sub(r'(\d)\s*%\s*[>)\]}]+', r'\1%)', l['text'])
        body = [l for l in self.lines if self.top <= l['y0'] and l['y1'] <= self.bottom + 2]
        self.body = body
        text = ' '.join(l['text'] for l in body)
        self.answered = bool(re.search(r'Answered\s*correct', text)) or bool(re.search(r'Correct\s*answer', text))
        self.unanswered = not self.answered and any(l['text'].strip().lower() == 'submit' for l in body)


def group_pages(pages):
    # Smooth isolated OCR misreads of the question id.
    ids = [p.qid for p in pages]
    for i, p in enumerate(pages):
        prev = next((ids[j] for j in range(i - 1, -1, -1) if ids[j]), None)
        nxt = next((ids[j] for j in range(i + 1, len(ids)) if ids[j]), None)
        if (p.qid is None or (prev == nxt and p.qid != prev)) and prev and (prev == nxt or p.qid is None):
            p.qid = prev
    groups = []
    for p in pages:
        if groups and groups[-1][0].qid == p.qid:
            groups[-1].append(p)
        else:
            groups.append([p])
    return groups


def align(views):
    """Canvas offset per view from shared OCR lines (mode of y differences)."""
    offsets = {views[0].n: 0.0}
    for prev, cur in zip(views, views[1:]):
        diffs = []
        pk = {}
        for l in prev.body:
            k = norm(l['text'])
            if len(k) >= 12:
                pk.setdefault(k, []).append(l)
        for l in cur.body:
            for m in pk.get(norm(l['text']), []):
                if abs(m['x0'] - l['x0']) < 6:
                    diffs.append(round(m['y0'] - l['y0']))
        if diffs:
            d, _ = Counter(diffs).most_common(1)[0]
            near = [x for x in diffs if abs(x - d) <= 2]
            offsets[cur.n] = offsets[prev.n] + float(np.median(near))
        else:
            offsets[cur.n] = offsets[prev.n] + pixel_shift(prev, cur)
    return offsets, True


def pixel_shift(prev, cur):
    """Scroll distance between two views from their pixels; no overlap means they abut."""
    top, bot = max(prev.top, cur.top), min(prev.bottom, cur.bottom)
    A = prev.a[top:bot, :1000:2].mean(axis=2)
    B = cur.a[top:bot, :1000:2].mean(axis=2)
    H = A.shape[0]
    best, best_d = 1e9, None
    for d in range(4, H - 40):
        diff = np.abs(A[d:] - B[:H - d])
        # ignore rows that are pure background in both (would match anything)
        busy = (A[d:].std(axis=1) > 6) | (B[:H - d].std(axis=1) > 6)
        if busy.sum() < 25:
            continue
        m = diff[busy].mean()
        if m < best:
            best, best_d = m, d
    if best_d is not None and best < 6:
        return float(best_d)
    return float(prev.bottom - prev.top)


def inside(l, box, oy, pad=3):
    cy = (l['y0'] + l['y1']) / 2 + oy
    cx = (l['x0'] + l['x1']) / 2
    return box[0] - pad <= cx <= box[2] + pad and box[1] - pad <= cy <= box[3] + pad


def clipped(box, view, margin=12):
    return box[1] <= view.top + margin or box[3] >= view.bottom - margin


def thumb(a, box):
    from PIL import Image
    x0, y0, x1, y1 = [int(v) for v in box]
    im = Image.fromarray(a[y0:y1, x0:x1].astype(np.uint8)).convert('L').resize((48, 48))
    v = np.asarray(im, float).ravel()
    v -= v.mean()
    n = np.linalg.norm(v)
    return v / n if n else v


def paragraphs(lines):
    out, cur, last = [], [], None
    if not lines:
        return out
    gaps = [b['cy'] - a['cy'] for a, b in zip(lines, lines[1:]) if 0 < b['cy'] - a['cy'] < 40]
    step = float(np.median(gaps)) if gaps else 25.0
    for l in lines:
        t = l['text'].strip()
        new = last is not None and (l['cy'] - last['cy'] > step * 1.45 or re.match(r'^\(Choices?\s+[A-J]', t))
        if new and cur:
            out.append(cur); cur = []
        cur.append(t)
        last = l
    if cur:
        out.append(cur)
    res = []
    for p in out:
        s = ''
        for t in p:
            if s.endswith('-') and t[:1].islower():
                s = s[:-1] + t
            else:
                s = (s + ' ' + t).strip()
        res.append(re.sub(r'\s+', ' ', s))
    return res


def collect(views, offsets, zones, y_min, y_max):
    """Lines of several aligned views, each kept once from its least-clipped view."""
    cands = []
    for v in views:
        oy = offsets.get(v.n)
        if oy is None:
            continue
        for l in v.body:
            cy = (l['y0'] + l['y1']) / 2 + oy
            if not (y_min < cy < y_max) or l['x0'] > 1000:
                continue
            if any(inside(l, z, oy) for z in zones):
                continue
            if not re.search(r'[A-Za-z]{3}', l['text']) and len(l['text']) < 16:
                continue
            cands.append({'text': l['text'], 'cy': cy, 'x0': l['x0'], 'edge': min(l['y0'] - v.top, v.bottom - l['y1'])})
    cands.sort(key=lambda c: c['cy'])
    kept = []
    for c in cands:
        dup = next((k for k in kept if abs(k['cy'] - c['cy']) < 7 and abs(k['x0'] - c['x0']) < 40), None)
        if dup:
            if c['edge'] > dup['edge']:
                kept[kept.index(dup)] = c
        else:
            kept.append(c)
    rows = []
    for l in sorted([k for k in kept if k['edge'] > 1], key=lambda c: c['cy']):
        if rows and abs(rows[-1][-1]['cy'] - l['cy']) < 6:
            rows[-1].append(l)
        else:
            rows.append([l])
    out = []
    for r in rows:
        r.sort(key=lambda c: c['x0'])
        gaps = [b['x0'] - a['x0'] - len(a['text']) * 6 for a, b in zip(r, r[1:])]
        out.append({**r[0], 'text': ' '.join(c['text'] for c in r), 'edge': min(c['edge'] for c in r),
                    'pieces': len(r), 'gap': max(gaps) if gaps else 0, 'longest': max(len(c['text']) for c in r)})
    return out


def option_box(view, lines, limit_y):
    """The bordered panel holding the answer choices (above the status panel)."""
    best = None
    for b in boxes(view.a, view.top, min(view.bottom, int(limit_y) + 2)):
        inner = [l for l in lines if inside(l, b, 0, pad=2)]
        score = sum(bool(OPT_RE.search(l['text']) or PCT_RE.search(l['text'])) for l in inner)
        if score >= 2 and (best is None or score > best[0]):
            best = (score, b)
    return best[1] if best else None


def split_options(lines):
    """Answer choices end with their '(NN%)' statistic; letters are read but not trusted."""
    lines = sorted(lines, key=lambda l: (l['y0'], l['x0']))
    split = []
    for l in lines:
        parts = [p for p in re.split(r'(?<=\d%\))\s+', l['text']) if p.strip()]
        if len(parts) == 1:
            parts = re.split(r'\s(?=(?:[vVxX]\s)?[B-J]\.\s)', l['text'])
        if len(parts) > 1 and all(len(p) > 3 for p in parts):
            for k, p in enumerate(parts):
                split.append({**l, 'text': p, 'y0': l['y0'] + k * .1, 'y1': l['y1'] + k * .1})
        else:
            split.append(l)
    lines = split
    chunks, cur = [], []
    has_pct = sum(bool(PCT_RE.search(l['text'])) for l in lines) >= 2
    for l in lines:
        t = l['text'].strip()
        if not t or re.fullmatch(r'[XVvx✓✗]', t):
            continue
        starts = OPT_RE.search(t)
        if cur and not has_pct and starts and l['y0'] - cur[-1]['y1'] > 6:
            chunks.append(cur); cur = []
        cur.append(l)
        if has_pct and PCT_RE.search(t):
            chunks.append(cur); cur = []
    if cur:
        chunks.append(cur)
    options = []
    for i, ch in enumerate(chunks):
        text = ' '.join(c['text'].strip() for c in ch)
        m = OPT_RE.search(text)
        body = m.group(2) if m and m.start() < 8 else re.sub(r'^\W{0,4}\w?\W{0,3}', '', text)
        letter = chr(65 + i)
        body = re.sub(r'^\W{0,3}(?:[O0@G6Qa(®]\W{0,2}\s*)?(?:' + letter + r'\b[.,]?|[A-J0-9]\s?[.,])\s+', '', body.strip())
        body = re.sub(r'\s+(?:[vV][xX]?|[xX][vVx]|Xx|v)\s*$', '', body)
        options.append({'letter': letter, 'read_letter': m.group(1) if m and m.start() < 8 else None,
                        'text': body.strip(), 'y': ch[0]['y0'], 'y1': ch[-1]['y1']})
    return options


def extract_question(views_all, pdf_sha):
    issues, notes = [], []
    qid = views_all[0].qid
    # Some PDFs store a question's screenshots newest-first; restore reading order.
    ia = next((i for i, v in enumerate(views_all) if v.answered and not v.exhibit), None)
    iu = next((i for i, v in enumerate(views_all) if v.unanswered and not v.exhibit), None)
    if ia is not None and iu is not None and iu > ia:
        views_all = views_all[::-1]
    pages = sorted(v.n for v in views_all)
    answered = next((i for i, v in enumerate(views_all) if v.answered and not v.exhibit), None)
    if answered is None:
        return None, ['no answered page']
    ans = views_all[answered]
    scroll = [v for v in views_all[answered:] if not v.exhibit]
    offsets, ok = align(scroll)
    if not ok:
        issues.append('scroll alignment failed')
        scroll = [v for v in scroll if offsets.get(v.n) is not None]
    # ---- question, options, statistics from the answered view
    lines = sorted(ans.body, key=lambda l: (l['y0'], l['x0']))
    status_i = next((i for i, l in enumerate(lines) if re.search(r'Correct\s*answer|Answered\s*correct|^\s*(In)?correct\s*$', l['text'])), None)
    if status_i is None:
        return None, ['status panel not found']
    opt_box = option_box(ans, lines, lines[status_i]['y0'])
    if opt_box is None:
        return None, ['options panel not found']
    opt_lines = [l for l in lines if inside(l, opt_box, 0, pad=2) and l['x0'] > opt_box[0] + 4]
    options = split_options(opt_lines)
    for o in options:
        m = PCT_RE.search(o['text'])
        o['selection_percent'] = int(m.group(1)) if m else None
        o['text'] = PCT_RE.sub('', o['text']).strip()
        o['text'] = re.sub(r'\s*\(\s*\d{1,3}\s*%?\s*$', '', o['text']).strip()
    first_opt_y = opt_box[1]
    # The stem is read from the views before answering (it may span several scrolls and a
    # picture); the answered view is used only when it is the sole view.
    stem_views = [v for v in views_all[:answered] if not v.exhibit] or [ans]
    soff, _ = align(stem_views)
    last = stem_views[-1]
    sl = sorted(last.body, key=lambda l: (l['y0'], l['x0']))
    stem_box = opt_box if last is ans else option_box(last, sl, last.bottom)
    cut = soff[last.n] + (stem_box[1] if stem_box else (opt_box[1] if last is ans else last.bottom))
    stem_zones, stem_media = [], []
    for v in stem_views:
        for b in images(v.a, v.top, v.bottom, lines=v.body):
            cb = [b[0], b[1] + soff[v.n], b[2], b[3] + soff[v.n]]
            if cb[1] >= cut:
                continue
            stem_zones.append(cb)
            if not clipped(b, v):
                stem_media.append({'kind': 'image', 'canvas': [cb[0], cb[1] - 100000, cb[2], cb[3] - 100000], 'page': v.n,
                                   'bbox': [int(x) for x in b], 'role': 'question', 'thumb': thumb(v.a, b)})
    stem_lines = collect(stem_views, soff, stem_zones, -1e9, cut)
    # The viewer marks the right choice with a green tick left of the radio button.
    green = []
    g = ans.a.astype(int)
    for o in options:
        y0, y1 = int(o['y']) - 4, int(o['y1']) + 4
        zone = g[max(0, y0):y1, 18:52]
        tick = ((zone[..., 1] > 100) & (zone[..., 1] - zone[..., 0] > 25) & (zone[..., 1] - zone[..., 2] > 15)).sum()
        green.append(tick)
    misread = [o['letter'] for o in options if o['read_letter'] and o['read_letter'].isalpha() and o['read_letter'] != o['letter']]
    if misread:
        issues.append('choice letters disagree with order: ' + ','.join(misread))
    for o in options:
        o.pop('y'); o.pop('y1'); o.pop('read_letter')
    stat_text = ' '.join(l['text'] for l in lines[status_i:status_i + 14] if l['y0'] < lines[status_i]['y0'] + 60)
    correct = None
    ca = next((i for i, l in enumerate(lines) if re.search(r'Correct\s*answer', l['text'])), None)
    if ca is not None:
        for l in lines[ca:ca + 6]:
            m = re.search(r'(?:answer\s+|^\s*)([A-J])\s*$', l['text'])
            if m and abs(l['x0'] - lines[ca]['x0']) < 30:
                correct = m.group(1); break
    tick_letter = options[int(np.argmax(green))]['letter'] if options and max(green) >= 3 and sorted(green)[-2:-1] != [max(green)] else None
    pct_line = re.search(r'(\d{1,3})\s*%\s*\W*\s*Answered', stat_text) or re.search(r'(\d{1,3})\s*%', stat_text)
    answered_pct = int(pct_line.group(1)) if pct_line else None
    by_pct = [o['letter'] for o in options if answered_pct is not None and o['selection_percent'] == answered_pct]
    pct_letter = by_pct[0] if len(by_pct) == 1 else None
    votes = [x for x in (tick_letter, pct_letter, correct) if x]
    if len(set(votes)) > 1:
        issues.append(f'correct answer signals disagree: tick {tick_letter}, percent {pct_letter}, text {correct}')
    correct = tick_letter or pct_letter or correct
    tm = re.search(r'(\d{1,2})\s*min\w*\W+(\d{1,2})\s*sec', stat_text) or re.search(r'(\d{1,2})\s*sec', stat_text)
    time_s = (int(tm.group(1)) * 60 + int(tm.group(2)) if tm and tm.lastindex == 2 else int(tm.group(1)) if tm else None)
    ver = re.search(r'\b(20[12]\d)\b', stat_text)
    stem = paragraphs(stem_lines)
    # ---- regions on every scroll view, mapped to canvas
    zones, media = [], []
    q_bottom = first_opt_y - 4
    for v in [x for x in views_all if not x.exhibit and offsets.get(x.n) is not None]:
        oy = offsets[v.n]
        for kind, found in (('table', boxes(v.a, v.top, v.bottom)), ('image', images(v.a, v.top, v.bottom, lines=v.body))):
            for b in found:
                # option list and stat panel are UI chrome, not content
                cb = [b[0], b[1] + oy, b[2], b[3] + oy]
                inner = [l for l in v.body if inside(l, b, 0)]
                if any(re.search(r'Answered\s*correct|Correct\s*answer|Time\s*Spent|Version', l['text']) for l in inner):
                    continue
                if any(OPT_RE.search(l['text']) and PCT_RE.search(l['text']) for l in inner) and kind == 'table':
                    continue
                zones.append(cb)
                if not clipped(b, v):
                    media.append({'kind': kind, 'canvas': cb, 'page': v.n, 'bbox': [int(x) for x in b], 'role': 'question' if (v is ans and b[3] <= q_bottom) else 'explanation', 'thumb': thumb(v.a, b)})
    media = [m for m in media if m['role'] != 'question'] + stem_media
    # ---- explanation lines on canvas, deduplicated
    expl_start = next((l['y0'] for l in ans.body if re.match(r'^\W*Explanation\W*$', l['text'])), None)
    if expl_start is None:
        notes = ['explanation heading not found']
        expl_start = lines[status_i]['y1'] + 30
    kept = collect(scroll, offsets, zones, expl_start + offsets[ans.n] + 8, 1e9)
    # Subject / system / topic labels follow the objective as one spaced-out row.
    meta_i = next((i for i, k in enumerate(kept) if k.get('pieces', 1) >= 2 and k.get('gap', 0) > 60 and k.get('longest', 99) < 45 and
                   any(re.match(r'^\W*Educational\s+objective', x['text'], re.I) for x in kept[:i])), None)
    if meta_i is not None:
        kept = kept[:meta_i]
    obj_at = next((i for i, k in enumerate(kept) if re.match(r'^\W*Educational\s+objective', k['text'], re.I)), None)
    if obj_at is not None:
        for i in range(obj_at + 1, len(kept)):
            if SUBJECT_RE.match(kept[i]['text']) and len(kept[i]['text']) < 110:
                kept = kept[:i]; break
    texts = [k['text'] for k in kept]
    ref_i = next((i for i, t in enumerate(texts) if re.match(r'^\W*(References?|Copyright)\b', t)), len(texts))
    obj_i = next((i for i, t in enumerate(texts) if re.match(r'^\W*Educational\s+objective', t, re.I)), None)
    body = kept[:obj_i if obj_i is not None else ref_i]
    objective = ' '.join(t for t in texts[obj_i + 1:ref_i]) if obj_i is not None else ''
    if obj_i is not None and re.sub(r'^\W*Educational\s+objective\W*', '', texts[obj_i], flags=re.I):
        objective = (re.sub(r'^\W*Educational\s+objective\W*', '', texts[obj_i], flags=re.I) + ' ' + objective).strip()
    prose = paragraphs(body)
    # ---- exhibits: popups before the answer belong to the question
    exhibits = []
    for i, v in enumerate(views_all):
        if v.exhibit and v.exhibit[0]:
            exhibits.append({'kind': 'exhibit', 'page': v.n, 'bbox': [int(x) for x in v.exhibit[0]],
                             'role': 'question' if i < answered else 'explanation', 'thumb': thumb(v.a, v.exhibit[0])})
    # Cells of a table seen while it was half scrolled are not tables of their own.
    def covered(m, others):
        c = m['canvas']; area = max(1, (c[2] - c[0]) * (c[3] - c[1]))
        for o in others:
            if o is m or 'canvas' not in o:
                continue
            k = o['canvas']
            ix = max(0, min(c[2], k[2]) - max(c[0], k[0])); iy = max(0, min(c[3], k[3]) - max(c[1], k[1]))
            if ix * iy / area > .6 and (k[2] - k[0]) * (k[3] - k[1]) > area:
                return True
        return False
    big = media + [{'canvas': z} for z in zones]
    media = [m for m in media if not covered(m, big)]
    # dedupe media: identical popups opened twice, and inline pictures that a popup shows full size
    uniq = []
    for m in exhibits + sorted(media, key=lambda m: m['canvas'][1]):
        if any(float(np.dot(m['thumb'], u['thumb'])) > .97 for u in uniq):
            continue
        if m['kind'] == 'image' and any(abs(m['canvas'][1] - u.get('canvas', [0, -99])[1]) < 6 for u in uniq):
            continue
        uniq.append(m)
    # Explanation pictures are reviewed from their full-size popups; inline thumbnails only
    # stand in when the question has no popup at all. Tables always ship as crops.
    if any(m['kind'] == 'exhibit' and m['role'] == 'explanation' for m in uniq):
        uniq = [m for m in uniq if not (m['kind'] == 'image' and m['role'] == 'explanation')]
    q_media = [m for m in uniq if m['role'] == 'question']
    e_media = [m for m in uniq if m['role'] == 'explanation']
    node = lambda m: {'type': 'figure', 'page': m['page'], 'bbox': m['bbox'], 'role': m['role']}
    # ---- checks
    letters = [o['letter'] for o in options]
    if not 4 <= len(options) <= 9 or letters != list('ABCDEFGHI')[:len(options)]:
        issues.append(f'options {letters}')
    if correct not in letters:
        issues.append('correct answer not read')
    pcts = [o['selection_percent'] for o in options]
    collecting = bool(re.search(r'Collecting\s+Statistics', stat_text, re.I))
    if all(p is None for p in pcts) and collecting:
        notes.append('source shows no statistics yet')
    elif None in pcts:
        issues.append('missing choice percent')
    elif not 96 <= sum(pcts) <= 104:
        issues.append(f'choice percents sum {sum(pcts)}')
    if correct in letters and answered_pct is not None and pcts[letters.index(correct)] is not None and abs(pcts[letters.index(correct)] - answered_pct) > 1:
        issues.append('answered% differs from correct choice%')
    if not stem:
        issues.append('empty stem')
    if not prose:
        issues.append('empty explanation')
    if not objective:
        issues.append('no educational objective')
    junk = [t for t in stem + prose + [objective] + [o['text'] for o in options] if JUNK_RE.search(' ' + t + ' ')]
    if junk:
        m = JUNK_RE.search(' ' + junk[0] + ' ')
        issues.append('suspicious OCR: …' + junk[0][max(0, m.start() - 40):m.end() + 20] + '…')
    if any(len(re.sub(r'\W', '', o['text'])) <= 2 for o in options):
        issues.append('choices look like pictures or a table')
    if any(not o['text'] for o in options):
        issues.append('empty choice text (image option?)')
    for m in media:
        if m['role'] == 'question' and m['kind'] == 'table':
            pass
    doc = {
        'id': 'UWORLD_' + str(qid), 'reviewed_pages': pages,
        'question': ' '.join(stem), 'options': [{k: o[k] for k in ('letter', 'text', 'selection_percent')} for o in options],
        'correct_label': correct, 'question_blocks': [node(m) for m in q_media],
        'explanation': [node(m) for m in e_media] + [{'type': 'paragraph', 'text': p} for p in prose],
        'educational_objective': objective,
        'statistics': {'answered_correctly_percent': answered_pct,
                       'selection_percent': {o['letter']: o['selection_percent'] for o in options}},
        'status': 'verified' if not issues else 'blocked', 'issues': issues,
        '_notes': notes,
        '_meta': {'item': ans.item, 'time_spent_seconds': time_s, 'version_year': int(ver.group(1)) if ver else None},
    }
    return doc, issues


WORD = re.compile(r"[A-Za-z]+")
# OCR renders accented letters as '~' or drops them; restore the medical/proper terms UWorld uses.
ACCENTS = [(r"\b([mM])[~\-]?ullerian", r"\1üllerian"), (r"\bfianc[~e]\b", "fiancé"), (r"\bMeni[~e]re", "Ménière"),
           (r"\bSj[~o]gren", "Sjögren"), (r"Guillain-Barr[~e]\b", "Guillain-Barré"), (r"\bcaf[~e]-au-lait", "café-au-lait"),
           (r"\bna[~i]ve\b", "naive"), (r"\bB[~a]r[~a]ny", "Bárány")]
SUBJECT_RE = re.compile(r"^\W*(Pathology|Pharmacology|Physiology|Biochemistry|Microbiology|Immunology|Anatomy|Genetics|"
                        r"Histology|Embryology|Behavioral science|Biostatistics|Epidemiology|Social Sciences|Ethics|"
                        r"Psychiatry|Medicine|Pediatrics|Obstetrics|Gynecology|Surgery|Neurology)\b")
SHORT_WORDS = set("a i an as at be by do eg ie go he if in is it me my no of on or so to up us we vs mg ml dl kg cm mm id ii iv vi pH".lower().split())


def build_vocab(pages):
    c = Counter()
    for p in pages:
        for l in p.lines:
            c.update(w.lower() for w in WORD.findall(l['text']))
    return c


def rejoin(text, vocab):
    """Undo OCR splits such as 'intern a' or 's t rongly' when the joined word is attested."""
    toks = text.split(' ')
    out, i = [], 0
    while i < len(toks):
        done = False
        for n in (3, 2):
            part = toks[i:i + n]
            if len(part) < n or not all(re.fullmatch(r"[A-Za-z]+", t.rstrip('.,;:)')) for t in part[:-1]):
                continue
            core = ''.join(part)
            tail = re.search(r"[.,;:)]*$", core).group(0)
            word = core[:len(core) - len(tail)] if tail else core
            if not re.fullmatch(r"[A-Za-z]+", word):
                continue
            joined = vocab.get(word.lower(), 0)
            counts = [vocab.get(t.rstrip('.,;:)').lower(), 0) for t in part]
            bogus_short = any(len(t.rstrip('.,;:)')) <= 2 and t.rstrip('.,;:)').lower() not in SHORT_WORDS for t in part)
            if (joined >= 3 and not all(c >= 3 for c in counts)) or (joined >= 2 and bogus_short):
                out.append(word + tail); i += n; done = True
                break
        if not done:
            out.append(toks[i]); i += 1
    return ' '.join(out)


def polish(doc, vocab):
    if not doc:
        return doc
    def fix(t):
        t = rejoin(t, vocab)
        t = re.sub(r'<\s?:\s?!\s?', '≥', t)                  # OCR of the ≥ sign
        for pat, rep in ACCENTS:
            t = re.sub(pat, rep, t)
        t = re.sub(r'\b([A-Z]{2,})ls\b', r'\1Is', t)        # UTls -> UTIs
        return re.sub(r'\b([A-Z]{2,})l\b', r'\1I', t)       # UTl -> UTI
    doc['question'] = fix(doc['question'])
    doc['educational_objective'] = fix(doc['educational_objective'])
    for o in doc['options']:
        o['text'] = fix(o['text'])
    for n in doc['explanation']:
        if n['type'] == 'paragraph':
            n['text'] = fix(n['text'])
    return doc


def extract(doc, pdf_sha, first=1, last=None, progress=None):
    last = last or doc.pages
    pages = []
    for n in range(first, last + 1):
        pages.append(Page(doc, n))
        if progress and n % 25 == 0:
            progress(n)
    vocab = build_vocab(pages)
    results = []
    for g in group_pages(pages):
        if not g[0].qid:
            results.append((None, ['unidentified pages %d-%d' % (g[0].n, g[-1].n)], [p.n for p in g]))
            continue
        d, issues = extract_question(g, pdf_sha)
        results.append((polish(d, vocab), issues, [p.n for p in g]))
    return results
