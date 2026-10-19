#!/usr/bin/env python3
"""Correct reviewed OCR misreads and watermark text in auto-extracted collections.

  fix_ocr_text.py [<slug> ...] [--dry-run]     (no slug: every auto collection)

1. Whole-word misreads from a hand-reviewed list (l for I, rn for m, n for r,
   o for c, ...). Every entry was checked in context; real words that only look
   like misreads (court, rails, tailed, stories, ...) are deliberately absent.
2. Words the OCR split or garbled with punctuation ("overl oad", "Shige/la").
3. The "@UWorld" image watermark that OCR copied into prose and table cells.
Corrections are stored in reviewed/fixes.json so a re-extraction keeps them.
"""
import hashlib, json, re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent))
ROOT = HERE.parents[1]
from uworld_reviewed_document import record_hash
from uworld_content_hygiene import validate_display

WORDS = {
    'acetytglucosamine': 'acetylglucosamine', 'acetyimuramic': 'acetylmuramic', 'acidosiis': 'acidosis',
    'afbicans': 'albicans', 'alanyt': 'alanyl', 'aloohol': 'alcohol', 'Aminogiycoside': 'Aminoglycoside',
    'angiiotensin': 'angiotensin', 'antenior': 'anterior', 'Antigenie': 'Antigenic',
    'Aspergilfus': 'Aspergillus', 'Autosornal': 'Autosomal', 'bactena': 'bacteria', 'Bactena': 'Bacteria',
    'bactenal': 'bacterial', 'Barlonella': 'Bartonella', 'Bartonelfa': 'Bartonella', 'beoome': 'become',
    'biipolar': 'bipolar', 'bndge': 'bridge', 'bordenline': 'borderline', 'capsufatum': 'capsulatum',
    'catanrhal': 'catarrhal', 'ceflriaxone': 'ceftriaxone', 'coftriaxone': 'ceftriaxone',
    'cephalosponns': 'cephalosporins', 'charactenized': 'characterized', 'charactenstic': 'characteristic',
    'Choiice': 'Choice', 'chroniic': 'chronic', 'Closfridium': 'Clostridium', 'Clostndium': 'Clostridium',
    'Clostndioides': 'Clostridioides', 'cniteria': 'criteria', 'critenia': 'criteria', 'cntical': 'critical',
    'comeum': 'corneum', 'Comorbicl': 'Comorbid', 'cornorbid': 'comorbid', 'concunrent': 'concurrent',
    'Condytoma': 'Condyloma', 'Conoomitant': 'Concomitant', 'contnbuted': 'contributed',
    'Crypfosporidium': 'Cryptosporidium', 'dally': 'daily', 'deaves': 'cleaves', 'dianrhea': 'diarrhea',
    'dihydrofotic': 'dihydrofolic', 'diisorder': 'disorder', 'diphthenae': 'diphtheriae',
    'diphtheniae': 'diphtheriae', 'dnnks': 'drinks', 'duning': 'during', 'dusters': 'clusters',
    'elderty': 'elderly', 'Enterooocci': 'Enterococci', 'enterooocci': 'enterococci',
    'epleronone': 'eplerenone', 'Felic': 'Folic', 'fluiid': 'fluid', 'fonmation': 'formation',
    'fumigafus': 'fumigatus', 'Fusobacferium': 'Fusobacterium', 'gluoose': 'glucose', 'glutamyt': 'glutamyl',
    'glyoosylated': 'glycosylated', 'Haemophifus': 'Haemophilus', 'Henxheimer': 'Herxheimer',
    'Herpesvindae': 'Herpesviridae', 'hisfolytica': 'histolytica', 'histolyfica': 'histolytica',
    'Histopfasma': 'Histoplasma', 'Hyperparathyroidisrn': 'Hyperparathyroidism', 'immifis': 'immitis',
    'impainment': 'impairment', 'indudes': 'includes', 'induding': 'including',
    'inffammatory': 'inflammatory', 'inffuenzae': 'influenzae', 'inflammalion': 'inflammation',
    'intennal': 'internal', 'intennational': 'international', 'lchthyosis': 'Ichthyosis', 'llgase': 'ligase',
    'lliopsoas': 'Iliopsoas', 'llpoprotein': 'lipoprotein', 'lmatinib': 'Imatinib', 'lmipenem': 'Imipenem',
    'lmiquimod': 'Imiquimod', 'lmmunocompetent': 'Immunocompetent', 'lmmunocompromised': 'Immunocompromised',
    'lmmunofluorescent': 'Immunofluorescent', 'lmmunostaining': 'Immunostaining',
    'lmmunosuppressants': 'Immunosuppressants', 'lmmunosuppressed': 'Immunosuppressed',
    'lmmunosuppression': 'Immunosuppression', 'lmmunotherapy': 'Immunotherapy', 'lndomethacin': 'Indomethacin',
    'lnfliximab': 'Infliximab', 'lnfundibulopelvic': 'Infundibulopelvic', 'lnhalational': 'Inhalational',
    'lnhibin': 'Inhibin', 'lnspiratory': 'Inspiratory', 'lntegrase': 'Integrase', 'lntegrins': 'Integrins',
    'lnteralveolar': 'Interalveolar', 'lnteratrial': 'Interatrial', 'lntercellular': 'Intercellular',
    'lntercostal': 'Intercostal', 'lnterferon': 'Interferon', 'lnterventricular': 'Interventricular',
    'lntraabdominal': 'Intraabdominal', 'lntracranial': 'Intracranial', 'lntracytoplasmic': 'Intracytoplasmic',
    'lntradermal': 'Intradermal', 'lntraepidermal': 'Intraepidermal', 'lntraepithelial': 'Intraepithelial',
    'lntraerythrocytic': 'Intraerythrocytic', 'lntraluminal': 'Intraluminal', 'lntranuclear': 'Intranuclear',
    'lntravascular': 'Intravascular', 'lntussusception': 'Intussusception', 'lnvagination': 'Invagination',
    'lpsilateral': 'Ipsilateral', 'lsoleucine': 'Isoleucine', 'lsoproterenol': 'Isoproterenol',
    'lsosorbide': 'Isosorbide', 'lsospora': 'Isospora', 'jsospora': 'Isospora',
    'lsovolumetric': 'Isovolumetric', 'lvermectin': 'Ivermectin', 'maculopapufar': 'maculopapular',
    'Mafassezia': 'Malassezia', 'malnutnition': 'malnutrition', 'mannum': 'marinum',
    'meningifidis': 'meningitidis', 'minonty': 'minority', 'monitoning': 'monitoring',
    'monocytogeres': 'monocytogenes', 'multinucieated': 'multinucleated', 'nbosomal': 'ribosomal',
    'nbosylation': 'ribosylation', 'ribosytation': 'ribosylation', 'Neissena': 'Neisseria',
    'nephnitic': 'nephritic', 'Noelsen': 'Neelsen', 'nonheating': 'nonhealing', 'Nonmal': 'Normal',
    'nonmal': 'normal', 'NSAlDs': 'NSAIDs', 'oasts': 'casts', 'oolonize': 'colonize', 'oommon': 'common',
    'oompleted': 'completed', 'oomplicated': 'complicated', 'oomplication': 'complication',
    'oomposed': 'composed', 'oonsistent': 'consistent', 'oontaining': 'containing',
    'oontamination': 'contamination', 'oontext': 'context', 'oonverted': 'converted', 'ooryza': 'coryza',
    'oount': 'count', 'penitoneum': 'peritoneum', 'retropenitoneum': 'retroperitoneum',
    'penosteal': 'periosteal', 'penpheral': 'peripheral', 'Peptosfreptococcus': 'Peptostreptococcus',
    'perfnngens': 'perfringens', 'Pneumocysfis': 'Pneumocystis', 'pnmarily': 'primarily',
    'primanly': 'primarily', 'Postinfeotious': 'Postinfectious', 'potyproteins': 'polyproteins',
    'prescnbed': 'prescribed', 'propna': 'propria', 'prostacyctin': 'prostacyclin',
    'pyelonephntis': 'pyelonephritis', 'pyunia': 'pyuria', 'recessiive': 'recessive', 'reoeptor': 'receptor',
    'rhinonrhea': 'rhinorrhea', 'rnyocytes': 'myocytes', 'sarooidosis': 'sarcoidosis',
    'schenckil': 'schenckii', 'Sciera': 'Scleral', 'sderosis': 'sclerosis', 'sequenoe': 'sequence',
    'Serrafia': 'Serratia', 'shortor': 'shorter', 'slowty': 'slowly', 'sofium': 'solium',
    'specifiic': 'specific', 'Sporothnx': 'Sporothrix', 'staghom': 'staghorn', 'Stalins': 'Statins',
    'stenle': 'sterile', 'stenlized': 'sterilized', 'stenotio': 'stenotic', 'stnictures': 'strictures',
    'surgenes': 'surgeries', 'sutfamethoxazole': 'sulfamethoxazole', 'symmetnc': 'symmetric',
    'tendenness': 'tenderness', 'Throe': 'Three', 'Tnchophyton': 'Trichophyton', 'tniad': 'triad',
    'tnmester': 'trimester', 'tnphosphate': 'triphosphate', 'transcnbed': 'transcribed',
    'trimethopnm': 'trimethoprim', 'undine': 'uridine', 'unidine': 'uridine', 'Uninalysis': 'Urinalysis',
    'uninalysis': 'urinalysis', 'Unnalysis': 'Urinalysis', 'unine': 'urine', 'unvaccinatad': 'unvaccinated',
    'vermiculans': 'vermicularis', 'Ziohl': 'Ziehl',
}
PHRASES = [
    (r'\boverl oad', 'overload'), (r'\brefl ecting', 'reflecting'), (r'\bpulsa tile\b', 'pulsatile'),
    (r'\bcombina ion t\b', 'combination'), (r'\bShige/la\b', 'Shigella'), (r'\bScleral!', 'Scleral'), (r'\bschizo@affective\b', 'schizoaffective'),
]
WORD = re.compile(r'\b(' + '|'.join(map(re.escape, WORDS)) + r')\b')
# "@UWorld", "@ UWO<ld", "e uworld", "uwend", "@l/Wortd": no English word starts with "uw".
WATERMARK = re.compile(r'(?:(?<=\s)|^)(?:[@©�®]\s?Q?|e\s)?(?:[Uu][Ww][^\s"]*|l/W[^\s"]*)(?=\s|$)')


