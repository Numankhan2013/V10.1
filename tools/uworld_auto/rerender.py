#!/usr/bin/env python3
"""Re-render a collection's committed crops (e.g. after changing the crop scale)."""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
from package import render_crop, lfs_path, ROOT
from pdfpages import Doc
from uworld_reviewed_document import figure_asset

slug = sys.argv[1]
src = ROOT / 'data/uworld/prepared' / slug
m = json.loads((src / 'manifest.json').read_text())
pdf = lfs_path(ROOT / m['source_pdf'])[0]
yoff = Doc(pdf).yoff
want = set()
for b in sorted((src / 'reviewed').glob('batch-*.json')):
    for d in json.loads(b.read_text())['records']:
        for n in d.get('question_blocks', []) + d['explanation']:
            if n['type'] == 'figure':
                name = Path(figure_asset(d['id'], n, m['source_sha256'])).name
                want.add(name)
                render_crop(pdf, n['page'], n['bbox'], yoff).save(src / 'figures' / name, optimize=True)
for f in (src / 'figures').glob('*.png'):
    if f.name not in want:
        f.unlink()
print(slug, len(want), 'crops')
