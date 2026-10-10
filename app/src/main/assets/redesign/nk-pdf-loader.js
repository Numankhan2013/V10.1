/* NK QBank — source-solution loading layer (presentation only).
 *
 * Watches the original-PDF solution pages that are on screen (web: PDF.js canvas
 * segments, Android: qbank.local <img> pages). While any visible page is still
 * rendering it shows
 *   1. an inline skeleton shimmer in each pending page, and
 *   2. a floating "Rendering solution" pill at the bottom with live progress,
 *      which turns into a check and slides away when everything is in.
 * Pages reveal with a short blur-to-sharp fade. No rendering logic is touched:
 * this file only reads state the renderers already expose (data-rendered,
 * img.complete) and adds classes. Honours prefers-reduced-motion.
 */
(function () {
  'use strict';
  if (window.__nkPdfLoader) return;
  window.__nkPdfLoader = true;

  var SHOW_DELAY = 220;   // ms: fast renders never flash the pill
  var MIN_VISIBLE = 520;  // ms: once shown, stay long enough to read
  var DONE_HOLD = 700;    // ms: how long the check stays before exit
  var PAGE_SEL = '.source-pdf-page';

  var visible = new Set();          // pages intersecting the viewport (+margin)
  var pill = null, bar = null, label = null, count = null;
  var state = 'idle';               // idle | waiting | shown | done
  var showTimer = 0, hideTimer = 0, shownAt = 0;
  var raf = 0;

  function isPending(node) {
    if (!node.isConnected) return false;
    if (node.classList.contains('nk-web-pdf-segment')) {
      var r = node.dataset.rendered;
      return r !== 'true' && r !== 'error';
    }
    var img = node.querySelector('img');
    return !!img && !(img.complete && img.naturalWidth > 0) && !img.dataset.nkPdlFailed;
  }

  /* ---------- pill ---------- */
  function buildPill() {
    pill = document.createElement('div');
    pill.className = 'nk-pdl-pill';
    pill.setAttribute('role', 'status');
    pill.setAttribute('aria-live', 'polite');
    pill.innerHTML =
      '<span class="nk-pdl-glyph" aria-hidden="true">' +
        '<svg viewBox="0 0 20 20" width="20" height="20">' +
          '<path class="nk-pdl-doc" d="M5.5 2.75h6.2l3.55 3.55v10.2a.75.75 0 0 1-.75.75H5.5a.75.75 0 0 1-.75-.75V3.5a.75.75 0 0 1 .75-.75Z"/>' +
          '<path class="nk-pdl-fold" d="M11.5 2.9v3.6h3.6"/>' +
          '<path class="nk-pdl-line l1" d="M7.25 9.5h5.5"/>' +
          '<path class="nk-pdl-line l2" d="M7.25 12h5.5"/>' +
          '<path class="nk-pdl-line l3" d="M7.25 14.5h3.25"/>' +
          '<path class="nk-pdl-check" d="M6.4 10.6l2.5 2.5 4.8-5.1"/>' +
        '</svg>' +
        '<span class="nk-pdl-scan"></span>' +
      '</span>' +
      '<span class="nk-pdl-text">' +
        '<span class="nk-pdl-label">Rendering solution</span>' +
        '<span class="nk-pdl-count"></span>' +
      '</span>' +
      '<span class="nk-pdl-track" aria-hidden="true"><span class="nk-pdl-bar"></span></span>';
    document.body.appendChild(pill);
    bar = pill.querySelector('.nk-pdl-bar');
    label = pill.querySelector('.nk-pdl-label');
    count = pill.querySelector('.nk-pdl-count');
  }

  function navOffset() {
    var nav = document.querySelector('.bottom-nav, .nkg-bottom-nav, nav.bottom-nav');
    if (!nav) return 0;
    var cs = getComputedStyle(nav);
    if (cs.display === 'none' || cs.visibility === 'hidden' || cs.position !== 'fixed') return 0;
    var r = nav.getBoundingClientRect();
    return r.height > 0 && r.top < innerHeight ? Math.max(0, innerHeight - r.top) : 0;
  }

  /* The pill sits in the middle of the page skeleton that is loading (first visible one),
     not over the bottom controls. It moves to the next loading page as each one lands. */
  function placePill() {
    if (!pill) return;
    var host = null;
    seen.forEach(function (n) { if (!host && n.isConnected && isPending(n)) host = n; });
    if (host && pill.parentNode !== host) host.appendChild(pill);
    else if (!pill.isConnected) document.body.appendChild(pill);
  }

  function show() {
    if (!pill) buildPill();
    placePill();
    clearTimeout(hideTimer);
    pill.style.setProperty('--nk-pdl-offset', navOffset() + 'px');
    pill.classList.remove('is-done', 'is-leaving');
    label.textContent = 'Rendering solution';
    void pill.offsetWidth;
    pill.classList.add('is-in');
    state = 'shown';
    shownAt = performance.now();
  }

  function finish() {
    if (state === 'waiting') { clearTimeout(showTimer); reset(); return; }
    if (state !== 'shown') return;
    var wait = Math.max(0, MIN_VISIBLE - (performance.now() - shownAt));
    state = 'done';
    hideTimer = setTimeout(function () {
      if (state !== 'done') return;
      pill.classList.add('is-done');
      label.textContent = 'Solution ready';
      count.textContent = '';
      hideTimer = setTimeout(function () {
        if (state !== 'done') return;
        pill.classList.add('is-leaving');
        pill.classList.remove('is-in');
        hideTimer = setTimeout(function () { if (state === 'done') { pill.classList.remove('is-done', 'is-leaving'); reset(); } }, 420);
      }, DONE_HOLD);
    }, wait);
  }

  function reset() { state = 'idle'; seen.clear(); }

  function paint(pending, total) {
    if (!pill) return;
    if (pending > 0) placePill();
    var done = Math.max(0, total - pending);
    count.textContent = total > 1 ? done + '/' + total : '';
    bar.style.transform = 'scaleX(' + (total ? Math.max(0.08, done / total) : 0.08).toFixed(3) + ')';
    pill.classList.toggle('is-multi', total > 1);
  }

  /* ---------- evaluation ---------- */
  var seen = new Set();   // pages that were pending on screen in this batch
  function evaluate() {
    raf = 0;
    document.querySelectorAll(PAGE_SEL).forEach(function (node) {
      var p = isPending(node);
      if (p) {
        if (!node.classList.contains('nk-pdl-pending')) node.classList.add('nk-pdl-pending');
        if (visible.has(node)) seen.add(node);
      } else if (node.classList.contains('nk-pdl-pending')) {
        node.classList.remove('nk-pdl-pending');
        node.classList.add('nk-pdl-reveal');
        setTimeout(function () { node.classList.remove('nk-pdl-reveal'); }, 600);
      }
    });
    // Pages from a question the user already left no longer count.
    seen.forEach(function (n) { if (!n.isConnected) seen.delete(n); });
    var pending = 0;
    seen.forEach(function (n) { if (isPending(n)) pending++; });
    var total = seen.size;

    if (pending > 0) {
      if (state === 'idle') {
        state = 'waiting'; clearTimeout(showTimer);
        showTimer = setTimeout(function () { if (state === 'waiting') { show(); evaluate(); } }, SHOW_DELAY);
      } else if (state === 'done') {
        clearTimeout(hideTimer);       // new pages arrived mid-exit: stay up
        show();
      }
      paint(pending, total);
    } else {
      if (state === 'waiting' || state === 'shown') { paint(0, total || 1); finish(); }
      if (state === 'idle' || state === 'done') seen.clear();
    }
  }
  function schedule() { if (!raf) raf = requestAnimationFrame(evaluate); }

  /* ---------- observers ---------- */
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) { if (e.isIntersecting) visible.add(e.target); else visible.delete(e.target); });
    schedule();
  }, { rootMargin: '0px 0px 120px 0px' });

  var tracked = new WeakSet();
  function track() {
    visible.forEach(function (n) { if (!n.isConnected) visible.delete(n); });
    document.querySelectorAll(PAGE_SEL).forEach(function (node) {
      if (tracked.has(node)) return;
      tracked.add(node);
      io.observe(node);
      var img = node.querySelector('img');
      if (img) {
        img.addEventListener('load', schedule);
        img.addEventListener('error', function () { img.dataset.nkPdlFailed = '1'; schedule(); });
      }
    });
    schedule();
  }

  function start() {
    new MutationObserver(function (records) {
      for (var i = 0; i < records.length; i++) {
        var r = records[i];
        if (r.type === 'attributes' || r.addedNodes.length || r.removedNodes.length) { track(); return; }
      }
    }).observe(document.body, { childList: true, subtree: true, attributes: true, attributeFilter: ['data-rendered'] });
    track();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
