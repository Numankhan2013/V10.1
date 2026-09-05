from pathlib import Path
import sys

ROOT = Path('app/src/main')
java = (ROOT / 'java/com/qbank/biochemistry/MainActivity.java').read_text(encoding='utf-8')
meta = ROOT / 'assets/source_visual_metadata.js'

checks = {
    'metadata contract': meta.exists(),
    'anatomy PDF route': 'qbank.local/anatomy/pdf' in java,
    'physiology PDF route': 'qbank.local/physiology/pdf' in java,
    'biochemistry PDF asset': (ROOT / 'assets/Biochemistry_QBank_Source.pdf').exists(),
    'physiology PDF asset': (ROOT / 'assets/Physiology_QBank_Source.pdf').exists(),
    'anatomy PDF asset': (ROOT / 'assets/Anatomy_QBank_Source.pdf').exists(),
}
failed = [name for name, ok in checks.items() if not ok]
if failed:
    print('SOURCE VISUAL CONTRACT FAILED:', ', '.join(failed))
    sys.exit(1)
print('SOURCE VISUAL CONTRACT PASSED:', ', '.join(checks))
