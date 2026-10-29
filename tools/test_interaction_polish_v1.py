#!/usr/bin/env python3
"""Late owner preserves existing routes and ships without a duplicate route listener."""
import re
from pathlib import Path
from app_page import css_section, app_source, app_css
ROOT=Path(__file__).resolve().parents[1]
def main():
    result=app_source()
    css=css_section('nk-interaction-polish-v1');core=(ROOT/'app/src/main/modules/interaction_polish.js').read_text()
    assert css and result.index('<link rel="stylesheet" href="app.css">')<result.index('</head>')
    assert result.count(core)==1 and result.count('NK_INTERACTION_POLISH_V1_START')==1
    assert result.index('NK_REFINED_ANALYSIS_V1_START')<result.index(core)<result.index('  window.QB={')
    assert "window.addEventListener('hashchange', () => { route = parseHash(); render(); });" not in result
    assert result.count("window.addEventListener('hashchange', () => {")==1,'one canonical route listener'
    listener=result[result.index("window.addEventListener('hashchange'"):][:900]
    assert 'route = parseHash();\n    render();' in listener and 'resetScrollPosition()' in listener,'the route listener renders and resets scroll for new screens'
    assert 'nkInteractionRender=render;' in core
    for marker in ['pointercancel','pointermove','prefers-reduced-motion','preventScroll','nkPolishSubmitted','nkPolishPanels']:
        assert marker in core+css,marker
    assert 'transition:none!important' in css
    assert 'inset 0 0 0 9999px color-mix(in srgb, currentcolor 5%, transparent)' in css,'press must acknowledge with the instant ink layer'
    assert 'transition:box-shadow 180ms' in css,'a completed tap must melt the layer'
    assert '.nk-pressed{box-shadow:inset 0 0 0 9999px' in css,'the layer must ride the polish class'
    assert ':is(:active,.nk-pressed){box-shadow:inset 0 0 0 9999px' not in css,'never key the layer on sticky touch :active'
    assert 'nk-pressed-out' in core,'the melt lifecycle lives in the polish module'
    assert 'brightness(0.96)' not in app_css(),'press feedback never dims by filter alone'
    assert 'node.animate(' not in core, 'shared polish must not animate route/question publication'
    assert 'transition:transform' not in css,'press never animates transform; positioned controls must keep their place'
    assert re.search(r':active[^{]*\{[^}]*transform:(?!none)',css) is None,'active states must not transform'
    assert '.nk-pressed{scale:.97;' in css,'buttons settle to 97% while held (individual scale property)'
    assert 'scale 300ms cubic-bezier(.34,1.56,.64,1)' in css,'release springs back'
    assert re.search(r'prefers-reduced-motion:reduce\)\{[^@]*scale:none!important',css),'reduced motion keeps buttons still'
    assert re.search(r'\{[^}]*scale:(?!none)[^}]*\}',css.split('Press spring')[0]) is None,'only the press spring scales'
    feel=(ROOT/'app/src/main/assets/redesign/nk-feel.js').read_text()
    # The slide is a native animation and the period changes only when it has finished:
    # the recompute rebuilds the control, and starting it mid-slide made the pill jump.
    assert "pill.animate([{ transform: from }, { transform: to }]" in feel,'the segment pill must slide natively'
    assert "M.animate(pill" not in feel and "SPRING_PILL" not in feel,'no script-driven pill spring (it stalls while the page recomputes)'
    assert "slide.finished.then(commit, commit);" in feel,'change the period only after the slide'
    assert "slide.ready" not in feel and "live.from" not in feel,'no mid-slide recompute'
    assert 'background-color 110ms' not in css
    assert 'border-color 110ms' not in css
    assert 'box-shadow 110ms' not in css
    print('INTERACTION_POLISH_OWNER_OK')
if __name__=='__main__':main()
