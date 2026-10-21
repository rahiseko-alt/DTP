from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import fitz,json
O=Path(__file__).parent
spec={
 'p10-main':{'page':10,'rects':[[0,530,2480,1530]],'size':[2480,1000],'tiles':[[0,0,2480,1000]]},
 'p10-small':{'page':10,'rects':[[63,2100,493,2640],[550,2130,975,2640],[1030,2100,1455,2640],[1510,2100,1940,2640],[2000,2100,2425,2640]],'size':[1600,1200],'tiles':[[0,0,500,600],[550,0,1050,600],[1100,0,1600,600],[275,600,775,1200],[825,600,1325,1200]]},
 'p11-main':{'page':11,'rects':[[1000,200,2480,1130]],'size':[1480,930],'tiles':[[0,0,1480,930]]},
 'p11-small':{'page':11,'rects':[[190,1390,595,1625],[705,1355,1125,1625],[1380,1380,1780,1625],[1950,1375,2375,1625],[92,2605,640,2870],[690,2605,1215,2870],[1270,2605,1790,2870],[1845,2605,2395,2870]],'size':[1600,1200],'tiles':[[0,0,500,350],[550,0,1050,350],[1100,0,1600,350],[0,400,500,750],[550,400,1050,750],[1100,400,1600,750],[275,800,775,1150],[825,800,1325,1150]]}}
for key,s in spec.items():
 src=Image.open(O/f'p{s["page"]}-source.png').convert('RGB');im=Image.new('RGB',s['size'],'#d8d8d8')
 for rect,tile in zip(s['rects'],s['tiles']):
  c=src.crop(rect);c=c.resize((tile[2]-tile[0],tile[3]-tile[1]),Image.Resampling.LANCZOS);im.paste(c,tile[:2])
 if key=='p10-main':
  d=ImageDraw.Draw(im);d.rectangle((0,0,745,370),fill='#eeeeeb');d.rectangle((1850,0,2480,75),fill='#eeeeeb');d.ellipse((2050,650,2480,1000),fill='#e2f5fb')
 if key=='p11-main':
  d=ImageDraw.Draw(im);d.rectangle((0,0,235,195),fill='#eeefed');d.rectangle((0,240,270,425),fill='#eeefed');d.rectangle((900,10,1480,230),fill='#eeefed');d.rectangle((950,360,1190,580),fill='#eef3f3')
 im.save(O/f'{key}-input.png')
# Precisely extract visible P12 photo, clipping away non-visible source.
doc=fitz.open('books/prospectus-isen-trial-2028/parts/latest-prospectus-pdf/62aa8e4415e5e6aa4523e1c14d024d8d45112d81dc92ce8db16db7718066f880/latest-prospectus-pdf.pdf')
p=doc[11]
# composed transform: page underlying stream flips y; form matrix scales/translates.
m=fitz.Matrix(.23999999,0,0,-.23999999,0,858.95996)*fitz.Matrix(1.0011,0,0,1.0011,-8.37726,-8.51334)*p.transformation_matrix
clip=fitz.Rect(1400,259.375,2384.375,662.5)*m
print('p12 clip:',clip,'matrix',m)
p.get_pixmap(matrix=fitz.Matrix(5,5),clip=clip).save(O/'p12-input.png')
spec['p12-photo']={'page':12,'clip_pt':list(clip),'size_px':list(Image.open(O/'p12-input.png').size),'source_image_xref':43,'source_image_bbox_pt':list(p.get_image_info(xrefs=True)[0]['bbox'])}
(O/'spec.json').write_text(json.dumps(spec,indent=2))
