/* NK QBank · source page viewer (redesign layer only).
 *
 * Replaces window.openSourceZoom in the Geist UI with a photo-viewer style surface:
 *   - opens from the tapped page (shared-element zoom) and closes back into it
 *   - always-dark backdrop regardless of theme (paper reads best on dark), soft blur
 *   - fit-to-width start; pinch, double-tap and wheel/ctrl zoom anchored at the finger
 *   - pan with momentum; edges rubber-band and spring back (the page never drifts away)
 *   - swipe down to dismiss at fit; tap toggles the chrome; Esc / + / − / 0 on keyboards
 * The legacy UI (and its tests) keep the original viewer. DOM contract kept:
 * #source-pdf-zoom, img.source-pdf-zoomimg, #spz-minus, #spz-reset, #spz-plus, #spz-close.
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

  var ICON_X = '<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>';
  var ICON_MINUS = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 12h12"/></svg>';
  var ICON_PLUS = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M12 6v12M6 12h12"/></svg>';

  function easeOut(t) { return 1 - Math.pow(1 - t, 3.2); }
  function clampN(v, a, b) { return Math.max(a, Math.min(b, v)); }

  function open(src) {
    if (!src) return;
    var old = document.getElementById('source-pdf-zoom'); if (old) old.remove();
    var page = String((src.dataset && src.dataset.sourcePage) || '');
    var root = document.createElement('div');
    root.id = 'source-pdf-zoom'; root.className = 'source-pdf-zoom nkv';
    root.setAttribute('role', 'dialog'); root.setAttribute('aria-modal', 'true'); root.tabIndex = -1;
    root.setAttribute('aria-label', 'Original source' + (page ? ', PDF page ' + page : ''));
    root.innerHTML =
      '<div class="nkv-backdrop"></div>' +
      '<div class="nkv-stage"><img class="source-pdf-zoomimg nkv-img" alt="Original source" draggable="false"></div>' +
      '<div class="nkv-top"><div class="nkv-title"><b>Original source</b>' + (page ? '<span>PDF page ' + page + '</span>' : '') + '</div>' +
      '<button type="button" id="spz-close" class="nkv-btn" aria-label="Close">' + ICON_X + '</button></div>' +
      '<div class="nkv-bottom" role="group" aria-label="Zoom">' +
      '<button type="button" id="spz-minus" class="nkv-btn" aria-label="Zoom out">' + ICON_MINUS + '</button>' +
      '<button type="button" id="spz-reset" class="nkv-pct" aria-label="Fit to width">100%</button>' +
      '<button type="button" id="spz-plus" class="nkv-btn" aria-label="Zoom in">' + ICON_PLUS + '</button></div>';
    var stage = root.querySelector('.nkv-stage'), img = root.querySelector('.nkv-img');
    var backdrop = root.querySelector('.nkv-backdrop'), pct = root.querySelector('.nkv-pct');
    var prevFocus = document.activeElement, prevOverflow = document.documentElement.style.overflow;
    var origin = lastSource && lastSource.isConnected ? lastSource : null;
    document.documentElement.style.overflow = 'hidden';
    document.body.appendChild(root);

    var W = 0, H = 0, nw = 1, nh = 1, fit = 1, minS = 1, maxS = 6;
    var s = 1, x = 0, y = 0, anim = 0, closing = false;
    function measure() { W = stage.clientWidth; H = stage.clientHeight; }
    function fitState() {
      // Fit to width (a document is read across), centred vertically when shorter than the screen.
      var pad = W > 700 ? 48 : 0;
      fit = Math.min((W - pad) / nw, W > 700 ? (H - 120) / nh : Infinity);
      if (!isFinite(fit) || fit <= 0) fit = W / nw;
      minS = Math.min(fit, H / nh) * 0.9; maxS = Math.max(fit * 6, 3);
      var w = nw * fit, h = nh * fit;
      return { s: fit, x: (W - w) / 2, y: h < H ? (H - h) / 2 : 0 };
    }
    function bounds(sc) {
      var w = nw * sc, h = nh * sc;
      return { minX: w <= W ? (W - w) / 2 : W - w, maxX: w <= W ? (W - w) / 2 : 0,
               minY: h <= H ? (H - h) / 2 : H - h, maxY: h <= H ? (H - h) / 2 : 0 };
    }
    function rubber(v, lo, hi) {
      if (v < lo) return lo - Math.pow(lo - v, 0.82) * 0.55;
      if (v > hi) return hi + Math.pow(v - hi, 0.82) * 0.55;
      return v;
    }
    function paint(extra) {
      img.style.transform = 'translate3d(' + x + 'px,' + y + 'px,0) scale(' + s + ')' + (extra || '');
      pct.textContent = Math.round(s / fit * 100) + '%';
    }
    function tween(to, ms, done) {
      cancelAnimationFrame(anim);
      var from = { s: s, x: x, y: y }, t0 = performance.now(), dur = RM.matches ? 1 : ms;
      (function step(now) {
        var k = easeOut(clampN((now - t0) / dur, 0, 1));
        s = from.s + (to.s - from.s) * k; x = from.x + (to.x - from.x) * k; y = from.y + (to.y - from.y) * k;
        paint();
        if (k < 1) anim = requestAnimationFrame(step); else if (done) done();
      })(t0);
    }
    function settle(ms) {
      var sc = clampN(s, fit, maxS), b = bounds(sc);
      var cx = W / 2, cy = H / 2, ix = (cx - x) / s, iy = (cy - y) / s;
      var nx = s === sc ? x : cx - ix * sc, ny = s === sc ? y : cy - iy * sc;
      tween({ s: sc, x: clampN(nx, b.minX, b.maxX), y: clampN(ny, b.minY, b.maxY) }, ms || 320);
    }
    function zoomTo(sc, cx, cy, ms) {
      sc = clampN(sc, fit, maxS);
      var ix = (cx - x) / s, iy = (cy - y) / s, b = bounds(sc);
      tween({ s: sc, x: clampN(cx - ix * sc, b.minX, b.maxX), y: clampN(cy - iy * sc, b.minY, b.maxY) }, ms || 300);
    }
    function sourceRect() {
      if (!origin || !origin.isConnected) return null;
      var r = (origin.querySelector('canvas, img') || origin).getBoundingClientRect();
      if (r.width < 8 || r.bottom < 0 || r.top > innerHeight) return null;
      return r;
    }

    function start() {
      nw = img.naturalWidth || 1; nh = img.naturalHeight || 1; measure();
      var target = fitState(), r = sourceRect();
      if (r) { s = r.width / nw; x = r.left; y = r.top; } else { s = target.s * 0.94; x = target.x + nw * target.s * 0.03; y = target.y + 16; }
      paint();
      root.classList.add('is-open');
      tween(target, 420, function () { root.focus({ preventScroll: true }); });
    }
    img.addEventListener('load', start, { once: true });
    img.src = src.src;

    function close() {
      if (closing) return; closing = true;
      cancelAnimationFrame(anim);
      root.classList.remove('is-open'); root.classList.add('is-closing');
      var r = sourceRect(), done = function () {
        root.remove(); document.documentElement.style.overflow = prevOverflow;
        document.removeEventListener('keydown', onKey, true); window.removeEventListener('resize', onResize);
        if (prevFocus && prevFocus.focus) try { prevFocus.focus({ preventScroll: true }); } catch (e) {}
      };
      if (r) tween({ s: r.width / nw, x: r.left, y: r.top }, 300, done);
      else { img.style.transition = 'opacity 200ms ease'; img.style.opacity = '0'; setTimeout(done, RM.matches ? 0 : 200); }
    }

    // ---------- controls ----------
    root.querySelector('#spz-close').onclick = close;
    root.querySelector('#spz-reset').onclick = function () { tween(fitState(), 300); };
    root.querySelector('#spz-plus').onclick = function () { zoomTo(s * 1.5, W / 2, H / 2); };
    root.querySelector('#spz-minus').onclick = function () { zoomTo(s / 1.5, W / 2, H / 2); };
    function onKey(e) {
      if (e.key === 'Escape') { e.preventDefault(); e.stopPropagation(); close(); }
      else if (e.key === '+' || e.key === '=') zoomTo(s * 1.5, W / 2, H / 2);
      else if (e.key === '-') zoomTo(s / 1.5, W / 2, H / 2);
      else if (e.key === '0') tween(fitState(), 300);
    }
    document.addEventListener('keydown', onKey, true);
    function onResize() { measure(); var at = s / fit; fitState(); s = fit * at; settle(1); }
    window.addEventListener('resize', onResize);

    // ---------- gestures ----------
    var pts = new Map(), g = null, lastTap = 0, tapTimer = 0, track = [];
    stage.addEventListener('pointerdown', function (e) {
      if (closing) return;
      e.preventDefault(); stage.setPointerCapture && stage.setPointerCapture(e.pointerId);
      cancelAnimationFrame(anim);
      pts.set(e.pointerId, { x: e.clientX, y: e.clientY });
      var a = Array.from(pts.values());
      if (a.length === 1) {
        g = { mode: 'pan', sx: e.clientX, sy: e.clientY, ox: x, oy: y, moved: false, t: performance.now() };
        track = [{ x: e.clientX, y: e.clientY, t: performance.now() }];
      } else if (a.length === 2) {
        var d = Math.hypot(a[0].x - a[1].x, a[0].y - a[1].y), mx = (a[0].x + a[1].x) / 2, my = (a[0].y + a[1].y) / 2;
        g = { mode: 'pinch', d: d, s: s, ix: (mx - x) / s, iy: (my - y) / s, moved: true };
      }
    });
    stage.addEventListener('pointermove', function (e) {
      if (!pts.has(e.pointerId) || !g) return;
      pts.set(e.pointerId, { x: e.clientX, y: e.clientY });
      var a = Array.from(pts.values());
      if (g.mode === 'pinch' && a.length >= 2) {
        var d = Math.hypot(a[0].x - a[1].x, a[0].y - a[1].y), mx = (a[0].x + a[1].x) / 2, my = (a[0].y + a[1].y) / 2;
        var raw = g.s * d / g.d;
        s = raw < fit ? fit - Math.pow(fit - raw, 0.9) * 0.5 : raw > maxS ? maxS + (raw - maxS) * 0.3 : raw;
        x = mx - g.ix * s; y = my - g.iy * s; paint(); return;
      }
      if (g.mode !== 'pan' && g.mode !== 'dismiss') return;
      var dx = e.clientX - g.sx, dy = e.clientY - g.sy;
      if (!g.moved && Math.hypot(dx, dy) > 6) {
        g.moved = true;
        // At fit, a mostly-vertical downward drag dismisses instead of panning.
        if (Math.abs(s - fit) < fit * 0.02 && dy > 0 && Math.abs(dy) > Math.abs(dx) * 1.2 && bounds(s).minY === bounds(s).maxY) g.mode = 'dismiss';
      }
      track.push({ x: e.clientX, y: e.clientY, t: performance.now() }); if (track.length > 6) track.shift();
      if (g.mode === 'dismiss') {
        var p = clampN(dy / 360, 0, 1);
        backdrop.style.opacity = String(1 - p * 0.85);
        root.classList.toggle('is-dragging', true);
        x = g.ox + dx * 0.4; y = g.oy + dy; paint(' scale(' + (1 - p * 0.18) + ')');
        return;
      }
      var b = bounds(s);
      x = rubber(g.ox + dx, b.minX, b.maxX); y = rubber(g.oy + dy, b.minY, b.maxY); paint();
    });
    function up(e) {
      if (!pts.has(e.pointerId)) return;
      pts.delete(e.pointerId);
      if (!g) return;
      if (g.mode === 'pinch') {
        if (pts.size === 1) { var r = Array.from(pts.values())[0]; g = { mode: 'pan', sx: r.x, sy: r.y, ox: x, oy: y, moved: true }; track = []; return; }
        g = null; settle(260); return;
      }
      if (pts.size) return;
      var vx = 0, vy = 0;
      if (track.length > 1) { var f = track[0], l = track[track.length - 1], dt = Math.max(16, l.t - f.t); vx = (l.x - f.x) / dt; vy = (l.y - f.y) / dt; }
      if (g.mode === 'dismiss') {
        root.classList.remove('is-dragging');
        if (e.clientY - g.sy > 110 || vy > 0.7) { backdrop.style.transition = 'opacity 260ms ease'; backdrop.style.opacity = '0'; g = null; close(); return; }
        backdrop.style.transition = 'opacity 220ms ease'; backdrop.style.opacity = ''; setTimeout(function () { backdrop.style.transition = ''; }, 240);
        g = null; tween(fitState(), 280); return;
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
      // Momentum, then settle inside the edges.
      if (Math.hypot(vx, vy) > 0.25 && !RM.matches) {
        var t0 = performance.now(), last = t0;
        cancelAnimationFrame(anim);
        (function glide(now) {
          var dt = now - last; last = now;
          vx *= Math.pow(0.94, dt / 16); vy *= Math.pow(0.94, dt / 16);
          var b = bounds(s); x += vx * dt; y += vy * dt;
          if (x < b.minX || x > b.maxX) vx *= 0.5;
          if (y < b.minY || y > b.maxY) vy *= 0.5;
          paint();
          if (Math.hypot(vx, vy) > 0.02 && now - t0 < 1400) anim = requestAnimationFrame(glide); else settle(300);
        })(t0);
      } else settle(300);
    }
    stage.addEventListener('pointerup', up); stage.addEventListener('pointercancel', up);
    stage.addEventListener('wheel', function (e) {
      e.preventDefault(); cancelAnimationFrame(anim);
      if (e.ctrlKey || e.metaKey) {                 // trackpad pinch / ctrl+wheel
        var sc = clampN(s * Math.exp(-e.deltaY * 0.01), fit, maxS), ix = (e.clientX - x) / s, iy = (e.clientY - y) / s;
        s = sc; x = e.clientX - ix * s; y = e.clientY - iy * s;
      } else { x -= e.deltaX; y -= e.deltaY; }
      var b = bounds(s); x = clampN(x, b.minX, b.maxX); y = clampN(y, b.minY, b.maxY); paint();
    }, { passive: false });
    backdrop.addEventListener('click', close);
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
  window.NKViewer = { open: open };
})();
