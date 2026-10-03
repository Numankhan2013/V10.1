#!/usr/bin/env python3
"""Verify every focused UWorld exhibit survives packaging and offline shell assembly."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile
from uworld_biochemistry import ROOT


def verify(read, web=False):
    inventory = json.loads(read('uworld_figure_inventory.json'))
    assert inventory['reviewedQuestions'] == 132
    assert inventory['sourcePdfSha256'] == '806d95d6f09dde57d34e0d0b5fda69298a7789041bb570ce4fa6dd1c95d4fae9'
    assert inventory['assets']
    shell = read('sw.js').decode() if web else ''
    for path, info in inventory['assets'].items():
        raw = read(path)
        assert raw.startswith(b'\x89PNG\r\n\x1a\n'), path
        assert hashlib.sha256(raw).hexdigest() == info['sha256'], path
        if web:
            assert './'+path in shell, 'Exhibit omitted from offline shell: '+path
    print('UWORLD_MEDIA_PACKAGE_OK assets='+str(len(inventory['assets']))+' offline='+str(web))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--web', default=str(ROOT/'build/web'))
    parser.add_argument('--apk')
    args = parser.parse_args()
    if args.apk:
        with zipfile.ZipFile(args.apk) as apk:
            verify(lambda path: apk.read('assets/'+path))
    else:
        directory = Path(args.web)
        verify(lambda path: (directory/path).read_bytes(), web=True)
