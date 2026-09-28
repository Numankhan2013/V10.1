#!/usr/bin/env python3
"""Render source regions for one manually claimed Marrow image batch on CI.

This tool deliberately delegates to marrow_images.py's Ubuntu-only renderer.
The artifact provides source-faithful, source-fingerprinted crops for review.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from PIL import Image
from marrow_images import SOURCES

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    checkpoint = args.checkpoint if args.checkpoint.is_absolute() else ROOT / args.checkpoint
    output = args.output if args.output.is_absolute() else ROOT / args.output
    data = json.loads(checkpoint.read_text())
    subjects = {filename: subject for subject, (_, filename) in SOURCES.items()}
    source_file = data.get('sourceFile')
    assert source_file in subjects, f'Unsupported Marrow source: {source_file!r}'
    subject = subjects[source_file]
    source = ROOT / 'data/marrow/source_pdfs' / source_file
    assert hashlib.sha256(source.read_bytes()).hexdigest() == data['sourceSha256']
    rows = [item for item in data['items'] if item.get('method') == 'region-render']
    assert rows, 'checkpoint has no region-render items'
    manifest = []
    output.mkdir(parents=True, exist_ok=True)
    for index, item in enumerate(rows):
        assert item['referenceId'].startswith({
            'Anatomy': 'marrow__ANAT_',
            'Biochemistry': 'marrow__BIOCHEM_',
            'Physiology': 'marrow__PHYS_',
        }[subject])
        # A reference can cite multiple source pages or regions. Keep its stable
        # ID in the manifest while giving every render its own artifact folder.
        target = output / (item['referenceId'].replace(':', '_') +
                           f"__p{item['page']}__r{index}")
        target.mkdir(parents=True, exist_ok=True)
        command = [sys.executable, str(ROOT / 'tools/marrow_images.py'), 'render-region',
                   '--subject', subject, '--page', str(item['page']),
                   '--region', *(str(v) for v in item['region']), '--dpi', '300',
                   '--output', str(target)]
        rendered = subprocess.run(command, check=True, text=True, capture_output=True)
        images = sorted(target.glob('*.png'))
        if len(images) != 1:
            raise AssertionError(f"Expected one render in {target}; stdout={rendered.stdout!r}; stderr={rendered.stderr!r}; files={list(target.iterdir())!r}")
        image = images[0]
        metadata = image.with_suffix('.json')
        assert image.is_file() and metadata.is_file()
        evidence = json.loads(metadata.read_text())
        assert evidence['sourceSha256'] == data['sourceSha256']
        assert evidence['page'] == item['page'] and evidence['region'] == item['region']
        manifest.append({'referenceId': item['referenceId'], 'page': item['page'],
                         'region': item['region'], 'sourceSha256': evidence['sourceSha256'],
                         'sha256': evidence['sha256'],
                         'file': image.relative_to(output).as_posix(),
                         'metadata': metadata.relative_to(output).as_posix(),
                         'width': Image.open(image).width,
                         'height': Image.open(image).height})
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f"MARROW_REGION_RENDERS_OK={len(manifest)} output={output}")


if __name__ == '__main__':
    main()
