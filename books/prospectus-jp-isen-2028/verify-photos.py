from pathlib import Path
import fitz,json,hashlib,io
import numpy as np
from PIL import Image,ImageDraw
from build import BOOK,ROOT,SOURCE,PAGES
source=fitz.open(SOURCE);records=[]
changes=json.loads((BOOK/'work/learning-a/changes.json').read_text())
spec=json.loads((BOOK/'work/support/spec.json').read_text())
for pn,rel in PAGES.items():
 original=np.array(Image.open(io.BytesIO(source.extract_image(source[pn-1].get_images(full=True)[0][0])['image'])).convert('RGB'))
 outpath=BOOK/'work'/rel;out=np.array(Image.open(outpath).convert('RGB'));diff=np.any(original!=out,axis=2)
 if pn==1:
  records.append({'page':1,'scope':'authorized cover re-composition; body photo-only mask does not apply','sha256':hashlib.sha256(outpath.read_bytes()).hexdigest()});continue
 mask=Image.new('L',(2480,3508),0);draw=ImageDraw.Draw(mask)
 if pn in [2,4,6]:mask=Image.open(BOOK/f'work/heroes/mask-{pn:02}.png').convert('L')
 elif pn in [3,5]:
  for v in changes['items']:
   if v['page']==pn:
    x0,y0,x1,y1=v['rect'];draw.rectangle((x0,y0,x1-1,y1-1),fill=255)
 elif pn in [7,9]:mask=Image.open(BOOK/f'work/learning-b/page-{pn:02}-edit-mask.png').convert('L')
 elif pn==8:draw.rectangle((0,0,2479,1321),fill=255)
 else:
  for v in spec.values():
   if v.get('page')==pn:
    for x0,y0,x1,y1 in v['rects']:draw.rectangle((x0,y0,x1-1,y1-1),fill=255)
 outside=int(np.count_nonzero(diff&(np.array(mask)==0)));assert outside==0,(pn,outside)
 records.append({'page':pn,'sha256':hashlib.sha256(outpath.read_bytes()).hexdigest(),'changed_pixels':int(diff.sum()),'outside_declared_photo_or_person_mask_changed_pixels':outside})
(BOOK/'reviews/parent-photo-protection-check.json').write_text(json.dumps({'revision':2,'records':records},ensure_ascii=False,indent=2)+'\n');print('body photo-scope checks passed')
