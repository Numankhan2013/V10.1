#!/usr/bin/env python3
"""Late owner preserves existing routes and rejects an unrecognized duplicate."""
from pathlib import Path
from apply_interaction_polish_v1 import transform
ROOT=Path(__file__).resolve().parents[1]
def main():
    base='<head></head>\n/* NK_REFINED_ANALYSIS_V1_START */\n  window.addEventListener(\'hashchange\', () => { route = parseHash(); render(); });\n  window.QB={};'
    result=transform(base)
    assert transform(result)==result
    assert 'route = parseHash(); render(); });' not in result
    assert 'nkInteractionRender=render;' in result
    for marker in ['pointercancel','pointermove','prefers-reduced-motion','preventScroll','nkPolishSubmitted','nkPolishPanels']:
        assert marker in result,marker
    assert 'transition:none!important' in result
    assert 'node.animate(' not in result, 'shared polish must not animate route/question publication'
    assert 'transition:transform 110ms' in result
    assert 'background-color 110ms' not in result
    assert 'border-color 110ms' not in result
    assert 'box-shadow 110ms' not in result
    try:transform(base.replace('route = parseHash(); render();','unexpectedRouteOwner();'))
    except ValueError:pass
    else:raise AssertionError('unexpected route owner was silently removed')
    print('INTERACTION_POLISH_OWNER_OK')
if __name__=='__main__':main()
