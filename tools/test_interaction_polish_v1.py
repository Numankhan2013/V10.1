#!/usr/bin/env python3
"""Late owner preserves existing routes and ships without a duplicate route listener."""
import re
from pathlib import Path
from app_page import css_section, app_source
ROOT=Path(__file__).resolve().parents[1]
def main():
    result=app_source()
    css=css_section('nk-interaction-polish-v1');core=(ROOT/'app/src/main/modules/interaction_polish.js').read_text()
    assert css and result.index('<link rel="stylesheet" href="app.css">')<result.index('</head>')
    assert result.count(core)==1 and result.count('NK_INTERACTION_POLISH_V1_START')==1
    assert result.index('NK_REFINED_ANALYSIS_V1_START')<result.index(core)<result.index('  window.QB={')
    assert "window.addEventListener('hashchange', () => { route = parseHash(); render(); });" not in result
    assert result.count("window.addEventListener('hashchange', () => {\n    route = parseHash();\n    render();\n    resetScrollPosition();\n  });")==1,'one canonical route listener'
    assert 'nkInteractionRender=render;' in core
    for marker in ['pointercancel','pointermove','prefers-reduced-motion','preventScroll','nkPolishSubmitted','nkPolishPanels']:
        assert marker in core+css,marker
    assert 'transition:none!important' in css
    assert 'node.animate(' not in core, 'shared polish must not animate route/question publication'
    assert 'transition:transform' not in css,'press must not ease movement'
    assert re.search(r':active[^{]*\{[^}]*transform:(?!none)',css) is None,'active states must not transform'
    assert 'background-color 110ms' not in css
    assert 'border-color 110ms' not in css
    assert 'box-shadow 110ms' not in css
    print('INTERACTION_POLISH_OWNER_OK')
if __name__=='__main__':main()
