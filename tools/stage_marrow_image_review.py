#!/usr/bin/env python3
"""Stage a bounded, deterministic native-image review batch.

Candidates are never marked PASS by this script. Existing reviewed entries are
preserved, and repeated streams are staged only once. Source-recorded visuals
from question-time metadata and structured explanation blocks are merged into
the legacy audit so they cannot be silently omitted.
"""
import argparse
import json
import re
from marrow_images import DATA,ROOT,extract,questions,write_json
from marrow_visual_inventory import enrich_audit_bindings

QUESTION_IMAGE_CUE=re.compile(r'(?:shown|seen|depicted).{0,48}(?:image|figure|diagram|graph)|(?:image|figure|diagram|graph).{0,48}(?:shown|given|below|above)',re.I|re.S)
SUBJECTS=('Anatomy','Biochemistry','Physiology')


def normalize_role(value,stem=''):
    role=str(value or '').strip().lower()
    if role.startswith('question'):return 'question'
    if role=='explanation':return 'explanation'
    return 'question' if QUESTION_IMAGE_CUE.search(stem or '') else 'explanation'


def binding_order(binding):
    if isinstance(binding.get('order'),int) and binding['order']>0:return binding['order']
    match=re.search(r':figure:(\d+)$',binding.get('id',''))
    return int(match.group(1)) if match else 1


def alt_text(metadata,role):
    if role=='question':return 'Source question figure'
    return str(metadata.get('title') or metadata.get('description') or 'Source explanation figure')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--per-subject',type=int,default=6)
    parser.add_argument('--batch-id',default='manual')
    parser.add_argument('--subject',choices=SUBJECTS,help='Stage only this subject; omit to preserve legacy all-subject behavior.')
    args=parser.parse_args();assert 1<=args.per_subject<=10
    audit=json.loads((ROOT/'build/marrow-images/audit.json').read_text())
    question_map=questions()
    bindings=enrich_audit_bindings(audit,question_map)
    registry=DATA/'images/registry.json';value=json.loads(registry.read_text())
    known={a['original']['sha256']:a for a in value['assets'] if a.get('original')}
    staged=[];deferred=[]
    subjects=(args.subject,) if args.subject else SUBJECTS
    for subject in subjects:
        seen=set();count=0
        for binding in bindings:
            if binding['subject']!=subject:continue
            candidates=binding.get('candidateImages',[])
            if len(candidates)!=1:
                deferred.append((subject,binding['questionId'],binding.get('id',''),len(candidates),'ambiguous-or-nonnative-source-visual'))
                continue
            c=candidates[0];digest=c['streamSha256']
            key=(digest,binding['questionId'],binding.get('role') or '')
            if c['mask'] or c['filter'] not in ('/DCTDecode',"['/DCTDecode']"):
                deferred.append((subject,binding['questionId'],binding.get('id',''),1,'masked-or-non-jpeg-candidate'))
                continue
            if key in seen:continue
            seen.add(key);f=binding.get('metadata') or {}
            role=normalize_role(binding.get('role') or f.get('role'),question_map[binding['questionId']]['question'])
            order=binding_order(binding)
            existing=known.get(digest)
            if existing:
                if any(b['questionId']==binding['questionId'] and b.get('role')==role for b in existing['bindings']):continue
                existing['bindings'].append({'questionId':binding['questionId'],'role':role,
                    'order':order,'alt':alt_text(f,role),'status':'REVIEW_REQUIRED','reviewBatch':args.batch_id,
                    'source':{'page':c['page'],'xref':c['xref'],'region':c['region']},
                    'qa':{'sourceCompared':False,'notes':'Verify this repeated-asset ownership, role and answer-safety against the cited source page.'}})
                staged.append((subject,binding['questionId'],existing['id'],'reuse-binding'));count+=1
            else:
                extract(subject,c['page'],c['xref'],DATA/'images/originals')
                record={'path':'data/marrow/images/originals/'+digest+'.jpg','sha256':digest,
                        'width':c['width'],'height':c['height']}
                existing={'id':subject.lower()+'-'+digest[:16],'subject':subject,'kind':'unknown','reviewBatch':args.batch_id,
                    'source':{'file':audit['sources'][subject]['file'],'sha256':audit['sources'][subject]['sha256'],
                              'page':c['page'],'xref':c['xref'],'region':c['region']},
                    'bindings':[{'questionId':binding['questionId'],'role':role,'order':order,'alt':alt_text(f,role),
                        'status':'REVIEW_REQUIRED','reviewBatch':args.batch_id,
                        'source':{'page':c['page'],'xref':c['xref'],'region':c['region']},
                        'qa':{'sourceCompared':False,'notes':'Verify this asset ownership, role and answer-safety against the cited source page.'}}],
                    'original':record,'production':record,'method':'native-jpeg-stream','status':'REVIEW_REQUIRED',
                    'qa':{'sourceCompared':False,'notes':'Candidate: '+str(f.get('title') or f.get('description') or '')+'. Verify role, ownership, overlays, classification and readability.'}}
                value['assets'].append(existing);known[digest]=existing
                staged.append((subject,binding['questionId'],existing['id'],'new-asset'));count+=1
            if count>=args.per_subject:break
    write_json(registry,value)
    print('SOURCE_RECORDED_BINDINGS',sum(bool(b.get('sourceRecorded')) for b in bindings),'AUDIT_BINDINGS',len(bindings))
    print('STAGED_REVIEW_ITEMS',len(staged),'TOTAL_ASSETS',len(value['assets']),'DEFERRED_REVIEW_ITEMS',len(deferred))
    for row in staged:print(*row)
    for row in deferred[:50]:print('DEFERRED',*row)

if __name__=='__main__':main()
