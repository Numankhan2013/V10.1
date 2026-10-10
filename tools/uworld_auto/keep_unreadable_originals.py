#!/usr/bin/env python3
"""Put back the original crop where the source labels are too blurry to upscale safely.

  keep_unreadable_originals.py <original-commit> <slug> [<slug> ...] [--threshold 0.6]

Real-ESRGAN sharpens most diagrams well, but where UWorld's own label text is a blur it
guesses letters ('Pronator teres' -> 'Pronator loros'). The PDF's OCR of the same pixels
is a good proxy for that: if under <threshold> of the OCR words inside a figure are words
that occur in the question corpus, the source text is unreadable and the original crop
(from <original-commit>) is restored. Restored figures are noted in upscaled.json.
"""
import collections, json, re, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
from pdfpages import Doc
from package import lfs_path, ROOT
from uworld_reviewed_document import figure_asset

args = sys.argv[1:]
threshold = float(args[args.index('--threshold') + 1]) if '--threshold' in args else 0.6
commit = args[0]
slugs = [a for i, a in enumerate(args[1:], 1) if not a.startswith('--') and args[i - 1] != '--threshold']
prepared = ROOT / 'data/uworld/prepared'
vocab = collections.Counter()
for batch in prepared.glob('*/reviewed/batch-*.json'):
    for d in json.loads(batch.read_text())['records']:
        text = ' '.join([d['question'], d.get('educational_objective', '')] + [o['text'] for o in d['options']] +
                        [n.get('text', '') for n in d['explanation'] if n['type'] == 'paragraph'])
        vocab.update(w.lower() for w in re.findall(r'[A-Za-z]{4,}', text))
for slug in slugs:
    src = prepared / slug
    log = src / 'upscaled.json'
    done = json.loads(log.read_text())
    manifest = json.loads((src / 'manifest.json').read_text())
    doc = Doc(lfs_path(ROOT / manifest['source_pdf'])[0])
    restored = 0
    for batch in sorted((src / 'reviewed').glob('batch-*.json')):
        for d in json.loads(batch.read_text())['records']:
            for n in d['question_blocks'] + d['explanation']:
                if n['type'] != 'figure':
                    continue
                name = figure_asset(d['id'], n, manifest['source_sha256'], 'webp').split('/')[-1]
                status = done.get(name, 'photo-kept')
                if status == 'photo-kept' or status.startswith('kept-original'):
                    continue
                x0, y0, x1, y1 = n['bbox']
                text = ' '.join(l['text'] for l in doc.lines(n['page'])
                                if l['x0'] >= x0 - 2 and l['x1'] <= x1 + 2 and l['y0'] >= y0 - 2 and l['y1'] <= y1 + 2)
                words = [w for w in re.findall(r'[A-Za-z]{4,}', text) if w.lower() != 'uworld']
                if len(words) < 3:
                    continue
                ratio = sum(vocab[w.lower()] >= 2 for w in words) / len(words)
                if ratio < threshold:
                    subprocess.run(['git', 'checkout', commit, '--', f'data/uworld/prepared/{slug}/figures/{name}'], cwd=ROOT, check=True)
                    done[name] = f'kept-original: source labels unreadable ({ratio:.0%} recognised words)'
                    restored += 1
    log.write_text(json.dumps(done, indent=0, sort_keys=True))
    print(slug, 'restored originals', restored, flush=True)
