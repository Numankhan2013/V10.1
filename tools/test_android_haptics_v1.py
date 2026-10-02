#!/usr/bin/env python3
"""Verify the native bridge survives the generated Activity pipeline."""
from pathlib import Path

from apply_android_haptics_v1 import transform

ROOT = Path(__file__).resolve().parents[1]


def main():
    generated = '''import android.view.Window;
class MainActivity {
    void setup(){webView.setBackgroundColor(Color.WHITE); webView.setWebChromeClient(new WebChromeClient());
        webView.addJavascriptInterface(new MigrationBridge(),"QBankMigration");}
    private final class MigrationBridge {}
}'''
    installed = transform(generated)
    assert transform(installed) == installed
    for contract in ('addJavascriptInterface(new HapticsBridge(), "QBankHaptics")',
                     'webView.performHapticFeedback(effect)', 'HapticFeedbackConstants.CONFIRM',
                     'HapticFeedbackConstants.REJECT', 'HapticFeedbackConstants.LONG_PRESS',
                     'webView.setHapticFeedbackEnabled(true)'):
        assert contract in installed, contract
    assert 'FLAG_IGNORE_GLOBAL_SETTING' not in installed
    gentle = installed.replace(
        'case "complete":\n                case "success": effect = Build.VERSION.SDK_INT >= 30 ? HapticFeedbackConstants.CONFIRM : HapticFeedbackConstants.VIRTUAL_KEY; break;\n                case "error": effect = Build.VERSION.SDK_INT >= 30 ? HapticFeedbackConstants.REJECT : HapticFeedbackConstants.LONG_PRESS; break;',
        'case "success":\n                case "error": effect = HapticFeedbackConstants.CLOCK_TICK; break;\n                case "complete": effect = Build.VERSION.SDK_INT >= 30 ? HapticFeedbackConstants.CONFIRM : HapticFeedbackConstants.VIRTUAL_KEY; break;'
    )
    assert transform(gentle) == installed, 'existing bridge must be restored to prior answer haptics'
    current = (ROOT / 'app/src/main/java/com/qbank/biochemistry/MainActivity.java').read_text()
    assert 'HapticFeedbackConstants.REJECT' in current
    assert 'HapticFeedbackConstants.LONG_PRESS' in current
    print('ANDROID_ACTION_HAPTICS_TEST_OK generated=true idempotent=true prior_answers=true current=true')


if __name__ == '__main__':
    main()
