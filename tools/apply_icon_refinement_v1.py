#!/usr/bin/env python3
"""Enrich the existing offline shared glyph factories after interaction owners."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT/'app/src/main/assets/index.html'
MARKER = 'NK_ICON_REFINEMENT_V1_START'


def transform(source):
    if MARKER in source:
        return source
    for anchor in ['NK_INTERACTION_POLISH_V1_END','  window.QB={','function nkSubjectGraphic(','function nkAnalysisIcon(']:
        if source.count(anchor) != 1:
            raise ValueError(f'Icon owner anchor mismatch: {anchor}')
    core = (ROOT/'tools/icon_refinement_core.js').read_text()
    return source.replace('  window.QB={',core+'\n  window.QB={',1)


if __name__ == '__main__':
    HTML.write_text(transform(HTML.read_text()),encoding='utf-8')
    print('ICON_REFINEMENT_INSTALLED shared_glyphs=layered action_ownership=preserved')
