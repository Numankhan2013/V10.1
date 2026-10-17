/* NK QBank — Geist redesign runtime.
 *
 * Loaded synchronously in <head> so the theme is applied before first paint.
 * It owns only presentation: the theme switch, the top bar, Phosphor icon
 * swaps, the Home greeting, the Appearance controls in More and the additive
 * Profile screen.  Study logic, storage and navigation stay with the app; this
 * file only reads progress (window.QB.getState / saved auth) and calls the
 * app's existing public actions (window.QB.nav, ...).
 *
 * Geist is the only UI; the old ?ui=legacy switch has been retired.
 *   localStorage "nkq.theme" = light | dark | system (default system).
 */
(function () {
  'use strict';
  var doc = document.documentElement;
  var THEME_KEY = 'nkq.theme', NAME_KEY = 'nkq.profile.name';

  function lsGet(k) { try { return window.localStorage.getItem(k); } catch (e) { return null; } }
  function lsSet(k, v) { try { window.localStorage.setItem(k, v); } catch (e) { /* storage blocked */ } }

  /* Forget a saved choice of the retired legacy UI. */
  try { window.localStorage.removeItem('nkq.ui'); } catch (e) { /* storage blocked */ }
  window.NKQ_UI = { mode: 'geist' };
  doc.setAttribute('data-nk-ui', 'geist');
  /* Android app shell (MainActivity NK_NATIVE_FEEL_V1): app-like touch
     behaviour, and the system bars follow the theme below. */
  var shell = window.QBankShell && typeof window.QBankShell.platform === 'function' ? window.QBankShell : null;
  if (shell) doc.classList.add('nk-android-shell');
  /* Route attribute is set before the app's first render and before its own
     hashchange handler, so route-scoped CSS (e.g. #profile) never flashes. */
  (function () {
    function r() { return (location.hash.replace(/^#/, '').split('/')[0]) || 'dashboard'; }
    doc.setAttribute('data-nkg-route', r());
    window.addEventListener('hashchange', function () { doc.setAttribute('data-nkg-route', r()); });
  })();

  /* ------------------------------------------------------------------ theme */
  var media = window.matchMedia ? window.matchMedia('(prefers-color-scheme: dark)') : null;
  function themePref() { var t = lsGet(THEME_KEY); return t === 'light' || t === 'dark' ? t : 'system'; }
  function resolvedTheme() {
    var p = themePref();
    return p === 'system' ? (media && media.matches ? 'dark' : 'light') : p;
  }
  function applyTheme() {
    var t = resolvedTheme();
    doc.setAttribute('data-nk-theme', t);
    doc.setAttribute('data-nk-theme-pref', themePref());
    var color = t === 'dark' ? '#0a0a0a' : '#ffffff';
    var metas = document.querySelectorAll('meta[name="theme-color"]');
    for (var i = 0; i < metas.length; i++) metas[i].setAttribute('content', color);
    if (shell && shell.theme) { try { shell.theme(t === 'dark'); } catch (e) { /* older shell */ } }
    syncThemeControls();
  }
  var themePt = null;
  document.addEventListener('pointerdown', function (e) { themePt = { x: e.clientX, y: e.clientY }; }, true);
  function setTheme(pref) {
    lsSet(THEME_KEY, pref);
    var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var before = doc.getAttribute('data-nk-theme');
    /* The new theme spreads in a circle from where it was chosen. */
    if (document.startViewTransition && !reduce && resolvedTheme() !== before) {
      var pt = themePt || { x: window.innerWidth - 60, y: 28 };
      var rad = Math.hypot(Math.max(pt.x, window.innerWidth - pt.x), Math.max(pt.y, window.innerHeight - pt.y));
      doc.classList.add('nkg-vt-theme');
      try {
        var vt = document.startViewTransition(function () { applyTheme(); });
        vt.ready.then(function () {
          doc.animate({ clipPath: ['circle(0px at ' + pt.x + 'px ' + pt.y + 'px)', 'circle(' + rad + 'px at ' + pt.x + 'px ' + pt.y + 'px)'] },
            { duration: 560, easing: 'cubic-bezier(.23, 1, .32, 1)', pseudoElement: '::view-transition-new(root)' });
        }, function () {});
        vt.finished.then(function () { doc.classList.remove('nkg-vt-theme'); }, function () { doc.classList.remove('nkg-vt-theme'); });
        return;
      } catch (e) { doc.classList.remove('nkg-vt-theme'); }
    }
    doc.classList.add('nkg-theme-switching');
    applyTheme();
    window.setTimeout(function () { doc.classList.remove('nkg-theme-switching'); }, 240);
  }
  if (media) {
    var onScheme = function () { if (themePref() === 'system') applyTheme(); };
    if (media.addEventListener) media.addEventListener('change', onScheme); else if (media.addListener) media.addListener(onScheme);
  }
  window.NKQ_UI.setTheme = setTheme;
  window.NKQ_UI.metrics = function () { return lifetime(); };
  window.NKQ_UI.theme = resolvedTheme;
  applyTheme();

  /* ------------------------------------------------------------------ icons */
  var ICON_MAP = {
    home: 'house', book: 'book-open', test: 'clipboard-text', chart: 'chart-line-up', bookmark: 'bookmark-simple',
    clock: 'clock', search: 'magnifying-glass', bell: 'bell', star: 'star', trash: 'trash', refresh: 'arrows-clockwise',
    share: 'share-network', molecule: 'atom', bulb: 'lightbulb', heart: 'heart', body: 'person', dna: 'dna',
    // Subjects and UWorld collections: Healthicons organ glyphs ("hi-"), Phosphor where it reads better.
    biochemistry: 'dna', physiology: 'hi-heart-cardiogram', anatomy: 'hi-skeleton', poisoning: 'hi-poison', biostatistics: 'chart-bar',
    ophthalmology: 'hi-eye', 'male-reproductive': 'hi-testicles', 'female-reproductive': 'hi-female-reproductive-system', pregnancy: 'hi-pregnant',
    pharmacology: 'hi-pills-2', pathology: 'hi-microscope', endocrine: 'hi-thyroid', psychiatry: 'brain', cardiovascular: 'hi-heart-organ',
    renal: 'hi-kidneys', gastrointestinal: 'hi-stomach', rheumatology: 'hi-joints', pulmonary: 'hi-lungs',
    uworld: 'books', back: 'arrow-left', chevron: 'caret-right', check: 'check', close: 'x', pause: 'pause',
    menu: 'list', more: 'dots-three', grid: 'squares-four', minus: 'minus', edit: 'pencil-simple', stopwatch: 'timer'
  };
  function iconSvg(name, size, cls) {
    var body = (window.NKQ_ICONS || {})[name] || '';
    size = size || 20;
    return '<svg class="nkg-ph' + (cls ? ' ' + cls : '') + '" data-nkg-icon="' + name + '" width="' + size + '" height="' + size +
      '" viewBox="0 0 256 256" fill="currentColor" aria-hidden="true" focusable="false">' + body + '</svg>';
  }
  function swapIcon(svg, name) {
    var body = (window.NKQ_ICONS || {})[name];
    if (!body) return;
    svg.setAttribute('viewBox', '0 0 256 256');
    svg.setAttribute('fill', 'currentColor');
    svg.removeAttribute('stroke');
    svg.removeAttribute('stroke-width');
    svg.setAttribute('data-nkg-icon', name);
    svg.innerHTML = body;
  }
  function swapIcons(root) {
    var list = root.querySelectorAll('svg[data-nk-icon]:not([data-nkg-icon])');
    for (var i = 0; i < list.length; i++) {
      var legacy = list[i].getAttribute('data-nk-icon');
      if (ICON_MAP[legacy]) swapIcon(list[i], ICON_MAP[legacy]);
      // Bookmark buttons carry both shapes; CSS shows the filled one while .bookmarked,
      // so the saved state reads at a glance without a toast or a re-render.
      if (legacy === 'bookmark' && list[i].closest('.bookmark-toggle') && (window.NKQ_ICONS || {})['bookmark-simple-fill']) {
        list[i].innerHTML = '<g class="nkg-off">' + list[i].innerHTML + '</g><g class="nkg-on">' + window.NKQ_ICONS['bookmark-simple-fill'] + '</g>';
      }
    }
    var flames = root.querySelectorAll('.nk-flame-svg:not([data-nkg-icon]), .nk-streak-flame-svg:not([data-nkg-icon])');
    for (var j = 0; j < flames.length; j++) swapIcon(flames[j], 'fire-fill');
    var arrows = root.querySelectorAll('.nk-home-focus-action > span:last-child');
    for (var k = 0; k < arrows.length; k++) {
      if (arrows[k].textContent.trim() === '\u2192') { arrows[k].className = 'nkg-arrow'; arrows[k].innerHTML = iconSvg('arrow-right', 18); }
    }
    var carets = root.querySelectorAll('.nk-home-range > span');
    for (var c = 0; c < carets.length; c++) {
      if (carets[c].textContent.trim() === '\u2304') { carets[c].className = 'nkg-caret'; carets[c].innerHTML = iconSvg('caret-down', 14); }
    }
  }

  /* --------------------------------------------------------------- helpers */
  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>'"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[c];
    });
  }
  function fmt(n) { try { return new Intl.NumberFormat('en-IN').format(Math.round(n || 0)); } catch (e) { return String(Math.round(n || 0)); } }
  function route() { return (location.hash.replace(/^#/, '').split('/')[0]) || 'dashboard'; }
  function profileName() { return (lsGet(NAME_KEY) || '').trim(); }
  function initials(name) {
    var parts = String(name || '').trim().split(/\s+/).filter(Boolean);
    if (!parts.length) return 'NK';
    return ((parts[0][0] || '') + (parts.length > 1 ? parts[parts.length - 1][0] : (parts[0][1] || ''))).toUpperCase();
  }
  function appState() {
    try { if (window.QB && typeof window.QB.getState === 'function') return window.QB.getState() || {}; } catch (e) { /* not booted */ }
    return {};
  }
  function savedAuth() {
    try { var a = JSON.parse(lsGet('qbank_firebase_auth_v1') || 'null'); return a && a.uid ? a : null; } catch (e) { return null; }
  }
  function syncMeta() { try { return JSON.parse(lsGet('qbank_sync_v1') || 'null') || {}; } catch (e) { return {}; } }
  function go(page, id) { if (window.QB && typeof window.QB.nav === 'function') window.QB.nav(page, id); else location.hash = page + (id ? '/' + id : ''); }
  function dayKey(ts) { var d = new Date(Number(ts)); return d.getFullYear() + '-' + (d.getMonth() + 1) + '-' + d.getDate(); }
  function haptic() { try { if (window.QBankHaptics && typeof window.QBankHaptics.play === 'function') window.QBankHaptics.play('choice'); } catch (e) { /* web: no haptics */ } }

  /* -------------------------------------------------------------- metrics
   * Same definitions as the app's own counters: attempts exclude undo/rating
   * revision entries; study time = non-exam answer time + timed-test time;
   * a streak day is any day with a recorded answer. */
  function subjectOf(id) {
    id = String(id);
    if (/^marrow__ANAT|^anatomy-/i.test(id)) return 'Anatomy';
    if (/^marrow__PHYS|^physiology-/i.test(id)) return 'Physiology';
    if (/^marrow__BIOCHEM|^\d+-\d+$/i.test(id)) return 'Biochemistry';
    if (/^marrow__MICRO|^microbiology-/i.test(id)) return 'Microbiology';
    if (/^UWORLD_/i.test(id)) return 'My UWorld';
    return 'Other';
  }
  function lifetime() {
    var s = appState(), attempts = s.attempts || {}, tests = Array.isArray(s.tests) ? s.tests : [];
    var total = 0, correct = 0, unique = 0, practiceMs = 0, reviews = 0, days = {}, subjects = {};
    Object.keys(attempts).forEach(function (qid) {
      var list = Array.isArray(attempts[qid]) ? attempts[qid] : [], counted = false;
      var sub = subjectOf(qid), undone = {};
      list.forEach(function (a) { if (a && a.isUndo && a.undoOf) undone[String(a.undoOf)] = true; });
      list.forEach(function (a) {
        if (!a || a.isUndo || a.isRatingRevision || typeof a.correct !== 'boolean' || undone[String(a.id)]) return;
        total++; if (a.correct) correct++;
        if (a.source !== 'exam') practiceMs += Math.max(0, Number(a.timeSpent) || 0);
        if (a.rating != null && a.schedulerVersion) reviews++;
        if (a.at) days[dayKey(a.at)] = (days[dayKey(a.at)] || 0) + 1;
        var row = subjects[sub] || (subjects[sub] = { answered: 0, correct: 0, unique: 0 });
        row.answered++; if (a.correct) row.correct++;
        if (!counted) { counted = true; unique++; row.unique++; }
      });
    });
    var testMs = tests.filter(function (t) { return t && t.kind !== 'practice'; })
      .reduce(function (n, t) { return n + Math.max(0, Number(t.totalTimeMs) || 0); }, 0);
    // Streaks.
    var cur = 0, best = 0, run = 0, today = new Date(); today.setHours(0, 0, 0, 0);
    var cursor = new Date(today);
    if (!days[dayKey(cursor)]) cursor.setDate(cursor.getDate() - 1);
    while (days[dayKey(cursor)]) { cur++; cursor.setDate(cursor.getDate() - 1); }
    var keys = Object.keys(days).map(function (k) { var p = k.split('-'); return new Date(+p[0], +p[1] - 1, +p[2]).getTime(); }).sort(function (a, b) { return a - b; });
    var prev = null;
    keys.forEach(function (t) {
      run = prev != null && Math.round((t - prev) / 86400000) === 1 ? run + 1 : 1;
      if (run > best) best = run; prev = t;
    });
    return {
      total: total, correct: correct, unique: unique, accuracy: total ? correct / total * 100 : null,
      studyMs: practiceMs + testMs, reviews: reviews, tests: tests.filter(function (t) { return t && t.kind !== 'practice'; }).length,
      current: cur, best: Math.max(best, cur), days: days, subjects: subjects,
      bookmarks: Object.keys(s.bookmarks || {}).filter(function (k) { return s.bookmarks[k]; }).length,
      notes: Object.keys(s.questionNotes || {}).filter(function (k) { var n = s.questionNotes[k]; return n && (typeof n === 'string' ? n.trim() : (n.text || '').trim()); }).length
    };
  }
  function fmtDuration(ms) {
    var m = Math.round((ms || 0) / 60000);
    if (!m) return '0m';
    var h = Math.floor(m / 60);
    return (h ? h + 'h ' : '') + (m % 60) + 'm';
  }

  /* ---------------------------------------------------------------- top bar */
  var TITLES = {
    dashboard: 'Home', 'quick-revision': 'Revision', fsrs: 'Revision', 'revision-browse': 'Revision', 'fsrs-settings': 'Revision settings',
    tests: 'Tests', 'test-builder': 'New test', analytics: 'Insights', more: 'More', profile: 'Profile',
    topics: 'Topics', chapter: 'Topic', banks: 'Question banks', uworld: 'My UWorld', 'study-library': 'Library',
    'question-search': 'Find a question', notes: 'My notes', bookmarks: 'Bookmarks', wrong: 'Mistakes', review: 'Review',
    'module-builder': 'Study module', result: 'Result'
  };
  var topbar = null;
  function buildTopbar() {
    if (topbar || !document.body) return;
    topbar = document.createElement('header');
    topbar.className = 'nkg-topbar';
    topbar.innerHTML =
      '<div class="nkg-topbar-inner">' +
      '<button type="button" class="nkg-brand" data-nkg-act="home" aria-label="NK QBank home"><span class="nkg-logo" aria-hidden="true"><svg viewBox="8.8 8.8 79.61 79.61" fill="currentColor"><path fill-rule="evenodd" d="M10 46a36 36 0 1 0 72 0a36 36 0 1 0-72 0ZM26.5 43.5a17 17 0 1 0 34 0a17 17 0 1 0-34 0Z"/><path d="M55.02 80.85A12 12 0 0 1 67.37 84.95L84.95 67.37A12 12 0 0 1 80.85 55.02Z"/><path d="M64.61 77.11a12.5 12.5 0 1 0 25 0a12.5 12.5 0 1 0-25 0Z"/></svg></span><span class="nkg-topbar-title">Home</span></button>' +
      '<span class="nkg-grow"></span>' +
      '<button type="button" class="nkg-icon-btn" data-nkg-act="search" aria-label="Find a question">' + iconSvg('magnifying-glass', 20) + '</button>' +
      '<button type="button" class="nkg-icon-btn nkg-theme-toggle" data-nkg-act="theme" aria-label="Switch theme">' + iconSvg('moon', 20, 'nkg-moon') + iconSvg('sun', 20, 'nkg-sun') + '</button>' +
      '<button type="button" class="nkg-avatar-btn" data-nkg-act="profile" aria-label="Open profile"><span class="nkg-avatar">' + esc(initials(profileName())) + '</span></button>' +
      '</div>';
    var app = document.getElementById('app');
    document.body.insertBefore(topbar, app || document.body.firstChild);
    syncThemeControls();
  }
  function updateTopbar(page, session) {
    if (!topbar) return;
    topbar.hidden = !!session;
    var title = topbar.querySelector('.nkg-topbar-title');
    if (title) title.textContent = TITLES[page] || 'NK QBank';
    var av = topbar.querySelector('.nkg-avatar');
    if (av) av.textContent = initials(profileName());
    var pb = topbar.querySelector('[data-nkg-act="profile"]');
    if (pb) pb.setAttribute('aria-current', page === 'profile' ? 'page' : 'false');
  }
  function syncThemeControls() {
    var t = doc.getAttribute('data-nk-theme'), pref = doc.getAttribute('data-nk-theme-pref');
    var toggles = document.querySelectorAll('[data-nkg-act="theme"]');
    for (var i = 0; i < toggles.length; i++) toggles[i].setAttribute('aria-label', t === 'dark' ? 'Switch to light theme' : 'Switch to dark theme');
    var seg = document.querySelectorAll('[data-nkg-theme-choice]');
    for (var j = 0; j < seg.length; j++) seg[j].setAttribute('aria-pressed', seg[j].getAttribute('data-nkg-theme-choice') === pref ? 'true' : 'false');
  }

  /* ------------------------------------------------------------ Home head */
  function decorateHome(app) {
    var greet = app.querySelector('.nk-home-greeting');
    if (!greet || app.querySelector('.nkg-home-head')) return;
    var h = new Date().getHours(), hello = h < 12 ? 'Good morning' : h < 18 ? 'Good afternoon' : 'Good evening';
    var name = profileName().split(/\s+/)[0];
    var date;
    try { date = new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long' }); } catch (e) { date = new Date().toDateString(); }
    var head = document.createElement('section');
    head.className = 'nkg-home-head';
    head.innerHTML = '<p class="nkg-date">' + esc(date) + '</p><h1>' + esc(hello) + (name ? ', ' + esc(name) : '') + '</h1>';
    greet.parentNode.insertBefore(head, greet);
    var label = app.querySelector('.nk-home-focus-label');
    if (label && /^TODAY.S FOCUS$/.test(label.textContent.trim())) label.textContent = 'Today\u2019s focus';
  }

  /* ---------------------------------------------------- More: Appearance */
  function appearanceMarkup() {
    var choice = function (val, label, icon) {
      return '<button type="button" data-nkg-theme-choice="' + val + '" aria-pressed="false">' + iconSvg(icon, 16) + '<span>' + label + '</span></button>';
    };
    return '<section class="nk-settings-group nkg-appearance" aria-labelledby="nkg-appearance-title">' +
      '<h2 class="nkg-group-title" id="nkg-appearance-title">Profile &amp; appearance</h2>' +
      '<div class="nkg-appearance-card">' +
      '<button type="button" class="nkg-profile-row" data-nkg-act="profile"><span class="nkg-avatar">' + esc(initials(profileName())) + '</span>' +
      '<span class="nkg-row-copy"><strong>' + esc(profileName() || 'Your profile') + '</strong></span>' + iconSvg('caret-right', 16, 'nkg-chev') + '</button>' +
      '<div class="nkg-theme-row"><span class="nkg-row-copy"><strong>Theme</strong></span>' +
      '<div class="nkg-seg" role="group" aria-label="Theme">' + choice('light', 'Light', 'sun') + choice('dark', 'Dark', 'moon') + choice('system', 'System', 'desktop') + '</div></div>' +
      '</div></section>';
  }
  function decorateMore(app) {
    if (app.querySelector('.nkg-appearance')) return;
    var host = app.querySelector('.nk-more-v114');
    if (!host) return;
    var firstGroup = host.querySelector('.nk-settings-group');
    var wrap = document.createElement('div');
    wrap.innerHTML = appearanceMarkup();
    var node = wrap.firstChild;
    if (firstGroup) firstGroup.parentNode.insertBefore(node, firstGroup); else host.appendChild(node);
    // One list for the app's tools: notes, search, revision settings and the source PDF.
    // Reset progress leaves the PDF card and becomes a quiet row of its own at the end.
    var list = host.querySelector('.nk-settings-row') && host.querySelector('.nk-settings-row').parentNode;
    var row = function (icon, label) {
      return '<span class="nk-settings-icon">' + iconSvg(icon, 18) + '</span><span><strong>' + label + '</strong></span>' + iconSvg('caret-right', 16, 'nkg-chev');
    };
    var fsrs = app.querySelector('.nk-fsrs-settings-entry');
    if (list && fsrs) {
      var b = document.createElement('button');
      b.type = 'button'; b.className = 'nk-settings-row nkg-row-added'; b.setAttribute('onclick', "window.QB.nav('fsrs-settings')");
      b.innerHTML = row('gear', 'Revision settings');
      list.appendChild(b); fsrs.remove();
    }
    if (list && window.NKStore) {
      var r = document.createElement('button');
      r.type = 'button'; r.className = 'nk-settings-row nkg-row-added'; r.setAttribute('data-nkg-act', 'restore');
      r.innerHTML = row('arrow-counter-clockwise', 'Restore points');
      list.appendChild(r);
    }
    var source = host.querySelector('.nk-source-card');
    if (list && source) {
      var pdf = source.querySelector('a[href]'), reset = source.querySelector('button[onclick*="resetProgress"]');
      if (pdf) {
        var a = document.createElement('a');
        a.className = 'nk-settings-row nkg-row-added'; a.href = pdf.getAttribute('href'); a.target = '_blank'; a.rel = 'noopener';
        a.innerHTML = row('file-pdf', 'Source PDF');
        list.appendChild(a);
      }
      var group = source.closest('.nk-settings-group');
      if (reset && group) {
        group.innerHTML = '<button type="button" class="nkg-reset-row" onclick="window.QB.resetProgress()">' + iconSvg('arrow-counter-clockwise', 16) + '<span>Reset progress</span></button>';
      }
    }
    guardReset();
    syncThemeControls();
  }

  /* --------------------------------------------------------------- Profile */
  function heatmap(days) {
    var weeks = 18, cells = [], today = new Date(); today.setHours(0, 0, 0, 0);
    var start = new Date(today); start.setDate(start.getDate() - (weeks * 7 - 1) - ((today.getDay() + 6) % 7 === 6 ? 0 : 0));
    // Align the first column to Monday.
    start.setDate(start.getDate() - ((start.getDay() + 6) % 7));
    var max = 0;
    Object.keys(days).forEach(function (k) { if (days[k] > max) max = days[k]; });
    for (var d = new Date(start); d <= today; d.setDate(d.getDate() + 1)) {
      var n = days[dayKey(d.getTime())] || 0;
      var lvl = !n ? 0 : n >= max * 0.75 ? 4 : n >= max * 0.5 ? 3 : n >= max * 0.25 ? 2 : 1;
      var label;
      try { label = d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' }); } catch (e) { label = d.toDateString(); }
      cells.push('<i data-l="' + lvl + '" title="' + esc(label + ': ' + n + (n === 1 ? ' answer' : ' answers')) + '"></i>');
    }
    return '<div class="nkg-heatmap-wrap"><div class="nkg-heatmap" role="img" aria-label="Answers per day over the last ' + weeks + ' weeks">' + cells.join('') + '</div></div>' +
      '<div class="nkg-legend" aria-hidden="true"><span>Less</span><i data-l="0"></i><i data-l="1"></i><i data-l="2"></i><i data-l="3"></i><i data-l="4"></i><span>More</span></div>';
  }
  function profileMarkup() {
    var m = lifetime(), name = profileName(), auth = savedAuth(), meta = syncMeta();
    var stat = function (label, value, sub) {
      return '<div class="nkg-stat"><span class="nkg-stat-label">' + label + '</span><strong class="nkg-num">' + value + '</strong>' + (sub ? '<small>' + sub + '</small>' : '') + '</div>';
    };
    var order = ['Anatomy', 'Physiology', 'Biochemistry', 'Microbiology', 'My UWorld', 'Other'];
    var subjRows = order.filter(function (k) { return m.subjects[k]; }).map(function (k) {
      var r = m.subjects[k], acc = r.answered ? Math.round(r.correct / r.answered * 100) : 0;
      var key = k.toLowerCase().replace(/[^a-z]/g, '');
      return '<div class="nkg-subj-row"><span class="nkg-dot is-' + key + '" aria-hidden="true"></span><span class="nkg-row-copy"><strong>' + esc(k) + '</strong><small>' +
        fmt(r.unique) + ' unique · ' + fmt(r.answered) + ' answers</small></span><span class="nkg-subj-acc"><span class="nkg-bar" aria-hidden="true"><i style="width:' + acc + '%"></i></span><b class="nkg-num">' + acc + '%</b></span></div>';
    }).join('');
    var lastSync = meta && meta.lastSyncAt ? new Date(meta.lastSyncAt) : null;
    var syncLine = !auth ? 'Not signed in. Progress is saved on this device only.' :
      (meta && meta.status === 'error' ? 'Sync paused. Open Sync to retry.' :
        lastSync ? 'Last synced ' + lastSync.toLocaleString('en-IN', { day: 'numeric', month: 'short', hour: 'numeric', minute: '2-digit' }) : 'Signed in. Waiting for the first sync.');
    var short = function (act, icon, label, meta2) {
      return '<button type="button" class="nkg-list-item" data-nkg-go="' + act + '">' + iconSvg(icon, 18, 'nkg-tile-ic') + '<span class="nkg-row-copy"><strong>' + label + '</strong>' + (meta2 ? '<small>' + meta2 + '</small>' : '') + '</span>' + iconSvg('caret-right', 16, 'nkg-chev') + '</button>';
    };
    return '<div class="nkg-profile" role="region" aria-label="Profile">' +
      '<section class="nkg-profile-head">' +
      '<span class="nkg-avatar nkg-avatar-lg" aria-hidden="true">' + esc(initials(name)) + '</span>' +
      '<div class="nkg-profile-id"><h1 class="nkg-profile-name">' + esc(name || 'Add your name') + '</h1>' + (auth && auth.email ? '<p>' + esc(auth.email) + '</p>' : '') + '</div>' +
      '<button type="button" class="nkg-btn nkg-btn-secondary nkg-btn-sm" data-nkg-act="edit-name">' + iconSvg('pencil-simple', 16) + '<span>Edit</span></button>' +
      '<form class="nkg-name-form" hidden><label for="nkg-name-input">Display name</label><div class="nkg-name-row"><input id="nkg-name-input" class="nkg-input" maxlength="40" autocomplete="name" value="' + esc(name) + '" placeholder="Your name"><button type="submit" class="nkg-btn nkg-btn-primary nkg-btn-sm">Save</button><button type="button" class="nkg-btn nkg-btn-ghost nkg-btn-sm" data-nkg-act="cancel-name">Cancel</button></div><small>Stored only on this device.</small></form>' +
      '</section>' +
      '<section class="nkg-card nkg-streak-card"><div class="nkg-streak-main"><span class="nkg-flame' + (m.current ? ' is-on' : '') + '" aria-hidden="true">' + iconSvg('fire-fill', 24) + '</span>' +
      '<div><strong class="nkg-num nkg-streak-n">' + fmt(m.current) + '</strong><span> day streak</span><small>Best ' + fmt(m.best) + (m.best === 1 ? ' day' : ' days') + '</small></div></div>' + heatmap(m.days) + '</section>' +
      '<section aria-labelledby="nkg-life-title"><h2 class="nkg-group-title" id="nkg-life-title">Lifetime</h2><div class="nkg-stats">' +
      stat('Answers', fmt(m.total)) +
      stat('Accuracy', m.accuracy == null ? '\u2014' : Math.round(m.accuracy) + '%', fmt(m.correct) + ' correct') +
      stat('Study time', fmtDuration(m.studyMs)) +
      stat('Reviews', fmt(m.reviews)) +
      stat('Timed tests', fmt(m.tests)) +
      stat('Best streak', fmt(m.best) + (m.best === 1 ? ' day' : ' days')) +
      '</div></section>' +
      '<section aria-labelledby="nkg-subj-title"><h2 class="nkg-group-title" id="nkg-subj-title">By subject</h2>' +
      (subjRows ? '<div class="nkg-list">' + subjRows + '</div>' : '<div class="nkg-empty">Answer a question in any subject to see your breakdown here.</div>') + '</section>' +
      '<section aria-labelledby="nkg-acct-title"><h2 class="nkg-group-title" id="nkg-acct-title">Account &amp; sync</h2><div class="nkg-list">' +
      (!auth ? '' : '<div class="nkg-list-item nkg-static"><span class="nkg-sync-dot' + (auth ? (meta && meta.status === 'error' ? ' is-error' : ' is-on') : '') + '" aria-hidden="true"></span><span class="nkg-row-copy"><strong>' + (auth ? esc(auth.email || 'QBank account') : 'This device only') + '</strong><small>' + esc(syncLine) + '</small></span></div>') +
      short('sync', auth ? 'cloud-check' : 'cloud-slash', auth ? 'Sync &amp; account' : 'Set up sync') +
      '</div></section>' +
      '<section aria-labelledby="nkg-short-title"><h2 class="nkg-group-title" id="nkg-short-title">Shortcuts</h2><div class="nkg-list">' +
      short('bookmarks', 'bookmark-simple', 'Bookmarks', fmt(m.bookmarks) + ' saved') +
      short('wrong', 'x-circle', 'Mistakes') +
      short('notes', 'note-pencil', 'My notes', fmt(m.notes) + ' notes') +
      short('fsrs-settings', 'gear', 'Revision settings') +
      '</div></section>' +
      '</div>';
  }
  function renderProfile(app) {
    var main = app.querySelector('main.page');
    if (!main || main.querySelector('.nkg-profile')) return;
    var header = app.querySelector('.nk-global-header-v114');
    if (header) header.remove();
    main.innerHTML = profileMarkup();
    var items = app.querySelectorAll('.bottom-nav .nav-item');
    for (var i = 0; i < items.length; i++) { items[i].classList.remove('active'); items[i].setAttribute('aria-current', 'false'); }
    swapIcons(main);
  }

  /* ------------------------------------------------------ Restore points */
  /* Progress lives in IndexedDB and nk-store.js snapshots it on its own: every
     half hour of study, once a day, and before a reset, restore or migration.
     This page lists those points; nothing here is a file to download. */
  var REASONS = { auto: '', migration: 'Moved to on-device database', 'before-restore': 'Before a restore', 'before-reset': 'Before reset', manual: 'Saved by you' };
  function restoreDay(at) {
    var d = new Date(at), today = new Date(); today.setHours(0, 0, 0, 0);
    var diff = Math.round((today - new Date(d.getFullYear(), d.getMonth(), d.getDate())) / 864e5);
    if (diff === 0) return 'Today';
    if (diff === 1) return 'Yesterday';
    return d.toLocaleDateString(undefined, { weekday: 'short', day: 'numeric', month: 'short' });
  }
  function restoreTime(at) { return new Date(at).toLocaleTimeString(undefined, { hour: 'numeric', minute: '2-digit' }); }
  function plural(n, word) { return n.toLocaleString() + ' ' + word + (n === 1 ? '' : 's'); }
  function bytesLabel(n) { return n >= 1048576 ? (n / 1048576).toFixed(1) + ' MB' : Math.max(1, Math.round(n / 1024)) + ' KB'; }
  function restoreRows(list) {
    if (!list.length) return '<p class="nkg-restore-empty">The first restore point is saved after a few minutes of study.</p>';
    var out = '', day = '';
    list.forEach(function (item) {
      var d = restoreDay(item.at);
      if (d !== day) { if (day) out += '</ul>'; out += '<h3 class="nkg-restore-day">' + esc(d) + '</h3><ul class="nkg-restore-list">'; day = d; }
      var detail = plural(item.answered || 0, 'answer') + (item.notes ? ' · ' + plural(item.notes, 'note') : '') + (item.tests ? ' · ' + plural(item.tests, 'test') : '');
      var why = REASONS[item.reason] || '';
      out += '<li><span class="nkg-restore-copy"><strong>' + esc(restoreTime(item.at)) + (why ? '<em>' + esc(why) + '</em>' : '') + '</strong><small>' + esc(detail) + '</small></span>' +
        '<button type="button" class="nkg-btn nkg-btn-secondary nkg-btn-sm" data-nkg-act="restore-pick" data-id="' + esc(item.id) + '">Restore</button></li>';
    });
    return out + '</ul>';
  }
  function openRestore() {
    if (!window.NKStore || document.getElementById('nk-restore-sheet')) return;
    document.body.insertAdjacentHTML('beforeend',
      '<div class="modal-backdrop nk-mock-sheet-backdrop" id="nk-restore-sheet" onkeydown="if(event.key===\'Escape\'){event.stopPropagation();this.querySelector(\'.nk-modal-close\').click()}">' +
      '<section class="modal card nk-mock-sheet" role="dialog" aria-modal="true" aria-labelledby="nk-restore-title">' +
      '<header class="nk-mock-sheet-head"><div class="nk-mock-sheet-title"><h2 id="nk-restore-title">Restore points</h2></div>' +
      '<button type="button" class="nk-modal-close" aria-label="Close" data-nkg-act="restore-close">' + iconSvg('x', 20) + '</button></header>' +
      '<div class="nk-mock-sheet-body"><p class="nkg-restore-lede">Saved automatically on this device while you study. Restoring keeps your current progress as a point too, so you can undo it.</p>' +
      '<p class="nkg-restore-status" role="status" aria-live="polite"></p><div class="nkg-restore-rows" aria-busy="true"></div>' +
      '<p class="nkg-restore-meta"></p></div></section></div>');
    var sheet = document.getElementById('nk-restore-sheet');
    window.NKStore.snapshots().then(function (list) {
      var rows = sheet.querySelector('.nkg-restore-rows');
      rows.innerHTML = restoreRows(list); rows.removeAttribute('aria-busy');
    }, function () { sheet.querySelector('.nkg-restore-rows').innerHTML = '<p class="nkg-restore-empty">Restore points are not available in this browser.</p>'; });
    window.NKStore.usage().then(function (u) {
      var meta = sheet.querySelector('.nkg-restore-meta');
      if (meta) meta.textContent = (window.NKStore.backend === 'indexeddb' ? 'On-device database' : 'Browser storage') + ' · progress ' + bytesLabel(u.progressBytes || 0);
    });
  }
  function closeRestore() { var s = document.getElementById('nk-restore-sheet'); if (s) s.remove(); }
  var restoreArmed = null;
  function pickRestore(btn) {
    var sheet = document.getElementById('nk-restore-sheet'), status = sheet && sheet.querySelector('.nkg-restore-status');
    if (!sheet) return;
    // Two taps: the first arms the row, the second restores. Nothing is lost
    // either way because the current progress is saved as a point first.
    if (restoreArmed !== btn) {
      if (restoreArmed && restoreArmed.isConnected) { restoreArmed.textContent = 'Restore'; restoreArmed.classList.remove('nkg-armed'); }
      restoreArmed = btn; btn.textContent = 'Tap to confirm'; btn.classList.add('nkg-armed'); haptic();
      window.setTimeout(function () { if (restoreArmed === btn && btn.isConnected) { btn.textContent = 'Restore'; btn.classList.remove('nkg-armed'); restoreArmed = null; } }, 4000);
      return;
    }
    restoreArmed = null;
    Array.prototype.forEach.call(sheet.querySelectorAll('[data-nkg-act="restore-pick"]'), function (b) { b.disabled = true; });
    btn.textContent = 'Restoring…'; btn.setAttribute('aria-busy', 'true');
    window.NKStore.restore(btn.getAttribute('data-id')).then(function () {
      if (status) status.textContent = 'Restored. Reopening…';
      window.setTimeout(function () { location.reload(); }, 450);
    }, function (error) {
      if (status) status.textContent = 'Could not restore: ' + (error && error.message || 'unknown error');
      Array.prototype.forEach.call(sheet.querySelectorAll('[data-nkg-act="restore-pick"]'), function (b) { b.disabled = false; });
      btn.textContent = 'Restore'; btn.classList.remove('nkg-armed'); btn.removeAttribute('aria-busy');
    });
  }
  // A reset keeps a restore point first, so it can be undone from this page.
  function guardReset() {
    var qb = window.QB;
    if (!qb || !window.NKStore || qb.__nkgResetGuard || typeof qb.resetProgress !== 'function') return;
    var reset = qb.resetProgress;
    qb.resetProgress = function () { window.NKStore.snapshot('before-reset'); return reset.apply(this, arguments); };
    qb.__nkgResetGuard = true;
  }

  /* --------------------------------------------------------------- events */
  document.addEventListener('click', function (ev) {
    var t = ev.target && ev.target.closest ? ev.target.closest('[data-nkg-act],[data-nkg-go],[data-nkg-theme-choice]') : null;
    if (!t) return;
    var choice = t.getAttribute('data-nkg-theme-choice');
    if (choice) { setTheme(choice); haptic(); return; }
    var go2 = t.getAttribute('data-nkg-go');
    if (go2) {
      if (go2 === 'sync') {
        go('more');
        window.setTimeout(function () {
          var card = document.querySelector('.nk-cloud-card') || document.querySelector('.nk-settings-group input[type="email"]');
          if (card && card.scrollIntoView) card.scrollIntoView({ block: 'center' });
        }, 60);
      } else if (go2 === 'bookmarks' || go2 === 'wrong') go('revision-browse', go2);
      else go(go2);
      return;
    }
    var act = t.getAttribute('data-nkg-act');
    if (act === 'home') go('dashboard');
    else if (act === 'search') go('question-search');
    else if (act === 'profile') { if (route() !== 'profile') location.hash = 'profile'; }
    else if (act === 'theme') { setTheme(resolvedTheme() === 'dark' ? 'light' : 'dark'); haptic(); }
    else if (act === 'restore') openRestore();
    else if (act === 'restore-close') closeRestore();
    else if (act === 'restore-pick') pickRestore(t);
    else if (act === 'edit-name' || act === 'cancel-name') {
      var form = document.querySelector('.nkg-name-form'), btn = document.querySelector('[data-nkg-act="edit-name"]');
      if (!form) return;
      var open = act === 'edit-name';
      form.hidden = !open; if (btn) btn.hidden = open;
      if (open) { var inp = form.querySelector('input'); if (inp) { inp.focus(); inp.select(); } }
    }
  });
  document.addEventListener('submit', function (ev) {
    var form = ev.target;
    if (!form || !form.classList || !form.classList.contains('nkg-name-form')) return;
    ev.preventDefault();
    var input = form.querySelector('input');
    lsSet(NAME_KEY, (input && input.value || '').trim().slice(0, 40));
    var main = document.querySelector('#app main.page');
    if (main) { main.innerHTML = profileMarkup(); swapIcons(main); }
    updateTopbar('profile', false);
    haptic();
  });

  /* ------------------------------------------------------------ observer */
  var scheduled = false, observers = [];
  function onRender() {
    scheduled = false;
    var app = document.getElementById('app');
    if (!app) return;
    buildTopbar();
    var page = route();
    var session = !!app.querySelector('.qbank-session-page, .nk-session-footer, .review-fixed-actions') ||
      page === 'practice' || page === 'exam' || page === 'review-test';
    doc.setAttribute('data-nkg-route', page);
    if (session) doc.setAttribute('data-nkg-session', ''); else doc.removeAttribute('data-nkg-session');
    if (page === 'profile') renderProfile(app);
    else if (page === 'more') decorateMore(app);
    if (page === 'dashboard') decorateHome(app);
    polishCopy(app, session);
    swapIcons(app);
    ['modal', 'nk-practice-sessions', 'nk-mock-sheet'].forEach(function (id) { var m = document.getElementById(id); if (m) swapIcons(m); });
    updateTopbar(page, session);
    syncThemeControls();
    measureDock();
    /* Re-measure once page-enter motion has settled (a transformed page offsets fixed docks). */
    window.clearTimeout(dockSettle); dockSettle = window.setTimeout(measureDock, 480);
    neutralizeInlineTracks(app);
    if (window.NKFeel && typeof window.NKFeel.render === 'function') window.NKFeel.render(app, page, session);
    var zero = app.querySelectorAll('.nk-review-chart > span');
    for (var z = 0; z < zero.length; z++) {
      var b = zero[z].querySelector('b');
      zero[z].classList.toggle('nkg-zero', !!b && b.textContent.trim() === '0');
    }
    /* Drop the mutations this pass made itself (icon swaps, decorations) so one app
       render costs one decoration pass instead of re-triggering itself. */
    for (var o = 0; o < observers.length; o++) observers[o].takeRecords();
  }
  /* Small Geist-only wording fixes on core markup (legacy UI and its tests keep the originals). */
  function polishCopy(app, session) {
    if (session) {
      // The last question's primary action ends the session, so say so.
      var st = window.QB && window.QB.getState && window.QB.getState(), s = st && st.activeSession;
      var next = app.querySelector('.fixed-actions-inner .primary-btn[onclick="window.QB.nextQ()"]');
      if (next && s && (s.mode === 'practice' || s.mode === 'exam') && s.questionIds && s.index === s.questionIds.length - 1) {
        var label = next.firstChild;
        if (label && label.nodeType === 3 && /Next/.test(label.nodeValue)) {
          label.nodeValue = 'Finish ';
          var icon = next.querySelector('svg[data-nk-icon]');
          if (icon) { icon.setAttribute('data-nk-icon', 'check'); icon.removeAttribute('data-nkg-icon'); }
        }
      }
    }
    // Declutter: hide what repeats another card or explains the obvious.
    var cards = app.querySelectorAll('.nk-li-card:not([data-nkg-seen])');
    for (var c = 0; c < cards.length; c++) {
      cards[c].setAttribute('data-nkg-seen', '');
      var h = cards[c].querySelector('header h2');
      // Period comparison repeats the stat tiles at the top of Insights.
      if (h && h.textContent.trim() === 'Period comparison') cards[c].classList.add('nkg-hidden');
    }
    var smalls = app.querySelectorAll('.nk-li-subjects small, .nk-note-bar-copy small');
    for (var k = 0; k < smalls.length; k++) {
      var t = smalls[k].textContent.trim();
      if (t === 'No previous answers' || /^Add text/.test(t)) smalls[k].classList.add('nkg-hidden');
    }
    // Marrow source line: keep the page reference, drop the build note.
    var prov = app.querySelectorAll('.nk-marrow-provenance:not([data-nkg-copy])');
    for (var i = 0; i < prov.length; i++) {
      var pages = (prov[i].textContent.match(/explanation pages? ([\d,\s]+)/) || [])[1];
      prov[i].textContent = 'Source: ' + (prov[i].getAttribute('data-nkg-source') || 'Marrow ED8') + (pages ? ' · page' + (/,/.test(pages) ? 's ' : ' ') + pages.trim().replace(/,\s*/g, ', ') : '');
      prov[i].setAttribute('data-nkg-copy', '');
    }
  }
  /* A few charts set their track colour inline (legacy lavender #eceaf4 /
     #eeecf4 / #ebe6f5). Swap only that literal for the neutral token. */
  var LAVENDER = /#(?:eceaf4|eeecf4|ebe6f5)/gi;
  function neutralizeInlineTracks(root) {
    var els = root.querySelectorAll('[style*="#eceaf4" i], [style*="#eeecf4" i], [style*="#ebe6f5" i]');
    for (var i = 0; i < els.length; i++) {
      var st = els[i].getAttribute('style');
      if (st) els[i].setAttribute('style', st.replace(LAVENDER, 'var(--nkg-active)'));
    }
  }
  /* Height of the band covered by fixed bottom docks (nav, session footer,
     recall dock, builder action bars). Published as --nkg-dock-h. */
  var dockFrame = 0, dockSettle = 0;
  function measureDock() {
    if (dockFrame) return;
    dockFrame = window.requestAnimationFrame(function () {
      dockFrame = 0;
      var app = document.getElementById('app');
      if (!app) return;
      var H = window.innerHeight, top = H;
      var c = app.querySelectorAll('nav, footer, [class*="action"], [class*="footer"], [class*="dock"], [class*="bar"], .nk-continue-learning');
      for (var i = 0; i < c.length; i++) {
        var el = c[i];
        if (el.offsetParent !== null) continue;
        var cs = window.getComputedStyle(el);
        if (cs.position !== 'fixed' || cs.display === 'none' || cs.visibility === 'hidden') continue;
        var rc = el.getBoundingClientRect();
        if (!rc.height || rc.height > H * 0.5 || rc.top < H * 0.4 || rc.bottom < H * 0.6) continue;
        if (rc.top < top) top = rc.top;
      }
      var h = Math.max(0, Math.round(H - top));
      if (h) { doc.style.setProperty('--nkg-dock-h', h + 'px'); doc.setAttribute('data-nkg-dock', ''); }
      else { doc.style.removeProperty('--nkg-dock-h'); doc.removeAttribute('data-nkg-dock'); }
    });
  }
  window.addEventListener('resize', measureDock);
  function schedule(records) {
    if (scheduled) return;
    for (var i = 0; records && i < records.length; i++) {
      var added = records[i].addedNodes;
      for (var j = 0; j < added.length; j++) {
        if (added[j].nodeType === 1) { scheduled = true; onRender(); return; }
      }
    }
  }
  function start() {
    var app = document.getElementById('app');
    if (!app) return;
    observers = [new MutationObserver(schedule), new MutationObserver(schedule)];
    observers[0].observe(app, { childList: true, subtree: true });
    observers[1].observe(document.body, { childList: true });
    window.addEventListener('hashchange', function () { window.setTimeout(onRender, 0); });
    onRender();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
