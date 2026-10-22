from pathlib import Path
from PIL import Image, ImageFilter, ImageDraw
import json, hashlib
P=Path(__file__).parent
R={3:[[1446,984,2400,1387],[1446,1487,2400,1892],[1446,1998,2400,2406]],5:[[122,769,868,1215],[921,769,1663,1215],[1714,769,2458,1215],[122,1566,1334,2029],[1401,1566,2458,2029],[126,2923,864,3351],[949,2923,1666,3351],[1756,2923,2458,3351]]}
items=[]
for page,rects in R.items():
 im=Image.open(P/f'original-{page:02}.png').convert('RGB')
 for i,r in enumerate(rects,1):
  name=f'p{page:02}-{i:02}';crop=im.crop(r);crop.save(P/f'{name}-source.png')
  # Remove incidental photograph lettering before model reference input.
  if page==3 and i==1:
   for b in [(0,70,175,350),(260,160,403,350)]:crop.paste(crop.crop(b).filter(ImageFilter.GaussianBlur(24)),b)
  if page==3 and i==3:
   b=(450,10,880,105);crop.paste(crop.crop(b).filter(ImageFilter.GaussianBlur(40)),b)
  if page==5 and i==1:
   ImageDraw.Draw(crop).ellipse((650,305,690,350),fill=(187,189,190))
  if page==5 and i==2:
   b=(300,350,355,390);crop.paste(crop.crop(b).filter(ImageFilter.GaussianBlur(20)),b)
  if page==5 and i==3:
   ImageDraw.Draw(crop).rectangle((560,313,690,363),fill=(76,79,82))
  if page==5 and i==4:
   ImageDraw.Draw(crop).polygon([(144,358),(445,358),(448,460),(143,460)],fill=(238,241,241))
  if page==5 and i==5:
   ImageDraw.Draw(crop).polygon([(108,20),(545,126),(545,211),(98,139)],fill=(203,216,235))
   ImageDraw.Draw(crop).polygon([(95,350),(510,370),(510,460),(84,460)],fill=(203,216,235))
   ImageDraw.Draw(crop).rectangle((600,310,810,382),fill=(239,240,237))
  if page==5 and i==7:
   b=(245,0,410,100);crop.paste(crop.crop(b).filter(ImageFilter.GaussianBlur(35)),b)
   b=(550,250,730,340);crop.paste(crop.crop(b).filter(ImageFilter.GaussianBlur(20)),b)
  if page==5 and i==8:
   b=(430,0,700,100);crop.paste(crop.crop(b).filter(ImageFilter.GaussianBlur(35)),b)
  crop.save(P/f'{name}-input.png')
  items.append(dict(id=name,page=page,rect=r,source_sha256=hashlib.sha256((P/f'{name}-source.png').read_bytes()).hexdigest()))
# Fixed cells, all exact 1000x500 with letterbox black gutters, input photographs cover cell by stretch.
GROUPS={'atlas-p03':['p03-01','p03-02','p03-03'],'atlas-p05-a':['p05-01','p05-02','p05-03','p05-04'],'atlas-p05-b':['p05-05','p05-06','p05-07','p05-08']}
for name,ids in GROUPS.items():
 atlas=Image.new('RGB',(1024,512*len(ids)),(0,0,0))
 for j,id in enumerate(ids):atlas.paste(Image.open(P/f'{id}-input.png').resize((1000,488),Image.Resampling.LANCZOS),(12,j*512+12))
 atlas.save(P/f'{name}-input.png')
(P/'layout.json').write_text(json.dumps(dict(items=items,groups=GROUPS,cell=[12,12,1012,500],atlas_width=1024,cell_step=512),ensure_ascii=False,indent=2))
