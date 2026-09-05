from pathlib import Path
import re

INDEX = Path('app/src/main/assets/index.html')
text = INDEX.read_text(encoding='utf-8')


def replace_function(source, signature, replacement):
    start = source.find(signature)
    if start < 0:
        raise SystemExit(f'{signature} target not found')
    brace = source.find('{', start)
    if brace < 0:
        raise SystemExit(f'{signature} opening brace not found')
    depth = 0
    in_str = None
    escape = False
    i = brace
    while i < len(source):
        ch = source[i]
        if in_str:
            if escape:
                escape = False
            elif ch == '\\':
                escape = True
            elif ch == in_str:
                in_str = None
        else:
            if ch in ('"', "'", '`'):
                in_str = ch
            elif ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    return source[:start] + replacement + source[i + 1:]
        i += 1
    raise SystemExit(f'{signature} closing brace not found')


# One authoritative navigation path. It handles both normal hash changes and
# same-route navigation, and resets all likely WebView scroll containers.
navigate_replacement = """function resetScrollPosition(){
    requestAnimationFrame(() => window.scrollTo(0,0));
    requestAnimationFrame(() => { document.documentElement.scrollTop=0; document.body.scrollTop=0; });
  }
  function navigate(page, id = '') {
    const target = id ? `${page}/${encodeURIComponent(id)}` : page;
    const targetHash = `#${target}`;
    if(location.hash === targetHash){
      route = parseHash();
      render();
      resetScrollPosition();
      return;
    }
    location.hash = target;
  }
  window.addEventListener('hashchange', () => {
    route = parseHash();
    render();
    resetScrollPosition();
  });"""
text = replace_function(text, 'function navigate(page, id = \'\')', navigate_replacement)

# Subject selection from Home remains direct and deterministic.
set_replacement = """function setSubject(name){
    if(!SUBJECT_BY_NAME[name]) return;
    applySubject(name);
    searchTerm='';
    topicFilter='all';
    if(route && route.page==='dashboard'){
      render();
      resetScrollPosition();
    } else {
      navigate('dashboard');
    }
  }
  function openSubjectTopics(name){
    if(!SUBJECT_BY_NAME[name]) return;
    applySubject(name);
    searchTerm='';
    topicFilter='all';
    navigate('topics');
  }"""
text = replace_function(text, 'function setSubject(name)', set_replacement)

if 'setSubject,openSubjectTopics,toggleMenu' not in text:
    old = "window.QB={getState:()=>state,nav:navigate,setSubject,toggleMenu,notify,openQuestionNavigator"
    new = "window.QB={getState:()=>state,nav:navigate,setSubject,openSubjectTopics,toggleMenu,notify,openQuestionNavigator"
    if old not in text:
        raise SystemExit('QB export target not found')
    text = text.replace(old, new, 1)

# Home subject rows open the selected subject's Topics view.
text = text.replace(
    "onclick=\"window.QB.setSubject('${esc(x.subject)}')\"",
    "onclick=\"window.QB.openSubjectTopics('${esc(x.subject)}')\"",
    1,
)

# Replace the large legacy subject hub used at the top of Topics with a compact
# integrated subject switcher. Switching subjects remains available, but the
# huge duplicate block is gone.
compact_picker = """function subjectPickerMarkup(){
    return `<div class=\"nk-topic-subject-switch\" aria-label=\"Choose subject\"><div class=\"nk-topic-subject-label\"><span class=\"nk-home-v4-label\">STUDY LIBRARY</span><strong>${esc(activeSubject)}</strong></div><div class=\"nk-topic-subject-options\">${SUBJECTS.map(x=>`<button type=\"button\" class=\"nk-topic-subject-option ${x.subject===activeSubject?'is-active':''}\" onclick=\"window.QB.openSubjectTopics('${esc(x.subject)}')\" aria-pressed=\"${x.subject===activeSubject?'true':'false'}\">${esc(x.subject)}</button>`).join('')}</div></div>`;
  }
  """
text = replace_function(text, 'function subjectPickerMarkup()', compact_picker)

