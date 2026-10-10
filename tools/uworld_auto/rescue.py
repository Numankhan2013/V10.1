#!/usr/bin/env python3
"""Recover questions the extractor could not assemble (manifest 'unowned_pages').

  rescue.py <slug> packets <dir>    write review packets (current.json, partial.json, page PNGs)
  rescue.py <slug> adopt <dir> <out>  turn verified reviewer JSON (INSTRUCTIONS_SONNET.md format)
                                    into owned questions: rows, display docs and figure crops

Figures come from the extractor's partial result for those pages; a reviewer
only supplies text. Groups whose question id is already owned (duplicate
screenshots) or that a reviewer could not verify stay unowned with their reason.
"""
import hashlib, json, re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
from pdfpages import Doc
from extract import extract, Stub, Page
from regions import images, white_panel
from package import lfs_path, render_crop, save_crop, ROOT
from apply_reviews import to_fix
from uworld_reviewed_document import record_hash, validate_node
from uworld_content_hygiene import validate_display
import subprocess


def load(slug):
    src = ROOT / 'data/uworld/prepared' / slug
    manifest = json.loads((src / 'manifest.json').read_text())
    rows = [json.loads(l) for l in (src / 'normalized.jsonl').read_text().splitlines() if l.strip()]
    return src, manifest, rows


def packets(slug, out):
    src, manifest, rows = load(slug)
    pdf = lfs_path(ROOT / manifest['source_pdf'])[0]
    doc = Doc(pdf)
    owned = {r['question_id'] for r in rows}
    out.mkdir(parents=True, exist_ok=True)
    n = 0
    for entry in manifest['unowned_pages']:
        pages = entry['pages']
        stubs = [Stub(doc, p) for p in pages]
        qid = next((s.qid for s in stubs if s.qid), None)
        if not qid or 'UWORLD_' + qid in owned:
            continue
        d = out / ('UWORLD_' + qid)
        if d.exists():
            continue
        results = extract(doc, manifest['source_sha256'], pages[0], pages[-1])
        partial = next((r[0] for r in results if r[0]), None)
        item = next((s.item for s in stubs if s.item), None)
        if partial is None:
            partial = {'id': 'UWORLD_' + qid, 'reviewed_pages': pages, 'question': '', 'options': [],
                       'correct_label': None, 'question_blocks': [], 'explanation': [],
                       'educational_objective': '', 'statistics': {}, 'issues': [entry['reason']],
                       '_meta': {'item': item, 'time_spent_seconds': None, 'version_year': None}}
        partial['reviewed_pages'] = pages
        partial.pop('_notes', None)
        d.mkdir()
        (d / 'partial.json').write_text(json.dumps(partial, ensure_ascii=False, indent=1))
        shown = {k: v for k, v in partial.items() if not k.startswith('_')}
        shown['issues'] = [entry['reason']]
        (d / 'current.json').write_text(json.dumps(shown, ensure_ascii=False, indent=1))
        for p in pages:
            subprocess.run(['pdftoppm', '-f', str(p), '-l', str(p), '-r', '60', '-png', '-singlefile', str(pdf), str(d / f'page-{p:04d}')])
        n += 1
    print(f'{slug}: {n} rescue packets -> {out}')


def question_figure(doc, n, pages):
    """The stem picture a reviewer located: the exhibit popup figure, else the largest image on that page."""
    if n not in pages:
        raise ValueError('figure page outside the question')
    pg = Page(doc, n)
    if pg.exhibit and pg.exhibit[0]:
        box = pg.exhibit[0]
    else:
        # Graphs are white panels on the light page (colour detection misses them);
        # photos are found by colour. The answer-statistics bar is never a picture.
        box = white_panel(pg.a, pg.top, pg.bottom)
        if box is None:
            stats = [l for l in pg.body if re.search(r'Answered|Correct|Time Spent|Version', l['text'])]
            found = [b for b in images(pg.a, pg.top, pg.bottom, lines=pg.body)
                     if not any(b[1] <= l['y0'] <= b[3] for l in stats)]
            if not found:
                raise ValueError('no picture found on page %d' % n)
            box = max(found, key=lambda b: (b[2] - b[0]) * (b[3] - b[1]))
    return {'type': 'figure', 'page': n, 'bbox': [int(x) for x in box], 'role': 'question'}


