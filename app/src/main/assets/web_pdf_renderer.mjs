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

  async function renderSegment(node) {
    if (node.dataset.rendered) return;
    node.dataset.rendered = 'loading';
    const subject = node.dataset.subject;
    try {
      const document = await loadDocument(subject);
      const page = await document.getPage(Number(node.dataset.page));
      const base = page.getViewport({scale: 1});
      const cssWidth = Math.max(280, Math.min(1180, node.clientWidth || 760));
      const density = Math.min(2, window.devicePixelRatio || 1);
      const scale = cssWidth / base.width * density;
      const viewport = page.getViewport({scale});
      const full = document.createElement('canvas');
      full.width = Math.ceil(viewport.width); full.height = Math.ceil(viewport.height);
      await page.render({canvasContext: full.getContext('2d', {alpha:false}), viewport}).promise;
      const top = node.dataset.top ? Math.max(0, Number(node.dataset.top) * scale) : 0;
      const bottom = node.dataset.bottom ? Math.min(full.height, Number(node.dataset.bottom) * scale) : full.height;
      const height = Math.max(1, Math.ceil(bottom - top));
      const canvas = node.querySelector('canvas');
      canvas.width = full.width; canvas.height = height;
      canvas.style.width = `${cssWidth}px`; canvas.style.height = `${height / density}px`;
      canvas.getContext('2d', {alpha:false}).drawImage(full, 0, top, full.width, height, 0, 0, full.width, height);
      node.querySelector('.nk-web-pdf-status')?.remove();
      node.dataset.rendered = 'true';
      node.onclick = () => {
        const image = new Image(); image.src = canvas.toDataURL('image/jpeg', .94); image.dataset.sourcePage = node.dataset.page;
        image.onload = () => window.openSourceZoom?.(image);
      };
      page.cleanup();
    } catch (error) {
      node.dataset.rendered = 'error';
      const status = node.querySelector('.nk-web-pdf-status');
      if (status) status.textContent = String(error.message || 'Source page unavailable.');
    }
  }

  const observer = new IntersectionObserver(entries => entries.forEach(entry => {
    if (!entry.isIntersecting || entry.target.dataset.rendered) return;
    observer.unobserve(entry.target);
    renderQueue = renderQueue.then(() => renderSegment(entry.target));
  }), {rootMargin: '500px 0px'});
  const mount = () => document.querySelectorAll('.nk-web-pdf-segment:not([data-observed])').forEach(node => {
    node.dataset.observed = 'true'; observer.observe(node);
  });
  new MutationObserver(mount).observe(document.documentElement, {childList:true, subtree:true});
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount); else mount();
}
