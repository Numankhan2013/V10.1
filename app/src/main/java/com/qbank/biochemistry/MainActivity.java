package com.qbank.biochemistry;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.SharedPreferences;
import android.graphics.Bitmap;
import android.graphics.Color;
import android.graphics.pdf.PdfRenderer;
import android.os.Build;
import android.os.Bundle;
import android.os.ParcelFileDescriptor;
import android.webkit.JavascriptInterface;
import android.content.ClipData;
import android.content.Intent;
import android.net.Uri;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.view.HapticFeedbackConstants;
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
    private PdfRenderer biochemistryRenderer, physiologyRenderer, anatomyRenderer;
    private ParcelFileDescriptor biochemistryPfd, physiologyPfd, anatomyPfd;
    private final Object pdfLock = new Object();
    private static final String APP_ORIGIN="https://qbank.local/app/";
    private SharedPreferences migrationPrefs;

    @SuppressLint("SetJavaScriptEnabled")
    @Override protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Window window = getWindow();
        window.setStatusBarColor(Color.rgb(52, 46, 134));
        window.setNavigationBarColor(Color.rgb(244, 245, 248));
        preparePdfs();
        migrationPrefs=getSharedPreferences("qbank_origin_migration_v1",Context.MODE_PRIVATE);
        webView = new WebView(this);
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true); settings.setDomStorageEnabled(true); settings.setDatabaseEnabled(true);
        // NK_WEBVIEW_MIGRATION_BOUNDARY_V1: file access is temporary.
        settings.setAllowFileAccess(!migrationPrefs.getBoolean("complete", false));
        settings.setAllowFileAccessFromFileURLs(false);
        settings.setAllowUniversalAccessFromFileURLs(false); settings.setAllowContentAccess(false);
        settings.setBuiltInZoomControls(false); settings.setDisplayZoomControls(false); settings.setSupportZoom(false);
        settings.setLoadsImagesAutomatically(true); settings.setMediaPlaybackRequiresUserGesture(true);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        webView.setBackgroundColor(Color.WHITE); webView.setHapticFeedbackEnabled(true); webView.setWebChromeClient(new NoteFileChooserClient());
        if (!migrationPrefs.getBoolean("complete", false)) webView.addJavascriptInterface(new MigrationBridge(), "QBankMigration");
        webView.addJavascriptInterface(new HapticsBridge(), "QBankHaptics");
        webView.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) { return !request.getUrl().toString().startsWith(APP_ORIGIN); }
            @Override public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                WebResourceResponse response = renderPdfRequest(request);
                if(response==null)response=serveAppAsset(request);
                return response != null ? response : super.shouldInterceptRequest(view, request);
            }
        });
        setContentView(webView);if(migrationPrefs.getBoolean("complete",false))webView.loadUrl(APP_ORIGIN+"index.html");else webView.loadUrl("file:///android_asset/migrate_local_state.html");
    }


    // NATIVE_ACTION_HAPTICS_V1: framework effects honor the user's touch setting.
    private final class HapticsBridge {
        @JavascriptInterface public void play(String kind) {
            if (kind == null) return;
            final int effect;
            switch (kind) {
                case "choice": effect = HapticFeedbackConstants.CLOCK_TICK; break;
                case "mark": effect = HapticFeedbackConstants.CONTEXT_CLICK; break;
                case "primary": effect = HapticFeedbackConstants.KEYBOARD_TAP; break;
                case "complete":
                case "success": effect = Build.VERSION.SDK_INT >= 30 ? HapticFeedbackConstants.CONFIRM : HapticFeedbackConstants.VIRTUAL_KEY; break;
                case "error": effect = Build.VERSION.SDK_INT >= 30 ? HapticFeedbackConstants.REJECT : HapticFeedbackConstants.LONG_PRESS; break;
                default: return;
            }
            runOnUiThread(() -> { if (webView != null) webView.performHapticFeedback(effect); });
        }
    }

    private final class MigrationBridge {
        @JavascriptInterface public void capture(String state, String subject, String sync, String auth, String backup) {
            migrationPrefs.edit().putString("state", state).putString("subject", subject).putString("sync", sync).putString("auth", auth).putString("backup", backup).apply();
            runOnUiThread(() -> webView.loadUrl(APP_ORIGIN + "index.html"));
        }
        @JavascriptInterface public void complete() {
            migrationPrefs.edit().putBoolean("complete", true).remove("state").remove("subject").remove("sync").remove("auth").remove("backup").apply();
            runOnUiThread(() -> { if (webView != null) { webView.getSettings().setAllowFileAccess(false); webView.removeJavascriptInterface("QBankMigration"); } });
        }
    }

    private WebResourceResponse serveAppAsset(WebResourceRequest request) {
        String url = request.getUrl().toString(); if (!url.startsWith(APP_ORIGIN)) return null;
        try {
            String path = URLDecoder.decode(request.getUrl().getPath().substring("/app/".length()), "UTF-8");
            if (path.isEmpty()) path = "index.html"; if(path.startsWith("assets/"))path=path.substring(7); if (path.contains("..") || path.startsWith("/")) return appAssetNotFound();
            byte[] bytes;
            try (InputStream in = getAssets().open(path); ByteArrayOutputStream out = new ByteArrayOutputStream()) { byte[] buffer=new byte[16384];int count;while((count=in.read(buffer))>=0)out.write(buffer,0,count);bytes=out.toByteArray(); }
            if ("index.html".equals(path) && !migrationPrefs.getBoolean("complete", false)) {
                String html=new String(bytes,StandardCharsets.UTF_8);
                String script="<script>(function(){var p="+migrationPayload()+";Object.keys(p).forEach(function(k){if(p[k]&&!localStorage.getItem(k))localStorage.setItem(k,p[k]);});try{QBankMigration.complete();}catch(e){}})();</script>";
                bytes=html.replace("<head>","<head>"+script).getBytes(StandardCharsets.UTF_8);
            }
            return new WebResourceResponse(mimeType(path), "UTF-8", new ByteArrayInputStream(bytes));
        } catch (Exception ignored) { return appAssetNotFound(); }
    }
    private static WebResourceResponse appAssetNotFound() {
        Map<String, String> headers = new HashMap<>();
        headers.put("X-Content-Type-Options", "nosniff");
        return new WebResourceResponse("text/plain", "UTF-8", 404, "Not Found", headers,
                new ByteArrayInputStream("App asset unavailable".getBytes(StandardCharsets.UTF_8)));
    }

    private String migrationPayload() {
        try { JSONObject p=new JSONObject();p.put("qbank_state_v1",migrationPrefs.getString("state",""));p.put("qbank_active_subject_v1",migrationPrefs.getString("subject",""));p.put("qbank_sync_v1",migrationPrefs.getString("sync",""));p.put("qbank_firebase_auth_v1",migrationPrefs.getString("auth",""));p.put("qbank_state_pre_cloud_v1",migrationPrefs.getString("backup",""));return p.toString().replace("<","\\u003c").replace(">","\\u003e").replace("&","\\u0026"); } catch(Exception ignored){return "{}";}
    }
    private static String mimeType(String path) {
        String p=path.toLowerCase();if(p.endsWith(".html"))return "text/html";if(p.endsWith(".js")||p.endsWith(".mjs"))return "application/javascript";if(p.endsWith(".css"))return "text/css";if(p.endsWith(".json")||p.endsWith(".webmanifest"))return "application/manifest+json";if(p.endsWith(".png"))return "image/png";if(p.endsWith(".jpg")||p.endsWith(".jpeg"))return "image/jpeg";if(p.endsWith(".pdf"))return "application/pdf";return "application/octet-stream";
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
    // NATIVE_BACK_SESSION_GUARD_V1: inspect the live route before system Back leaves a question.
    private boolean backCheckPending;
    private AlertDialog backDialog;

    private void continueBackNavigation() {
        if (webView != null && webView.canGoBack()) webView.goBack();
        else super.onBackPressed();
    }

    @Override public void onBackPressed() {
        if (webView == null) { super.onBackPressed(); return; }
        if (backCheckPending || (backDialog != null && backDialog.isShowing())) return;
        backCheckPending = true;
        webView.evaluateJavascript(
            "(function(){try{var q=window.QB;var s=q&&q.getState&&q.getState().activeSession;" +
            "var page=location.hash.split('/')[0];" +
            "if(s&&page==='#practice'&&s.mode==='practice'&&s.lifecycle!=='paused')return 'practice';" +
            "if(s&&page==='#exam'&&s.mode==='exam')return 'exam';" +
            "}catch(e){}return '';})()",
            value -> {
                backCheckPending = false;
                if (isFinishing()) return;
                boolean exam = "\"exam\"".equals(value);
                if (!exam && !"\"practice\"".equals(value)) { continueBackNavigation(); return; }
                backDialog = new AlertDialog.Builder(this)
                    .setTitle("Do you want to exit?")
                    .setIcon(android.R.drawable.ic_dialog_alert)
                    .setMessage(exam
                        ? "Your timed test will keep running if you exit now."
                        : "Your practice progress will be saved if you exit now.")
                    .setNegativeButton("Stay", null)
                    .setPositiveButton("Exit", (dialog, which) -> continueBackNavigation())
                    .create();
                backDialog.setOnDismissListener(dialog -> backDialog = null);
                backDialog.show();
            });
    }

    // NOTE_FILE_CHOOSER_V1: a plain WebChromeClient ignores <input type=file>.
    private static final int NOTE_FILE_REQUEST = 4107;
    private ValueCallback<Uri[]> noteFileCallback;

    private final class NoteFileChooserClient extends WebChromeClient {
        @Override public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback, FileChooserParams params) {
            if (noteFileCallback != null) noteFileCallback.onReceiveValue(null);
            noteFileCallback = callback;
            java.util.ArrayList<String> mimes = new java.util.ArrayList<>();
            for (String raw : params.getAcceptTypes()) {
                for (String part : raw.split(",")) {
                    String type = part.trim().toLowerCase(java.util.Locale.ROOT);
                    if (type.equals(".pdf")) type = "application/pdf";
                    if (type.contains("/") && !mimes.contains(type)) mimes.add(type);
                }
            }
            Intent intent = new Intent(Intent.ACTION_GET_CONTENT);
            intent.addCategory(Intent.CATEGORY_OPENABLE);
            intent.setType(mimes.size() == 1 ? mimes.get(0) : "*/*");
            if (mimes.size() > 1) intent.putExtra(Intent.EXTRA_MIME_TYPES, mimes.toArray(new String[0]));
            intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, params.getMode() == FileChooserParams.MODE_OPEN_MULTIPLE);
            try {
                startActivityForResult(Intent.createChooser(intent, "Add to note"), NOTE_FILE_REQUEST);
                return true;
            } catch (Exception error) {
                noteFileCallback = null;
                return false;
            }
        }
    }

    @Override protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        if (requestCode != NOTE_FILE_REQUEST) { super.onActivityResult(requestCode, resultCode, data); return; }
        ValueCallback<Uri[]> callback = noteFileCallback;
        noteFileCallback = null;
        if (callback == null) return;
        Uri[] result = null;
        ClipData clip = data == null ? null : data.getClipData();
        if (resultCode == RESULT_OK && clip != null && clip.getItemCount() > 0) {
            result = new Uri[clip.getItemCount()];
            for (int i = 0; i < clip.getItemCount(); i++) result[i] = clip.getItemAt(i).getUri();
        } else {
            result = WebChromeClient.FileChooserParams.parseResult(resultCode, data);
        }
        callback.onReceiveValue(result);
    }

    @Override protected void onDestroy(){synchronized(pdfLock){try{if(biochemistryRenderer!=null)biochemistryRenderer.close();}catch(Exception ignored){}try{if(biochemistryPfd!=null)biochemistryPfd.close();}catch(Exception ignored){}try{if(physiologyRenderer!=null)physiologyRenderer.close();}catch(Exception ignored){}try{if(physiologyPfd!=null)physiologyPfd.close();}catch(Exception ignored){}try{if(anatomyRenderer!=null)anatomyRenderer.close();}catch(Exception ignored){}try{if(anatomyPfd!=null)anatomyPfd.close();}catch(Exception ignored){}}if(webView!=null){webView.loadUrl("about:blank");webView.stopLoading();webView.setWebChromeClient(null);webView.setWebViewClient(null);webView.destroy();webView=null;}super.onDestroy();}
}
