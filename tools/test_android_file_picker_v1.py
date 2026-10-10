#!/usr/bin/env python3
"""Check the Android note file chooser installs once on the generated activity."""

from pathlib import Path

from apply_android_file_picker_v1 import JAVA, MARKER, transform


GENERATED = """import android.webkit.WebChromeClient;
public class MainActivity extends Activity {
    void setup(){webView.setBackgroundColor(Color.WHITE); webView.setHapticFeedbackEnabled(true); webView.setWebChromeClient(new WebChromeClient());}
    @Override protected void onDestroy(){if(webView!=null){webView.setWebChromeClient(null);}super.onDestroy();}
}
"""


def main() -> None:
    for label, source in (("generated", GENERATED), ("source", JAVA.read_text(encoding="utf-8"))):
        result = transform(source)
        assert transform(result) == result, label
        assert result.count(MARKER) == 1, label
        assert "setWebChromeClient(new NoteFileChooserClient())" in result, label
        assert "setWebChromeClient(new WebChromeClient())" not in result, label
        assert "setWebChromeClient(null)" in result, label
        assert "onShowFileChooser" in result and "onActivityResult" in result, label
        assert "EXTRA_ALLOW_MULTIPLE" in result and "getClipData()" in result, label
        assert result.index("NoteFileChooserClient extends") < result.index("protected void onDestroy()"), label
    print("ANDROID_NOTE_FILE_CHOOSER_OK")


if __name__ == "__main__":
    main()
