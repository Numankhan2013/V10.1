#!/usr/bin/env python3
"""Auditable Marrow figure inventory, immutable extraction and release validation.

Audit uses pure-Python pypdf; region rendering is an explicit Ubuntu-only action.
No candidate or extraction is automatically approved for learner display.
"""
from __future__ import annotations
import argparse
import base64
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import zlib

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/marrow'
SOURCES = {'Anatomy': ('anatomy_ch001_063', 'Anatomy_ed8.pdf'),
           'Biochemistry': ('biochemistry_ch001_028', 'biochemistryed8.pdf'),
           'Physiology': ('physiology_ch001_043', 'physiologyed8.pdf')}
SIGNAL = re.compile(r'\b(image|figure|diagram|graph|flowchart|shown below)\b', re.I)
RELEASE_STATUSES = {'PASS','SOURCE_LIMITED'}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def binding_is_released(asset,binding):
    return asset['status'] in RELEASE_STATUSES and binding.get('status',asset['status']) in RELEASE_STATUSES

def questions():
    result = {}
    for subject, (prefix, _) in SOURCES.items():
        manifest = json.loads((DATA / (prefix + '_manifest.json')).read_text())
        parts = sorted(DATA.glob(prefix + '.zlib.b64.part*'))
        assert len(parts) == manifest['parts'], prefix
        compressed = base64.b64decode(''.join(p.read_text().strip() for p in parts), validate=True)
        assert sha(compressed) == manifest['compressed_sha256'], prefix
        raw = zlib.decompress(compressed)
        assert sha(raw) == manifest['raw_sha256'], prefix
        bank = json.loads(raw)
        assert len(bank['questions']) == manifest['questions'], prefix
        for q in bank['questions']:
            assert q['id'] not in result
            result[q['id']] = q
    return result

def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

