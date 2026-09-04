from pathlib import Path

HTML = Path('app/src/main/assets/index.html')
s = HTML.read_text(encoding='utf-8')

lock = r'''<script id="cbt-final-lock-v3">
(function(){
  'use strict';

  function esc(v){return String(v==null?'':v).replace(/[&<>\"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#39;'}[c];});}
  function cleanExamUi(){
    document.querySelectorAll('.navigator .primary-btn,.qb-nav-submit').forEach(function(b){
      if(/submit\s*test/i.test(String(b.textContent||''))){b.disabled=true;b.remove();}
    });
    var nav=document.getElementById('qb-question-navigator');if(nav)nav.remove();
    document.querySelectorAll('#toast-root .toast').forEach(function(e){e.remove();});
  }

  function allQuestions(){
    var out=[];
    var base=window.QBANK_DATA||{};
    if(Array.isArray(base.questions))out=out.concat(base.questions.map(function(q){return Object.assign({},q,{subject:q.subject||'Biochemistry'});}));
    var subjects=window.SUBJECT_QBANK_DATA&&Array.isArray(window.SUBJECT_QBANK_DATA.subjects)?window.SUBJECT_QBANK_DATA.subjects:[];
    subjects.forEach(function(sub){if(Array.isArray(sub.questions))out=out.concat(sub.questions.map(function(q){return Object.assign({},q,{subject:q.subject||sub.subject});}));});
    return out;
  }

  function findQuestion(id){
    var wanted=String(id);
    var base=window.QBANK_DATA||{};
    var q=Array.isArray(base.questions)?base.questions.find(function(x){return String(x.id)===wanted;}):null;
    if(q)return Object.assign({},q,{subject:q.subject||'Biochemistry'});
    var subjects=window.SUBJECT_QBANK_DATA&&Array.isArray(window.SUBJECT_QBANK_DATA.subjects)?window.SUBJECT_QBANK_DATA.subjects:[];
    for(var i=0;i<subjects.length;i++){
      var arr=subjects[i]&&Array.isArray(subjects[i].questions)?subjects[i].questions:[];
      q=arr.find(function(x){return String(x.id)===wanted;});
      if(q)return Object.assign({},q,{subject:q.subject||subjects[i].subject});
    }
    return null;
  }

  function subjectFor(q){
    var id=String(q&&q.id||'').toLowerCase();
    if(id.indexOf('anatomy-')===0)return 'anatomy';
    if(id.indexOf('physiology-')===0)return 'physiology';
    var s=String(q&&q.subject||'').toLowerCase();
    if(s==='anatomy'||s==='physiology')return s;
    return 'biochemistry';
  }

  function segmentsFor(q){
    var subject=subjectFor(q),id=String(q&&q.id||''),segments=[];
    if(subject==='biochemistry'&&Array.isArray(window.BIOCHEM_SOURCE_SOLUTIONS)){
      var hit=window.BIOCHEM_SOURCE_SOLUTIONS.find(function(x){return String(x.id)===id;});
      segments=hit&&Array.isArray(hit.segments)?hit.segments:[];
    }else if(window.SUBJECT_SOURCE_SOLUTIONS&&Array.isArray(window.SUBJECT_SOURCE_SOLUTIONS[subject])){
      var hit2=window.SUBJECT_SOURCE_SOLUTIONS[subject].find(function(x){return String(x.id)===id;});
      segments=hit2&&Array.isArray(hit2.segments)?hit2.segments:[];
    }
    if(!segments.length){
      var ref=String(q&&q.sourceRef||'');
      var m=ref.match(/Solution\s+Pages?\s+(\d+)(?:\s*-\s*(\d+))?/i);
      if(m){var a=Number(m[1]),b=Number(m[2]||m[1]);for(var p=a;p<=b;p++)segments.push({page:p});}
    }
    return segments;
  }

  function sourceHtml(q){
    var subject=subjectFor(q),label=subject==='physiology'?'Physiology':subject==='anatomy'?'Anatomy':'Biochemistry';
    var segs=segmentsFor(q);
    if(!segs.length)return '<div class="source-pdf-note">Original source solution is not mapped for this question.</div>';
    return '<div class="source-pdf-explanation"><div class="source-pdf-head">Original source solution · '+label+'</div>'+segs.map(function(seg){
      var url='https://qbank.local/'+subject+'/pdf?page='+encodeURIComponent(seg.page)+'&scale=3.5'+(seg.top!=null?'&top='+encodeURIComponent(seg.top):'')+(seg.bottom!=null?'&bottom='+encodeURIComponent(seg.bottom):'');
      return '<div class="source-pdf-page" onclick="window.openSourceZoom(this.querySelector(\'img\'))"><img loading="lazy" src="'+url+'" data-source-page="'+esc(seg.page)+'" alt="Original '+label+' PDF solution page '+esc(seg.page)+'"></div>';
    }).join('')+'<div class="source-pdf-note">Original PDF rendering only. No explanation text is parsed or reconstructed.</div></div>';
  }

  function openReview(testId){
    try{
      var qb=window.QB;
      var st=qb&&typeof qb.getState==='function'?qb.getState():null;
      if(!st||!Array.isArray(st.tests)){
        var raw=localStorage.getItem('qbank_state_v1');st=raw?JSON.parse(raw):null;
      }
      var wanted=decodeURIComponent(String(testId||''));
      var tests=st&&Array.isArray(st.tests)?st.tests:[];
      var t=tests.find(function(x){return String(x.id)===wanted||String(x.id)===String(testId);});
      if(!t||!Array.isArray(t.questionIds)||!t.questionIds.length){console.error('CBT Review v3: test not found',wanted);return false;}

      var answers=Object.assign({},t.answers||{});
      var submitted={};t.questionIds.forEach(function(id){submitted[id]=Object.prototype.hasOwnProperty.call(answers,id);});
      var session={id:'review_'+String(t.id),mode:'review',sourceTestId:String(t.id),title:'Review · '+String(t.title||'Completed Test'),questionIds:t.questionIds.slice(),index:0,answers:answers,submitted:submitted,startedAt:t.createdAt||Date.now(),questionEnteredAt:Date.now(),questionTimes:Object.assign({},t.questionTimes||{})};
      st.activeSession=session;
      localStorage.setItem('qbank_state_v1',JSON.stringify(st));
      renderReview(session,t);
      return false;
    }catch(e){console.error('CBT Review v3 failed',e);return false;}
  }

  function renderReview(session,test){
    cleanExamUi();
    var q=findQuestion(session.questionIds[session.index]);
    if(!q){console.error('CBT Review v3: question not found',session.questionIds[session.index]);return;}
    var selected=Number(session.answers[q.id]||0)||0;
    var correct=Number(q.correctOption||0);
    var status=selected?(selected===correct?'Correct':'Incorrect'):'Unattempted';
    var statusClass=selected?(selected===correct?'good':'bad'):'bad';
    var options=(Array.isArray(q.options)?q.options:[]).map(function(o){
      var n=o.letter?o.letter.charCodeAt(0)-64:0,cls='option';
      if(n===selected)cls+=' selected';
      if(n===correct)cls+=' correct';
      if(n===selected&&n!==correct)cls+=' wrong';
      return '<div class="'+cls+'"><span class="radio"></span><span class="option-letter">'+esc(o.letter||'')+'</span><span class="option-text">'+esc(o.text||'')+'</span></div>';
    }).join('');
    var pct=Math.round((session.index+1)/session.questionIds.length*100);
    var source=sourceHtml(q);
    var app=document.getElementById('app');
    if(!app)return;
    app.innerHTML='<header class="topbar"><div class="brand">QBank</div><button class="ghost-btn" id="cbt-review-back">Back to Tests</button></header>'+
      '<main class="page fade-in"><div class="page-head"><div><div class="mode-pill">Test Review</div><h1 class="page-title" style="margin-top:9px">'+esc(session.title)+'</h1><div class="page-sub">Question '+(session.index+1)+' of '+session.questionIds.length+'</div></div><div class="small-muted">'+pct+'% through</div></div>'+
      '<section class="card question-card"><div class="q-head"><div class="q-number">Question '+esc(q.questionNumber||session.index+1)+' of '+session.questionIds.length+'</div></div><div class="crumb">'+esc(q.chapter||'')+'</div><div class="question-text">'+esc(q.question||'')+'</div><div class="option-list">'+options+'</div><div class="feedback '+statusClass+'"><div class="feedback-title">'+status+'</div><div class="label">Correct answer</div><div style="font-weight:800">'+(correct?String.fromCharCode(64+correct)+'. '+esc((q.options&&q.options[correct-1]&&q.options[correct-1].text)||''):'')+'</div></div>'+source+'<div class="q-footer"><button class="ghost-btn" id="cbt-review-prev" '+(session.index<=0?'disabled':'')+'>Previous</button><button class="primary-btn" id="cbt-review-next" '+(session.index>=session.questionIds.length-1?'disabled':'')+'>Next</button></div></section></main>';
    document.getElementById('cbt-review-back').onclick=function(){if(qbNavTests())return false;};
    document.getElementById('cbt-review-prev').onclick=function(){if(session.index>0){session.index--;session.questionEnteredAt=Date.now();localStorage.setItem('qbank_state_v1',JSON.stringify(Object.assign(stFromLive(),{activeSession:session})));renderReview(session,test);}};
    document.getElementById('cbt-review-next').onclick=function(){if(session.index<session.questionIds.length-1){session.index++;session.questionEnteredAt=Date.now();localStorage.setItem('qbank_state_v1',JSON.stringify(Object.assign(stFromLive(),{activeSession:session})));renderReview(session,test);}};
  }

  function stFromLive(){var qb=window.QB;if(qb&&typeof qb.getState==='function')return qb.getState();try{return JSON.parse(localStorage.getItem('qbank_state_v1')||'{}');}catch(e){return {};}}
  function qbNavTests(){try{if(window.QB&&typeof window.QB.nav==='function'){window.QB.nav('tests');return true;}}catch(e){}location.hash='#tests';return true;}

  window.__QB_OPEN_REVIEW=openReview;
  if(window.QB)window.QB.reviewTest=openReview;

  // Keep the successful submit cleanup from v2, but never depend on it for Review.
  if(window.QB&&typeof window.QB.submitExam==='function'&&!window.QB.submitExam.__cbtFinalLockV3){
    var original=window.QB.submitExam;
    function submitExamFinal(){cleanExamUi();try{return original.apply(this,arguments);}finally{setTimeout(cleanExamUi,0);setTimeout(cleanExamUi,80);setTimeout(cleanExamUi,250);}}
    submitExamFinal.__cbtFinalLockV3=true;window.QB.submitExam=submitExamFinal;
  }
})();
</script>'''

# Remove any previous v3 injection if this script is ever run twice.
start=s.find('<script id="cbt-final-lock-v3">')
if start>=0:
    end=s.find('</script>',start)
    if end>=0:s=s[:start]+s[end+9:]

s=s.replace('</body>',lock+'\n</body>',1)
HTML.write_text(s,encoding='utf-8')
print('CBT final lock v3 installed: standalone Review Solutions renderer independent of hash/render pipeline.')
