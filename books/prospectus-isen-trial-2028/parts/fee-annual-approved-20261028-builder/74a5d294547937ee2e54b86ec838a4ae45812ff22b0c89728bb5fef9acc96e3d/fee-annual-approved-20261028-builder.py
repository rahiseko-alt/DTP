"""Replace the fee blocks on reading pages 12 and 13 of each current brochure PDF."""
from pathlib import Path
import hashlib,json
import fitz
B=Path(__file__).resolve().parent;R=B.parents[1];fitz.TOOLS.set_small_glyph_heights(True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipts=json.loads((B/'receipts.json').read_text());reading=fitz.open(R/next(x['path'] for x in receipts if x['label']=='brochure-original'));w,h=reading[12].rect.width,reading[12].rect.height
blocks={12:fitz.Rect(31.416460037,190,564.50213623,434.475006),13:fitz.Rect(31.416460037,347,564.50213623,643.955017)};panels={pn:fitz.open(B/f'panels/page{pn}.pdf') for pn in blocks};faces=[pair for k in range(4) for pair in [(16-2*k,1+2*k),(2+2*k,15-2*k)]]
assert all(len(p)==1 for p in panels.values()),'fee panel must be exactly one page'
(B/'output').mkdir(exist_ok=True);outputs=[]
for item in receipts:
 source=R/item['path'];assert sha(source)==item['asset']['sha256'];doc=fitz.open(source);regions=[]
 for pn,local in blocks.items():
  if item['kind'] in ['reading','master']:pi,s,dx,dy=pn-1,1,0,0
  else:
   pi,side=next((i,j) for i,pair in enumerate(faces) for j,n in enumerate(pair) if n==pn);p=doc[pi];s=min(p.rect.width/2/w,p.rect.height/h);dx=side*p.rect.width/2+(p.rect.width/2-w*s)/2;dy=(p.rect.height-h*s)/2
  rect=fitz.Rect(dx+local.x0*s,dy+local.y0*s,dx+local.x1*s,dy+local.y1*s);area=rect+(-s,-s,s,s);page=doc[pi]
  page.add_redact_annot(area,fill=None,cross_out=False);page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE,graphics=0,text=0);page.draw_rect(area,color=None,fill=(1,1,1),overlay=True);page.show_pdf_page(rect,panels[pn],0,keep_proportion=False,overlay=True)
  tableheight=local.height-31-6-53.308624-1;table=fitz.Rect(rect.x0,rect.y0+31*s,rect.x1,rect.y0+(31+tableheight)*s)
  regions.append({'reading_page':pn,'pdf_page':pi+1,'rect_pt':list(rect),'changed_rect_pt':list(area),'table_rect_pt':list(table),'scale':s,'offset':[dx,dy]})
 target=B/'output'/f'{item["label"]}-approved-annual-table-20261028.pdf';doc.save(target,garbage=0,deflate=True)
 outputs.append({'label':item['label'],'document':item['document'],'kind':item['kind'],'file':str(target.relative_to(R)),'sha256':sha(target),'bytes':target.stat().st_size,'pages':len(doc),'regions':regions,'source':{'file':item['path'],'id':item['asset']['id'],'revision':item['asset']['revision'],'sha256':item['asset']['sha256']}});print(item['label'],'built',flush=True)
(B/'build-proof.json').write_text(json.dumps({'date':'2026-10-28','columns':['費目','1年次','2年次'],'note':'上記金額には検定料2万円は含みません。','facts_sha256':sha(R/'company-data/facts/admissions.yaml'),'display_data_sha256':sha(R/'company-data/facts/booklet.yaml'),'outputs':outputs,'release':False},ensure_ascii=False,indent=2)+'\n')
