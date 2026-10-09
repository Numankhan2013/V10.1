#!/usr/bin/env python3
"""Apply reviewer corrections to an extracted collection without re-reading the PDF.

Usage: apply_reviews.py <slug> <review-out-dir>
Each <review-out-dir>/UWORLD_<id>.json follows review INSTRUCTIONS.md. Only flagged
questions of this collection are touched. Corrections are also stored in
reviewed/fixes.json so a later full re-extraction re-applies them.
"""
import hashlib, json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
from uworld_reviewed_document import record_hash
from uworld_content_hygiene import validate_display

ROOT = HERE.parents[1]
PICTURE_FLAG = 'choices look like pictures or a table'


def to_fix(cur, rev):
    """Reviewer JSON -> fields of a display document (figures are kept from the extractor)."""
    letters = [o['letter'] for o in rev['options']]
    if letters != list('ABCDEFGHI')[:len(letters)] or rev['correct_label'] not in letters:
        raise ValueError('choice letters')
    paras = [p.strip() for p in rev['explanation_paragraphs'] if p and p.strip()]
    if not paras or not rev['question'].strip() or any(not o['text'].strip() for o in rev['options']):
        raise ValueError('empty field')
    figures = [n for n in cur['explanation'] if n['type'] != 'paragraph']
    status = rev.get('status')
    issues = [] if status == 'verified' else ['review: ' + (rev.get('notes') or 'held by reviewer')]
    # A correction should stay close to what the screenshots' OCR said; a large rewrite
    # (e.g. a reviewer that could not see the images) is never trusted as verified.
    from difflib import SequenceMatcher
    close = lambda a, b: SequenceMatcher(None, a.lower(), b.lower(), autojunk=False).ratio()
    old_p = ' '.join(n['text'] for n in cur['explanation'] if n['type'] == 'paragraph')
    drift = [name for name, a, b, lim in (('stem', rev['question'], cur['question'], .85),
                                           ('explanation', ' '.join(paras), old_p, .80)) if close(a, b) < lim]
    if rev['correct_label'] != cur['correct_label']:
        drift.append('correct answer changed ' + cur['correct_label'] + '→' + rev['correct_label'])
    if status == 'verified' and drift:
        status, issues = 'blocked', ['review drifted from OCR: ' + ', '.join(drift)]
    if any(i.startswith(PICTURE_FLAG) for i in cur['issues']):
        status, issues = 'blocked', issues or ['review: picture/table choices need a person']
    return {
        'question': rev['question'].strip(),
        'options': [{'letter': o['letter'], 'text': o['text'].strip(), 'selection_percent': o.get('selection_percent')} for o in rev['options']],
        'correct_label': rev['correct_label'],
        'explanation': figures + [{'type': 'paragraph', 'text': p} for p in paras],
        'educational_objective': (rev.get('educational_objective') or '').strip(),
        'statistics': {'answered_correctly_percent': rev.get('answered_correctly_percent'),
                       'selection_percent': {o['letter']: o.get('selection_percent') for o in rev['options']}},
        'status': 'verified' if status == 'verified' else 'blocked', 'issues': issues,
    }


def main():
    slug, outdir = sys.argv[1], Path(sys.argv[2])
    src = ROOT / 'data/uworld/prepared' / slug
    manifest = json.loads((src / 'manifest.json').read_text())
    rows = [json.loads(l) for l in (src / 'normalized.jsonl').read_text().splitlines() if l.strip()]
    batches = sorted((src / 'reviewed').glob('batch-*.json'))
    docs = {r['id']: r for b in batches for r in json.loads(b.read_text())['records']}
    fixes_path = src / 'reviewed/fixes.json'
    fixes = json.loads(fixes_path.read_text()) if fixes_path.exists() else {}
    qa = json.loads((src / 'qa_report.json').read_text())
    applied, rejected = 0, []
    for flag in qa['flagged']:
        qid = flag['id']; f = outdir / f'{qid}.json'
        if not f.exists():
            continue
        try:
            fix = to_fix(docs[qid], json.loads(f.read_text()))
            probe = {**docs[qid], **fix}
            validate_display(probe)
        except Exception as e:  # malformed or leaky review: keep the question blocked
            rejected.append((qid, str(e))); continue
        fixes[qid] = fix; applied += 1
    by_id = {r['question_id']: r for r in rows}
    for qid, fix in fixes.items():
        if qid not in docs:
            continue
        d = docs[qid]; d.update(fix)
        row = by_id[qid]
        letters = [o['letter'] for o in d['options']]
        row.update(question_text=d['question'],
                   options=[{'label': o['letter'].lower(), 'text': o['text'], 'selection_percent': o['selection_percent']} for o in d['options']],
                   correct_option=d['correct_label'].lower(),
                   correct_answer_text=d['options'][letters.index(d['correct_label'])]['text'],
                   explanation={'text': '\n\n'.join(n['text'] for n in d['explanation'] if n['type'] == 'paragraph'),
                                'educational_objective': d['educational_objective']})
        row['statistics']['answered_correctly_percent'] = d['statistics']['answered_correctly_percent']
        d['source_record_sha256'] = record_hash(row)
    raw = ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows).encode()
    (src / 'normalized.jsonl').write_bytes(raw)
    for b in batches:
        data = json.loads(b.read_text())
        data['records'] = [docs[r['id']] for r in data['records']]
        b.write_text(json.dumps(data, ensure_ascii=False, indent=1))
    fixes_path.write_text(json.dumps(fixes, ensure_ascii=False, indent=1))
    flagged = [{'id': d['id'], 'pages': d['reviewed_pages'], 'issues': d['issues']} for d in docs.values() if d['status'] != 'verified']
    qa['flagged'] = flagged
    (src / 'qa_report.json').write_text(json.dumps(qa, ensure_ascii=False, indent=1))
    manifest.update(jsonl_sha256=hashlib.sha256(raw).hexdigest(), verified=len(docs) - len(flagged), blocked=len(flagged),
                    reviewed_by='claude-haiku (flagged questions only)')
    (src / 'manifest.json').write_text(json.dumps(manifest, indent=1))
    print(f'{slug}: applied {applied}, rejected {len(rejected)}, now verified {len(docs) - len(flagged)}/{len(docs)}')
    for r in rejected:
        print('  rejected', *r)


if __name__ == '__main__':
    main()
