#!/usr/bin/env python3
"""Extract one UWorld screenshot PDF into a shippable prepared/<slug>/ collection.

Usage: package.py <slug> "<Collection name>" <repo-relative pdf path> [--pdf-file local.pdf]

Writes manifest.json, normalized.jsonl, page_to_question_manifest.json,
reviewed/batch-NN.json, figures/*.png, qa_report.json and tools/uworld_<slug>.py.
Corrections from a review pass live in reviewed/fixes.json ({id: {field: value}})
and are re-applied on every run, so regeneration never loses them.
"""
import argparse, hashlib, io, json, os, re, subprocess, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
from pdfpages import Doc
from extract import extract
from uworld_reviewed_document import record_hash, figure_asset, validate_node
from uworld_content_hygiene import validate_display
from PIL import Image

ROOT = HERE.parents[1]


def lfs_path(pointer):
    text = pointer.read_bytes()[:300].decode('latin1')
    m = re.search(r'oid sha256:([0-9a-f]{64})', text)
    if not m:
        return pointer, hashlib.sha256(pointer.read_bytes()).hexdigest()
    oid = m.group(1)
    return ROOT / '.git/lfs/objects' / oid[:2] / oid[2:4] / oid, oid


def blocks_from_items(docs):
    """A block restarts when an item number repeats or its 'of N' total changes (page order may run either way)."""
    block, seen, total = 1, set(), None
    for d in docs:
        item = d['_meta']['item']
        if item:
            if (total is not None and item[1] != total) or item[0] in seen:
                block += 1; seen = set()
            seen.add(item[0]); total = item[1]
        d['_meta']['block'] = block
        d['_meta']['number'] = item[0] if item else None


def render_crop(pdf, page, bbox, yoff, scale=1.3):
    png = subprocess.run(['pdftoppm', '-f', str(page), '-l', str(page), '-r', str(72 * scale), '-png', str(pdf)],
                         capture_output=True).stdout
    im = Image.open(io.BytesIO(png)).convert('RGB')
    x0, y0, x1, y1 = bbox
    return im.crop((round(x0 * scale), round((y0 + yoff) * scale), round(x1 * scale), round((y1 + yoff) * scale)))


