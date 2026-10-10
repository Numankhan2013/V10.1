#!/usr/bin/env python3
"""Sharpen line diagrams in auto-extracted UWorld figures with Real-ESRGAN.

  upscale_figures.py <slug> [<slug> ...] [--limit N]

Model: https://huggingface.co/tamnvcc/Real-ESRGAN-General-x4v3_float (onnx/model.onnx)
saved as tools/uworld_auto/models/realesr-general-x4v3.onnx (not committed).

The source PDFs hold the viewer screenshots at ~91 ppi, so labelled diagrams look
soft on phone screens. Diagram-like crops (mostly white background: line art, text
labels, charts) are upscaled 4x with Real-ESRGAN General x4v3 (BSD-3, compact
SRVGG model, ONNX) and stored at 1.5x the original size. Photographs and
micrographs are left untouched: a GAN upscaler alters fine tissue texture.
File names are unchanged (they pin page + bbox), so the app needs no change.
Processed files are listed in prepared/<slug>/upscaled.json (re-runs skip them).
"""
import json, sys, time
from pathlib import Path
import numpy as np
import onnxruntime as ort
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MODEL = HERE / 'models/realesr-general-x4v3.onnx'
T, O, SCALE = 128, 12, 1.5
sess = None


def is_diagram(im):
    a = np.asarray(im.convert('L').resize((96, 96)))
    return (a > 235).mean() > 0.5


def up4(a):
    """a: float32 HxWx3 in [0,1], already edge-padded by O. Returns 4x of the unpadded area."""
    h, w, _ = a.shape
    step = T - 2 * O
    ny, nx = max(1, -(-(h - 2 * O) // step)), max(1, -(-(w - 2 * O) // step))
    H, W = ny * step + 2 * O, nx * step + 2 * O
    p = np.pad(a, ((0, H - h), (0, W - w), (0, 0)), mode='edge')
    out = np.zeros((H * 4, W * 4, 3), np.float32)
    for y in range(ny):
        for x in range(nx):
            tile = p[y * step:y * step + T, x * step:x * step + T].transpose(2, 0, 1)[None]
            r = sess.run(None, {'image': tile})[0][0].transpose(1, 2, 0)
            oy, ox = y * step * 4, x * step * 4
            out[oy + O * 4:oy + (T - O) * 4, ox + O * 4:ox + (T - O) * 4] = r[O * 4:(T - O) * 4, O * 4:(T - O) * 4]
    return out[O * 4:(h - O) * 4, O * 4:(w - O) * 4]


def upscale(im):
    rgb = np.asarray(im.convert('RGB'), dtype=np.float32) / 255.0
    big = up4(np.pad(rgb, ((O, O), (O, O), (0, 0)), mode='edge'))
    big = Image.fromarray((np.clip(big, 0, 1) * 255 + .5).astype(np.uint8))
    return big.resize((round(im.width * SCALE), round(im.height * SCALE)), Image.LANCZOS)


def main():
    global sess
    args = sys.argv[1:]
    limit = int(args[args.index('--limit') + 1]) if '--limit' in args else None
    slugs = [a for i, a in enumerate(args) if not a.startswith('--') and (i == 0 or args[i - 1] != '--limit')]
    sess = ort.InferenceSession(str(MODEL), providers=['CPUExecutionProvider'])
    for slug in slugs:
        src = ROOT / 'data/uworld/prepared' / slug
        log_path = src / 'upscaled.json'
        done = json.loads(log_path.read_text()) if log_path.exists() else {}
        n = skipped = 0; t0 = time.time()
        for f in sorted((src / 'figures').glob('*.webp')):
            if f.name in done:
                continue
            im = Image.open(f)
            if not is_diagram(im):
                done[f.name] = 'photo-kept'; skipped += 1
            else:
                out = upscale(im)
                out.save(f, 'WEBP', quality=88, method=6)
                done[f.name] = f'{im.width}x{im.height}->{out.width}x{out.height}'
                n += 1
            if (n + skipped) % 25 == 0:
                log_path.write_text(json.dumps(done, indent=0, sort_keys=True))
                print(slug, n, 'upscaled', skipped, 'kept', round(time.time() - t0), 's', flush=True)
            if limit and n >= limit:
                break
        log_path.write_text(json.dumps(done, indent=0, sort_keys=True))
        print('DONE', slug, n, 'upscaled', skipped, 'kept', round(time.time() - t0), 's', flush=True)


if __name__ == '__main__':
    main()
