from pathlib import Path
import re

HTML = Path('app/src/main/assets/index.html')
s = HTML.read_text(encoding='utf-8')

# Remove all previous final CBT runtime layers from the generated HTML.  The
# canonical layer below must be the only owner of Review Solutions.
s = re.sub(r'<script id="cbt-final-lock-v3">.*?</script>\s*', '', s, flags=re.S)
s = re.sub(r'<script id="cbt-final-lock-v2">.*?</script>\s*', '', s, flags=re.S)

# Replace the CTA with exactly one stable entry point.
s = re.sub(
    r'onclick="return window\.__QB_OPEN_REVIEW\(this\.getAttribute\(\'data-review-test-id\'\)\)"',
    "onclick=\"return window.__QB_OPEN_REVIEW(this.getAttribute('data-review-test-id'))\"",
    s
)

lock = r'''<script id="cbt-canonical-review">
(function(){
  'use strict';

  function esc(v){return String(v==null?'':v).replace(/[&<>\"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[c];});}
  function state(){
    try{if(window.QB&&typeof window.QB.getState==='function'){var x=window.QB.getState();if(x)return x;}}catch(e){}
    try{return JSON.parse(localStorage.getItem('qbank_state_v1')||'{}');}catch(e){return {};}
  }
  function questions(){
    var out=[],base=window.QBANK_DATA||{};
    if(Array.isArray(base.questions))out=out.concat(base.questions.map(function(q){return Object.assign({},q,{subject:q.subject||'Biochemistry'});}));
    var ss=window.SUBJECT_QBANK_DATA&&Array.isArray(window.SUBJECT_QBANK_DATA.subjects)?window.SUBJECT_QBANK_DATA.subjects:[];
    ss.forEach(function(sub){if(Array.isArray(sub.questions))out=out.concat(sub.questions.map(function(q){return Object.assign({},q,{subject:q.subject||sub.subject});}));});
    return out;
  }
  function findQuestion(id){var wanted=String(id),qs=questions();return qs.find(function(q){return String(q.id)===wanted;})||null;}
  function subject(q){var id=String(q&&q.id||'').toLowerCase();if(id.indexOf('anatomy-')===0)return'anatomy';if(id.indexOf('physiology-')===0)return'physiology';return'biochemistry';}
  function solutionSegments(q){
    var sub=subject(q),id=String(q&&q.id||''),hit=null,arr=[];
    if(sub==='biochemistry'&&Array.isArray(window.BIOCHEM_SOURCE_SOLUTIONS))arr=window.BIOCHEM_SOURCE_SOLUTIONS;
    if(sub!=='biochemistry'&&window.SUBJECT_SOURCE_SOLUTIONS&&Array.isArray(window.SUBJECT_SOURCE_SOLUTIONS[sub]))arr=window.SUBJECT_SOURCE_SOLUTIONS[sub];
    hit=arr.find(function(x){return String(x.id)===id;});
    if(hit&&Array.isArray(hit.segments)&&hit.segments.length)return hit.segments;
    var m=String(q&&q.sourceRef||'').match(/Solution\s+Pages?\s+(\d+)(?:\s*-\s*(\d+))?/i),r=[];
    if(m){for(var p=Number(m[1]);p<=Number(m[2]||m[1]);p++)r.push({page:p});}
    return r;
  }
  function solution(q){
    var sub=subject(q),label=sub==='anatomy'?'Anatomy':sub==='physiology'?'Physiology':'Biochemistry',segs=solutionSegments(q);
    if(!segs.length)return'<div class="source-pdf-note">Original source solution is not mapped for this question.</div>';
    return'<div class="source-pdf-explanation"><div class="source-pdf-head">Original source solution · '+label+'</div>'+segs.map(function(x){
      var u='https://qbank.local/'+sub+'/pdf?page='+encodeURIComponent(x.page)+'&scale=3.5'+(x.top!=null?'&top='+encodeURIComponent(x.top):'')+(x.bottom!=null?'&bottom='+encodeURIComponent(x.bottom):'');
      return'<div class="source-pdf-page" onclick="window.openSourceZoom(this.querySelector(\'img\'))"><img loading="lazy" src="'+u+'" alt="Original '+label+' PDF solution page '+esc(x.page)+'"></div>';
    }).join('')+'</div>';
  }
  function clean(){
    document.querySelectorAll('.navigator .primary-btn,.qb-nav-submit').forEach(function(b){if(/submit\s*test/i.test(String(b.textContent||'')))b.remove();});
    var n=document.getElementById('qb-question-navigator');if(n)n.remove();
    document.querySelectorAll('#toast-root .toast').forEach(function(x){x.remove();});
  }
  function testsPage(){
    try{if(window.QB&&typeof window.QB.nav==='function'){window.QB.nav('tests');return;}}catch(e){}
    location.hash='#tests';
  }
  function persist(st,session){st.activeSession=session;localStorage.setItem('qbank_state_v1',JSON.stringify(st));}
  function openReview(testId){
    var st=state(),wanted;try{wanted=decodeURIComponent(String(testId||''));}catch(e){wanted=String(testId||'');}
    var t=(Array.isArray(st.tests)?st.tests:[]).find(function(x){return String(x.id)===wanted||String(x.id)===String(testId);});
    if(!t||!Array.isArray(t.questionIds)||!t.questionIds.length){console.error('Canonical CBT Review: test not found',wanted);return false;}
    var session={id:'review_'+String(t.id),mode:'review',sourceTestId:String(t.id),title:'Review · '+String(t.title||'Completed Test'),questionIds:t.questionIds.slice(),index:0,answers:Object.assign({},t.answers||{}),questionTimes:Object.assign({},t.questionTimes||{})};
    persist(st,session);render(session,t);return false;
  }
  function render(session,test){
    clean();
    var q=findQuestion(session.questionIds[session.index]),app=document.getElementById('app');
    if(!app||!q){console.error('Canonical CBT Review: question/app missing',session.questionIds[session.index]);return;}
    var selected=Number(session.answers[q.id]||0),correct=Number(q.correctOption||0),status=selected?(selected===correct?'Correct':'Incorrect'):'Unattempted';
    var opts=(Array.isArray(q.options)?q.options:[]).map(function(o){var n=o.letter?o.letter.charCodeAt(0)-64:0,c='option';if(n===selected)c+=' selected';if(n===correct)c+=' correct';if(n===selected&&n!==correct)c+=' wrong';return'<div class="'+c+'"><span class="radio"></span><span class="option-letter">'+esc(o.letter||'')+'</span><span class="option-text">'+esc(o.text||'')+'</span></div>';}).join('');
    app.innerHTML='<header class="topbar"><div class="brand">QBank</div><button class="ghost-btn" id="cr-back">Back to Tests</button></header><main class="page fade-in"><div class="page-head"><div><div class="mode-pill">Test Review</div><h1 class="page-title" style="margin-top:9px">'+esc(session.title)+'</h1><div class="page-sub">Question '+(session.index+1)+' of '+session.questionIds.length+'</div></div></div><section class="card question-card"><div class="q-number">Question '+esc(q.questionNumber||session.index+1)+' of '+session.questionIds.length+'</div><div class="crumb">'+esc(q.chapter||'')+'</div><div class="question-text">'+esc(q.question||'')+'</div><div class="option-list">'+opts+'</div><div class="feedback '+(status==='Correct'?'good':'bad')+'"><div class="feedback-title">'+status+'</div><div class="label">Correct answer</div><div style="font-weight:800">'+(correct?String.fromCharCode(64+correct)+'. '+esc((q.options&&q.options[correct-1]&&q.options[correct-1].text)||''):'')+'</div></div>'+solution(q)+'<div class="q-footer"><button class="ghost-btn" id="cr-prev" '+(session.index<=0?'disabled':'')+'>Previous</button><button class="primary-btn" id="cr-next" '+(session.index>=session.questionIds.length-1?'disabled':'')+'>Next</button></div></section></main>';
    document.getElementById('cr-back').onclick=function(){testsPage();};
    document.getElementById('cr-prev').onclick=function(){if(session.index>0){session.index--;persist(state(),session);render(session,test);}};
    document.getElementById('cr-next').onclick=function(){if(session.index<session.questionIds.length-1){session.index++;persist(state(),session);render(session,test);}};
  }
  window.__QB_OPEN_REVIEW=openReview;
  window.QB=window.QB||{};
  window.QB.reviewTest=openReview;
  if(typeof window.QB.submitExam==='function'&&!window.QB.submitExam.__canonicalReviewSubmit){
    var original=window.QB.submitExam;
    function submit(){clean();try{return original.apply(this,arguments);}finally{setTimeout(clean,0);setTimeout(clean,80);setTimeout(clean,250);}}
    submit.__canonicalReviewSubmit=true;window.QB.submitExam=submit;
  }
})();
</script>'''

s=s.replace('</body>',lock+'\n</body>',1)
HTML.write_text(s,encoding='utf-8')
print('Canonical CBT Review renderer installed; previous v2/v3 runtime layers removed.')
