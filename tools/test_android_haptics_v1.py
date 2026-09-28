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
                     'HapticFeedbackConstants.REJECT', 'webView.setHapticFeedbackEnabled(true)'):
        assert contract in installed, contract
    assert 'FLAG_IGNORE_GLOBAL_SETTING' not in installed
    current = (ROOT / 'app/src/main/java/com/qbank/biochemistry/MainActivity.java').read_text()
    assert 'private final class HapticsBridge' in current
    print('ANDROID_ACTION_HAPTICS_TEST_OK generated=true idempotent=true current=true')


if __name__ == '__main__':
    main()
