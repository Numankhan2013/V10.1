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
    await page.render({canvasContext:canvas.getContext('2d',{alpha:false}),viewport,transform:[1,0,0,1,0,-top*scale]}).promise;
    page.cleanup();
    return canvas;
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
      node.onclick=async()=>{
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
