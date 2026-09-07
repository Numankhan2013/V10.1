#!/usr/bin/env python3
"""Regression checks for the isolated Marrow bank pilot."""
from __future__ import annotations
import argparse, base64, hashlib, json, re, subprocess, tempfile, zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/'app/src/main/assets/index.html'
DATA=ROOT/'data/marrow'

def load_data():
    m=json.loads((DATA/'anatomy_pilot_manifest.json').read_text())
    parts=sorted(DATA.glob('anatomy_pilot.zlib.b64.part*'))
    assert len(parts)==m['parts'],(len(parts),m['parts'])
    b64=''.join(p.read_text().strip() for p in parts)
    assert len(b64)==m['base64_chars']
    comp=base64.b64decode(b64,validate=True)
    assert hashlib.sha256(comp).hexdigest()==m['compressed_sha256']
    raw=zlib.decompress(comp)
    assert hashlib.sha256(raw).hexdigest()==m['raw_sha256']
    return json.loads(raw)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data-only',action='store_true');args=ap.parse_args()
    d=load_data();qs=d['questions'];topics=d['topics']
    gold=json.loads((DATA/'explanation_gold_pilot.json').read_text(encoding='utf-8'))
    assert len(qs)==62 and len(topics)==4
    assert len({q['id'] for q in qs})==62 and all(q['id'].startswith('marrow__') for q in qs)
    assert [t['questionCount'] for t in topics]==[19,13,16,14]
    assert all(len(q['options'])==4 and q['correctOption'] in (1,2,3,4) for q in qs)
    assert not any(q.get('reviewStatus')=='needs_manual_review' for q in qs)
    repaired={q['sourceQuestionId']:q for q in qs if q.get('reviewStatus')=='resolved_reconstruction'}
    assert set(repaired)=={'ANAT_CH02_Q010','ANAT_CH03_Q004','ANAT_CH04_Q013'}
    assert '1. Cavitation' in repaired['ANAT_CH02_Q010']['question'] and '4. Cleavage' in repaired['ANAT_CH02_Q010']['question']
    assert '3. Primitive pit (blastopore)' in repaired['ANAT_CH03_Q004']['question']
    assert '1. Dichorionic diamniotic monozygotic twins' in repaired['ANAT_CH04_Q013']['question']
    gold_q=gold.get('questions',{})
    assert len(gold_q)==20
    assert set(gold_q).issubset({q['id'] for q in qs})
    assert all(len(v.get('rationales',{}))==3 for v in gold_q.values())
    assert all(v.get('emphasis') for v in gold_q.values())
    if args.data_only:
        print('MARROW_DATA_OK questions=62 topics=4 repaired=3 gold=20 rationales=60');return
    s=HTML.read_text(encoding='utf-8')
    required=['NK_MARROW_BANK_PILOT_V1_START','nk-marrow-bank-pilot-v1','function nkBankRecords(name)','function openBank(name,bank)','function bankPage(name)',"route.page==='banks'",'Detailed explanation','Structured text','function nkRenderMarrowExplanation(q)',"q.bank==='Marrow'",'qbank_active_bank_v1','marrow__ANAT_CH01_Q001','NK_MARROW_EXPLANATION_GOLD_V1','nk-marrow-explanation-gold-v1','Why the other options are wrong','function nkRenderMarrowExplanationBase(q)','function nkRenderGoldWrongOptions(q,cfg)']
    missing=[x for x in required if x not in s]
    assert not missing,missing
    assert 'const nkFsrsAllQuestions=()=>SUBJECTS.flatMap' in s
    assert 'return SUBJECTS.flatMap(record=>' in s
    assert 'BY_ID[s.questionIds[s.index]]||nkFsrsAllById()[s.questionIds[s.index]]' in s
    assert 'BY_ID[String(qid)]||nkFsrsAllById()[String(qid)]' in s
    assert s.count('id="nk-marrow-bank-pilot-v1"')==1
    assert s.count('id="nk-marrow-explanation-gold-v1"')==1
    assert s.count('NK_MARROW_EXPLANATION_GOLD_V1')>=1
    assert s.count('NK_FSRS_RECALL_DOCK_V2')==1
    assert '.nk-session-footer .nk-fsrs-rating' in s
    scripts=re.findall(r'<script(?:[^>]*)>(.*?)</script>',s,re.S|re.I)
    with tempfile.TemporaryDirectory() as td:
        checked=0
        for i,src in enumerate(scripts):
            if not src.strip():continue
            p=Path(td)/f'i{i}.js';p.write_text(src)
            subprocess.run(['node','--check',str(p)],check=True,stdout=subprocess.DEVNULL)
            checked+=1
    print(f'MARROW_BANK_PILOT_TEST_OK questions=62 topics=4 gold=20 rationales=60 fsrs_dock=preserved scripts={checked}')
if __name__=='__main__':main()