# A full Topics page refresh focused on hierarchy and scanability while keeping
# the existing question/chapter logic untouched.
topics_replacement = """function topics() {
    const qTerm=searchTerm.trim().toLowerCase();
    let chapters=CHAPTERS.filter(c => {
      const stats=chapterStats(c.id);
      if(topicFilter==='completed' && stats.attempted < stats.total) return false;
      if(topicFilter==='unattempted' && stats.attempted > 0) return false;
      if(topicFilter==='inprogress' && !(stats.attempted>0 && stats.attempted<stats.total)) return false;
      return !qTerm || c.title.toLowerCase().includes(qTerm) || chapterQuestions(c.id).some(q=>q.question.toLowerCase().includes(qTerm));
    });
    const attemptedTopics=chapters.filter(c=>chapterStats(c.id).attempted>0).length;
    return shell(`
      <div class=\"nk-topics-v2\">
        <div class=\"nk-topics-v2-head\">
          <div><div class=\"nk-home-v4-label\">${esc(activeSubject)} · STUDY MAP</div><h1>Topics</h1><p>Pick a chapter, build recall, and move straight into questions.</p></div>
          <button class=\"primary-btn nk-topics-v2-mixed\" onclick=\"window.QB.startAllPractice()\">Mixed Practice <span>→</span></button>
        </div>
        ${subjectPickerMarkup()}
        <div class=\"nk-topics-v2-tools\">
          <div class=\"nk-topics-v2-search\">${navIcon('search',18)}<input aria-label=\"Search questions\" placeholder=\"Search chapters or questions…\" value=\"${esc(searchTerm)}\" oninput=\"window.QB.setSearch(this.value)\" /></div>
          <select class=\"select nk-topics-v2-select\" onchange=\"window.QB.setTopicFilter(this.value)\"><option value=\"all\" ${topicFilter==='all'?'selected':''}>All topics</option><option value=\"completed\" ${topicFilter==='completed'?'selected':''}>Completed</option><option value=\"unattempted\" ${topicFilter==='unattempted'?'selected':''}>Unattempted</option><option value=\"inprogress\" ${topicFilter==='inprogress'?'selected':''}>In progress</option></select>
        </div>
        <div class=\"nk-topics-v2-summary\"><div><strong>${fmtNum(chapters.length)}</strong> topics shown <span>·</span> <strong>${fmtNum(attemptedTopics)}</strong> started</div><div class=\"nk-topics-v2-tabs\">${[['all','All'],['completed','Completed'],['unattempted','Unattempted'],['inprogress','In Progress']].map(([v,l])=>`<button class=\"tab ${topicFilter===v?'active':''}\" onclick=\"window.QB.setTopicFilter('${v}')\">${l}</button>`).join('')}</div></div>
        <div class=\"nk-topic-list-v2\">${chapters.map((c,i)=>{const s=chapterStats(c.id),pct=s.accuracy?Math.min(100,s.attempted/s.total*100):0;return `<button type=\"button\" class=\"nk-topic-row-v2\" onclick=\"window.QB.openChapter('${c.id}')\"><div class=\"nk-topic-index-v2\">${String(i+1).padStart(2,'0')}</div><div class=\"nk-topic-main-v2\"><div class=\"nk-topic-title-v2\">${esc(c.title)}</div><div class=\"nk-topic-meta-v2\">${s.total} MCQs <span>·</span> ${s.attempted} completed <span>·</span> ${fmtPct(s.accuracy)} accuracy</div><div class=\"nk-topic-progress-v2\"><span style=\"width:${pct}%\"></span></div></div><div class=\"nk-topic-stat-v2\"><strong>${fmtPct(pct)}</strong><span>${s.attempted}/${s.total}</span></div><span class=\"nk-topic-arrow-v2\">→</span></button>;}).join('')}</div>
        ${qTerm?`<div class=\"card pad nk-topics-v2-results\"><div class=\"section-title\"><span>Matching questions</span><span class=\"sub\">Actual source questions</span></div><div class=\"library\">${QUESTIONS.filter(q=>q.question.toLowerCase().includes(qTerm)).slice(0,60).map(q=>libraryRow(q,'search')).join('')}</div></div>`:''}
      </div>
    `, 'topics');
  }
  """
text = replace_function(text, 'function topics()', topics_replacement)

