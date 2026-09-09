#!/usr/bin/env python3
"""Check released image bytes and offline manifest in the actual web/APK output."""
import argparse
import json
import zipfile
from pathlib import Path
from marrow_images import ROOT,DATA,binding_is_released,sha,validate
def main():
    p=argparse.ArgumentParser();p.add_argument('--apk',action='store_true');a=p.parse_args()
    if a.apk:
        paths=list((ROOT/'app/build/outputs/apk/debug').glob('*.apk'));assert len(paths)==1
        package=zipfile.ZipFile(paths[0]);read=lambda path:package.read('assets/'+path)
    else:
        read=lambda path:(ROOT/'build/web'/path).read_bytes()
    manifest=json.loads(read('marrow_visual_metadata.js').decode().split('=',1)[1].rstrip(';\n'))
    expected=validate(DATA/'images/registry.json')
    released=[x for x in expected['assets'] if x['status'] in {'PASS','SOURCE_LIMITED'}]
    expected_pairs={(x['id'],b['questionId'],b['role']) for x in released for b in x['bindings'] if binding_is_released(x,b)}
    actual_pairs={(x['id'],qid,x['role']) for qid,rows in manifest.items() for x in rows}
    assert actual_pairs==expected_pairs
    for qid,rows in manifest.items():
        for row in rows:
            content=read(row['src'])
            assert sha(content)==Path(row['src']).stem
            if not a.apk:assert './'+row['src'] in read('sw.js').decode(), 'Figure absent from offline cache'
    assert 'data-marrow-question' in read('index.html').decode()
    assert 'window.NKSourceVisualViewer=viewer;' in read('source_visual_renderer.js').decode()
    print('MARROW_IMAGE_PACKAGE_OK', 'apk' if a.apk else 'web',len(released))
if __name__=='__main__':main()
