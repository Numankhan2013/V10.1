#!/usr/bin/env python3
"""Install the scoped visual identity layer after existing interaction owners."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / 'app/src/main/assets/index.html'
STYLE_ID = 'nk-visual-refinement-v1'


def transform(source):
    if f'id="{STYLE_ID}"' in source:
        return source
    if 'NK_INTERACTION_POLISH_V1_START' not in source:
        raise ValueError('Visual refinement must follow the final interaction owner')
    if source.count('</body>') != 1:
        raise ValueError('Expected one final body boundary')
    css = (ROOT / 'tools/visual_refinement.css').read_text()
    return source.replace('</body>', f'<style id="{STYLE_ID}">\n{css}\n</style>\n</body>', 1)


if __name__ == '__main__':
    HTML.write_text(transform(HTML.read_text()), encoding='utf-8')
    print('VISUAL_REFINEMENT_INSTALLED behavior=preserved identity=incumbent')