def adopt(slug, pk, out):
    src, manifest, rows = load(slug)
    sha = manifest['source_sha256']
    pdf = lfs_path(ROOT / manifest['source_pdf'])[0]
    yoff = Doc(pdf).yoff
    batches = sorted((src / 'reviewed').glob('batch-*.json'))
    owned = {r['question_id'] for r in rows}
    # Question ids are global across collections (a truncated OCR id can collide).
    import uworld_collections
    elsewhere = {q['id'] for rec in uworld_collections.bank_records() if rec['subject'] != 'UWorld · ' + manifest['collection']
                 for q in rec['questions']}
    doc = Doc(pdf)
    page_block = {p: r['block_number'] for r in rows for p in r['source']['source_pages']}
    fixes_path = src / 'reviewed/fixes.json'
    fixes = json.loads(fixes_path.read_text()) if fixes_path.exists() else {}
    new_docs, kept, adopted, rejected = [], [], 0, []
    for entry in manifest['unowned_pages']:
        pages = entry['pages']
        hit = next((f for f in (pk.glob('UWORLD_*/partial.json')) if json.loads(f.read_text())['reviewed_pages'] == pages), None)
        rev = out / (hit.parent.name + '.json') if hit else None
        if not hit or not rev.exists() or hit.parent.name in owned or hit.parent.name in elsewhere:
            kept.append(entry); continue
        partial = json.loads(hit.read_text())
        meta = partial.pop('_meta')
        try:
            review = json.loads(rev.read_text())
            if review.get('status') != 'verified':
                raise ValueError('reviewer held it: ' + (review.get('notes') or ''))
            fig_page = review.get('question_figure_page')
            if fig_page and not partial['question_blocks']:
                partial['question_blocks'] = [question_figure(doc, int(fig_page), pages)]
            cur = {**partial, 'issues': [], 'correct_label': review['correct_label']}
            fix = to_fix(cur, review, careful=True)
            if fix['status'] != 'verified':
                raise ValueError('; '.join(fix['issues']))
            d = {**partial, **fix}
            for node in d['question_blocks'] + d['explanation']:
                node.pop('asset', None)
                if node['type'] == 'figure':
                    validate_node(node, d['id'], pages, node['role'], sha, (1416, 757), 'webp')
            validate_display(d)
        except Exception as e:
            rejected.append((hit.parent.name, str(e))); kept.append({**entry, 'reason': entry['reason'] + '; rescue: ' + str(e)[:120]})
            continue
        letters = [o['letter'] for o in d['options']]
        block = page_block.get(pages[0] - 1) or page_block.get(pages[-1] + 1) or 1
        item = meta.get('item')
        row = {
            'schema_version': 1, 'question_id': d['id'], 'uworld_question_id': d['id'].split('_', 1)[1],
            'bank': 'UWorld', 'collection': manifest['collection'], 'block_number': block,
            'question_number': item[0] if item else None, 'question_text': d['question'],
            'options': [{'label': o['letter'].lower(), 'text': o['text'], 'selection_percent': o['selection_percent']} for o in d['options']],
            'correct_option': d['correct_label'].lower(),
            'correct_answer_text': d['options'][letters.index(d['correct_label'])]['text'],
            'explanation': {'text': '\n\n'.join(n['text'] for n in d['explanation'] if n['type'] == 'paragraph'),
                            'educational_objective': d['educational_objective']},
            'statistics': {'answered_correctly_percent': d['statistics']['answered_correctly_percent'],
                           'time_spent_seconds': meta.get('time_spent_seconds'), 'version_year': meta.get('version_year')},
            'source': {'source_pdf_sha256': sha, 'source_pages': pages, 'extraction': 'uworld-auto-extract'},
        }
        for node in [n for n in d['question_blocks'] + d['explanation'] if n['type'] == 'figure']:
            target = src / 'figures' / Path(node['asset']).name
            if not target.exists():
                save_crop(render_crop(pdf, node['page'], node['bbox'], yoff), target)
            node.pop('asset')
        d['issues'] = []
        d['status'] = 'verified'
        d['source_record_sha256'] = record_hash(row)
        rows.append(row); new_docs.append(d); owned.add(d['id']); adopted += 1
        fixes[d['id']] = {k: d[k] for k in ('question', 'options', 'correct_label', 'explanation', 'educational_objective', 'statistics', 'status', 'issues')}
    if not adopted:
        print(f'{slug}: nothing adopted'); [print('  rejected', *r) for r in rejected]; return
    rows.sort(key=lambda r: (r['block_number'], r['question_number'] or 999))
    raw = ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows).encode()
    (src / 'normalized.jsonl').write_bytes(raw)
    last = json.loads(batches[-1].read_text())
    last['records'].extend(new_docs)
    batches[-1].write_text(json.dumps(last, ensure_ascii=False, indent=1))
    fixes_path.write_text(json.dumps(fixes, ensure_ascii=False, indent=1))
    page_map = {str(p): r['question_id'] for r in rows for p in r['source']['source_pages']}
    (src / 'page_to_question_manifest.json').write_text(json.dumps(page_map, indent=1))
    blocks = {}
    for r in rows:
        blocks[r['block_number']] = blocks.get(r['block_number'], 0) + 1
    qa = json.loads((src / 'qa_report.json').read_text())
    qa['unowned_pages'] = kept
    (src / 'qa_report.json').write_text(json.dumps(qa, ensure_ascii=False, indent=1))
    manifest.update(record_count=len(rows), jsonl_sha256=hashlib.sha256(raw).hexdigest(), blocks=blocks,
                    unowned_pages=kept, verified=manifest['verified'] + adopted)
    (src / 'manifest.json').write_text(json.dumps(manifest, indent=1))
    owner = ROOT / 'tools' / f'uworld_{slug}.py'
    text = owner.read_text()
    text = re.sub(r"(\{sha!r\}|'[0-9a-f]{64}'), \d+, (\d+), \{[^}]*\}\)",
                  lambda m: f"{m.group(1)}, {len(rows)}, {m.group(2)}, {blocks!r})", text)
    owner.write_text(text)
    print(f'{slug}: adopted {adopted}, rejected {len(rejected)}, still unowned {len(kept)}')
    for r in rejected:
        print('  rejected', *r)


if __name__ == '__main__':
    slug, mode = sys.argv[1], sys.argv[2]
    if mode == 'packets':
        packets(slug, Path(sys.argv[3]))
    else:
        adopt(slug, Path(sys.argv[3]), Path(sys.argv[4]))
