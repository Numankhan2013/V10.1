#!/usr/bin/env python3
"""Build a small review packet for the questions an extraction flagged.

Usage: review_packet.py <slug> [--pdf-file local.pdf] [--out dir]
For each flagged question it writes the current display JSON and low-resolution
page images, so a reviewer (a person or a small, inexpensive model) can correct
only those fields. Corrections go in data/uworld/prepared/<slug>/reviewed/fixes.json
as {"UWORLD_123": {"options": [...], "status": "verified", "issues": []}}; re-run
package.py to apply them. Verified questions never need this step.
"""
import argparse, json, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from package import lfs_path, ROOT


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('slug'); ap.add_argument('--pdf-file'); ap.add_argument('--out')
    a = ap.parse_args()
    src = ROOT / 'data/uworld/prepared' / a.slug
    manifest = json.loads((src / 'manifest.json').read_text())
    pdf = Path(a.pdf_file) if a.pdf_file else lfs_path(ROOT / manifest['source_pdf'])[0]
    out = Path(a.out or f'/tmp/uworld-review-{a.slug}'); out.mkdir(parents=True, exist_ok=True)
    docs = {r['id']: r for f in sorted((src / 'reviewed').glob('batch-*.json')) for r in json.loads(f.read_text())['records']}
    flagged = json.loads((src / 'qa_report.json').read_text())['flagged']
    for f in flagged:
        d = out / f['id']
        if d.exists() and any(d.glob('page-*.png')):
            (d / 'current.json').write_text(json.dumps(docs[f['id']], indent=1, ensure_ascii=False))
            continue
        d.mkdir(exist_ok=True)
        (d / 'current.json').write_text(json.dumps(docs[f['id']], indent=1, ensure_ascii=False))
        for p in f['pages']:
            subprocess.run(['pdftoppm', '-f', str(p), '-l', str(p), '-r', '60', '-png', '-singlefile', str(pdf), str(d / f'page-{p:04d}')])
    print(f'{len(flagged)} flagged questions -> {out}')


if __name__ == '__main__':
    main()
