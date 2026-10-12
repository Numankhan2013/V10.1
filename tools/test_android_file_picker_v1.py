#!/usr/bin/env python3
"""Check the Android note file chooser ships once in the activity."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / "app/src/main/java/com/qbank/biochemistry/MainActivity.java"
MARKER = "NOTE_FILE_CHOOSER_V1"


def main() -> None:
    result = JAVA.read_text(encoding="utf-8")
    assert result.count(MARKER) == 1
    for imp in ("android.content.ClipData", "android.content.Intent", "android.net.Uri", "android.webkit.ValueCallback"):
        assert result.count(f"import {imp};") == 1, imp
    assert result.count("setWebChromeClient(new NoteFileChooserClient())") == 1
    assert "setWebChromeClient(new WebChromeClient())" not in result
    assert "setWebChromeClient(null)" in result
    assert "onShowFileChooser" in result and "onActivityResult" in result
    assert "requestCode != NOTE_FILE_REQUEST" in result and "noteFileCallback.onReceiveValue(null)" in result
    assert "EXTRA_ALLOW_MULTIPLE" in result and "getClipData()" in result
    assert '"application/pdf"' in result and "EXTRA_MIME_TYPES" in result
    assert result.index("NoteFileChooserClient extends") < result.index("protected void onDestroy()")
    print("ANDROID_NOTE_FILE_CHOOSER_OK")


if __name__ == "__main__":
    main()
