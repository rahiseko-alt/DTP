from pathlib import Path
import json,fitz,re
from PIL import Image,ImageStat
B=Path(__file__).resolve().parent;R=B.parents[1];proof=json.load(open(B/'build-proof.json'));o=next(x for x in proof['outputs'] if x['label']=='flyer');d=fitz.open(R/o['file']);a=fitz.open(R/o['normalized']);MM=72/25.4

def patch(page,rect):
 p=page.get_pixmap(matrix=fitz.Matrix(150/72,150/72),clip=rect,alpha=False,colorspace=fitz.csRGB);return Image.frombytes('RGB',(p.width,p.height),p.samples)
def mmrect(x0,y0,x1,y1,dx=0,dy=0):return fitz.Rect(x0*MM+dx,y0*MM+dy,x1*MM+dx,y1*MM+dy)
T=d[0].trimbox;s1=patch(a[0],mmrect(111,278,113,280));s2=patch(d[0],mmrect(111,278,113,280,T.x0,T.y0));before=[round(x,1) for x in ImageStat.Stat(s1).mean];after=[round(x,1) for x in ImageStat.Stat(s2).mean];assert after[2]>after[0]+15 and after[1]>after[0]+8 and after[2]>40,(before,after)
count=lambda im:sum(r>150 and g>100 and b<205 and r-b>30 for r,g,b in im.getdata())
g1=count(patch(a[0],mmrect(10,242,110,260)));g2=count(patch(d[0],mmrect(10,242,110,260,T.x0,T.y0)));assert g1>100 and g2>g1*.65,(g1,g2)
audit=[]
for o in proof['outputs']:
 doc=fitz.open(R/o['file']);rgb=[];trans=[]
 for ix in range(1,doc.xref_length()):
  if doc.xref_is_stream(ix) and (doc.xref_get_key(ix,'Subtype')==('name','/Form') or any(ix in p.get_contents() for p in doc)):
   data=doc.xref_stream(ix)
   if re.search(rb'(?<![A-Za-z])(?:rg|RG)(?![A-Za-z])',data):rgb.append(ix)
  typ,val=doc.xref_get_key(ix,'SMask')
  if typ not in ['null'] and val not in ['/None','null']:trans.append((ix,'SMask',val))
  for key in ['ca','CA']:
   typ,val=doc.xref_get_key(ix,key)
   if typ in ['real','int'] and float(val)!=1:trans.append((ix,key,val))
 assert not rgb,(o['label'],rgb);assert not trans,(o['label'],trans);audit.append({'label':o['label'],'RGB_vector_operators':0,'transparency_objects':0})
v=json.load(open(B/'verification.json'));v['color_preservation']={'navy_source_RGB':before,'navy_print_softproof_RGB':after,'gold_source_pixels':g1,'gold_print_pixels':g2,'colored_type_and_panels_preserved':True};v['PDFX_structural_audit']=audit;(B/'verification.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(v['color_preservation']);print(audit)
