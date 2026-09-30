#!/usr/bin/env python3
"""Integrate the exact source-reviewed final Physiology request, without inferring mappings.

Native images retain their bytes. Composite/vector source regions render only on
Ubuntu CI. This consumes reviewed source ownership, not page-level candidates.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
from pypdf import PdfReader
from marrow_images import ROOT, DATA, questions, binding_is_released

REQUEST = DATA / 'images/review_requests/FINAL_PHYS_SOURCE_REVIEW_20260930.json'
REGISTRY = DATA / 'images/registry.json'


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--native-only', action='store_true')
    args = parser.parse_args()
    request = json.loads(REQUEST.read_text())
    assert request['schemaVersion'] == 1
    source = request['source']
    pdf = DATA / 'source_pdfs' / source['file']
    assert digest(pdf.read_bytes()) == source['sha256']
    registry = json.loads(REGISTRY.read_text())
    qmap = questions()
    reader = PdfReader(pdf)
    ids = [entry['referenceId'] for entry in request['entries']]
    assert len(ids) == len(set(ids)) == 14
    document = None
    if not args.native_only:
        from verification_preflight import pdf_preflight
        assert pdf_preflight(require=True)
        import fitz
        document = fitz.open(pdf)
    applied = []
    for entry in request['entries']:
        assert qmap[entry['questionId']]['subject'] == 'Physiology'
        assert entry['referenceId'] == entry['questionId'] + f":figure:{entry['order']}"
        assert entry['role'] in {'question', 'explanation'} and entry['notes']
        assert entry['status'] in {'PASS', 'SOURCE_LIMITED'}
        if entry['role'] == 'question':
            assert entry['alt'] == 'Source figure', 'Question captions must remain neutral'
        if entry['method'] == 'region-render' and args.native_only:
            continue
        page = int(entry['page'])
        if entry['method'] == 'native-jpeg-stream':
            objects = reader.pages[page - 1]['/Resources']['/XObject']
            matches = [v.get_object() for v in objects.values() if v.idnum == entry['xref']]
            assert len(matches) == 1
            obj = matches[0]
            assert obj['/Subtype'] == '/Image'
            assert obj['/Filter'] == '/DCTDecode' or obj['/Filter'] == ['/DCTDecode']
            assert not obj.get('/Mask') and not obj.get('/SMask')
            raw = obj._data
            assert digest(raw) == entry['expectedStreamSha256']
            width, height, suffix = int(obj['/Width']), int(obj['/Height']), '.jpg'
        else:
            assert entry['method'] == 'region-render' and document is not None
            import fitz
            rect = fitz.Rect(entry['region'])
            source_page = document[page - 1]
            assert source_page.rotation == 0 and source_page.rect.contains(rect)
            assert entry['dpi'] == 300
            pix = source_page.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72), clip=rect, alpha=False)
            raw, width, height, suffix = pix.tobytes('png'), pix.width, pix.height, '.png'
        sha = digest(raw)
        relative_path = f'data/marrow/images/originals/{sha}{suffix}'
        target = ROOT / relative_path
        if target.exists():
            assert target.read_bytes() == raw
        else:
            target.write_bytes(raw)
        source_binding = {k: entry[k] for k in ('page', 'xref', 'region')}
        evidence = f"Direct source-page review 2026-09-30; {REQUEST.relative_to(ROOT)}; PDF SHA-256 {source['sha256']}."
        # A wrong earlier candidate must stay rejected even if that shared asset
        # is now approved for its true owning question.
        for old_asset in registry['assets']:
            for old_binding in old_asset['bindings']:
                if (old_binding['questionId'], old_binding['role'], old_binding['order']) != (entry['questionId'], entry['role'], entry['order']):
                    continue
                if old_asset['original']['sha256'] == sha:
                    continue
                if binding_is_released(old_asset, old_binding):
                    assert entry.get('replacesSha256') == old_asset['original']['sha256'], 'Do not silently replace a released binding'
                old_binding['status'] = 'REJECTED'
                old_binding.setdefault('source', {k: old_asset['source'][k] for k in ('page', 'xref', 'region')})
                old_binding['qa'] = {'sourceCompared': True, 'notes': 'Superseded source crop/candidate; replaced by the directly source-reviewed complete owning figure. ' + entry['notes'], 'evidence': evidence}
        matches = [asset for asset in registry['assets'] if asset['original']['sha256'] == sha]
        assert len(matches) <= 1
        qa = {'sourceCompared': True, 'notes': entry['notes'], 'evidence': evidence,
              'originalSha256': sha, 'productionSha256': sha}
        if matches:
            asset = matches[0]
            assert asset['subject'] == 'Physiology'
            assert asset['production']['sha256'] == sha
            # Explicitly reject the known glial diagram misbinding to Q3 before
            # approving its true Q1 ownership. Never release siblings by accident.
            for binding in asset['bindings']:
                if entry['questionId'] == 'marrow__PHYS_CH06_Q001' and binding['questionId'] == 'marrow__PHYS_CH06_Q003':
                    binding['status'] = 'REJECTED'
                    binding.setdefault('source', {k: asset['source'][k] for k in ('page', 'xref', 'region')})
                    binding['qa'] = {'sourceCompared': True, 'notes': 'Page 105 glial-cell classification belongs to Solution 1; Q3 neuron diagram is on page 106.', 'evidence': evidence}
            if asset['status'] not in {'PASS', 'SOURCE_LIMITED'}:
                asset.update(status=entry['status'], qa=qa, kind=entry['kind'])
        else:
            record = {'path': relative_path, 'sha256': sha, 'width': width, 'height': height}
            asset = {'id': f'physiology-{sha[:16]}', 'subject': 'Physiology', 'kind': entry['kind'],
                     'reviewBatch': request['batchId'], 'source': {**source, **source_binding},
                     'bindings': [], 'original': record, 'production': dict(record),
                     'method': entry['method'], 'status': entry['status'], 'qa': qa}
            registry['assets'].append(asset)
        bindings = [b for b in asset['bindings'] if (b['questionId'], b['role'], b['order']) == (entry['questionId'], entry['role'], entry['order'])]
        assert len(bindings) <= 1
        binding = {'questionId': entry['questionId'], 'role': entry['role'], 'order': entry['order'],
                   'alt': entry['alt'], 'source': source_binding, 'status': 'PASS',
                   'reviewBatch': request['batchId'], 'qa': qa}
        if bindings:
            bindings[0].clear()
            bindings[0].update(binding)
        else:
            asset['bindings'].append(binding)
        applied.append(entry['referenceId'])
    if document is not None:
        document.close()
    REGISTRY.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + '\n')
    print('PHYS_FINAL_SOURCE_REVIEW_APPLIED', len(applied))


if __name__ == '__main__':
    main()
