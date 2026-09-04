from pathlib import Path
import re

HTML = Path('app/src/main/assets/index.html')
s = HTML.read_text(encoding='utf-8')

# Remove every previous final CBT runtime layer. The canonical layer below is
# the sole owner of Review Solutions at runtime.
s = re.sub(r'<script id="cbt-final-lock-v3">.*?</script>\s*', '', s, flags=re.S)
s = re.sub(r'<script id="cbt-final-lock-v2">.*?</script>\s*', '', s, flags=re.S)

# Normalize all known Review Solutions CTA forms to one entry point.
s = s.replace("onclick=\"window.QB.reviewTest(this.getAttribute('data-review-test-id'))\"", "onclick=\"return window.__QB_OPEN_REVIEW(this.getAttribute('data-review-test-id'))\"")
s = s.replace("onclick=\"return window.__QB_OPEN_REVIEW(this.getAttribute('data-review-test-id'))\"", "onclick=\"return window.__QB_OPEN_REVIEW(this.getAttribute('data-review-test-id'))\"")

lock = r'''<script id="cbt-canonical-review">
(function(){
  'use strict';
  function esc(v){return String(v==null?'':v).replace(/[&<>\"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[c];});}
  function getState(){
    try{if(window.QB&&typeof window.QB.getState==='function'){var x=window.QB.getState();if(x)return x;}}catch(e){}
    try{return JSON.parse(localStorage.getItem('qbank_state_v1')||'{}');}catch(e){return {};}
  }
  function findQuestion(id){
    var wanted=String(id),base=window.QBANK_DATA||{},q=null;
    if(Array.isArray(base.questions)){q=base.questions.find(function(x){return String(x.id)===wanted;});if(q)return Object.assign({},q,{subject:q.subject||'Biochemistry'});}
    var ss=window.SUBJECT_QBANK_DATA&&Array.isArray(window.SUBJECT_QBANK_DATA.subjects)?window.SUBJECT_QBANK_DATA.subjects:[];
    for(var i=0;i<ss.length;i++){var a=Array.isArray(ss[i].questions)?ss[i].questions:[];q=a.find(function(x){return String(x.id)===wanted;});if(q)return Object.assign({},q,{subject:q.subject||ss[i].subject});}
    return null;
  }
  function subject(q){var id=String(q&&q.id||'').toLowerCase();if(id.indexOf('anatomy-')===0)return'anatomy';if(id.indexOf('physiology-')===0)return'physiology';return'biochemistry';}
  function segments(q){
    var sub=subject(q),id=String(q.id||''),arr=[];
    if(sub==='biochemistry'&&Array.isArray(window.BIOCHEM_SOURCE_SOLUTIONS))arr=window.BIOCHEM_SOURCE_SOLUTIONS;
    if(sub!=='biochemistry'&&window.SUBJECT_SOURCE_SOLUTIONS&&Array.isArray(window.SUBJECT_SOURCE_SOLUTIONS[sub]))arr=window.SUBJECT_SOURCE_SOLUTIONS[sub];
    var hit=arr.find(function(x){return String(x.id)===id;});
    if(hit&&Array.isArray(hit.segments)&&hit.segments.length)return hit.segments;
    var m=String(q.sourceRef||'').match(/Solution\s+Pages?\s+(\d+)(?:\s*-\s*(\d+))?/i),r=[];
    if(m)for(var p=Number(m[1]);p<=Number(m[2]||m[1]);p++)r.push({page:p});
    return r;
  }
  function source(q){
    var sub=subject(q),label=sub==='anatomy'?'Anatomy':sub==='physiology'?'Physiology':'Biochemistry',ss=segments(q);
    if(!ss.length)return'<div class="source-pdf-note">Original source solution is not mapped for this question.</div>';
    return'<div class="source-pdf-explanation"><div class="source-pdf-head">Original source solution · '+label+'</div>'+ss.map(function(x){var u='https://qbank.local/'+sub+'/pdf?page='+encodeURIComponent(x.page)+'&scale=3.5'+(x.top!=null?'&top='+encodeURIComponent(x.top):'')+(x.bottom!=null?'&bottom='+encodeURIComponent(x.bottom):'');return'<div class="source-pdf-page" onclick="window.openSourceZoom(this.querySelector(\'img\'))"><img loading="lazy" src="'+u+'" alt="Original '+label+' PDF solution page '+esc(x.page)+'"></div>';}).join('')+'</div>';
  }
  function clean(){document.querySelectorAll('.navigator .primary-btn,.qb-nav-submit').forEach(function(b){if(/submit\s*test/i.test(String(b.textContent||'')))b.remove();});var n=document.getElementById('qb-question-navigator');if(n)n.remove();document.querySelectorAll('#toast-root .toast').forEach(function(x){x.remove();});}
  function back(){try{if(window.QB&&typeof window.QB.nav==='function'){window.QB.nav('tests');return;}}catch(e){}location.hash='#tests';}
  function persist(st,s){st.activeSession=s;localStorage.setItem('qbank_state_v1',JSON.stringify(st));}
  function openReview(testId){
    var st=getState(),wanted;try{wanted=decodeURIComponent(String(testId||''));}catch(e){wanted=String(testId||'');}
    var t=(Array.isArray(st.tests)?st.tests:[]).find(function(x){return String(x.id)===wanted||String(x.id)===String(testId);});
    if(!t||!Array.isArray(t.questionIds)||!t.questionIds.length){console.error('Canonical CBT Review: test not found',wanted);return false;}
    var s={id:'review_'+String(t.id),mode:'review',sourceTestId:String(t.id),title:'Review · '+String(t.title||'Completed Test'),questionIds:t.questionIds.slice(),index:0,answers:Object.assign({},t.answers||{}),questionTimes:Object.assign({},t.questionTimes||{})};
    persist(st,s);render(s,t);return false;
  }
  function render(s,t){
    clean();var q=findQuestion(s.questionIds[s.index]),app=document.getElementById('app');
    if(!app||!q){console.error('Canonical CBT Review: question/app missing',s.questionIds[s.index]);return;}
    var selected=Number(s.answers[q.id]||0),correct=Number(q.correctOption||0),status=selected?(selected===correct?'Correct':'Incorrect'):'Unattempted';
    var opts=(Array.isArray(q.options)?q.options:[]).map(function(o){var n=o.letter?o.letter.charCodeAt(0)-64:0,c='option';if(n===selected)c+=' selected';if(n===correct)c+=' correct';if(n===selected&&n!==correct)c+=' wrong';return'<div class="'+c+'"><span class="radio"></span><span class="option-letter">'+esc(o.letter||'')+'</span><span class="option-text">'+esc(o.text||'')+'</span></div>';}).join('');
    app.innerHTML='<header class="topbar"><div class="brand">QBank</div><button class="ghost-btn" id="cr-back">Back to Tests</button></header><main class="page fade-in"><div class="page-head"><div><div class="mode-pill">Test Review</div><h1 class="page-title" style="margin-top:9px">'+esc(s.title)+'</h1><div class="page-sub">Question '+(s.index+1)+' of '+s.questionIds.length+'</div></div></div><section class="card question-card"><div class="q-number">Question '+esc(q.questionNumber||s.index+1)+' of '+s.questionIds.length+'</div><div class="crumb">'+esc(q.chapter||'')+'</div><div class="question-text">'+esc(q.question||'')+'</div><div class="option-list">'+opts+'</div><div class="feedback '+(status==='Correct'?'good':'bad')+'"><div class="feedback-title">'+status+'</div><div class="label">Correct answer</div><div style="font-weight:800">'+(correct?String.fromCharCode(64+correct)+'. '+esc((q.options&&q.options[correct-1]&&q.options[correct-1].text)||''):'')+'</div></div>'+source(q)+'<div class="q-footer"><button class="ghost-btn" id="cr-prev" '+(s.index<=0?'disabled':'')+'>Previous</button><button class="primary-btn" id="cr-next" '+(s.index>=s.questionIds.length-1?'disabled':'')+'>Next</button></div></section></main>';
    document.getElementById('cr-back').onclick=back;
    document.getElementById('cr-prev').onclick=function(){if(s.index>0){s.index--;persist(getState(),s);render(s,t);}};
    document.getElementById('cr-next').onclick=function(){if(s.index<s.questionIds.length-1){s.index++;persist(getState(),s);render(s,t);}};
  }
  window.__QB_OPEN_REVIEW=openReview;window.QB=window.QB||{};window.QB.reviewTest=openReview;
  if(typeof window.QB.submitExam==='function'&&!window.QB.submitExam.__canonicalReviewSubmit){var original=window.QB.submitExam;function submit(){clean();try{return original.apply(this,arguments);}finally{setTimeout(clean,0);setTimeout(clean,80);setTimeout(clean,250);}}submit.__canonicalReviewSubmit=true;window.QB.submitExam=submit;}
})();
</script>'''
s=s.replace('</body>',lock+'\n</body>',1)
HTML.write_text(s,encoding='utf-8')
print('Canonical CBT Review renderer installed; previous final CBT runtime layers removed.')
