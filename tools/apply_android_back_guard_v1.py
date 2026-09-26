#!/usr/bin/env python3
"""Confirm Android system Back before leaving an active question session."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / "app/src/main/java/com/qbank/biochemistry/MainActivity.java"
MARKER = "NATIVE_BACK_SESSION_GUARD_V1"
OLD_BACK = "    @Override public void onBackPressed(){if(webView!=null&&webView.canGoBack())webView.goBack();else super.onBackPressed();}"
NEW_BACK = '''    // NATIVE_BACK_SESSION_GUARD_V1: inspect the live route before system Back leaves a question.
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
                boolean exam = "\\\"exam\\\"".equals(value);
                if (!exam && !"\\\"practice\\\"".equals(value)) { continueBackNavigation(); return; }
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
'''


def main() -> None:
    source = JAVA.read_text(encoding="utf-8")
    if MARKER in source:
        print("ANDROID_BACK_GUARD_OK already installed")
        return
    if source.count(OLD_BACK) != 1:
        raise SystemExit(f"Android Back owner mismatch: {source.count(OLD_BACK)} anchors")
    if source.count("import android.app.Activity;") != 1:
        raise SystemExit("Android Activity import owner mismatch")
    source = source.replace("import android.app.Activity;", "import android.app.Activity;\nimport android.app.AlertDialog;", 1)
    source = source.replace(OLD_BACK, NEW_BACK, 1)
    JAVA.write_text(source, encoding="utf-8")
    print("ANDROID_BACK_GUARD_OK active Practice and timed-test Back confirmation installed")


if __name__ == "__main__":
    main()
