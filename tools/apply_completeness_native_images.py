#!/usr/bin/env python3
"""Extract exact reviewed native streams discovered by the completeness pass."""
import json
from pypdf import PdfReader

from marrow_images import DATA, ROOT, SOURCES, binding_is_released, questions, sha


def main():
    request_path = DATA / 'images/source_visual_discoveries.json'
    request = json.loads(request_path.read_text())
    assert request['schemaVersion'] == 1
    registry_path = DATA / 'images/registry.json'
    registry = json.loads(registry_path.read_text())
    qmap = questions()
    readers = {}
    source_hashes = {}
    for entry in request['entries']:
        q = qmap[entry['questionId']]
        assert q['subject'] == entry['subject']
        fingerprint = sha(json.dumps({key: q.get(key) for key in (
            'id', 'question', 'options', 'correctOption', 'sourcePage', 'sourceQuestionId')},
            ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode())
        assert fingerprint == entry['canonicalSourceFingerprint']
        assert entry['role'] == 'question' and entry['reason'] and entry['evidence']
        source = entry['source']
        assert source['file'] == SOURCES[entry['subject']][1]
        pdf = DATA / 'source_pdfs' / source['file']
        if source['file'] not in source_hashes:
            source_hashes[source['file']] = sha(pdf.read_bytes())
            readers[source['file']] = PdfReader(pdf)
        assert source_hashes[source['file']] == source['sha256']
        reader = readers[source['file']]
        assert len(entry['sourcePages']) == 1
        page = entry['sourcePages'][0]
        matches = [obj.get_object() for obj in reader.pages[page - 1]['/Resources']['/XObject'].values()
                   if obj.idnum == entry['xref']]
        assert len(matches) == 1
        obj = matches[0]
        assert obj['/Subtype'] == '/Image'
        assert obj['/Filter'] in ('/DCTDecode', ['/DCTDecode'])
        assert not obj.get('/SMask') and not obj.get('/Mask')
        raw = obj._data
        digest = sha(raw)
        assert digest == entry['expectedStreamSha256']
        path = f'data/marrow/images/originals/{digest}.jpg'
        target = ROOT / path
        if target.exists():
            assert target.read_bytes() == raw
        else:
            target.write_bytes(raw)
        record = {'path': path, 'sha256': digest, 'width': int(obj['/Width']), 'height': int(obj['/Height'])}
        binding_source = {'page': page, 'xref': entry['xref'], 'region': entry['region']}
        qa = {'sourceCompared': True, 'notes': entry['reason'], 'evidence': entry['evidence'],
              'originalSha256': digest, 'productionSha256': digest}
        assets = [a for a in registry['assets'] if a['original']['sha256'] == digest]
        assert len(assets) <= 1
        if assets:
            asset = assets[0]
            assert asset['subject'] == entry['subject'] and asset['production']['sha256'] == digest
            assert asset['status'] in {'PASS', 'SOURCE_LIMITED'}
        else:
            asset = {'id': entry['subject'].lower() + '-' + digest[:16], 'subject': entry['subject'],
                     'kind': entry['kind'], 'source': {**source, **binding_source},
                     'bindings': [], 'original': record, 'production': dict(record),
                     'method': 'native-jpeg-stream', 'status': 'PASS', 'qa': qa,
                     'reviewBatch': 'QUESTION_COMPLETENESS_20260930'}
            registry['assets'].append(asset)
        for old_asset in registry['assets']:
            for old in old_asset['bindings']:
                if (old['questionId'], old['role'], old['order']) == (entry['questionId'], entry['role'], entry['order']):
                    assert old_asset is asset and binding_is_released(old_asset, old), 'Conflicting image binding'
        binding = {'questionId': entry['questionId'], 'role': entry['role'], 'order': entry['order'],
                   'alt': 'Source figure', 'source': binding_source, 'status': 'PASS', 'qa': qa,
                   'reviewBatch': 'QUESTION_COMPLETENESS_20260930'}
        if not any((b['questionId'], b['role'], b['order']) == (entry['questionId'], entry['role'], entry['order']) for b in asset['bindings']):
            asset['bindings'].append(binding)
    registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + '\n')
    print('COMPLETENESS_NATIVE_IMAGES_APPLIED', len(request['entries']))


if __name__ == '__main__':
    main()
