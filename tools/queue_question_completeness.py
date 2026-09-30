#!/usr/bin/env python3
"""Cheap review queue; never adjudicates or changes learner content."""
import hashlib
import argparse
import json
import re
from collections import Counter
from pathlib import Path

from audit_question_structure import load_marrow
from build_question_completeness_reviews import load_inputs

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-reviewed', action='store_true', help='Fail if the source review queue contains an unreviewed candidate')
    args = parser.parse_args()
    audit_path = ROOT / 'build/question-fidelity/structure-audit.json'
    audit = json.loads(audit_path.read_text())
    records, hashes = load_marrow()
    raw = {q['id']: q for record in records for q in record['questions']}
    if hashes != audit['canonicalShardSha256']:
        raise ValueError('Stale structural audit: rerun audit_question_structure.py')
    rows = {q['id']: q for q in audit['candidates'] if q['unresolved']}
    inputs, input_hashes = load_inputs()
    if input_hashes != hashes:
        raise ValueError('Source changed while constructing review queue')
    all_raw = inputs['raw']
    flagged = {qid for qid, q in raw.items()
               if str(q.get('reviewStatus', '')).startswith('needs_manual_review')}
    coverage = json.loads((ROOT / 'data/marrow/images/coverage.json').read_text())
    visuals = {}
    for ref in coverage['sourceVisuals']:
        visuals.setdefault(ref['questionId'], []).append({k: ref.get(k) for k in
            ('id', 'role', 'coverageStatus', 'released', 'sourcePages', 'reviewedSourcePages')})
    runtime_source = (ROOT / 'app/src/main/assets/marrow_visual_metadata.js').read_text().strip()
    runtime_visuals = json.loads(runtime_source.removeprefix('window.MARROW_VISUALS=').removesuffix(';'))
    # Also inspect questions that never acquired figure metadata. An inventory-only
    # audit cannot find an omitted continuation-page figure.
    supplemental = {}
    cue = re.compile(r'\b(?:shown|depicted|illustrated)\b|\b(?:structure|area|region|organ|part|nerve)\s+(?:marked|labelled|labeled)\b|\b(?:marked|labelled|labeled)\s+(?:structure|area|region)\b|\b(?:image|figure|diagram|graph|photograph)\s+(?:below|above|given)\b', re.I)
    for qid, q in all_raw.items():
        reasons = []
        stem = str(inputs['normalized'][qid].get('question', ''))
        if qid in raw and cue.search(stem) and not any(
                ref.get('role') == 'question' and ref.get('src') for ref in runtime_visuals.get(qid, [])):
            reasons.append('visual-dependency-without-released-question-image')
        # Replacement glyphs are cheap to detect across both banks, including
        # ordinary questions excluded by the table-oriented structural audit.
        if re.search('[\u25a0\ufffd]', stem):
            reasons.append('question-replacement-glyph')
        if reasons:
            supplemental[qid] = reasons
    queue = []
    reviewed = {}
    for evidence_path in sorted((ROOT / 'docs/question-completeness').glob('review-*.json')):
        report = json.loads(evidence_path.read_text())
        for item in report.get('questions', report.get('items', [])):
            qid = item.get('id', item.get('questionId'))
            decision = item.get('decision', item.get('outcome'))
            if qid and decision:
                reviewed[qid] = (decision, str(evidence_path.relative_to(ROOT)))
    for qid in sorted(set(rows) | flagged | set(supplemental)):
        row = rows.get(qid, {})
        q = all_raw.get(qid, {})
        queue.append({
            'id': qid, 'priority': 1 if qid in flagged else 2,
            'bank': row.get('bank', q.get('bank', 'Marrow')), 'subject': row.get('subject', q.get('subject')),
            'sourcePage': row.get('sourcePage', q.get('sourcePage')),
            'reviewStatus': q.get('reviewStatus', row.get('reviewStatus')),
            'reasons': (['existing-manual-review-flag'] if qid in flagged else []) + row.get('issues', []) + supplemental.get(qid, []),
            'families': row.get('families', []),
            'canonicalSourceFingerprint': row.get('canonicalSourceFingerprint'),
            'question': row.get('rawQuestion', q.get('question')),
            'visualCoverage': visuals.get(qid, []),
            'decision': reviewed.get(qid, ('UNREVIEWED', None))[0],
            'evidence': [reviewed[qid][1]] if qid in reviewed else [],
        })
    queue.sort(key=lambda q: (q['priority'], q['bank'], q['subject'] or '', q['sourcePage'] or 0, q['id']))
    result = {'schemaVersion': 1, 'inputHead': audit['head'],
              'auditSha256': hashlib.sha256(audit_path.read_bytes()).hexdigest(),
              'canonicalShardSha256': hashes,
              'warning': 'Heuristic candidates are not confirmed defects. Released images do not prove question completeness. Decisions require source review.',
              'summary': {'total': len(queue), 'byPriority': dict(Counter(q['priority'] for q in queue)),
                          'unreviewed': sum(q['decision'] == 'UNREVIEWED' for q in queue),
                          'byBank': dict(Counter(q['bank'] for q in queue))}, 'questions': queue}
    output = audit_path.parent / 'completeness-review-queue.json'
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print('QUESTION_COMPLETENESS_QUEUE_OK', json.dumps(result['summary']), output)
    if args.require_reviewed and result['summary']['unreviewed']:
        raise SystemExit('New source-completeness candidates require review: ' + ', '.join(
            q['id'] for q in queue if q['decision'] == 'UNREVIEWED'))


if __name__ == '__main__':
    main()
