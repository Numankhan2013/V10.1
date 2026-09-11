#!/usr/bin/env python3
"""Install explicit ID-based Marrow figures after the Marrow content transform.

The generated question UI can arrive here in a mixed state: upstream transforms
may already have attached the Marrow question binding to one or more question
surfaces. Treat those pre-bound surfaces as valid and bind only the remaining
raw surfaces. This keeps the installer idempotent and prevents unrelated UI
work from breaking the image pipeline merely by running earlier in the build.
"""
from pathlib import Path
from marrow_images import ROOT, release
from apply_canonical_bank_explanation_wiring_v1 import install as install_canonical_wiring

QUESTION_RAW = '<div class="question-text">'
QUESTION_BOUND = '<div class="question-text" data-marrow-question="${q.bank===\'Marrow\'?esc(String(q.id)):\'\'}">'
MIN_QUESTION_SURFACES = 3


def install():
    # The Marrow transform has now created the shared bank registry and learner
    # explanation renderer. Repair the canonical two-bank Home routing and graft
    # every approved explanation into that runtime before images wrap the same
    # question/explanation surfaces.
    install_canonical_wiring()
    release(ROOT/'data/marrow/images/registry.json')
    assets=ROOT/'app/src/main/assets'
    path=assets/'index.html'
    html=path.read_text()
    marker='<!-- NK_MARROW_IMAGES_V1 -->'
    if marker not in html:
        raw_count=html.count(QUESTION_RAW)
        bound_count=html.count(QUESTION_BOUND)
        assert raw_count+bound_count>=MIN_QUESTION_SURFACES, (
            f'Question surfaces missing: raw={raw_count} prebound={bound_count}'
        )
        if raw_count:
            html=html.replace(QUESTION_RAW,QUESTION_BOUND)
        final_bound_count=html.count(QUESTION_BOUND)
        assert final_bound_count>=MIN_QUESTION_SURFACES, (
            f'Marrow question bindings incomplete: bound={final_bound_count}'
        )

        anchor='  function nkRenderMarrowExplanation(q){'
        assert html.count(anchor)==1
        html=html.replace(anchor,'  function nkRenderMarrowExplanationContent(q){',1)
        wrapper='''  function nkRenderMarrowExplanation(q){
    return '<div data-marrow-explanation="'+esc(String(q.id))+'">'+nkRenderMarrowExplanationContent(q)+'</div>';
  }
'''
        html=html.replace('  function nkRenderMarrowExplanationContent(q){',wrapper+'  function nkRenderMarrowExplanationContent(q){',1)
        html=html.replace('</head>',marker+'\n<script defer src="marrow_visual_metadata.js"></script>\n<script defer src="marrow_visual_renderer.js"></script>\n</head>',1)
        path.write_text(html)
        print(f'MARROW_QUESTION_BINDINGS_OK raw={raw_count} prebound={bound_count} final={final_bound_count}')
    viewer=assets/'source_visual_renderer.js'
    content=viewer.read_text()
    if 'window.NKSourceVisualViewer=viewer;' not in content:
        assert 'function stripLeakedReference(' in content
        content=content.replace('function stripLeakedReference(', 'window.NKSourceVisualViewer=viewer;\nfunction stripLeakedReference(',1)
        viewer.write_text(content)
    # The legacy stem matcher must not attach a PrepLadder image to Marrow.
    anchor='if(!qt)return;stripLeakedReference(qt);'
    guard="if(!qt)return;if(qt.getAttribute('data-marrow-question')){mounted.add(card);return;}stripLeakedReference(qt);"
    if guard not in content:
        assert anchor in content, 'Legacy image mount anchor missing'
        content=content.replace(anchor,guard,1)
        viewer.write_text(content)
    print('MARROW_IMAGE_INSTALL_OK')

if __name__=='__main__':install()