def clean(text):
    new = WORD.sub(lambda m: WORDS[m.group(1)], text)
    for pattern, repl in PHRASES:
        new = re.sub(pattern, repl, new)
    new = WATERMARK.sub('', new)
    return re.sub(r'  +', ' ', new).strip() if new != text else text


def clean_nodes(nodes):
    out = []
    for node in nodes:
        node = dict(node)
        if node['type'] == 'paragraph':
            node['text'] = clean(node['text'])
            if not node['text']:
                continue
        elif node['type'] == 'table':
            node['columns'] = [clean(c) for c in node['columns']]
            node['rows'] = [[clean(c) for c in row] for row in node['rows']]
        out.append(node)
    return out


def clean_doc(d):
    changed = {}
    for key, value in (('question', clean(d['question'])),
                       ('educational_objective', clean(d.get('educational_objective') or '') or d.get('educational_objective')),
                       ('options', [{**o, 'text': clean(o['text'])} for o in d['options']]),
                       ('question_blocks', clean_nodes(d.get('question_blocks', []))),
                       ('explanation', clean_nodes(d['explanation']))):
        if value != d.get(key, [] if key == 'question_blocks' else None):
            changed[key] = value
    return changed


def clean_row(row):
    row['question_text'] = clean(row['question_text'])
    row['correct_answer_text'] = clean(row['correct_answer_text'])
    for option in row['options']:
        option['text'] = clean(option['text'])
    exp = row['explanation']
    exp['text'] = '\n\n'.join(filter(None, (clean(p) for p in exp['text'].split('\n\n'))))
    if exp.get('educational_objective'):
        exp['educational_objective'] = clean(exp['educational_objective'])


