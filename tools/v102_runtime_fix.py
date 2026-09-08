from pathlib import Path

INDEX = Path('app/src/main/assets/index.html')
BAD = "function subjectSourceNote(q){ const subj=q.subject||activeSubject; return subj==='Biochemistry' ? `${subjectSourceNote(q)}` : `<div class=\"small-muted\" style=\"margin-top:10px\">Source: ${esc(q.sourceRef||`${subj} · PDF page ${q.sourcePage||'—'}`)}</div>`; }"
GOOD = "function subjectSourceNote(q){ const subj=q.subject||activeSubject; return `<div class=\"small-muted\" style=\"margin-top:10px\">Source: ${esc(q.sourceRef||`${subj} · PDF page ${q.sourcePage||'—'}`)}</div>`; }"

text = INDEX.read_text(encoding='utf-8')
if text.count(BAD) != 1:
    raise SystemExit(f'Expected exactly one recursive subjectSourceNote, found {text.count(BAD)}')
INDEX.write_text(text.replace(BAD, GOOD), encoding='utf-8')
print('Fixed recursive subjectSourceNote() in index.html')
