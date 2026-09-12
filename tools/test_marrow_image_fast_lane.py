#!/usr/bin/env python3
"""Deterministic contracts for the supervised image fast-lane planner."""
import tempfile
from pathlib import Path
from marrow_image_fast_lane import build_plan, clean_native, validate_reviewed_plan

def main():
    candidate={'xref':8,'filter':'/DCTDecode','mask':False,'streamSha256':'a'*64}
    assert clean_native(candidate) and not clean_native({**candidate,'mask':True})
    audit={'sources':{'Physiology':{'file':'physiologyed8.pdf','sha256':'f'*64}},'bindings':[
      {'id':f'q{i}:figure:1','questionId':f'q{i}','subject':'Physiology',
       'metadata':{'role':'explanation','source_page':i},
       'candidateImages':[{**candidate,'page':i,'region':[1,2,3,4]}]} for i in range(1,26)]}
    coverage={'sourceVisuals':[{'id':f'q{i}:figure:1','questionId':f'q{i}','subject':'Physiology',
      'coverageStatus':'UNTRACKED_SOURCE_VISUAL','role':'explanation','order':1,'sourcePages':[i]} for i in range(1,26)]}
    registry={'assets':[{'id':'known','subject':'Physiology','status':'PASS',
      'original':{'sha256':'a'*64},'production':{'sha256':'a'*64},'bindings':[]}]}
    qs={f'q{i}':{'question':f'Question {i}','explanation':'Explanation'} for i in range(1,26)}
    with tempfile.TemporaryDirectory() as directory:
        directory=Path(directory)
        paths=[]
        for name in ('registry','progress','coverage'):
            path=directory/(name+'.json');path.write_text('{}');paths.append(path)
        plan=build_plan('Physiology',25,'test','b'*40,audit,coverage,registry,qs,*paths)
    assert plan['auditedReferenceCount']==25
    assert plan['entries'][0]['sourceReferenceId']=='q1:figure:1'
    assert plan['laneHintCounts']=={'B':25,'C':0,'D':0}
    for row in plan['entries']:
        row['decision']='B';row['reuse']={'assetId':'known'}
        row['review']={'sourcePageInspected':True,'questionOwnershipChecked':True,
          'roleOrderChecked':True,'answerSafetyChecked':True,
          'evidence':'rendered page','notes':'exact repeated hash'}
    validate_reviewed_plan(plan)
    try: build_plan('Physiology',6,'bad','b'*40,audit,coverage,registry,qs,*paths)
    except ValueError: pass
    else: raise AssertionError('six-item unattended default leaked into supervised fast lane')
    print('MARROW_IMAGE_FAST_LANE_TEST_OK')

if __name__=='__main__': main()
