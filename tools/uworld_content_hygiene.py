"""Fail closed on screenshot chrome or long page overlap in reviewed prose.

This validates display documents; it never rewrites medical text or sources.
"""
import re

CHROME = re.compile(
    r'Exhibit Display|Answered correctly|Collecting Statistics|Correct answer|'
    r'Block Time Elapsed|Time Spent|My Notebook|Flashcards|End Block|'
    r'https?://t\.me|alee\s+mme|Ela»|\[\s*\[\s*@|©U\w+', re.I)


def display_texts(doc):
    yield 'question', doc['question']
    yield 'objective', doc.get('educational_objective') or ''
    for option in doc['options']:
        yield 'option ' + option['letter'], option['text']
    for role in ('question_blocks', 'explanation'):
        for i, node in enumerate(doc.get(role, [])):
            if node['type'] == 'paragraph':
                yield f'{role} {i}', node['text']
            elif node['type'] == 'table':
                for j, row in enumerate([node['columns']] + node['rows']):
                    for k, cell in enumerate(row):
                        yield f'{role} {i} cell {j},{k}', cell


def validate_display(doc):
    for field, text in display_texts(doc):
        if CHROME.search(text):
            raise ValueError(f'UWorld screenshot text leaked: {doc["id"]} {field}')
    # A whole repeated sentence run across explanation paragraphs is generally
    # overlapping screenshots, not a second source argument. Source-specific
    # intentional repetition must be reviewed before relaxing this gate.
    seen = {}
    for i, node in enumerate(doc['explanation']):
        if node['type'] != 'paragraph':
            continue
        words = re.findall(r'\w+', node['text'].lower())
        for offset in range(len(words) - 31):
            run = tuple(words[offset:offset + 32])
            previous = seen.get(run)
            if previous is not None and (previous[0] != i or offset - previous[1] >= 32):
                raise ValueError('UWorld screenshot overlap leaked: ' + doc['id'])
            seen[run] = (i, offset)


def learner_question(question):
    """Keep the review contract and source identity, omit the extraction archive.

    Original JSONLs/page OCR remain immutable on disk. Shared-engine fallbacks
    and search receive reviewed prose instead of raw extraction text.
    """
    doc = question['uworldDocument']
    text = '\n\n'.join(n['text'] for n in doc['explanation'] if n['type'] == 'paragraph')
    full_question = ' '.join([doc['question']] + [n['text'] for n in doc.get('question_blocks', [])
                                               if n['type'] == 'paragraph'])
    question = {k: v for k, v in question.items() if k != 'uworldTranscript'}
    question.update(question=full_question, explanation=text,
                    uworldSource={
                        'question_id': question['id'], 'bank': 'UWorld',
                        'correct_option': doc['correct_label'],
                        'options': doc['options'], 'statistics': doc['statistics'],
                        'explanation': {'text': text, 'educational_objective': doc.get('educational_objective')},
                        'source': {'bank': 'UWorld', 'source_pages': doc['reviewed_pages'],
                                   'source_pdf_sha256': question['provenance']['sourcePdfSha256'],
                                   'source_record_sha256': doc['source_record_sha256']}})
    return question
