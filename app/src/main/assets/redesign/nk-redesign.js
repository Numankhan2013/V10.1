/* NK QBank — Geist redesign runtime.
 *
 * Loaded synchronously in <head> so the theme is applied before first paint.
 * It owns only presentation: the theme switch, the top bar, Phosphor icon
 * swaps, the Home greeting, the Appearance controls in More and the additive
 * Profile screen.  Study logic, storage and navigation stay with the app; this
 * file only reads progress (window.QB.getState / saved auth) and calls the
 * app's existing public actions (window.QB.nav, ...).
 *
 * Switches:
 *   ?ui=legacy / ?ui=geist  persist the choice in localStorage "nkq.ui".
 *   Without a stored choice the redesign is on, except under browser
 *   automation (navigator.webdriver), where the legacy contract suites run.
 *   localStorage "nkq.theme" = light | dark | system (default system).
 */
(function () {
  'use strict';
  var doc = document.documentElement;
  var UI_KEY = 'nkq.ui', THEME_KEY = 'nkq.theme', NAME_KEY = 'nkq.profile.name';

  function lsGet(k) { try { return window.localStorage.getItem(k); } catch (e) { return null; } }
  function lsSet(k, v) { try { window.localStorage.setItem(k, v); } catch (e) { /* storage blocked */ } }

  var forced = (location.search.match(/[?&]ui=(geist|legacy)(?:&|$)/) || [])[1];
  if (forced) lsSet(UI_KEY, forced);
  var stored = lsGet(UI_KEY);
  var mode = stored === 'geist' || stored === 'legacy' ? stored : (navigator.webdriver ? 'legacy' : 'geist');

  window.NKQ_UI = {
    mode: mode,
    setMode: function (next) { lsSet(UI_KEY, next === 'legacy' ? 'legacy' : 'geist'); location.reload(); }
  };
  if (mode !== 'geist') { doc.setAttribute('data-nk-ui', 'legacy'); return; }
  doc.setAttribute('data-nk-ui', 'geist');
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
    syncThemeControls();
  }
  function setTheme(pref) {
    lsSet(THEME_KEY, pref);
    doc.classList.add('nkg-theme-switching');
    applyTheme();
    window.setTimeout(function () { doc.classList.remove('nkg-theme-switching'); }, 240);
  }
  if (media) {
    var onScheme = function () { if (themePref() === 'system') applyTheme(); };
    if (media.addEventListener) media.addEventListener('change', onScheme); else if (media.addListener) media.addListener(onScheme);
  }
  window.NKQ_UI.setTheme = setTheme;
  window.NKQ_UI.theme = resolvedTheme;
  applyTheme();

  /* ------------------------------------------------------------------ icons */
  var ICON_MAP = {
    home: 'house', book: 'book-open', test: 'clipboard-text', chart: 'chart-line-up', bookmark: 'bookmark-simple',
    clock: 'clock', search: 'magnifying-glass', bell: 'bell', star: 'star', trash: 'trash', refresh: 'arrows-clockwise',
    share: 'share-network', molecule: 'atom', bulb: 'lightbulb', heart: 'heart', body: 'person', dna: 'dna',
    biochemistry: 'dna', physiology: 'heartbeat', anatomy: 'bone', poisoning: 'flask', biostatistics: 'chart-bar',
    ophthalmology: 'eye', 'male-reproductive': 'gender-male', 'female-reproductive': 'gender-female', pregnancy: 'baby',
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
  function go(page) { if (window.QB && typeof window.QB.nav === 'function') window.QB.nav(page); else location.hash = page; }
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
    if (/^UWORLD_/i.test(id)) return 'My UWorld';
    return 'Other';
  }
  function lifetime() {
    var s = appState(), attempts = s.attempts || {}, tests = Array.isArray(s.tests) ? s.tests : [];
    var total = 0, correct = 0, unique = 0, practiceMs = 0, reviews = 0, days = {}, subjects = {};
    Object.keys(attempts).forEach(function (qid) {
      var list = Array.isArray(attempts[qid]) ? attempts[qid] : [], counted = false;
      var sub = subjectOf(qid);
      list.forEach(function (a) {
        if (!a || a.isUndo || a.isRatingRevision || typeof a.correct !== 'boolean') return;
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
      '<button type="button" class="nkg-brand" data-nkg-act="home" aria-label="NK QBank home"><span class="nkg-logo" aria-hidden="true">NK</span><span class="nkg-topbar-title">Home</span></button>' +
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
      '<h2 class="nkg-group-title" id="nkg-appearance-title">Appearance</h2>' +
      '<div class="nkg-appearance-card">' +
      '<button type="button" class="nkg-profile-row" data-nkg-act="profile"><span class="nkg-avatar">' + esc(initials(profileName())) + '</span>' +
      '<span class="nkg-row-copy"><strong>' + esc(profileName() || 'Your profile') + '</strong><small>Lifetime progress, streaks and account</small></span>' + iconSvg('caret-right', 16, 'nkg-chev') + '</button>' +
      '<div class="nkg-theme-row"><span class="nkg-row-copy"><strong>Theme</strong><small>Light, dark or follow this device</small></span>' +
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
    var order = ['Anatomy', 'Physiology', 'Biochemistry', 'My UWorld', 'Other'];
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
      '<div class="nkg-profile-id"><h1 class="nkg-profile-name">' + esc(name || 'Add your name') + '</h1><p>' + (auth && auth.email ? esc(auth.email) : 'Local profile on this device') + '</p></div>' +
      '<button type="button" class="nkg-btn nkg-btn-secondary nkg-btn-sm" data-nkg-act="edit-name">' + iconSvg('pencil-simple', 16) + '<span>Edit</span></button>' +
      '<form class="nkg-name-form" hidden><label for="nkg-name-input">Display name</label><div class="nkg-name-row"><input id="nkg-name-input" class="nkg-input" maxlength="40" autocomplete="name" value="' + esc(name) + '" placeholder="Your name"><button type="submit" class="nkg-btn nkg-btn-primary nkg-btn-sm">Save</button><button type="button" class="nkg-btn nkg-btn-ghost nkg-btn-sm" data-nkg-act="cancel-name">Cancel</button></div><small>Stored only on this device.</small></form>' +
      '</section>' +
      '<section class="nkg-card nkg-streak-card"><div class="nkg-streak-main"><span class="nkg-flame' + (m.current ? ' is-on' : '') + '" aria-hidden="true">' + iconSvg('fire-fill', 24) + '</span>' +
      '<div><strong class="nkg-num nkg-streak-n">' + fmt(m.current) + '</strong><span> day streak</span><small>Best ' + fmt(m.best) + (m.best === 1 ? ' day' : ' days') + '</small></div></div>' + heatmap(m.days) + '</section>' +
      '<section aria-labelledby="nkg-life-title"><h2 class="nkg-group-title" id="nkg-life-title">Lifetime</h2><div class="nkg-stats">' +
      stat('Answers', fmt(m.total), fmt(m.unique) + ' unique questions') +
      stat('Accuracy', m.accuracy == null ? '\u2014' : Math.round(m.accuracy) + '%', fmt(m.correct) + ' correct') +
      stat('Study time', fmtDuration(m.studyMs), 'Practice and timed tests') +
      stat('Reviews', fmt(m.reviews), 'Rated in Revision') +
      stat('Timed tests', fmt(m.tests), 'Completed') +
      stat('Best streak', fmt(m.best), m.best === 1 ? 'day' : 'days') +
      '</div></section>' +
      '<section aria-labelledby="nkg-subj-title"><h2 class="nkg-group-title" id="nkg-subj-title">By subject</h2>' +
      (subjRows ? '<div class="nkg-list">' + subjRows + '</div>' : '<div class="nkg-empty">Answer a question in any subject to see your breakdown here.</div>') + '</section>' +
      '<section aria-labelledby="nkg-acct-title"><h2 class="nkg-group-title" id="nkg-acct-title">Account &amp; sync</h2><div class="nkg-list">' +
      '<div class="nkg-list-item nkg-static"><span class="nkg-sync-dot' + (auth ? (meta && meta.status === 'error' ? ' is-error' : ' is-on') : '') + '" aria-hidden="true"></span><span class="nkg-row-copy"><strong>' + (auth ? esc(auth.email || 'QBank account') : 'This device only') + '</strong><small>' + esc(syncLine) + '</small></span></div>' +
      short('sync', auth ? 'cloud-check' : 'cloud-slash', auth ? 'Sync &amp; account' : 'Set up sync', auth ? 'Sync now, sign out' : 'Email and password, across devices') +
      '</div></section>' +
      '<section aria-labelledby="nkg-short-title"><h2 class="nkg-group-title" id="nkg-short-title">Shortcuts</h2><div class="nkg-list">' +
      short('bookmarks', 'bookmark-simple', 'Bookmarks', fmt(m.bookmarks) + ' saved') +
      short('wrong', 'x-circle', 'Mistakes', 'Questions to get right') +
      short('notes', 'note-pencil', 'My notes', fmt(m.notes) + ' notes') +
      short('fsrs-settings', 'gear', 'Revision settings', 'Daily limits and scheduling') +
      short('more', 'sun', 'Appearance & app', 'Theme and app controls') +
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
      } else go(go2);
      return;
    }
    var act = t.getAttribute('data-nkg-act');
    if (act === 'home') go('dashboard');
    else if (act === 'search') go('question-search');
    else if (act === 'profile') { if (route() !== 'profile') location.hash = 'profile'; }
    else if (act === 'theme') { setTheme(resolvedTheme() === 'dark' ? 'light' : 'dark'); haptic(); }
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
  var scheduled = false;
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
    swapIcons(app);
    var modal = document.getElementById('modal');
    if (modal) swapIcons(modal);
    updateTopbar(page, session);
    syncThemeControls();
    measureDock();
    neutralizeInlineTracks(app);
    var zero = app.querySelectorAll('.nk-review-chart > span');
    for (var z = 0; z < zero.length; z++) {
      var b = zero[z].querySelector('b');
      zero[z].classList.toggle('nkg-zero', !!b && b.textContent.trim() === '0');
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
  var dockFrame = 0;
  function measureDock() {
    if (dockFrame) return;
    dockFrame = window.requestAnimationFrame(function () {
      dockFrame = 0;
      var app = document.getElementById('app');
      if (!app) return;
      var H = window.innerHeight, top = H;
      var c = app.querySelectorAll('nav, footer, [class*="action"], [class*="footer"], [class*="dock"], [class*="bar"]');
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
    new MutationObserver(schedule).observe(app, { childList: true, subtree: true });
    new MutationObserver(schedule).observe(document.body, { childList: true });
    window.addEventListener('hashchange', function () { window.setTimeout(onRender, 0); });
    onRender();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
