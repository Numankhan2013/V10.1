from pathlib import Path
import re


HTML = Path("app/src/main/assets/index.html")
STYLE_ID = "nk-session-experience-v114"


HELPERS_AND_PRACTICE = r'''function nkSessionSubject(q) {
    const raw=String(q?.subject||activeSubject||'').trim();
    if(raw) return raw.charAt(0).toUpperCase()+raw.slice(1).toLowerCase();
    const id=String(q?.id||'').toLowerCase();
    return id.startsWith('physiology-')?'Physiology':id.startsWith('anatomy-')?'Anatomy':'Biochemistry';
  }

  function nkSessionSubjectKey(q) { return nkSessionSubject(q).toLowerCase(); }

  function nkSessionSubjectIcon(q) {
    const key=nkSessionSubjectKey(q);
    return navIcon(key==='physiology'?'heart':key==='anatomy'?'body':'dna',20);
  }

  function nkSourceTakeaway(q) {
    const reviewed=String(q?.keyTakeaway||q?.takeaway||'').replace(/\s+/g,' ').trim();
    if(reviewed.length>=24) return reviewed;
    const option=Array.isArray(q?.options)?q.options[Number(q.correctOption)-1]:null;
    const answer=String(option?.text||'').replace(/\s+/g,' ').trim();
    let source=String(q?.explanation||'').replace(/\r/g,'\n');
    if(!answer || !source) return '';
    source=source
      .replace(/^\s*Correct\s+(?:Answer|answer|Option)\s*:?\s*[A-E]\)?[^\n]*\n?/i,'')
      .replace(/^\s*Explanation\s*:?\s*/i,'')
      .replace(/[•▪◦]\s*/g,' ')
      .replace(/\s+/g,' ')
      .trim();
    const stop=new Set(['this','that','with','from','into','than','then','which','what','when','where','have','has','were','been','being','their','there','about','answer','option','correct']);
    const tokens=answer.toLowerCase().replace(/[^a-z0-9+]+/g,' ').split(/\s+/).filter(x=>x.length>=4&&!stop.has(x));
    if(!tokens.length) return '';
    const sentences=(source.match(/[^.!?]+[.!?]+|[^.!?]+$/g)||[])
      .map(x=>x.replace(/^[-–—:\s]+/,'').replace(/\s*\(Option\s+[A-E]\)\s*/ig,' ').replace(/\s+/g,' ').trim())
      .filter(x=>x.length>=35&&x.length<=300&&/^[A-Z0-9]/.test(x));
    let best='',bestScore=0;
    sentences.forEach(sentence=>{
      const lower=sentence.toLowerCase();
      const overlap=tokens.reduce((n,t)=>n+(lower.includes(t)?1:0),0);
      const exact=answer.length>=5&&lower.includes(answer.toLowerCase())?3:0;
      const score=overlap+exact-(sentence.length>240?1:0);
      if(score>bestScore){best=sentence;bestScore=score;}
    });
    const needed=tokens.length===1?1:2;
    return best&&bestScore>=needed?best:'';
  }

  function nkSessionHeader(q,s,mode,timerHtml='') {
    const total=Math.max(1,s.questionIds.length),position=s.index+1;
    const progress=Math.max(0,Math.min(100,Math.round(position/total*100)));
    const backAction=mode==='review'?'window.QB.endReview()':'window.QB.openSessionReview()';
    const backLabel=mode==='review'?'End review':'Review or finish session';
    return `<header class="nk-session-head"><button class="icon-btn nk-session-back" aria-label="${backLabel}" onclick="${backAction}">${navIcon('back',24)}</button><div class="nk-session-count"><strong>${position}</strong> / ${total}</div><div class="q-actions">${bookmarkButton(q.id,23)}<button id="cr-grid" class="icon-btn nk-grid-trigger" aria-label="Question navigator" onclick="window.QB.openQuestionNavigator()">${navIcon('grid',22)}</button></div></header><div class="nk-session-progress" role="progressbar" aria-label="Session progress" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${progress}"><i style="width:${progress}%"></i><span>${progress}%</span></div>${timerHtml}`;
  }

  function nkQuestionContext(q) {
    const subject=nkSessionSubject(q),key=nkSessionSubjectKey(q);
    return `<div class="nk-question-context is-${esc(key)}"><span class="nk-subject-icon">${nkSessionSubjectIcon(q)}</span><strong>${esc(subject)}</strong><i aria-hidden="true"></i><span>${esc(q.chapter)}</span></div>`;
  }

  function nkSessionOptions(q,selected,mode,submitted) {
    const locked=mode==='review'||(mode==='practice'&&submitted);
    return q.options.map(o=>{
      const n=o.letter.charCodeAt(0)-64,isChosen=Number(selected)===n,isCorrect=Number(q.correctOption)===n;
      let cls='option';
      if(mode==='exam'){if(isChosen)cls+=' selected';}
      else if(mode==='practice'&&submitted){if(isCorrect)cls+=' correct';if(isChosen&&!isCorrect)cls+=' wrong';}
      else if(mode==='practice'&&isChosen){cls+=' selected';}
      else if(mode==='review'){if(isCorrect)cls+=' correct';if(isChosen&&!isCorrect)cls+=' wrong';if(!selected)cls+=' review-unattempted';}
      const tag=locked?'div':'button';
      const action=mode==='exam'?` onclick="window.QB.selectExam(${n})"`:mode==='practice'?` onclick="window.QB.selectPractice('${q.id}',${n})"`:'';
      return `<${tag} class="${cls}"${action}${tag==='button'?' type="button"':''}><span class="option-letter">${o.letter}</span><span class="option-text">${esc(o.text)}</span></${tag}>`;
    }).join('');
  }

  function nkStudySupport(q,timeMs,unattempted=false) {
    const takeaway=nkSourceTakeaway(q);
    const time=unattempted
      ? `<div class="nk-answer-time is-empty">${navIcon('clock',19)}<span>Not answered in this test</span></div>`
      : `<div class="nk-answer-time">${navIcon('clock',19)}<span>Answered in <strong>${esc(nkFormatQuestionTime(timeMs||0))}</strong></span></div>`;
    return `<div class="nk-study-support">${time}${takeaway?`<section class="nk-key-takeaway"><span class="nk-takeaway-icon">${navIcon('bulb',22)}</span><div><div class="nk-takeaway-label">Key takeaway</div><p>${esc(takeaway)}</p></div></section>`:''}<section class="nk-source-section"><header><div>${navIcon('book',19)}<strong>Source explanation</strong></div><span>Original PDF</span></header>${q.explanation?`<div class="feedback-body source-explanation">${renderExplanationText(q.explanation,q)}</div>`:'<div class="nk-source-empty">No source explanation was provided for this question.</div>'}</section></div>`;
  }

  function nkSessionActionBar(s,mode) {
    const prevDisabled=s.index===0?'disabled':'';
    return `<div class="fixed-actions nk-session-footer" role="toolbar" aria-label="Question navigation"><div class="fixed-actions-inner"><button class="ghost-btn" onclick="window.QB.prevQ()" ${prevDisabled}>${navIcon('back',20)} Previous</button><button class="primary-btn" onclick="window.QB.nextQ()">Next ${navIcon('chevron',20)}</button></div></div>`;
  }

  function practicePage() {
    const s=state.activeSession;
    if(!s || s.mode!=='practice') return dashboard();
    const q=BY_ID[s.questionIds[s.index]]; if(!q) return dashboard();
    const selected=s.answers[q.id]||null,submitted=Boolean(s.submitted[q.id]);
    return sessionShell(`<div class="nk-v114-session is-practice">${nkSessionHeader(q,s,'practice')}<div class="question-shell"><section class="question-card">${nkQuestionContext(q)}<div class="question-text">${esc(q.question)}</div><div class="option-list">${nkSessionOptions(q,selected,'practice',submitted)}</div>${submitted?nkStudySupport(q,s.questionTimes?.[q.id]||0,false):''}</section></div></div>`,'topics')+practiceActionBar(s,q,selected,submitted);
  }

  '''


