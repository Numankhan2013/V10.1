#!/usr/bin/env python3
"""Exercise release invariants without PDF dependencies or app mutation."""
import copy
import json
from pathlib import Path
import tempfile
from marrow_images import DATA, questions, validate

def main():
    assert len(questions())==2115
    registry=DATA/'images/registry.json'
    value=validate(registry)
    assert value['assets']
    with tempfile.TemporaryDirectory() as directory:
        path=Path(directory)/'registry.json'
        for change in ('duplicate','wrong-subject','corrupt','medical-redraw','unreviewed'):
            bad=copy.deepcopy(value)
            a=bad['assets'][0]
            if change=='duplicate':bad['assets'].append(copy.deepcopy(a))
            elif change=='wrong-subject':a['bindings'][0]['questionId']='marrow__ANAT_CH01_Q001'
            elif change=='corrupt':a['production']['sha256']='0'*64
            elif change=='medical-redraw':a['method']='svg-reconstruction'
            else:a['qa']['sourceCompared']=False
            path.write_text(json.dumps(bad))
            try:validate(path)
            except AssertionError:pass
            else:raise AssertionError('Accepted invalid registry: '+change)
    print('MARROW_IMAGES_TEST_OK')

if __name__=='__main__':main()
