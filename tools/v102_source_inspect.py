from pathlib import Path
import re

s=Path('app/src/main/assets/index.html').read_text(encoding='utf-8')
print('SIZE', len(s), 'LINES', s.count('\n')+1)
print('FUNCTIONS')
for m in re.finditer(r'function\s+([A-Za-z0-9_$]+)\s*\(', s):
    print(m.group(1))
print('REVIEW')
for m in re.finditer(r'Review Solutions|reviewTest|window\.QB|review-test/', s):
    print(s[max(0,m.start()-350):m.start()+650].replace('\n',' ')[:1100])
print('SELECTS')
for m in re.finditer(r'<select[^>]*>', s, re.I):
    print(s[max(0,m.start()-250):m.start()+1300].replace('\n',' ')[:1500])
print('TOPBAR')
for m in re.finditer(r'<[^>]*class="[^"]*topbar[^"]*"[^>]*>',s,re.I):
    print(m.group(0))
