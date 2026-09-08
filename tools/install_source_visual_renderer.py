#!/usr/bin/env python3
from pathlib import Path
p=Path('app/src/main/assets/index.html')
s=p.read_text(encoding='utf-8')
marker='<!-- NK_SOURCE_VISUALS_V11 -->'
if marker not in s:
    inject='''\n<!-- NK_SOURCE_VISUALS_V11 -->\n<script src="source_visual_metadata.js"></script>\n<script src="source_visual_renderer.js"></script>\n'''
    pos=s.lower().rfind('</body>')
    if pos<0: raise SystemExit('index.html has no </body>')
    s=s[:pos]+inject+s[pos:]
    p.write_text(s,encoding='utf-8')
    print('installed source visual renderer')
else:
    print('source visual renderer already installed')
