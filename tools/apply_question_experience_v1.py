from pathlib import Path
import re


HTML = Path("app/src/main/assets/index.html")
STYLE_ID = "nk-question-experience-v113"


HELPERS_AND_PAGE = r'''function nkPracticeSubject(q) {
    const raw=String(q?.subject||activeSubject||'').trim();
    if(raw) return raw.charAt(0).toUpperCase()+raw.slice(1).toLowerCase();
    const id=String(q?.id||'').toLowerCase();
    return id.startsWith('physiology-')?'Physiology':id.startsWith('anatomy-')?'Anatomy':'Biochemistry';
  }

  function nkPracticeSubjectKey(q) { return nkPracticeSubject(q).toLowerCase(); }

  function nkPracticeSubjectIcon(q) {
    const key=nkPracticeSubjectKey(q);
    return navIcon(key==='physiology'?'heart':key==='anatomy'?'body':'molecule',20);
  }

  function nkFormatQuestionTime(ms) {
    const seconds=Math.max(0,Math.round(Number(ms||0)/1000));
    if(seconds<60) return `${seconds} second${seconds===1?'':'s'}`;
    const minutes=Math.floor(seconds/60), remainder=seconds%60;
    return remainder?`${minutes} min ${String(remainder).padStart(2,'0')} sec`:`${minutes} min`;
  }

  function nkPracticeTakeaway(q) {
    const explicit=String(q?.keyTakeaway||q?.takeaway||'').trim();
    if(explicit) return explicit;
    const option=Array.isArray(q?.options)?q.options[Number(q.correctOption)-1]:null;
    return option?.text?String(option.text):'';
  }

  function practicePage() {
    const s=state.activeSession;
    if(!s || s.mode!=='practice') return dashboard();
    const q=BY_ID[s.questionIds[s.index]]; if(!q) return dashboard();
    const selected=s.answers[q.id] || null;
    const submitted=Boolean(s.submitted[q.id]);
    const total=Math.max(1,s.questionIds.length), position=s.index+1;
    const progress=Math.max(0,Math.min(100,Math.round(position/total*100)));
    const subject=nkPracticeSubject(q), subjectKey=nkPracticeSubjectKey(q);
    const takeaway=nkPracticeTakeaway(q);
    const timeText=nkFormatQuestionTime(s.questionTimes?.[q.id]||0);
    const navItems=s.questionIds.map((id,i)=>{const qq=BY_ID[id], val=s.answers[id], sub=Boolean(s.submitted[id]), corr=sub&&Number(qq.correctOption)===Number(val);let cls=i===s.index?'active ':'';if(sub)cls+=corr?'correct ':'incorrect ';else if(val)cls+='answered ';if(state.bookmarks[id])cls+='bookmarked';return `<button class="nav-q ${cls}" onclick="window.QB.goIndex(${i})" aria-label="Question ${i+1}">${i+1}</button>`}).join('');
    const feedback=submitted?`<div class="nk-practice-response">
      <div class="nk-answer-time">${navIcon('clock',18)}<span>Answered in <strong>${esc(timeText)}</strong></span></div>
      ${takeaway?`<section class="nk-key-takeaway"><span class="nk-takeaway-icon">${navIcon('bulb',22)}</span><div><div class="nk-takeaway-label">Key takeaway</div><p>${esc(takeaway)}</p></div></section>`:''}
      <section class="nk-source-section"><header><div>${navIcon('book',19)}<strong>Source explanation</strong></div><span>Original PDF</span></header>${q.explanation?`<div class="feedback-body source-explanation">${renderExplanationText(q.explanation,q)}</div>`:'<div class="nk-source-empty">No source explanation was provided for this question.</div>'}</section>
    </div>`:'';
    return sessionShell(`
      <div class="nk-v113-question">
        <header class="practice-focus-head"><button class="icon-btn nk-session-exit" aria-label="End practice session" onclick="window.QB.endSession()">${navIcon('back',24)}</button><div class="nk-session-count"><strong>${position}</strong> / ${total}</div><div class="q-actions">${bookmarkButton(q.id,23)}<button class="icon-btn" aria-label="Question navigator" onclick="window.QB.openQuestionNavigator()">${navIcon('grid',22)}</button></div></header>
        <div class="nk-session-progress" role="progressbar" aria-label="Session progress" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${progress}"><i style="width:${progress}%"></i><span>${progress}%</span></div>
        <div class="question-shell"><section class="question-card"><div class="nk-question-context is-${esc(subjectKey)}"><span class="nk-subject-icon">${nkPracticeSubjectIcon(q)}</span><strong>${esc(subject)}</strong><i aria-hidden="true"></i><span>${esc(q.chapter)}</span></div><div class="question-text">${esc(q.question)}</div><div class="option-list">${q.options.map(o=>{const n=o.letter.charCodeAt(0)-64,isChosen=Number(selected)===n,isCorrectOption=Number(q.correctOption)===n,isWrongChosen=submitted&&isChosen&&!isCorrectOption;let cls='option';if(submitted&&isCorrectOption)cls+=' correct';if(isWrongChosen)cls+=' wrong';if(isChosen&&!submitted)cls+=' selected';const status=submitted&&isCorrectOption?navIcon('check',20):isWrongChosen?navIcon('close',19):'';return `<button class="${cls}" ${submitted?'disabled':''} onclick="window.QB.selectPractice('${q.id}',${n})"><span class="option-letter">${o.letter}</span><span class="option-text">${esc(o.text)}</span><span class="nk-option-state">${status}</span></button>`}).join('')}</div>${feedback}</section><aside class="card navigator"><div class="section-title"><span>Question Navigator</span><span class="sub">${total}</span></div><div class="nav-grid">${navItems}</div><div class="nav-legend"><span><i class="legend-dot" style="background:#eff5ff"></i>Answered</span><span><i class="legend-dot" style="background:#effbf6"></i>Correct</span><span><i class="legend-dot" style="background:#fff3f3"></i>Incorrect</span><span><i class="legend-dot"></i>Unanswered</span></div></aside></div>
      </div>
    `,'topics') + practiceActionBar(s, q, selected, submitted);
  }

  '''


