#!/usr/bin/env python3
"""Integrate user-supplied Marrow ED8 Biochemistry Ch27-28 without explanation enhancement."""
from __future__ import annotations
import base64, hashlib, json, zlib
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'/'marrow'
OLD_PREFIX='biochemistry_phase_a'
NEW_PREFIX='biochemistry_ch001_028'
PART_SIZE=60000
SOURCE_TRANSPORT={
 27:('qbank_biochem_chunk_027_regulation_of_gene_expression.jsonl.zlib.b64',36947,'d4d4b5e6b89bd97050d907818603aa2f3099428cfd2eae71d3a98596cfb7c349',12,'Regulation of gene expression','genetics:05'),
 28:('qbank_biochem_chunk_028_molecular_genetics_recombinant_dna_genomic_technologies.jsonl.zlib.b64',76031,'f7f1d24434cb072bb3e849d960fda3f654aae66a148475c5b0f322cd08c74027',27,'Molecular genetics, recombinant DNA & genomic technologies','genetics:06'),
}
SRC_DIR=DATA/'automation_ingest'/'biochemistry'

def load_bundle(prefix):
 m=json.loads((DATA/f'{prefix}_manifest.json').read_text(encoding='utf-8'))
 parts=sorted(DATA.glob(f'{prefix}.zlib.b64.part*'))
 assert len(parts)==int(m['parts']),(prefix,len(parts),m['parts'])
 encoded=''.join(p.read_text(encoding='utf-8').strip() for p in parts)
 assert len(encoded)==int(m['base64_chars'])
 comp=base64.b64decode(encoded,validate=True)
 assert len(comp)==int(m['compressed_bytes'])
 assert hashlib.sha256(comp).hexdigest()==m['compressed_sha256']
 raw=zlib.decompress(comp)
 assert len(raw)==int(m['raw_bytes'])
 assert hashlib.sha256(raw).hexdigest()==m['raw_sha256']
 return json.loads(raw.decode('utf-8')),m

def read_source(ch):
 name,nbytes,sha,count,title,_=SOURCE_TRANSPORT[ch]
 encoded=(SRC_DIR/name).read_text(encoding='utf-8').strip()
 raw=zlib.decompress(base64.b64decode(encoded,validate=True))
 assert len(raw)==nbytes,(ch,len(raw),nbytes)
 assert hashlib.sha256(raw).hexdigest()==sha,(ch,hashlib.sha256(raw).hexdigest(),sha)
 rows=[json.loads(line) for line in raw.decode('utf-8').splitlines() if line.strip()]
 assert len(rows)==count
 ids=[]; qnums=[]; titles=set()
 for r in rows:
  assert r.get('subject')=='Biochemistry'
  assert int(r.get('chapter_number',0))==ch
  assert str(r.get('question_text','')).strip()
  assert len(r.get('options',[]))==4
  assert [str(x.get('label','')).lower() for x in r['options']]==['a','b','c','d']
  assert str(r.get('correct_option','')).lower() in 'abcd'
  ids.append(str(r.get('question_id','')));qnums.append(int(r.get('question_number',0)));titles.add(str(r.get('chapter','')).strip())
 assert len(ids)==len(set(ids))==count and all(ids)
 assert qnums==list(range(1,count+1)),qnums
 assert titles=={title},(titles,title)
 return rows

def adapt(r):
 ans=str(r['correct_option']).lower(); correct='abcd'.index(ans)+1
 options=[{'letter':str(o.get('label','')).strip().upper(),'text':str(o.get('text',''))} for o in r['options']]
 exp=r.get('explanation') or {}
 structured={'text':str(exp.get('text','')),'blocks':exp.get('blocks',[]),'tables':exp.get('tables',[]),'figures':exp.get('figures',[])}
 src=r.get('source') or {}; pages=src.get('question_pages') or []
 qfig=[f for f in structured['figures'] if str(f.get('role','')).lower()=='question']
 return {
  'id':'marrow__'+str(r['question_id']),'sourceQuestionId':str(r['question_id']),'subject':'Biochemistry','bank':'Marrow',
  'chapter':str(r['chapter']),'chapterId':str(r['chapter_number']),'questionNumber':int(r['question_number']),
  'questionType':str(r.get('question_type') or 'single_best_answer'),'question':str(r['question_text']),'options':options,
  'correctOption':correct,'correctAnswerText':str(r.get('correct_answer_text') or options[correct-1]['text']),
  'explanation':structured['text'],'structuredExplanation':structured,'sourcePage':min(pages) if pages else None,
  'provenance':src,'sourceFidelity':r.get('source_fidelity',{}),'reviewStatus':str(r.get('review_status','')),
  'imageDependent':bool(qfig),
 }

