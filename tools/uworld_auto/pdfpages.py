"""Poppler-backed page access for UWorld screenshot PDFs (OCR text layer + raster)."""
import re, subprocess, html
from functools import lru_cache
from PIL import Image
import io

LINE_RE = re.compile(r'<line xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</line>', re.S)
WORD_RE = re.compile(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>')
PAGE_RE = re.compile(r'<page width="([\d.]+)" height="([\d.]+)">(.*?)</page>', re.S)


class Doc:
    def __init__(self, path):
        self.path = str(path)
        info = subprocess.run(['pdfinfo', '-box', self.path], capture_output=True, text=True).stdout
        self.pages = int(re.search(r'Pages:\s+(\d+)', info).group(1))
        mb = re.search(r'MediaBox:\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)', info)
        cb = re.search(r'CropBox:\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)', info)
        # Pages are rotated 90°: the unrotated x crop becomes a vertical offset.
        self.yoff = float(cb.group(1)) - float(mb.group(1)) if cb else 0.0
        self._lines = {}

    def load_lines(self, first, last):
        out = subprocess.run(['pdftotext', '-f', str(first), '-l', str(last), '-bbox-layout', self.path, '-'],
                             capture_output=True, text=True).stdout
        for i, m in enumerate(PAGE_RE.finditer(out)):
            lines = []
            for lm in LINE_RE.finditer(m.group(3)):
                words = [(float(a), float(b) - self.yoff, float(c), float(d) - self.yoff, html.unescape(t))
                         for a, b, c, d, t in WORD_RE.findall(lm.group(5))]
                if words:
                    lines.append({'x0': min(w[0] for w in words), 'y0': min(w[1] for w in words),
                                  'x1': max(w[2] for w in words), 'y1': max(w[3] for w in words),
                                  'words': words, 'text': ' '.join(w[4] for w in words)})
            self._lines[first + i] = lines

    def lines(self, page):
        if page not in self._lines:
            self.load_lines(page, min(self.pages, page + 49))
        return self._lines[page]

    def image(self, page, dpi=72):
        png = subprocess.run(['pdftoppm', '-f', str(page), '-l', str(page), '-r', str(dpi), '-png', self.path],
                             capture_output=True).stdout
        im = Image.open(io.BytesIO(png)).convert('RGB')
        s = dpi / 72
        return im.crop((0, round(self.yoff * s), im.width, im.height))
