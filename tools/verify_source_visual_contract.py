from pathlib import Path
import re, sys

ROOT = Path('app/src/main')
html = (ROOT / 'assets/index.html').read_text(encoding='utf-8')
java = (ROOT / 'java/com/qbank/biochemistry/MainActivity.java').read_text(encoding='utf-8')
meta = ROOT / 'assets/source_visual_metadata.js'

checks = {
    'metadata contract': meta.exists(),
    'anatomy PDF route': 'qbank.local/anatomy/pdf' in java,
    'physiology PDF route': 'qbank.local/physiology/pdf' in java,
    'question visual hook': bool(re.search(r'question[^\n]{0,120}visual|visual[^\n]{0,120}question', html, re.I)),
    'option visual hook': bool(re.search(r'option[^\n]{0,120}visual|visual[^\n]{0,120}option', html, re.I)),
    'source visual schema': 'SOURCE_VISUAL_SCHEMA' in html or 'source_visual_metadata.js' in html,
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    print('SOURCE VISUAL CONTRACT FAILED:', ', '.join(failed))
    sys.exit(1)
print('SOURCE VISUAL CONTRACT PASSED:', ', '.join(checks))
