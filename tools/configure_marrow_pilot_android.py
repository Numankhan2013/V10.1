#!/usr/bin/env python3
"""Switch feature-branch Android identity without changing the production identity."""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
GRADLE=ROOT/'app/build.gradle'
MANIFEST=ROOT/'app/src/main/AndroidManifest.xml'

g=GRADLE.read_text(encoding='utf-8')
m=MANIFEST.read_text(encoding='utf-8')
restore='--restore' in sys.argv

PROD_ID="applicationId 'com.qbank.biochemistry'"
PILOT_ID="applicationId 'com.qbank.marrowpilot'"
PROD_LABEL='android:label="NK QBank"'
PILOT_LABEL='android:label="NK QBank · Marrow Pilot"'

if restore:
    if PILOT_ID not in g:
        raise SystemExit('Pilot applicationId anchor missing')
    if PILOT_LABEL not in m:
        raise SystemExit('Pilot app label anchor missing')
    g=g.replace(PILOT_ID,PROD_ID,1)
    m=m.replace(PILOT_LABEL,PROD_LABEL,1)
    msg='MARROW_PILOT_ANDROID_RESTORED production source identity'
else:
    if PROD_ID not in g:
        raise SystemExit('Production applicationId anchor missing')
    if PROD_LABEL not in m:
        raise SystemExit('Production app label anchor missing')
    g=g.replace(PROD_ID,PILOT_ID,1)
    m=m.replace(PROD_LABEL,PILOT_LABEL,1)
    msg='MARROW_PILOT_ANDROID_OK applicationId=com.qbank.marrowpilot'

GRADLE.write_text(g,encoding='utf-8')
MANIFEST.write_text(m,encoding='utf-8')
print(msg)
