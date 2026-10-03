#!/usr/bin/env python3
"""A visual layer may add CSS, never rewrite executable or source content."""
import re
from apply_visual_refinement_v1 import transform, STYLE_ID


def main():
    source = '''<html><head><style>.source{color:red}</style></head><body>
    <script>/* NK_INTERACTION_POLISH_V1_START */ const saved={answer:2};</script>
    <figure data-source="original"><img src="source_visuals/one.png"></figure>
    <button onclick="QB.selectPractice('q',2)">Answer</button></body></html>'''
    result = transform(source)
    assert transform(result) == result
    assert result.count(f'id="{STYLE_ID}"') == 1
    restored = re.sub(rf'<style id="{STYLE_ID}">.*?</style>\n', '', result, flags=re.S)
    assert restored == source, 'visual owner changed existing content or logic'
    for broken in [source.replace('NK_INTERACTION_POLISH_V1_START','OLD_OWNER'), source.replace('</body>',''), source+'</body>']:
        try:
            transform(broken)
        except ValueError:
            pass
        else:
            raise AssertionError('unexpected pipeline shape accepted')
    print('VISUAL_REFINEMENT_OWNER_OK application_bytes_preserved=true')


if __name__ == '__main__':
    main()
