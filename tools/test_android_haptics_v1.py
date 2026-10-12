#!/usr/bin/env python3
"""Verify the shipped Activity keeps the native action-haptics bridge."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JAVA = ROOT / 'app/src/main/java/com/qbank/biochemistry/MainActivity.java'

BRIDGE = '''    // NATIVE_ACTION_HAPTICS_V1: framework effects honor the user's touch setting.
    private final class HapticsBridge {
        @JavascriptInterface public void play(String kind) {
            if (kind == null) return;
            final int effect;
            switch (kind) {
                case "choice": effect = HapticFeedbackConstants.CLOCK_TICK; break;
                case "mark": effect = HapticFeedbackConstants.CONTEXT_CLICK; break;
                case "primary": effect = HapticFeedbackConstants.KEYBOARD_TAP; break;
                case "complete":
                case "success": effect = Build.VERSION.SDK_INT >= 30 ? HapticFeedbackConstants.CONFIRM : HapticFeedbackConstants.VIRTUAL_KEY; break;
                case "error": effect = Build.VERSION.SDK_INT >= 30 ? HapticFeedbackConstants.REJECT : HapticFeedbackConstants.LONG_PRESS; break;
                default: return;
            }
            runOnUiThread(() -> { if (webView != null) webView.performHapticFeedback(effect); });
        }
    }

'''


def main():
    current = JAVA.read_text(encoding='utf-8')
    assert current.count(BRIDGE) == 1, 'haptics bridge must ship once with prior answer haptics'
    assert current.index(BRIDGE) < current.index('    private final class MigrationBridge')
    assert current.count('import android.view.HapticFeedbackConstants;') == 1
    for contract in ('addJavascriptInterface(new HapticsBridge(), "QBankHaptics")',
                     'webView.performHapticFeedback(effect)', 'HapticFeedbackConstants.CONFIRM',
                     'HapticFeedbackConstants.REJECT', 'HapticFeedbackConstants.LONG_PRESS',
                     'webView.setHapticFeedbackEnabled(true)'):
        assert current.count(contract) == 1, contract
    assert 'FLAG_IGNORE_GLOBAL_SETTING' not in current
    assert 'case "error": effect = HapticFeedbackConstants.CLOCK_TICK' not in current, 'answer haptics must not be flattened'
    print('ANDROID_ACTION_HAPTICS_TEST_OK bridge=true prior_answers=true current=true')


if __name__ == '__main__':
    main()
