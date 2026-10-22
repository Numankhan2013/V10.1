package com.qbank.biochemistry;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.ClipData;
import android.content.Intent;
import android.content.res.Configuration;
import android.graphics.Color;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.HapticFeedbackConstants;
import android.view.View;
import android.view.ViewTreeObserver;
import android.view.Window;
import android.view.WindowInsetsController;
import android.webkit.JavascriptInterface;
import android.webkit.JsPromptResult;
import android.webkit.JsResult;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Button;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

// NK_THIN_SHELL_V1: the app is the web build at BuildConfig.APP_URL. Questions,
// explanations, figures and PDFs load on demand there and the service worker
// keeps what has been opened for offline use, so the APK bundles no content.
// NK_NATIVE_FEEL_V1: the shell should read as an Android app, not a browser tab:
// the system splash stays until the first paint, system bars and window follow
// the app theme, offline is a native screen and toasts are Android toasts.
public class MainActivity extends Activity {
    private WebView webView;
    private View offlineView;
    private boolean firstPaint;
    private Boolean dark;
    private final Handler ui = new Handler(Looper.getMainLooper());
    private static final Uri APP_URL = Uri.parse(BuildConfig.APP_URL);
    // Production sits behind Cloudflare Access; its one-time-PIN login runs in the WebView.
    private static final String ACCESS_DOMAIN = ".cloudflareaccess.com";

