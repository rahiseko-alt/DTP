from pathlib import Path
import json,re
import fitz
B=Path(__file__).resolve().parent;R=B.parents[1];spec=json.load(open(B/'patches.json'));notice=re.sub(r'\s+','',spec['notice']);proof=json.load(open(B/'build-proof.json'));counts={}
for o in proof['outputs']:
 d=fitz.open(R/o['file']);total=0
 for i,p in enumerate(d,1):
  found=re.sub(r'\s+','',p.get_text()).count(notice);expected=sum(r['pdf_page']==i for r in o['regions']);assert found==expected,(o['label'],i,found,expected);total+=found
 assert total==6;counts[o['label']]=total
v=json.load(open(B/'verification.json'));v['exact_approved_notice_count_each_pdf']=counts;v['notice_on_each_expected_page_or_face_only']=True;(B/'verification.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(counts,flush=True)
