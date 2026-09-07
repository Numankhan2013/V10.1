#!/usr/bin/env python3
"""Switch feature-branch Android identity without changing the production identity."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
GRADLE=ROOT/'app/build.gradle';MANIFEST=ROOT/'app/src/main/AndroidManifest.xml'
g=GRADLE.read_text();m=MANIFEST.read_text()
restore='--restore' in sys.argv
if restore:
    if 'applicationId "com.qbank.marrowpilot"' not in g: raise SystemExit('Pilot applicationId anchor missing')
    if 'android:label="NK QBank · Marrow Pilot"' not in m: raise SystemExit('Pilot app label anchor missing')
    g=g.replace('applicationId "com.qbank.marrowpilot"','applicationId "com.qbank.biochemistry"',1)
    m=m.replace('android:label="NK QBank · Marrow Pilot"','android:label="NK QBank"',1)
    msg='MARROW_PILOT_ANDROID_RESTORED production source identity'
else:
    if 'applicationId "com.qbank.biochemistry"' not in g: raise SystemExit('Production applicationId anchor missing')
    if 'android:label="NK QBank"' not in m: raise SystemExit('Production app label anchor missing')
    g=g.replace('applicationId "com.qbank.biochemistry"','applicationId "com.qbank.marrowpilot"',1)
    m=m.replace('android:label="NK QBank"','android:label="NK QBank · Marrow Pilot"',1)
    msg='MARROW_PILOT_ANDROID_OK applicationId=com.qbank.marrowpilot'
GRADLE.write_text(g);MANIFEST.write_text(m)
print(msg)
