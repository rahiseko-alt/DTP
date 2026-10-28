"""Apply only approved Japanese-audience copy patches to four saved R13 PDFs."""
from pathlib import Path
import hashlib,json
import fitz
B=Path(__file__).resolve().parent;R=B.parents[1];spec=json.loads((B/'patches.json').read_text());inputs=json.loads((B/'receipts.json').read_text());OUT=B/'output';OUT.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();faces=[pair for k in range(4) for pair in [(16-2*k,1+2*k),(2+2*k,15-2*k)]]
reading=fitz.open(R/inputs[0]['path']);w,h=reading[0].rect.width,reading[0].rect.height;outputs=[]
assert len({p['id'] for p in spec['patches']})==len(spec['patches'])
packet=fitz.open()
for patch in spec['patches']:
 ov=fitz.open(B/'overlays'/f'{patch["id"]}.pdf');assert len(ov)==1;packet.insert_pdf(ov)
packet.save(B/'overlay-packet.pdf',deflate=True)
packet=fitz.open(B/'overlay-packet.pdf')
for src in inputs:
 path=R/src['path'];assert sha(path)==src['asset']['sha256'];d=fitz.open(path);regions=[]
 for patch_index,patch in enumerate(spec['patches']):
  pn=patch['page']
  if src['kind']=='print':
   pi,side=next((i,face.index(pn)) for i,face in enumerate(faces) if pn in face);p=d[pi];s=min(p.rect.width/2/w,p.rect.height/h);dx=side*p.rect.width/2+(p.rect.width/2-w*s)/2;dy=(p.rect.height-h*s)/2
  else:pi=pn-1;p=d[pi];s=p.rect.width/w;dx=dy=0
  r=fitz.Rect(patch['rect_px']);r=fitz.Rect(r.x0*w/2480*s+dx,r.y0*h/3508*s+dy,r.x1*w/2480*s+dx,r.y1*h/3508*s+dy)
  p.show_pdf_page(r,packet,patch_index,keep_proportion=False,overlay=True)
  regions.append({'id':patch['id'],'pdf_page':pi+1,'reading_page':pn,'rect':list(r),'scale':s,'source_rect_px':patch['rect_px']})
 dest=OUT/f'{src["label"]}-curriculum-notice-20261028.pdf';d.save(dest,garbage=0,deflate=True)
 outputs.append({'label':src['label'],'kind':src['kind'],'file':str(dest.relative_to(R)),'sha256':sha(dest),'pages':len(d),'source':{'id':src['asset']['id'],'revision':src['asset']['revision'],'file':src['path'],'sha256':src['asset']['sha256']},'regions':regions})
 print(src['label'],len(d),'pages',sha(dest),flush=True)
(B/'build-proof.json').write_text(json.dumps({'outputs':outputs,'patch_count':len(spec['patches']),'release':False},ensure_ascii=False,indent=2)+'\n')
# Reading-size inspection images.
p=fitz.open(R/outputs[0]['file']);(B/'draft').mkdir(exist_ok=True)
for pn in sorted({p['page'] for p in spec['patches']}):p[pn-1].get_pixmap(matrix=fitz.Matrix(1.8,1.8),alpha=False).save(B/'draft'/f'page-{pn:02}.png')