def replace(path,old,new,count=None,optional=False):
 text=path.read_text(encoding='utf-8'); n=text.count(old)
 if optional and n==0:return False
 if count is not None and n!=count: raise AssertionError(f'{path}: expected {count} x {old!r}, got {n}')
 if n==0: raise AssertionError(f'{path}: missing anchor {old!r}')
 path.write_text(text.replace(old,new),encoding='utf-8');return True

def write_bundle(record,old_manifest,rows):
 raw=json.dumps(record,ensure_ascii=False,separators=(',',':')).encode('utf-8');comp=zlib.compress(raw,9);enc=base64.b64encode(comp).decode('ascii')
 parts=[enc[i:i+PART_SIZE] for i in range(0,len(enc),PART_SIZE)]
 for p in DATA.glob(f'{NEW_PREFIX}.zlib.b64.part*'):p.unlink()
 for i,p in enumerate(parts):(DATA/f'{NEW_PREFIX}.zlib.b64.part{i:02d}').write_text(p+'\n',encoding='utf-8')
 rc=Counter(old_manifest.get('review_status_counts',{}))
 for rs in rows.values():rc.update(str(r.get('review_status','')) for r in rs)
 manifest=dict(old_manifest);manifest.update({
  'scope':'complete_ch001_028','chapters':list(range(1,29)),'topics':28,'questions':582,'parts':len(parts),'part_size':PART_SIZE,
  'base64_chars':len(enc),'raw_bytes':len(raw),'compressed_bytes':len(comp),'raw_sha256':hashlib.sha256(raw).hexdigest(),
  'compressed_sha256':hashlib.sha256(comp).hexdigest(),'source_archive':'Marrow ED8 Biochemistry canonical JSONL Ch01-Ch28',
  'source_files':list(old_manifest.get('source_files',[]))+[SOURCE_TRANSPORT[27][0].replace('.zlib.b64',''),SOURCE_TRANSPORT[28][0].replace('.zlib.b64','')],
  'review_status_counts':dict(sorted(rc.items())),'user_supplied_ch27_sha256':SOURCE_TRANSPORT[27][2],'user_supplied_ch28_sha256':SOURCE_TRANSPORT[28][2],
 })
 (DATA/f'{NEW_PREFIX}_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def update_taxonomy(titles):
 p=DATA/'topic_index_taxonomy.json';tax=json.loads(p.read_text(encoding='utf-8'));bio=tax['subjects']['Biochemistry']
 assert [str(x['id']) for x in bio['topics']]==[str(i) for i in range(1,27)]
 slots={x['slot'] for s in bio['plannedIndex'] for x in s['topics']}
 for ch in (27,28):
  slot=SOURCE_TRANSPORT[ch][5];assert slot in slots
  bio['topics'].append({'id':str(ch),'title':titles[ch],'section':'Genetics','plannedSlots':[slot]})
 p.write_text(json.dumps(tax,ensure_ascii=False,separators=(',',':'))+'\n',encoding='utf-8')

def update_runtime_tests():
 p=ROOT/'tools'/'apply_marrow_bank_pilot.py'
 replace(p,'load_expanded_bank("biochemistry_phase_a","Biochemistry")',f'load_expanded_bank("{NEW_PREFIX}","Biochemistry")',1)
 replace(p,'if len(expanded_ids)!=2455 or len(expanded_ids)!=len(set(expanded_ids)):','if len(expanded_ids)!=2494 or len(expanded_ids)!=len(set(expanded_ids)):',1)

 p=ROOT/'tools'/'test_marrow_bank_pilot.py'
 replace(p,"load_expanded('biochemistry_phase_a')",f"load_expanded('{NEW_PREFIX}')",1)
 replace(p,"full_biochem_manifest['scope']=='phase_a_ch001_026' and len(fb_q)==543 and len(fb_t)==26","full_biochem_manifest['scope']=='complete_ch001_028' and len(fb_q)==582 and len(fb_t)==28",1)
 replace(p,"len(all_expanded)==2455 and len({q['id'] for q in all_expanded})==2455","len(all_expanded)==2494 and len({q['id'] for q in all_expanded})==2494",1)
 replace(p,"'marrow__BIOCHEM_CH26_Q022'","'marrow__BIOCHEM_CH26_Q022','marrow__BIOCHEM_CH27_Q012','marrow__BIOCHEM_CH28_Q027'",1)
 replace(p,'anatomy=898/52 biochemistry=543/26 physiology=1014/43 total=2455','anatomy=898/52 biochemistry=582/28 physiology=1014/43 total=2494')

 p=ROOT/'tools'/'inventory_marrow_explanations.py'
 replace(p,'"Biochemistry": "biochemistry_phase_a"',f'"Biochemistry": "{NEW_PREFIX}"',1)
 replace(p,'== 2455','== 2494');replace(p,'2455 - enhanced','2494 - enhanced');replace(p,'pending={2455-enhanced}','pending={2494-enhanced}')

 p=ROOT/'tools'/'test_marrow_explanation_inventory.py'
 replace(p,'== 2455','== 2494');replace(p,'{"Anatomy": 898, "Biochemistry": 543, "Physiology": 1014}','{"Anatomy": 898, "Biochemistry": 582, "Physiology": 1014}',1)
 replace(p,'2455 - enhanced','2494 - enhanced');replace(p,'questions=2455','questions=2494');replace(p,'pending={2455-enhanced}','pending={2494-enhanced}')

 p=ROOT/'tools'/'test_marrow_biochem_explanation_rollout.py'
 if p.exists():
  replace(p,'"pending": 2271','"pending": 2310',optional=True);replace(p,'pending=2271','pending=2310',optional=True)
  replace(p,'questions=2455','questions=2494',optional=True)

 p=ROOT/'tools'/'marrow_images.py'
 if p.exists():replace(p,"'Biochemistry': ('biochemistry_phase_a', 'biochemistryed8.pdf')",f"'Biochemistry': ('{NEW_PREFIX}', 'biochemistryed8.pdf')",optional=True)
 p=ROOT/'tools'/'test_marrow_images.py'
 if p.exists():replace(p,'assert len(questions())==2455','assert len(questions())==2494',optional=True)

def update_taxonomy_test():
 p=ROOT/'tools'/'test_marrow_topic_taxonomy.py';text=p.read_text(encoding='utf-8')
 pairs={
  '"Biochemistry": "biochemistry_phase_a"':f'"Biochemistry": "{NEW_PREFIX}"',
  'assert flatten_current(biochem) == [str(i) for i in range(1, 27)]':'assert flatten_current(biochem) == [str(i) for i in range(1, 29)]',
  'assert total == 121':'assert total == 123','current_topics=121':'current_topics=123','biochemistry_visible=26':'biochemistry_visible=28',
 }
 for old,new in pairs.items():
  n=text.count(old)
  if n!=1:raise AssertionError(f'taxonomy anchor {old!r}: {n}')
  text=text.replace(old,new,1)
 anchor='    assert flatten_current(biochem) == [str(i) for i in range(1, 29)]\n'
 extra='''    assert {str(item["id"]): item["plannedSlots"] for item in biochem["topics"] if int(item["id"]) >= 27} == {\n        "27": ["genetics:05"],\n        "28": ["genetics:06"],\n    }\n'''
 assert text.count(anchor)==1;text=text.replace(anchor,anchor+extra,1);p.write_text(text,encoding='utf-8')

def update_browser():
 p=ROOT/'tools'/'verify_marrow_bank_browser.py';text=p.read_text(encoding='utf-8')
 insert='''\n# Biochemistry Ch27-28 source expansion: keep the core smoke suite and extend it.\nbiochem_replacements = {\n    "            for marker in ('PrepLadder','Marrow','543'):": "            for marker in ('PrepLadder','Marrow','582'):",\n    "            if page.locator('button.nk-topic-row').count()!=26: raise SystemExit('Marrow Biochemistry topic count is not 26')": "            if page.locator('button.nk-topic-row').count()!=28: raise SystemExit('Marrow Biochemistry topic count is not 28')",\n    "            if bnums!=list(range(1,27)): raise SystemExit(f'Marrow Biochemistry learner numbering is not contiguous 1-26: {bnums!r}')": "            if bnums!=list(range(1,29)): raise SystemExit(f'Marrow Biochemistry learner numbering is not contiguous 1-28: {bnums!r}')",\n}\nfor old, new in biochem_replacements.items():\n    if source.count(old) != 1:\n        raise SystemExit(f"Biochemistry browser source-count/numbering anchor count for {old!r}: {source.count(old)}")\n    source = source.replace(old, new, 1)\n\nbiochem_anchor = "            page.locator('button.nk-topic-row').filter(has_text='Chemistry of Carbohydrates, Amino sugars and Mucopolysaccharides').click();page.wait_for_timeout(80)"\nbiochem_guard = '''            # Newly supplied Ch27-28 must behave like ordinary learner questions, including the red+green contract.\n            page.locator('button.nk-topic-row').filter(has_text='Regulation of gene expression').click();page.wait_for_timeout(80)\n            if page.locator('button.nk-library-row').count()!=12: raise SystemExit('Marrow Biochemistry Ch27 count is not 12')\n            page.locator('button.nk-library-row').first.click();page.wait_for_timeout(80)\n            if 'housekeeping genes' not in page.locator('.question-text').inner_text().lower(): raise SystemExit('Biochemistry Ch27 Q1 did not render')\n            learner_text=page.locator('body').inner_text()\n            for raw_marker in ('question_id','chapter_number','correct_option','schema_version','review_status','source_fidelity'):\n                if raw_marker in learner_text: raise SystemExit(f'Raw Biochemistry JSON key leaked into learner view: {raw_marker}')\n            page.locator('.option-list button').nth(0).click();page.wait_for_timeout(120)\n            if page.locator('.option-list .option.wrong').count()!=1 or page.locator('.option-list .option.correct').count()!=1:\n                raise SystemExit('New Biochemistry wrong answer must show exactly one red wrong and one green correct option')\n            green=page.locator('.option-list .option.correct .option-letter').evaluate("el=>getComputedStyle(el).backgroundColor")\n            red=page.locator('.option-list .option.wrong .option-letter').evaluate("el=>getComputedStyle(el).backgroundColor")\n            if green!='rgb(16, 154, 99)' or red!='rgb(201, 75, 87)': raise SystemExit(f'New Biochemistry answer colors regressed: correct={green} wrong={red}')\n            page.evaluate("window.QB.nav('banks','Biochemistry')");page.wait_for_timeout(80)\n            page.locator('button.nk-bank-card').filter(has_text='Marrow').click();page.wait_for_timeout(80)\n            page.locator('button.nk-topic-row').filter(has_text='Molecular genetics, recombinant DNA & genomic technologies').click();page.wait_for_timeout(80)\n            if page.locator('button.nk-library-row').count()!=27: raise SystemExit('Marrow Biochemistry Ch28 count is not 27')\n            page.locator('button.nk-library-row').first.click();page.wait_for_timeout(80)\n            if 'enzymes that cut dna' not in page.locator('.question-text').inner_text().lower(): raise SystemExit('Biochemistry Ch28 Q1 did not render')\n            page.locator('.option-list button').nth(0).click();page.wait_for_timeout(120)\n            if page.locator('.option-list .option.wrong').count()!=1 or page.locator('.option-list .option.correct').count()!=1: raise SystemExit('Biochemistry Ch28 red+green contract failed')\n            page.evaluate("window.QB.nav('banks','Biochemistry')");page.wait_for_timeout(80)\n            page.locator('button.nk-bank-card').filter(has_text='Marrow').click();page.wait_for_timeout(80)\n'''\nif source.count(biochem_anchor)!=1: raise SystemExit(f'Biochemistry browser insertion anchor count: {source.count(biochem_anchor)}')\nsource=source.replace(biochem_anchor,biochem_guard+biochem_anchor,1)\nsource=source.replace('biochemistry=543/26 physiology=1014/43 physiology_plan=42 physiology_numbering=contiguous raw_json=clean total=2455','biochemistry=582/28 physiology=1014/43 physiology_plan=42 physiology_numbering=contiguous raw_json=clean total=2494')\n'''
 exec_anchor='exec(\n    compile(source, str(CORE), "exec"),'
 if text.count(exec_anchor)!=1:raise AssertionError(f'browser exec anchor {text.count(exec_anchor)}')
 text=text.replace(exec_anchor,insert+'\n'+exec_anchor,1);p.write_text(text,encoding='utf-8')

def main():
 old,oldm=load_bundle(OLD_PREFIX);assert old['subject']=='Biochemistry' and old['bank']=='Marrow';assert len(old['topics'])==26 and len(old['questions'])==543
 rows={ch:read_source(ch) for ch in (27,28)};assert sum(map(len,rows.values()))==39
 topics=list(old['topics']);questions=list(old['questions']);old_ids={q['id'] for q in questions}
 titles={ch:rows[ch][0]['chapter'] for ch in rows}
 for ch in (27,28):
  pages=[p for r in rows[ch] for p in ((r.get('source') or {}).get('question_pages') or [])]
  topics.append({'id':str(ch),'title':titles[ch],'subject':'Biochemistry','bank':'Marrow','questionCount':len(rows[ch]),'startPage':min(pages) if pages else None})
  questions.extend(adapt(r) for r in rows[ch])
 ids=[q['id'] for q in questions];assert len(topics)==28 and len(questions)==582 and len(ids)==len(set(ids))==582 and old_ids.issubset(set(ids))
 assert all([o['letter'] for o in q['options']]==['A','B','C','D'] for q in questions)
 record=dict(old);record['scope']='complete_ch001_028';record['topics']=topics;record['questions']=questions
 write_bundle(record,oldm,rows);update_taxonomy(titles);update_runtime_tests();update_taxonomy_test();update_browser()
 print('BIOCHEM_AUTOMATION_INGEST_OK chapters=27-28 new_questions=39 biochemistry=582/28 global=2494/123 explanations_unchanged=true')
if __name__=='__main__':main()
