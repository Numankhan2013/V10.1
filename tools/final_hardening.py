"""Map every Physiology and Anatomy question to its exact solution region in the source PDF.

Writes assets/subject_source_solution_maps.js; the app's source renderer reads it.
"""
from pathlib import Path
import json
import re
from verification_preflight import is_termux, pdf_preflight

if is_termux() and not pdf_preflight():
    raise SystemExit(0)

import fitz

DATA = Path('app/src/main/assets/subjects_qbank_data.js')
MAP = Path('app/src/main/assets/subject_source_solution_maps.js')


def question_ids(raw, subject):
    pat = re.compile(r'["\'](?:id|questionId)["\']\s*:\s*["\'](' + re.escape(subject) + r'-\d+-\d+)["\']')
    ids = pat.findall(raw)
    # Preserve order while removing accidental duplicate occurrences.
    out=[]; seen=set()
    for qid in ids:
        if qid not in seen:
            seen.add(qid); out.append(qid)
    return out


def build_map(pdf_path, ids, subject):
    doc = fitz.open(pdf_path)
    markers=[]
    for page_no, page in enumerate(doc, 1):
        for block in page.get_text('blocks'):
            text=block[4]
            for m in re.finditer(r'Solution\s+for\s+Question\s+(\d+)\s*:', text, re.I):
                markers.append((page_no, float(block[1]), int(m.group(1))))
    doc.close()
    if len(markers) != len(ids):
        raise SystemExit(f'{subject}: expected {len(ids)} solution markers, found {len(markers)}')
    items=[]
    for i,qid in enumerate(ids):
        p,y,_=markers[i]
        nxt=markers[i+1] if i+1<len(markers) else None
        if nxt is None:
            seg=[{'page':p,'top':round(y,2)}]
        else:
            np,ny,_=nxt
            if np==p:
                seg=[{'page':p,'top':round(y,2),'bottom':round(ny,2)}]
            else:
                seg=[{'page':p,'top':round(y,2)}]
                for mid in range(p+1,np): seg.append({'page':mid})
                seg.append({'page':np,'bottom':round(ny,2)})
        items.append({'id':qid,'segments':seg})
    return items

raw=DATA.read_text(encoding='utf-8')
result={}
for subject,pdf in [
    ('physiology', Path('app/src/main/assets/Physiology_QBank_Source.pdf')),
    ('anatomy', Path('app/src/main/assets/Anatomy_QBank_Source.pdf')),
]:
    if not pdf.exists():
        print(f'{subject}: source PDF absent; leaving that map empty')
        result[subject]=[]
        continue
    ids=question_ids(raw, subject)
    if not ids:
        raise SystemExit(f'{subject}: could not extract question IDs from subjects_qbank_data.js')
    result[subject]=build_map(pdf, ids, subject)
    print(f'{subject}: generated {len(result[subject])} exact solution mappings')

MAP.write_text('window.SUBJECT_SOURCE_SOLUTIONS='+json.dumps(result,separators=(',',':'))+';\n', encoding='utf-8')