PRACTICE_ACTION = r'''function practiceActionBar(s, q, selected, submitted) {
    return nkSessionActionBar(s,'practice');
  }

  '''


EXAM_PAGE = r'''function examPage() {
    const s=state.activeSession;
    if(!s || s.mode!=='exam') return dashboard();
    const q=BY_ID[s.questionIds[s.index]]; if(!q) return dashboard();
    const selected=s.answers[q.id]||null;
    const elapsed=Math.max(0,Date.now()-s.startedAt),totalSec=s.questionIds.length*60;
    const remaining=Math.max(0,totalSec-Math.floor(elapsed/1000));
    const timer=`<div class="nk-exam-strip"><span>Timed CBT · answers remain changeable</span><strong id="exam-timer" class="timer ${remaining<120?'danger':remaining<300?'warn':''}">${formatTimer(remaining)}</strong></div>`;
    return sessionShell(`<div class="nk-v114-session is-exam">${nkSessionHeader(q,s,'exam',timer)}<div class="question-shell"><section class="question-card">${nkQuestionContext(q)}<div class="question-text">${esc(q.question)}</div><div class="option-list">${nkSessionOptions(q,selected,'exam',false)}</div></section></div></div>`,'tests')+nkSessionActionBar(s,'exam');
  }

  '''


