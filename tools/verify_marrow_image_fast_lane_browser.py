#!/usr/bin/env python3
"""Targeted learner-state verification for reviewed Marrow fast-lane bindings."""
from __future__ import annotations
import argparse, contextlib, http.server, json, socketserver, threading
from pathlib import Path
from playwright.sync_api import sync_playwright
from marrow_image_fast_lane import validate_reviewed_plan
from marrow_images import DATA, ROOT, binding_is_released, validate

WEB=ROOT/'build/web'
OUT=ROOT/'build/marrow-fast-lane-browser'

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
    def translate_path(self,path):
        if path.split('?',1)[0].split('#',1)[0]=='/anatomy-source.pdf':
            return str(ROOT/'app/src/main/assets/Anatomy_QBank_Source.pdf')
        return super().translate_path(path)

def released_for_question(registry,question_id):
    rows=[]
    for asset in registry['assets']:
        for binding in asset.get('bindings',[]):
            if binding.get('questionId')!=question_id or not binding_is_released(asset,binding): continue
            production=asset['production'];suffix=Path(production['path']).suffix.lower()
            rows.append({'assetId':asset['id'],'role':binding['role'],'order':binding['order'],
              'src':'marrow_visuals/'+production['sha256']+suffix,'alt':binding.get('alt','Source figure'),
              'width':production['width'],'height':production['height']})
    return sorted(rows,key=lambda row:(row['order'],row['assetId']))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--plan',type=Path,required=True)
    parser.add_argument('--web',type=Path,default=WEB);parser.add_argument('--output',type=Path,default=OUT)
    args=parser.parse_args()
    plan_path=args.plan.resolve();review_root=(DATA/'images/review_batches').resolve()
    if not plan_path.is_relative_to(review_root): raise SystemExit('Reviewed plan must live under data/marrow/images/review_batches')
    plan=json.loads(plan_path.read_text());validate_reviewed_plan(plan)
    registry=validate(DATA/'images/registry.json')
    assets={asset['id']:asset for asset in registry['assets']}
    changed=[]
    for row in plan['entries']:
        if row['decision']=='B': asset_id=row['reuse']['assetId']
        elif row['decision']=='C': asset_id=row['extraction']['assetId']
        else: continue
        asset=assets[asset_id]
        bindings=[b for b in asset['bindings'] if b['questionId']==row['questionId'] and b['role']==row['role'] and b['order']==row['order']]
        assert len(bindings)==1 and binding_is_released(asset,bindings[0]),row['sourceReferenceId']
        changed.append({**row,'assetId':asset_id,'newUniqueAsset':row['decision']=='C' and row['extraction'].get('newUniqueAsset',False)})
    args.output.mkdir(parents=True,exist_ok=True)
    handler=lambda *a,**k:Quiet(*a,directory=str(args.web.resolve()),**k)
    with socketserver.TCPServer(('127.0.0.1',0),handler) as server:
        threading.Thread(target=server.serve_forever,daemon=True).start();port=server.server_address[1]
        with sync_playwright() as p:
            browser=p.chromium.launch(headless=True)
            page=browser.new_page(viewport={'width':390,'height':844});errors=[]
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.goto(f'http://127.0.0.1:{port}/index.html',wait_until='networkidle')
            page.locator('button.nk-subject-row').filter(has_text=plan['subject']).click()
            page.locator('button.nk-bank-card').filter(has_text='Marrow').click()
            for row in changed:
                qid=row['questionId'];expected=released_for_question(registry,qid)
                page.evaluate('(id)=>window.QB.practiceOne(id)',qid);page.wait_for_timeout(80)
                question_expected=[item for item in expected if item['role']=='question']
                actual_before=page.locator('.nk-marrow-figure-button img')
                page.wait_for_timeout(60)
                assert actual_before.count()==len(question_expected),(qid,'pre-answer-count',actual_before.count(),len(question_expected))
                before_src=[actual_before.nth(i).get_attribute('src') for i in range(actual_before.count())]
                assert all(any(src.endswith(item['src']) for src in before_src) for item in question_expected)
                target=next(item for item in expected if item['assetId']==row['assetId'] and item['role']==row['role'] and item['order']==row['order'])
                target_locator=page.locator(f'.nk-marrow-figure-button img[src$="{target["src"]}"]')
                if row['role']=='question':
                    assert target_locator.count()==1
                    assert target_locator.get_attribute('alt')==target['alt']
                    assert target['alt']=='Source question figure'
                    page.wait_for_function('(src)=>{const x=[...document.querySelectorAll(".nk-marrow-figure-button img")].find(i=>i.src.endsWith(src));return x&&x.naturalWidth>0}',target['src'])
                else:
                    assert target_locator.count()==0,(qid,'explanation-leak')
                    page.locator('.option-list button').first.click();page.wait_for_timeout(120)
                    actual_after=page.locator('.nk-marrow-figure-button img')
                    assert actual_after.count()==len(expected),(qid,'post-answer-count',actual_after.count(),len(expected))
                    after_src=[actual_after.nth(i).get_attribute('src') for i in range(actual_after.count())]
                    assert all(any(src.endswith(item['src']) for src in after_src) for item in expected)
                    target_locator=page.locator(f'.nk-marrow-figure-button img[src$="{target["src"]}"]')
                    assert target_locator.count()==1
                    page.wait_for_function('(src)=>{const x=[...document.querySelectorAll(".nk-marrow-figure-button img")].find(i=>i.src.endsWith(src));return x&&x.naturalWidth>0}',target['src'])
                page.screenshot(path=str(args.output/f"{row['position']:02d}-{qid}-{row['role']}.png"),full_page=True)
                if row['newUniqueAsset']:
                    target_locator.click();page.wait_for_timeout(60)
                    assert page.locator('#nk-source-viewer img').count()==1
                    page.screenshot(path=str(args.output/f"{row['position']:02d}-{qid}-viewer.png"))
                    page.locator('#nk-source-viewer .nk-sv-close').click()
            browser.close()
    if errors: raise SystemExit('Browser errors: '+repr(errors))
    print('MARROW_FAST_LANE_BROWSER_OK',len(changed),'viewport=390x844')

if __name__=='__main__': main()
