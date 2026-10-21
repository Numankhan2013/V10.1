# BUG-05-004 — Native JS bridge is reachable from the Cloudflare Access login page

- **Area:** 05 android-pwa-security
- **Severity:** medium
- **Confidence:** medium
- **Status:** open — proposed fix, not applied
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
@@ -203,6 +203,5 @@
         @JavascriptInterface public String platform() { return "android"; }
         @JavascriptInterface public void theme(boolean isDark) { runOnUiThread(() -> applySystemBars(isDark)); }
         @JavascriptInterface public void toast(String message) {
-            if (message == null || message.isEmpty()) return;
             runOnUiThread(() -> Toast.makeText(MainActivity.this, message, message.length() > 60 ? Toast.LENGTH_LONG : Toast.LENGTH_SHORT).show());
         }
     }```

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
