#!/usr/bin/env python3
"""Protect conservative optional OCR reading assistance, not primary content."""
import copy
import json
from pathlib import Path

from uworld_biochemistry import load_source
from uworld_source_text import collapse_exact_overlaps, remove_explicit_ui, source_transcript


def main():
    phrase = ' '.join('token' + str(index) for index in range(50))
    cleaned, audit = collapse_exact_overlaps('before ' + phrase + ' between ' + phrase + ' after')
    assert cleaned == 'before ' + phrase + ' between after'
    assert len(audit) == 1 and audit[0]['word_count'] == 50
    assert audit[0]['kept_word_sha256'] == audit[0]['normalized_word_sha256']
    assert collapse_exact_overlaps('short repeated phrase. short repeated phrase.')[0] == 'short repeated phrase. short repeated phrase.'
    # A changed scientific symbol or word forbids approximate de-duplication.
    changed = phrase.replace('token25', 'Na+')
    assert collapse_exact_overlaps(phrase + ' ' + changed)[1] == []
    assert collapse_exact_overlaps('Na+ decreases. Na− decreases.')[1] == []
    try:
        collapse_exact_overlaps(phrase, minimum=5)
        raise AssertionError('Unsafe short dedup accepted')
    except ValueError:
        pass
    manifest, records = load_source()
    frozen = copy.deepcopy(records)
    transcripts = [source_transcript(record) for record in records]
    assert records == frozen, 'Immutable source changed'
    assert len(transcripts) == 132 and len({t['question_id'] for t in transcripts}) == 132
    assert all(t['paragraphs'] and not t['authoritative'] for t in transcripts)
    assert all(t['status'] == 'ocr-pilot-display' and 'ocr-unverified' in t['flags'] for t in transcripts)
    for record, transcript in zip(records, transcripts):
        assert transcript['educational_objective'] == record['explanation']['educational_objective']
        assert transcript['source_pages'] == record['source']['source_pages']
        assert transcript['display_word_count'] <= transcript['original_word_count']
        for removal in transcript['removals']:
            if removal['kind'] == 'exact-overlap':
                assert removal['word_count'] >= 40
                assert removal['normalized_word_sha256'] == removal['kept_word_sha256']
        # Every remaining token must still occur, in order, in source after
        # explicit UI label removal. Scientific punctuation is not substituted.
        source_tokens = remove_explicit_ui(record['explanation']['text'])[0].split()
        display_tokens = ' '.join(transcript['paragraphs']).split()
        cursor = 0
        for token in display_tokens:
            while cursor < len(source_tokens) and source_tokens[cursor] != token:
                cursor += 1
            assert cursor < len(source_tokens), (record['question_id'], token)
            cursor += 1
    by_id = {t['question_id']: t for t in transcripts}
    assert by_id['uw2024_biochem_1486']['educational_objective'] is None
    assert 'educational-objective-unavailable-in-source' in by_id['uw2024_biochem_1486']['flags']
    first = by_id['uw2024_biochem_1756']
    assert first['paragraphs'][0].startswith('The two primary modes')
    assert len(first['paragraphs']) >= 7
    assert any('(Choice A)' in p for p in first['paragraphs'])
    print('UWORLD_OPTIONAL_TRANSCRIPT_TEST_OK', len(transcripts))


if __name__ == '__main__':
    main()
