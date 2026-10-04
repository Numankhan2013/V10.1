"""Source-pinned display documents; canonical imports and learner IDs stay immutable."""
from copy import deepcopy
from pathlib import Path
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parents[1]
REVIEWED = ROOT / 'data/uworld/reviewed/biochemistry'


def record_hash(row):
    return hashlib.sha256(json.dumps(row, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def figure_asset(qid, node, pdf_sha='806d95d6f09dde57d34e0d0b5fda69298a7789041bb570ce4fa6dd1c95d4fae9'):
    spec = {'pdf': pdf_sha,
            'page': node['page'], 'bbox': node['bbox']}
    digest = record_hash(spec)[:16]
    return f'source_visuals/uworld/{qid}-{digest}.png'


def percentage(value):
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= 100:
        raise ValueError('Invalid UWorld source percentage')
    return value


def validate_node(node, qid, pages, role, pdf_sha='806d95d6f09dde57d34e0d0b5fda69298a7789041bb570ce4fa6dd1c95d4fae9', page_size=(1417,728)):
    kind = node.get('type')
    if kind == 'paragraph':
        if not isinstance(node.get('text'), str) or not node['text'].strip():
            raise ValueError('Empty reviewed paragraph: ' + qid)
    elif kind == 'table':
        columns, rows = node.get('columns'), node.get('rows')
        if not isinstance(columns, list) or not columns or not isinstance(rows, list) or not rows:
            raise ValueError('Empty reviewed table: ' + qid)
        if any(not isinstance(row, list) or len(row) != len(columns) for row in rows):
            raise ValueError('Ragged reviewed table: ' + qid)
        if any(not isinstance(cell, str) for row in [columns] + rows for cell in row):
            raise ValueError('Non-text reviewed table cell: ' + qid)
    elif kind == 'figure':
        bbox = node.get('bbox')
        if node.get('page') not in pages or node.get('role') != role or not isinstance(bbox, list) or len(bbox) != 4:
            raise ValueError('Invalid reviewed figure provenance: ' + qid)
        if any(isinstance(n, bool) or not isinstance(n, (int, float)) or not math.isfinite(n) for n in bbox):
            raise ValueError('Invalid reviewed figure geometry: ' + qid)
        if not (0 <= bbox[0] < bbox[2] <= page_size[0] and 0 <= bbox[1] < bbox[3] <= page_size[1]):
            raise ValueError('Reviewed figure outside source page: ' + qid)
        node['asset'] = figure_asset(qid, node, pdf_sha)
    else:
        raise ValueError('Unknown reviewed document node: ' + qid)


def load_reviewed(rows, pdf_sha, reviewed_dir=None, page_size=(1417,728)):
    source = {r['question_id']: r for r in rows}
    result = {}
    for path in sorted((Path(reviewed_dir) if reviewed_dir is not None else REVIEWED).glob('batch-*.json')):
        batch = json.loads(path.read_text())
        if batch.get('schema_version') != 1 or batch.get('source_pdf_sha256') != pdf_sha:
            raise ValueError('Reviewed UWorld PDF/version mismatch: ' + path.name)
        for supplied in batch['records']:
            doc = deepcopy(supplied)
            qid = doc['id']
            row = source.get(qid)
            if row is None or qid in result or doc.get('source_record_sha256') != record_hash(row):
                raise ValueError('Reviewed UWorld source/identity mismatch: ' + qid)
            if sorted(doc.get('reviewed_pages', [])) != sorted(row['source'].get('source_pages', row['source'].get('all_question_id_pages', []))):
                raise ValueError('Incomplete UWorld page review: ' + qid)
            if doc.get('status') not in ('verified', 'blocked') or not isinstance(doc.get('issues'), list):
                raise ValueError('Invalid UWorld review status: ' + qid)
            if not isinstance(doc.get('question'), str) or not doc['question'].strip() or not doc.get('explanation'):
                raise ValueError('Empty UWorld reviewed content: ' + qid)
            labels = [o['letter'] for o in doc['options']]
            if labels != [o['label'].upper() for o in row['options']] or doc['correct_label'] != row['correct_option'].upper():
                raise ValueError('Reviewed UWorld answer/choice contract changed: ' + qid)
            if any(not isinstance(o.get('text'), str) or not o['text'].strip() for o in doc['options']):
                raise ValueError('Empty reviewed UWorld choice: ' + qid)
            pages = doc['reviewed_pages']
            for node in doc.get('question_blocks', []):
                validate_node(node, qid, pages, 'question', pdf_sha, page_size)
            for node in doc['explanation']:
                validate_node(node, qid, pages, 'explanation', pdf_sha, page_size)
            for option in doc['options']:
                if option.get('figure'):
                    validate_node(option['figure'], qid, pages, 'option', pdf_sha, page_size)
            statistics = doc['statistics']
            percentage(statistics.get('answered_correctly_percent'))
            if set(statistics.get('selection_percent', {})) != set(labels):
                raise ValueError('Incomplete UWorld statistic labels: ' + qid)
            for value in statistics['selection_percent'].values():
                percentage(value)
            result[qid] = doc
    return result


def figures(doc):
    return [n for n in doc.get('question_blocks', []) + doc['explanation'] if n['type'] == 'figure'] + [o['figure'] for o in doc['options'] if o.get('figure')]
