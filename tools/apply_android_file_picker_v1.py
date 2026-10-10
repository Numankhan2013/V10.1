#!/usr/bin/env python3
"""Let the Android WebView open the system picker for note images and PDF pages."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / "app/src/main/java/com/qbank/biochemistry/MainActivity.java"
MARKER = "NOTE_FILE_CHOOSER_V1"

IMPORTS = """import android.content.ClipData;
import android.content.Intent;
import android.net.Uri;
import android.webkit.ValueCallback;
"""

MEMBERS = """    // NOTE_FILE_CHOOSER_V1: a plain WebChromeClient ignores <input type=file>.
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

"""


def once(source: str, old: str, new: str, label: str) -> str:
    count = source.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    return source.replace(old, new, 1)


def transform(source: str) -> str:
    if MARKER in source:
        return source
    source = once(source, "import android.webkit.WebChromeClient;\n", IMPORTS + "import android.webkit.WebChromeClient;\n", "file chooser imports")
    source = once(source, "webView.setWebChromeClient(new WebChromeClient());", "webView.setWebChromeClient(new NoteFileChooserClient());", "file chooser client")
    source = once(source, "    @Override protected void onDestroy(){", MEMBERS + "    @Override protected void onDestroy(){", "file chooser members")
    return source


if __name__ == "__main__":
    JAVA.write_text(transform(JAVA.read_text(encoding="utf-8")), encoding="utf-8")
    print("ANDROID_NOTE_FILE_CHOOSER_INSTALLED images=true pdf=true multiple=true")
