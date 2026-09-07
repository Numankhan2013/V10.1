#!/usr/bin/env python3
"""Serve bundled WebView assets from a private HTTPS origin and migrate file-origin state."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / "app/src/main/java/com/qbank/biochemistry/MainActivity.java"
MANIFEST = ROOT / "app/src/main/AndroidManifest.xml"


def once(source: str, old: str, new: str, label: str) -> str:
    if source.count(old) != 1:
        raise SystemExit(f"{label}: expected one anchor, found {source.count(old)}")
    return source.replace(old, new, 1)


METHODS = r'''
    private final class MigrationBridge {
        @JavascriptInterface public void capture(String state, String subject, String sync, String auth, String backup) {
            migrationPrefs.edit().putString("state", state).putString("subject", subject).putString("sync", sync).putString("auth", auth).putString("backup", backup).apply();
            runOnUiThread(() -> webView.loadUrl(APP_ORIGIN + "index.html"));
        }
        @JavascriptInterface public void complete() {
            migrationPrefs.edit().putBoolean("complete", true).remove("state").remove("subject").remove("sync").remove("auth").remove("backup").apply();
            runOnUiThread(() -> { if (webView != null) webView.removeJavascriptInterface("QBankMigration"); });
        }
    }

    private WebResourceResponse serveAppAsset(WebResourceRequest request) {
        String url = request.getUrl().toString(); if (!url.startsWith(APP_ORIGIN)) return null;
        try {
            String path = URLDecoder.decode(request.getUrl().getPath().substring("/app/".length()), "UTF-8");
            if (path.isEmpty()) path = "index.html"; if (path.contains("..") || path.startsWith("/")) return null;
            byte[] bytes;
            try (InputStream in = getAssets().open(path); ByteArrayOutputStream out = new ByteArrayOutputStream()) { byte[] buffer=new byte[16384];int count;while((count=in.read(buffer))>=0)out.write(buffer,0,count);bytes=out.toByteArray(); }
            if ("index.html".equals(path) && !migrationPrefs.getBoolean("complete", false)) {
                String html=new String(bytes,StandardCharsets.UTF_8);
                String script="<script>(function(){var p="+migrationPayload()+";Object.keys(p).forEach(function(k){if(p[k]&&!localStorage.getItem(k))localStorage.setItem(k,p[k]);});try{QBankMigration.complete();}catch(e){}})();</script>";
                bytes=html.replace("<head>","<head>"+script).getBytes(StandardCharsets.UTF_8);
            }
            return new WebResourceResponse(mimeType(path), "UTF-8", new ByteArrayInputStream(bytes));
        } catch (Exception ignored) { return null; }
    }
    private String migrationPayload() {
        try { JSONObject p=new JSONObject();p.put("qbank_state_v1",migrationPrefs.getString("state",""));p.put("qbank_active_subject_v1",migrationPrefs.getString("subject",""));p.put("qbank_sync_v1",migrationPrefs.getString("sync",""));p.put("qbank_firebase_auth_v1",migrationPrefs.getString("auth",""));p.put("qbank_state_pre_cloud_v1",migrationPrefs.getString("backup",""));return p.toString(); } catch(Exception ignored){return "{}";}
    }
    private static String mimeType(String path) {
        String p=path.toLowerCase();if(p.endsWith(".html"))return "text/html";if(p.endsWith(".js")||p.endsWith(".mjs"))return "application/javascript";if(p.endsWith(".css"))return "text/css";if(p.endsWith(".json")||p.endsWith(".webmanifest"))return "application/manifest+json";if(p.endsWith(".png"))return "image/png";if(p.endsWith(".jpg")||p.endsWith(".jpeg"))return "image/jpeg";if(p.endsWith(".pdf"))return "application/pdf";return "application/octet-stream";
    }

'''


def main() -> None:
    source = JAVA.read_text(encoding="utf-8")
    if "qbank_origin_migration_v1" in source:
        print("Android secure origin already installed")
        return
    source = once(source, "import android.app.Activity;", "import android.app.Activity;\nimport android.content.Context;\nimport android.content.SharedPreferences;", "context imports")
    source = once(source, "import android.webkit.WebChromeClient;", "import android.webkit.JavascriptInterface;\nimport android.webkit.WebChromeClient;", "bridge import")
    source = once(source, "import android.view.Window;", "import android.view.Window;\n\nimport org.json.JSONObject;", "JSON import")
    source = once(source, "import java.net.URLDecoder;", "import java.net.URLDecoder;\nimport java.nio.charset.StandardCharsets;", "charset import")
    source = once(source, "    private final Object pdfLock = new Object();", "    private final Object pdfLock = new Object();\n    private static final String APP_ORIGIN=\"https://qbank.local/app/\";\n    private SharedPreferences migrationPrefs;", "origin fields")
    source = once(source, "        preparePdfs();\n        webView = new WebView(this);", "        preparePdfs();\n        migrationPrefs=getSharedPreferences(\"qbank_origin_migration_v1\",Context.MODE_PRIVATE);\n        webView = new WebView(this);", "migration prefs")
    source = once(source, "        webView.setBackgroundColor(Color.WHITE); webView.setWebChromeClient(new WebChromeClient());", "        webView.setBackgroundColor(Color.WHITE); webView.setWebChromeClient(new WebChromeClient());\n        webView.addJavascriptInterface(new MigrationBridge(),\"QBankMigration\");", "bridge install")
    source = once(source, "@Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) { return true; }", "@Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) { return !request.getUrl().toString().startsWith(APP_ORIGIN); }", "navigation policy")
    source = once(source, "                WebResourceResponse response = renderPdfRequest(request);\n                return response != null ? response : super.shouldInterceptRequest(view, request);", "                WebResourceResponse response = renderPdfRequest(request);\n                if(response==null)response=serveAppAsset(request);\n                return response != null ? response : super.shouldInterceptRequest(view, request);", "asset interception")
    source = once(source, '        setContentView(webView); webView.loadUrl("file:///android_asset/index.html");', '        setContentView(webView);if(migrationPrefs.getBoolean("complete",false))webView.loadUrl(APP_ORIGIN+"index.html");else webView.loadUrl("file:///android_asset/migrate_local_state.html");', "secure app load")
    source = once(source, "    private void preparePdfs() {", METHODS + "    private void preparePdfs() {", "migration methods")
    JAVA.write_text(source, encoding="utf-8")

    manifest = MANIFEST.read_text(encoding="utf-8")
    if "android.permission.INTERNET" not in manifest:
        manifest = once(manifest, '<uses-permission android:name="android.permission.VIBRATE" />', '<uses-permission android:name="android.permission.VIBRATE" />\n    <uses-permission android:name="android.permission.INTERNET" />', "Internet permission")
        MANIFEST.write_text(manifest, encoding="utf-8")
    print("ANDROID_SECURE_ORIGIN_OK: HTTPS asset origin and one-time localStorage migration installed")


if __name__ == "__main__":
    main()
