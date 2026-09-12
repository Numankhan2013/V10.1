#!/usr/bin/env python3
"""Batch planning and PDF evidence for supervised Marrow image fast lanes.

Proposal-only: never mutates registry, coverage, progress, raw data, or assets.
Human review still owns A/B/C/D decisions and PASS status.
"""
from __future__ import annotations
import argparse, hashlib, html, json, subprocess
from pathlib import Path
from marrow_images import DATA, ROOT, SOURCES, questions

AUDIT=ROOT/'build/marrow-images/audit.json'
COVERAGE=DATA/'images/coverage.json'
REGISTRY=DATA/'images/registry.json'
PROGRESS=DATA/'images/progress.json'
RESOLVED={'RELEASED','SOURCE_METADATA_INVALID'}
LANES={'A','B','C','D'}

def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def clean_native(candidate):
    return (not candidate.get('mask')
            and candidate.get('filter') in {'/DCTDecode',"['/DCTDecode']"}
            and isinstance(candidate.get('xref'),int))

def existing_matches(candidates,registry,subject):
    by_hash={}
    for asset in registry.get('assets',[]):
        if asset.get('subject')!=subject: continue
        hashes={(asset.get('original') or {}).get('sha256'),(asset.get('production') or {}).get('sha256')}-{None}
        for value in hashes: by_hash.setdefault(value,[]).append(asset)
    rows=[];seen=set()
    for candidate in candidates:
        for asset in by_hash.get(candidate.get('streamSha256'),[]):
            key=(candidate.get('streamSha256'),asset.get('id'))
            if key in seen: continue
            seen.add(key)
            rows.append({'streamSha256':key[0],'assetId':key[1],'assetStatus':asset.get('status'),
                'existingBindings':[{'questionId':b.get('questionId'),'role':b.get('role'),'order':b.get('order'),
                  'status':b.get('status',asset.get('status'))} for b in asset.get('bindings',[])]})
    return rows

def lane_hint(candidates,matches):
    if len({row['assetId'] for row in matches})==1: return 'B'
    if len(candidates)==1 and clean_native(candidates[0]): return 'C'
    return 'D'

def git_head():
    return subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()

def build_plan(subject,count,batch_id,base_sha,audit,coverage,registry,question_map,
               registry_path=REGISTRY,progress_path=PROGRESS,coverage_path=COVERAGE):
    if not 25<=count<=40: raise ValueError('supervised fast-lane count must be between 25 and 40')
    audit_by_id={row['id']:row for row in audit.get('bindings',[])}
    unresolved=[row for row in coverage.get('sourceVisuals',[])
                if row.get('subject')==subject and row.get('coverageStatus') not in RESOLVED][:count]
    entries=[]
    for position,coverage_row in enumerate(unresolved,1):
        source_row=audit_by_id[coverage_row['id']]
        candidates=source_row.get('candidateImages',[])
        matches=existing_matches(candidates,registry,subject)
        question=question_map[source_row['questionId']]
        entries.append({'position':position,'sourceReferenceId':source_row['id'],
          'questionId':source_row['questionId'],'coverageStatusBefore':coverage_row.get('coverageStatus'),
          'role':coverage_row.get('role'),'order':coverage_row.get('order'),
          'sourcePages':coverage_row.get('sourcePages',[]),'metadata':source_row.get('metadata',{}),
          'question':question.get('question',''),'explanation':question.get('explanation',''),
          'structuredTables':(question.get('structuredExplanation') or {}).get('tables',[]),
          'candidateImages':candidates,'existingAssetMatches':matches,
          'laneHint':lane_hint(candidates,matches),'decision':None,
          'review':{'sourcePageInspected':False,'questionOwnershipChecked':False,
            'roleOrderChecked':False,'answerSafetyChecked':False,'evidence':'','notes':''}})
    source=audit['sources'][subject]
    return {'schemaVersion':1,'kind':'MARROW_IMAGE_FAST_LANE_PLAN','batchId':batch_id,
      'subject':subject,'canonicalBaseSha':base_sha,'requestedReferenceCount':count,
      'auditedReferenceCount':len(entries),'source':{'file':source['file'],'sha256':source['sha256']},
      'inputFingerprints':{'registrySha256':digest(registry_path),'progressSha256':digest(progress_path),
                           'coverageSha256':digest(coverage_path)},
      'laneHintCounts':{lane:sum(row['laneHint']==lane for row in entries) for lane in ('B','C','D')},
      'uniqueSourcePages':sorted({p for row in entries for p in row['sourcePages']}),'entries':entries}

