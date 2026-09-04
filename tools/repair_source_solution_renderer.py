from pathlib import Path
import re

HTML=Path('app/src/main/assets/index.html')
JAVA=Path('app/src/main/java/com/qbank/biochemistry/MainActivity.java')
MAP='<script src="biochemistry_source_solution_map.js"></script>'
MARK='<!-- SOURCE_PDF_EXPLANATION_V16 -->'

s=HTML.read_text(encoding='utf-8')
if MAP not in s:
    s=s.replace('</head>',MAP+'\n</head>',1)
start=s.find('function renderExplanationText(text,question){')
if start<0: raise SystemExit('renderExplanationText not found')
brace=s.find('{',start); depth=0; end=-1
for i in range(brace,len(s)):
    if s[i]=='{': depth+=1
    elif s[i]=='}':
        depth-=1
        if depth==0: end=i+1; break
if end<0: raise SystemExit('renderExplanationText end not found')
replacement=r'''function renderExplanationText(text,question){
    const id=String(question?.id||'').toLowerCase();
    const subject=id.startsWith('anatomy-')?'anatomy':window.sourceSubjectV14(question);
    const label=subject==='physiology'?'Physiology':(subject==='anatomy'?'Anatomy':'Biochemistry');
    let segments=[];
    if(subject==='biochemistry' && window.BIOCHEM_SOURCE_SOLUTIONS){
      const hit=window.BIOCHEM_SOURCE_SOLUTIONS.find(x=>x.id===String(question?.id||''));
      segments=hit?.segments||[];
    }
    if(!segments.length){
      const ref=String(question?.sourceRef||'');
      const m=ref.match(/Solution\s+Pages?\s+(\d+)(?:\s*-\s*(\d+))?/i);
      if(m){const a=Number(m[1]),b=Number(m[2]||m[1]);for(let p=a;p<=b;p++)segments.push({page:p});}
    }
    if(!segments.length)return '';
    const url=(seg)=>`https://qbank.local/${subject}/pdf?page=${encodeURIComponent(seg.page)}&scale=3.5${seg.top!=null?`&top=${encodeURIComponent(seg.top)}`:''}${seg.bottom!=null?`&bottom=${encodeURIComponent(seg.bottom)}`:''}`;
    return `<div class="source-pdf-explanation"><div class="source-pdf-scroll"><div class="source-pdf-head">Original source solution · ${label}</div>${segments.map(seg=>`<div class="source-pdf-page" onclick="window.openSourceZoom(this.querySelector('img'))"><img loading="lazy" src="${url(seg)}" data-source-page="${seg.page}" alt="Original ${label} PDF solution page ${seg.page}"></div>`).join('')}<div class="source-pdf-note">Original PDF rendering only. No explanation text is parsed or reconstructed.</div></div></div>`;
  }'''
s=s[:start]+replacement+s[end:]
if MARK not in s: s=s.replace('</body>',MARK+'\n</body>',1)
HTML.write_text(s,encoding='utf-8')

j=JAVA.read_text(encoding='utf-8')
# The generated MainActivity is intentionally patched here, after the generic renderer generator.
j=j.replace('private PdfRenderer biochemistryRenderer, physiologyRenderer;', 'private PdfRenderer biochemistryRenderer, physiologyRenderer, anatomyRenderer;')
j=j.replace('private ParcelFileDescriptor biochemistryPfd, physiologyPfd;', 'private ParcelFileDescriptor biochemistryPfd, physiologyPfd, anatomyPfd;')
j=j.replace('File phys = copyAsset("Physiology_QBank_Source.pdf");', 'File phys = copyAsset("Physiology_QBank_Source.pdf");\n            File anatomy = copyAsset("Anatomy_QBank_Source.pdf");')
j=j.replace('physiologyRenderer = new PdfRenderer(physiologyPfd);', 'physiologyRenderer = new PdfRenderer(physiologyPfd);\n                    anatomyPfd = ParcelFileDescriptor.open(anatomy, ParcelFileDescriptor.MODE_READ_ONLY);\n                    anatomyRenderer = new PdfRenderer(anatomyPfd);')
j=j.replace('else if (url.startsWith("https://qbank.local/physiology/pdf")) renderer = physiologyRenderer;', 'else if (url.startsWith("https://qbank.local/physiology/pdf")) renderer = physiologyRenderer;\n        else if (url.startsWith("https://qbank.local/anatomy/pdf")) renderer = anatomyRenderer;')
old='''int page = Math.max(1, Integer.parseInt(q.getOrDefault("page", "1"))) - 1;\n            float scale = Math.max(1f, Math.min(4f, Float.parseFloat(q.getOrDefault("scale", "3"))));\n            synchronized (pdfLock) {\n                if (page < 0 || page >= renderer.getPageCount()) return null;\n                PdfRenderer.Page p = renderer.openPage(page);\n                int w = Math.max(1, Math.round(p.getWidth() * scale));\n                int h = Math.max(1, Math.round(p.getHeight() * scale));\n                Bitmap full = Bitmap.createBitmap(w, h, Bitmap.Config.ARGB_8888); full.eraseColor(Color.WHITE);\n                p.render(full, null, null, PdfRenderer.Page.RENDER_MODE_FOR_DISPLAY); p.close();'''
new='''int page = Math.max(1, Integer.parseInt(q.getOrDefault("page", "1"))) - 1;\n            float scale = Math.max(1f, Math.min(4f, Float.parseFloat(q.getOrDefault("scale", "3"))));\n            synchronized (pdfLock) {\n                if (page < 0 || page >= renderer.getPageCount()) return null;\n                PdfRenderer.Page p = renderer.openPage(page);\n                int w = Math.max(1, Math.round(p.getWidth() * scale));\n                int h = Math.max(1, Math.round(p.getHeight() * scale));\n                Bitmap full = Bitmap.createBitmap(w, h, Bitmap.Config.ARGB_8888); full.eraseColor(Color.WHITE);\n                p.render(full, null, null, PdfRenderer.Page.RENDER_MODE_FOR_DISPLAY); p.close();\n                float top=Float.parseFloat(q.getOrDefault("top", "0"));\n                float bottom=Float.parseFloat(q.getOrDefault("bottom", Float.toString(h/scale)));\n                int y1=Math.max(0,Math.min(h-1,Math.round(top*scale)));\n                int y2=Math.max(y1+1,Math.min(h,Math.round(bottom*scale)));\n                if(y1>0 || y2<h){ Bitmap crop=Bitmap.createBitmap(full,0,y1,w,y2-y1); full.recycle(); full=crop; }'''
if old not in j: raise SystemExit('Java render block not found')
j=j.replace(old,new)
j=j.replace('try{if(physiologyPfd!=null)physiologyPfd.close();}catch(Exception ignored){}', 'try{if(physiologyPfd!=null)physiologyPfd.close();}catch(Exception ignored){}try{if(anatomyRenderer!=null)anatomyRenderer.close();}catch(Exception ignored){}try{if(anatomyPfd!=null)anatomyPfd.close();}catch(Exception ignored){}')
JAVA.write_text(j,encoding='utf-8')
print('Installed V16 exact solution renderer with Anatomy routing, sourceRef ranges, crops, and multi-page support.')
