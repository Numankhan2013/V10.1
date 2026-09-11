#!/usr/bin/env python3
"""Exercise release invariants without PDF dependencies or app mutation."""
import copy
import json
from pathlib import Path
import tempfile
from marrow_images import DATA, binding_is_released, questions, validate, validate_svg
from stage_marrow_image_review import normalize_role, alt_text, binding_order
from marrow_image_progress import build_progress

def main():
    assert len(questions())==2494
    assert normalize_role('question-critical image')=='question'
    assert normalize_role(None)=='explanation'
    assert normalize_role(None,'Microscopy is shown in the given image.')=='question'
    assert normalize_role(None,'An image-guided biopsy was discussed.')=='explanation'
    assert binding_order({'id':'q:figure:2'})==2
    assert alt_text({'title':'Answer-revealing label'},'question')=='Source question figure'
    registry=DATA/'images/registry.json'
    value=validate(registry)
    assert value['assets']
    rejected=[(a,b) for a in value['assets'] for b in a['bindings'] if b.get('status')=='REJECTED']
    assert rejected and all(not binding_is_released(a,b) for a,b in rejected)
    progress=build_progress(value)
    assert progress['bindings']['releasedQuestionCount']>=34
    assert progress['bindings']['byStatus']['REJECTED']>=2
    assert json.loads((DATA/'images/progress.json').read_text())==progress
    with tempfile.TemporaryDirectory() as directory:
        directory=Path(directory);path=directory/'registry.json'
        for change in ('duplicate','wrong-subject','corrupt','medical-redraw','unreviewed','stale-qa'):
            bad=copy.deepcopy(value)
            a=bad['assets'][0]
            if change=='duplicate':bad['assets'].append(copy.deepcopy(a))
            elif change=='wrong-subject':a['bindings'][0]['questionId']='marrow__ANAT_CH01_Q001'
            elif change=='corrupt':a['production']['sha256']='0'*64
            elif change=='medical-redraw':a['method']='svg-reconstruction'
            elif change=='stale-qa':a['qa']['productionSha256']='0'*64
            else:a['qa']['sourceCompared']=False
            path.write_text(json.dumps(bad))
            try:validate(path)
            except AssertionError:pass
            else:raise AssertionError('Accepted invalid registry: '+change)
        safe=directory/'safe.svg'
        safe.write_text('<svg xmlns="http://www.w3.org/2000/svg"><defs><marker id="a"><path d="M0 0L1 1"/></marker></defs><path marker-end="url(#a)"/></svg>')
        validate_svg(safe)
        for name,markup in {
            'script':'<svg xmlns="http://www.w3.org/2000/svg"><script/></svg>',
            'external':'<svg xmlns="http://www.w3.org/2000/svg"><path marker-end="url(https://bad.example/a)"/></svg>',
            'event':'<svg xmlns="http://www.w3.org/2000/svg"><path onclick="bad()"/></svg>',
            'wrong-target':'<svg xmlns="http://www.w3.org/2000/svg"><path id="a"/><path marker-end="url(#a)"/></svg>'}.items():
            bad_svg=directory/(name+'.svg');bad_svg.write_text(markup)
            try:validate_svg(bad_svg)
            except AssertionError:pass
            else:raise AssertionError('Accepted unsafe SVG: '+name)
    print('MARROW_IMAGES_TEST_OK')

if __name__=='__main__':main()
