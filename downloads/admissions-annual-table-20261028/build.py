"""Change only the current admissions fee table into approved annual columns."""
from pathlib import Path
import hashlib,json
import fitz
B=Path(__file__).resolve().parent;R=B.parents[1];fitz.TOOLS.set_small_glyph_heights(True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipts=json.loads((B/'receipts.json').read_text());reading=fitz.open(R/next(x['path'] for x in receipts if x['label']=='admissions-photo'));w,h=reading[5].rect.width,reading[5].rect.height
local=fitz.Rect(192.75,263.25,552.75,527.25);panel=fitz.open(B/'panels/admissions.pdf');assert len(panel)==1
(B/'output').mkdir(exist_ok=True);outputs=[]
for item in receipts:
 source=R/item['path'];assert sha(source)==item['asset']['sha256'];doc=fitz.open(source)
 if item['kind']=='reading':pi,s,dx,dy=5,1,0,0
 else:
  faces=[pair for k in range(6) for pair in [(24-2*k,1+2*k),(2+2*k,23-2*k)]];pi,side=next((i,j) for i,pair in enumerate(faces) for j,n in enumerate(pair) if n==6)
  bleed=3*72/25.4;cw,ch=w-2*bleed,h-2*bleed;p=doc[pi];s=min(p.rect.width/2/cw,p.rect.height/ch);dx=side*p.rect.width/2+(p.rect.width/2-cw*s)/2-bleed*s;dy=(p.rect.height-ch*s)/2-bleed*s
 rect=fitz.Rect(dx+local.x0*s,dy+local.y0*s,dx+local.x1*s,dy+local.y1*s);area=rect+(-s,-2.5*s,s,s);page=doc[pi]
 page.add_redact_annot(area,fill=None,cross_out=False);page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE,graphics=0,text=0);page.draw_rect(area,color=None,fill=(1,1,1),overlay=True);page.show_pdf_page(rect,panel,0,keep_proportion=False,overlay=True)
 target=B/'output'/f'{item["label"]}-approved-annual-table-20261028.pdf';doc.save(target,garbage=0,deflate=True)
 outputs.append({'label':item['label'],'document':item['document'],'kind':item['kind'],'file':str(target.relative_to(R)),'sha256':sha(target),'bytes':target.stat().st_size,'pages':len(doc),'changed_page':pi+1,'table_rect_pt':list(rect),'changed_rect_pt':list(area),'source':{'file':item['path'],'id':item['asset']['id'],'revision':item['asset']['revision'],'sha256':item['asset']['sha256']}});print(item['label'],'built',flush=True)
(B/'build-proof.json').write_text(json.dumps({'date':'2026-10-28','columns':['費目','1年次','2年次'],'outputs':outputs,'release':False},ensure_ascii=False,indent=2)+'\n')
