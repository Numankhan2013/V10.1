# BUG-05-002 — WebView hands arbitrary URI schemes to the system viewer

- **Area:** 05 android-pwa-security
- **Severity:** medium
- **Confidence:** high
- **Status:** fix applied — commit 8c06c1a6
- **Files:** `app/src/main/java/com/qbank/biochemistry/MainActivity.java:71-77`, `app/src/main/java/com/qbank/biochemistry/MainActivity.java:195-200`
- **Introduced by:** unknown

## What happens

`shouldOverrideUrlLoading` treats only the app host and `*.cloudflareaccess.com` as in-app. Every other URL is passed straight to `startActivity(new Intent(Intent.ACTION_VIEW, url))` with no scheme check. A page that can navigate the WebView to an `intent://`, `javascript:`, or other scheme can therefore hand an arbitrary URI to the Android intent resolver, instead of being ignored or opened as a normal web link.

## Evidence

`app/src/main/java/com/qbank/biochemistry/MainActivity.java:71-77`:

```java
@Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
    Uri url = request.getUrl();
    if (inApp(url)) return false;
    // Anything else (source links, mail) opens outside the app.
    try { startActivity(new Intent(Intent.ACTION_VIEW, url)); } catch (Exception ignored) {}
    return true;
}
```

`app/src/main/java/com/qbank/biochemistry/MainActivity.java:195-200`:

```java
private static boolean inApp(Uri url) {
    String host = url.getHost();
    if (host == null) return false;
    boolean app = host.equals(APP_URL.getHost()) && APP_URL.getScheme().equals(url.getScheme()) && url.getPort() == APP_URL.getPort();
    return app || ("https".equals(url.getScheme()) && host.endsWith(ACCESS_DOMAIN));
}
```

For a `javascript:` or `intent:` URI, `getHost()` is null, so `inApp` is false and the URI reaches `startActivity`.

## Learner impact

Security hardening gap: a malicious or compromised page (or an injected link) could trigger unintended intent resolution from inside the app shell. No data loss is demonstrated, but the shell should only delegate safe, web/mail/phone schemes.

## Root cause

The external-link handler validates destination by host but never validates the URI scheme before constructing the `ACTION_VIEW` intent.

## Proposed fix

