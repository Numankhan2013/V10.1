#!/usr/bin/env python3
"""Stage a bounded, deterministic cross-subject native-image review batch.

Candidates are never marked PASS by this script. Existing reviewed entries are
preserved, and repeated streams are staged only once.
"""
import argparse
import json
from marrow_images import DATA,ROOT,extract,write_json

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--per-subject',type=int,default=6)
    args=parser.parse_args();assert 1<=args.per_subject<=10
    audit=json.loads((ROOT/'build/marrow-images/audit.json').read_text())
    registry=DATA/'images/registry.json';value=json.loads(registry.read_text())
    known={a['original']['sha256'] for a in value['assets']}
    for subject in ('Anatomy','Biochemistry','Physiology'):
        seen=set();count=0
        for binding in audit['bindings']:
            if binding['subject']!=subject:continue
            candidates=binding.get('candidateImages',[])
            if len(candidates)!=1:continue
            c=candidates[0];digest=c['streamSha256']
            if c['mask'] or c['filter'] not in ('/DCTDecode',"['/DCTDecode']") or digest in seen:continue
            seen.add(digest);count+=1
            if digest not in known:
                extract(subject,c['page'],c['xref'],DATA/'images/originals')
                f=binding['metadata'];role=f.get('role')
                if role not in ('question','explanation'):role='explanation'
                record={'path':'data/marrow/images/originals/'+digest+'.jpg','sha256':digest,
                        'width':c['width'],'height':c['height']}
                value['assets'].append({'id':subject.lower()+'-'+digest[:16],'subject':subject,'kind':'unknown',
                    'source':{'file':audit['sources'][subject]['file'],'sha256':audit['sources'][subject]['sha256'],
                              'page':c['page'],'xref':c['xref'],'region':c['region']},
                    'bindings':[{'questionId':binding['questionId'],'role':role,'order':1,'alt':'Source figure'}],
                    'original':record,'production':record,'method':'native-jpeg-stream','status':'REVIEW_REQUIRED',
                    'qa':{'sourceCompared':False,'notes':'Candidate: '+str(f.get('title') or f.get('description') or '')+'. Verify role, ownership, overlays, classification and readability.'}})
                known.add(digest)
            if count>=args.per_subject:break
    write_json(registry,value)
    print('STAGED_REVIEW_ASSETS',len(value['assets']))

if __name__=='__main__':main()
