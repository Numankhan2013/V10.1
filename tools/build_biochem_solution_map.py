from pathlib import Path
import json,re
import fitz

PDF=Path('app/src/main/assets/Biochemistry_QBank_Source.pdf')
DATA=Path('app/src/main/assets/qbank_data.js')
OUT=Path('app/src/main/assets/biochemistry_source_solution_map.js')

data=json.loads(DATA.read_text(encoding='utf-8').split('=',1)[1].rstrip(';'))
qs=data['questions']
doc=fitz.open(PDF)
markers=[]
for page_no,page in enumerate(doc,1):
    for block in page.get_text('blocks'):
        for m in re.finditer(r'Solution\s+for\s+Question\s+(\d+)\s*:',block[4],re.I):
            markers.append((page_no,float(block[1])))
if len(markers)!=len(qs):
    raise SystemExit(f'Expected {len(qs)} solution markers, found {len(markers)}')
items=[]
for i,q in enumerate(qs):
    p,y=markers[i]; nxt=markers[i+1] if i+1<len(markers) else None
    if nxt is None:
        seg=[{'page':p,'top':round(y,2)}]
    else:
        np,ny=nxt
        if np==p:
            seg=[{'page':p,'top':round(y,2),'bottom':round(ny,2)}]
        else:
            seg=[{'page':p,'top':round(y,2)}]
            for mid in range(p+1,np): seg.append({'page':mid})
            seg.append({'page':np,'bottom':round(ny,2)})
    items.append({'id':q['id'],'segments':seg})
OUT.write_text('window.BIOCHEM_SOURCE_SOLUTIONS='+json.dumps(items,separators=(',',':'))+';\n',encoding='utf-8')
print(f'Generated {OUT}: {len(items)} questions')
