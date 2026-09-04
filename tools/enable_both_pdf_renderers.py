from pathlib import Path
import re

JAVA = Path('app/src/main/java/com/qbank/biochemistry/MainActivity.java')
HTML = Path('app/src/main/assets/index.html')

java = r'''package com.qbank.biochemistry;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.graphics.Bitmap;
import android.graphics.Color;
import android.graphics.pdf.PdfRenderer;
import android.os.Build;
import android.os.Bundle;
import android.os.ParcelFileDescriptor;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.view.Window;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.net.URLDecoder;
import java.util.HashMap;
import java.util.Map;

public class MainActivity extends Activity {
    private WebView webView;
    private PdfRenderer biochemistryRenderer, physiologyRenderer;
    private ParcelFileDescriptor biochemistryPfd, physiologyPfd;
    private final Object pdfLock = new Object();

    @SuppressLint("SetJavaScriptEnabled")
    @Override protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Window window = getWindow();
        window.setStatusBarColor(Color.rgb(52, 46, 134));
        window.setNavigationBarColor(Color.rgb(244, 245, 248));
        preparePdfs();
        webView = new WebView(this);
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true); settings.setDomStorageEnabled(true); settings.setDatabaseEnabled(true);
        settings.setAllowFileAccess(true); settings.setAllowContentAccess(false);
        settings.setBuiltInZoomControls(false); settings.setDisplayZoomControls(false); settings.setSupportZoom(false);
        settings.setLoadsImagesAutomatically(true); settings.setMediaPlaybackRequiresUserGesture(true);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        webView.setBackgroundColor(Color.WHITE); webView.setWebChromeClient(new WebChromeClient());
        webView.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) { return true; }
            @Override public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                WebResourceResponse response = renderPdfRequest(request);
                return response != null ? response : super.shouldInterceptRequest(view, request);
            }
        });
        setContentView(webView); webView.loadUrl("file:///android_asset/index.html");
    }

    private void preparePdfs() {
        try {
            File bio = copyAsset("Biochemistry_QBank_Source.pdf");
            File phys = copyAsset("Physiology_QBank_Source.pdf");
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                synchronized (pdfLock) {
                    biochemistryPfd = ParcelFileDescriptor.open(bio, ParcelFileDescriptor.MODE_READ_ONLY);
                    biochemistryRenderer = new PdfRenderer(biochemistryPfd);
                    physiologyPfd = ParcelFileDescriptor.open(phys, ParcelFileDescriptor.MODE_READ_ONLY);
                    physiologyRenderer = new PdfRenderer(physiologyPfd);
                }
            }
        } catch (Exception ignored) {}
    }

    private File copyAsset(String name) throws Exception {
        File out = new File(getCacheDir(), name);
        if (!out.exists() || out.length() < 100000) {
            try (InputStream in = getAssets().open(name); FileOutputStream fos = new FileOutputStream(out)) {
                byte[] buf = new byte[8192]; int n; while ((n = in.read(buf)) >= 0) fos.write(buf, 0, n);
            }
        }
        return out;
    }

    private WebResourceResponse renderPdfRequest(WebResourceRequest request) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.LOLLIPOP) return null;
        String url = request.getUrl().toString();
        PdfRenderer renderer;
        if (url.startsWith("https://qbank.local/biochemistry/pdf")) renderer = biochemistryRenderer;
        else if (url.startsWith("https://qbank.local/physiology/pdf")) renderer = physiologyRenderer;
        else return null;
        if (renderer == null) return null;
        try {
            Map<String,String> q = query(request.getUrl().getQuery());
            int page = Math.max(1, Integer.parseInt(q.getOrDefault("page", "1"))) - 1;
            float scale = Math.max(1f, Math.min(4f, Float.parseFloat(q.getOrDefault("scale", "3"))));
            synchronized (pdfLock) {
                if (page < 0 || page >= renderer.getPageCount()) return null;
                PdfRenderer.Page p = renderer.openPage(page);
                int w = Math.max(1, Math.round(p.getWidth() * scale));
                int h = Math.max(1, Math.round(p.getHeight() * scale));
                Bitmap full = Bitmap.createBitmap(w, h, Bitmap.Config.ARGB_8888); full.eraseColor(Color.WHITE);
                p.render(full, null, null, PdfRenderer.Page.RENDER_MODE_FOR_DISPLAY); p.close();
                ByteArrayOutputStream out = new ByteArrayOutputStream(Math.max(65536, w*h/3));
                full.compress(Bitmap.CompressFormat.PNG, 100, out); full.recycle();
                return new WebResourceResponse("image/png", null, new ByteArrayInputStream(out.toByteArray()));
            }
        } catch (Exception ignored) { return null; }
    }
    private static Map<String,String> query(String raw) throws Exception {
        Map<String,String> m = new HashMap<>(); if (raw == null) return m;
        for (String part : raw.split("&")) { int k=part.indexOf('='); if(k<0) continue; m.put(URLDecoder.decode(part.substring(0,k),"UTF-8"), URLDecoder.decode(part.substring(k+1),"UTF-8")); }
        return m;
    }
    @Override public void onBackPressed(){if(webView!=null&&webView.canGoBack())webView.goBack();else super.onBackPressed();}
    @Override protected void onDestroy(){synchronized(pdfLock){try{if(biochemistryRenderer!=null)biochemistryRenderer.close();}catch(Exception ignored){}try{if(biochemistryPfd!=null)biochemistryPfd.close();}catch(Exception ignored){}try{if(physiologyRenderer!=null)physiologyRenderer.close();}catch(Exception ignored){}try{if(physiologyPfd!=null)physiologyPfd.close();}catch(Exception ignored){}}if(webView!=null){webView.loadUrl("about:blank");webView.stopLoading();webView.setWebChromeClient(null);webView.setWebViewClient(null);webView.destroy();webView=null;}super.onDestroy();}
}
'''

