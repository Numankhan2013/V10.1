/* NK QBank · page and image viewer (source PDFs in the Geist UI, note images everywhere).
 *
 *   - opens at once from the picture already on screen, then swaps in a sharper render
 *     when one is supplied (the PDF renderer passes its inline canvas + a high-res promise)
 *   - grows out of the tapped element and shrinks back into it; always-dark frosted backdrop
 *   - fit-to-width for reading; pinch, double-tap and ctrl/⌘-wheel zoom anchored at the finger
 *   - panning follows the finger 1:1 and stops firmly at the edges: no rubber band, no bounce,
 *     every edge of the page is reachable; a short glide never runs past an edge
 *   - several items: arrows, ←/→ keys and a sideways swipe at fit move between them
 *   - swipe down at fit to dismiss; tap toggles the chrome; Esc / + / − / 0 on keyboards
 * Source-PDF DOM contract kept: #source-pdf-zoom, .source-pdf-zoomimg, #spz-minus,
 * #spz-reset, #spz-plus, #spz-close. The legacy UI keeps its original source viewer.
 */
(function () {
  'use strict';
  var RM = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : { matches: false };
  var lastSource = null;
  function geist() { return document.documentElement.getAttribute('data-nk-ui') === 'geist'; }

  // Remember what was tapped, so the viewer can grow out of it and shrink back into it.
  document.addEventListener('pointerdown', function (e) {
    var t = e.target && e.target.closest && e.target.closest('.nk-web-pdf-segment, .source-pdf-page, [onclick*="openSourceZoom"], .source-visual-figure, figure');
    if (t) lastSource = t;
  }, true);

  var ICON = {
    x: '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>',
    minus: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 12h12"/></svg>',
    plus: '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 6v12M6 12h12"/></svg>',
    prev: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 6l-6 6 6 6"/></svg>',
    next: '<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 6l6 6-6 6"/></svg>'
  };
  function easeOut(t) { return 1 - Math.pow(1 - t, 3.2); }
  function clampN(v, a, b) { return Math.max(a, Math.min(b, v)); }
  function esc(v) { return String(v == null ? '' : v).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }

  // Turns a source (canvas, image, URL or a promise of one) into a displayable element.
  function materialise(source) {
    return Promise.resolve(typeof source === 'function' ? source() : source).then(function (src) {
      if (!src) throw new Error('No picture');
      if (typeof HTMLCanvasElement !== 'undefined' && src instanceof HTMLCanvasElement) {
        return { el: src, w: src.width, h: src.height };
      }
      var img = src instanceof HTMLImageElement ? src : Object.assign(new Image(), { src: String(src) });
      img.decoding = 'async';
      var ready = img.complete && img.naturalWidth ? Promise.resolve() : (img.decode ? img.decode() : new Promise(function (ok, bad) { img.onload = ok; img.onerror = bad; }));
      return ready.then(function () { return { el: img, w: img.naturalWidth, h: img.naturalHeight }; });
    });
  }
  // The on-screen preview is copied, never moved out of the page.
  function copyCanvas(canvas) {
    var c = document.createElement('canvas'); c.width = canvas.width; c.height = canvas.height;
    c.getContext('2d').drawImage(canvas, 0, 0); return c;
  }

  /* items: [{ preview, highRes?, title?, subtitle?, origin? }]
   *   preview  canvas | img | URL | promise/function of one — shown immediately
   *   highRes  optional function returning a promise of a sharper canvas/img/URL
   *   origin   element the item grows out of and returns to
   * options:   { index, className, id, label, imageClass, onClose } */
  function show(items, options) {
    options = options || {};
    items = (items || []).filter(Boolean); if (!items.length) return null;
    var prior = document.querySelector('.nkv'); if (prior && prior.__nkvClose) prior.__nkvClose(true);
    var index = clampN(Number(options.index) || 0, 0, items.length - 1), many = items.length > 1;
    var root = document.createElement('div');
    if (options.id) root.id = options.id;
    root.className = 'nkv' + (options.className ? ' ' + options.className : '');
    root.setAttribute('role', 'dialog'); root.setAttribute('aria-modal', 'true'); root.tabIndex = -1;
    root.setAttribute('aria-label', options.label || 'Image viewer');
    root.innerHTML =
      '<div class="nkv-backdrop"></div>' +
      '<div class="nkv-stage"><div class="nkv-frame"></div></div>' +
      '<div class="nkv-progress" aria-hidden="true"></div>' +
      '<div class="nkv-top"><div class="nkv-title"><b></b><span class="nkv-sub"></span></div>' +
      (many ? '<span class="nkv-count nk-note-viewer-count" aria-live="polite"></span>' : '') +
      '<button type="button" id="spz-close" class="nkv-btn nkv-close" aria-label="Close">' + ICON.x + '</button></div>' +
      (many ? '<button type="button" class="nkv-nav is-prev" aria-label="Previous image">' + ICON.prev + '</button><button type="button" class="nkv-nav is-next" aria-label="Next image">' + ICON.next + '</button>' : '') +
      '<div class="nkv-bottom" role="group" aria-label="Zoom">' +
      '<button type="button" id="spz-minus" class="nkv-btn" aria-label="Zoom out">' + ICON.minus + '</button>' +
      '<button type="button" id="spz-reset" class="nkv-pct" aria-label="Fit to width">100%</button>' +
      '<button type="button" id="spz-plus" class="nkv-btn" aria-label="Zoom in">' + ICON.plus + '</button></div>';
    var stage = root.querySelector('.nkv-stage'), frame = root.querySelector('.nkv-frame');
    var backdrop = root.querySelector('.nkv-backdrop'), pct = root.querySelector('.nkv-pct');
    var titleEl = root.querySelector('.nkv-title b'), subEl = root.querySelector('.nkv-sub'), countEl = root.querySelector('.nkv-count');
    var prevFocus = document.activeElement, prevOverflow = document.documentElement.style.overflow;
    document.documentElement.style.overflow = 'hidden';
    document.body.appendChild(root);

    var W = 0, H = 0, nw = 1, nh = 1, fit = 1, maxS = 6;
    var s = 1, x = 0, y = 0, anim = 0, closing = false, shown = false, token = 0, el = null, slide = 0;
    function measure() { W = stage.clientWidth; H = stage.clientHeight; }
    function fitState() {
      // Fit to width for reading (capped on wide screens); centre whatever is shorter than the screen.
      var pad = W > 700 ? 48 : 0, room = Math.min(W - pad, 980);
      fit = room / nw;
      if (nw * fit < W * 0.5 && nh * fit > H) fit = Math.min(fit, H / nh); // very tall, narrow items fit the height
      if (!isFinite(fit) || fit <= 0) fit = W / nw;
      maxS = Math.max(fit * 6, 3);
      var w = nw * fit, h = nh * fit;
      return { s: fit, x: (W - w) / 2, y: h < H ? (H - h) / 2 : 0 };
    }
    function bounds(sc) {
      var w = nw * sc, h = nh * sc;
      return { minX: w <= W ? (W - w) / 2 : W - w, maxX: w <= W ? (W - w) / 2 : 0,
               minY: h <= H ? (H - h) / 2 : H - h, maxY: h <= H ? (H - h) / 2 : 0 };
    }
    function clampPos() { var b = bounds(s); x = clampN(x, b.minX, b.maxX); y = clampN(y, b.minY, b.maxY); }
    function paint(extra) {
      frame.style.transform = 'translate3d(' + (x + slide) + 'px,' + y + 'px,0) scale(' + s + ')' + (extra || '');
      pct.textContent = Math.round(s / fit * 100) + '%';
    }
    function tween(to, ms, done) {
      cancelAnimationFrame(anim);
      var from = { s: s, x: x, y: y, slide: slide }, t0 = performance.now(), dur = RM.matches ? 1 : ms;
      var toSlide = to.slide == null ? 0 : to.slide;
      (function step(now) {
        var k = easeOut(clampN((now - t0) / dur, 0, 1));
        s = from.s + (to.s - from.s) * k; x = from.x + (to.x - from.x) * k; y = from.y + (to.y - from.y) * k;
        slide = from.slide + (toSlide - from.slide) * k;
        paint();
        if (k < 1) anim = requestAnimationFrame(step); else if (done) done();
      })(t0);
    }
    function zoomTo(sc, cx, cy, ms) {
      sc = clampN(sc, fit, maxS);
      var ix = (cx - x) / s, iy = (cy - y) / s, b = bounds(sc);
      tween({ s: sc, x: clampN(cx - ix * sc, b.minX, b.maxX), y: clampN(cy - iy * sc, b.minY, b.maxY) }, ms || 300);
    }
    function settle(ms) {
      var sc = clampN(s, fit, maxS);
      if (sc !== s) { zoomTo(sc, W / 2, H / 2, ms); return; }
      var b = bounds(s); tween({ s: s, x: clampN(x, b.minX, b.maxX), y: clampN(y, b.minY, b.maxY) }, ms || 240);
    }
    function originRect() {
      var o = items[index].origin; if (!o || !o.isConnected) return null;
      var r = (o.matches && o.matches('canvas, img') ? o : (o.querySelector('canvas, img') || o)).getBoundingClientRect();
      if (r.width < 8 || r.bottom < 0 || r.top > innerHeight) return null;
      return r;
    }
    function setElement(next, w, h) {
      // Logical size stays the preview's, so a sharper render swaps in without moving.
      next.classList.add('nkv-img'); if (options.imageClass) next.classList.add(options.imageClass);
      next.setAttribute('draggable', 'false');
      if (next.tagName === 'IMG' && !next.alt) next.alt = items[index].title || 'Image';
      next.style.width = nw + 'px'; next.style.height = nh + 'px';
      frame.style.width = nw + 'px'; frame.style.height = nh + 'px';
      if (el && el !== next) { var old = el; frame.replaceChild(next, old); if (old.tagName === 'CANVAS' && old.__nkvCopy) { old.width = old.height = 0; } }
      else if (!el) frame.appendChild(next);
      el = next; root.dataset.quality = w > nw * 1.05 ? 'high' : 'preview';
    }
    function labels() {
      var it = items[index];
      titleEl.textContent = it.title || 'Image';
      subEl.textContent = it.subtitle || ''; subEl.hidden = !it.subtitle;
      if (countEl) countEl.textContent = (index + 1) + ' / ' + items.length;
      root.setAttribute('aria-label', (it.title || 'Image') + (it.subtitle ? ', ' + it.subtitle : ''));
    }
    function load(first) {
      var mine = ++token, it = items[index];
      labels(); root.classList.add('is-loading');
      var preview = it.preview;
      if (typeof HTMLCanvasElement !== 'undefined' && preview instanceof HTMLCanvasElement) { var c = copyCanvas(preview); c.__nkvCopy = true; preview = c; }
      materialise(preview).then(function (pic) {
        if (mine !== token || closing) return;
        nw = pic.w || 1; nh = pic.h || 1; measure();
        if (el) { el.remove(); el = null; }
        setElement(pic.el, pic.w, pic.h);
        var target = fitState(), r = first ? originRect() : null;
        if (first && r) { s = r.width / nw; x = r.left; y = r.top; slide = 0; }
        else if (first) { s = target.s * 0.94; x = target.x + nw * target.s * 0.03; y = target.y + 16; }
        else { s = target.s; x = target.x; y = target.y; }
        paint();
        // A timer, not the tween's callback: a gesture that interrupts the motion must not
        // stop the sharper render from loading.
        var motion = RM.matches ? 1 : first ? 380 : 260;
        var settled = new Promise(function (done) { setTimeout(done, motion + 20); });
        if (first) { root.classList.add('is-open'); shown = true; tween(target, motion, function () { root.focus({ preventScroll: true }); }); }
        else tween({ s: target.s, x: target.x, y: target.y, slide: 0 }, motion);
        if (!it.highRes) { root.classList.remove('is-loading'); return; }
        // The sharper render starts once the opening motion has finished, so it never janks it.
        settled.then(function () { return mine === token && !closing ? materialise(it.highRes) : null; }).then(function (hi) {
          if (mine !== token || closing || !hi || !hi.w) return;
          setElement(hi.el, hi.w, hi.h);
        }).catch(function () {}).then(function () { if (mine === token) root.classList.remove('is-loading'); });
      }).catch(function () {
        if (mine !== token) return;
        root.classList.remove('is-loading'); titleEl.textContent = 'Could not open this picture';
        if (first) { root.classList.add('is-open'); shown = true; }
      });
    }
    function go(step) {
      if (!many || closing) return;
      var dir = step > 0 ? 1 : -1;
      index = (index + dir + items.length) % items.length;
      slide = -dir * Math.min(W * 0.18, 120); load(false);
    }

    function close(immediate) {
      if (closing) return; closing = true; token++;
      cancelAnimationFrame(anim);
      root.classList.remove('is-open'); root.classList.add('is-closing');
      var r = shown && !immediate ? originRect() : null, done = function () {
        if (el && el.__nkvCopy) { el.width = el.height = 0; }
        root.remove(); document.documentElement.style.overflow = prevOverflow;
        document.removeEventListener('keydown', onKey, true); window.removeEventListener('resize', onResize);
        if (!immediate && prevFocus && prevFocus.focus) try { prevFocus.focus({ preventScroll: true }); } catch (e) {}
        if (typeof options.onClose === 'function') options.onClose();
      };
      if (immediate) done();
      else if (r) tween({ s: r.width / nw, x: r.left, y: r.top }, 280, done);
      else { frame.style.transition = 'opacity 180ms ease'; frame.style.opacity = '0'; setTimeout(done, RM.matches ? 0 : 180); }
    }
    root.__nkvClose = close;

    // ---------- controls ----------
    root.querySelector('#spz-close').onclick = function () { close(); };
    root.querySelector('#spz-reset').onclick = function () { tween(fitState(), 300); };
    root.querySelector('#spz-plus').onclick = function () { zoomTo(s * 1.5, W / 2, H / 2); };
    root.querySelector('#spz-minus').onclick = function () { zoomTo(s / 1.5, W / 2, H / 2); };
    if (many) {
      root.querySelector('.nkv-nav.is-prev').onclick = function () { go(-1); };
      root.querySelector('.nkv-nav.is-next').onclick = function () { go(1); };
    }
    function onKey(e) {
      var k = e.key;
      if (k === 'Escape') close();
      else if (k === '+' || k === '=') zoomTo(s * 1.5, W / 2, H / 2);
      else if (k === '-') zoomTo(s / 1.5, W / 2, H / 2);
      else if (k === '0') tween(fitState(), 300);
      else if (k === 'ArrowRight' && many) go(1);
      else if (k === 'ArrowLeft' && many) go(-1);
      else return;
      // The page underneath also listens for these keys; the open viewer owns them.
      e.preventDefault(); e.stopPropagation();
    }
    document.addEventListener('keydown', onKey, true);
    function onResize() { if (!shown) return; measure(); var at = s / fit; fitState(); s = fit * at; clampPos(); paint(); }
    window.addEventListener('resize', onResize);

    // ---------- gestures ----------
    var pts = new Map(), g = null, lastTap = 0, tapTimer = 0, track = [];
    function atFit() { return Math.abs(s - fit) < fit * 0.02; }
    stage.addEventListener('pointerdown', function (e) {
      if (closing || !shown) return;
      e.preventDefault(); if (stage.setPointerCapture) stage.setPointerCapture(e.pointerId);
      cancelAnimationFrame(anim);
      pts.set(e.pointerId, { x: e.clientX, y: e.clientY });
      var a = Array.from(pts.values());
      if (a.length === 1) {
        g = { mode: 'pan', sx: e.clientX, sy: e.clientY, ox: x, oy: y, moved: false };
        track = [{ x: e.clientX, y: e.clientY, t: performance.now() }];
      } else if (a.length === 2) {
        var d = Math.hypot(a[0].x - a[1].x, a[0].y - a[1].y), mx = (a[0].x + a[1].x) / 2, my = (a[0].y + a[1].y) / 2;
        slide = 0; g = { mode: 'pinch', d: d || 1, s: s, ix: (mx - x) / s, iy: (my - y) / s, moved: true };
      }
    });
    stage.addEventListener('pointermove', function (e) {
      if (!pts.has(e.pointerId) || !g) return;
      pts.set(e.pointerId, { x: e.clientX, y: e.clientY });
      var a = Array.from(pts.values());
      if (g.mode === 'pinch' && a.length >= 2) {
        var d = Math.hypot(a[0].x - a[1].x, a[0].y - a[1].y), mx = (a[0].x + a[1].x) / 2, my = (a[0].y + a[1].y) / 2;
        var raw = g.s * d / g.d;
        s = raw < fit ? fit - (fit - raw) * 0.35 : Math.min(raw, maxS * 1.15);
        x = mx - g.ix * s; y = my - g.iy * s; paint(); return;
      }
      var dx = e.clientX - g.sx, dy = e.clientY - g.sy;
      if (!g.moved && Math.hypot(dx, dy) > 6) {
        g.moved = true;
        var b0 = bounds(s), fitsV = b0.minY === b0.maxY, fitsH = b0.minX === b0.maxX;
        // At fit: a downward drag dismisses, a sideways drag changes item.
        if (atFit() && fitsV && dy > 0 && Math.abs(dy) > Math.abs(dx) * 1.2) g.mode = 'dismiss';
        else if (many && atFit() && fitsH && Math.abs(dx) > Math.abs(dy) * 1.2) g.mode = 'swipe';
      }
      track.push({ x: e.clientX, y: e.clientY, t: performance.now() }); if (track.length > 6) track.shift();
      if (g.mode === 'dismiss') {
        var p = clampN(dy / 360, 0, 1);
        backdrop.style.opacity = String(1 - p * 0.85); root.classList.add('is-dragging');
        x = g.ox + dx * 0.4; y = g.oy + dy; paint(' scale(' + (1 - p * 0.18) + ')'); return;
      }
      if (g.mode === 'swipe') { slide = dx; paint(); return; }
      // Panning follows the finger and stops firmly at every edge.
      var b = bounds(s); x = clampN(g.ox + dx, b.minX, b.maxX); y = clampN(g.oy + dy, b.minY, b.maxY);
      if (x !== g.ox + dx) g.ox = x - dx; if (y !== g.oy + dy) g.oy = y - dy; // reversing direction responds at once
      paint();
    });
    function up(e) {
      if (!pts.has(e.pointerId)) return;
      pts.delete(e.pointerId);
      if (!g) return;
      if (g.mode === 'pinch') {
        if (pts.size === 1) { var r = Array.from(pts.values())[0]; g = { mode: 'pan', sx: r.x, sy: r.y, ox: x, oy: y, moved: true }; track = []; return; }
        g = null; settle(240); return;
      }
      if (pts.size) return;
      var vx = 0, vy = 0;
      if (track.length > 1) { var f = track[0], l = track[track.length - 1], dt = Math.max(16, l.t - f.t); if (performance.now() - l.t < 90) { vx = (l.x - f.x) / dt; vy = (l.y - f.y) / dt; } }
      if (g.mode === 'dismiss') {
        root.classList.remove('is-dragging');
        if (e.clientY - g.sy > 110 || vy > 0.7) { backdrop.style.transition = 'opacity 240ms ease'; backdrop.style.opacity = '0'; g = null; close(); return; }
        backdrop.style.transition = 'opacity 220ms ease'; backdrop.style.opacity = ''; setTimeout(function () { backdrop.style.transition = ''; }, 240);
        g = null; tween(fitState(), 260); return;
      }
      if (g.mode === 'swipe') {
        var dxs = e.clientX - g.sx; g = null;
        if (Math.abs(dxs) > W * 0.18 || Math.abs(vx) > 0.5) go(dxs < 0 ? 1 : -1);
        else tween({ s: s, x: x, y: y, slide: 0 }, 220);
        return;
      }
      if (!g.moved) {
        var now = performance.now(), tx = e.clientX, ty = e.clientY;
        if (now - lastTap < 300) {               // double tap: fit <-> 2.5x at the finger
          clearTimeout(tapTimer); lastTap = 0;
          if (s > fit * 1.15) tween(fitState(), 300); else zoomTo(fit * 2.5, tx, ty, 320);
        } else {
          lastTap = now;
          tapTimer = setTimeout(function () { root.classList.toggle('is-chrome-hidden'); }, 300);
        }
        g = null; return;
      }
      g = null;
      // A short glide in the flick direction that stops at the edge instead of bouncing.
      if (Math.hypot(vx, vy) > 0.3 && !RM.matches) {
        var last = performance.now(), t0 = last;
        (function glide(now) {
          var dt = now - last; last = now;
          vx *= Math.pow(0.9, dt / 16); vy *= Math.pow(0.9, dt / 16);
          var b = bounds(s), nx = x + vx * dt, ny = y + vy * dt;
          x = clampN(nx, b.minX, b.maxX); y = clampN(ny, b.minY, b.maxY);
          if (x !== nx) vx = 0; if (y !== ny) vy = 0;
          paint();
          if (Math.hypot(vx, vy) > 0.03 && now - t0 < 700) anim = requestAnimationFrame(glide);
        })(last);
      }
    }
    stage.addEventListener('pointerup', up); stage.addEventListener('pointercancel', up);
    stage.addEventListener('wheel', function (e) {
      if (!shown) return;
      e.preventDefault(); cancelAnimationFrame(anim);
      if (e.ctrlKey || e.metaKey) {                 // trackpad pinch / ctrl+wheel
        var sc = clampN(s * Math.exp(-e.deltaY * 0.01), fit, maxS), ix = (e.clientX - x) / s, iy = (e.clientY - y) / s;
        s = sc; x = e.clientX - ix * s; y = e.clientY - iy * s;
      } else { x -= e.deltaX; y -= e.deltaY; }
      clampPos(); paint();
    }, { passive: false });
    backdrop.addEventListener('click', function () { close(); });

    load(true);
    return { close: close };
  }

  // Source PDFs: window.openSourceZoom(img) in the Geist UI opens this viewer.
  function open(src) {
    if (!src) return;
    var page = String((src.dataset && src.dataset.sourcePage) || '');
    var origin = lastSource && lastSource.isConnected ? lastSource : null;
    return show([{ preview: src, title: 'Original source', subtitle: page ? 'PDF page ' + page : '', origin: origin }],
      { id: 'source-pdf-zoom', className: 'source-pdf-zoom', imageClass: 'source-pdf-zoomimg', label: 'Original source' + (page ? ', PDF page ' + page : '') });
  }

  // Take over openSourceZoom in the Geist UI only; later assignments by the app are kept
  // as the fallback for the legacy UI.
  var fallback = window.openSourceZoom;
  try {
    Object.defineProperty(window, 'openSourceZoom', {
      configurable: true,
      get: function () { return geist() ? open : fallback; },
      set: function (v) { fallback = v; }
    });
  } catch (e) { if (geist()) window.openSourceZoom = open; }
  window.NKViewer = { open: open, show: show, isGeist: geist, escape: esc };
})();
