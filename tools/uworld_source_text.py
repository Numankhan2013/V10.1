"""Optional, conservative reading aid for the immutable Biochemistry OCR.

This is not a source-faithfulness certification. Source diagrams and complete
question-by-question validation are deferred. It never manufactures sections, rationales, tables or medical copy.
Only explicit application labels and long *exact* screenshot repetitions may
be removed. Every removal remains auditable, and the original import is intact.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

MIN_EXACT_OVERLAP_WORDS = 40
NOTICE = (
    'OCR pilot. Scanning errors and flattened tables may remain. '
    'Diagrams and question-by-question validation will follow.'
)
# Complete, explicitly known screenshot labels only. Corrupt lookalikes and
# ambiguous words such as "Version" are left in place rather than guessed.
UI_LABELS = (
    ('exhibit_display', re.compile(r'\bExhibit Display\b')),
    ('time_spent', re.compile(r'\b(?:Time|Tnne|Tfflle|Tune) Spent\b')),
    ('answered_correctly', re.compile(r'\bAnswered correctly\b')),
    ('collecting_statistics', re.compile(r'\bCollecting Statistics\b')),
    ('explanation_tab', re.compile(r'\bExplanation\b')),
)
PARAGRAPH_BOUNDARY = re.compile(
    r'(?=\(Choice [A-H](?:\s*(?:,|and|&)\s*[A-H])*\))|'
    r'(?<![\d.])(?=\b[1-9]\.\s+[A-Z][a-z]+:)'
)
RESIDUAL_UI = re.compile(
    r'\b(?:Incorrect|Correct answer|Version|Exhibit|Display|Spent|Submit|'
    r'Question Id|My Notebook|Flashcards|Time Elapsed)\b'
)


def digest(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def remove_explicit_ui(text: str) -> tuple[str, list[dict]]:
    removals = []
    for name, pattern in UI_LABELS:
        matches = list(pattern.finditer(text))
        for match in matches:
            removals.append({'kind': 'ui-label', 'label': name,
                             'removed_sha256': digest(match.group()),
                             'character_count': len(match.group())})
        text = pattern.sub(' ', text)
    return text, removals


def collapse_exact_overlaps(text: str, minimum: int = MIN_EXACT_OVERLAP_WORDS) -> tuple[str, list[dict]]:
    """Keep the earlier copy of long, byte-identical word runs.

    Case, punctuation, symbols and hyphenation participate in equality. No
    approximate matching, token substitution, medical inference or short
    repeated conclusion removal is permitted. This is an optional OCR reading
    aid because even a long source repetition can be deliberate.
    """
    if minimum < MIN_EXACT_OVERLAP_WORDS:
        raise ValueError('Short phrase de-duplication is not source-safe')
    removals = []
    while True:
        words = list(re.finditer(r'\S+', text))
        values = [word.group() for word in words]
        seen = {}
        best = None
        for later in range(len(values) - minimum + 1):
            key = tuple(values[later:later + minimum])
            earlier = seen.get(key)
            if earlier is None:
                seen[key] = later
                continue
            if later - earlier < minimum:
                continue
            length = minimum
            while (later + length < len(values) and earlier + length < later
                   and values[earlier + length] == values[later + length]):
                length += 1
            if best is None or length > best[2]:
                best = (earlier, later, length)
        if best is None:
            break
        earlier, later, length = best
        start, end = words[later].start(), words[later + length - 1].end()
        exact_words = ' '.join(values[later:later + length])
        earlier_words = ' '.join(values[earlier:earlier + length])
        assert exact_words == earlier_words
        removals.append({'kind': 'exact-overlap', 'word_count': length,
                         'removed_sha256': digest(text[start:end]),
                         'normalized_word_sha256': digest(exact_words),
                         'kept_word_sha256': digest(earlier_words)})
        text = text[:start] + ' ' + text[end:]
    return re.sub(r'\s+', ' ', text).strip(), removals


def source_transcript(record: dict) -> dict:
    """Return a source-linked optional transcript; never alter ``record``."""
    if record.get('subject') != 'Biochemistry' or record.get('source', {}).get('bank') != 'UWorld':
        raise ValueError('The source-text pilot is Biochemistry UWorld only')
    original = record['explanation']['text']
    text, ui = remove_explicit_ui(original)
    text, overlap = collapse_exact_overlaps(text)
    # Remove a leading screenshot statistic only when the prefix contains no
    # possible medical word. Preserve all scientific prose and record the removal.
    lead = re.search(r'(?<!\S)[A-Za-z]{2,}', text)
    if lead and 0 < lead.start() <= 160 and '%' in text[:lead.start()] and not re.search(r'[A-Za-z]{2,}',text[:lead.start()]):
        prefix=text[:lead.start()]
        ui.append({'kind':'ui-label','label':'leading-statistic','removed_sha256':digest(prefix),'character_count':len(prefix)})
        text=text[lead.start():]
    paragraphs = []
    for part in PARAGRAPH_BOUNDARY.split(text):
        # Whitespace-only reading breaks at full sentences; no summary or rewrite.
        part=part.strip()
        while len(part)>650:
            boundary=re.search(r'(?<=[.!?]) (?=[A-Z][a-z])',part[280:])
            if not boundary:break
            cut=280+boundary.start()+1
            paragraphs.append(part[:cut].strip());part=part[cut:].strip()
        if part:paragraphs.append(part)
    flags = ['ocr-unverified', 'visual-material-not-transcribed']
    if RESIDUAL_UI.search(text):
        flags.append('residual-ui-or-scanning-fragments')
    objective = record['explanation'].get('educational_objective')
    if not objective:
        flags.append('educational-objective-unavailable-in-source')
    return {
        'schema_version': 1,
        'question_id': record['question_id'],
        'status': 'ocr-pilot-display',
        'authoritative': False,
        'notice': NOTICE,
        'source_text_sha256': digest(original),
        'source_pages': list(record['source']['source_pages']),
        'paragraphs': paragraphs,
        'educational_objective': objective,
        'flags': flags,
        'removals': ui + overlap,
        'original_word_count': len(original.split()),
        'display_word_count': len(text.split()),
    }


def main() -> None:
    import argparse
    from uworld_biochemistry import load_source
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audit-output', type=Path, required=True)
    args = parser.parse_args()
    manifest, records = load_source()
    transcripts = [source_transcript(record) for record in records]
    audit = {'schema_version': 1, 'source_sha256': manifest['source_sha256'],
             'record_count': len(transcripts), 'authoritative': False,
             'questions': {entry['question_id']: entry for entry in transcripts}}
    args.audit_output.parent.mkdir(parents=True, exist_ok=True)
    args.audit_output.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n')
    print('UWORLD_OPTIONAL_TRANSCRIPT_AUDIT_OK', len(transcripts))


if __name__ == '__main__':
    main()
