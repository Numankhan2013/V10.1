from pathlib import Path
import json
import re

DATA_PREFIX = 'window.SUBJECT_QBANK_DATA='


def clean_physiology_explanation(text):
    x = str(text or '')

    # High-confidence PDF extraction repairs. These restore symbols that were
    # replaced by the black-square glyph without changing the supplied wording.
    replacements = [
        (r'HCO\s*3\s*■', 'HCO₃⁻'),
        (r'HCO■■', 'HCO₃⁻'),
        (r'NH4\s*■', 'NH₄⁺'),
        (r'Fe³■', 'Fe³⁺'),
        (r'Fe²■', 'Fe²⁺'),
        (r'Ca²■', 'Ca²⁺'),
        (r'Mg²■', 'Mg²⁺'),
        (r'H■CO■', 'H₂CO₃'),
        (r'PCO■', 'PCO₂'),
        (r'PO■', 'PO₂'),
        (r'FEV■', 'FEV₁'),
        (r'VO■', 'VO₂'),
        (r'DO■', 'DO₂'),
        (r'CO■', 'CO₂'),
        (r'O■', 'O₂'),
        (r'Na\s*■', 'Na⁺'),
        (r'K\s*■', 'K⁺'),
        (r'Cl\s*■', 'Cl⁻'),
        (r'H\s*■', 'H⁺'),
        (r'voltage■gated', 'voltage-gated'),
        (r'P=2T/r■', 'P=2T/r²'),
        (r'\[Na⁺\]inside■', '[Na⁺]inside'),
        (r'■-Actinin', 'α-Actinin'),
        (r'H2PO4■', 'H₂PO₄⁻'),
        (r'PO2■■', 'PO₂'),
        (r'PCO2■■', 'PCO₂'),
        (r'I■', 'I⁻'),
        (r'formula ■ does', 'formula does'),
        (r'■ total', 'R_total'),
        (r'\s+■\s+(?=(?:45|15)\b)', ' = '),
        (r'■ x 100', '4/5 x 100'),
        (r'■heart rate', '↑ heart rate'),
        (r'\bdi■erent\b', 'different'),
        (r'■4 atm', '4 atm'),
        (r'fine-tune sound vibrations■■', 'fine-tune sound vibrations.'),
    ]
    for pattern, repl in replacements:
        flags = re.I if pattern in (r'voltage■gated', r'\bdi■erent\b') else 0
        x = re.sub(pattern, repl, x, flags=flags)

    # A few fractions were represented by an isolated glyph in the source extraction.
    x = x.replace('reached ■ rd', 'reached ¾ of a')
    x = x.replace('remaining ■ rd', 'remaining ¼ of the')
    x = x.replace('transit time = ■ x 0.75', 'transit time = ¼ x 0.75')
    x = x.replace('Dissolved Gas■ /', 'Dissolved Gas /')

    # Normalize spacing without rewriting wording.
    x = re.sub(r'\s+([,.;:])', r'\1', x)
    x = re.sub(r'\s{2,}', ' ', x).strip()

    # The source data is flattened to one line. Turn its genuine bullet markers
    # and explicit section labels back into structural boundaries for the renderer.
    x = re.sub(r'\s*•\s*', '\n• ', x)
    labels = r'(Explanation|Mechanism|Key Point|Key Concept|Clinical Features|Diagnosis|Investigations|Treatment|Pathophysiology|Summary|Important|Note|Functions|Features|Definition|Location|Structure|Stimulus|Process|Reflex Pathway|Other options|Incorrect Options|Correct Option|Applications of the Nernst Equation|Limitations|Factors Influencing Blood Flow within vessels|Flow, Pressure, and Resistance Relationship)'
    x = re.sub(r'\s+(?=' + labels + r'\s*:)', '\n', x, flags=re.I)

    # Remove only duplicated heading labels; repeated table values such as
    # “Closed Closed” are deliberately left untouched.
    x = re.sub(
        r'\b(Function|Functions|Mechanism|Pathway|Definition|Location|Structure|Stimulus|Process|Features|Clinical Features|Investigations|Treatment|Summary|Important|Note)\s+\1\b',
        r'\1', x, flags=re.I,
    )
    return x


def clean_subject_file(path):
    p = Path(path)
    s = p.read_text(encoding='utf-8')
    start = s.find(DATA_PREFIX)
    if start < 0:
        raise SystemExit(f'{path}: SUBJECT_QBANK_DATA assignment not found')
    json_start = start + len(DATA_PREFIX)
    end = s.find('</script>', json_start)
    if end < 0:
        end = len(s)
    raw = s[json_start:end].strip()
    if raw.endswith(';'):
        raw = raw[:-1]
    data = json.loads(raw)
    physiology = next((x for x in data.get('subjects', []) if x.get('subject') == 'Physiology'), None)
    if not physiology:
        raise SystemExit(f'{path}: Physiology dataset not found')

    before = sum(
        sum((q.get(k) or '').count('■') for k in ('question', 'correctAnswerText', 'explanation'))
        + sum((o.get('text') or '').count('■') for o in q.get('options', []))
        for q in physiology.get('questions', [])
    )
    changed = 0
    for q in physiology.get('questions', []):
        old_ex = q.get('explanation') or ''
        new_ex = clean_physiology_explanation(old_ex)
        if new_ex != old_ex:
            q['explanation'] = new_ex
            changed += 1
        for key in ('question', 'correctAnswerText'):
            old = q.get(key) or ''
            new = clean_physiology_explanation(old).replace('\n', ' ')
            if new != old:
                q[key] = new
        for o in q.get('options', []):
            old = o.get('text') or ''
            new = clean_physiology_explanation(old).replace('\n', ' ')
            if new != old:
                o['text'] = new
    after = sum(
        sum((q.get(k) or '').count('■') for k in ('question', 'correctAnswerText', 'explanation'))
        + sum((o.get('text') or '').count('■') for o in q.get('options', []))
        for q in physiology.get('questions', [])
    )

    encoded = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    s = s[:json_start] + encoded + ';\n\n' + s[end:]

    # The current review renderer must use the established explanation renderer;
    # the old formatExplanation() symbol no longer exists after the v8 system.
    s = s.replace('${formatExplanation(q.explanation)}', '${renderExplanationText(q.explanation,q)}')
    p.write_text(s, encoding='utf-8')
    print(f'{path}: cleaned {changed} explanations; black squares {before}->{after}')


clean_subject_file('app/src/main/assets/index.html')
clean_subject_file('app/src/main/assets/subjects_qbank_data.js')
