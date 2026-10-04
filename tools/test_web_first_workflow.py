"""Protect web-only dispatch/push paths and the explicit optional Android gate."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def main():
    workflow = (ROOT/'.github/workflows/build-apk.yml').read_text()
    assert re.search(r'      build_apk:\n(?:        .*\n)*?        default: false', workflow)
    android_job = workflow.split('  android-interaction:', 1)[1].split('  build:', 1)[0]
    job_if = re.search(r'^    if: (.*)$', android_job, re.M).group(1)
    assert 'workflow_dispatch' in job_if and 'inputs.build_apk' in job_if
    steps = {}
    for block in re.split(r'^      - name: ', workflow.split('  build:', 1)[1], flags=re.M)[1:]:
        name, body = block.split('\n', 1)
        steps[name] = body
    android = ['Set up JDK 17','Set up Gradle','Configure side-by-side Marrow pilot APK',
               'Build debug APK','Restore production Android source identity','Verify packaged APK',
               'Verify packaged product contract','Write reproducibility manifest',
               'Verify packaged Marrow image bytes','Upload debug APK and build manifest']
    for name in android:
        assert 'workflow_dispatch' in steps[name].split('if: ', 1)[1].split('\n', 1)[0] and 'inputs.build_apk' in steps[name].split('if: ', 1)[1].split('\n', 1)[0], name
    for name in ['Verify packaged PWA product contract','Write PWA reproducibility manifest','Upload verified PWA artifact']:
        assert '        if:' not in steps[name], name
    assert 'name: V11.7-pwa' in steps['Upload verified PWA artifact']
    assert '--web-only' in steps['Write PWA reproducibility manifest']
    assert '--html build/web/index.html' in steps['Verify packaged PWA product contract']
    assert 'inputs.build_apk' not in steps['Deploy PWA preview to Cloudflare Pages']
    assert 'inputs.promote_production' in steps['Promote PWA to Cloudflare Pages production']
    approved = (ROOT/'.github/workflows/deploy-approved-main.yml').read_text()
    assert 'Build and verify PWA (optional APK)' in approved
    assert "'V11.7-pwa' || 'V11.7-android-pwa'" in approved
    assert 'tools/approved_release_artifact.py --release-sha' in approved
    assert "contains(github.event.workflow_run.head_commit.message, '[approved-production]')" in approved
    assert 'git ls-remote origin refs/heads/main' in approved
    print('WEB_FIRST_WORKFLOW_OK pushes=web_only dispatch_default=web_only android=explicit_opt_in production=guarded')


if __name__ == '__main__':
    main()
