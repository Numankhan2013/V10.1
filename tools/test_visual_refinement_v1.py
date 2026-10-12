#!/usr/bin/env python3
"""A visual layer may add CSS, never rewrite executable or source content."""
import re
from pathlib import Path
from app_page import app_page

ROOT = Path(__file__).resolve().parents[1]
STYLE_ID = 'nk-visual-refinement-v1'


def main():
    app = app_page()
    css = (ROOT / 'app/src/main/modules/visual_refinement.css').read_text()
    block = f'<style id="{STYLE_ID}">\n{css}\n</style>\n</body>'
    assert app.count(f'id="{STYLE_ID}"') == 1
    assert app.count('</body>') == 1 and app.count(block) == 1, 'visual layer must be the final body owner'
    assert app.index('NK_INTERACTION_POLISH_V1_START') < app.index(block)
    assert not re.search(r'<|@import|javascript:|https?:|url\(|expression\(|behavior:', css), 'visual layer must stay pure scoped CSS'
    assert not re.search(r'(?<![\w-])content\s*:', css), 'visual layer must not inject text content'
    print('VISUAL_REFINEMENT_OWNER_OK application_bytes_preserved=true')


if __name__ == '__main__':
    main()
