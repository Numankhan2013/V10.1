/* NK QBank — Geist interaction layer ("feel").
 *
 * Presentation only. Runs after nk-redesign.js; nk-redesign's render observer
 * calls NKFeel.render(app, page) after every app render. Every enhancement is
 * idempotent: the app re-renders by replacing markup, so each pass upgrades the
 * fresh DOM and remembers just enough (pill positions, data signatures) to
 * animate *changes* instead of replaying entrances.
 *
 * Libraries (vendored, offline):
 *   Motion 12.23.12 (motion.dev, MIT)  — springs, keyframes, number tweens, inView.
 *   ios-haptics technique (tijn.dev, MIT) — the iOS 18 Safari switch-input haptic.
 * Haptics prefer the native Android bridge (window.QBankHaptics), then the
 * Vibration API, then the iOS switch technique.
 *
 * Study logic is never touched: controls drive the app's own selects/buttons
 * (dispatching their change/click), so the app keeps owning state.
 */
(function () {
  'use strict';
  var doc = document.documentElement;
  if (doc.getAttribute('data-nk-ui') !== 'geist') return;

  var M = window.Motion || null;
  var RM = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : { matches: false };
  function motionOK() { return !!(M && M.animate) && !RM.matches; }
  var EASE_OUT = [0.23, 1, 0.32, 1];
  var SPRING_PILL = { type: 'spring', stiffness: 520, damping: 40, mass: 1 };
  /* Entrance animations clean up after themselves: a lingering inline
     transform would make the element a containing block for fixed children
     (session docks, builder bars) and would override hover transforms.
     Pass { keep: true } when the final animated value is the resting state. */
  function anim(target, kf, opts) {
    if (!motionOK() || !target) return null;
    opts = opts || {};
    var keep = opts.keep; delete opts.keep;
    try {
      var a = M.animate(target, kf, Object.assign({ duration: 0.24, ease: EASE_OUT }, opts));
      if (!keep && a && a.finished) {
        var list = target.length != null && !target.style ? target : [target];
        var props = Object.keys(kf);
        a.finished.then(function () { window.setTimeout(function () { each(list, function (n) { if (n && n.style) props.forEach(function (p) { n.style[p] = ''; }); }); }, 32); }, function () {});
      }
      return a;
    } catch (e) { return null; }
  }

  /* ---------------------------------------------------------------- utils */
  function el(tag, cls, html) { var n = document.createElement(tag); if (cls) n.className = cls; if (html != null) n.innerHTML = html; return n; }
  function icon(name, size) {
    var body = (window.NKQ_ICONS || {})[name] || '';
    size = size || 16;
    return '<svg data-nkg-icon="' + name + '" width="' + size + '" height="' + size + '" viewBox="0 0 256 256" fill="currentColor" aria-hidden="true" focusable="false">' + body + '</svg>';
  }
  function esc(v) { return String(v == null ? '' : v).replace(/[&<>'"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[c]; }); }
  function fmtInt(n) { return Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ','); }
  function fmtMins(m) { m = Math.round(m); var h = Math.floor(m / 60); return (h ? h + 'h ' : '') + (m % 60) + 'm'; }
  function each(list, fn) { for (var i = 0; i < list.length; i++) fn(list[i], i); }
  function txt(n) { return n ? n.textContent.replace(/\s+/g, ' ').trim() : ''; }
  /* Parse a displayed figure ("1,105", "74%", "1h 57m", "39m", "13 days"). */
  function parseFigure(t) {
    t = String(t || '').replace(/\s+/g, ' ').trim();
    var m;
    if ((m = t.match(/^(\d+)h (\d+)m$/))) return { v: +m[1] * 60 + +m[2], f: fmtMins, unit: 'min' };
    if ((m = t.match(/^(\d+)h$/))) return { v: +m[1] * 60, f: fmtMins, unit: 'min' };
    if ((m = t.match(/^(\d+)m$/))) return { v: +m[1], f: fmtMins, unit: 'min' };
    if ((m = t.match(/^([\d,]+)%$/))) return { v: +m[1].replace(/,/g, ''), f: function (x) { return fmtInt(x) + '%'; }, unit: 'pct' };
    if ((m = t.match(/^([\d,]+)( days?)$/))) { var suf = m[2]; return { v: +m[1].replace(/,/g, ''), f: function (x) { return fmtInt(x) + (Math.round(x) === 1 ? ' day' : suf.replace(/^ day$/, ' days')); }, unit: 'n' }; }
    if ((m = t.match(/^[\d,]+$/))) return { v: +t.replace(/,/g, ''), f: fmtInt, unit: 'n' };
    return null;
  }

  /* -------------------------------------------------------------- haptics */
  var Haptics = (function () {
    var isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
    var canVibrate = typeof navigator.vibrate === 'function' && !isIOS;
    var NATIVE = { selection: 'choice', tick: 'choice', toggle: 'mark', impact: 'primary', success: 'success', error: 'error' };
    var VIBE = { selection: 8, tick: 5, toggle: 10, impact: 14, success: [10, 70, 18], error: [22, 60, 22] };
    var last = 0, label = null;
    function native(kind) {
      try { if (window.QBankHaptics && typeof window.QBankHaptics.play === 'function') { window.QBankHaptics.play(NATIVE[kind] || 'choice'); return true; } } catch (e) { /* bridge gone */ }
      return false;
    }
    /* ios-haptics (MIT): toggling a hidden <input switch> inside a user gesture
       makes iOS 18+ Safari play the system selection haptic. */
    function ios() {
      try {
        if (!label) {
          label = document.createElement('label');
          label.setAttribute('aria-hidden', 'true');
          label.style.cssText = 'position:fixed;left:-9999px;top:0;width:1px;height:1px;overflow:hidden;opacity:0;pointer-events:none';
          var input = document.createElement('input');
          input.type = 'checkbox'; input.setAttribute('switch', ''); input.tabIndex = -1;
          label.appendChild(input);
          document.body.appendChild(label);
        }
        label.click();
      } catch (e) { /* unsupported */ }
    }
    function play(kind) {
      var now = Date.now();
      if (kind === 'tick' && now - last < 40) return;
      last = now;
      if (native(kind)) return;
      if (canVibrate) { try { navigator.vibrate(VIBE[kind] || 8); } catch (e) { /* blocked */ } return; }
      if (isIOS && kind !== 'tick') ios();
      else if (isIOS) ios();
    }
    return { play: play, hasNative: function () { return !!window.QBankHaptics; } };
  })();
  /* Haptics mark outcomes, not taps: the core app already buzzes once for an answer,
     a mark and a finished test. Navigation, segments, menus, grids and outcomes stay silent
     here so an answer never buzzes twice. */
  var haptic = function () { /* intentionally silent: one buzz per answer comes from the core */ };

  /* -------------------------------------------------- sliding seg indicator */
  var pillMemo = {};
  var ro = window.ResizeObserver ? new ResizeObserver(function (entries) {
    each(entries, function (e) { var c = e.target; if (c.__nkgPill) placePill(c, c.__nkgPill.sel(), c.__nkgPill.key, false); });
  }) : null;
  function placePill(container, btn, key, animate) {
    var pill = container.querySelector(':scope > .nkg-seg-pill');
    if (!pill) {
      pill = el('span', 'nkg-seg-pill'); pill.setAttribute('aria-hidden', 'true');
      container.insertBefore(pill, container.firstChild);
      container.classList.add('nkg-has-pill');
    }
    if (!btn) { pill.style.opacity = '0'; return; }
    var cr = container.getBoundingClientRect(), br = btn.getBoundingClientRect();
    if (!cr.width || !br.width) return;
    var left = br.left - cr.left - container.clientLeft, w = br.width;
    var prev = pillMemo[key];
    pill.style.opacity = '1';
    pill.style.width = w + 'px';
    pill.style.transform = 'translateX(' + left + 'px)';
    if (animate !== false && prev && (Math.abs(prev.left - left) > 0.5 || Math.abs(prev.w - w) > 0.5)) {
      /* Transform-only so the slide runs on the compositor, even while the page recomputes. */
      anim(pill, { transform: ['translateX(' + prev.left + 'px)', 'translateX(' + left + 'px)'] }, Object.assign({ keep: true }, SPRING_PILL));
    }
    pillMemo[key] = { left: left, w: w };
  }
  function trackPill(container, key, selectorFn) {
    container.__nkgPill = { key: key, sel: selectorFn };
    placePill(container, selectorFn(), key, true);
    if (ro) ro.observe(container);
    /* The app marks the chosen button in place (class change, no re-render); follow it. */
    if (window.MutationObserver && !container.__nkgPillMo) {
      var queued = false;
      container.__nkgPillMo = new MutationObserver(function () {
        if (queued) return;
        queued = true;
        window.requestAnimationFrame(function () {
          queued = false;
          var sel = selectorFn();
          each(container.querySelectorAll(':scope > button'), function (b) { b.setAttribute('aria-pressed', b === sel ? 'true' : 'false'); });
          placePill(container, sel, key, true);
        });
      });
      container.__nkgPillMo.observe(container, { subtree: true, attributes: true, attributeFilter: ['class'] });
    }
  }

  /* Build a seg from a native <select>; the select stays (hidden) and owns state. */
  function segFromSelect(select, key, labels, opts) {
    opts = opts || {};
    var seg = el('div', 'nkg-seg nkg-seg-fill' + (opts.cls ? ' ' + opts.cls : ''));
    seg.setAttribute('role', 'group');
    seg.setAttribute('aria-label', select.getAttribute('aria-label') || '');
    each(select.options, function (o) {
      var b = el('button'); b.type = 'button';
      b.textContent = (labels && labels[o.value]) || o.textContent;
      b.dataset.value = o.value;
      b.setAttribute('aria-pressed', o.selected ? 'true' : 'false');
      seg.appendChild(b);
    });
    seg.addEventListener('click', function (e) {
      var b = e.target.closest('button');
      if (!b || b.getAttribute('aria-pressed') === 'true') return;
      haptic('selection');
      each(seg.querySelectorAll('button'), function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
      /* Slide the pill first, then recompute once it has mostly arrived, so heavy pages (Insights) never stall the motion. */
      placePill(seg, b, key, true);
      var value = b.dataset.value;
      window.clearTimeout(seg.__nkgCommit);
      seg.__nkgCommit = window.setTimeout(function () {
        if (select.value === value) return;
        select.value = value;
        select.dispatchEvent(new Event('change', { bubbles: true }));
      }, RM.matches ? 0 : 140);
    });
    select.classList.add('nkg-hidden-native');
    select.setAttribute('tabindex', '-1');
    select.setAttribute('aria-hidden', 'true');
    return seg;
  }

  /* ---------------------------------------------------- dropdown (02) */
  var openDd = null;
  function closeDd(focusBtn) {
    if (!openDd) return;
    var dd = openDd; openDd = null;
    dd.classList.remove('is-open');
    var btn = dd.querySelector('.nkg-dd-btn'), panel = dd.querySelector('.nkg-dd-panel');
    btn.setAttribute('aria-expanded', 'false');
    panel.hidden = true;
    if (focusBtn) btn.focus();
  }
  document.addEventListener('pointerdown', function (e) { if (openDd && !openDd.contains(e.target)) closeDd(false); }, true);
  window.addEventListener('resize', function () { closeDd(false); });
  var ddSeq = 0;
  function ddFromSelect(select, opts) {
    opts = opts || {};
    var id = 'nkg-dd-' + (++ddSeq);
    var dd = el('div', 'nkg-dd' + (opts.cls ? ' ' + opts.cls : ''));
    var cur = select.options[select.selectedIndex];
    var btn = el('button', 'nkg-dd-btn', '<span class="nkg-dd-val">' + esc(displayLabel(cur)) + '</span><span class="nkg-dd-chev">' + icon('caret-down', 14) + '</span>');
    btn.type = 'button';
    btn.setAttribute('aria-haspopup', 'listbox'); btn.setAttribute('aria-expanded', 'false'); btn.setAttribute('aria-controls', id);
    btn.setAttribute('aria-label', (select.getAttribute('aria-label') || labelText(select) || 'Choose') + ': ' + (cur ? cur.textContent : ''));
    var panel = el('div', 'nkg-dd-panel'); panel.id = id; panel.setAttribute('role', 'listbox'); panel.hidden = true;
    var lastGroup = null;
    each(select.options, function (o) {
      var m = o.textContent.match(/^(UWorld) · (.+)$/);
      var group = m ? 'My UWorld' : null;
      if (group && group !== lastGroup) { panel.appendChild(el('div', 'nkg-dd-sep')); panel.appendChild(el('div', 'nkg-dd-group', esc(group))); }
      lastGroup = group;
      var opt = el('button', 'nkg-dd-opt', '<span>' + esc(m ? m[2] : o.textContent) + '</span>' + icon('check', 16));
      opt.type = 'button'; opt.setAttribute('role', 'option'); opt.tabIndex = -1;
      opt.dataset.value = o.value;
      opt.setAttribute('aria-selected', o.selected ? 'true' : 'false');
      panel.appendChild(opt);
    });
    dd.appendChild(btn); dd.appendChild(panel);
    function options() { return [].slice.call(panel.querySelectorAll('.nkg-dd-opt')); }
    function open() {
      if (openDd && openDd !== dd) closeDd(false);
      openDd = dd; dd.classList.add('is-open'); btn.setAttribute('aria-expanded', 'true'); panel.hidden = false;
      var r = dd.getBoundingClientRect();
      dd.classList.toggle('is-right', r.left + Math.max(r.width, 240) > window.innerWidth - 8);
      anim(panel, { opacity: [0, 1], transform: ['translateY(-4px) scale(.98)', 'translateY(0) scale(1)'] }, { duration: 0.16 });
      var sel = panel.querySelector('[aria-selected="true"]') || options()[0];
      if (sel) { sel.classList.add('is-active'); sel.focus({ preventScroll: true }); sel.scrollIntoView({ block: 'nearest' }); }
      haptic('selection');
    }
    function pick(opt) {
      closeDd(true);
      if (!opt || opt.getAttribute('aria-selected') === 'true') return;
      haptic('selection');
      select.value = opt.dataset.value;
      select.dispatchEvent(new Event('change', { bubbles: true }));
      if (dd.isConnected) {
        each(options(), function (x) { x.setAttribute('aria-selected', x === opt ? 'true' : 'false'); });
        dd.querySelector('.nkg-dd-val').textContent = displayLabel(select.options[select.selectedIndex]);
      }
    }
    btn.addEventListener('click', function () { if (dd.classList.contains('is-open')) closeDd(false); else open(); });
    btn.addEventListener('keydown', function (e) { if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); open(); } });
    panel.addEventListener('click', function (e) { var o = e.target.closest('.nkg-dd-opt'); if (o) pick(o); });
    panel.addEventListener('keydown', function (e) {
      var list = options(), i = list.indexOf(document.activeElement);
      if (e.key === 'Escape') { e.preventDefault(); closeDd(true); }
      else if (e.key === 'Tab') closeDd(false);
      else if (e.key === 'ArrowDown' || e.key === 'ArrowUp' || e.key === 'Home' || e.key === 'End') {
        e.preventDefault();
        var n = e.key === 'Home' ? 0 : e.key === 'End' ? list.length - 1 : Math.max(0, Math.min(list.length - 1, i + (e.key === 'ArrowDown' ? 1 : -1)));
        each(list, function (x) { x.classList.remove('is-active'); });
        list[n].classList.add('is-active'); list[n].focus({ preventScroll: true }); list[n].scrollIntoView({ block: 'nearest' });
      } else if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); pick(document.activeElement.closest('.nkg-dd-opt')); }
    });
    select.classList.add('nkg-hidden-native');
    select.setAttribute('tabindex', '-1');
    select.setAttribute('aria-hidden', 'true');
    return dd;
  }
  function displayLabel(o) { return o ? o.textContent.replace(/^UWorld · /, 'UWorld: ') : ''; }
  function labelText(select) { var l = select.closest('label'); var s = l && l.querySelector('.nk-li-sr'); return s ? s.textContent.trim() : ''; }

  /* ------------------------------------------------------------ count-up */
  var figMemo = {};
  function countUp(node, key, fromZero) {
    if (!node || node.__nkgCounted) return;
    node.__nkgCounted = true;
    var final = node.textContent;
    var p = parseFigure(final);
    if (!p) return;
    var prev = figMemo[key];
    figMemo[key] = p.v;
    var from = prev != null ? prev : (fromZero ? 0 : null);
    if (from == null || from === p.v || !motionOK()) return;
    try {
      M.animate(from, p.v, {
        duration: Math.min(0.9, 0.45 + Math.abs(p.v - from) / 4000), ease: [0.16, 1, 0.3, 1],
        onUpdate: function (x) {
          var now = performance.now();
          if (now - (node.__nkgAt || 0) < 70) return;
          node.__nkgAt = now;
          var t = p.f(x); if (t !== node.textContent) node.textContent = t;
        },
        onComplete: function () { node.textContent = final; }
      });
    } catch (e) { node.textContent = final; }
  }

  /* -------------------------------------------------------- data signature */
  var sigMemo = {};
  function changed(key, sig) { var c = sigMemo[key] !== sig; sigMemo[key] = sig; return c; }
  function onView(node, fn) {
    if (!node) return;
    if (M && M.inView) { try { M.inView(node, function () { fn(); }, { amount: 0.25 }); return; } catch (e) { /* fall through */ } }
    fn();
  }

  /* ================================================================ Home */
  function rangeWindow(range, now) {
    var start = new Date(now); start.setHours(0, 0, 0, 0);
    var pStart = new Date(start);
    if (range === 'today') { pStart.setDate(pStart.getDate() - 1); }
    else if (range === 'week') { start.setDate(start.getDate() - ((start.getDay() + 6) % 7)); pStart = new Date(start); pStart.setDate(pStart.getDate() - 7); }
    else if (range === 'month') { start.setDate(1); pStart = new Date(start); pStart.setMonth(pStart.getMonth() - 1); }
    else if (range === 'year') { start.setMonth(0, 1); pStart = new Date(start); pStart.setFullYear(pStart.getFullYear() - 1); }
    var elapsed = now - start;
    return { cur: [+start, +now], prev: [+pStart, +pStart + elapsed] };
  }
  function rangeMetrics(w) {
    var s = {}; try { s = window.QB.getState() || {}; } catch (e) { /* not booted */ }
    var attempts = s.attempts || {}, tests = Array.isArray(s.tests) ? s.tests : [];
    var uniq = {}, total = 0, correct = 0, ms = 0;
    Object.keys(attempts).forEach(function (qid) {
      var list = attempts[qid] || [], undone = {};
      list.forEach(function (a) { if (a && a.isUndo && a.undoOf) undone[String(a.undoOf)] = true; });
      list.forEach(function (a) {
        if (!a || a.isUndo || a.isRatingRevision || typeof a.correct !== 'boolean' || undone[String(a.id)]) return;
        var at = Number(a.reviewedAt || a.at); if (!(at >= w[0] && at <= w[1])) return;
        uniq[qid] = 1; total++; if (a.correct) correct++;
        if (a.source !== 'exam') ms += Math.max(0, Number(a.timeSpent) || 0);
      });
    });
    tests.forEach(function (t) { if (t && t.kind !== 'practice' && t.createdAt >= w[0] && t.createdAt <= w[1]) ms += Math.max(0, Number(t.totalTimeMs) || 0); });
    return { unique: Object.keys(uniq).length, acc: total ? correct / total * 100 : null, mins: ms / 60000 };
  }
  function deltaChip(cur, prev, kind) {
    if (prev == null || cur == null) return null;
    var d, label;
    if (kind === 'pp') { d = cur - prev; if (Math.abs(d) < 0.05) return ['No change', 'is-neutral']; label = Math.abs(d).toFixed(1) + ' pp'; }
    else { if (!prev) return cur ? ['New', 'is-neutral'] : null; d = (cur - prev) / prev * 100; if (Math.abs(d) < 0.5) return ['No change', 'is-neutral']; label = Math.round(Math.abs(d)) + '%'; }
    return [(d > 0 ? '↑ ' : '↓ ') + label, d > 0 ? 'is-up' : 'is-down'];
  }
  function enhanceHome(app) {
    var head = app.querySelector('.nk-home-progress-head');
    var select = head && head.querySelector('.nk-home-range select');
    if (select && !head.querySelector('.nkg-seg')) {
      var seg = segFromSelect(select, 'home-range', { today: 'Today', week: 'Week', month: 'Month', year: 'Year' });
      head.appendChild(seg);
      trackPill(seg, 'home-range', function () { return seg.querySelector('[aria-pressed="true"]'); });
      /* Honest deltas: only when our recomputation matches what the app shows. */
      var range = select.value, w = rangeWindow(range, Date.now());
      var cur = rangeMetrics(w.cur), prev = rangeMetrics(w.prev);
      var rows = app.querySelectorAll('.nk-home-progress-copy');
      each(rows, function (row, i) {
        var b = row.querySelector('b'); if (!b) return;
        var shown = txt(b), chip = null;
        if (i === 0 && shown.replace(/,/g, '') === String(cur.unique)) chip = deltaChip(cur.unique, prev.unique, '%');
        if (i === 1 && cur.acc != null && shown === Math.round(cur.acc) + '%') chip = deltaChip(cur.acc, prev.acc, 'pp');
        if (i === 2 && parseFigure(shown) && Math.abs(parseFigure(shown).v - Math.round(cur.mins)) <= 1) chip = deltaChip(cur.mins, prev.mins, '%');
        var wrap = el('span', 'nkg-val');
        b.parentNode.insertBefore(wrap, b); wrap.appendChild(b);
        if (chip) { var c = el('span', 'nkg-delta ' + chip[1]); c.textContent = chip[0]; c.title = 'Compared with the same point of the previous ' + (range === 'today' ? 'day' : range); wrap.appendChild(c); }
        countUp(b, 'home-' + range + '-' + i, false);
      });
    }
    enhanceStreak(app.querySelector('.nk-home-streak-card'));
  }

  /* ========================================================== streak (11) */
  var streakOpen = false;
  var MILESTONES = [3, 7, 14, 30, 60, 100, 180, 365];
  function lsGet(k) { try { return window.localStorage.getItem(k); } catch (e) { return null; } }
  function lsSet(k, v) { try { window.localStorage.setItem(k, v); } catch (e) { /* blocked */ } }
  function enhanceStreak(card) {
    if (!card || card.__nkg) return;
    card.__nkg = true;
    var numEl = card.querySelector('.nk-streak-number');
    var n = numEl ? parseInt(txt(numEl).replace(/,/g, ''), 10) || 0 : 0;
    var tier = n >= 30 ? 30 : n >= 14 ? 14 : n >= 7 ? 7 : n >= 3 ? 3 : n >= 1 ? 1 : 0;
    card.setAttribute('data-tier', String(tier));
    var m = {};
    try { m = (window.NKQ_UI && window.NKQ_UI.metrics) ? window.NKQ_UI.metrics() : {}; } catch (e) { m = {}; }
    var next = MILESTONES.filter(function (x) { return x > n; })[0] || n + 30;
    var prevMs = MILESTONES.filter(function (x) { return x <= n; }).pop() || 0;
    var activeDays = m.days ? Object.keys(m.days).length : null;
    var more = el('div', 'nkg-streak-more');
    more.id = 'nkg-streak-more';
    more.innerHTML = '<div class="nkg-streak-more-inner">' +
      '<div class="nkg-streak-stats">' +
      '<div><b>' + fmtInt(n) + '</b><small>Current</small></div>' +
      '<div><b>' + (m.best != null ? fmtInt(Math.max(m.best, n)) : '—') + '</b><small>Longest</small></div>' +
      '<div><b>' + (activeDays != null ? fmtInt(activeDays) : '—') + '</b><small>Active days</small></div></div>' +
      '<div class="nkg-milestone"><div class="nkg-milestone-head"><span>' + (n ? (next - n) + (next - n === 1 ? ' day' : ' days') + ' to the ' + next + '-day mark' : 'Answer one question to start a streak') + '</span><b>' + n + ' / ' + next + '</b></div>' +
      '<div class="nkg-milestone-bar" role="progressbar" aria-valuemin="0" aria-valuemax="' + next + '" aria-valuenow="' + n + '"><i style="width:' + Math.max(0, Math.min(100, (n - prevMs) / Math.max(1, next - prevMs) * 100)) + '%"></i></div></div>' +
      '<p class="nkg-streak-rule">A day counts when you answer at least one question. Miss a calendar day and the streak starts again.</p>' +
      '</div>';
    more.hidden = !streakOpen;
    card.appendChild(more);
    card.setAttribute('role', 'button');
    card.setAttribute('tabindex', '0');
    card.setAttribute('aria-expanded', streakOpen ? 'true' : 'false');
    card.setAttribute('aria-controls', 'nkg-streak-more');
    card.setAttribute('aria-label', n + ' day study streak. Show streak details');
    function toggle() {
      streakOpen = !streakOpen;
      card.setAttribute('aria-expanded', streakOpen ? 'true' : 'false');
      haptic('toggle');
      if (streakOpen) {
        more.hidden = false;
        var h = more.scrollHeight;
        anim(more, { height: ['0px', h + 'px'], opacity: [0, 1] }, { duration: 0.28 });
        var bar = more.querySelector('.nkg-milestone-bar i');
        anim(bar, { transform: ['scaleX(0)', 'scaleX(1)'] }, { duration: 0.6, delay: 0.08 });
      } else {
        var a = anim(more, { height: [more.scrollHeight + 'px', '0px'], opacity: [1, 0] }, { duration: 0.2 });
        if (a && a.finished) a.finished.then(function () { if (!streakOpen) more.hidden = true; more.style.height = ''; }); else more.hidden = true;
      }
    }
    card.addEventListener('click', function (e) { if (e.target.closest('a,button')) return; toggle(); });
    card.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle(); } });
    /* Living flame: a slow, small flicker while the streak is alive. */
    var flame = card.querySelector('.nk-home-streak-flame svg');
    if (flame && tier >= 1 && motionOK()) {
      anim(flame, { transform: ['scale(1,1) rotate(0deg)', 'scale(.97,1.06) rotate(-2deg)', 'scale(1.02,.97) rotate(1.5deg)', 'scale(.99,1.04) rotate(-1deg)', 'scale(1,1) rotate(0deg)'] },
        { duration: tier >= 14 ? 2.2 : 2.8, repeat: Infinity, ease: 'easeInOut' });
    }
    /* The day the streak grows: one ignite moment, once. */
    var seen = parseInt(lsGet('nkg.streak.seen') || '0', 10);
    if (n > seen && n > 0) {
      lsSet('nkg.streak.seen', String(n));
      if (seen > 0 || n === 1) {
        var tile = card.querySelector('.nk-home-streak-flame');
        anim(tile, { transform: ['scale(.6)', 'scale(1)'] }, { type: 'spring', stiffness: 380, damping: 14 });
        if (numEl) { figMemo['streak'] = seen; numEl.__nkgCounted = false; countUp(numEl, 'streak', false); }
        window.setTimeout(function () { haptic('success'); }, 120);
      }
    } else if (n < seen) lsSet('nkg.streak.seen', String(n));
  }

  /* ============================================================ Insights */
  function enhanceInsights(app) {
    var root = app.querySelector('.nk-learning-insights');
    if (!root) return;
    /* 02 · unified period bar */
    var period = root.querySelector('#nk-li-period');
    var nav = root.querySelector('.nk-li-period-nav');
    if (period && nav && !nav.querySelector('.nkg-seg')) {
      var seg = segFromSelect(period, 'li-period', { week: 'Week', month: 'Month', year: 'Year' });
      var buttons = nav.querySelectorAll(':scope > button');
      if (buttons[0]) { buttons[0].innerHTML = icon('caret-left', 18); buttons[0].setAttribute('aria-label', buttons[0].getAttribute('aria-label') || 'Previous period'); }
      if (buttons[1]) { buttons[1].innerHTML = icon('caret-right', 18); buttons[1].setAttribute('aria-label', buttons[1].getAttribute('aria-label') || 'Next period'); }
      nav.insertBefore(seg, buttons[1] || null);
      trackPill(seg, 'li-period', function () { return seg.querySelector('[aria-pressed="true"]'); });
    }
    each(root.querySelectorAll('.nk-li-scope select'), function (s, i) {
      /* Filters narrow each other: rebuild the menu whenever the native options change. */
      var sig = [].map.call(s.options, function (o) { return o.value + '\u001f' + o.textContent; }).join('\u001e') + '|' + s.value;
      if (s.classList.contains('nkg-hidden-native') && s.__nkgSig === sig && s.__nkgDd && s.__nkgDd.isConnected) return;
      if (s.__nkgDd) s.__nkgDd.remove();
      var lab = s.closest('label');
      var dd = ddFromSelect(s, { cls: i ? 'is-right' : '' });
      s.__nkgSig = sig; s.__nkgDd = dd;
      (lab || s).parentNode.insertBefore(dd, lab || s);
    });
    var yearSel = root.querySelector('.nk-li-year-activity > header select');
    if (yearSel && !yearSel.classList.contains('nkg-hidden-native')) {
      var yl = yearSel.closest('label');
      var ydd = ddFromSelect(yearSel, { cls: 'is-right' });
      (yl || yearSel).parentNode.insertBefore(ydd, yl || yearSel);
    }
    var periodKey = (period && period.value || '') + '|' + txt(nav && nav.querySelector('strong'));
    /* Figures count from their previous value when the period changes. */
    each(root.querySelectorAll('.nk-li-stats > article'), function (a) { countUp(a.querySelector(':scope > b'), 'li-stat-' + a.getAttribute('data-metric'), true); });
    each(root.querySelectorAll('.nk-li-year-summary b'), function (b, i) { countUp(b, 'li-year-' + i, true); });
    enhanceDonuts(root, periodKey);
    enhanceBars(root, periodKey);
    each(root.querySelectorAll('svg.nk-li-trend'), function (svg) { enhanceTrend(svg, periodKey); });
    enhanceTopics(root);
    enhanceSubjects(root.querySelector('.nk-li-subjects'));
    enhanceComparison(root.querySelector('.nk-li-comparison'), periodKey);
    each(root.querySelectorAll('.nk-li-forecast'), function (f) { enhanceForecast(f, 'li'); });
    enhanceHeatmap(root.querySelector('.nk-li-year-activity'));
  }

  /* 06 · donut sweep + count */
  function enhanceDonuts(root, periodKey) {
    each(root.querySelectorAll('.nk-li-donut'), function (d, i) {
      if (d.__nkg) return; d.__nkg = true;
      var sig = (d.getAttribute('style') || '') + periodKey;
      if (!changed('donut-' + i, sig) || !motionOK()) return;
      d.classList.add('nkg-sweep-start');
      var outcomes = d.closest('.nk-li-outcomes');
      var center = d.querySelector('b, strong');
      onView(d, function () {
        void d.offsetWidth;
        d.classList.add('nkg-sweeping');
        d.classList.remove('nkg-sweep-start');
        if (center) { figMemo['donut-' + i] = 0; countUp(center, 'donut-' + i, true); }
        if (outcomes) anim(outcomes.querySelectorAll('dl > *'), { opacity: [0, 1], transform: ['translateY(4px)', 'none'] }, { duration: 0.3, delay: M.stagger ? M.stagger(0.04, { startDelay: 0.25 }) : 0.25 });
      });
    });
  }

  /* 03 · questions bars */
  function enhanceBars(root, periodKey) {
    var bars = root.querySelector('.nk-li-bars');
    if (!bars || bars.__nkg) return; bars.__nkg = true;
    var sig = txt(bars) + periodKey;
    if (!changed('bars', sig) || !motionOK()) return;
    var cols = bars.querySelectorAll('.nk-li-bar-pair');
    onView(bars, function () {
      each(cols, function (c, i) { anim(c.querySelectorAll('i'), { transform: ['scaleY(0)', 'scaleY(1)'] }, { type: 'spring', stiffness: 260, damping: 26, delay: i * 0.035 }); });
    });
  }

  /* 03 · study-time trend: smooth ink curve, area, peak, scrub with tooltip. */
  function smoothPath(pts) {
    if (pts.length < 2) return pts.length ? 'M' + pts[0][0] + ',' + pts[0][1] : '';
    var d = 'M' + pts[0][0].toFixed(1) + ',' + pts[0][1].toFixed(1);
    for (var i = 0; i < pts.length - 1; i++) {
      var p0 = pts[Math.max(0, i - 1)], p1 = pts[i], p2 = pts[i + 1], p3 = pts[Math.min(pts.length - 1, i + 2)];
      var t = 0.18;
      var c1x = p1[0] + (p2[0] - p0[0]) * t, c1y = p1[1] + (p2[1] - p0[1]) * t;
      var c2x = p2[0] - (p3[0] - p1[0]) * t, c2y = p2[1] - (p3[1] - p1[1]) * t;
      d += ' C' + c1x.toFixed(1) + ',' + c1y.toFixed(1) + ' ' + c2x.toFixed(1) + ',' + c2y.toFixed(1) + ' ' + p2[0].toFixed(1) + ',' + p2[1].toFixed(1);
    }
    return d;
  }
  function minsOf(s) { var p = parseFigure(s); return p && p.unit === 'min' ? p.v : null; }
  var trendSeq = 0;
  function enhanceTrend(svg, periodKey) {
    if (!svg || svg.__nkg) return; svg.__nkg = true;
    var label = svg.getAttribute('aria-label') || '';
    var body = label.replace(/^[^.]*\.\s*/, '');
    var entries = body.split(/;\s*/).map(function (part) {
      var m = part.match(/^(.+?):\s*([^,]+?)(?:,\s*previous\s+(.+))?$/);
      return m ? { name: m[1].trim(), cur: minsOf(m[2]), prev: m[3] != null ? minsOf(m[3]) : null } : null;
    }).filter(Boolean);
    var axis = [].slice.call(svg.querySelectorAll('text')).filter(function (t) { return t.getAttribute('text-anchor') === 'middle'; });
    var grid = [].slice.call(svg.querySelectorAll('line')).map(function (l) { return { y: +l.getAttribute('y1'), x1: +l.getAttribute('x1'), x2: +l.getAttribute('x2') }; });
    var gridText = [].slice.call(svg.querySelectorAll('text')).filter(function (t) { return t.getAttribute('text-anchor') !== 'middle'; });
    if (!entries.length || axis.length < 2 || grid.length < 2 || gridText.length < 2) return;
    var gv = gridText.map(function (t) { return { y: +t.getAttribute('y') - 4, v: parseFloat(t.textContent), unit: /h/.test(t.textContent) ? 60 : 1, label: t.textContent }; });
    var lo = gv[0], hi = gv[gv.length - 1];
    var pxPerMin = (lo.y - hi.y) / ((hi.v - lo.v) * hi.unit || 1);
    var X = axis.map(function (t) { return +t.getAttribute('x'); });
    var names = axis.map(function (t) { return t.textContent; });
    function y(mins) { return lo.y - (mins - lo.v * lo.unit) * pxPerMin; }
    var cur = [], prev = [];
    entries.forEach(function (e) {
      var i = names.indexOf(e.name); if (i < 0) return;
      if (e.cur != null) cur.push([X[i], y(e.cur), e, i]);
      if (e.prev != null) prev.push([X[i], y(e.prev), e, i]);
    });
    if (!cur.length) return;
    var id = 'nkg-tr-' + (++trendSeq);
    var L = grid[0].x1, R = grid[0].x2, base = lo.y;
    var peak = cur.reduce(function (a, b) { return b[2].cur > a[2].cur ? b : a; }, cur[0]);
    var parts = [];
    parts.push('<defs><linearGradient id="' + id + '" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="var(--nkg-fg)" stop-opacity=".10"/><stop offset="1" stop-color="var(--nkg-fg)" stop-opacity="0"/></linearGradient></defs>');
    gv.forEach(function (g) { parts.push('<line x1="' + L + '" x2="' + R + '" y1="' + g.y + '" y2="' + g.y + '" stroke="var(--nkg-border)" stroke-width="1"/><text x="0" y="' + (g.y + 4) + '" font-size="11">' + esc(g.label) + '</text>'); });
    names.forEach(function (n, i) { parts.push('<text x="' + X[i] + '" y="196" text-anchor="middle" font-size="11"' + (i > cur[cur.length - 1][3] ? ' opacity=".55"' : '') + '>' + esc(n) + '</text>'); });
    var curD = smoothPath(cur), prevD = smoothPath(prev);
    if (prev.length > 1) parts.push('<path class="nkg-tr-prev" d="' + prevD + '" fill="none" stroke="var(--nkg-border-strong)" stroke-width="2" stroke-dasharray="4 5" stroke-linecap="round"/>');
    if (cur.length > 1) parts.push('<path class="nkg-tr-area" d="' + curD + ' L' + cur[cur.length - 1][0] + ',' + base + ' L' + cur[0][0] + ',' + base + ' Z" fill="url(#' + id + ')"/>');
    parts.push('<path class="nkg-tr-cur" d="' + curD + '" fill="none" stroke="var(--nkg-fg)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" pathLength="1"/>');
    parts.push('<g class="nkg-tr-peak"><circle cx="' + peak[0] + '" cy="' + peak[1] + '" r="4" fill="var(--nkg-fg)" stroke="var(--nkg-surface)" stroke-width="2"/>' +
      '<text x="' + Math.min(R - 14, Math.max(L + 14, peak[0])) + '" y="' + Math.max(12, peak[1] - 10) + '" text-anchor="middle" font-size="11" font-weight="600" style="fill:var(--nkg-fg)">' + fmtMins(peak[2].cur) + '</text></g>');
    parts.push('<line class="nkg-tr-scrub" x1="0" x2="0" y1="' + (hi.y - 6) + '" y2="' + base + '" stroke="var(--nkg-fg)" stroke-width="1" stroke-dasharray="2 3" opacity="0"/>');
    parts.push('<circle class="nkg-tr-focus" r="5" fill="var(--nkg-surface)" stroke="var(--nkg-fg)" stroke-width="2.5" opacity="0"/>');
    svg.innerHTML = parts.join('');
    svg.setAttribute('tabindex', '0');
    var wrap = el('div', 'nkg-trend');
    svg.parentNode.insertBefore(wrap, svg); wrap.appendChild(svg);
    var tip = el('div', 'nkg-tip'); tip.setAttribute('aria-hidden', 'true'); wrap.appendChild(tip);
    var scrub = svg.querySelector('.nkg-tr-scrub'), focus = svg.querySelector('.nkg-tr-focus'), peakG = svg.querySelector('.nkg-tr-peak');
    var period = (txt(svg.closest('.nk-li-card') && svg.closest('.nk-li-card').querySelector('.nk-li-key span')) || 'This period');
    var active = -1, hideT = 0;
    function show(k) {
      if (k < 0 || k >= cur.length) return;
      window.clearTimeout(hideT);
      if (k !== active) { haptic('tick'); active = k; }
      var p = cur[k], vb = svg.viewBox.baseVal, r = svg.getBoundingClientRect(), sx = r.width / vb.width, sy = r.height / vb.height;
      scrub.setAttribute('x1', p[0]); scrub.setAttribute('x2', p[0]); scrub.setAttribute('opacity', '.5');
      focus.setAttribute('cx', p[0]); focus.setAttribute('cy', p[1]); focus.setAttribute('opacity', '1');
      peakG.setAttribute('opacity', '.25');
      var e = p[2];
      tip.innerHTML = '<div class="t">' + esc(e.name) + ' · ' + esc(period) + '</div><div class="v">' + fmtMins(e.cur) + '</div>' + (e.prev != null ? '<div class="p">previous ' + fmtMins(e.prev) + '</div>' : '');
      var left = Math.min(r.width - 64, Math.max(64, p[0] * sx));
      tip.style.left = left + 'px'; tip.style.top = (p[1] * sy) + 'px';
      tip.classList.add('is-on');
    }
    function hide(delay) {
      window.clearTimeout(hideT);
      hideT = window.setTimeout(function () { active = -1; scrub.setAttribute('opacity', '0'); focus.setAttribute('opacity', '0'); peakG.setAttribute('opacity', '1'); tip.classList.remove('is-on'); }, delay || 0);
    }
    function nearest(clientX) {
      var r = svg.getBoundingClientRect(), sx = (clientX - r.left) * (svg.viewBox.baseVal.width / r.width), best = 0, bd = 1e9;
      cur.forEach(function (p, i) { var d = Math.abs(p[0] - sx); if (d < bd) { bd = d; best = i; } });
      return best;
    }
    var down = false;
    svg.addEventListener('pointerdown', function (e) { down = true; show(nearest(e.clientX)); });
    svg.addEventListener('pointermove', function (e) { if (down || e.pointerType === 'mouse') show(nearest(e.clientX)); });
    svg.addEventListener('pointerup', function (e) { down = false; hide(e.pointerType === 'mouse' ? 0 : 1600); });
    svg.addEventListener('pointercancel', function () { down = false; hide(0); });
    svg.addEventListener('pointerleave', function (e) { if (e.pointerType === 'mouse') hide(0); });
    svg.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') { e.preventDefault(); show(Math.max(0, Math.min(cur.length - 1, (active < 0 ? cur.length - 1 : active) + (e.key === 'ArrowRight' ? 1 : -1)))); }
      else if (e.key === 'Escape') hide(0);
    });
    svg.addEventListener('blur', function () { hide(0); });
    /* Draw in on first view and whenever the period changes (CSS transitions:
       SVG paint properties are not reliably driven by WAAPI). */
    if (changed('trend', label + periodKey) && motionOK()) {
      var line = svg.querySelector('.nkg-tr-cur'), area = svg.querySelector('.nkg-tr-area'), pv = svg.querySelector('.nkg-tr-prev');
      line.style.strokeDasharray = '1'; line.style.strokeDashoffset = '1';
      [area, pv, peakG].forEach(function (n) { if (n) n.style.opacity = '0'; });
      onView(wrap, function () {
        cssTo(line, { strokeDashoffset: '0' }, 900, 0, 'cubic-bezier(.65,0,.35,1)');
        cssTo(pv, { opacity: '1' }, 500, 100);
        cssTo(area, { opacity: '1' }, 600, 450);
        cssTo(peakG, { opacity: '1' }, 300, 800);
      });
    }
  }
  function cssTo(node, props, dur, delay, ease) {
    if (!node) return;
    var keys = Object.keys(props);
    node.style.transition = keys.map(function (k) { return k.replace(/[A-Z]/g, function (c) { return '-' + c.toLowerCase(); }) + ' ' + dur + 'ms ' + (ease || 'cubic-bezier(.23,1,.32,1)') + ' ' + (delay || 0) + 'ms'; }).join(',');
    window.requestAnimationFrame(function () { window.requestAnimationFrame(function () { keys.forEach(function (k) { node.style[k] = props[k]; }); }); });
  }

  /* Subject performance: rows without answers collapse to one quiet line, after the rows with data. */
  function enhanceSubjects(box) {
    if (!box || box.__nkg) return; box.__nkg = true;
    var empty = [];
    each(box.children, function (r) {
      var b = r.querySelector(':scope > b');
      if (b && /^[\u2014-]$/.test(txt(b))) { r.classList.add('nkg-empty-row'); empty.push(r); }
    });
    empty.forEach(function (r) { box.appendChild(r); });
    if (empty.length && empty.length < box.children.length) empty[0].classList.add('nkg-first-empty');
  }

  /* 05 · topic tabs + rows */
  function enhanceTopics(root) {
    var tabs = root.querySelector('.nk-li-tabs');
    if (!tabs || tabs.__nkg) return; tabs.__nkg = true;
    trackPill(tabs, 'li-topics', function () { return tabs.querySelector('[aria-pressed="true"]'); });
    tabs.addEventListener('click', function (e) { if (e.target.closest('button')) haptic('selection'); }, true);
    var mode = txt(tabs.querySelector('[aria-pressed="true"]'));
    var card = tabs.closest('.nk-li-card');
    var rows = card ? card.querySelectorAll('.nk-li-topic') : [];
    if (changed('li-topics', mode + rows.length + txt(rows[0])) && motionOK() && sigMemo['li-topics-seen']) {
      anim(rows, { opacity: [0, 1], transform: ['translateY(6px)', 'none'] }, { duration: 0.28, delay: M.stagger ? M.stagger(0.035) : 0 });
    }
    sigMemo['li-topics-seen'] = 1;
  }

  /* 08 · period comparison as change rows: ○ previous → ● current on one scale. */
  function enhanceComparison(box, periodKey) {
    if (!box || box.__nkg) return; box.__nkg = true;
    var head = box.querySelector('.nk-li-comparison-head');
    var hs = head ? head.querySelectorAll('span') : [];
    var curName = txt(hs[1]) || 'This period', prevName = txt(hs[2]) || 'Previous period';
    var rows = [].slice.call(box.children).filter(function (r) { return r !== head && r.querySelector('strong'); });
    if (!rows.length) return;
    var out = el('div', 'nkg-cmp');
    out.appendChild(el('div', 'nkg-cmp-legend', '<span><i class="is-prev"></i>' + esc(prevName) + '</span><span><i class="is-cur"></i>' + esc(curName) + '</span>'));
    var moves = [];
    rows.forEach(function (r) {
      var name = txt(r.querySelector('strong')), cb = r.querySelector('b'), ps = r.querySelector(':scope > span:not(.nk-li-delta)'), ds = r.querySelector('.nk-li-delta');
      var cv = parseFigure(txt(cb)), pv = parseFigure(txt(ps));
      var dir = ds && ds.classList.contains('is-up') ? 'is-up' : ds && ds.classList.contains('is-down') ? 'is-down' : 'is-neutral';
      var row = el('div', 'nkg-cmp-row ' + dir);
      row.setAttribute('role', 'group');
      row.setAttribute('aria-label', name + ': ' + txt(cb) + ' ' + curName.toLowerCase() + ', ' + txt(ps) + ' ' + prevName.toLowerCase() + (ds ? ', ' + txt(ds) : ''));
      var html = '<span class="nkg-cmp-label">' + esc(name) + '</span>' + (ds ? '<span class="nkg-delta ' + dir + '">' + esc(txt(ds)) + '</span>' : '');
      var a = null, b = null;
      if (cv && pv) {
        var max = Math.max(cv.v, pv.v);
        a = max ? pv.v / max * 100 : 0; b = max ? cv.v / max * 100 : 0;
        if (cv.unit === 'pct') { a = pv.v; b = cv.v; }
        var lo = Math.min(a, b), hi = Math.max(a, b);
        html += '<div class="nkg-cmp-track" aria-hidden="true"><span class="nkg-cmp-seg" style="left:' + lo + '%;width:' + (hi - lo) + '%"></span><span class="nkg-cmp-dot is-prev" style="left:' + a + '%"></span><span class="nkg-cmp-dot is-cur" style="left:' + b + '%"></span></div>';
      }
      html += '<span class="nkg-cmp-vals"><b class="is-prev">' + esc(txt(ps)) + '</b><span class="nkg-cmp-arrow" aria-hidden="true">' + icon('arrow-right', 12) + '</span><b class="is-cur">' + esc(txt(cb)) + '</b></span>';
      row.innerHTML = html;
      out.appendChild(row);
      if (a != null && Math.abs(a - b) > 0.5) moves.push({ row: row, a: a, b: b });
    });
    box.appendChild(out);
    box.classList.add('nkg-cmp-ready');
    if (changed('cmp', txt(box) + periodKey) && motionOK() && moves.length) {
      /* Final geometry is set once; the motion is transform-only (compositor), so the
         period switch never forces a layout per frame. */
      onView(out, function () {
        moves.forEach(function (mv, i) {
          var dot = mv.row.querySelector('.is-cur.nkg-cmp-dot'), seg = mv.row.querySelector('.nkg-cmp-seg');
          var track = dot && dot.parentElement, W = track ? track.getBoundingClientRect().width : 0;
          var opts = { duration: 0.7, delay: 0.1 + i * 0.06, ease: [0.22, 1, 0.36, 1] };
          if (dot && W) anim(dot, { transform: ['translateX(' + ((mv.a - mv.b) * W / 100) + 'px)', 'translateX(0px)'] }, Object.assign({}, opts));
          if (seg) {
            seg.style.transformOrigin = mv.b > mv.a ? 'left center' : 'right center';
            anim(seg, { transform: ['scaleX(0)', 'scaleX(1)'] }, Object.assign({}, opts));
          }
        });
      });
    }
  }

  /* 09 · review forecast: selectable days, scrub with ticks, contained today. */
  var fcSel = {};
  function enhanceForecast(box, key) {
    if (!box || box.__nkg) return; box.__nkg = true;
    var cols = [].slice.call(box.querySelectorAll(':scope > span'));
    if (!cols.length) return;
    cols.forEach(function (c, i) {
      var b = c.querySelector('b'), s = c.querySelector('small');
      var n = parseInt(txt(b).replace(/,/g, ''), 10) || 0;
      c.classList.toggle('nkg-zero', n === 0);
      if (i === 0) c.classList.add('nkg-today');
      c.setAttribute('role', 'button');
      c.setAttribute('tabindex', '-1');
      c.setAttribute('aria-label', txt(s) + ': ' + n + (n === 1 ? ' review' : ' reviews') + ' due');
      c.dataset.n = n;
    });
    box.setAttribute('role', 'group');
    box.setAttribute('aria-label', 'Review forecast for the next seven days');
    var readout = el('div', 'nkg-fc-readout'); readout.setAttribute('role', 'status'); readout.setAttribute('aria-live', 'polite');
    box.parentNode.insertBefore(readout, box.nextSibling);
    var sel = fcSel[key] != null && fcSel[key] < cols.length ? fcSel[key] : 0;
    var DAY = { Mon: 'Monday', Tue: 'Tuesday', Wed: 'Wednesday', Thu: 'Thursday', Fri: 'Friday', Sat: 'Saturday', Sun: 'Sunday' };
    function select(i, fromUser) {
      if (i < 0 || i >= cols.length) return;
      if (fromUser && i !== sel) haptic('tick');
      sel = i; fcSel[key] = i;
      cols.forEach(function (c, j) { c.classList.toggle('is-selected', j === i); c.setAttribute('tabindex', j === i ? '0' : '-1'); c.setAttribute('aria-pressed', j === i ? 'true' : 'false'); });
      var c = cols[i], n = +c.dataset.n, day = txt(c.querySelector('small'));
      readout.innerHTML = '<strong>' + esc(DAY[day] || day) + '</strong> <span aria-hidden="true">—</span> <b>' + fmtInt(n) + '</b> <span>' + (n === 1 ? 'review due' : 'reviews due') + (n === 0 ? ' · a free day' : '') + '</span>';
    }
    function at(clientX) {
      for (var i = 0; i < cols.length; i++) { var r = cols[i].getBoundingClientRect(); if (clientX >= r.left - 2 && clientX <= r.right + 2) return i; }
      return -1;
    }
    var down = false;
    box.addEventListener('pointerdown', function (e) { down = true; var i = at(e.clientX); if (i >= 0) select(i, true); });
    box.addEventListener('pointermove', function (e) { if (!down) return; var i = at(e.clientX); if (i >= 0) select(i, true); });
    window.addEventListener('pointerup', function () { down = false; });
    box.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') { e.preventDefault(); select(sel + (e.key === 'ArrowRight' ? 1 : -1), true); cols[sel].focus(); }
      else if (e.key === 'Home') { e.preventDefault(); select(0, true); cols[0].focus(); }
      else if (e.key === 'End') { e.preventDefault(); select(cols.length - 1, true); cols[cols.length - 1].focus(); }
    });
    select(sel, false);
    if (changed('fc-' + key, txt(box)) && motionOK()) {
      var bars = cols.map(function (c) { return c.querySelector('i'); }).filter(Boolean);
      bars.forEach(function (b) { b.style.transform = 'scaleY(0)'; });
      onView(box, function () { bars.forEach(function (b, i) { anim(b, { transform: ['scaleY(0)', 'scaleY(1)'] }, { type: 'spring', stiffness: 300, damping: 26, delay: i * 0.04 }); }); });
    }
  }

  /* 12 · heatmap: dense ink grid, scroll to now, floating tooltip, one wave. */
  var heatTip = null, heatSeen = false, heatScroll = null;
  function heatTipEl() {
    if (!heatTip) { heatTip = el('div', 'nkg-heat-tip'); heatTip.setAttribute('aria-hidden', 'true'); document.body.appendChild(heatTip); }
    return heatTip;
  }
  function showHeatTip(btn) {
    var lab = btn.getAttribute('aria-label') || '';
    var m = lab.match(/^(.+?):\s*(\d[\d,]*)\s*(answers?)/);
    if (!m) return;
    var d = new Date(m[1]), day = isNaN(d) ? m[1] : d.toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' });
    var t = heatTipEl();
    t.innerHTML = '<b>' + esc(m[2]) + '</b> ' + esc(m[3]) + ' · ' + esc(day);
    var r = btn.getBoundingClientRect();
    t.style.left = Math.min(window.innerWidth - 80, Math.max(80, r.left + r.width / 2)) + 'px';
    t.style.top = r.top + 'px';
    t.classList.add('is-on');
  }
  function hideHeatTip() { if (heatTip) heatTip.classList.remove('is-on'); }
  window.addEventListener('scroll', hideHeatTip, { passive: true, capture: true });
  function enhanceHeatmap(card) {
    if (!card || card.__nkg) return; card.__nkg = true;
    var body = card.querySelector('.nk-li-year-body'), scroller = card.querySelector('.nk-li-year-scroll'), grid = card.querySelector('.nk-li-year-grid');
    if (!scroller || !grid) return;
    function edge() { body.classList.toggle('nkg-fade-l', scroller.scrollLeft > 4); }
    window.requestAnimationFrame(function () {
      scroller.scrollLeft = heatScroll != null ? heatScroll : scroller.scrollWidth;
      edge();
    });
    scroller.addEventListener('scroll', function () { heatScroll = scroller.scrollWidth - scroller.clientWidth - scroller.scrollLeft < 4 ? null : scroller.scrollLeft; edge(); hideHeatTip(); }, { passive: true });
    grid.addEventListener('pointerover', function (e) { var b = e.target.closest('button'); if (b && e.pointerType === 'mouse' && !b.disabled) showHeatTip(b); });
    grid.addEventListener('pointerout', function (e) { if (e.pointerType === 'mouse') hideHeatTip(); });
    grid.addEventListener('focusin', function (e) { var b = e.target.closest('button'); if (b) showHeatTip(b); });
    grid.addEventListener('focusout', hideHeatTip);
    grid.addEventListener('click', function (e) {
      var b = e.target.closest('button'); if (!b) return;
      haptic('selection');
      if (e.pointerType !== 'mouse') { window.requestAnimationFrame(function () { var nb = document.querySelector('.nk-li-year-grid .is-selected'); if (nb) { showHeatTip(nb); window.setTimeout(hideHeatTip, 1800); } }); }
    });
    if (!heatSeen && motionOK()) {
      heatSeen = true;
      /* One compositor animation for the whole year (hundreds of per-cell animations
         stall phones). */
      onView(grid, function () {
        anim(grid, { opacity: [0, 1], transform: ['translateY(6px)', 'translateY(0px)'] }, { duration: 0.36 });
      });
    }
  }

  /* ============================================================== Tests */
  function enhanceTests(app) {
    each(app.querySelectorAll('.nk-test-source-card'), function (c) {
      if (c.querySelector('.nkg-check')) return;
      var chk = el('span', 'nkg-check', icon('check', 13)); chk.setAttribute('aria-hidden', 'true');
      c.appendChild(chk);
      c.setAttribute('aria-pressed', c.classList.contains('active') ? 'true' : 'false');
      c.addEventListener('click', function () { if (!c.disabled) haptic('selection'); });
    });
    var grid = app.querySelector('.nk-test-count-grid');
    if (grid && !grid.__nkg) {
      grid.__nkg = true;
      grid.setAttribute('role', 'group'); grid.setAttribute('aria-label', 'Number of questions');
      each(grid.querySelectorAll('button'), function (b) { b.setAttribute('aria-pressed', b.classList.contains('active') ? 'true' : 'false'); });
      trackPill(grid, 'test-count', function () { return grid.querySelector('button.active'); });
      grid.addEventListener('click', function (e) { if (e.target.closest('button')) haptic('selection'); }, true);
      var p = grid.parentNode.querySelector(':scope > p');
      if (p && !p.querySelector('.nkg-num')) {
        p.innerHTML = p.innerHTML.replace(/^(\d[\d,]*)/, '<span class="nkg-num">$1</span>');
        countUp(p.querySelector('.nkg-num'), 'test-avail', false);
      }
    }
  }



  /* ================================================= Home · subject banks */
  /* Each subject shows how far you are through every bank it comes from. */
  function enhanceSubjects(app) {
    each(app.querySelectorAll('.nk-v3-subject-card[data-nk-banks]'), function (card) {
      if (card.__nkgBanks) return;
      var banks; try { banks = JSON.parse(card.getAttribute('data-nk-banks')); } catch (e) { return; }
      if (!banks || !banks.length) return;
      card.__nkgBanks = true;
      var copy = card.querySelector('.nk-v3-subject-copy'); if (!copy) return;
      var done = 0, total = 0;
      banks.forEach(function (b) { done += +b[1] || 0; total += +b[2] || 0; });
      card.classList.add('nkg-banked');
      var title = copy.querySelector('strong');
      if (title && !copy.querySelector('.nkg-subj-head')) {
        var head = el('span', 'nkg-subj-head');
        title.parentNode.insertBefore(head, title); head.appendChild(title);
        head.appendChild(el('em', 'nkg-subj-total', fmtInt(done) + ' / ' + fmtInt(total)));
      }
      var rows = el('span', 'nkg-bank-rows');
      banks.forEach(function (b) {
        var pct = b[2] ? Math.round(b[1] / b[2] * 100) : 0;
        var row = el('span', 'nkg-bank-row', '<span class="nkg-bank-name">' + esc(b[0]) + '</span><span class="nkg-bank-bar" role="presentation"><i></i></span><span class="nkg-bank-pct">' + pct + '%</span>');
        row.setAttribute('aria-label', b[0] + ': ' + fmtInt(b[1]) + ' of ' + fmtInt(b[2]) + ' questions, ' + pct + '%');
        rows.appendChild(row);
        var bar = row.querySelector('i');
        window.requestAnimationFrame(function () { window.requestAnimationFrame(function () { bar.style.transform = 'scaleX(' + ((pct ? Math.max(2, pct) : 0) / 100) + ')'; }); });
      });
      copy.appendChild(rows);
    });
  }

  /* ===================================================== CBT builder */
  /* Presentation only: the builder's markup, handlers and labels stay owned by the app. */
  var builderOpen = {};
  function enhanceBuilder(app) {
    var root = app.querySelector('.nk-cbt-builder, .nk-module-builder');
    if (!root) return;
    var steps = root.querySelectorAll('.nk-module-stepper > span'), step = 1;
    each(steps, function (s, i) { if (s.classList.contains('is-current')) step = i + 1; });
    root.classList.remove('nkg-step-1', 'nkg-step-2', 'nkg-step-3', 'nkg-step-4');
    root.classList.add('nkg-builder', 'nkg-step-' + step);
    /* Step 1 · sources grouped by bank, each row a compact checklist item. */
    var grid = root.querySelector('.nk-module-choice-grid');
    if (grid && !grid.__nkg) {
      grid.__nkg = true;
      var groups = {}, order = [];
      each([].slice.call(grid.querySelectorAll(':scope > .nk-module-subject')), function (b) {
        var meta = txt(b.querySelector('small')), bank = meta.split(' · ')[0] || 'Other';
        if (!groups[bank]) { groups[bank] = []; order.push(bank); }
        groups[bank].push(b);
        var title = b.querySelector('strong');
        if (title && !title.__nkg) { title.__nkg = true; var t = txt(title).replace(/^UWorld · /, ''); title.innerHTML = '<span class="nkg-sr-only">' + esc(txt(title)) + '</span><span aria-hidden="true">' + esc(t) + '</span>'; }
        var small = b.querySelector('small');
        if (small) small.textContent = meta.split(' · ').slice(1).join(' · ').replace(/\b1 topics\b/, '1 topic');
        if (!b.querySelector('.nkg-check')) { var c = el('span', 'nkg-check', icon('check', 13)); c.setAttribute('aria-hidden', 'true'); b.appendChild(c); }
        b.addEventListener('click', function () { haptic('selection'); });
      });
      grid.classList.add('nkg-bank-groups');
      order.forEach(function (bank) {
        var list = groups[bank], on = list.filter(function (b) { return b.classList.contains('is-selected'); }).length;
        var sec = el('section', 'nkg-bank-group');
        sec.appendChild(el('header', '', '<h3>' + esc(bank) + '</h3><span>' + on + ' of ' + list.length + '</span>'));
        var box = el('div', 'nkg-bank-list');
        list.forEach(function (b) { box.appendChild(b); });
        sec.appendChild(box); grid.appendChild(sec);
      });
    }
    /* Step 2 · groups collapse to their header so 260+ topics stay scannable; search opens them. */
    each(root.querySelectorAll('.nk-module-topic-group'), function (g) {
      var head = g.querySelector(':scope > header'), title = txt(g.querySelector('.nk-module-group-title'));
      if (!head || head.__nkg) return;
      head.__nkg = true;
      if (!(title in builderOpen)) builderOpen[title] = root.querySelectorAll('.nk-module-topic-group').length === 1;
      g.classList.toggle('is-collapsed', !builderOpen[title]);
      var tog = el('button', 'nkg-group-toggle', icon('caret-down', 16));
      tog.type = 'button';
      function sync() { var open = !g.classList.contains('is-collapsed'); tog.setAttribute('aria-expanded', String(open)); tog.setAttribute('aria-label', (open ? 'Hide ' : 'Show ') + title + ' topics'); }
      sync();
      tog.addEventListener('click', function () { g.classList.toggle('is-collapsed'); builderOpen[title] = !g.classList.contains('is-collapsed'); sync(); haptic('selection'); });
      head.appendChild(tog);
      var copy = head.querySelector(':scope > div');
      if (copy) { copy.style.cursor = 'pointer'; copy.addEventListener('click', function () { tog.click(); }); }
    });
    var search = root.querySelector('.nk-module-topic-search input');
    if (search && !search.__nkg) { search.__nkg = true; search.addEventListener('input', function () { root.classList.toggle('nkg-searching', Boolean(search.value.trim())); }); }
    /* Step 3 · the bank summary becomes compact chips. */
    var bankSum = root.querySelector('.nk-cbt-summary > div:first-child strong');
    if (bankSum && !bankSum.__nkg) {
      bankSum.__nkg = true;
      var parts = bankSum.innerHTML.split(/<br\s*\/?>/i).map(function (h) { var d = el('span'); d.innerHTML = h; return txt(d).replace(/^UWorld · (.+) · UWorld$/, 'UWorld · $1'); }).filter(Boolean);
      bankSum.innerHTML = parts.map(function (t) { return '<span class="nkg-chip">' + esc(t) + '</span>'; }).join('');
      bankSum.classList.add('nkg-chips');
    }
    /* Step 2 · topic rows get the same check affordance. */
    each(root.querySelectorAll('.nk-module-topic .nk-module-check'), function (c) { c.classList.add('nkg-check'); if (!c.querySelector('svg')) c.innerHTML = icon('check', 13); });
    /* Step 3 · presets become a segmented control. */
    var presets = root.querySelector('.nk-cbt-count-grid, .nk-module-count-presets');
    if (presets && !presets.__nkg) {
      presets.__nkg = true;
      presets.classList.add('nkg-seg', 'nkg-seg-fill');
      presets.setAttribute('role', 'group'); presets.setAttribute('aria-label', 'Number of questions');
      each(presets.querySelectorAll('button'), function (b) { b.setAttribute('aria-pressed', b.classList.contains('is-selected') ? 'true' : 'false'); });
      trackPill(presets, 'cbt-count', function () { return presets.querySelector('button.is-selected'); });
      presets.addEventListener('click', function (e) { if (e.target.closest('button')) haptic('selection'); }, true);
    }
    /* The dock states what will be built before you commit. */
    var dock = root.querySelector('.nk-cbt-main-actions, .nk-module-builder-actions');
    if (dock && step === 1 && !dock.querySelector('.nkg-dock-sum, [id$="-footer-count"]')) {
      var rowsAll = root.querySelectorAll('.nk-module-choice-grid .nk-module-subject'), on = root.querySelectorAll('.nk-module-choice-grid .nk-module-subject.is-selected').length;
      if (rowsAll.length) dock.insertBefore(el('span', 'nkg-dock-sum', on + ' of ' + rowsAll.length + ' banks selected'), dock.firstChild);
    }
    /* Module question pool reads as a single-choice list. */
    each(root.querySelectorAll('.nk-module-pool-grid > button'), function (b) {
      if (b.querySelector('.nkg-radio')) return;
      b.setAttribute('aria-pressed', b.classList.contains('is-selected') ? 'true' : 'false');
      var r = el('span', 'nkg-radio'); r.setAttribute('aria-hidden', 'true'); b.appendChild(r);
    });
  }

  /* =========================================================== Revision */
  function enhanceRevision(app) {
    each(app.querySelectorAll('.nk-review-chart'), function (f) { enhanceForecast(f, 'rev'); });
    each(app.querySelectorAll('.nk-revision-card-head > b'), function (b, i) { countUp(b, 'rev-' + i, false); });
  }

  /* ======================================================= top bar + page */
  var titleIO = null, lastRoute = null;
  function pageTitle(app) { return app.querySelector('main.page :is(.nk-v3-page-hero, .nk-page-head, .nk-li-head, .nkg-home-head) h1, main.page .nkg-profile-name') || app.querySelector('main.page h1'); }
  function syncTopbar(app, page, session) {
    var bar = document.querySelector('.nkg-topbar');
    if (!bar) return;
    var brand = bar.querySelector('.nkg-brand');
    if (brand && !brand.querySelector('.nkg-topbar-wordmark')) {
      var wm = el('span', 'nkg-topbar-wordmark'); wm.textContent = 'NK QBank';
      brand.insertBefore(wm, brand.querySelector('.nkg-topbar-title'));
    }
    var h1 = session ? null : pageTitle(app);
    if (titleIO) { titleIO.disconnect(); titleIO = null; }
    bar.classList.toggle('has-page-title', !!h1);
    if (h1 && window.IntersectionObserver) {
      var topH = bar.getBoundingClientRect().height || 56;
      titleIO = new IntersectionObserver(function (es) { es.forEach(function (e) { bar.classList.toggle('show-title', !e.isIntersecting && e.boundingClientRect.top < topH); }); },
        { rootMargin: '-' + Math.round(topH) + 'px 0px 0px 0px', threshold: 0 });
      titleIO.observe(h1);
    } else bar.classList.add('show-title');
    onScroll();
  }
  function onScroll() {
    var bar = document.querySelector('.nkg-topbar');
    if (bar) bar.classList.toggle('is-scrolled', (window.scrollY || document.documentElement.scrollTop || 0) > 2);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  function pageEnter(app, page, session) {
    var key = page + (session ? ':s' : '');
    if (lastRoute === null) { lastRoute = key; return; }
    if (key === lastRoute) return;
    lastRoute = key;
    var main = app.querySelector('main.page');
    if (main && !session) anim(main, { opacity: [0, 1], transform: ['translateY(6px)', 'none'] }, { duration: 0.26 });
  }

  /* ===================================================== global feedback */
  /* Web-only touch feedback for app controls (Android native already plays its own). */
  document.addEventListener('pointerdown', function (e) {
    if (Haptics.hasNative() || e.pointerType === 'mouse') return;
    var t = e.target.closest && e.target.closest('.bottom-nav .nav-item, .option:not(.correct):not(.wrong), .nk-v3-subject-card, .nk-revision-actions > button, .nk-home-revision-counts button');
    if (t) haptic('selection');
  }, { passive: true, capture: true });
  /* Answer outcome: one success / error pulse when the feedback appears. */
  var lastOutcome = null;
  function answerFeedback(app) {
    var o = app.querySelector('.nk-answer-outcome');
    var sig = o ? txt(o) + '|' + txt(app.querySelector('.nk-session-count')) : null;
    if (o && sig !== lastOutcome && lastOutcome !== null && !Haptics.hasNative()) haptic(o.classList.contains('is-wrong') ? 'error' : 'success');
    if (o && sig !== lastOutcome) {
      var picked = app.querySelector('.option.correct .option-letter, .option.wrong .option-letter');
      each(app.querySelectorAll('.option.correct .option-letter, .option.wrong .option-letter'), function (l) { anim(l, { transform: ['scale(.7)', 'scale(1)'] }, { type: 'spring', stiffness: 520, damping: 18 }); });
      if (picked) anim(o, { opacity: [0, 1], transform: ['translateY(-3px)', 'none'] }, { duration: 0.22 });
    }
    lastOutcome = sig || lastOutcome;
  }

  /* ================================================================ entry */

  /* ===================================================== Test result follow-ups */
  /* Missed / marked / save-as-mock become one tappable action list: icon, task, count.
     The app's buttons (and their handlers) stay; the card only re-composes them. */
  function enhanceResult(app) {
    each(app.querySelectorAll('.nk-na-followup:not(.nkg-action)'), function (sec) {
      var btn = sec.querySelector(':scope > button'), label = sec.querySelector(':scope > strong');
      var marked = sec.classList.contains('nk-cbt-marked');
      sec.classList.add('nkg-action', btn ? (marked ? 'is-marked' : 'is-missed') : 'is-clear');
      var ic = el('span', 'nkg-action-icon', icon(btn ? (marked ? 'star' : 'arrows-clockwise') : 'check-circle', 18));
      ic.setAttribute('aria-hidden', 'true');
      sec.insertBefore(ic, sec.firstChild);
      if (btn && !btn.querySelector('.nkg-action-chev')) {
        each(btn.querySelectorAll('svg'), function (svg) { svg.remove(); });
        btn.insertAdjacentHTML('beforeend', '<span class="nkg-action-chev" aria-hidden="true">' + icon('caret-right', 16) + '</span>');
      }
    });
    var save = app.querySelector('.nk-na-save-mock:not(.nkg-action)');
    if (save) {
      save.classList.add('nkg-action', 'is-save');
      var t = save.textContent.trim();
      save.setAttribute('aria-label', t);
      save.innerHTML = '<span class="nkg-action-icon" aria-hidden="true">' + icon('stack', 18) + '</span>' +
        '<span class="nkg-action-text"><b>' + esc(t) + '</b><small>Reuse this exact set of questions later</small></span>' +
        '<span class="nkg-action-chev" aria-hidden="true">' + icon('caret-right', 16) + '</span>';
    }
  }


  /* Answered UWorld options carry the source pick-rate; expose it to CSS for a bar. */
  function cohortChip(app) {
    var c = app.querySelector('.nk-uworld-cohort:not(.nkg-cohort)'); if (!c) return;
    var st = c.querySelector('strong'); var m = st && st.textContent.match(/(\d+)\s*%/); if (!m) return;
    var n = Math.max(0, Math.min(100, +m[1]));
    c.classList.add('nkg-cohort', n >= 70 ? 'is-easy' : n < 40 ? 'is-hard' : 'is-mid');
    c.setAttribute('aria-label', n + '% of UWorld users answered correctly');
    st.innerHTML = '<b>' + n + '%</b><small>got it right</small>';
    var bar = el('span', 'nkg-cohort-bar', '<i></i>'); bar.setAttribute('aria-hidden', 'true'); bar.style.setProperty('--nkg-p', String(n));
    c.appendChild(bar);
  }
  function optionRates(app) {
    each(app.querySelectorAll('.option-list .option'), function (o) {
      var p = o.querySelector('.nk-uworld-option-percent');
      var n = p ? parseInt(p.textContent, 10) : NaN;
      if (isNaN(n)) { if (o.style.getPropertyValue('--nkg-pct')) o.style.removeProperty('--nkg-pct'); return; }
      if (o.style.getPropertyValue('--nkg-pct') !== String(n)) o.style.setProperty('--nkg-pct', String(Math.max(0, Math.min(100, n))));
    });
  }


  /* Practice v3: question eyebrow, answered-state hook, letter badges for choice notes. */
  function practiceScreen(app) {
    var card = app.querySelector('.qbank-session-page .question-card');
    if (!card) return;
    var count = app.querySelector('.nk-session-count');
    var m = count && count.textContent.replace(/\s+/g, ' ').match(/(\d+)\s*\/\s*(\d+)/);
    var eb = card.querySelector(':scope > .nkg-q-eyebrow');
    var label = m ? 'Question ' + m[1] + ' of ' + m[2] : '';
    if (label && (!eb || eb.getAttribute('data-l') !== label)) {
      if (!eb) { eb = el('div', 'nkg-q-eyebrow'); card.insertBefore(eb, card.firstChild); }
      eb.setAttribute('data-l', label); eb.textContent = label;
      var bank = app.querySelector('.nk-uworld-stem') ? 'UWorld' : '';
      if (bank) eb.insertAdjacentHTML('beforeend', '<i>' + bank + '</i>');
    }
    var list = card.querySelector('.option-list');
    if (list) list.classList.toggle('nkg-answered', !!list.querySelector('.option.correct, .option.wrong'));
    each(app.querySelectorAll('.nk-uworld-choice-discussion:not([data-nkg-l])'), function (a) {
      var h = a.querySelector('h4'); if (!h) return;
      var letters = (h.textContent.replace(/^Choices?\s*/i, '').match(/\b[A-L]\b/g) || []);
      if (letters.length) a.setAttribute('data-nkg-l', letters.join(' · '));
    });
  }

  function render(app, page, session) {
    if (!app) return;
    try {
      syncTopbar(app, page, session);
      pageEnter(app, page, session);
      if (page === 'dashboard') { enhanceHome(app); enhanceSubjects(app); }
      else if (page === 'analytics') enhanceInsights(app);
      else if (page === 'tests' || page === 'test-builder') enhanceTests(app);
      else if (page === 'quick-revision' || page === 'fsrs') enhanceRevision(app);
      enhanceBuilder(app);
      if (app.querySelector('.nk-na-followup, .nk-na-save-mock')) enhanceResult(app);
      if (session) { answerFeedback(app); optionRates(app); cohortChip(app); practiceScreen(app); }
    } catch (e) {
      if (window.console && console.warn) console.warn('NKFeel', e);
    }
  }
  window.NKFeel = { render: render, haptic: haptic };
})();