# Home streak is scoped to Home only; keep it and make its outer shape match the
# sharper/cornered Home language. Internal icon/day capsules remain rounded.
style_marker = '/* NK HOME V8 — functional navigation, authoritative scroll, Topics V2 */'
if style_marker not in text:
    topic_style = r"""
<style id="nk-home-v8-style">
/* NK HOME V8 — functional navigation, authoritative scroll, Topics V2 */
.streak-card.streak-card-compact{border-radius:0!important;box-shadow:none!important;margin-top:14px}
.nk-topic-subject-switch{display:flex;align-items:center;justify-content:space-between;gap:18px;padding:14px 0 16px;border-bottom:1px solid #e1e3eb}
.nk-topic-subject-label{display:flex;flex-direction:column;gap:3px}.nk-topic-subject-label strong{font-size:18px;letter-spacing:-.35px}.nk-topic-subject-options{display:flex;gap:7px;overflow:auto;max-width:70%}.nk-topic-subject-option{border:1px solid #dfe1e9;background:#fff;color:#70727f;padding:9px 13px;border-radius:10px;font-size:12px;font-weight:800;white-space:nowrap}.nk-topic-subject-option.is-active{background:#eef1ff;border-color:#cfd7ff;color:#2f2d63}
.nk-topics-v2{max-width:1040px;margin:0 auto;padding-bottom:36px}.nk-topics-v2-head{display:flex;align-items:flex-end;justify-content:space-between;gap:18px;padding:22px 4px 18px;border-bottom:1px solid #e1e3eb}.nk-topics-v2-head h1{font-size:31px;line-height:1.06;letter-spacing:-1.2px;margin:5px 0 5px;font-weight:850}.nk-topics-v2-head p{margin:0;color:#747683;font-size:13px;line-height:1.45}.nk-topics-v2-mixed span{margin-left:7px}.nk-topics-v2-tools{display:flex;gap:10px;align-items:center;padding:18px 0 10px}.nk-topics-v2-search{position:relative;flex:1}.nk-topics-v2-search input{width:100%;height:46px;border:1px solid #dfe1e9;border-radius:12px;padding:0 16px 0 42px;background:#fff;outline:none}.nk-topics-v2-search svg{position:absolute;left:14px;top:14px;color:#7b7e8b;z-index:1}.nk-topics-v2-select{height:46px;min-width:150px}.nk-topics-v2-summary{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:6px 0 12px;color:#777a87;font-size:12px}.nk-topics-v2-summary strong{color:#303145;font-size:13px}.nk-topics-v2-summary>div:first-child span{padding:0 4px;color:#b0b2bc}.nk-topics-v2-tabs{display:flex;gap:5px;overflow:auto}.nk-topics-v2-tabs .tab{padding:8px 10px}.nk-topic-list-v2{display:flex;flex-direction:column;border-top:1px solid #e3e5ec}.nk-topic-row-v2{display:grid;grid-template-columns:48px minmax(0,1fr) 62px 26px;gap:12px;align-items:center;width:100%;border:0;border-bottom:1px solid #e5e6ed;background:transparent;text-align:left;padding:15px 4px;color:inherit}.nk-topic-row-v2:hover{background:#fbfbff}.nk-topic-index-v2{font-size:12px;font-weight:850;color:#9093a0}.nk-topic-main-v2{min-width:0}.nk-topic-title-v2{font-size:15px;font-weight:800;letter-spacing:-.15px}.nk-topic-meta-v2{font-size:11px;color:#818390;margin-top:4px}.nk-topic-meta-v2 span{padding:0 3px;color:#b6b8c2}.nk-topic-progress-v2{height:5px;background:#eceef3;margin-top:10px;overflow:hidden;border-radius:999px}.nk-topic-progress-v2 span{display:block;height:100%;background:#3d65d8;border-radius:inherit}.nk-topic-stat-v2{text-align:right;display:flex;flex-direction:column;gap:2px}.nk-topic-stat-v2 strong{font-size:13px;color:#464859}.nk-topic-stat-v2 span{font-size:10px;color:#9a9ca7}.nk-topic-arrow-v2{font-size:18px;color:#a1a4af;text-align:right}.nk-topics-v2-results{margin-top:18px}
@media(max-width:640px){.nk-topic-subject-switch{align-items:flex-start;flex-direction:column;gap:10px}.nk-topic-subject-options{max-width:100%;width:100%}.nk-topics-v2-head{align-items:flex-start}.nk-topics-v2-head h1{font-size:28px}.nk-topics-v2-head p{max-width:300px}.nk-topics-v2-mixed{min-height:42px}.nk-topics-v2-tools{align-items:stretch;flex-direction:column}.nk-topics-v2-select{width:100%}.nk-topics-v2-summary{align-items:flex-start;flex-direction:column}.nk-topics-v2-tabs{width:100%}.nk-topic-row-v2{grid-template-columns:34px minmax(0,1fr) 50px 18px;gap:9px;padding:14px 2px}.nk-topic-title-v2{font-size:14px}.nk-topic-meta-v2{font-size:10.5px;white-space:normal}.nk-topic-arrow-v2{font-size:16px}.streak-card.streak-card-compact{border-radius:0!important}}
</style>
"""
    if '</head>' not in text:
        raise SystemExit('head close not found')
    text = text.replace('</head>', topic_style + '</head>', 1)

marker = '<!-- NK_HOME_V5_FIXES -->'
if marker not in text:
    text = text.replace('</head>', marker + '</head>', 1)

INDEX.write_text(text, encoding='utf-8')
print('Applied Home V8: compact Topics subject switcher, redesigned Topics page, authoritative navigation scroll reset, scoped streak geometry, and preserved subject/count fixes.')