def validate_reviewed_plan(plan):
    assert plan.get('schemaVersion')==1 and plan.get('kind')=='MARROW_IMAGE_FAST_LANE_PLAN'
    assert plan.get('subject') in SOURCES and 25<=plan.get('requestedReferenceCount',0)<=40
    entries=plan.get('entries',[])
    assert len(entries)==plan.get('auditedReferenceCount')
    assert [r.get('position') for r in entries]==list(range(1,len(entries)+1))
    seen=set()
    for row in entries:
        ref=row.get('sourceReferenceId');assert ref and ref not in seen;seen.add(ref)
        decision=row.get('decision');assert decision in LANES,f'Unreviewed fast-lane decision: {ref}'
        review=row.get('review') or {}
        for key in ('sourcePageInspected','questionOwnershipChecked','roleOrderChecked','answerSafetyChecked'):
            assert review.get(key) is True,f'{ref}: missing {key}'
        assert review.get('evidence') and review.get('notes')
        if decision=='A': assert row.get('adjudication',{}).get('reason')
        elif decision=='B':
            assert row.get('reuse',{}).get('assetId') in {m['assetId'] for m in row.get('existingAssetMatches',[])}
        elif decision=='C':
            assert row.get('extraction',{}).get('method') in {'native-jpeg-stream','region-render'}
        else:
            assert row.get('defer',{}).get('status')=='REVIEW_REQUIRED' and row['defer'].get('reason')

