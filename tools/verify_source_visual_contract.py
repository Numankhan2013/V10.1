from pathlib import Path
import hashlib
import json
import sys

ROOT = Path('app/src/main')
java = (ROOT / 'java/com/qbank/biochemistry/MainActivity.java').read_text(encoding='utf-8')
meta = ROOT / 'assets/source_visual_metadata.js'
report_file = ROOT / 'assets/source_visual_mapping_report.json'
inventory_file = ROOT / 'assets/source_visual_inventory.json'

checks = {
    'metadata contract': meta.exists(),
    'mapping report': report_file.exists(),
    'full visual inventory': inventory_file.exists(),
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

try:
    inventory = json.loads(inventory_file.read_text(encoding='utf-8'))
except Exception as exc:
    print('SOURCE VISUAL CONTRACT FAILED: invalid inventory:', exc)
    sys.exit(1)
items = inventory.get('items', [])
if inventory.get('schemaVersion') != 2 or inventory.get('visualCount') != len(items):
    print('SOURCE VISUAL CONTRACT FAILED: inventory schema/count mismatch')
    sys.exit(1)
if len(items) < sum(int(report[s]['mappedQuestions']) for s in required):
    print('SOURCE VISUAL CONTRACT FAILED: inventory omits mapped visuals')
    sys.exit(1)
required_fields = ('id','subject','questionId','sourcePdf','sourcePage','sourcePlacement','sourceComparisonCrop','extractionMethod','productionPath','productionWidth','productionHeight','productionSha256','riskFlags','reviewStatus','technicalChecks')
for item in items:
    missing = [field for field in required_fields if item.get(field) is None]
    if missing:
        print('SOURCE VISUAL CONTRACT FAILED: incomplete inventory item', item.get('id'), missing)
        sys.exit(1)
    if item['subject'] not in required or item['reviewStatus'] not in ('PENDING_MANUAL_REVIEW','PASS'):
        print('SOURCE VISUAL CONTRACT FAILED: invalid subject/review state', item.get('id'))
        sys.exit(1)
    if item['technicalChecks'].get('status') != 'PASS':
        print('SOURCE VISUAL CONTRACT FAILED: crop-safety gate did not pass', item.get('id'), item['technicalChecks'])
        sys.exit(1)
    asset = ROOT / 'assets' / item['productionPath']
    if not asset.is_file() or hashlib.sha256(asset.read_bytes()).hexdigest() != item['productionSha256']:
        print('SOURCE VISUAL CONTRACT FAILED: missing or changed production bytes', item.get('id'))
        sys.exit(1)
    if item['extractionMethod'] == 'native-jpeg-byte-copy' and item.get('sourceSha256') != item['productionSha256']:
        print('SOURCE VISUAL CONTRACT FAILED: native JPEG was not preserved byte-for-byte', item.get('id'))
        sys.exit(1)

generator = (Path('tools/build_source_visual_metadata.py')).read_text(encoding='utf-8')
quality_stage = (Path('tools/improve_source_visual_assets_v1.py')).read_text(encoding='utf-8')
for forbidden in ('crop_native_figure', 'Image.Resampling', 'LANCZOS', 'dominant_edge'):
    if forbidden in generator or forbidden in quality_stage:
        print('SOURCE VISUAL CONTRACT FAILED: destructive legacy transform remains:', forbidden)
        sys.exit(1)
pending = sum(item.get('reviewStatus') != 'PASS' for item in items)
if not inventory.get('reviewBatches') or inventory.get('technicalSummary', {}).get('manualReviewPending') != pending:
    print('SOURCE VISUAL CONTRACT FAILED: bounded manual-review batches missing')
    sys.exit(1)

print('SOURCE VISUAL CONTRACT PASSED:', ', '.join(checks))
print('SOURCE VISUAL MAPPING:', json.dumps(report, sort_keys=True, separators=(',', ':')))
print('SOURCE VISUAL AUDIT:', json.dumps(inventory.get('technicalSummary', {}), sort_keys=True, separators=(',', ':')))
