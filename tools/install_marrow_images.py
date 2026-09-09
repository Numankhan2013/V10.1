#!/usr/bin/env python3
"""Install explicit ID-based Marrow figures after the Marrow content transform."""
from pathlib import Path
from marrow_images import ROOT, release

def install():
    release(ROOT/'data/marrow/images/registry.json')
    assets=ROOT/'app/src/main/assets'
    path=assets/'index.html'
    html=path.read_text()
    marker='<!-- NK_MARROW_IMAGES_V1 -->'
    if marker not in html:
        anchor='<div class="question-text">'
        assert html.count(anchor)>=3, 'Question surfaces missing'
        html=html.replace(anchor,'<div class="question-text" data-marrow-question="${q.bank===\'Marrow\'?esc(String(q.id)):\'\'}">')
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
    viewer=assets/'source_visual_renderer.js'
    content=viewer.read_text()
    if 'window.NKSourceVisualViewer=viewer;' not in content:
        assert 'function stripLeakedReference(' in content
        content=content.replace('function stripLeakedReference(', 'window.NKSourceVisualViewer=viewer;\nfunction stripLeakedReference(',1)
        viewer.write_text(content)
    print('MARROW_IMAGE_INSTALL_OK')

if __name__=='__main__':install()
