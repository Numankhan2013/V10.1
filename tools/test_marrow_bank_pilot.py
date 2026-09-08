#!/usr/bin/env python3
"""Regression checks for the isolated Marrow bank pilot."""
from __future__ import annotations
import argparse, base64, hashlib, json, re, subprocess, tempfile, zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/'app/src/main/assets/index.html'
DATA=ROOT/'data/marrow'

def load_data(prefix):
    m=json.loads((DATA/f'{prefix}_pilot_manifest.json').read_text())
    parts=sorted(DATA.glob(f'{prefix}_pilot.zlib.b64.part*'))
    assert len(parts)==m['parts'],(prefix,len(parts),m['parts'])
    b64=''.join(p.read_text().strip() for p in parts)
    assert len(b64)==m['base64_chars']
    comp=base64.b64decode(b64,validate=True)
    if 'compressed_bytes' in m: assert len(comp)==m['compressed_bytes']
    assert hashlib.sha256(comp).hexdigest()==m['compressed_sha256']
    raw=zlib.decompress(comp)
    if 'raw_bytes' in m: assert len(raw)==m['raw_bytes']
    assert hashlib.sha256(raw).hexdigest()==m['raw_sha256']
    return json.loads(raw),m

def load_phys_explanations():
    m=json.loads((DATA/'explanation_physio_pilot_manifest.json').read_text())
    parts=sorted(DATA.glob('explanation_physio_pilot.zlib.b64.part*'))
    assert len(parts)==m['parts'],(len(parts),m['parts'])
    b64=''.join(p.read_text().strip() for p in parts)
    assert len(b64)==m['base64_chars']
    comp=base64.b64decode(b64,validate=True)
    assert len(comp)==m['compressed_bytes']
    assert hashlib.sha256(comp).hexdigest()==m['compressed_sha256']
    raw=zlib.decompress(comp)
    assert len(raw)==m['raw_bytes']
    assert hashlib.sha256(raw).hexdigest()==m['raw_sha256']
    return json.loads(raw),m

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data-only',action='store_true');args=ap.parse_args()
    d,anatomy_manifest=load_data('anatomy');qs=d['questions'];topics=d['topics']
    phys,phys_manifest=load_data('physiology');pqs=phys['questions'];ptopics=phys['topics']
    gold=json.loads((DATA/'explanation_gold_pilot.json').read_text(encoding='utf-8'))
    phys_gold,phys_gold_manifest=load_phys_explanations()
    assert len(qs)==62 and len(topics)==4
    assert len({q['id'] for q in qs})==62 and all(q['id'].startswith('marrow__') for q in qs)
    assert [t['questionCount'] for t in topics]==[19,13,16,14]
    assert all(len(q['options'])==4 and q['correctOption'] in (1,2,3,4) for q in qs)
    assert not any(q.get('reviewStatus')=='needs_manual_review' for q in qs)
    assert phys['subject']=='Physiology' and phys['bank']=='Marrow'
    assert phys_manifest['scope']=='pilot_chapters_001_004'
    assert len(pqs)==80 and len(ptopics)==4
    assert [t['questionCount'] for t in ptopics]==[21,21,24,14]
    assert len({q['id'] for q in pqs})==80 and all(q['id'].startswith('marrow__PHYS_') for q in pqs)
    assert all(len(q['options'])==4 and q['correctOption'] in (1,2,3,4) for q in pqs)
    assert len({q['id'] for q in qs+pqs})==142
    repaired={q['sourceQuestionId']:q for q in qs if q.get('reviewStatus')=='resolved_reconstruction'}
    assert set(repaired)=={'ANAT_CH02_Q010','ANAT_CH03_Q004','ANAT_CH04_Q013'}
    assert '1. Cavitation' in repaired['ANAT_CH02_Q010']['question'] and '4. Cleavage' in repaired['ANAT_CH02_Q010']['question']
    assert '3. Primitive pit (blastopore)' in repaired['ANAT_CH03_Q004']['question']
    assert '1. Dichorionic diamniotic monozygotic twins' in repaired['ANAT_CH04_Q013']['question']
    gold_q=gold.get('questions',{})
    assert len(gold_q)==62
    assert set(gold_q)=={q['id'] for q in qs}
    assert all(len(v.get('rationales',{}))==3 for v in gold_q.values())
    by_id={q['id']:q for q in qs}
    letters=('a','b','c','d')
    for qid,cfg in gold_q.items():
        correct=letters[by_id[qid]['correctOption']-1]
        assert set(cfg.get('rationales',{}))==set(letters)-{correct},qid
        assert all(len(str(x).strip())<=300 for x in cfg.get('rationales',{}).values()),qid
        assert 1<=len(cfg.get('emphasis',[]))<=4,qid
    assert all(v.get('emphasis') for v in gold_q.values())
    phys_gold_q=phys_gold.get('questions',{})
    assert phys_gold.get('scope',{}).get('subject')=='Physiology'
    assert phys_gold_manifest['questions']==80 and phys_gold_manifest['rationales']==240
    assert len(phys_gold_q)==80 and set(phys_gold_q)=={q['id'] for q in pqs}
    pby_id={q['id']:q for q in pqs}
    for qid,cfg in phys_gold_q.items():
        correct=letters[pby_id[qid]['correctOption']-1]
        assert set(cfg.get('rationales',{}))==set(letters)-{correct},qid
        assert all(1<=len(str(x).strip())<=320 for x in cfg.get('rationales',{}).values()),qid
        assert 1<=len(cfg.get('emphasis',[]))<=4,qid
        assert 20<=len(str(cfg.get('takeaway','')).strip())<=300,qid
        display=str(cfg.get('displayText','')).strip()
        assert len(display)>=20,qid
        lowered=display.lower()
        assert 'wok no' not in lowered and 'internalef' not in lowered and '\nmarrow' not in lowered,qid
    assert set(gold_q).isdisjoint(phys_gold_q)
    assert len(gold_q)+len(phys_gold_q)==142
    if args.data_only:
        print('MARROW_DATA_OK anatomy_questions=62 anatomy_topics=4 physiology_questions=80 physiology_topics=4 combined=142 repaired=3 enhanced=142 rationales=426');return
    s=HTML.read_text(encoding='utf-8')
    required=['NK_MARROW_BANK_PILOT_V1_START','nk-marrow-bank-pilot-v1','const MARROW_RECORDS = Array.isArray(MARROW_DATA.records) ? MARROW_DATA.records : [MARROW_DATA]','const MARROW_BY_SUBJECT = Object.freeze','const BANKS_BY_SUBJECT = Object.create(null)','Object.values(BANKS_BY_SUBJECT).flatMap','function nkBankRecords(name)','function openBank(name,bank)','function bankPage(name)',"route.page==='banks'",'Detailed explanation','Structured text','function nkRenderMarrowExplanation(q)',"q.bank==='Marrow'",'qbank_active_bank_v1','marrow__ANAT_CH01_Q001','marrow__PHYS_CH01_Q001','NK_MARROW_EXPLANATION_GOLD_V1','nk-marrow-explanation-gold-v1','Why the other options are wrong','function nkRenderMarrowExplanationBase(q)','function nkRenderGoldWrongOptions(q,cfg)','function nkGoldConciseText(text,q)','function nkGoldOverlap(a,b)','displayText','homeostatic control system']
    missing=[x for x in required if x not in s]
    assert not missing,missing
    assert 'const MARROW_RECORD =' not in s
    assert s.count('const BANKS_BY_SUBJECT = Object.create(null)')==1
    assert s.count('const MARROW_BY_SUBJECT = Object.freeze')==1
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
    print(f'MARROW_BANK_PILOT_TEST_OK anatomy=62/4 physiology=80/4 combined=142 enhanced=142 rationales=426 phys_clean=80 micro_concision=on fsrs_dock=preserved scripts={checked}')
if __name__=='__main__':main()