def save_crop(im, target):
    # WebP q90 is visually lossless for these screenshots and ~10x smaller than PNG.
    im.save(target, 'WEBP', quality=90, method=6)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('slug'); ap.add_argument('collection'); ap.add_argument('pdf')
    ap.add_argument('--pdf-file'); ap.add_argument('--first', type=int, default=1); ap.add_argument('--last', type=int)
    args = ap.parse_args()
    pointer = ROOT / args.pdf
    local, sha = (Path(args.pdf_file), None) if args.pdf_file else lfs_path(pointer)
    if sha is None:
        sha = hashlib.sha256(Path(local).read_bytes()).hexdigest()
    doc = Doc(local)
    out = ROOT / 'data/uworld/prepared' / args.slug
    (out / 'reviewed').mkdir(parents=True, exist_ok=True); (out / 'figures').mkdir(exist_ok=True)
    fixes_path = out / 'reviewed/fixes.json'
    fixes = json.loads(fixes_path.read_text()) if fixes_path.exists() else {}
    results = extract(doc, sha, args.first, args.last, progress=lambda n: print('  page', n, file=sys.stderr))
    docs, unowned, seen = [], [], set()
    for d, issues, pages in results:
        letters = [o['letter'] for o in d['options']] if d else []
        usable = (d and d.get('correct_label') in letters and 4 <= len(letters) <= 12 and
                  letters == list('ABCDEFGHIJKL')[:len(letters)] and d['question'].strip() and
                  any(n['type'] == 'paragraph' for n in d['explanation']) and all(o['text'] for o in d['options']))
        if not usable or d['id'] in seen:
            unowned.append({'pages': pages, 'reason': '; '.join(issues) or 'duplicate question id'})
            continue
        seen.add(d['id']); docs.append(d)
    blocks_from_items(docs)
    docs.sort(key=lambda d: (d['_meta']['block'], d['_meta']['number'] or 999))
    rows, reviewed, qa = [], [], []
    for d in docs:
        fix = fixes.get(d['id'], {})
        for k, v in fix.items():
            d[k] = v
        meta = d.pop('_meta'); d.pop('_notes', None)
        letters = [o['letter'] for o in d['options']]
        row = {
            'schema_version': 1, 'question_id': d['id'], 'uworld_question_id': d['id'].split('_', 1)[1],
            'bank': 'UWorld', 'collection': args.collection, 'block_number': meta['block'],
            'question_number': meta['number'], 'question_text': d['question'],
            'options': [{'label': o['letter'].lower(), 'text': o['text'], 'selection_percent': o['selection_percent']} for o in d['options']],
            'correct_option': d['correct_label'].lower(),
            'correct_answer_text': d['options'][letters.index(d['correct_label'])]['text'],
            'explanation': {'text': '\n\n'.join(n['text'] for n in d['explanation'] if n['type'] == 'paragraph'),
                            'educational_objective': d['educational_objective']},
            'statistics': {'answered_correctly_percent': d['statistics']['answered_correctly_percent'],
                           'time_spent_seconds': meta['time_spent_seconds'], 'version_year': meta['version_year']},
            'source': {'source_pdf_sha256': sha, 'source_pages': d['reviewed_pages'],
                       'extraction': 'uworld-auto-extract'},
        }
        rows.append(row)
        d['source_record_sha256'] = record_hash(row)
        if not fix.get('status'):
            try:
                validate_display(d)
            except ValueError as e:
                d['issues'].append(str(e))
            d['status'] = 'verified' if not d['issues'] else 'blocked'
        for node in [n for n in d['question_blocks'] + d['explanation'] if n['type'] == 'figure']:
            validate_node(node, d['id'], d['reviewed_pages'], node['role'], sha, (1416, 757), 'webp')
            target = out / 'figures' / Path(node['asset']).name
            if not target.exists():
                save_crop(render_crop(local, node['page'], node['bbox'], doc.yoff), target)
            node.pop('asset')
        if d['status'] != 'verified':
            qa.append({'id': d['id'], 'pages': d['reviewed_pages'], 'issues': d['issues']})
        reviewed.append(d)
    pages = doc.pages if not args.last else args.last
    raw = ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows).encode()
    (out / 'normalized.jsonl').write_bytes(raw)
    for i in range(0, len(reviewed), 25):
        (out / f'reviewed/batch-{i // 25 + 1:02d}.json').write_text(json.dumps(
            {'schema_version': 1, 'source_pdf_sha256': sha, 'records': reviewed[i:i + 25]}, ensure_ascii=False, indent=1))
    page_map = {str(p): r['question_id'] for r in rows for p in r['source']['source_pages']}
    (out / 'page_to_question_manifest.json').write_text(json.dumps(page_map, indent=1))
    blocks = {}
    for r in rows:
        blocks[r['block_number']] = blocks.get(r['block_number'], 0) + 1
    manifest = {'schema_version': 1, 'collection': args.collection, 'source_sha256': sha, 'source_pdf': args.pdf,
                'page_count': pages, 'record_count': len(rows), 'jsonl_file': 'normalized.jsonl',
                'jsonl_sha256': hashlib.sha256(raw).hexdigest(), 'source_extraction_method': 'uworld-auto-extract',
                'blocks': blocks, 'unowned_pages': unowned,
                'figures_dir': f'data/uworld/prepared/{args.slug}/figures',
                'verified': sum(d['status'] == 'verified' for d in reviewed), 'blocked': len(qa)}
    (out / 'manifest.json').write_text(json.dumps(manifest, indent=1))
    (out / 'qa_report.json').write_text(json.dumps({'flagged': qa, 'unowned_pages': unowned}, indent=1, ensure_ascii=False))
    owner = ROOT / 'tools' / f'uworld_{args.slug}.py'
    owner.write_text(f'''"""Auto-extracted collection; see tools/uworld_auto and data/uworld/prepared/{args.slug}/qa_report.json."""
from uworld_auto_collection import AutoCollection

OWNER = AutoCollection(
    {args.slug!r}, {args.collection!r},
    {args.pdf!r},
    {sha!r}, {len(rows)}, {pages}, {blocks!r})
PDF, PDF_SHA, PAGE_SIZE = OWNER.PDF, OWNER.PDF_SHA, OWNER.PAGE_SIZE
load_source = OWNER.load_source
reviewed_documents = OWNER.reviewed_documents
bank_record = OWNER.bank_record
''')
    print(json.dumps({k: manifest[k] for k in ('collection', 'record_count', 'verified', 'blocked', 'blocks')}),
          'unowned', sum(len(u['pages']) for u in unowned))


if __name__ == '__main__':
    main()
