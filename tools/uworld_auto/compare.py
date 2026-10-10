"""Score the extractor against an already hand-reviewed collection."""
import sys, json, glob, re, os
from difflib import SequenceMatcher
sys.path.insert(0, os.path.dirname(__file__))
from pdfpages import Doc
from extract import extract

def n(s): return re.sub(r'\s+', ' ', s or '').strip()
def sim(a, b): return SequenceMatcher(None, n(a), n(b), autojunk=False).ratio()

pdf, reviewed, first, last = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
gt = {}
for f in sorted(glob.glob(reviewed + '/batch-*.json')):
    for r in json.load(open(f))['records']:
        gt[r['id']] = r
res = extract(Doc(pdf), '', first, last)
stats = dict(q=0, missing=0, stem=0, opts=0, pct=0, correct=0, objective=0, prose=[], figs=[], verified=0)
bad = []
for d, issues, pages in res:
    if not d:
        print('FAIL', pages[:3], issues); continue
    g = gt.get(d['id'])
    if not g:
        stats['missing'] += 1; print('not in gt', d['id'], pages[:2]); continue
    stats['q'] += 1
    stats['verified'] += d['status'] == 'verified'
    s1 = sim(d['question'], g['question']); stats['stem'] += s1 > .97
    oo = [o['text'] for o in d['options']] == [o['text'] for o in g['options']]; stats['opts'] += oo
    stats['pct'] += [o['selection_percent'] for o in d['options']] == [o['selection_percent'] for o in g['options']]
    stats['correct'] += d['correct_label'] == g['correct_label']
    stats['objective'] += sim(d['educational_objective'], g.get('educational_objective', '')) > .95
    gp = ' '.join(x['text'] for x in g['explanation'] if x['type'] == 'paragraph')
    dp = ' '.join(x['text'] for x in d['explanation'] if x['type'] == 'paragraph')
    sp = sim(dp, gp); stats['prose'].append(sp)
    gf = sum(x['type'] in ('figure', 'table') for x in g['explanation'] + g['question_blocks'])
    df = sum(x['type'] == 'figure' for x in d['explanation'] + d['question_blocks'])
    stats['figs'].append((gf, df))
    if s1 < .97 or not oo or sp < .95 or gf != df or d['correct_label'] != g['correct_label']:
        bad.append((d['id'], round(s1, 3), oo, round(sp, 3), gf, df, d['issues'][:2]))
        if os.environ.get('V'):
            if not oo: print('  OPT', d['id'], [o['text'] for o in d['options']], '\n   GT', [o['text'] for o in g['options']])
            if d['correct_label'] != g['correct_label']: print('  ANS', d['id'], d['correct_label'], g['correct_label'])
            if sim(d['educational_objective'], g.get('educational_objective', '')) <= .95: print('  OBJ', d['id'], repr(d['educational_objective'][-160:]), '\n   GT', repr(g.get('educational_objective', '')[-160:]))
            if sp < .95:
                import difflib
                for op in difflib.SequenceMatcher(None, n(dp), n(gp), autojunk=False).get_opcodes():
                    if op[0] != 'equal' and (op[2]-op[1] > 15 or op[4]-op[3] > 15): print('  PROSE', d['id'], op[0], repr(n(dp)[op[1]:op[2]][:160]), '| GT', repr(n(gp)[op[3]:op[4]][:160]))
            if gf != df: print('  MEDIA', d['id'], [(x['type'], x.get('page'), x.get('bbox')) for x in g['question_blocks'] + g['explanation'] if x['type'] != 'paragraph'], '\n   GOT', [(x['role'], x['page'], x['bbox']) for x in d['question_blocks'] + d['explanation'] if x['type'] == 'figure'])
            for i in d['issues']:
                if i.startswith('suspicious'): print('  JUNK', d['id'], i)
q = stats['q']
print(f"questions {q} | stem {stats['stem']} | options {stats['opts']} | percents {stats['pct']} | correct {stats['correct']} | objective {stats['objective']} | auto-verified {stats['verified']}")
pr = stats['prose']; print('explanation prose similarity: mean %.3f, >=.98: %d, >=.95: %d' % (sum(pr) / len(pr), sum(x >= .98 for x in pr), sum(x >= .95 for x in pr)))
import collections;print(collections.Counter(re.sub(r'[:(].*','',i) for d,iss,_ in res if d for i in d['issues']));print('media count equal: %d / %d' % (sum(a == b for a, b in stats['figs']), len(stats['figs'])))
for b in bad[:25]: print(b)
