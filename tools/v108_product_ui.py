from pathlib import Path
import re
HTML=Path('app/src/main/assets/index.html')
JAVA=Path('app/src/main/java/com/qbank/biochemistry/MainActivity.java')
s=HTML.read_text(encoding='utf-8')
def replace_script(text,sid,body):
    return re.sub(r'<script id="'+re.escape(sid)+r'">.*?</script>', '<script id="'+sid+'">\n'+body+'\n</script>', text, count=1, flags=re.S)
def replace_fn(text,name,repl):
    start=text.find('function '+name+'(')
    if start<0:return text
    b=text.find('{',start)
    if b<0:return text
    depth=0; quote=None; esc=False
    for i in range(b,len(text)):
        c=text[i]
        if quote:
            if esc: esc=False
            elif c=='\\': esc=True
            elif c==quote: quote=None
        else:
            if c in "'\"`": quote=c
            elif c=='{': depth+=1
            elif c=='}':
                depth-=1
                if depth==0:return text[:start]+repl+text[i+1:]
    return text
m=re.search(r'<script id="v104-ui-runtime">(.*?)</script>',s,re.S)
if m:
    body=replace_fn(m.group(1),'enhance','function enhance(){}')
    s=s[:m.start()]+'<script id="v104-ui-runtime">'+body+'</script>'+s[m.end():]
s=replace_script(s,'v104-1-runtime',"(function(){'use strict';})();")
v105="""(function(){'use strict';\nfunction questionPolish(){var list=document.querySelector('.option-list');if(!list)return;if(!list.parentNode.querySelector('.v105-option-hint')){var h=document.createElement('p');h.className='v105-option-hint';h.textContent='Select the best answer';list.parentNode.insertBefore(h,list);}document.querySelectorAll('.option').forEach(function(o,i){if(o.querySelector('.v105-option-letter'))return;var l=document.createElement('span');l.className='v105-option-letter';l.textContent=String.fromCharCode(65+i);o.insertBefore(l,o.firstChild);});}\nnew MutationObserver(questionPolish).observe(document.documentElement,{childList:true,subtree:true});setTimeout(questionPolish,150);})();"""
s=replace_script(s,'v105-runtime',v105)
bridge="""<script id=\"v108-practice-hub\">\n(function(){'use strict';window.QB=window.QB||{};window.QB.startPractice=window.QB.startPractice||function(){if(typeof window.startAllPractice==='function')return window.startAllPractice();};window.QB.startWrong=window.QB.startWrong||function(){if(typeof window.startLibrary==='function')return window.startLibrary('wrong');};window.QB.startBookmarks=window.QB.startBookmarks||function(){if(typeof window.startLibrary==='function')return window.startLibrary('bookmarks');};window.QB.startTimed=window.QB.startTimed||function(){if(typeof window.openTestBuilder==='function')return window.openTestBuilder();};function hub(){var a=document.getElementById('app');if(!a)return;a.innerHTML='<main class=\"page v108-practice-hub\"><div class=\"page-head\"><div><div class=\"mode-pill\">STUDY</div><h1 class=\"page-title\" style=\"margin-top:8px\">Practice</h1><div class=\"page-sub\">Choose how you want to study right now.</div></div></div><section class=\"v108-practice-grid\"><button class=\"v108-practice-card primary\" onclick=\"window.QB.startPractice()\"><span class=\"v108-icon\">✓</span><span><b>Mixed Practice</b><small>20 questions · immediate feedback</small></span><strong>›</strong></button><button class=\"v108-practice-card\" onclick=\"window.QB.startWrong()\"><span class=\"v108-icon\">↻</span><span><b>Wrong Questions</b><small>Revisit questions you missed</small></span><strong>›</strong></button><button class=\"v108-practice-card\" onclick=\"window.QB.startBookmarks()\"><span class=\"v108-icon\">☆</span><span><b>Bookmarked</b><small>Study the questions you saved</small></span><strong>›</strong></button><button class=\"v108-practice-card\" onclick=\"window.QB.startTimed()\"><span class=\"v108-icon\">◷</span><span><b>Timed CBT</b><small>Open the existing test builder</small></span><strong>›</strong></button></section><button class=\"ghost-btn v108-back\" onclick=\"location.hash='#dashboard'\">Back to Home</button></main>';}function route(){if(location.hash==='#practice-hub')hub();}window.addEventListener('hashchange',route);setTimeout(route,50);})();\n</script>"""
if 'id="v108-practice-hub"' not in s:s=s.replace('</body>',bridge+'\n</body>',1)
css="""<style id=\"v108-clean-ui\">.v108-practice-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:20px}.v108-practice-card{min-height:104px;border:1px solid var(--line);border-radius:20px;background:#fff;padding:18px;display:flex;align-items:center;gap:14px;text-align:left;box-shadow:0 8px 24px rgba(33,35,70,.06);cursor:pointer;transition:transform .16s ease,box-shadow .16s ease}.v108-practice-card:hover{transform:translateY(-2px);box-shadow:0 12px 30px rgba(33,35,70,.10)}.v108-practice-card:active{transform:scale(.985)}.v108-practice-card.primary{background:linear-gradient(135deg,#f0efff,#fff);border-color:#d5d2ff}.v108-icon{width:42px;height:42px;border-radius:13px;display:grid;place-items:center;background:#eef0ff;color:#403bb5;font-size:22px;font-weight:900;flex:none}.v108-practice-card span:nth-child(2){flex:1}.v108-practice-card b{display:block;font-size:15px}.v108-practice-card small{display:block;color:var(--muted);margin-top:4px;font-size:11px;line-height:1.35}.v108-practice-card strong{font-size:24px;color:#9aa2b3}.v108-back{margin-top:18px}@media(max-width:640px){.v108-practice-grid{grid-template-columns:1fr}.v108-practice-card{min-height:82px}}body{padding-bottom:92px!important}</style>"""
if 'id="v108-clean-ui"' not in s:s=s.replace('</head>',css+'\n</head>',1)
cleanup="""<script id=\"v108-overlay-cleanup\">(function(){function clean(){['.v104-command','.v104-grid','.v104-backup','.v105-cockpit','.v105-subjects'].forEach(function(x){document.querySelectorAll(x).forEach(function(e){e.remove();});});}new MutationObserver(clean).observe(document.documentElement,{childList:true,subtree:true});setTimeout(clean,0);})();</script>"""
if 'id="v108-overlay-cleanup"' not in s:s=s.replace('</body>',cleanup+'\n</body>',1)
HTML.write_text(s,encoding='utf-8')
j=JAVA.read_text(encoding='utf-8')
j=j.replace('shell.addView(webView, new FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));','FrameLayout.LayoutParams webLp = new FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT);\n        webLp.bottomMargin = dp(92);\n        shell.addView(webView, webLp);')
j=j.replace('go("practice")','go("practice-hub")')
JAVA.write_text(j,encoding='utf-8')
print('V10.8 clean product UI installed')