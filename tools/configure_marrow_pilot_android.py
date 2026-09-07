#!/usr/bin/env python3
"""Make feature-branch Android artifact install alongside production NK QBank."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
GRADLE=ROOT/'app/build.gradle';MANIFEST=ROOT/'app/src/main/AndroidManifest.xml'
g=GRADLE.read_text();m=MANIFEST.read_text()
if 'applicationId "com.qbank.biochemistry"' not in g: raise SystemExit('Production applicationId anchor missing')
g=g.replace('applicationId "com.qbank.biochemistry"','applicationId "com.qbank.marrowpilot"',1)
if 'android:label="NK QBank"' not in m: raise SystemExit('Production app label anchor missing')
m=m.replace('android:label="NK QBank"','android:label="NK QBank · Marrow Pilot"',1)
GRADLE.write_text(g);MANIFEST.write_text(m)
print('MARROW_PILOT_ANDROID_OK applicationId=com.qbank.marrowpilot')
