# BUG-05-004 — Native JS bridge is reachable from the Cloudflare Access login page

- **Area:** 05 android-pwa-security
- **Severity:** medium
- **Confidence:** medium
- **Status:** fix applied — commit 8c06c1a6
- **Files:** `app/src/main/java/com/qbank/biochemistry/MainActivity.java:67-69`, `app/src/main/java/com/qbank/biochemistry/MainActivity.java:195-200`, `app/src/main/java/com/qbank/biochemistry/MainActivity.java:202-209`
- **Introduced by:** unknown

## What happens

`inApp()` treats any `https://*.cloudflareaccess.com` URL as in-app, so the WebView loads the Cloudflare Access login page with JavaScript enabled and with `QBankShell`/`QBankHaptics` still injected. Those bridge objects are therefore callable from an origin the app does not control. The exposed methods are limited (`platform`, `theme`, `toast`, haptic effects), but a login-page script can still drive native UI (system bars, toasts, haptics) and read the `platform()` marker.

## Evidence

`app/src/main/java/com/qbank/biochemistry/MainActivity.java:67-69`:

```java
webView.addJavascriptInterface(new HapticsBridge(), "QBankHaptics");
webView.addJavascriptInterface(new ShellBridge(), "QBankShell");
```

`app/src/main/java/com/qbank/biochemistry/MainActivity.java:195-200`:

```java
return app || ("https".equals(url.getScheme()) && host.endsWith(ACCESS_DOMAIN));
```

`app/src/main/java/com/qbank/biochemistry/MainActivity.java:202-209`:

```java
private final class ShellBridge {
    @JavascriptInterface public String platform() { return "android"; }
    @JavascriptInterface public void theme(boolean isDark) { runOnUiThread(() -> applySystemBars(isDark)); }
    @JavascriptInterface public void toast(String message) { ... }
}
```

No origin check guards these methods; `addJavascriptInterface` exposes them to every document in the WebView.

## Learner impact

Security/privacy hardening gap: a third-party login page can call the native bridge. Impact is limited to UI manipulation because the methods are small, but the boundary is wrong and any future bridge method would inherit the exposure. Device-only behavior is unverified in this environment.

## Root cause

The native bridges are registered globally for the WebView and are never gated on the current document's origin, while the in-app definition deliberately includes the Cloudflare Access origin.

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

(Apply the same `appOrigin()` guard to `HapticsBridge.play`.)

## Verification

- Manual: on the Cloudflare Access login page, `window.QBankShell` either is undefined or its methods no-op; on the app origin they behave as before.
- Regressions to re-check: theme sync, toasts, haptics, file chooser, back navigation.

## Alternatives considered

Removing the bridge entirely would break native feel (theme sync, toasts, haptics) for the trusted app; gating by origin keeps the feature while closing the third-party path.

## Main-agent review

- **Verdict:** approved
- **Checked evidence:** yes
- **Checked patch:** yes
- **Notes:** Verified that the native bridge is registered on the WebView regardless of which page is loaded, so the Cloudflare Access login page can reach it. Medium severity and medium confidence are right: reachability depends on the Access deployment and what the login page does with the bridge. The fix scopes the bridge to the app origin.


The finding is correct, but the proposed patch was wrong and was reworked before being applied.

The proposed patch removed the `if (message == null || message.isEmpty()) return;` guard from `toast` and changed nothing else: it would have introduced a null dereference on `message.length()` and left the bridge just as reachable. The prose in that finding did describe the right fix ("apply the same `appOrigin()` guard to `HapticsBridge.play`"), but the diff did not contain it.

The applied patch is the one the finding describes in prose:

- `appOrigin(Uri)` factors the app-origin test out of `inApp`, which keeps the Cloudflare Access origin in-app but on a separate test.
- `onAppOrigin()` compares the WebView's current URL with the app origin, so a bridge call is only honoured while the app itself is in front of the learner.
- `ShellBridge.platform`, `ShellBridge.theme`, `ShellBridge.toast` and `HapticsBridge.play` all check it. `platform()` returns an empty string off-origin, which is the "not the native shell" answer.

`tools/test_android_shell_contract_v1.py` is new and checks that all four bridge methods consult the origin. It fails on the pre-fix shell with "the bridge method platform() must check the origin".

The Android build cannot be compiled in this environment, so the shell must be confirmed by a passing GitHub Actions run before the fix is called verified.
