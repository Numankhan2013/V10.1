#!/usr/bin/env python3
"""Regressions for fail-closed Marrow source-image discovery."""
import json
from pathlib import Path

from marrow_images import ROOT, questions
from marrow_visual_inventory import source_image_occurrences, source_visual_expectations


def require_occurrence(occurrences,qid,role):
    rows=[o for o in occurrences if any(x['questionId']==qid and x['role']==role for x in o['candidateOwners'])]
    assert rows, f'{qid}: no {role} PDF image placement discovered from canonical page provenance'
    return rows


def main():
    audit_path=ROOT/'build/marrow-images/audit.json'
    assert audit_path.exists(),'run marrow_images.py audit first'
    audit=json.loads(audit_path.read_text())
    qmap=questions()
    occurrences=source_image_occurrences(audit,qmap,'Biochemistry')

    # Permanent regressions from the learner-reported omissions. These do not
    # depend on fragile visual metadata: source page provenance + PDF placement
    # must be sufficient to keep each case visible to the integration workflow.
    cases=[
        ('marrow__BIOCHEM_CH18_Q003','explanation'),
        ('marrow__BIOCHEM_CH18_Q005','explanation'),
        ('marrow__BIOCHEM_CH18_Q006','explanation'),
        ('marrow__BIOCHEM_CH19_Q002','question'),
        ('marrow__BIOCHEM_CH19_Q011','question'),
        ('marrow__BIOCHEM_CH19_Q011','explanation'),
        ('marrow__BIOCHEM_CH19_Q012','question'),
        ('marrow__BIOCHEM_CH19_Q012','explanation'),
        ('marrow__BIOCHEM_CH19_Q019','question'),
        ('marrow__BIOCHEM_CH19_Q019','explanation'),
        ('marrow__BIOCHEM_CH20_Q006','explanation'),
        ('marrow__BIOCHEM_CH20_Q011','explanation'),
        ('marrow__BIOCHEM_CH20_Q014','explanation'),
        ('marrow__BIOCHEM_CH20_Q017','explanation'),
        ('marrow__BIOCHEM_CH21_Q008','explanation'),
        ('marrow__BIOCHEM_CH21_Q009','question'),
        ('marrow__BIOCHEM_CH21_Q010','question'),
        ('marrow__BIOCHEM_CH21_Q012','question'),
        ('marrow__BIOCHEM_CH22_Q002','explanation'),
    ]
    found={}
    for qid,role in cases:
        found[f'{qid}:{role}']=[(r['page'],r['xref']) for r in require_occurrence(occurrences,qid,role)]

    # Metadata discovery remains useful when present, but is no longer the
    # source-of-truth for completeness.
    sample={
        'id':'marrow__TEST_Q001','subject':'Biochemistry',
        'question_visuals':[{'visual_id':'QF1','source_page':10,'role':'question','visual_type':'graph'}],
        'structuredExplanation':{'blocks':[
            {'type':'paragraph','text':'x','source_page':11},
            {'type':'flowchart','visual_id':'F1','source_page':12,'role':'explanation'},
            {'type':'table','table_id':'T1','source_page':13,'rows':[]},
        ]},
    }
    rows=source_visual_expectations(sample)
    assert [(x['role'],x['visualId']) for x in rows]==[('question','QF1'),('explanation','F1')],rows
    assert len(occurrences)>100,'Biochemistry PDF placement inventory implausibly small'
    print('MARROW_IMAGE_SOURCE_COVERAGE_REGRESSION_OK',json.dumps({'placements':len(occurrences),'cases':found},sort_keys=True))

if __name__=='__main__':main()
