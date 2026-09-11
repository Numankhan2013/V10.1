#!/usr/bin/env python3
"""Regressions for complete Marrow source-visual discovery."""
from marrow_images import questions
from marrow_visual_inventory import source_visual_expectations


def roles(qid):
    q=questions()[qid]
    return [(v['role'],v['visualId'],tuple(v['sourcePages'])) for v in source_visual_expectations(q)]


def require(qid, role, minimum=1):
    rows=roles(qid)
    count=sum(r[0]==role for r in rows)
    assert count>=minimum, f'{qid}: expected >= {minimum} {role} visuals, found {rows}'


def main():
    # User-reported omissions: these visual declarations are already source-owned
    # and must never disappear from image discovery again.
    require('marrow__BIOCHEM_CH18_Q003','explanation')
    require('marrow__BIOCHEM_CH18_Q005','explanation')
    require('marrow__BIOCHEM_CH18_Q006','explanation')
    require('marrow__BIOCHEM_CH19_Q002','question')
    require('marrow__BIOCHEM_CH19_Q011','question')
    require('marrow__BIOCHEM_CH19_Q011','explanation')

    # Synthetic coverage protects both canonical snake_case question visuals and
    # visual blocks even if future normalization changes field casing.
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
    print('MARROW_IMAGE_SOURCE_COVERAGE_REGRESSION_OK real=6 synthetic=2')

if __name__=='__main__':main()
