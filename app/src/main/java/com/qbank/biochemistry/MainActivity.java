package com.qbank.biochemistry;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.ClipData;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.view.HapticFeedbackConstants;
import android.view.Window;
import android.webkit.JavascriptInterface;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

// NK_THIN_SHELL_V1: the app is the web build at BuildConfig.APP_URL. Questions,
// explanations, figures and PDFs load on demand there and the service worker
// keeps what has been opened for offline use, so the APK bundles no content.
public class MainActivity extends Activity {
    private WebView webView;
    private static final Uri APP_URL = Uri.parse(BuildConfig.APP_URL);
    // Production sits behind Cloudflare Access; its one-time-PIN login runs in the WebView.
    private static final String ACCESS_DOMAIN = ".cloudflareaccess.com";

    @SuppressLint("SetJavaScriptEnabled")
    @Override protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        Window window = getWindow();
        window.setStatusBarColor(Color.rgb(52, 46, 134));
        window.setNavigationBarColor(Color.rgb(244, 245, 248));
        webView = new WebView(this);
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true); settings.setDomStorageEnabled(true); settings.setDatabaseEnabled(true);
        settings.setAllowFileAccess(false); settings.setAllowFileAccessFromFileURLs(false);
        settings.setAllowUniversalAccessFromFileURLs(false); settings.setAllowContentAccess(false);
        settings.setBuiltInZoomControls(false); settings.setDisplayZoomControls(false); settings.setSupportZoom(false);
        settings.setLoadsImagesAutomatically(true); settings.setMediaPlaybackRequiresUserGesture(true);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        webView.setBackgroundColor(Color.WHITE); webView.setHapticFeedbackEnabled(true); webView.setWebChromeClient(new NoteFileChooserClient());
        webView.addJavascriptInterface(new HapticsBridge(), "QBankHaptics");
        webView.addJavascriptInterface(new ShellBridge(), "QBankShell");
        webView.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri url = request.getUrl();
                if (inApp(url)) return false;
                // Anything else (source links, mail) opens outside the app.
                try { startActivity(new Intent(Intent.ACTION_VIEW, url)); } catch (Exception ignored) {}
                return true;
            }
            @Override public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                if (request.isForMainFrame()) showOffline();
            }
        });
        setContentView(webView);
        if (savedInstanceState == null || webView.restoreState(savedInstanceState) == null) webView.loadUrl(APP_URL.toString());
    }

    @Override protected void onSaveInstanceState(Bundle outState) { super.onSaveInstanceState(outState); if (webView != null) webView.saveState(outState); }

    private static boolean inApp(Uri url) {
        String host = url.getHost();
        if (host == null) return false;
        boolean app = host.equals(APP_URL.getHost()) && APP_URL.getScheme().equals(url.getScheme()) && url.getPort() == APP_URL.getPort();
        return app || ("https".equals(url.getScheme()) && host.endsWith(ACCESS_DOMAIN));
    }

    // The first launch needs a connection to sign in and load the app; after
    // that the service worker serves it offline and this page is not reached.
    private void showOffline() {
        String html = "<!doctype html><meta name=viewport content='width=device-width,initial-scale=1'>"
            + "<body style='font:16px system-ui,sans-serif;margin:0;display:grid;place-items:center;min-height:100vh;background:#fff;color:#111'>"
            + "<div style='max-width:320px;padding:24px;text-align:center'><h1 style='font-size:20px'>NK QBank is offline</h1>"
            + "<p style='color:#555'>Connect to the internet to open the app. Questions you have opened before stay available offline.</p>"
            + "<button onclick='QBankShell.retry()' style='font:inherit;padding:12px 20px;border-radius:10px;border:1px solid #111;background:#111;color:#fff'>Try again</button></div>";
        webView.loadDataWithBaseURL(null, html, "text/html", "UTF-8", null);
    }

    private final class ShellBridge {
        @JavascriptInterface public String platform() { return "android"; }
        @JavascriptInterface public void retry() { runOnUiThread(() -> { if (webView != null) webView.loadUrl(APP_URL.toString()); }); }
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

    @Override protected void onDestroy() {
        if (noteFileCallback != null) { noteFileCallback.onReceiveValue(null); noteFileCallback = null; }
        if (webView != null) { webView.setWebChromeClient(null); webView.destroy(); webView = null; }
        super.onDestroy();
    }
}