def render_evidence(plan,output,page_dpi,crop_dpi):
    from verification_preflight import is_termux
    if is_termux(): raise SystemExit('Fast-lane PDF evidence rendering requires Ubuntu CI.')
    import fitz
    subject=plan['subject'];pdf_path=DATA/'source_pdfs'/SOURCES[subject][1]
    assert digest(pdf_path)==plan['source']['sha256']
    pages_dir=output/'pages';crops_dir=output/'reference-regions'
    pages_dir.mkdir(parents=True,exist_ok=True);crops_dir.mkdir(parents=True,exist_ok=True)
    evidence=[]
    with fitz.open(pdf_path) as document:
        for number in plan['uniqueSourcePages']:
            page=document[number-1];assert page.rotation==0
            data=page.get_pixmap(matrix=fitz.Matrix(page_dpi/72,page_dpi/72),alpha=False).tobytes('png')
            (pages_dir/f'{subject.lower()}-page-{number:04d}.png').write_bytes(data)
        for row in plan['entries']:
            candidates=row.get('candidateImages',[]);crop_name=None;crop_sha=None
            if candidates and len({c['page'] for c in candidates})==1:
                number=candidates[0]['page'];page=document[number-1];regions=[c['region'] for c in candidates];margin=8
                rect=fitz.Rect(max(0,min(r[0] for r in regions)-margin),max(0,min(r[1] for r in regions)-margin),
                  min(page.rect.width,max(r[2] for r in regions)+margin),min(page.rect.height,max(r[3] for r in regions)+margin))
                data=page.get_pixmap(matrix=fitz.Matrix(crop_dpi/72,crop_dpi/72),clip=rect,alpha=False).tobytes('png')
                crop_name=f"{row['position']:02d}-{row['sourceReferenceId'].replace(':','_')}.png"
                (crops_dir/crop_name).write_bytes(data);crop_sha=hashlib.sha256(data).hexdigest()
            evidence.append({'position':row['position'],'sourceReferenceId':row['sourceReferenceId'],
              'pageFiles':[f"pages/{subject.lower()}-page-{p:04d}.png" for p in row['sourcePages']],
              'referenceRegionFile':f'reference-regions/{crop_name}' if crop_name else None,
              'referenceRegionSha256':crop_sha})
    blocks=[]
    for row,item in zip(plan['entries'],evidence):
        images=''.join(f'<img loading="lazy" src="{html.escape(p)}">' for p in item['pageFiles'])
        if item['referenceRegionFile']: images+=f'<img loading="lazy" src="{html.escape(item["referenceRegionFile"])}">'
        blocks.append(f'<article><h2>{row["position"]}. {html.escape(row["sourceReferenceId"])}</h2>'
          f'<p><b>Hint:</b> {row["laneHint"]} · <b>Role/order:</b> {row["role"]}/{row["order"]}</p>'
          f'<p><b>Question:</b> {html.escape(row["question"])}</p><details><summary>Explanation and metadata</summary>'
          f'<pre>{html.escape(row["explanation"])}\n\n{html.escape(json.dumps(row["metadata"],indent=2))}</pre></details>{images}</article>')
    (output/'index.html').write_text('<!doctype html><meta charset=utf-8><title>Marrow fast lane</title>'
      '<style>body{font:16px system-ui;max-width:1200px;margin:auto;padding:24px}article{border-top:2px solid #333;padding:20px 0}'
      'img{max-width:48%;vertical-align:top;margin:8px}pre{white-space:pre-wrap}</style>'+''.join(blocks))
    (output/'plan.json').write_text(json.dumps(plan,ensure_ascii=False,indent=2)+'\n')
    (output/'evidence.json').write_text(json.dumps({'schemaVersion':1,'batchId':plan['batchId'],
      'subject':subject,'source':plan['source'],'pageDpi':page_dpi,'referenceRegionDpi':crop_dpi,'entries':evidence},indent=2)+'\n')
    print('MARROW_FAST_LANE_EVIDENCE_OK',len(plan['entries']),len(plan['uniqueSourcePages']))

def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('plan');p.add_argument('--subject',choices=SOURCES,required=True);p.add_argument('--count',type=int,default=35)
    p.add_argument('--batch-id',required=True);p.add_argument('--base-sha');p.add_argument('--audit',type=Path,default=AUDIT)
    p.add_argument('--coverage',type=Path,default=COVERAGE);p.add_argument('--registry',type=Path,default=REGISTRY);p.add_argument('--output',type=Path,required=True)
    r=sub.add_parser('render');r.add_argument('--plan',type=Path,required=True);r.add_argument('--output',type=Path,required=True)
    r.add_argument('--page-dpi',type=int,default=144);r.add_argument('--crop-dpi',type=int,default=240)
    v=sub.add_parser('validate-reviewed');v.add_argument('--plan',type=Path,required=True);args=parser.parse_args()
    if args.command=='plan':
        for path in (args.audit,args.coverage,args.registry,PROGRESS):
            if not path.exists(): raise SystemExit(f'Required fast-lane input missing: {path}')
        value=build_plan(args.subject,args.count,args.batch_id,args.base_sha or git_head(),
          json.loads(args.audit.read_text()),json.loads(args.coverage.read_text()),
          json.loads(args.registry.read_text()),questions(),args.registry,PROGRESS,args.coverage)
        args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
        print('MARROW_FAST_LANE_PLAN_OK',value['auditedReferenceCount'],json.dumps(value['laneHintCounts'],sort_keys=True))
    elif args.command=='render':
        if not 96<=args.page_dpi<=300 or not 144<=args.crop_dpi<=400: raise SystemExit('Unsafe evidence DPI')
        render_evidence(json.loads(args.plan.read_text()),args.output,args.page_dpi,args.crop_dpi)
    else:
        validate_reviewed_plan(json.loads(args.plan.read_text()));print('MARROW_FAST_LANE_REVIEW_OK')

if __name__=='__main__': main()
