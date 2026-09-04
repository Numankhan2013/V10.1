from pathlib import Path
import re
import subprocess
import tempfile

html = Path('app/src/main/assets/index.html').read_text(encoding='utf-8')
scripts = re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>', html, flags=re.S | re.I)
if not scripts:
    raise SystemExit('No inline JavaScript blocks found')

checked = 0
for i, body in enumerate(scripts, 1):
    if not body.strip():
        continue
    with tempfile.NamedTemporaryFile('w', suffix='.js', encoding='utf-8', delete=False) as f:
        f.write(body)
        path = f.name
    p = subprocess.run(['node', '--check', path], text=True, capture_output=True)
    if p.returncode:
        print(f'JavaScript syntax error in inline script #{i}')
        print(p.stderr)
        raise SystemExit(1)
    checked += 1

print(f'Generated JavaScript syntax guard passed: {checked} inline scripts checked.')