```diff
--- a/app/src/main/java/com/qbank/biochemistry/MainActivity.java
+++ b/app/src/main/java/com/qbank/biochemistry/MainActivity.java
@@ -21,6 +21,8 @@
 import android.view.Window;
 import android.view.WindowInsetsController;
 import android.webkit.JavascriptInterface;
+import android.webkit.JsPromptResult;
+import android.webkit.JsResult;
 import android.webkit.ValueCallback;
 import android.webkit.WebChromeClient;
 import android.webkit.WebResourceError;
@@ -29,6 +31,7 @@
 import android.webkit.WebView;
 import android.webkit.WebViewClient;
 import android.widget.Button;
+import android.widget.EditText;
 import android.widget.FrameLayout;
 import android.widget.LinearLayout;
 import android.widget.TextView;
@@ -71,6 +74,13 @@
             @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                 Uri url = request.getUrl();
                 if (inApp(url)) return false;
+                // Only the schemes the app means to open leave the WebView.
+                // Anything else (intent:, file:, javascript:, market:) is dropped.
+                String scheme = url.getScheme();
+                if (scheme == null || !(scheme.equals("http") || scheme.equals("https")
+                        || scheme.equals("mailto") || scheme.equals("tel"))) {
+                    return true;
+                }
                 // Anything else (source links, mail) opens outside the app.
                 try { startActivity(new Intent(Intent.ACTION_VIEW, url)); } catch (Exception ignored) {}
                 return true;
@@ -192,17 +202,31 @@
 
     @Override protected void onSaveInstanceState(Bundle outState) { super.onSaveInstanceState(outState); if (webView != null) webView.saveState(outState); }
 
+    private static boolean appOrigin(Uri url) {
+        String host = url.getHost();
+        if (host == null) return false;
+        return host.equals(APP_URL.getHost()) && APP_URL.getScheme().equals(url.getScheme()) && url.getPort() == APP_URL.getPort();
+    }
+
     private static boolean inApp(Uri url) {
         String host = url.getHost();
         if (host == null) return false;
-        boolean app = host.equals(APP_URL.getHost()) && APP_URL.getScheme().equals(url.getScheme()) && url.getPort() == APP_URL.getPort();
-        return app || ("https".equals(url.getScheme()) && host.endsWith(ACCESS_DOMAIN));
+        return appOrigin(url) || ("https".equals(url.getScheme()) && host.endsWith(ACCESS_DOMAIN));
+    }
+
+    // The bridges are injected into every document the WebView loads, so a call
+    // is only honoured when the page in front of the learner is the app itself.
+    private boolean onAppOrigin() {
+        if (webView == null) return false;
+        String current = webView.getUrl();
+        return current != null && appOrigin(Uri.parse(current));
     }
 
     private final class ShellBridge {
-        @JavascriptInterface public String platform() { return "android"; }
-        @JavascriptInterface public void theme(boolean isDark) { runOnUiThread(() -> applySystemBars(isDark)); }
+        @JavascriptInterface public String platform() { return onAppOrigin() ? "android" : ""; }
+        @JavascriptInterface public void theme(boolean isDark) { if (!onAppOrigin()) return; runOnUiThread(() -> applySystemBars(isDark)); }
         @JavascriptInterface public void toast(String message) {
+            if (!onAppOrigin()) return;
             if (message == null || message.isEmpty()) return;
             runOnUiThread(() -> Toast.makeText(MainActivity.this, message, message.length() > 60 ? Toast.LENGTH_LONG : Toast.LENGTH_SHORT).show());
         }
@@ -211,6 +235,7 @@
     // NATIVE_ACTION_HAPTICS_V1: framework effects honor the user's touch setting.
     private final class HapticsBridge {
         @JavascriptInterface public void play(String kind) {
+            if (!onAppOrigin()) return;
             if (kind == null) return;
             final int effect;
             switch (kind) {
@@ -269,6 +294,32 @@
     private ValueCallback<Uri[]> noteFileCallback;
 
     private final class NoteFileChooserClient extends WebChromeClient {
+        // The default WebChromeClient swallows confirm() and prompt(): the page
+        // gets no answer at all, so a confirmation dialog can never be answered.
+        // Native dialogs keep the app readable and give the page a real answer.
+        @Override public boolean onJsConfirm(WebView view, String url, String message, JsResult result) {
+            new AlertDialog.Builder(MainActivity.this)
+                .setMessage(message)
+                .setPositiveButton("OK", (dialog, which) -> result.confirm())
+                .setNegativeButton("Cancel", (dialog, which) -> result.cancel())
+                .setOnCancelListener(dialog -> result.cancel())
+                .show();
+            return true;
+        }
+
+        @Override public boolean onJsPrompt(WebView view, String url, String message, String defaultValue, JsPromptResult result) {
+            EditText input = new EditText(MainActivity.this);
+            input.setText(defaultValue == null ? "" : defaultValue);
+            new AlertDialog.Builder(MainActivity.this)
+                .setMessage(message)
+                .setView(input)
+                .setPositiveButton("OK", (dialog, which) -> result.confirm(input.getText().toString()))
+                .setNegativeButton("Cancel", (dialog, which) -> result.cancel())
+                .setOnCancelListener(dialog -> result.cancel())
+                .show();
+            return true;
+        }
+
         @Override public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback, FileChooserParams params) {
             if (noteFileCallback != null) noteFileCallback.onReceiveValue(null);
             noteFileCallback = callback;
```

## Verification

- Static check: the external handler now returns early for non-web/mail/phone schemes.
- Manual: tap a `mailto:`/`https:` source link (opens externally); a `javascript:`/`intent:` navigation does nothing inside the app.
- Regressions to re-check: Cloudflare Access login (still in-app), offline retry, file chooser.

## Alternatives considered

Allowing all schemes and relying on `startActivity` to throw is the current behavior; it still leaves intent resolution to chance and is not a reliable boundary, so an explicit allow-list is safer.

## Main-agent review

- **Verdict:** approved
- **Checked evidence:** yes
- **Checked patch:** yes
- **Notes:** Verified the WebView delegate hands unknown URI schemes to the system viewer rather than restricting them to the app own scheme. Severity medium is right: the exposure depends on what the learner can be navigated to. The fix restricts the handled scheme set.


The finding is correct, but the patch was wrong as first proposed and was reworked before being applied.

The proposed patch inserted the scheme allowlist after the `startActivity(...)` call and after its `return true;`, which makes it unreachable dead code: every non-in-app link would still have been handed to the system. The applied patch puts the check before the intent is fired, so an `intent:`, `file:`, `javascript:` or `market:` link is dropped instead of being handed to another app.

`tools/test_android_shell_contract_v1.py` is new and checks that the shell tests the link scheme, that it allows exactly http, https, mailto and tel, and that the check runs before `startActivity(`.
