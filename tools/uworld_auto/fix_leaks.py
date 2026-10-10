#!/usr/bin/env python3
"""Remove answer-panel leakage from auto-extracted questions.

  fix_leaks.py <slug> [<slug> ...] [--dry-run]

1. Stem text that repeats the answer choices (OCR of the options panel, with radio
   glyphs such as "Q", "0", "@") is cut out of the stem.
2. Question figures whose crop contains the answer panel's "Submit" button (in the
   PDF text layer) are dropped; they are screenshots of the choices, not exhibits.
Corrections are stored in reviewed/fixes.json so a re-extraction keeps them.
"""
import hashlib, json, re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
from pdfpages import Doc
from package import lfs_path, ROOT
from uworld_reviewed_document import record_hash
from uworld_content_hygiene import validate_display

GLYPH = r'(?:[Q0O@©o]\s*)?'


def norm(t):
    return re.sub(r'\s+', ' ', t).strip()


def strip_choices(stem, options):
    """Cut a run of answer-choice text out of the stem; return the new stem or None."""
    texts = [norm(o['text']) for o in options if len(norm(o['text'])) >= 2]
    if not texts:
        return None
    # Lettered run: "... A. first ... B. second ... E. last" (glyphs optional).
    first = re.search(GLYPH + r'\bA\.\s+' + re.escape(texts[0][:12]), stem)
    if first:
        last_text = texts[-1]
        end = stem.find(last_text, first.end() - 12)
        if end < 0:  # OCR differs slightly at the end; cut to the last letter marker
            m = list(re.finditer(GLYPH + r'\b' + options[-1]['letter'] + r'\.\s+\S+', stem[first.start():]))
            if not m:
                return None
            end, last_text = first.start() + m[-1].start(), m[-1].group(0)
        new = norm(stem[:first.start()] + ' ' + stem[end + len(last_text):])
        return new if len(new) >= 40 and new != norm(stem) else None
    # Table run: the stem ends (after its question mark) with the choices' cell values.
    q = stem.rfind('?')
    if 0 < q < len(stem) - 1:
        tail = stem[q + 1:].split()
        words = set(w.strip('.,').lower() for t in texts for w in t.replace('·', ' ').split())
        if tail and sum(w.strip('.,').lower() in words for w in tail) >= 0.6 * len(tail):
            return norm(stem[:q + 1])
    return None


def panel_figure(doc, node):
    if node.get('type') != 'figure':
        return False
    x0, y0, x1, y1 = node['bbox']
    inside = [l['text'] for l in doc.lines(node['page'])
              if l['x0'] >= x0 - 2 and l['x1'] <= x1 + 2 and l['y0'] >= y0 - 2 and l['y1'] <= y1 + 2]
    # The answer panel's "Submit" button only ever appears in a crop of the choices.
    return any(re.fullmatch(r'\s*Submit\s*', t) for t in inside)


def main():
    dry = '--dry-run' in sys.argv
    for slug in [a for a in sys.argv[1:] if not a.startswith('--')]:
        src = ROOT / 'data/uworld/prepared' / slug
        manifest = json.loads((src / 'manifest.json').read_text())
        doc = Doc(lfs_path(ROOT / manifest['source_pdf'])[0])
        rows = [json.loads(l) for l in (src / 'normalized.jsonl').read_text().splitlines() if l.strip()]
        by_id = {r['question_id']: r for r in rows}
        batches = sorted((src / 'reviewed').glob('batch-*.json'))
        data = {b: json.loads(b.read_text()) for b in batches}
        fixes_path = src / 'reviewed/fixes.json'
        fixes = json.loads(fixes_path.read_text()) if fixes_path.exists() else {}
        stems = figs = 0
        for b, batch in data.items():
            for d in batch['records']:
                changed = {}
                new = strip_choices(d['question'], d['options'])
                if new:
                    changed['question'] = new
                keep = [n for n in d['question_blocks'] if not panel_figure(doc, n)]
                if len(keep) != len(d['question_blocks']):
                    changed['question_blocks'] = keep
                if not changed:
                    continue
                probe = {**d, **changed}
                try:
                    validate_display(probe)
                except ValueError as e:
                    print('  skip', d['id'], e); continue
                print(' ', d['id'], 'stem' if 'question' in changed else '', 'figure' if 'question_blocks' in changed else '')
                if dry:
                    continue
                stems += 'question' in changed; figs += 'question_blocks' in changed
                d.update(changed)
                fixes.setdefault(d['id'], {}).update(changed)
                row = by_id[d['id']]
                row['question_text'] = d['question']
                d['source_record_sha256'] = record_hash(row)
        if dry or not (stems or figs):
            print(slug, 'stems', stems, 'figures', figs, '(dry run)' if dry else ''); continue
        raw = ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows).encode()
        (src / 'normalized.jsonl').write_bytes(raw)
        for b, batch in data.items():
            b.write_text(json.dumps(batch, ensure_ascii=False, indent=1))
        fixes_path.write_text(json.dumps(fixes, ensure_ascii=False, indent=1))
        manifest['jsonl_sha256'] = hashlib.sha256(raw).hexdigest()
        (src / 'manifest.json').write_text(json.dumps(manifest, indent=1))
        print(slug, 'stems', stems, 'figures', figs)


if __name__ == '__main__':
    main()