ACTION_BAR = r'''function practiceActionBar(s, q, selected, submitted) {
    return `<div class="fixed-actions practice-actions nk-v113-actions" role="toolbar" aria-label="Practice navigation"><div class="fixed-actions-inner"><button class="ghost-btn" onclick="window.QB.prevQ()" ${s.index===0?'disabled':''}>${navIcon('back',20)} Previous</button><button class="primary-btn" onclick="window.QB.nextQ()">Next ${navIcon('chevron',20)}</button></div></div>`;
  }

  '''


CSS = r'''<style id="nk-question-experience-v113">
:root{--nk-indigo:#29265f;--nk-blue:#3f75e8;--nk-ink:#11183d;--nk-muted:#67708e;--nk-line:#e1e5ef;--nk-green:#109a63;--nk-green-soft:#effaf5;--nk-blue-soft:#f4f7ff;--nk-canvas:#fffefa}
body:has(.nk-v113-question){background:var(--nk-canvas)}
body:has(.nk-v113-question) .bottom-nav{display:none!important}
.qbank-session-page:has(.nk-v113-question){max-width:none!important;padding:0 16px calc(104px + var(--safe-bottom))!important;background:var(--nk-canvas)}
.nk-v113-question{width:min(100%,760px);margin:0 auto;color:var(--nk-ink)}
.nk-v113-question .practice-focus-head{height:62px;margin:0!important;padding:5px 0!important;display:grid!important;grid-template-columns:48px 1fr auto;align-items:center;border-bottom:0}
.nk-v113-question .nk-session-exit{justify-self:start}.nk-v113-question .nk-session-count{justify-self:center;font-size:18px;color:#26305a;letter-spacing:.2px}.nk-v113-question .nk-session-count strong{font-size:22px;color:#101947}
.nk-v113-question .q-actions{display:flex;align-items:center;gap:7px}.nk-v113-question .icon-btn{width:44px!important;height:44px!important;border:0!important;background:transparent!important;color:#121b49!important;border-radius:12px!important}
.nk-session-progress{display:grid;grid-template-columns:1fr 44px;align-items:center;gap:10px;margin:0 0 22px}.nk-session-progress:before{content:"";grid-column:1;grid-row:1;height:5px;background:#e8ebf2;border-radius:999px}.nk-session-progress i{grid-column:1;grid-row:1;height:5px;background:var(--nk-blue);border-radius:999px;z-index:1;transition:width .22s ease}.nk-session-progress span{font-size:12px;font-weight:750;color:#52618e;text-align:right}
.nk-v113-question .question-shell{display:grid;grid-template-columns:minmax(0,1fr) 250px;gap:20px!important;align-items:start}.nk-v113-question .question-card{border:0!important;border-radius:0!important;box-shadow:none!important;background:transparent!important;padding:0!important;min-width:0}
.nk-question-context{display:inline-flex;max-width:100%;min-height:42px;align-items:center;gap:8px;padding:5px 12px 5px 7px;margin-bottom:22px;border-radius:14px;background:#f5f5fa;color:#59617d;font-size:13px;line-height:1.2}.nk-question-context strong{color:#17204c;font-size:14px}.nk-question-context>i{width:3px;height:3px;border-radius:50%;background:#8a90a6;flex:none}.nk-subject-icon{width:32px;height:32px;border-radius:10px;display:grid;place-items:center;flex:none}.nk-question-context.is-physiology .nk-subject-icon{background:#fff0ee;color:#c85a50}.nk-question-context.is-anatomy .nk-subject-icon{background:#edf7fc;color:#277899}.nk-question-context.is-biochemistry .nk-subject-icon{background:#f9edf6;color:#9e287b}
.nk-v113-question .question-text{margin:0 0 22px!important;color:#10163b!important;font-size:22px!important;line-height:1.38!important;font-weight:720!important;letter-spacing:-.35px!important;text-align:left!important}
.nk-v113-question .option-list{display:grid;gap:10px!important}.nk-v113-question .option{width:100%;min-height:62px!important;display:grid!important;grid-template-columns:38px minmax(0,1fr) 34px!important;align-items:center!important;gap:10px!important;padding:10px 12px!important;border:1px solid #dfe3ec!important;border-radius:13px!important;background:#fff!important;color:#11183d!important;box-shadow:none!important;text-align:left!important;opacity:1!important}.nk-v113-question .option:active{transform:scale(.995)}
.nk-v113-question .option-letter{width:34px!important;height:34px!important;min-width:34px!important;border-radius:50%!important;display:grid!important;place-items:center!important;padding:0!important;background:#f0f2f6!important;color:#17204b!important;font-size:14px!important;font-weight:800!important}.nk-v113-question .option-text{font-size:16px!important;line-height:1.42!important;font-weight:520!important;letter-spacing:-.1px!important}.nk-option-state{width:30px;height:30px;border:1.5px solid #c5ccda;border-radius:50%;display:grid;place-items:center;color:#fff}
.nk-v113-question .option.correct{border-color:#3dbf85!important;background:var(--nk-green-soft)!important}.nk-v113-question .option.correct .option-letter,.nk-v113-question .option.correct .nk-option-state{background:var(--nk-green)!important;border-color:var(--nk-green)!important;color:#fff!important}.nk-v113-question .option.wrong{border-color:#e06b72!important;background:#fff4f4!important}.nk-v113-question .option.wrong .option-letter,.nk-v113-question .option.wrong .nk-option-state{background:#c94b57!important;border-color:#c94b57!important;color:#fff!important}
.nk-practice-response{margin-top:14px}.nk-answer-time{min-height:48px;display:flex;align-items:center;gap:9px;padding:8px 13px;border-radius:12px;background:var(--nk-blue-soft);color:#52649d;font-size:13px}.nk-answer-time strong{color:#263d83}
.nk-key-takeaway{display:grid;grid-template-columns:42px 1fr;gap:10px;align-items:center;margin-top:14px;padding:15px 14px;border-radius:14px;background:#eff9f3;color:#173e35}.nk-takeaway-icon{width:36px;height:36px;display:grid;place-items:center;color:#159b65;border-right:1px solid #cfe9dc}.nk-takeaway-label{font-size:10px;font-weight:850;letter-spacing:1.15px;text-transform:uppercase;color:#138858}.nk-key-takeaway p{font-size:15px;line-height:1.45;margin:4px 0 0;color:#17234e}
.nk-source-section{margin-top:18px;padding-top:14px;border-top:1px solid var(--nk-line)}.nk-source-section>header{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:10px}.nk-source-section>header>div{display:flex;align-items:center;gap:8px;font-size:16px;color:#15204f}.nk-source-section>header>div svg{color:#356bd6}.nk-source-section>header>span{padding:5px 9px;border-radius:999px;background:#f3f6ff;color:#4268c7;font-size:10px;font-weight:750}.nk-source-section .source-pdf-explanation{margin:0!important;border:1px solid var(--nk-line)!important;border-radius:12px!important;background:#fff!important;overflow:hidden}.nk-source-section .source-pdf-scroll{max-height:none!important;overflow:visible!important;padding:6px!important}.nk-source-section .source-pdf-head,.nk-source-section .source-pdf-note{display:none!important}.nk-source-section .source-pdf-page{margin:0 0 8px!important;border:0!important;border-radius:8px!important;overflow:hidden!important;background:#fff!important}.nk-source-section .source-pdf-page:last-child{margin-bottom:0!important}.nk-source-section .source-pdf-page img{display:block!important;width:100%!important;height:auto!important;image-rendering:auto}.nk-source-empty{padding:18px;border:1px solid var(--nk-line);border-radius:12px;color:var(--nk-muted);font-size:13px}
.nk-v113-question .source-box,.nk-v113-question .action-spacer{display:none!important}.nk-v113-question .navigator{position:sticky;top:12px}.nk-v113-actions{background:rgba(255,254,250,.98)!important;border-top:1px solid #e1e4ec!important;padding:10px 16px calc(10px + var(--safe-bottom))!important;backdrop-filter:none!important}.nk-v113-actions .fixed-actions-inner{width:min(100%,760px)!important;margin:0 auto!important;display:grid!important;grid-template-columns:1fr 1fr!important;gap:10px!important}.nk-v113-actions button{width:100%;min-height:52px!important;border-radius:13px!important;display:flex;align-items:center;justify-content:center;gap:7px;font-size:15px!important;font-weight:800!important}.nk-v113-actions .ghost-btn{border:1px solid #cfd5e1!important;background:#fff!important;color:#1b2452!important}.nk-v113-actions .primary-btn{border:0!important;background:var(--nk-indigo)!important;color:#fff!important}.nk-v113-actions button:disabled{opacity:.42!important}
@media(max-width:820px){.nk-v113-question .question-shell{grid-template-columns:1fr}.nk-v113-question .navigator{display:none!important}}
@media(max-width:520px){.qbank-session-page:has(.nk-v113-question){padding-left:14px!important;padding-right:14px!important}.nk-session-progress{margin-bottom:18px}.nk-question-context{margin-bottom:18px}.nk-v113-question .question-text{font-size:20px!important;line-height:1.4!important;margin-bottom:18px!important}.nk-v113-question .option{min-height:60px!important;padding:9px 11px!important}.nk-v113-question .option-text{font-size:15.5px!important}.nk-key-takeaway{padding:14px 12px}}
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
    source = re.sub(rf'<style id="{STYLE_ID}">.*?</style>\s*', "", source, flags=re.S)
    source = replace_function(source, "practicePage", HELPERS_AND_PAGE)
    source = replace_function(source, "practiceActionBar", ACTION_BAR)

    icon_needle = "      clock:`<svg ${common}><circle cx=\"12\" cy=\"12\" r=\"8.5\"/><path d=\"M12 7v5l3 2\"/></svg>`,"
    if "heart:`<svg ${common}>" not in source:
        if icon_needle not in source:
            raise SystemExit("navIcon clock marker not found")
        extra = """      heart:`<svg ${common}><path d=\"M12 21s-7-4.4-7-10a4 4 0 0 1 7-2.6A4 4 0 0 1 19 11c0 5.6-7 10-7 10Z\"/><path d=\"M3.5 12h4l1.5-3 2.4 6 1.7-3H20\"/></svg>`,\n      body:`<svg ${common}><circle cx=\"12\" cy=\"5\" r=\"2.2\"/><path d=\"M5 10h14M12 7.5V21M8 21l4-7 4 7\"/></svg>`,\n      molecule:`<svg ${common}><circle cx=\"6\" cy=\"12\" r=\"2.5\"/><circle cx=\"17.5\" cy=\"6\" r=\"2.5\"/><circle cx=\"17.5\" cy=\"18\" r=\"2.5\"/><path d=\"m8.3 10.8 7-3.6M8.3 13.2l7 3.6\"/></svg>`,\n      bulb:`<svg ${common}><path d=\"M9 18h6M10 22h4\"/><path d=\"M8.5 15.5A7 7 0 1 1 15.5 15.5L14 18h-4l-1.5-2.5Z\"/></svg>`,\n"""
        source = source.replace(icon_needle, extra + icon_needle, 1)

    if "&scale=3.5" not in source:
        raise SystemExit("source PDF scale marker not found")
    source = source.replace("&scale=3.5", "&scale=4")
    if "</head>" not in source:
        raise SystemExit("</head> not found")
    return source.replace("</head>", CSS + "\n</head>", 1)


def main() -> None:
    source = HTML.read_text(encoding="utf-8")
    HTML.write_text(transform(source), encoding="utf-8")
    print("Applied NK QBank V11.3 approved question experience and 4x source PDF rendering.")


if __name__ == "__main__":
    main()
