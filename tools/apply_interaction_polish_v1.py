#!/usr/bin/env python3
"""Install shared interaction feedback after all screen owners."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/'app/src/main/assets/index.html'

def transform(source):
    if 'NK_INTERACTION_POLISH_V1_START' in source:return source
    if 'NK_REFINED_ANALYSIS_V1_START' not in source:raise ValueError('Interaction polish must follow analysis')
    # Legacy route listeners rendered the same destination twice. The first
    # listener already parses, renders and resets scroll; retain it unchanged.
    duplicate="  window.addEventListener('hashchange', () => { route = parseHash(); render(); });"
    if source.count(duplicate)!=1:raise ValueError('Expected one redundant route listener')
    source=source.replace(duplicate,'',1)
    source=source.replace('</head>','<style id="nk-interaction-polish-v1">\n'+(ROOT/'tools/interaction_polish.css').read_text()+'\n</style>\n</head>',1)
    return source.replace('  window.QB={',(ROOT/'tools/interaction_polish_core.js').read_text()+'\n  window.QB={',1)

if __name__=='__main__':
    HTML.write_text(transform(HTML.read_text()))
    print('INTERACTION_POLISH_INSTALLED immediate_press=true stable_question=true')
