package com.qbank.biochemistry;

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

import org.json.JSONObject;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

public class MainActivity extends Activity {
    private WebView webView;
    private PdfRenderer physiologyRenderer;
    private ParcelFileDescriptor physiologyPfd;
    private final Object pdfLock = new Object();

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Window window = getWindow();
        window.setStatusBarColor(Color.rgb(52, 46, 134));
        window.setNavigationBarColor(Color.rgb(244, 245, 248));
        preparePhysiologyPdf();

        webView = new WebView(this);
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(false);
        settings.setBuiltInZoomControls(false);
        settings.setDisplayZoomControls(false);
        settings.setSupportZoom(false);
        settings.setLoadsImagesAutomatically(true);
        settings.setMediaPlaybackRequiresUserGesture(true);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);

        webView.setBackgroundColor(Color.WHITE);
        webView.setWebChromeClient(new WebChromeClient());
        webView.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) { return true; }
            @Override public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                injectHomePolish();
            }
            @Override public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                WebResourceResponse response = renderPhysiologyPdfRequest(request);
                return response != null ? response : super.shouldInterceptRequest(view, request);
            }
        });
        setContentView(webView);
        webView.loadUrl("file:///android_asset/index.html");
    }

    private void injectHomePolish() {
        if (webView == null) return;
        try (InputStream in = getAssets().open("home_polish_v2.js"); ByteArrayOutputStream out = new ByteArrayOutputStream()) {
            byte[] buf = new byte[8192]; int n;
            while ((n = in.read(buf)) >= 0) out.write(buf, 0, n);
            String script = new String(out.toByteArray(), StandardCharsets.UTF_8);
            webView.evaluateJavascript("eval(" + JSONObject.quote(script) + ")", null);
        } catch (Exception ignored) { }
    }

    private void preparePhysiologyPdf() {
        try {
            File out = new File(getCacheDir(), "Physiology_QBank_Source.pdf");
            if (!out.exists() || out.length() < 100000) {
                try (InputStream in = getAssets().open("Physiology_QBank_Source.pdf"); FileOutputStream fos = new FileOutputStream(out)) {
                    byte[] buf = new byte[8192]; int n;
                    while ((n = in.read(buf)) >= 0) fos.write(buf, 0, n);
                }
            }
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
                synchronized (pdfLock) {
                    physiologyPfd = ParcelFileDescriptor.open(out, ParcelFileDescriptor.MODE_READ_ONLY);
                    physiologyRenderer = new PdfRenderer(physiologyPfd);
                }
            }
        } catch (Exception ignored) { physiologyRenderer = null; }
    }

    private WebResourceResponse renderPhysiologyPdfRequest(WebResourceRequest request) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.LOLLIPOP || physiologyRenderer == null) return null;
        if (!request.getUrl().toString().startsWith("https://qbank.local/physiology/pdf")) return null;
        try {
            Map<String,String> q = query(request.getUrl().getQuery());
            int page = Math.max(1, Integer.parseInt(q.getOrDefault("page", "1"))) - 1;
            float scale = Math.max(1f, Math.min(3f, Float.parseFloat(q.getOrDefault("scale", "2.5"))));
            float top=parseFloat(q.get("top"),0), bottom=parseFloat(q.get("bottom"),-1), left=parseFloat(q.get("left"),0), right=parseFloat(q.get("right"),-1);
            byte[] jpeg;
            synchronized (pdfLock) {
                if (page < 0 || page >= physiologyRenderer.getPageCount()) return null;
                PdfRenderer.Page p=physiologyRenderer.openPage(page);
                int w=Math.max(1,Math.round(p.getWidth()*scale)), h=Math.max(1,Math.round(p.getHeight()*scale));
                Bitmap full=Bitmap.createBitmap(w,h,Bitmap.Config.ARGB_8888); full.eraseColor(Color.WHITE);
                p.render(full,null,null,PdfRenderer.Page.RENDER_MODE_FOR_DISPLAY); p.close();
                int x0=Math.max(0,Math.round(left*scale)), y0=Math.max(0,Math.round(top*scale));
                int x1=right>left?Math.min(w,Math.round(right*scale)):w, y1=bottom>top?Math.min(h,Math.round(bottom*scale)):h;
                if(x1<=x0||y1<=y0){x0=0;y0=0;x1=w;y1=h;}
                Bitmap crop=(x0==0&&y0==0&&x1==w&&y1==h)?full:Bitmap.createBitmap(full,x0,y0,x1-x0,y1-y0);
                ByteArrayOutputStream out=new ByteArrayOutputStream(Math.max(32768,crop.getWidth()*crop.getHeight()/4)); crop.compress(Bitmap.CompressFormat.JPEG,92,out); jpeg=out.toByteArray();
                if(crop!=full)crop.recycle(); full.recycle();
            }
            return new WebResourceResponse("image/jpeg","UTF-8",new ByteArrayInputStream(jpeg));
        } catch(Exception ignored){ return null; }
    }
    private static float parseFloat(String s,float d){try{return s==null?d:Float.parseFloat(s);}catch(Exception e){return d;}}
    private static Map<String,String> query(String raw)throws Exception{Map<String,String>m=new HashMap<>();if(raw==null)return m;for(String part:raw.split("&")){int k=part.indexOf('=');if(k<0)continue;m.put(URLDecoder.decode(part.substring(0,k),"UTF-8"),URLDecoder.decode(part.substring(k+1),"UTF-8"));}return m;}

    @Override public void onBackPressed(){if(webView!=null&&webView.canGoBack())webView.goBack();else super.onBackPressed();}
    @Override protected void onDestroy(){synchronized(pdfLock){try{if(physiologyRenderer!=null)physiologyRenderer.close();}catch(Exception ignored){}try{if(physiologyPfd!=null)physiologyPfd.close();}catch(Exception ignored){}physiologyRenderer=null;physiologyPfd=null;}if(webView!=null){webView.loadUrl("about:blank");webView.stopLoading();webView.setWebChromeClient(null);webView.setWebViewClient(null);webView.destroy();webView=null;}super.onDestroy();}
}
