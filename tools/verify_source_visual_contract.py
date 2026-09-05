from pathlib import Path
import json
import sys

ROOT = Path('app/src/main')
java = (ROOT / 'java/com/qbank/biochemistry/MainActivity.java').read_text(encoding='utf-8')
meta = ROOT / 'assets/source_visual_metadata.js'
report_file = ROOT / 'assets/source_visual_mapping_report.json'

checks = {
    'metadata contract': meta.exists(),
    'mapping report': report_file.exists(),
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

try:
    report = json.loads(report_file.read_text(encoding='utf-8'))
except Exception as exc:
    print('SOURCE VISUAL CONTRACT FAILED: invalid mapping report:', exc)
    sys.exit(1)

required = ('Anatomy', 'Physiology', 'Biochemistry')
for subject in required:
    row = report.get(subject, {})
    if int(row.get('mappedQuestions', 0)) < 10:
        print('SOURCE VISUAL CONTRACT FAILED: too few mapped questions for', subject, row)
        sys.exit(1)
    if int(row.get('imageBlocksAccepted', 0)) < int(row.get('mappedQuestions', 0)):
        print('SOURCE VISUAL CONTRACT FAILED: accepted image-block count is inconsistent for', subject, row)
        sys.exit(1)

print('SOURCE VISUAL CONTRACT PASSED:', ', '.join(checks))
print('SOURCE VISUAL MAPPING:', json.dumps(report, sort_keys=True, separators=(',', ':')))