def immutable(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert path.read_bytes() == data, f'Immutable extraction conflict: {path}'
    else:
        path.write_bytes(data)

def validate_svg(path):
    """Allow inert SVG geometry and local marker arrows; reject active content."""
    import xml.etree.ElementTree as ET
    tree = ET.fromstring(path.read_text())
    nodes = list(tree.iter());ids = {}
    for node in nodes:
        tag = node.tag.split('}')[-1]
        assert tag not in {'script','foreignObject','image','use','style','animate','animateMotion','animateTransform','set'}
        node_id = node.attrib.get('id')
        if node_id:
            assert re.fullmatch(r'[A-Za-z][A-Za-z0-9_.-]*', node_id)
            assert node_id not in ids;ids[node_id] = tag
    for node in nodes:
        for key, value in node.attrib.items():
            attr = key.split('}')[-1].lower()
            assert not attr.startswith('on') and attr != 'href'
            if 'url(' not in value.lower():continue
            assert attr in {'marker-start','marker-mid','marker-end'}
            match = re.fullmatch(r'url\(#([A-Za-z][A-Za-z0-9_.-]*)\)', value)
            assert match and ids.get(match.group(1)) == 'marker'
    return tree

def pdf_inventory(path):
    from pypdf import PdfReader
    reader = PdfReader(path)
    pages = []
    for number, page in enumerate(reader.pages, 1):
        objects = page.get('/Resources', {}).get('/XObject', {})
        images = []
        def visit(op, args, cm, tm):
            if op != b'Do' or args[0] not in objects:
                return
            ref = objects[args[0]]
            obj = ref.get_object()
            if obj.get('/Subtype') != '/Image':
                return
            a,b,c,d,e,f = map(float,cm)
            points = [(e,f),(a+e,b+f),(c+e,d+f),(a+c+e,b+d+f)]
            xs,ys = zip(*points)
            height = float(page.mediabox.height)
            rect = [round(min(xs),3),round(height-max(ys),3),round(max(xs),3),round(height-min(ys),3)]
            coverage = abs(a*d-b*c) / (float(page.mediabox.width)*height)
            images.append({'xref': obj.indirect_reference.idnum, 'name': str(args[0]),
                           'width':obj.get('/Width'), 'height':obj.get('/Height'),
                           'filter':str(obj.get('/Filter')), 'mask':bool(obj.get('/SMask') or obj.get('/Mask')),
                           'region':rect, 'pageBackgroundCandidate':coverage > .90,
                           'streamSha256':sha(obj._data)})
        # Walk graphics operators directly: damaged text encodings are irrelevant
        # to image placement and must not make the inventory depend on OCR/fonts.
        cm=[1,0,0,1,0,0];stack=[]
        for args,op in page.get_contents().operations:
            if op==b'q':stack.append(cm[:])
            elif op==b'Q':cm=stack.pop() if stack else [1,0,0,1,0,0]
            elif op==b'cm':
                a,b,c,d,e,f=map(float,args)
                g,h,i,j,k,l=cm
                cm=[a*g+b*i,a*h+b*j,c*g+d*i,c*h+d*j,e*g+f*i+k,e*h+f*j+l]
            elif op==b'Do':visit(op,args,cm,None)
        pages.append({'page':number, 'width':float(page.mediabox.width),
                      'height':float(page.mediabox.height), 'rotation':page.rotation,
                      'images':images,
                      'formObjects':sum(ref.get_object().get('/Subtype') == '/Form' for ref in objects.values())})
    return {'file':path.name,'sha256':sha(path.read_bytes()),'pages':pages}

def audit(output):
    qs = questions()
    pdfs = {s:pdf_inventory(DATA/'source_pdfs'/filename) for s,(_,filename) in SOURCES.items()}
    bindings = []
    summaries = {}
    for subject in SOURCES:
        subject_qs = [q for q in qs.values() if q['subject']==subject]
        explicit = signals = 0
        for q in subject_qs:
            figures = q.get('structuredExplanation',{}).get('figures',[])
            explicit += bool(figures)
            if not figures and SIGNAL.search(q['question']+' '+q.get('explanation','')):
                signals += 1
                bindings.append({'id':q['id']+':unmapped','questionId':q['id'],'subject':subject,
                                 'status':'REVIEW_REQUIRED','reason':'Text cue without figure metadata',
                                 'provenance':q['provenance']})
            for i,figure in enumerate(figures):
                pages = figure.get('source_pages') or [figure.get('source_page')]
                candidates = []
                for p in pages:
                    if isinstance(p,int) and 1<=p<=len(pdfs[subject]['pages']):
                        candidates.extend({'page':p,**im} for im in pdfs[subject]['pages'][p-1]['images'] if not im['pageBackgroundCandidate'])
                bindings.append({'id':q['id']+':figure:'+str(i+1),'questionId':q['id'],
                                 'subject':subject,'metadata':figure,'candidateImages':candidates,
                                 'status':'REVIEW_REQUIRED',
                                 'reason':'Verify ownership, crop, role, labels and quality against source'})
        rows = [b for b in bindings if b['subject']==subject]
        summaries[subject] = {'questions':len(subject_qs),'questionsWithFigureMetadata':explicit,
                              'additionalTextCueQuestions':signals,'figureReferences':sum(len(q.get('structuredExplanation',{}).get('figures',[])) for q in subject_qs),
                              'referencesWithNativeCandidates':sum(bool(b.get('candidateImages')) for b in rows),
                              'pdfPages':len(pdfs[subject]['pages']),
                              'uniqueNonBackgroundImageStreams':len({im['streamSha256'] for p in pdfs[subject]['pages'] for im in p['images'] if not im['pageBackgroundCandidate']}),
                              'qualityApproved':0,'classificationPending':len(rows)}
    report = {'schemaVersion':1,'coordinateSystem':'PDF points, top-left origin, unrotated MediaBox',
              'summary':summaries,'sources':pdfs,'bindings':bindings,
              'limitations':['Native candidates do not establish ownership or acceptable quality.',
                              'Text cues can be false positives; pages without cues also need coverage review.',
                              'Form XObjects, page rotation and composited annotations require region inspection.',
                              'Image stream counts are not educational asset counts.']}
    write_json(output,report)
    write_json(output.with_name('summary.json'),{'schemaVersion':1,'summary':summaries,
               'sourceHashes':{s:p['sha256'] for s,p in pdfs.items()},'limitations':report['limitations']})
    print(json.dumps(summaries,indent=2))

def extract(subject, page_number, xref, output):
    from pypdf import PdfReader
    filename = SOURCES[subject][1]
    source = DATA/'source_pdfs'/filename
    reader = PdfReader(source)
    page = reader.pages[page_number-1]
    matches = [r for r in page['/Resources'].get('/XObject',{}).values() if r.idnum==xref]
    assert len(matches)==1, 'Object must occur on the specified page'
    obj = matches[0].get_object()
    assert obj.get('/Subtype')=='/Image'
    filters = obj.get('/Filter')
    assert filters == '/DCTDecode' or filters == ['/DCTDecode'], 'Use region rendering or lossless decoder for non-JPEG objects'
    assert not obj.get('/SMask') and not obj.get('/Mask'), 'Masked image needs compositing review'
    raw = obj._data
    digest = sha(raw)
    target = output/(digest+'.jpg')
    immutable(target,raw)
    write_json(output/(digest+'.json'),{'source':filename,'sourceSha256':sha(source.read_bytes()),
               'page':page_number,'xref':xref,'sha256':digest,'method':'native-jpeg-stream',
               'width':obj['/Width'],'height':obj['/Height'],'status':'REVIEW_REQUIRED'})
    print(target)

def render_region(subject, page_number, region, dpi, output):
    from verification_preflight import is_termux
    if is_termux():
        raise SystemExit('Region rendering requires Ubuntu CI; do not install PyMuPDF in Termux.')
    import fitz
    assert 144<=dpi<=600
    filename=SOURCES[subject][1]
    source=DATA/'source_pdfs'/filename
    with fitz.open(source) as document:
        assert 1<=page_number<=len(document)
        page=document[page_number-1]
        assert page.rotation==0, 'Resolve rotation explicitly before rendering'
        rect=fitz.Rect(region)
        assert not rect.is_empty and page.rect.contains(rect)
        png=page.get_pixmap(matrix=fitz.Matrix(dpi/72,dpi/72),clip=rect,alpha=False).tobytes('png')
        digest=sha(png)
        immutable(output/(digest+'.png'),png)
        evidence={'source':filename,'sourceSha256':sha(source.read_bytes()),'page':page_number,
                  'region':region,'dpi':dpi,'sha256':digest,'method':'region-render',
                  'status':'REVIEW_REQUIRED','note':'Rendering does not recover lost raster detail.'}
        immutable(output/(digest+'.json'),(json.dumps(evidence,indent=2)+'\n').encode())
        print(output/(digest+'.png'))

def validate(registry):
    qs = questions()
    value = json.loads(registry.read_text())
    assert value['schemaVersion']==1
    ids = set()
    for asset in value['assets']:
        assert asset['id'] not in ids
        ids.add(asset['id'])
        assert asset['status'] in {'PASS','REVIEW_REQUIRED','SOURCE_LIMITED','REJECTED'}
        assert asset['subject'] in SOURCES
        assert asset['kind'] in {'diagram','medical','hybrid','table','unknown'}
        src = asset['source']
        source_path = DATA/'source_pdfs'/SOURCES[asset['subject']][1]
        assert src['file']==source_path.name and src['sha256']==sha(source_path.read_bytes())
        assert isinstance(src['page'],int) and src['page']>0
        assert len(src['region'])==4 and src['region'][0]<src['region'][2] and src['region'][1]<src['region'][3]
        assert all(isinstance(n,(float,int)) and __import__('math').isfinite(n) for n in src['region'])
        assert src['region'][0]>=0 and src['region'][1]>=0
        assert asset['method'] in {'native-jpeg-stream','region-render','svg-reconstruction','hybrid-overlay','conservative-processing'}
        for binding in asset['bindings']:
            assert qs[binding['questionId']]['subject']==asset['subject']
            assert binding['role'] in {'question','explanation'}
            assert isinstance(binding['order'],int)
            binding_status = binding.get('status')
            if binding_status is not None:
                assert binding_status in {'PASS','REVIEW_REQUIRED','REJECTED'}
                binding_source=binding.get('source')
                assert binding_source and isinstance(binding_source.get('page'),int) and isinstance(binding_source.get('xref'),int)
                assert len(binding_source.get('region',[]))==4
                if binding_status == 'PASS':
                    assert binding.get('qa',{}).get('sourceCompared') is True
                    assert binding['qa'].get('notes')
        for key in ('original','production'):
            record = asset.get(key)
            if record:
                path = (ROOT/record['path']).resolve()
                assert path.is_relative_to(ROOT)
                assert sha(path.read_bytes())==record['sha256']
        if asset.get('production'):
            assert all(isinstance(asset['production'][k],int) and asset['production'][k]>0 for k in ('width','height'))
        if asset['status'] in {'PASS','SOURCE_LIMITED'}:
            assert asset.get('original') and asset.get('production') and asset.get('qa')
            assert asset['qa'].get('sourceCompared') is True
            assert asset['qa'].get('notes')
            assert asset['qa'].get('originalSha256')==asset['original']['sha256'], 'Source changed since QA'
            assert asset['qa'].get('productionSha256')==asset['production']['sha256'], 'Production changed since QA'
        if asset['kind']=='medical' and asset['method']=='native-jpeg-stream':
            assert asset['original']['sha256']==asset['production']['sha256']
        assert not (asset['kind']=='medical' and asset['method']=='svg-reconstruction')
    return value

def release(registry):
    value = validate(registry)
    assets = ROOT/'app/src/main/assets'
    runtime = {}
    for a in value['assets']:
        if a['status'] not in RELEASE_STATUSES:
            continue
        p = a['production']
        src = ROOT/p['path']
        assert src.suffix.lower() in {'.svg','.png','.jpg','.webp'}
        if src.suffix.lower()=='.svg':
            validate_svg(src)
        rel = 'marrow_visuals/'+p['sha256']+src.suffix.lower()
        immutable(assets/rel,src.read_bytes())
        for b in a['bindings']:
            if not binding_is_released(a,b):
                continue
            runtime.setdefault(b['questionId'],[]).append({'id':a['id'],'role':b['role'],
                 'order':b['order'],'src':rel,'alt':b.get('alt','Source figure'),
                 'status':a['status'],'width':p['width'],'height':p['height']})
    for rows in runtime.values():
        rows.sort(key=lambda r:(r['order'],r['id']))
    (assets/'marrow_visual_metadata.js').write_text('window.MARROW_VISUALS='+json.dumps(runtime,separators=(',',':')).replace('</','<\\/')+';\n')
    print(f'MARROW_IMAGES_RELEASE_OK questions={len(runtime)} assets={sum(a["status"] in {"PASS","SOURCE_LIMITED"} for a in value["assets"])}')

def review(registry, asset_id, status, kind, notes, evidence):
    value=validate(registry)
    matches=[a for a in value['assets'] if a['id']==asset_id]
    assert len(matches)==1
    a=matches[0]
    a['status']=status;a['kind']=kind
    a['qa']={'sourceCompared':True,'notes':notes,'evidence':evidence,
             'originalSha256':a['original']['sha256'],'productionSha256':a['production']['sha256']}
    write_json(registry,value)
    validate(registry)
    print('MARROW_IMAGE_REVIEW_RECORDED',asset_id,status)

def review_binding(registry, asset_id, question_id, status, notes, evidence):
    value=validate(registry)
    matches=[a for a in value['assets'] if a['id']==asset_id]
    assert len(matches)==1
    bindings=[b for b in matches[0]['bindings'] if b['questionId']==question_id]
    assert len(bindings)==1
    binding=bindings[0];binding['status']=status
    binding['qa']={'sourceCompared':status=='PASS','notes':notes,'evidence':evidence}
    write_json(registry,value)
    validate(registry)
    print('MARROW_IMAGE_BINDING_REVIEW_RECORDED',asset_id,question_id,status)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='command',required=True)
    a=sub.add_parser('audit');a.add_argument('--output',type=Path,default=ROOT/'build/marrow-images/audit.json')
    e=sub.add_parser('extract');e.add_argument('--subject',choices=SOURCES,required=True);e.add_argument('--page',type=int,required=True);e.add_argument('--xref',type=int,required=True);e.add_argument('--output',type=Path,default=DATA/'images/originals')
    r=sub.add_parser('render-region');r.add_argument('--subject',choices=SOURCES,required=True);r.add_argument('--page',type=int,required=True);r.add_argument('--region',type=float,nargs=4,required=True);r.add_argument('--dpi',type=int,default=300);r.add_argument('--output',type=Path,default=DATA/'images/originals')
    for command in ('validate','release'):
        a=sub.add_parser(command);a.add_argument('--registry',type=Path,default=DATA/'images/registry.json')
    r=sub.add_parser('review');r.add_argument('--registry',type=Path,default=DATA/'images/registry.json');r.add_argument('--asset',required=True);r.add_argument('--status',choices=['PASS','SOURCE_LIMITED','REVIEW_REQUIRED','REJECTED'],required=True);r.add_argument('--kind',choices=['diagram','medical','hybrid','table','unknown'],required=True);r.add_argument('--notes',required=True);r.add_argument('--evidence',required=True)
    b=sub.add_parser('review-binding');b.add_argument('--registry',type=Path,default=DATA/'images/registry.json');b.add_argument('--asset',required=True);b.add_argument('--question',required=True);b.add_argument('--status',choices=['PASS','REVIEW_REQUIRED','REJECTED'],required=True);b.add_argument('--notes',required=True);b.add_argument('--evidence',required=True)
    a=p.parse_args()
    if a.command=='audit':audit(a.output)
    elif a.command=='extract':extract(a.subject,a.page,a.xref,a.output)
    elif a.command=='render-region':render_region(a.subject,a.page,a.region,a.dpi,a.output)
    elif a.command=='validate':validate(a.registry);print('MARROW_IMAGE_REGISTRY_OK')
    elif a.command=='review':review(a.registry,a.asset,a.status,a.kind,a.notes,a.evidence)
    elif a.command=='review-binding':review_binding(a.registry,a.asset,a.question,a.status,a.notes,a.evidence)
    else:release(a.registry)

if __name__=='__main__':main()