REVIEW_PAGE = r'''function reviewTestPage(){
    let s=state.activeSession;
    const routeId=(()=>{try{return decodeURIComponent(String(route.id||''));}catch(_){return String(route.id||'');}})();
    if(!s || s.mode!=='review' || (routeId&&String(s.sourceTestId)!==routeId)){
      const t=state.tests.find(x=>String(x.id)===routeId||String(x.id)===String(route.id));
      if(!t)return testsPage();
      s=buildReviewSession(t);state.activeSession=s;saveState();
    }
    const q=BY_ID[s.questionIds[s.index]];if(!q)return testsPage();
    const selected=s.answers[q.id]||null;
    return sessionShell(`<div class="nk-v114-session is-review">${nkSessionHeader(q,s,'review')}<div class="question-shell"><section class="question-card">${nkQuestionContext(q)}<div class="question-text">${esc(q.question)}</div><div class="option-list">${nkSessionOptions(q,selected,'review',true)}</div>${nkStudySupport(q,s.questionTimes?.[q.id]||0,!selected)}</section></div></div>`,'tests')+nkSessionActionBar(s,'review');
  }

  '''


NAVIGATOR = r'''function openQuestionNavigator(){
    closeQuestionNavigator();
    const s=state.activeSession;
    if(!s||!Array.isArray(s.questionIds)||!s.questionIds.length){showToast('No active question session.','bad');return;}
    const review=s.mode==='review',exam=s.mode==='exam',practice=s.mode==='practice';
    const items=s.questionIds.map((id,i)=>{
      const q=BY_ID[id];if(!q)return'';
      const val=s.answers&&s.answers[id],submitted=Boolean(s.submitted&&s.submitted[id]);
      let cls=i===s.index?'active ':'';
      if(exam){if(val)cls+='answered ';}
      else if(submitted){cls+=Number(q.correctOption)===Number(val)?'correct ':'incorrect ';}
      else if(val)cls+='answered ';
      if(state.bookmarks&&state.bookmarks[id])cls+='bookmarked ';
      return `<button type="button" class="qb-nav-q ${cls}" onclick="window.QB.jumpFromNavigator(${i})" aria-label="Question ${i+1}"><span>${i+1}</span></button>`;
    }).join('');
    const legend=exam
      ? '<span><i class="qb-legend-dot current"></i>Current</span><span><i class="qb-legend-dot answered"></i>Answered</span><span><i class="qb-legend-dot unanswered"></i>Unanswered</span>'
      : '<span><i class="qb-legend-dot current"></i>Current</span><span><i class="qb-legend-dot correct"></i>Correct</span><span><i class="qb-legend-dot incorrect"></i>Incorrect</span><span><i class="qb-legend-dot unanswered"></i>Unanswered</span>';
    const action=exam
      ? '<button type="button" class="primary-btn qb-nav-submit" onclick="window.QB.submitExam(false)">Submit Test</button>'
      : practice
        ? '<button type="button" class="primary-btn qb-nav-submit" onclick="window.QB.closeQuestionNavigator();window.QB.openSessionReview()">Review or Finish Session</button>'
        : review?'<button type="button" class="primary-btn qb-nav-submit" onclick="window.QB.endReview()">End Review</button>':'';
    document.body.insertAdjacentHTML('beforeend',`<div class="qb-nav-backdrop" id="qb-question-navigator" role="dialog" aria-modal="true" aria-labelledby="qb-nav-title"><div class="qb-nav-panel"><div class="qb-nav-head"><div><div class="qb-nav-eyebrow">${esc(review?'Review Solutions':exam?'Timed CBT':'Guided Practice')}</div><h3 id="qb-nav-title">Question Navigator</h3><p>${s.questionIds.length} questions · tap a number to jump</p></div><button type="button" class="qb-nav-close" aria-label="Close navigator" onclick="window.QB.closeQuestionNavigator()">${navIcon('close',20)}</button></div><div class="qb-nav-grid">${items}</div><div class="qb-nav-legend">${legend}</div>${action}</div></div>`);
  }

  '''


