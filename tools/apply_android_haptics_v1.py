#!/usr/bin/env python3
"""Install action-specific Android haptics after the PDF-owned Activity rebuild."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / 'app/src/main/java/com/qbank/biochemistry/MainActivity.java'

BRIDGE = '''    // NATIVE_ACTION_HAPTICS_V1: framework effects honor the user's touch setting.
    private final class HapticsBridge {
        @JavascriptInterface public void play(String kind) {
            if (kind == null) return;
            final int effect;
            switch (kind) {
                case "choice": effect = HapticFeedbackConstants.CLOCK_TICK; break;
                case "navigate": effect = HapticFeedbackConstants.VIRTUAL_KEY; break;
                case "toggle": effect = HapticFeedbackConstants.CONTEXT_CLICK; break;
                case "mark": effect = HapticFeedbackConstants.LONG_PRESS; break;
                case "primary": effect = HapticFeedbackConstants.KEYBOARD_TAP; break;
                case "success": effect = Build.VERSION.SDK_INT >= 30 ? HapticFeedbackConstants.CONFIRM : HapticFeedbackConstants.VIRTUAL_KEY; break;
                case "error": effect = Build.VERSION.SDK_INT >= 30 ? HapticFeedbackConstants.REJECT : HapticFeedbackConstants.LONG_PRESS; break;
                default: return;
            }
            runOnUiThread(() -> { if (webView != null) webView.performHapticFeedback(effect); });
        }
    }

'''


def transform(source: str) -> str:
    if 'private final class HapticsBridge' in source:
        return source
    if 'private final class MigrationBridge' not in source:
        raise ValueError('Android secure-origin migration bridge must be installed first')
    if source.count('import android.view.Window;') != 1:
        raise ValueError('Window import owner mismatch')
    if source.count('webView.setBackgroundColor(Color.WHITE);') != 1:
        raise ValueError('WebView background owner mismatch')
    source = source.replace('import android.view.Window;',
                            'import android.view.HapticFeedbackConstants;\nimport android.view.Window;', 1)
    source = source.replace('webView.setBackgroundColor(Color.WHITE);',
                            'webView.setBackgroundColor(Color.WHITE); webView.setHapticFeedbackEnabled(true);', 1)
    source, count = re.subn(r'(webView\.addJavascriptInterface\(new MigrationBridge\(\),\s*"QBankMigration"\);)',
                            r'\1\n        webView.addJavascriptInterface(new HapticsBridge(), "QBankHaptics");', source, count=1)
    if count != 1:
        raise ValueError('Migration bridge registration owner mismatch')
    source = source.replace('    private final class MigrationBridge {', BRIDGE + '    private final class MigrationBridge {', 1)
    return source


def main() -> None:
    source = JAVA.read_text(encoding='utf-8')
    updated = transform(source)
    if updated != source:
        JAVA.write_text(updated, encoding='utf-8')
    print('ANDROID_ACTION_HAPTICS_OK')


if __name__ == '__main__':
    main()