    @SuppressLint("SetJavaScriptEnabled")
    @Override protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        applySystemBars((getResources().getConfiguration().uiMode & Configuration.UI_MODE_NIGHT_MASK) == Configuration.UI_MODE_NIGHT_YES);
        webView = new WebView(this);
        webView.setBackgroundColor(background());
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true); settings.setDomStorageEnabled(true); settings.setDatabaseEnabled(true);
        settings.setAllowFileAccess(false); settings.setAllowFileAccessFromFileURLs(false);
        settings.setAllowUniversalAccessFromFileURLs(false); settings.setAllowContentAccess(false);
        settings.setBuiltInZoomControls(false); settings.setDisplayZoomControls(false); settings.setSupportZoom(false);
        settings.setLoadsImagesAutomatically(true); settings.setMediaPlaybackRequiresUserGesture(true);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        webView.setHapticFeedbackEnabled(true); webView.setWebChromeClient(new NoteFileChooserClient());
        webView.addJavascriptInterface(new HapticsBridge(), "QBankHaptics");
        webView.addJavascriptInterface(new ShellBridge(), "QBankShell");
        webView.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri url = request.getUrl();
                if (inApp(url)) return false;
                // Only the schemes the app means to open leave the WebView.
                // Anything else (intent:, file:, javascript:, market:) is dropped.
                String scheme = url.getScheme();
                if (scheme == null || !(scheme.equals("http") || scheme.equals("https")
                        || scheme.equals("mailto") || scheme.equals("tel"))) {
                    return true;
                }
                // Anything else (source links, mail) opens outside the app.
                try { startActivity(new Intent(Intent.ACTION_VIEW, url)); } catch (Exception ignored) {}
                return true;
            }
            @Override public void onPageCommitVisible(WebView view, String url) {
                if (url != null && url.startsWith("http")) { offlineView.setVisibility(View.GONE); markPainted(); }
            }
            @Override public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                if (request.isForMainFrame()) { offlineView.setVisibility(View.VISIBLE); markPainted(); }
            }
        });
        FrameLayout root = new FrameLayout(this);
        root.addView(webView, new FrameLayout.LayoutParams(FrameLayout.LayoutParams.MATCH_PARENT, FrameLayout.LayoutParams.MATCH_PARENT));
        offlineView = buildOfflineView();
        offlineView.setVisibility(View.GONE);
        root.addView(offlineView, new FrameLayout.LayoutParams(FrameLayout.LayoutParams.MATCH_PARENT, FrameLayout.LayoutParams.MATCH_PARENT));
        setContentView(root);
        // Keep the system splash (Android 12+) or plain themed window up until the
        // page paints, instead of flashing an empty WebView; never longer than 4 s.
        root.getViewTreeObserver().addOnPreDrawListener(new ViewTreeObserver.OnPreDrawListener() {
            @Override public boolean onPreDraw() {
                if (!firstPaint) return false;
                root.getViewTreeObserver().removeOnPreDrawListener(this);
                return true;
            }
        });
        ui.postDelayed(this::markPainted, 4000);
        if (savedInstanceState == null || webView.restoreState(savedInstanceState) == null) webView.loadUrl(APP_URL.toString());
    }

    private void markPainted() {
        if (firstPaint) return;
        firstPaint = true;
        View content = findViewById(android.R.id.content);
        if (content != null) content.invalidate();
    }

    private int dp(int value) { return Math.round(TypedValue.applyDimension(TypedValue.COMPLEX_UNIT_DIP, value, getResources().getDisplayMetrics())); }

    // Same palette as the web theme (Geist monochrome).
    private int background() { return Boolean.TRUE.equals(dark) ? Color.rgb(10, 10, 10) : Color.WHITE; }
    private int foreground() { return Boolean.TRUE.equals(dark) ? Color.rgb(237, 237, 237) : Color.rgb(23, 23, 23); }
    private int muted() { return Boolean.TRUE.equals(dark) ? Color.rgb(161, 161, 161) : Color.rgb(102, 102, 102); }

    // The first launch needs a connection to sign in and load the app; after
    // that the service worker serves it offline and this screen is not reached.
    private View buildOfflineView() {
        LinearLayout box = new LinearLayout(this);
        box.setOrientation(LinearLayout.VERTICAL);
        box.setGravity(Gravity.CENTER);
        box.setPadding(dp(32), dp(32), dp(32), dp(32));
        box.setClickable(true);
        TextView title = new TextView(this);
        title.setText("You're offline");
        title.setTextSize(TypedValue.COMPLEX_UNIT_SP, 20);
        title.setTypeface(android.graphics.Typeface.DEFAULT_BOLD);
        title.setGravity(Gravity.CENTER);
        TextView body = new TextView(this);
        body.setText("Connect to the internet to open NK QBank for the first time. Questions you have opened before stay available offline.");
        body.setTextSize(TypedValue.COMPLEX_UNIT_SP, 15);
        body.setGravity(Gravity.CENTER);
        body.setLineSpacing(0, 1.2f);
        body.setPadding(0, dp(8), 0, dp(24));
        Button retry = new Button(this);
        retry.setText("Try again");
        retry.setAllCaps(false);
        retry.setTextSize(TypedValue.COMPLEX_UNIT_SP, 15);
        retry.setStateListAnimator(null);
        retry.setPadding(dp(24), 0, dp(24), 0);
        retry.setOnClickListener(v -> {
            v.performHapticFeedback(HapticFeedbackConstants.KEYBOARD_TAP);
            webView.loadUrl(APP_URL.toString());
        });
        box.addView(title);
        box.addView(body, new LinearLayout.LayoutParams(Math.min(dp(320), getResources().getDisplayMetrics().widthPixels - dp(64)), LinearLayout.LayoutParams.WRAP_CONTENT));
        box.addView(retry, new LinearLayout.LayoutParams(LinearLayout.LayoutParams.WRAP_CONTENT, dp(44)));
        box.setTag(new View[] {title, body, retry});
        paintOffline(box);
        return box;
    }

    private void paintOffline(View box) {
        if (box == null) return;
        View[] parts = (View[]) box.getTag();
        box.setBackgroundColor(background());
        ((TextView) parts[0]).setTextColor(foreground());
        ((TextView) parts[1]).setTextColor(muted());
        GradientDrawable shape = new GradientDrawable();
        shape.setCornerRadius(dp(10));
        shape.setColor(foreground());
        parts[2].setBackground(shape);
        ((TextView) parts[2]).setTextColor(background());
    }

    // Status bar, navigation bar, window and WebView backdrop follow the app theme.
    private void applySystemBars(boolean isDark) {
        if (dark != null && dark == isDark) return;
        dark = isDark;
        int color = background();
        Window window = getWindow();
        window.setStatusBarColor(color);
        window.setNavigationBarColor(color);
        window.getDecorView().setBackgroundColor(color);
        if (webView != null) webView.setBackgroundColor(color);
        if (Build.VERSION.SDK_INT >= 30) {
            WindowInsetsController bars = window.getInsetsController();
            if (bars != null) {
                int light = WindowInsetsController.APPEARANCE_LIGHT_STATUS_BARS | WindowInsetsController.APPEARANCE_LIGHT_NAVIGATION_BARS;
                bars.setSystemBarsAppearance(isDark ? 0 : light, light);
            }
        } else {
            View decor = window.getDecorView();
            int flags = decor.getSystemUiVisibility();
            int light = View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR | (Build.VERSION.SDK_INT >= 26 ? View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR : 0);
            decor.setSystemUiVisibility(isDark ? flags & ~light : flags | light);
        }
        paintOffline(offlineView);
    }

    @Override protected void onSaveInstanceState(Bundle outState) { super.onSaveInstanceState(outState); if (webView != null) webView.saveState(outState); }

    private static boolean appOrigin(Uri url) {
        String host = url.getHost();
        if (host == null) return false;
        return host.equals(APP_URL.getHost()) && APP_URL.getScheme().equals(url.getScheme()) && url.getPort() == APP_URL.getPort();
    }

    private static boolean inApp(Uri url) {
        String host = url.getHost();
        if (host == null) return false;
        return appOrigin(url) || ("https".equals(url.getScheme()) && host.endsWith(ACCESS_DOMAIN));
    }

    // The bridges are injected into every document the WebView loads, so a call
    // is only honoured when the page in front of the learner is the app itself.
    private boolean onAppOrigin() {
        if (webView == null) return false;
        String current = webView.getUrl();
        return current != null && appOrigin(Uri.parse(current));
    }

    private final class ShellBridge {
        @JavascriptInterface public String platform() { return onAppOrigin() ? "android" : ""; }
        @JavascriptInterface public void theme(boolean isDark) { if (!onAppOrigin()) return; runOnUiThread(() -> applySystemBars(isDark)); }
        @JavascriptInterface public void toast(String message) {
            if (!onAppOrigin()) return;
            if (message == null || message.isEmpty()) return;
            runOnUiThread(() -> Toast.makeText(MainActivity.this, message, message.length() > 60 ? Toast.LENGTH_LONG : Toast.LENGTH_SHORT).show());
        }
    }

    // NATIVE_ACTION_HAPTICS_V1: framework effects honor the user's touch setting.
    private final class HapticsBridge {
        @JavascriptInterface public void play(String kind) {
            if (!onAppOrigin()) return;
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
        // The default WebChromeClient swallows confirm() and prompt(): the page
        // gets no answer at all, so a confirmation dialog can never be answered.
        // Native dialogs keep the app readable and give the page a real answer.
        @Override public boolean onJsConfirm(WebView view, String url, String message, JsResult result) {
            new AlertDialog.Builder(MainActivity.this)
                .setMessage(message)
                .setPositiveButton("OK", (dialog, which) -> result.confirm())
                .setNegativeButton("Cancel", (dialog, which) -> result.cancel())
                .setOnCancelListener(dialog -> result.cancel())
                .show();
            return true;
        }

        @Override public boolean onJsPrompt(WebView view, String url, String message, String defaultValue, JsPromptResult result) {
            EditText input = new EditText(MainActivity.this);
            input.setText(defaultValue == null ? "" : defaultValue);
            new AlertDialog.Builder(MainActivity.this)
                .setMessage(message)
                .setView(input)
                .setPositiveButton("OK", (dialog, which) -> result.confirm(input.getText().toString()))
                .setNegativeButton("Cancel", (dialog, which) -> result.cancel())
                .setOnCancelListener(dialog -> result.cancel())
                .show();
            return true;
        }

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
        ui.removeCallbacksAndMessages(null);
        if (noteFileCallback != null) { noteFileCallback.onReceiveValue(null); noteFileCallback = null; }
        if (webView != null) { webView.setWebChromeClient(null); webView.destroy(); webView = null; }
        super.onDestroy();
    }
}