CSS = r'''<style id="nk-session-experience-v114">
:root{--nk-indigo:#29265f;--nk-blue:#3777ed;--nk-blue-deep:#2458bd;--nk-ink:#11183d;--nk-muted:#67708e;--nk-line:#e1e5ef;--nk-green:#109a63;--nk-green-soft:#effaf5;--nk-red:#c94b57;--nk-red-soft:#fff3f4;--nk-canvas:#fffefa}
body:has(.nk-v114-session){background:var(--nk-canvas)!important}
body:has(.nk-v114-session) .bottom-nav{display:none!important}
.qbank-session-page:has(.nk-v114-session){max-width:none!important;padding:0 14px calc(94px + env(safe-area-inset-bottom))!important;background:var(--nk-canvas)!important}
.nk-v114-session{width:min(100%,760px);margin:0 auto;color:var(--nk-ink)}
.nk-session-head{height:62px;display:grid;grid-template-columns:48px 1fr auto;align-items:center}.nk-session-head .nk-session-back{justify-self:start}.nk-session-count{justify-self:center;font-size:18px;color:#26305a;letter-spacing:.2px}.nk-session-count strong{font-size:22px;color:#101947}.nk-session-head .q-actions{display:flex;align-items:center;gap:7px}.nk-session-head .icon-btn{width:44px!important;height:44px!important;border:0!important;background:transparent!important;color:#121b49!important;border-radius:12px!important}
.nk-session-progress{display:grid;grid-template-columns:1fr 44px;align-items:center;gap:10px;margin:0 0 20px}.nk-session-progress:before{content:"";grid-column:1;grid-row:1;height:5px;background:#e8ebf2;border-radius:999px}.nk-session-progress i{grid-column:1;grid-row:1;height:5px;background:var(--nk-blue);border-radius:999px;z-index:1;transition:width .2s ease}.nk-session-progress span{font-size:12px;font-weight:800;color:#52618e;text-align:right}
.nk-exam-strip{min-height:44px;margin:-4px 0 18px;padding:7px 11px;border:1px solid #dbe6ff;border-radius:12px;background:#f3f7ff;display:flex;align-items:center;justify-content:space-between;gap:12px;color:#5a6787;font-size:11px}.nk-exam-strip .timer{font-size:15px!important;color:var(--nk-blue-deep);background:transparent!important;padding:0!important;border:0!important}.nk-exam-strip .timer.warn{color:#a66b0d!important}.nk-exam-strip .timer.danger{color:#be3f4b!important}
.nk-v114-session .question-shell{display:block!important;margin:0!important}.nk-v114-session .question-card{border:0!important;border-radius:0!important;box-shadow:none!important;background:transparent!important;padding:0!important;min-width:0}
.nk-question-context{display:inline-flex;max-width:100%;min-height:42px;align-items:center;gap:8px;padding:5px 12px 5px 7px;margin-bottom:20px;border-radius:14px;background:#f5f5fa;color:#59617d;font-size:13px;line-height:1.2}.nk-question-context strong{color:#17204c;font-size:14px}.nk-question-context>i{width:3px;height:3px;border-radius:50%;background:#8a90a6;flex:none}.nk-subject-icon{width:32px;height:32px;border-radius:10px;display:grid;place-items:center;flex:none}.nk-question-context.is-physiology .nk-subject-icon{background:#fff0ee;color:#c85a50}.nk-question-context.is-anatomy .nk-subject-icon{background:#edf7fc;color:#277899}.nk-question-context.is-biochemistry .nk-subject-icon{background:#f9edf6;color:#a22a80}
.nk-v114-session .question-text{margin:0 0 20px!important;color:#10163b!important;font-size:21px!important;line-height:1.4!important;font-weight:720!important;letter-spacing:-.3px!important;text-align:left!important}
.nk-v114-session .option-list{display:grid!important;gap:10px!important}.nk-v114-session .option{width:100%;min-height:60px!important;display:grid!important;grid-template-columns:38px minmax(0,1fr)!important;align-items:center!important;gap:10px!important;padding:10px 12px!important;border:1px solid #dfe3ec!important;border-radius:13px!important;background:#fff!important;color:#11183d!important;box-shadow:none!important;text-align:left!important;opacity:1!important}.nk-v114-session button.option:active{transform:scale(.995)}
.nk-v114-session .option-letter{width:34px!important;height:34px!important;min-width:34px!important;border-radius:50%!important;display:grid!important;place-items:center!important;padding:0!important;background:#f0f2f6!important;color:#17204b!important;font-size:14px!important;font-weight:800!important}.nk-v114-session .option-text{font-size:15.5px!important;line-height:1.42!important;font-weight:560!important;letter-spacing:-.08px!important}.nk-v114-session .option.selected{border-color:#7da5fa!important;background:#f2f6ff!important}.nk-v114-session .option.selected .option-letter{background:var(--nk-blue)!important;color:#fff!important}.nk-v114-session .option.correct{border-color:#3dbf85!important;background:var(--nk-green-soft)!important}.nk-v114-session .option.correct .option-letter{background:var(--nk-green)!important;color:#fff!important}.nk-v114-session .option.wrong{border-color:#e06b72!important;background:var(--nk-red-soft)!important}.nk-v114-session .option.wrong .option-letter{background:var(--nk-red)!important;color:#fff!important}
.nk-study-support{margin-top:14px}.nk-answer-time{min-height:50px;display:flex;align-items:center;gap:10px;padding:9px 13px;border:1px solid #cfe0ff;border-left:4px solid var(--nk-blue);border-radius:12px;background:#edf4ff;color:#49618f;font-size:13px;box-shadow:0 4px 14px rgba(55,119,237,.08)}.nk-answer-time svg{color:var(--nk-blue)}.nk-answer-time strong{color:var(--nk-blue-deep);font-size:14px}.nk-answer-time.is-empty{border-left-color:#a7afc1;background:#f6f7fa;color:#70778a;box-shadow:none}.nk-answer-time.is-empty svg{color:#7c8498}
.nk-key-takeaway{display:grid;grid-template-columns:42px 1fr;gap:10px;align-items:center;margin-top:14px;padding:15px 14px;border-radius:14px;background:#eff9f3;color:#173e35}.nk-takeaway-icon{width:36px;height:36px;display:grid;place-items:center;color:#159b65;border-right:1px solid #cfe9dc}.nk-takeaway-label{font-size:10px;font-weight:850;letter-spacing:1.15px;text-transform:uppercase;color:#138858}.nk-key-takeaway p{font-size:15px;line-height:1.46;margin:4px 0 0;color:#17234e}
.nk-source-section{margin-top:18px;padding-top:14px;border-top:1px solid var(--nk-line)}.nk-source-section>header{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:10px}.nk-source-section>header>div{display:flex;align-items:center;gap:8px;font-size:16px;color:#15204f}.nk-source-section>header>div svg{color:#356bd6}.nk-source-section>header>span{padding:5px 9px;border-radius:999px;background:#f3f6ff;color:#4268c7;font-size:10px;font-weight:750}.nk-source-section .source-pdf-explanation{margin:0!important;border:1px solid var(--nk-line)!important;border-radius:12px!important;background:#fff!important;overflow:hidden}.nk-source-section .source-pdf-scroll{max-height:none!important;overflow:visible!important;padding:6px!important}.nk-source-section .source-pdf-head,.nk-source-section .source-pdf-note{display:none!important}.nk-source-section .source-pdf-page{margin:0 0 8px!important;border:0!important;border-radius:8px!important;overflow:hidden!important;background:#fff!important}.nk-source-section .source-pdf-page:last-child{margin-bottom:0!important}.nk-source-section .source-pdf-page img{display:block!important;width:100%!important;height:auto!important;image-rendering:auto}.nk-source-empty{padding:18px;border:1px solid var(--nk-line);border-radius:12px;color:var(--nk-muted);font-size:13px}
.nk-v114-session .nk-source-visuals{margin:12px 0 20px!important}.nk-v114-session .nk-source-visual{width:100%!important}.nk-v114-session .nk-source-visual img{width:100%!important;height:auto!important;max-width:100%!important;max-height:none!important;object-fit:contain!important;image-rendering:auto!important}
.nk-session-footer{position:fixed!important;left:0!important;right:0!important;bottom:0!important;z-index:220!important;width:100%!important;margin:0!important;box-sizing:border-box!important;background:#fffefa!important;border-top:1px solid #e1e4ec!important;box-shadow:0 -5px 18px rgba(26,32,65,.08)!important;padding:9px 14px calc(9px + env(safe-area-inset-bottom))!important}.nk-session-footer .fixed-actions-inner{width:min(100%,760px)!important;margin:0 auto!important;display:grid!important;grid-template-columns:1fr 1fr!important;gap:10px!important}.nk-session-footer button{position:static!important;width:100%!important;min-height:52px!important;border-radius:13px!important;display:flex!important;align-items:center!important;justify-content:center!important;gap:7px!important;font-size:15px!important;font-weight:800!important}.nk-session-footer .ghost-btn{border:1px solid #cfd5e1!important;background:#fff!important;color:#1b2452!important}.nk-session-footer .primary-btn{border:0!important;background:var(--nk-indigo)!important;color:#fff!important}.nk-session-footer button:disabled{opacity:.42!important}
.qb-nav-backdrop{z-index:1200!important;padding:10px!important;place-items:end center!important}.qb-nav-panel{width:min(720px,100%)!important;max-height:calc(100vh - 20px)!important;border-radius:22px 22px 16px 16px!important;padding:16px!important}.qb-nav-grid{grid-template-columns:repeat(6,minmax(0,1fr))!important}.qb-nav-q span{font-size:12px;font-weight:850}.qb-nav-submit{position:sticky!important;bottom:0!important;min-height:48px!important;margin-top:14px!important;box-shadow:0 -8px 16px rgba(255,255,255,.96)!important}
@media(max-width:520px){.nk-session-progress{margin-bottom:18px}.nk-question-context{margin-bottom:18px}.nk-v114-session .question-text{font-size:20px!important}.nk-v114-session .option{min-height:58px!important;padding:9px 11px!important}.nk-key-takeaway{padding:14px 12px}.nk-session-footer{padding-left:12px!important;padding-right:12px!important}.qb-nav-grid{gap:7px!important}}
</style>'''


