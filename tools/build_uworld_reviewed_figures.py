#!/usr/bin/env python3
"""CI-only lossless focused crops from visually reviewed, PDF-pinned coordinates."""
import argparse
import hashlib
import json
from pathlib import Path
from verification_preflight import pdf_preflight
from uworld_biochemistry import ROOT
from uworld_reviewed_document import figures
from uworld_collections import media_sources


def build(output):
    import fitz
    from PIL import Image
    output = Path(output)
    target = output / 'source_visuals/uworld'
    target.mkdir(parents=True, exist_ok=True)
    assets = {}
    sources = []
    for source_pdf, manifest, reviewed in media_sources():
        if hashlib.sha256(source_pdf.read_bytes()).hexdigest() != manifest['source_sha256']:
            raise ValueError('Original UWorld PDF unavailable or hash mismatch; fetch its LFS object')
        sources.append({'sourcePdfSha256': manifest['source_sha256'], 'reviewedQuestions': len(reviewed)})
        with fitz.open(source_pdf) as pdf:
            for doc in reviewed.values():
                for node in figures(doc):
                    asset = node['asset']
                    if asset in assets:
                        continue
                    page = pdf[node['page'] - 1]
                    bbox = node['bbox']
                    if bbox[2] > page.rect.width + .1 or bbox[3] > page.rect.height + .1:
                        raise ValueError('Reviewed crop exceeds actual PDF display geometry: ' + asset)
                    # Render the rotated display page, then crop in the reviewed coordinate space.
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                    image = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
                    crop = image.crop(tuple(round(v * 2) for v in bbox))
                    path = output / asset
                    crop.save(path, optimize=True)
                    assets[asset] = {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'width': crop.width, 'height': crop.height, 'sourcePdfSha256': manifest['source_sha256'],
                                     'sourcePage': node['page'], 'bbox': bbox}
    expected = {Path(asset).name for asset in assets}
    for stale in target.glob('*.png'):
        if stale.name not in expected:
            stale.unlink()
    report = {'sourcePdfSha256': sources[0]['sourcePdfSha256'], 'reviewedQuestions': sum(s['reviewedQuestions'] for s in sources), 'sources': sources, 'assets': assets}
    (output / 'uworld_figure_inventory.json').write_text(json.dumps(report, indent=2))
    print(f'UWORLD_REVIEWED_FIGURES_OK questions={report["reviewedQuestions"]} assets={len(assets)} lossless=true')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default=str(ROOT / 'app/src/main/assets'))
    args = parser.parse_args()
    if pdf_preflight():
        build(args.output)
