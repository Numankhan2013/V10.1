# Source-PDF rendering method (PrepLadder explanations)

Use this for any PDF surface in the app (explanations today, imported note PDFs next).

## What is actually wrong with the sources

- The PrepLadder PDFs (Physiology 1,156 p, Biochemistry 966 p, Anatomy 1,934 p) were
  produced by a generator that used **non-embedded Helvetica (WinAnsi)**. No font data
  ships in the files; every viewer substitutes its own sans.
- WinAnsi has no subscripts/superscripts. The generator replaced each missing character
  with a **ZapfDingbats `I` glyph**, which prints as a black box: `pCO■`, `HCO■■`, `Na■`.
  `pdftotext` shows the boxes as literal text, so **no renderer can recover them** —
  the characters are not in the files. 724 boxes in total (Physiology 456, Biochemistry
  252, Anatomy 16). The few ZapfDingbats `§` glyphs are real marks and are left alone.
- The text is thin, mid-grey Helvetica, so on phones it reads washed out.

## Pipeline

1. **Renderer: Mozilla PDF.js** (`app/src/main/assets/vendor/pdfjs`, `web_pdf_renderer.mjs`)
   on the web; Android keeps native `PdfRenderer`. PDF.js stays the right engine: the
   problems above are in the files, not the rasteriser.
2. **Glyph repair map** — `tools/build_pdf_glyph_repairs.py` (PyMuPDF / MuPDF):
   - reads every page with `get_text("rawdict")`, finds ZapfDingbats `I` chars;
   - infers the intended character from the token it belongs to, using already-repaired
     text to the left and raw text to the right (`CO■→CO₂`, `HCO■■→HCO₃⁻`, `HCO3■→HCO3⁻`,
     `H■O→H₂O`, `H■CO■→H₂CO₃`, `H■→H⁺`, `Na/K■→⁺`, `Cl■→⁻`, `Ca²■→Ca²⁺`, `FADH■→FADH₂`,
     `FEV■→FEV₁`, `NH■■→NH₄⁺`, `[A■]→[A⁻]`, `voltage■gated→-`, `strati■ed→fi`, `90■→90°`);
   - **boxes whose meaning is not certain stay boxes** (no guessed medical content);
   - writes `app/src/main/assets/pdf_glyph_repairs.json`:
     `[x0, y0, x1, y1, char, sub|sup|base, fontSize, color, baseline]` in PDF points,
     top-left origin. Cover rect spans box→next character and the full line height.
   - Current coverage: Physiology 353/456, Biochemistry 187/252, Anatomy 3/16 (543/724).
   - Re-run after any source PDF change: `python3 tools/build_pdf_glyph_repairs.py`.
3. **Paint-over at raster time** (`repairGlyphs` in `web_pdf_renderer.mjs`), after
   `page.render()`: fill the cover rect with the paper colour (brightest pixel just
   above/below the line — never the neighbouring ink), then draw the character with
   canvas `fillText` in the span's colour; sub/sup at 0.68× size, baseline +0.20em /
   −0.38em. Works for inline crops and the fullscreen raster (same `raster()` path).
4. **Tone curve** (`toneCurve`): per-channel gamma 1.7 LUT on the rendered pixels.
   Paper stays 255, grey ink darkens, hue is preserved. The CSS
   `contrast(1.16) saturate(1.12)` filter on canvas/img is a tested contract — leave it,
   and never animate `filter` on the canvas itself (animate a wrapper).
5. **Viewer** (Geist UI): `redesign/nk-viewer.js` + `nk-viewer.css` replace
   `window.openSourceZoom` (legacy UI keeps the original). Shared-element open/close from
   the tapped page, always-dark frosted backdrop, fit-to-width start, pinch/double-tap/
   ctrl-wheel zoom at the finger, momentum pan with rubber-band edges, swipe-down to
   dismiss at fit, tap to hide chrome, Esc/+/−/0. DOM contract kept: `#source-pdf-zoom`,
   `img.source-pdf-zoomimg`, `#spz-minus`, `#spz-reset`, `#spz-plus`, `#spz-close`.

## For a new PDF surface (e.g. imported note PDFs)

- Render with the same PDF.js build; call the same tone curve on the canvas.
- User-imported PDFs normally embed their fonts, so no repair map is needed; if a file
  shows boxes, check `pdffonts` (emb = no) and `pdftotext` first — boxes in the text
  layer mean the source lost the characters.
- Open full-screen through `window.openSourceZoom(img)` (set `img.dataset.sourcePage`
  for the title) to get the same viewer.
