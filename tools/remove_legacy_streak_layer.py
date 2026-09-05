from pathlib import Path
import re

INDEX = Path('app/src/main/assets/index.html')
text = INDEX.read_text(encoding='utf-8')

# The V10.2 streak injector is a global runtime layer. Home V4 already has its
# own streak component, so keeping this injector creates duplicate/leaking UI.
patterns = [
    r'\s*<style\s+id=["\']v102-streak-layer["\'][^>]*>.*?</style>\s*',
    r'\s*<script\s+id=["\']v102-streak-layer-script["\'][^>]*>.*?</script>\s*',
]
for pattern in patterns:
    text, n = re.subn(pattern, '\n', text, count=1, flags=re.S | re.I)
    if n:
        print(f'Removed legacy streak layer: {n}')

if 'id="v102-streak-layer-script"' in text or "id='v102-streak-layer-script'" in text:
    raise SystemExit('Legacy streak injector still present after cleanup')
if 'id="v102-streak-layer"' in text or "id='v102-streak-layer'" in text:
    raise SystemExit('Legacy streak style still present after cleanup')

INDEX.write_text(text, encoding='utf-8')
print('Legacy streak layer removed; Home streak remains owned by the canonical Home composition.')