def replace_function(source: str, name: str, replacement: str) -> str:
    start = source.find(f"function {name}(")
    if start < 0:
        raise SystemExit(f"{name} not found")
    brace = source.find("{", start)
    depth = 0
    end = -1
    for index in range(brace, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                end = index + 1
                break
    if end < 0:
        raise SystemExit(f"{name} end not found")
    return source[:start] + replacement.rstrip() + source[end:]


def transform(source: str) -> str:
    source = re.sub(r'<style id="nk-question-experience-v113">.*?</style>\s*', '', source, flags=re.S)
    source = re.sub(rf'<style id="{STYLE_ID}">.*?</style>\s*', '', source, flags=re.S)
    if "function nkPracticeTakeaway(" in source:
        source = replace_function(source, "nkPracticeTakeaway", "")
    source = replace_function(source, "practicePage", HELPERS_AND_PRACTICE)
    source = replace_function(source, "practiceActionBar", PRACTICE_ACTION)
    source = replace_function(source, "examPage", EXAM_PAGE)
    source = replace_function(source, "reviewTestPage", REVIEW_PAGE)
    source = replace_function(source, "openQuestionNavigator", NAVIGATOR)

    molecule = '      molecule:`<svg ${common}><circle cx="6" cy="12" r="2.5"/><circle cx="17.5" cy="6" r="2.5"/><circle cx="17.5" cy="18" r="2.5"/><path d="m8.3 10.8 7-3.6M8.3 13.2l7 3.6"/></svg>`,\n'
    if "dna:`<svg ${common}>" not in source:
        if molecule not in source:
            raise SystemExit("V11.3 molecule icon marker not found")
        dna = '      dna:`<svg ${common}><path d="M5 3c7 0 7 18 14 18M19 3C12 3 12 21 5 21"/><path d="M7.5 6h9M6.5 10h11M6.5 14h11M7.5 18h9"/></svg>`,\n'
        source = source.replace(molecule, molecule + dna, 1)
    if "</head>" not in source:
        raise SystemExit("</head> not found")
    return source.replace("</head>", CSS + "\n</head>", 1)


def main() -> None:
    source = HTML.read_text(encoding="utf-8")
    HTML.write_text(transform(source), encoding="utf-8")
    print("Applied V11.3.1 shared Practice/CBT/Review experience, functional navigator, and verified takeaways.")


if __name__ == "__main__":
    main()
