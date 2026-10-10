#!/usr/bin/env python3
"""Strip screenshot chrome / overlap from blocked documents so the hygiene gate can load them.

The extractor already marks such questions blocked; this only removes the offending
fragments (they are UI text, never medical content) and records it in `issues`.
"""
import json, re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from uworld_content_hygiene import validate_display, CHROME

ROOT = HERE.parents[1]


def clean(doc):
    try:
        validate_display(doc); return False
    except ValueError:
        pass
    strip = lambda t: re.sub(r'\s{2,}', ' ', CHROME.sub(' ', t)).strip()
    doc['question'] = strip(doc['question']) or doc['question']
    doc['educational_objective'] = strip(doc.get('educational_objective') or '')
    for o in doc['options']:
        o['text'] = strip(o['text']) or o['text']
    paras, seen = [], []
    for n in doc['explanation']:
        if n['type'] != 'paragraph':
            paras.append(n); continue
        t = strip(n['text'])
        words = re.findall(r'\w+', t.lower())
        runs = {tuple(words[i:i + 32]) for i in range(max(0, len(words) - 31))}
        if t and not (runs & set(seen)):
            paras.append({**n, 'text': t}); seen.extend(runs)
    doc['explanation'] = paras
    doc['status'] = 'blocked'
    doc['issues'] = doc.get('issues', []) + ['screenshot chrome removed automatically']
    validate_display(doc)
    return True


def fix_percents(src):
    """OCR can read '17%' as '117%'; drop impossible values and hold the question."""
    import hashlib
    from uworld_reviewed_document import record_hash
    rows = [json.loads(l) for l in (src / 'normalized.jsonl').read_text().splitlines() if l.strip()]
    bs = sorted((src / 'reviewed').glob('batch-*.json'))
    docs = {d['id']: d for b in bs for d in json.loads(b.read_text())['records']}
    ok = lambda v: v is None or (isinstance(v, (int, float)) and 0 <= v <= 100)
    n = 0
    for r in rows:
        d = docs[r['question_id']]
        bad = any(not ok(o['selection_percent']) for o in r['options']) or not ok(r['statistics'].get('answered_correctly_percent'))
        if bad:
            for o in r['options'] + d['options']:
                if not ok(o['selection_percent']):
                    o['selection_percent'] = None
            for st in (r['statistics'], d['statistics']):
                if not ok(st.get('answered_correctly_percent')):
                    st['answered_correctly_percent'] = None
            d['statistics']['selection_percent'] = {k: (v if ok(v) else None) for k, v in d['statistics']['selection_percent'].items()}
            d['status'] = 'blocked'; d['issues'] = d['issues'] + ['impossible percentage removed']; n += 1
        d['source_record_sha256'] = record_hash(r)
    raw = ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows).encode()
    (src / 'normalized.jsonl').write_bytes(raw)
    for b in bs:
        data = json.loads(b.read_text()); data['records'] = [docs[x['id']] for x in data['records']]
        b.write_text(json.dumps(data, ensure_ascii=False, indent=1))
    m = json.loads((src / 'manifest.json').read_text()); m['jsonl_sha256'] = hashlib.sha256(raw).hexdigest()
    (src / 'manifest.json').write_text(json.dumps(m, indent=1))
    return n


def main():
    for slug in sys.argv[1:]:
        src = ROOT / 'data/uworld/prepared' / slug
        pct = fix_percents(src)
        n = 0
        for b in sorted((src / 'reviewed').glob('batch-*.json')):
            data = json.loads(b.read_text())
            n += sum(clean(d) for d in data['records'])
            b.write_text(json.dumps(data, ensure_ascii=False, indent=1))
        qa_p = src / 'qa_report.json'; qa = json.loads(qa_p.read_text())
        docs = [d for b in sorted((src / 'reviewed').glob('batch-*.json')) for d in json.loads(b.read_text())['records']]
        qa['flagged'] = [{'id': d['id'], 'pages': d['reviewed_pages'], 'issues': d['issues']} for d in docs if d['status'] != 'verified']
        qa_p.write_text(json.dumps(qa, ensure_ascii=False, indent=1))
        m_p = src / 'manifest.json'; m = json.loads(m_p.read_text())
        m.update(verified=len(docs) - len(qa['flagged']), blocked=len(qa['flagged'])); m_p.write_text(json.dumps(m, indent=1))
        print(slug, 'cleaned', n, 'percent fixes', pct)


if __name__ == '__main__':
    main()