def auto_slugs():
    for manifest in sorted((ROOT / 'data/uworld/prepared').glob('*/manifest.json')):
        if json.loads(manifest.read_text()).get('source_extraction_method') == 'uworld-auto-extract':
            yield manifest.parent.name


def main():
    dry = '--dry-run' in sys.argv
    for slug in [a for a in sys.argv[1:] if not a.startswith('--')] or list(auto_slugs()):
        src = ROOT / 'data/uworld/prepared' / slug
        manifest = json.loads((src / 'manifest.json').read_text())
        rows = [json.loads(l) for l in (src / 'normalized.jsonl').read_text().splitlines() if l.strip()]
        by_id = {r['question_id']: r for r in rows}
        data = {b: json.loads(b.read_text()) for b in sorted((src / 'reviewed').glob('batch-*.json'))}
        fixes_path = src / 'reviewed/fixes.json'
        fixes = json.loads(fixes_path.read_text()) if fixes_path.exists() else {}
        count = 0
        for batch in data.values():
            for d in batch['records']:
                changed = clean_doc(d)
                if not changed:
                    continue
                validate_display({**d, **changed})
                count += 1
                if dry:
                    print(' ', d['id'], ', '.join(changed)); continue
                d.update(changed)
                fixes.setdefault(d['id'], {}).update(changed)
                row = by_id[d['id']]
                clean_row(row)
                d['source_record_sha256'] = record_hash(row)
        print(slug, 'questions', count, '(dry run)' if dry else '')
        if dry or not count:
            continue
        raw = ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows).encode()
        (src / 'normalized.jsonl').write_bytes(raw)
        for b, batch in data.items():
            b.write_text(json.dumps(batch, ensure_ascii=False, indent=1))
        fixes_path.write_text(json.dumps(fixes, ensure_ascii=False, indent=1))
        manifest['jsonl_sha256'] = hashlib.sha256(raw).hexdigest()
        (src / 'manifest.json').write_text(json.dumps(manifest, indent=1))


if __name__ == '__main__':
    main()
