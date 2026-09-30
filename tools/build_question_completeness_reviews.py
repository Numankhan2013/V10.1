#!/usr/bin/env python3
"""Pin reviewed display repairs and compile their shared runtime contracts.

This is a source-only compiler. It never edits imported question bundles or
generates PDFs/app assets. Review acceptance is a separate primary-writer step.
"""
import argparse
import copy
import hashlib
import json
import subprocess
from pathlib import Path

from audit_question_structure import load_marrow

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / 'data/question_completeness_reviews_v1.json'
CORE = ROOT / 'tools/question_presentation_core.js'
START = '  /* NK_QUESTION_COMPLETENESS_REVIEWS_START */'
END = '  /* NK_QUESTION_COMPLETENESS_REVIEWS_END */'


def packed(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()


def digest(value):
    return hashlib.sha256(value).hexdigest()


def load_inputs():
    records, hashes = load_marrow()
    raw = [copy.deepcopy(q) for record in records for q in record['questions']]
    owner_path = ROOT / 'tools/apply_marrow_bank_pilot.py'
    owner = owner_path.read_text()
    namespace = {'DATA': ROOT / 'data/marrow', 'json': json, 'hashlib': hashlib, 'expanded_records': records}
    # Same bounded source-verified display-overlay block used by the audit.
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(owner[owner.index('CONTENT_OVERRIDE_PATHS='):owner.index('expanded_ids=')], str(owner_path), 'exec'), namespace)
    node = r'''
const fs=require('fs'),vm=require('vm'),input=JSON.parse(fs.readFileSync(0,'utf8'));
const c={window:{},SUBJECTS:[],esc:v=>String(v??'')};vm.createContext(c);
for(const file of input.prepFiles)vm.runInContext(fs.readFileSync(file,'utf8'),c);
vm.runInContext(input.hygiene,c);
vm.runInContext(input.core,c);
const prep=[{subject:'Biochemistry',questions:c.window.QBANK_DATA.questions},...c.window.SUBJECT_QBANK_DATA.subjects]
 .flatMap(r=>r.questions.map(q=>({...q,subject:r.subject,bank:'PrepLadder'})));
const originals=[...prep,...input.rawMarrow],learner=[...prep,...input.marrow];
const clone=q=>JSON.parse(JSON.stringify(q));
const clean=learner.map(q=>c.nkSanitizeMarrowQuestion(clone(q)));
const normalized=clean.map(q=>{const value=clone(q);c.nkQuestionPresentationFor(value);return value;});
process.stdout.write(JSON.stringify({raw:originals,learner,clean,normalized}));
'''
    payload = {'prepFiles': [str(ROOT / 'app/src/main/assets' / name) for name in ('qbank_data.js', 'subjects_qbank_data.js')],
               'hygiene': (ROOT / 'tools/question_content_hygiene_core.js').read_text(),
               'core': CORE.read_text(),
               'rawMarrow': raw, 'marrow': [q for record in records for q in record['questions']]}
    data = json.loads(subprocess.run(['node', '-e', node], input=json.dumps(payload), text=True,
                                    capture_output=True, check=True, cwd=ROOT).stdout)
    return {name: {q['id']: q for q in data[name]} for name in data}, hashes


def fnv(text):
    result = 2166136261
    # JavaScript hashes UTF-16 code units, not Unicode code points.
    encoded = text.encode('utf-16-le')
    for index in range(0, len(encoded), 2):
        result = ((result ^ int.from_bytes(encoded[index:index + 2], 'little')) * 16777619) & 0xffffffff
    return result


def runtime_hash(q):
    fields = ['id', 'question', 'options', 'correctOption', 'sourcePage', 'sourcePageEnd']
    return fnv(json.dumps([q.get(key) for key in fields], ensure_ascii=False, separators=(',', ':')))


def compiled_specs(ledger, inputs, hashes):
    assert ledger['schemaVersion'] == 1 and ledger['canonicalShardSha256'] == hashes
    specs = {}
    source_hashes = {}
    for entry in ledger['entries']:
        qid = entry['id']
        assert qid not in specs and qid in inputs['raw']
        q = inputs['raw'][qid]
        fingerprint = digest(packed({key: q.get(key) for key in (
            'id', 'question', 'options', 'correctOption', 'sourcePage', 'sourceQuestionId')}))
        assert fingerprint == entry['canonicalSourceFingerprint'], qid + ' source question changed'
        source = entry['source']
        path = ROOT / source['file']
        if source['file'] not in source_hashes:
            source_hashes[source['file']] = digest(path.read_bytes())
        assert source_hashes[source['file']] == source['sha256']
        assert source['pages'] and entry['evidenceFile'] and entry['decision']
        spec = {'decision': entry['decision'], **entry['display']}
        if 'correctOption' in spec:
            assert qid in {'physiology-23-38', 'physiology-33-33'} and q.get('correctOption') is None
            assert spec['correctOption'] == 1 and entry['decision'] == 'EXACT_SOURCE_REPAIR'
        variants = [copy.deepcopy(inputs[name][qid]) for name in ('raw', 'learner', 'clean', 'normalized')]
        fingerprints = set()
        explanation_hashes = set()
        for variant in variants:
            fingerprints.add(runtime_hash(variant))
            if spec.get('correctOption') is not None:
                variant['correctOption'] = spec['correctOption']
                fingerprints.add(runtime_hash(variant))
            if spec.get('options'):
                assert len(variant['options']) == len(spec['options'])
                assert [o['letter'] for o in variant['options']] == [o['letter'] for o in spec['options']]
                variant['options'] = copy.deepcopy(spec['options'])
                fingerprints.add(runtime_hash(variant))
            if spec.get('explanation') or spec.get('explanationFirstParagraph'):
                old = variant.get('explanation', '')
                explanation_hashes.add(fnv(old))
                new = spec.get('explanation') or spec['explanationFirstParagraph'] + (old[old.index('\n\n'):] if '\n\n' in old else '')
                explanation_hashes.add(fnv(new))
        spec['fingerprints'] = sorted(fingerprints)
        if explanation_hashes:
            spec['explanationHashes'] = sorted(explanation_hashes)
        table = spec.get('table')
        if table:
            assert table['groups'] and len(table['groups']) == len(table['headers'])
            assert all(group and len({cell['label'] for cell in group}) == len(group) for group in table['groups'])
            assert all(cell['value'].strip() for group in table['groups'] for cell in group)
            assert len({len(group) for group in table['groups']}) == 1, qid + ' unequal reviewed table'
            table['rows'] = [[group[index] for group in table['groups']] for index in range(len(table['groups'][0]))]
        specs[qid] = spec
    return specs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    inputs, hashes = load_inputs()
    ledger = json.loads(LEDGER.read_text())
    specs = compiled_specs(ledger, inputs, hashes)
    block = START + '\n  const NK_QUESTION_COMPLETENESS_REVIEWS_V1=' + json.dumps(specs, ensure_ascii=False, separators=(',', ':')) + ';\n' + END
    source = CORE.read_text()
    assert source.count(START) == source.count(END) == 1
    start, end = source.index(START), source.index(END) + len(END)
    result = source[:start] + block + source[end:]
    if args.check:
        assert source == result, 'Reviewed runtime contracts stale: run build_question_completeness_reviews.py'
    else:
        CORE.write_text(result)
    print('QUESTION_COMPLETENESS_REVIEWS_OK', len(specs))


if __name__ == '__main__':
    main()
