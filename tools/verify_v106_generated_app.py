from pathlib import Path

checks = [
    ('index.html', 'SOURCE_PDF_EXPLANATION_V18'),
    ('index.html', 'BIOCHEM_SOURCE_SOLUTIONS'),
    ('index.html', 'SUBJECT_SOURCE_SOLUTIONS'),
    ('index.html', 'anatomy-'),
    ('MainActivity.java', 'qbank.local/anatomy/pdf'),
    ('index.html', 'cbt-canonical-review'),
    ('index.html', 'v104-design-system'),
    ('index.html', 'v104-ui-runtime'),
    ('index.html', 'v104-1-polish'),
    ('index.html', 'v104-1-runtime'),
    ('index.html', 'v105-experience'),
    ('index.html', 'v105-runtime'),
    ('MainActivity.java', 'V10.6_NATIVE_SHELL'),
    ('MainActivity.java', 'ic_home_v106'),
    ('MainActivity.java', 'ic_practice_v106'),
    ('MainActivity.java', 'ic_tests_v106'),
    ('MainActivity.java', 'ic_backup_v106'),
    ('index.html', 'Backup & Restore'),
]
files = {
    'index.html': Path('app/src/main/assets/index.html'),
    'MainActivity.java': Path('app/src/main/java/com/qbank/biochemistry/MainActivity.java'),
}
for name, needle in checks:
    text = files[name].read_text(encoding='utf-8')
    if needle not in text:
        raise SystemExit(f'GENERATED APP CHECK FAILED: {name} is missing {needle!r}')
for name, needle in [('index.html', 'cbt-final-lock-v2'), ('index.html', 'cbt-final-lock-v3')]:
    text = files[name].read_text(encoding='utf-8')
    if needle in text:
        raise SystemExit(f'GENERATED APP CHECK FAILED: forbidden legacy marker {needle!r} remains')
required_files = [
    Path('app/src/main/assets/biochemistry_source_solution_map.js'),
    Path('app/src/main/assets/subject_source_solution_maps.js'),
    Path('app/src/main/assets/Biochemistry_QBank_Source.pdf'),
    Path('app/src/main/assets/Physiology_QBank_Source.pdf'),
    Path('app/src/main/assets/Anatomy_QBank_Source.pdf'),
]
for p in required_files:
    if not p.is_file() or p.stat().st_size == 0:
        raise SystemExit(f'GENERATED APP CHECK FAILED: missing/empty required asset {p}')
print('V10.6 generated-app verification passed: all required runtime markers and source assets are present; legacy CBT layers are absent.')
