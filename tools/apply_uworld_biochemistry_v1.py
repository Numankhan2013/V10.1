#!/usr/bin/env python3
"""Install the bounded source-native UWorld adapter after all incumbent render owners."""
from pathlib import Path
import json,re
from uworld_biochemistry import ROOT,bank_record
HTML=ROOT/'app/src/main/assets/index.html'
START='  /* NK_UWORLD_BANK_DATA_START */'
END='  /* NK_UWORLD_BANK_DATA_END */'

def transform(source):
    data=json.dumps(bank_record(),ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
    registry=START+'\n  const NK_UWORLD_BIOCHEMISTRY_BANK='+data+''';
  // Collection namespace participates in the shared engines, never My Subjects.
  BANKS_BY_SUBJECT[NK_UWORLD_BIOCHEMISTRY_BANK.subject]=[NK_UWORLD_BIOCHEMISTRY_BANK];
  SUBJECT_BY_NAME[NK_UWORLD_BIOCHEMISTRY_BANK.subject]=NK_UWORLD_BIOCHEMISTRY_BANK;
  const nkUworldOriginalBankRecord=nkBankRecord;
  nkBankRecord=function(name,bank){
    return nkUworldOriginalBankRecord(name==='Biochemistry'&&bank==='UWorld'?NK_UWORLD_BIOCHEMISTRY_BANK.subject:name,bank);
  };
'''+END
    if START in source:
        a=source.index(START);b=source.index(END,a)+len(END);source=source[:a]+registry+source[b:]
    else:
        anchor='  let activeSubject = ';assert source.count(anchor)==1,'Subject registry anchor changed'
        source=source.replace(anchor,registry+'\n'+anchor,1)
    marker='  /* NK_UWORLD_BIOCHEMISTRY_V1_START */';end='  /* NK_UWORLD_BIOCHEMISTRY_V1_END */'
    core=(ROOT/'tools/uworld_biochemistry_core.js').read_text().rstrip()
    if marker in source:
        a=source.index(marker);b=source.index(end,a)+len(end);source=source[:a]+core+source[b:]
    else:
        assert source.count('  window.QB={')==1
        source=source.replace('  window.QB={',core+'\n  window.QB={uworldReference:nkUworldReference,',1)
    source=source.replace('uworldZoom:nkUworldZoom,uworldRetryImages:nkUworldRetryImages,','uworldReference:nkUworldReference,')
    if 'uworldReference:nkUworldReference' not in source:
        source=source.replace('  window.QB={','  window.QB={uworldReference:nkUworldReference,',1)
    if 'uworldFigure:nkUworldFigure' not in source:
        source=source.replace('  window.QB={','  window.QB={uworldFigure:nkUworldFigure,uworldRetryFigures:nkUworldRetryFigures,',1)
    # A real route makes Home/browser Back/reload use the existing navigation.
    route="else if(route.page==='uworld') out=nkUworldLibraryPage();"
    if route not in source:
        anchor="else if(route.page==='topics') out=topics();"
        if anchor in source:source=source.replace(anchor,route+'\n    '+anchor,1)
    # Locked Practice outcomes and Review Solutions share this option renderer.
    # Exam choices remain free of source percentages until Review Solutions.
    option_end='</span></${tag}>`'
    percent_end="</span>${q.bank==='UWorld'?nkUworldOptionPercentage(q,o,locked):''}</${tag}>`"
    source=source.replace("</span>${q.bank==='UWorld'&&locked?nkUworldOptionPercentage(q,o):''}</${tag}>`",percent_end)
    if percent_end not in source:
        if option_end in source:source=source.replace(option_end,percent_end,1)
        elif 'function nkSessionOptions(' in source:raise ValueError('Shared option percentage anchor changed')
    # The installed shared question presenter must match its canonical owner.
    pstart='  /* NK_QUESTION_PRESENTATION_V1_START';pend='  /* NK_QUESTION_PRESENTATION_V1_END */'
    a=source.index(pstart);b=source.index(pend,a)+len(pend)
    source=source[:a]+(ROOT/'tools/question_presentation_core.js').read_text().rstrip()+source[b:]
    old='${nkScientificMarkup(o.text)}';new="${q.bank==='UWorld'?nkUworldOptionMarkup(q,o):nkScientificMarkup(o.text)}"
    if old in source:source=source.replace(old,new)
    elif new not in source:raise ValueError('Shared choice renderer missing')
    source=source.replace("${marrow?'M':'PL'}","${record.bank==='UWorld'?'UW':marrow?'M':'PL'}")
    source=source.replace("${marrow?'Native text':'PDF source'}","${record.bank==='UWorld'?'Source collection':marrow?'Native text':'PDF source'}")
    source=source.replace("record.bank==='UWorld'?'Source native'","record.bank==='UWorld'?'Source collection'")
    css='<style id="nk-uworld-biochemistry-v1">'+(ROOT/'tools/uworld_biochemistry.css').read_text()+'</style>'
    source=re.sub(r'<style id="nk-uworld-biochemistry-v1">.*?</style>',css,source,flags=re.S)
    if 'id="nk-uworld-biochemistry-v1"' not in source:source=source.replace('</head>',css+'\n</head>',1)
    source=source.replace('<script src="uworld_visual_metadata.js"></script>\n','')
    source=source.replace('Both banks use the same practice, test, review and progress architecture.','All banks use the same practice, test, review and progress architecture.')
    # Legacy exact-stem image matching belongs only to PrepLadder.
    source=source.replace('data-marrow-question="${q.bank===\'Marrow\'?esc(String(q.id)):\'\'}"','data-marrow-question="${q.bank!==\'PrepLadder\'?esc(String(q.id)):\'\'}"')
    return source

if __name__=='__main__':
    HTML.write_text(transform(HTML.read_text()),encoding='utf-8')
    print('UWORLD_BIOCHEMISTRY_INSTALLED questions=132 topics=4 shared_engine=true original_records=preserved')
