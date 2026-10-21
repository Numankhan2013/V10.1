# BUG-05-002 — WebView hands arbitrary URI schemes to the system viewer

- **Area:** 05 android-pwa-security
- **Severity:** medium
- **Confidence:** high
- **Status:** open — proposed fix, not applied
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
@@ -75,5 +75,10 @@
                 try { startActivity(new Intent(Intent.ACTION_VIEW, url)); } catch (Exception ignored) {}
                 return true;
             }
+                String scheme = url.getScheme();
+                if (scheme == null || !(scheme.equals("http") || scheme.equals("https")
+                        || scheme.equals("mailto") || scheme.equals("tel"))) {
+                    return true;
+                }
             @Override public void onPageCommitVisible(WebView view, String url) {
                 if (url != null && url.startsWith("http")) { offlineView.setVisibility(View.GONE); markPainted(); }
             }```

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
