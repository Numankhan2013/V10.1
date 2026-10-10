/* Browser-only source-solution renderer using Mozilla PDF.js. Android keeps native PdfRenderer. */
if (location.hostname !== 'qbank.local') {
  const pdfjs = await import('./vendor/pdfjs/pdf.min.mjs');
  pdfjs.GlobalWorkerOptions.workerSrc = './vendor/pdfjs/pdf.worker.min.mjs';
  const config = window.NK_QBANK_FIREBASE_CONFIG || {};
  const urls = {
    biochemistry: './Biochemistry_QBank_Source.pdf',
    physiology: './Physiology_QBank_Source.pdf',
    anatomy: String(config.anatomyPdfUrl || '')
  };
  const documents = new Map();
  let renderQueue = Promise.resolve();

  // Glyph repairs: the PrepLadder PDFs print a black box wherever their generator had no
  // subscript/superscript (pCO■, HCO■■, Na■). tools/build_pdf_glyph_repairs.py maps each
  // box to its intended character; here it is painted over the box after PDF.js draws.
  let repairs = null;
  const repairsReady = fetch('./pdf_glyph_repairs.json').then(r => r.ok ? r.json() : null)
    .then(j => { repairs = j && j.subjects || {}; }).catch(() => { repairs = {}; });
  function repairGlyphs(ctx, subject, pageNo, scale, top, bottom) {
    const list = repairs && repairs[subject] && repairs[subject][String(pageNo)];
    if (!list) return;
    for (const [x0, y0, x1, y1, ch, kind, size, color, baseline] of list) {
      if (y1 < top || y0 > bottom) continue;
      const bx = x0 * scale, by = (y0 - top) * scale, w = (x1 - x0) * scale, h = (y1 - y0) * scale;
      // Paper colour: brightest pixel just above/below the line (never the neighbouring ink).
      let bg = '#ffffff', best = -1;
      for (const [sx, sy] of [[bx, by - 2], [bx + w, by - 2], [bx, by + h + 2], [bx + w, by + h + 2]]) {
        try {
          const d = ctx.getImageData(Math.max(0, Math.round(sx)), Math.max(0, Math.round(sy)), 1, 1).data, l = d[0] + d[1] + d[2];
          if (l > best) { best = l; bg = `rgb(${d[0]},${d[1]},${d[2]})`; }
        } catch (e) {}
      }
      ctx.fillStyle = bg; ctx.fillRect(bx - 1, by - 1, w + 2, h + 2);
      const px = size * scale * (kind === 'base' ? 1 : 0.68);
      const shift = kind === 'sub' ? 0.2 * size * scale : kind === 'sup' ? -0.38 * size * scale : 0;
      ctx.font = `${px}px Helvetica, Arial, "Liberation Sans", Roboto, sans-serif`;
      ctx.fillStyle = color || '#000'; ctx.textBaseline = 'alphabetic';
      ctx.fillText(ch, bx, (baseline - top) * scale + shift);
    }
  }
  // Tone curve: the sources use thin, mid-grey, non-embedded Helvetica that reads washed
  // out on phones. A gamma curve on the rendered pixels darkens ink and keeps paper white
  // (255 stays 255); colours keep their hue. The CSS contrast/saturate filter still applies.
  const TONE = new Uint8ClampedArray(256).map((_, v) => Math.round(255 * Math.pow(v / 255, 1.7)));
  // Applied in bands that yield to the browser between them, so a 12 MP full-screen render
  // never freezes taps, scrolling or the viewer's animation.
  async function toneCurve(ctx, w, h) {
    const band = Math.max(1, Math.floor(600000 / Math.max(1, w)));
    for (let y = 0; y < h; y += band) {
      const rows = Math.min(band, h - y), img = ctx.getImageData(0, y, w, rows), d = img.data;
      for (let i = 0; i < d.length; i += 4) { d[i] = TONE[d[i]]; d[i + 1] = TONE[d[i + 1]]; d[i + 2] = TONE[d[i + 2]]; }
      ctx.putImageData(img, 0, y);
      if (y + band < h) await new Promise(resolve => setTimeout(resolve, 0));
    }
  }

  function loadDocument(subject) {
    const url = urls[subject];
    if (!url) return Promise.reject(new Error('Anatomy source PDF needs the configured R2 URL.'));
    if (!documents.has(subject)) documents.set(subject, pdfjs.getDocument({url}).promise);
    return documents.get(subject);
  }

  // Render only the authoritative crop. A 12 MP limit bounds each canvas,
  // including unusually tall segments, without changing the source geometry.
  async function raster(node, requestedWidth) {
    const pdf = await loadDocument(node.dataset.subject);
    const page = await pdf.getPage(Number(node.dataset.page));
    const base = page.getViewport({scale:1});
    const top = Math.max(0, Number(node.dataset.top || 0));
    const bottom = Math.min(base.height, Number(node.dataset.bottom || base.height));
    const cropHeight = Math.max(1, bottom-top);
    const scale = Math.min(requestedWidth/base.width, Math.sqrt(12000000/(base.width*cropHeight)));
    const viewport = page.getViewport({scale});
    const canvas = document.createElement('canvas');
    canvas.width = Math.ceil(viewport.width); canvas.height = Math.ceil(cropHeight*scale);
    const ctx = canvas.getContext('2d',{alpha:false,willReadFrequently:true});
    await page.render({canvasContext:ctx,viewport,transform:[1,0,0,1,0,-top*scale]}).promise;
    page.cleanup();
    await repairsReady;
    repairGlyphs(ctx, node.dataset.subject, Number(node.dataset.page), scale, top, bottom);
    await toneCurve(ctx, canvas.width, canvas.height);
    return canvas;
  }
  // Sharp full-screen renders: one in flight per segment, the last two kept (each is up to
  // 12 MP, so a small cache keeps iPad memory in check). No PNG round trip: the viewer
  // shows the canvas itself.
  const sharp = new Map();
  function sharpRaster(node) {
    const key = `${node.dataset.subject}|${node.dataset.page}|${node.dataset.top||0}|${node.dataset.bottom||''}`;
    if (sharp.has(key)) { const hit = sharp.get(key); sharp.delete(key); sharp.set(key, hit); return hit; }
    const job = raster(node, Math.min(3600, Math.max(2400, innerWidth * 3)));
    sharp.set(key, job);
    job.catch(() => sharp.delete(key));
    while (sharp.size > 2) { const [oldKey, oldJob] = sharp.entries().next().value; sharp.delete(oldKey); oldJob.then(c => { if (!c.isConnected) c.width = c.height = 0; }).catch(() => {}); }
    return job;
  }
  async function renderSegment(node) {
    if (!node.isConnected) return;
    const width = Math.max(1,node.clientWidth || 760);
    const density = Math.max(2,Math.min(3,window.devicePixelRatio || 1));
    const target = Math.ceil(width*density);
    if (node.dataset.rendered==='true' && Number(node.dataset.pixelWidth)===target) return;
    node.dataset.rendered='loading';
    try {
      const canvas = await raster(node,target);
      if (!node.isConnected) {canvas.width=canvas.height=0;return;}
      canvas.style.width='100%';canvas.style.height='auto';canvas.style.display='block';
      node.querySelector('canvas').replaceWith(canvas);
      node.querySelector('.nk-web-pdf-status')?.remove();
      node.dataset.rendered='true';node.dataset.pixelWidth=String(target);
      // Geist viewer: open at once from this inline canvas, then swap in a sharper render.
      node.onclick=async()=>{
        if(window.NKViewer&&window.NKViewer.isGeist()){
          const inline=node.querySelector('canvas');
          window.NKViewer.show([{preview:inline,highRes:()=>sharpRaster(node),title:'Original source',subtitle:node.dataset.page?`PDF page ${node.dataset.page}`:'',origin:node}],
            {id:'source-pdf-zoom',className:'source-pdf-zoom',imageClass:'source-pdf-zoomimg',label:`Original source${node.dataset.page?`, PDF page ${node.dataset.page}`:''}`});
          return;
        }
        if(node.dataset.zoomLoading)return;
        node.dataset.zoomLoading='true';node.setAttribute('aria-busy','true');
        try {
          // Fullscreen gets a fresh lossless raster, never the inline thumbnail.
          const high=await raster(node,Math.min(3600,Math.max(2400,innerWidth*3)));
          const blob=await new Promise(resolve=>high.toBlob(resolve,'image/png'));
          high.width=high.height=0;
          const url=URL.createObjectURL(blob), image=new Image();
          image.dataset.sourcePage=node.dataset.page;
          image.onload=()=>{window.openSourceZoom?.(image);setTimeout(()=>URL.revokeObjectURL(url),10000);};
          image.onerror=()=>URL.revokeObjectURL(url);image.src=url;
        } catch(error) {window.QB?.showToast?.('Source zoom unavailable. Please retry.');}
        finally {delete node.dataset.zoomLoading;node.removeAttribute('aria-busy');}
      };
    } catch(error) {
      node.dataset.rendered='error';
      const status=node.querySelector('.nk-web-pdf-status');
      if(status)status.textContent=String(error.message||'Source page unavailable. Tap to retry.');
      node.onclick=()=>{delete node.dataset.rendered;renderQueue=renderQueue.then(()=>renderSegment(node));};
    }
  }
  let resizeTimer;
  const resizeObserver=new ResizeObserver(()=>{
    clearTimeout(resizeTimer);
    resizeTimer=setTimeout(()=>document.querySelectorAll('.nk-web-pdf-segment[data-rendered="true"]').forEach(node=>{
      renderQueue=renderQueue.then(()=>renderSegment(node));
    }),180);
  });

  const observer = new IntersectionObserver(entries => entries.forEach(entry => {
    if (!entry.isIntersecting || entry.target.dataset.rendered) return;
    observer.unobserve(entry.target);
    renderQueue = renderQueue.then(() => renderSegment(entry.target));
  }), {rootMargin: '500px 0px'});
  const tracked=new Set();
  const mount = () => {
    tracked.forEach(node=>{if(!node.isConnected){observer.unobserve(node);resizeObserver.unobserve(node);tracked.delete(node);}});
    document.querySelectorAll('.nk-web-pdf-segment:not([data-observed])').forEach(node => {
    node.dataset.observed = 'true'; tracked.add(node); observer.observe(node); resizeObserver.observe(node);
  });
  };
  new MutationObserver(mount).observe(document.documentElement, {childList:true, subtree:true});
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount); else mount();
}
