# BUG-05-001 — Android auto-backup can restore another account's auth token and progress

- **Area:** 05 android-pwa-security
- **Severity:** high
- **Confidence:** medium
- **Status:** fix applied — commit pending (this commit)
- **Files:** `app/src/main/AndroidManifest.xml:7`, `app/src/main/res/xml/nk_data_extraction_rules.xml`
- **Introduced by:** unknown

## What happens

NK QBank stores its signed-in Firebase refresh token and all learner progress inside the WebView origin (localStorage/IndexedDB). With `android:allowBackup="true"` and no backup rules, Android Auto Backup can upload that data to the user's Google account and restore it onto another device or after a reinstall. That can resurrect an old session, including a still-valid refresh token, on a device that is not signed in, creating an account-crossover/privacy exposure.

## Evidence

`app/src/main/AndroidManifest.xml:7`:

```xml
<application
    android:allowBackup="true"
    ...
```

The app has no `android:fullBackupContent`/`android:dataExtractionRules`, so the default backup set applies. `cross_device_sync.js` persists `NK_AUTH_KEY='qbank_firebase_auth_v1'` (refresh token) in `localStorage` (`nkSaveAuth`), and `MainActivity` uses `setDomStorageEnabled(true)` with a remote HTTPS origin, so WebView storage is part of the app data directory.

## Learner impact

Privacy/account crossover: a restored backup can silently re-authenticate a previous account or overwrite local progress on a shared/replacement device. Device-only behavior is unverified in this environment (no emulator), so confidence is medium.

## Root cause

The thin-shell Android app delegates all identity and state to the web origin, but the manifest still opts into the platform's default full-data backup. Nothing excludes the WebView storage that holds credentials.

## Proposed fix

```diff
--- a/app/src/main/AndroidManifest.xml
+++ b/app/src/main/AndroidManifest.xml
@@ -4,7 +4,8 @@
     <uses-permission android:name="android.permission.INTERNET" />
 
     <application
-        android:allowBackup="true"
+        android:allowBackup="false"
+        android:dataExtractionRules="@xml/nk_data_extraction_rules"
         android:icon="@drawable/nk_qbank_icon"
         android:label="NK QBank"
         android:resizeableActivity="true"
```

## Verification

- Inspect the built APK manifest for `android:allowBackup="false"`.
- Manual: install, sign in, back up, uninstall/reinstall or restore to a second device; confirm no automatic sign-in/progress appears and the app starts signed out.
- Regressions to re-check: first-launch offline screen, Cloudflare Access login, PWA update flow.

## Alternatives considered

Adding `android:dataExtractionRules` to exclude only WebView storage would preserve non-sensitive backup, but it requires per-API-level XML and is easier to get wrong; disabling backup is the smallest safe containment for a credential-holding app.

## Main-agent review

- **Verdict:** approved
- **Checked evidence:** yes
- **Checked patch:** yes
- **Notes:** Verified against AndroidManifest.xml and MainActivity.java: the app sets no android:allowBackup="false" and ships no dataExtractionRules or fullBackupContent, so android:autoBackup includes the app data directory, which holds the Firebase auth token and the progress store. Severity high is right because a restored backup can sign the learner into a previous account on a new device and merge two accounts of progress. Confidence medium is honest: the exact backup payload depends on the Android version and the backup transport. The fix must keep allowBackup=false consistent with the app own data rules.


The finding is correct, and the fix was strengthened during review.

`android:allowBackup="false"` on its own is not enough for this app. The app targets SDK 35, and the platform documentation says that for apps targeting Android 12 (API 31) or higher the behaviour varies: on some manufacturers `allowBackup="false"` disables cloud backup but not device-to-device transfer, and a `<device-transfer>` section that is missing leaves that mode "fully enabled for all content". The WebView origin lives in the app data directory, so a device-to-device transfer would still carry the refresh token and the progress store.

The applied fix therefore does both: `android:allowBackup="false"` and `android:dataExtractionRules="@xml/nk_data_extraction_rules"`, with a new `app/src/main/res/xml/nk_data_extraction_rules.xml` that excludes every domain (`root`, `file`, `database`, `sharedpref`, `external` and the four `device_*` domains) from both `<cloud-backup>` and `<device-transfer>`. The `root` domain is what covers the WebView data directory.

`tools/test_android_shell_contract_v1.py` is new and checks the manifest, the rules file and the Android build's own data rules. It fails on the pre-fix manifest with "the app must not be eligible for backup".

The Android build itself cannot be compiled in this environment, so the manifest and the new resource file must be confirmed by a passing GitHub Actions run before the fix is called verified.
