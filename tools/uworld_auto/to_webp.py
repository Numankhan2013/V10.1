#!/usr/bin/env python3
"""Convert a collection's PNG crops to WebP in place (scale 2x crops down to native 1.3x)."""
import sys
from pathlib import Path
from PIL import Image
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
from package import save_crop, ROOT

scale = 1.0
args = sys.argv[1:]
if args and args[0].startswith('--scale='):
    scale = float(args.pop(0).split('=', 1)[1])
for slug in args:
    figs = ROOT / 'data/uworld/prepared' / slug / 'figures'
    n = 0
    for png in sorted(figs.glob('*.png')):
        im = Image.open(png).convert('RGB')
        if scale != 1.0:
            im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))), Image.LANCZOS)
        save_crop(im, png.with_suffix('.webp'))
        png.unlink(); n += 1
    print(slug, n, 'converted')
