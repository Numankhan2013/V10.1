# BUG-05-006 — Android WebView swallows `confirm()` and `prompt()`

- **Area:** 05 android-pwa-security
- **Severity:** medium
- **Confidence:** high
- **Status:** open — proposed fix, not applied
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
@@ -9,6 +9,7 @@
 import android.graphics.Color;
 import android.graphics.drawable.GradientDrawable;
 import android.net.Uri;
+import android.widget.EditText;
 import android.os.Build;
 import android.os.Bundle;
 import android.os.Handler;
@@ -29,6 +30,8 @@
 import android.webkit.WebView;
 import android.webkit.WebViewClient;
 import android.widget.Button;
+import android.webkit.JsResult;
+import android.webkit.JsPromptResult;
 import android.widget.FrameLayout;
 import android.widget.LinearLayout;
 import android.widget.TextView;
@@ -270,5 +273,26 @@
 
     private final class NoteFileChooserClient extends WebChromeClient {
         @Override public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback, FileChooserParams params) {
+        @Override public boolean onJsConfirm(WebView view, String url, String message, JsResult result) {
+            new AlertDialog.Builder(MainActivity.this)
+                .setMessage(message)
+                .setPositiveButton("OK", (dialog, which) -> result.confirm())
+                .setNegativeButton("Cancel", (dialog, which) -> result.cancel())
+                .setOnCancelListener(dialog -> result.cancel())
+                .show();
+            return true;
+        }
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
             if (noteFileCallback != null) noteFileCallback.onReceiveValue(null);
             noteFileCallback = callback;
             java.util.ArrayList<String> mimes = new java.util.ArrayList<>();```

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
