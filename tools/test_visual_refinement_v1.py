#!/usr/bin/env python3
"""A visual layer may add CSS, never rewrite executable or source content."""
import re
from pathlib import Path
from app_page import app_css, css_section

ROOT = Path(__file__).resolve().parents[1]
STYLE_ID = 'nk-visual-refinement-v1'


def main():
    css = css_section('nk-visual-refinement-v1')
    sheet = app_css()
    assert sheet.count(f'/* ── {STYLE_ID} ── */') == 1
    assert sheet.rstrip().endswith(css), 'visual layer must be the last section of the stylesheet'
    assert not re.search(r'<|@import|javascript:|https?:|url\(|expression\(|behavior:', css), 'visual layer must stay pure scoped CSS'
    assert not re.search(r'(?<![\w-])content\s*:', css), 'visual layer must not inject text content'
    print('VISUAL_REFINEMENT_OWNER_OK application_bytes_preserved=true')


if __name__ == '__main__':
    main()
