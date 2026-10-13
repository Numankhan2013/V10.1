#!/usr/bin/env python3
"""Unit checks for tools/prune_unreachable_css.py."""
import tempfile
from pathlib import Path

from prune_unreachable_css import Pruner, Reachability, prune_build

SOURCE = """
<div class="card live">x</div>
<script>el.className = 'nk-step-' + n; el.classList.add(`nk-tone-${tone}`); el.id = 'panel';</script>
"""


def prune(css: str) -> str:
    return Pruner(Reachability(SOURCE)).prune(css)


def main() -> None:
    # Reachable rules, including runtime-joined names, stay byte for byte.
    kept = '.card{color:red}\n.nk-step-3 .live{x:1}\n#panel>.card{y:2}\n.nk-tone-good{z:3}'
    assert prune(kept) == kept
    # Unreachable rules go; an empty @media goes with them; @keyframes and @font-face are untouched.
    assert prune('.gone{a:1}.card{b:2}') == '.card{b:2}'
    assert prune('@media (max-width:9px){.gone{a:1}}.card{b:2}') == '.card{b:2}'
    assert prune('@media (max-width:9px){.gone{a:1}.card{b:2}}') == '@media (max-width:9px){.card{b:2}}'
    frames = '@keyframes gone{from{opacity:0}to{opacity:1}}@font-face{font-family:x;src:url(x.woff2)}'
    assert prune(frames) == frames
    # Only unreachable alternatives of a selector list are dropped.
    assert prune('.gone, .card ,#nope{c:3}') == '.card{c:3}'
    # Logical pseudo-classes and attribute values never make a rule unreachable.
    for css in ('.card:not(.gone){d:4}', '.card:is(.gone,.live){d:4}', 'html:has(.gone) .card{d:4}', '[class~="gone"] .card{d:4}'):
        assert prune(css) == css, css
    # Strings, comments and escapes are respected.
    tricky = '.card::after{content:"{.gone}"}/* .gone{a:1} */.sm\\:gone{e:5}'
    assert prune(tricky) == tricky
    # Nested @supports/@media and selectors in a comment between rules.
    assert prune('@supports (display:grid){@media print{.gone{a:1}}}.live{b:2}') == '.live{b:2}'
    # prune_build reads the whole build: names used only in another script stay.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / 'redesign').mkdir()
        (root / 'index.html').write_text('<style>.card{a:1}.only-js{b:2}.gone{c:3}</style><div class="card"></div>', encoding='utf-8')
        (root / 'app.js').write_text("node.classList.add('only-js')", encoding='utf-8')
        (root / 'redesign/x.css').write_text('.gone{a:1}.card{b:2}', encoding='utf-8')
        pruner = prune_build(root)
        assert (root / 'index.html').read_text(encoding='utf-8') == '<style>.card{a:1}.only-js{b:2}</style><div class="card"></div>'
        assert (root / 'redesign/x.css').read_text(encoding='utf-8') == '.card{b:2}'
        assert pruner.removed_rules == 2
    print('PRUNE_UNREACHABLE_CSS_TEST_OK')


if __name__ == '__main__':
    main()
