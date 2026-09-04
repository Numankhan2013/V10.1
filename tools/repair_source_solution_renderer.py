from pathlib import Path

HTML=Path('app/src/main/assets/index.html')
JAVA=Path('app/src/main/java/com/qbank/biochemistry/MainActivity.java')
MAP='<script src="biochemistry_source_solution_map.js"></script>'
MARK='<!-- SOURCE_PDF_EXPLANATION_V18 -->'

s=HTML.read_text(encoding='utf-8')
if MAP not in s: s=s.replace('</head>',MAP+'\n</head>',1)
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

java=r'''package com.qbank.biochemistry;

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
    private PdfRenderer biochemistryRenderer, physiologyRenderer, anatomyRenderer;
    private ParcelFileDescriptor biochemistryPfd, physiologyPfd, anatomyPfd;
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
        File bio = null, phys = null, anatomy = null;
        try { bio = copyAsset("Biochemistry_QBank_Source.pdf"); } catch (Exception ignored) {}
        try { phys = copyAsset("Physiology_QBank_Source.pdf"); } catch (Exception ignored) {}
        try { anatomy = copyAsset("Anatomy_QBank_Source.pdf"); } catch (Exception ignored) {}
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.LOLLIPOP) return;
        synchronized (pdfLock) {
            try { if (bio != null) { biochemistryPfd = ParcelFileDescriptor.open(bio, ParcelFileDescriptor.MODE_READ_ONLY); biochemistryRenderer = new PdfRenderer(biochemistryPfd); } } catch (Exception ignored) {}
            try { if (phys != null) { physiologyPfd = ParcelFileDescriptor.open(phys, ParcelFileDescriptor.MODE_READ_ONLY); physiologyRenderer = new PdfRenderer(physiologyPfd); } } catch (Exception ignored) {}
            try { if (anatomy != null) { anatomyPfd = ParcelFileDescriptor.open(anatomy, ParcelFileDescriptor.MODE_READ_ONLY); anatomyRenderer = new PdfRenderer(anatomyPfd); } } catch (Exception ignored) {}
        }
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
        else if (url.startsWith("https://qbank.local/anatomy/pdf")) renderer = anatomyRenderer;
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
                float top=Float.parseFloat(q.getOrDefault("top", "0"));
                float bottom=Float.parseFloat(q.getOrDefault("bottom", Float.toString(h/scale)));
                int y1=Math.max(0,Math.min(h-1,Math.round(top*scale)));
                int y2=Math.max(y1+1,Math.min(h,Math.round(bottom*scale)));
                if(y1>0 || y2<h){ Bitmap crop=Bitmap.createBitmap(full,0,y1,w,y2-y1); full.recycle(); full=crop; }
                ByteArrayOutputStream out = new ByteArrayOutputStream(Math.max(65536, w*Math.max(1,y2-y1)/3));
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
    @Override protected void onDestroy(){synchronized(pdfLock){try{if(biochemistryRenderer!=null)biochemistryRenderer.close();}catch(Exception ignored){}try{if(biochemistryPfd!=null)biochemistryPfd.close();}catch(Exception ignored){}try{if(physiologyRenderer!=null)physiologyRenderer.close();}catch(Exception ignored){}try{if(physiologyPfd!=null)physiologyPfd.close();}catch(Exception ignored){}try{if(anatomyRenderer!=null)anatomyRenderer.close();}catch(Exception ignored){}try{if(anatomyPfd!=null)anatomyPfd.close();}catch(Exception ignored){}}if(webView!=null){webView.loadUrl("about:blank");webView.stopLoading();webView.setWebChromeClient(null);webView.setWebViewClient(null);webView.destroy();webView=null;}super.onDestroy();}
}
'''
JAVA.write_text(java,encoding='utf-8')
print('Installed V18 source solution renderer with robust three-PDF initialization, Anatomy routing, exact Biochemistry solution mapping, sourceRef multi-page support, and PDF-region cropping.')
