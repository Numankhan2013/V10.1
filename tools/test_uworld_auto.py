#!/usr/bin/env python3
"""Auto-extracted UWorld collections: shippable documents, committed crops, OCR repair helpers."""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / 'uworld_auto'))
from uworld_collections import COLLECTIONS
from uworld_reviewed_document import figures
from extract import rejoin, split_options, PCT_RE
from fix_ocr_text import clean_doc, clean

ROOT = Path(__file__).resolve().parents[1]


def main():
    autos = [m for m in COLLECTIONS if getattr(getattr(m, 'OWNER', None), 'AUTO', False)]
    assert autos, 'no auto-extracted collection registered'
    total = verified = 0
    for m in autos:
        manifest, rows = m.load_source()
        docs = m.reviewed_documents(rows)
        bank = m.bank_record()
        assert len(docs) == len(rows) == len(bank['questions']) == manifest['record_count']
        figs = ROOT / manifest['figures_dir']
        for doc in docs.values():
            for node in figures(doc):
                assert (figs / Path(node['asset']).name).exists(), node['asset']
            if doc['status'] == 'verified':
                assert not doc['issues'] and doc['educational_objective'] and doc['correct_label']
                verified += 1
            # Reviewed OCR misreads and the image watermark stay corrected.
            assert not clean_doc(doc), (doc['id'], list(clean_doc(doc)))
        qa = json.loads((m.OWNER.SOURCE / 'qa_report.json').read_text())
        assert {f['id'] for f in qa['flagged']} == {d['id'] for d in docs.values() if d['status'] != 'verified'}
        total += len(rows)
    # OCR repair helpers
    assert clean('@UWO<ld lmmunosuppressed patients with dusters') == 'Immunosuppressed patients with clusters'
    assert clean('Obtain a court order; bed rails') == 'Obtain a court order; bed rails'
    vocab = {'interna': 5, 'strongly': 9, 'last': 30, 'the': 900, 'a': 500, 'is': 400, 'typical': 10, 'atypical': 3}
    assert rejoin('Theca intern a', vocab) == 'Theca interna'
    assert rejoin('are s t rongly related', vocab) == 'are strongly related'
    assert rejoin('a typical case', vocab) == 'a typical case'
    lines = [{'text': t, 'x0': 54, 'y0': y, 'y1': y + 14} for t, y in
             [('( A. Early menarche (8%)', 0), ('X @) B. Family history of endometrial', 30), ('cancer (9%)', 46),
              ('Amoxicillin (20%) X ® 8 . Bactrim (5%)', 80)]]
    opts = split_options(lines)
    assert [o['letter'] for o in opts] == list('ABCD'), opts
    assert PCT_RE.sub('', opts[1]['text']).strip().endswith('endometrial cancer')
    # Long choices wrap with the percentage on their first line, or sorted just above the text.
    box = lambda t, x0, x1, y0, y1: {'text': t, 'x0': x0, 'x1': x1, 'y0': y0, 'y1': y1}
    lines = [box('0 A . "I believe that ensuring safety is our', 50, 740, 249, 270), box('(57%)', 762, 803, 254, 268),
             box('shared goal."', 100, 190, 279, 293), box('® 8 . "We should proceed with vaccination', 50, 730, 307, 328),
             box('(0%)', 771, 803, 312, 326), box('today."', 100, 147, 337, 351), box('0', 50, 63, 364, 385),
             box('(16%)', 762, 803, 369, 383), box('C. "I would like to provide resources', 79, 743, 370, 384)]
    opts = split_options(lines)
    assert [(o['letter'], o['text']) for o in opts] == [
        ('A', '"I believe that ensuring safety is our shared goal." (57%)'),
        ('B', '"We should proceed with vaccination today." (0%)'),
        ('C', '"I would like to provide resources (16%)')], opts
    print(f'UWORLD_AUTO_OK collections={len(autos)} questions={total} verified={verified}')


if __name__ == '__main__':
    main()
