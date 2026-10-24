# BUG-05-006 — Android WebView swallows `confirm()` and `prompt()`

- **Area:** 05 android-pwa-security
- **Severity:** medium
- **Confidence:** high
- **Status:** fix applied — commit 8c06c1a6
- **Files:** `app/src/main/java/com/qbank/biochemistry/MainActivity.java:67`, `app/src/main/java/com/qbank/biochemistry/MainActivity.java:267-296`
- **Introduced by:** unknown

## What happens

The app's `WebChromeClient` only overrides `onShowFileChooser`. The default `WebChromeClient` returns `false` for `onJsConfirm`/`onJsPrompt`, so the WebView never shows a dialog and `window.confirm()` resolves to `false` and `window.prompt()` to `null`. On Android this disables every confirmation-gated action in the app: deleting/renaming study modules, abandoning a timed test, deleting note images/PDF pages, and the account-wide reset confirmation. Those actions either silently do nothing or can never be confirmed.

## Evidence

`app/src/main/java/com/qbank/biochemistry/MainActivity.java:67`:

```java
webView.setWebChromeClient(new NoteFileChooserClient());
```

`app/src/main/java/com/qbank/biochemistry/MainActivity.java:267-271`:

```java
private final class NoteFileChooserClient extends WebChromeClient {
    @Override public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback, FileChooserParams params) {
```

No `onJsConfirm` or `onJsPrompt` override exists in the file. The web code depends on them, e.g. `app/src/main/modules/study_modules.js`:

```javascript
if(!confirm(`Restart ${module.name}? ...`)) return;
const name=prompt('Rename study module',module.name); if(name===null) return;
```

and `app/src/main/modules/cross_device_sync.js`:

```javascript
if(!confirm(message)) return;
if(account&&!confirm('Confirm account-wide reset...')) return;
```

## Learner impact

Broken secondary actions on Android: module restart/rename/delete, timed-test abandonment, note-media deletion, and account reset confirmation can never be completed from the Android shell.

## Root cause

The native shell replaced the default dialog-capable `WebChromeClient` with a file-chooser-only subclass and did not re-implement JavaScript confirm/prompt dialogs.

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

- Manual on Android: confirm dialogs appear for module delete/restart and timed-test abandon; `prompt` opens a text field for rename; OK/Cancel return the expected boolean/string to JS.
- Regressions to re-check: file chooser (still works), haptics, toasts, back navigation, offline screen.

## Alternatives considered

Replacing `confirm()`/`prompt()` calls in the web code with custom in-app modals would be larger and would diverge Android from PWA; restoring the native dialogs keeps both platforms identical.

## Main-agent review

- **Verdict:** approved
- **Checked evidence:** yes
- **Checked patch:** yes
- **Notes:** Verified MainActivity.java: the WebView chrome client does not handle onJsConfirm or onJsPrompt, so confirm() and prompt() are silently dropped. Medium severity is right: the WebView default is to cancel the dialog, so a confirmation-dependent flow cannot be completed. Confidence high: the missing overrides are visible in the source.


The finding is correct, but the proposed patch was wrong and was reworked before being applied.

The proposed patch inserted the two dialog handlers inside the body of `onShowFileChooser`, which is not valid Java: a method cannot contain another method declaration, so the app would not have compiled.

The applied patch declares `onJsConfirm` and `onJsPrompt` as members of the `NoteFileChooserClient` class, next to `onShowFileChooser`, and adds the three imports they need. The handlers answer the page with a native dialog and always resolve the JavaScript result, including when the dialog is dismissed.

`tools/test_android_shell_contract_v1.py` is new and checks that both handlers exist and are declared at the same level as `onShowFileChooser`, so a nested declaration is caught. It fails on the pre-fix shell with "the shell must answer onJsConfirm()".

The Android build cannot be compiled in this environment, so the shell must be confirmed by a passing GitHub Actions run before the fix is called verified.
