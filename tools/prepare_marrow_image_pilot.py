#!/usr/bin/env python3
"""Reproducible first inspected original microscopy figure; no pixel processing."""
from marrow_images import DATA, ROOT, extract, sha, write_json

def main():
    if (DATA/'images/registry.json').exists():
        raise SystemExit('Pilot registry already exists; use review/stage commands to preserve existing QA.')
    extract('Biochemistry',10,19,DATA/'images/originals')
    digest='62a5d0ea810266a026e2eae163014e45496c313ad0f426c304a34cd7fe9a6956'
    original='data/marrow/images/originals/'+digest+'.jpg'
    record={'path':original,'sha256':digest,'width':720,'height':1218}
    assets=[{
        'id':'biochemistry-ch01-q023-microscopy','subject':'Biochemistry','kind':'medical',
        'source':{'file':'biochemistryed8.pdf','sha256':sha((DATA/'source_pdfs/biochemistryed8.pdf').read_bytes()),
                  'page':10,'xref':19,'region':[162,56,450,272]},
        'bindings':[{'questionId':'marrow__BIOCHEM_CH01_Q023','role':'question','order':1,
                     'alt':'Two source microscopy panels labelled a and b'}],
        'original':record,'production':record,'method':'native-jpeg-stream','status':'SOURCE_LIMITED',
        'qa':{'sourceCompared':True,'originalSha256':digest,'productionSha256':digest,'notes':'Inspected native xref 19 on source page 10: both panels a and b and their lettering preserved. Native JPEG bytes retained exactly. Lower panel shows source compression/posterization; no diagnostic pixels processed or recreated. Physical device review pending.'}
    }]
    for subject,page,xref,digest,name,qid,region in [
        ('Physiology',11,21,'fa647be99a1c86a886512e180a5100f22b486752dabb96ad624903f099d224e5','homeostasis','marrow__PHYS_CH01_Q002',[162,476,450,692]),
        ('Biochemistry',33,69,'031ee7297698de79e56af46f711381b1b34a8be947e25cf6511fc5e8f1eff890','enzyme-activity','marrow__BIOCHEM_CH02_Q009',[162,212,450,428])]:
        extract(subject,page,xref,DATA/'images/originals')
        filename='physiologyed8.pdf' if subject=='Physiology' else 'biochemistryed8.pdf'
        production='data/marrow/images/editable/'+name+'.svg'
        assets.append({'id':name,'subject':subject,'kind':'diagram',
          'source':{'file':filename,'sha256':sha((DATA/'source_pdfs'/filename).read_bytes()),'page':page,'xref':xref,'region':region},
          'bindings':[{'questionId':qid,'role':'explanation','order':1,'alt':'Source '+('homeostasis control diagram' if name=='homeostasis' else 'enzyme activity graph')}],
          'original':{'path':'data/marrow/images/originals/'+digest+'.jpg','sha256':digest},
          'production':{'path':production,'sha256':sha((ROOT/production).read_bytes()),'width':600,'height':450},
          'method':'svg-reconstruction','status':'REVIEW_REQUIRED',
          'qa':{'sourceCompared':False,'notes':'Geometry and all educational labels transcribed from inspected native image. Await rendered SVG comparison before release.'}})
    write_json(DATA/'images/registry.json',{'schemaVersion':1,'assets':assets})

if __name__=='__main__':main()
