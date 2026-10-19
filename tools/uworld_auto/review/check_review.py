#!/usr/bin/env python3
"""Check reviewer answers for one UWorld review batch (plain Python 3, no packages).

  python3 tools/uworld_auto/review/check_review.py data/uworld/review/batches/<batch>

Answers live in data/uworld/review/answers/<batch>/UWORLD_<id>.json, one per
question folder of the batch, in the format of INSTRUCTIONS.md (rescue batches
may add "question_figure_page"). Prints one line per problem; exit 1 if any.
"""
import json, re, sys
from pathlib import Path

KEYS = {'id', 'question', 'options', 'correct_label', 'answered_correctly_percent',
        'explanation_paragraphs', 'educational_objective', 'status', 'notes'}
UI = re.compile(r'Correct answer|Answered correctly|Time Spent|Question Id|Exhibit Display|\bPrevious\s+Next\b|\bNext\s+Mark\b', re.I)


def pct(v):
    return v is None or (isinstance(v, (int, float)) and not isinstance(v, bool) and 0 <= v <= 100)


def check(folder, answer):
    qid = folder.name
    if not answer.exists():
        return ['missing answer']
    try:
        r = json.loads(answer.read_text(encoding='utf-8'))
    except ValueError as e:
        return [f'not valid JSON: {e}']
    errs = []
    extra = set(r) - KEYS - {'question_figure_page'}
    if KEYS - set(r): errs.append(f'missing keys {sorted(KEYS - set(r))}')
    if extra: errs.append(f'unexpected keys {sorted(extra)}')
    if errs: return errs
    if r['id'] != qid: errs.append(f'id {r["id"]!r} is not the folder name')
    if r['status'] not in ('verified', 'blocked'): errs.append('status must be "verified" or "blocked"')
    if not isinstance(r['notes'], str) or not r['notes'].strip(): errs.append('notes: one line saying what you changed')
    opts = r['options'] if isinstance(r['options'], list) else []
    letters = [o.get('letter') for o in opts if isinstance(o, dict)]
    if len(letters) != len(r['options'] or []) or letters != list('ABCDEFGHIJKL')[:len(letters)]:
        errs.append('option letters must run A, B, C… in order')
    if r['correct_label'] not in letters: errs.append('correct_label is not one of the option letters')
    for o in opts:
        if set(o) - {'letter', 'text', 'selection_percent'}: errs.append(f'option {o.get("letter")}: unexpected keys')
        if not pct(o.get('selection_percent')): errs.append(f'option {o.get("letter")}: selection_percent must be 0-100 or null')
    if not pct(r['answered_correctly_percent']): errs.append('answered_correctly_percent must be 0-100 or null')
    paras = r['explanation_paragraphs']
    if not isinstance(paras, list) or not all(isinstance(p, str) for p in paras):
        errs.append('explanation_paragraphs must be a list of strings')
        paras = []
    if r['status'] == 'verified':
        if len(letters) < 2: errs.append('verified needs at least two options')
        if not str(r['question']).strip(): errs.append('verified needs the stem')
        if any(not str(o.get('text', '')).strip() for o in opts): errs.append('verified needs every option text')
        if not [p for p in paras if p.strip()]: errs.append('verified needs the explanation')
        if not str(r['educational_objective']).strip(): errs.append('verified needs the educational objective')
        for name, t in [('stem', r['question']), ('objective', r['educational_objective'])] + [('explanation', p) for p in paras]:
            if UI.search(str(t)): errs.append(f'{name} contains screen chrome ({UI.search(str(t)).group(0)!r})')
    fp = r.get('question_figure_page')
    if fp is not None:
        pages = {int(m.group(1)) for p in folder.glob('page-*.*') if (m := re.match(r'page-(\d+)', p.name))}
        if not (isinstance(fp, int) and fp in pages): errs.append(f'question_figure_page {fp!r} is not one of this folder\'s pages')
    return errs


def main():
    batch = Path(sys.argv[1])
    answers = batch.parents[1] / 'answers' / batch.name
    folders = sorted(p for p in batch.iterdir() if p.is_dir())
    bad = 0
    for f in folders:
        for e in check(f, answers / f'{f.name}.json'):
            print(f'{batch.name}/{f.name}: {e}'); bad += 1
    print(f'{batch.name}: {len(folders)} questions, {bad} problems')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