JAVA.write_text(java, encoding='utf-8')

s = HTML.read_text(encoding='utf-8')
marker = '<!-- SOURCE_PDF_EXPLANATION_V12 -->'
if marker not in s:
    css = r'''<style id="source-pdf-explanation-css-v12">
.source-pdf-explanation{margin-top:14px;border:1px solid var(--line);border-radius:16px;background:#fff;overflow:hidden}.source-pdf-scroll{max-height:min(58vh,560px);overflow:auto;-webkit-overflow-scrolling:touch;padding:12px}.source-pdf-head{font-size:11px;font-weight:850;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);padding:2px 2px 9px}.source-pdf-page{margin:0 0 12px;border:1px solid var(--line);border-radius:10px;overflow:hidden;background:#fff;cursor:zoom-in}.source-pdf-page:last-child{margin-bottom:0}.source-pdf-page img{display:block;width:100%;height:auto}.source-pdf-note{font-size:11px;line-height:1.45;color:var(--muted);padding:9px 2px 2px}.source-pdf-zoom{position:fixed;inset:0;z-index:10000;background:rgba(8,9,17,.96);display:flex;flex-direction:column}.source-pdf-zoombar{height:56px;display:flex;align-items:center;justify-content:space-between;padding:7px 10px;color:#fff}.source-pdf-zoomtitle{font-size:12px;font-weight:800;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.source-pdf-zoombar button{width:38px;height:38px;margin-left:5px;border:1px solid rgba(255,255,255,.25);border-radius:10px;background:rgba(255,255,255,.1);color:#fff;font-size:19px}.source-pdf-zoomstage{position:relative;flex:1;overflow:hidden;touch-action:none;display:flex;align-items:center;justify-content:center}.source-pdf-zoomimg{max-width:none;max-height:none;width:auto;height:auto;transform-origin:0 0;user-select:none;-webkit-user-drag:none}
</style>'''
    js = r'''<script id="source-pdf-explanation-js-v12">
(function(){
  const escSource=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  function sourceSubject(q){
    const raw=String(q?.subject||' '+q?.sourceRef||'').toLowerCase();
    return raw.includes('physiology')||raw.includes('physiology qbank')?'physiology':'biochemistry';
  }
  function sourcePages(q){
    const a=Number(q?.sourcePage||0), b=Number(q?.sourcePageEnd||a);
    if(!a)return[]; const out=[]; for(let p=a;p<=Math.max(a,b);p++)out.push(p); return out;
  }
  function sourcePdfUrl(q,p){return `https://qbank.local/${sourceSubject(q)}/pdf?page=${encodeURIComponent(p)}&scale=3.5`;}
  function openSourceZoom(img){
    document.getElementById('source-pdf-zoom')?.remove();
    const b=document.createElement('div');b.id='source-pdf-zoom';b.className='source-pdf-zoom';
    b.innerHTML=`<div class="source-pdf-zoombar"><div class="source-pdf-zoomtitle">Original source · PDF page ${escSource(img.dataset.sourcePage||'')}</div><div><button id="spz-minus">−</button><button id="spz-reset">1×</button><button id="spz-plus">+</button><button id="spz-close">×</button></div></div><div class="source-pdf-zoomstage"><img class="source-pdf-zoomimg" src="${img.src}" alt="${escSource(img.alt||'Original source')}"></div>`;
    document.body.appendChild(b); const st=b.querySelector('.source-pdf-zoomstage'), i=b.querySelector('.source-pdf-zoomimg');
    let scale=1,x=0,y=0,bx=0,by=0,sx=0,sy=0,pointers=new Map(),startDist=0,startScale=1;
    const apply=()=>i.style.transform=`translate(${x}px,${y}px) scale(${scale})`;
    const reset=()=>{if(!i.naturalWidth)return;scale=Math.min(1,Math.min(st.clientWidth/i.naturalWidth,st.clientHeight/i.naturalHeight));x=(st.clientWidth-i.naturalWidth*scale)/2;y=(st.clientHeight-i.naturalHeight*scale)/2;apply();};
    i.addEventListener('load',reset); b.querySelector('#spz-close').onclick=()=>b.remove(); b.querySelector('#spz-reset').onclick=reset;
    b.querySelector('#spz-plus').onclick=()=>{scale=Math.min(6,scale*1.35);apply();}; b.querySelector('#spz-minus').onclick=()=>{scale=Math.max(.5,scale/1.35);apply();};
    st.addEventListener('pointerdown',e=>{pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});if(pointers.size===1){sx=e.clientX;sy=e.clientY;bx=x;by=y;}else{const a=[...pointers.values()];startDist=Math.hypot(a[0].x-a[1].x,a[0].y-a[1].y);startScale=scale;}});
    st.addEventListener('pointermove',e=>{if(!pointers.has(e.pointerId))return;pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});const a=[...pointers.values()];if(a.length===1){x=bx+e.clientX-sx;y=by+e.clientY-sy;apply();}else if(a.length===2&&startDist){scale=Math.max(.5,Math.min(6,startScale*Math.hypot(a[0].x-a[1].x,a[0].y-a[1].y)/startDist));apply();}});
    ['pointerup','pointercancel','pointerleave'].forEach(ev=>st.addEventListener(ev,e=>pointers.delete(e.pointerId)));
    b.addEventListener('click',e=>{if(e.target===b)b.remove();});
  }
  window.openSourceZoom=openSourceZoom;

  // IMPORTANT: replace the lexical function actually called by the question renderer.
  // Assigning window.renderExplanationText alone does not replace a local function declaration.
  const originalExplanationFunctionMarker='SOURCE_PDF_EXPLANATION_OVERRIDE_V12';
  const sourceExplanationRenderer=function(text,question){
    const pages=sourcePages(question);
    if(!pages.length)return '';
    const subject=sourceSubject(question), label=subject==='physiology'?'Physiology':'Biochemistry';
    return `<div class="source-pdf-explanation"><div class="source-pdf-scroll"><div class="source-pdf-head">Original source explanation · ${label}</div>${pages.map(p=>`<div class="source-pdf-page" onclick="window.openSourceZoom(this.querySelector('img'))"><img loading="lazy" src="${sourcePdfUrl(question,p)}" data-source-page="${p}" alt="Original ${label} PDF page ${p}"></div>`).join('')}<div class="source-pdf-note">Rendered directly from the bundled original source PDF. The explanation text is not parsed, reconstructed, rewritten, or reformatted.</div></div></div>`;
  };

  // Find the existing function declaration in the page source at build time; this runtime marker is
  // consumed by the build patch below only as a safety flag. The actual replacement is performed below.
  window.__sourcePdfExplanationRendererV12=sourceExplanationRenderer;
})();
</script>'''
    # Replace the existing lexical renderer body. The hardening step has already installed it.
    start=s.find('function renderExplanationText(text,question){')
    if start<0: raise SystemExit('Could not find lexical renderExplanationText function after hardening.')
    brace=s.find('{',start); depth=0; end=-1
    for i in range(brace,len(s)):
        if s[i]=='{': depth+=1
        elif s[i]=='}':
            depth-=1
            if depth==0: end=i+1; break
    if end<0: raise SystemExit('Could not find end of renderExplanationText function.')
    replacement='''function renderExplanationText(text,question){\n    const pages=sourcePages(question);\n    if(!pages.length)return '';\n    const subject=sourceSubject(question), label=subject==='physiology'?'Physiology':'Biochemistry';\n    return `<div class="source-pdf-explanation"><div class="source-pdf-scroll"><div class="source-pdf-head">Original source explanation · ${label}</div>${pages.map(p=>`<div class="source-pdf-page" onclick="window.openSourceZoom(this.querySelector('img'))"><img loading="lazy" src="${sourcePdfUrl(question,p)}" data-source-page="${p}" alt="Original ${label} PDF page ${p}"></div>`).join('')}<div class="source-pdf-note">Rendered directly from the bundled original source PDF. The explanation text is not parsed, reconstructed, rewritten, or reformatted.</div></div></div>`;\n  }'''
    s=s[:start]+replacement+s[end:]
    s=s.replace('</head>',css+'\n</head>',1)
    s=s.replace('</body>',js+'\n'+marker+'\n</body>',1)
    HTML.write_text(s,encoding='utf-8')
    print('Installed V12 source-PDF explanation renderer by replacing the actual lexical renderExplanationText function.')
else:
    print('V12 source-PDF renderer already installed.')
