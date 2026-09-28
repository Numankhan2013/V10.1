#!/usr/bin/env python3
"""Render source regions for one manually claimed Marrow image batch on CI.

This tool deliberately delegates to marrow_images.py's Ubuntu-only renderer.
The artifact provides source-faithful, source-fingerprinted crops for review.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    checkpoint = args.checkpoint if args.checkpoint.is_absolute() else ROOT / args.checkpoint
    output = args.output if args.output.is_absolute() else ROOT / args.output
    data = json.loads(checkpoint.read_text())
    assert data.get('sourceFile') == 'biochemistryed8.pdf'
    rows = [item for item in data['items'] if item.get('method') == 'region-render']
    assert rows, 'checkpoint has no region-render items'
    manifest = []
    for item in rows:
        target = output / item['referenceId'].replace(':', '_')
        command = [sys.executable, str(ROOT / 'tools/marrow_images.py'), 'render-region',
                   '--subject', 'Biochemistry', '--page', str(item['page']),
                   '--region', *(str(v) for v in item['region']), '--dpi', '300',
                   '--output', str(target)]
        rendered = subprocess.run(command, check=True, text=True, capture_output=True).stdout.strip()
        image = Path(rendered)
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
    output.mkdir(parents=True, exist_ok=True)
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f"MARROW_REGION_RENDERS_OK={len(manifest)} output={output}")


if __name__ == '__main__':
    main()
