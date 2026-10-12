#!/usr/bin/env python3
"""Late owner preserves existing routes and ships without a duplicate route listener."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    result=(ROOT/'app/src/main/assets/index.html').read_text()
    css=(ROOT/'tools/interaction_polish.css').read_text();core=(ROOT/'tools/interaction_polish_core.js').read_text()
    style='<style id="nk-interaction-polish-v1">\n'+css+'\n</style>'
    assert result.count(style)==1 and result.index(style)<result.index('</head>')
    assert result.count(core)==1 and result.count('NK_INTERACTION_POLISH_V1_START')==1
    assert result.index('NK_REFINED_ANALYSIS_V1_START')<result.index(core)<result.index('  window.QB={')
    assert "window.addEventListener('hashchange', () => { route = parseHash(); render(); });" not in result
    assert result.count("window.addEventListener('hashchange', () => {\n    route = parseHash();\n    render();\n    resetScrollPosition();\n  });")==1,'one canonical route listener'
    assert 'nkInteractionRender=render;' in core
    for marker in ['pointercancel','pointermove','prefers-reduced-motion','preventScroll','nkPolishSubmitted','nkPolishPanels']:
        assert marker in core+css,marker
    assert 'transition:none!important' in css
    assert 'node.animate(' not in core, 'shared polish must not animate route/question publication'
    assert 'transition:transform 110ms' in css
    assert 'background-color 110ms' not in css
    assert 'border-color 110ms' not in css
    assert 'box-shadow 110ms' not in css
    print('INTERACTION_POLISH_OWNER_OK')
if __name__=='__main__':main()
