#!/usr/bin/env python3
"""Reproduce narrowly masked person edits; all other original pixels retained."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import hashlib,json, yaml
import numpy as np
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
PDF=ROOT/'books/prospectus-isen-trial-2028/parts/latest-prospectus-pdf/62aa8e4415e5e6aa4523e1c14d024d8d45112d81dc92ce8db16db7718066f880/latest-prospectus-pdf.pdf'
SPECS={
2:{'crop':[0,0,2480,850], 'polygons':[
[(575,85),(955,85),(990,350),(950,480),(875,550),(818,650),(710,646),(620,540),(585,400)],
[(980,250),(1300,250),(1325,460),(1285,605),(1220,660),(1100,805),(1060,735),(1010,680),(975,530)],
[(1500,250),(1870,245),(1970,660),(1875,705),(1830,745),(1710,775),(1590,730),(1525,650)],
[(1960,80),(2370,80),(2420,360),(2360,515),(2320,585),(2180,650),(2110,635),(2070,550),(1990,465)]
], 'protected':[[0,850,2480,3508]]},
4:{'crop':[870,0,2480,1300],'polygons':[
[(870,0),(1640,0),(1700,400),(1620,640),(1560,870),(1460,980),(1350,995),(1190,1120),(1100,1240),(1035,1160),(985,1035),(950,920),(920,840),(870,810)],
[(1540,500),(1960,470),(2070,700),(2085,980),(1980,1160),(1890,1210),(1750,1260),(1640,1160),(1580,1000),(1510,830)],
[(2050,450),(2479,450),(2479,1000),(2380,1160),(2220,1205),(2130,1110),(2070,980),(2010,760)]
], 'protected':[[0,0,785,300],[0,1580,2480,3508]], 'glyph_protection_rect':[50,705,1000,1450], 'feather':90},
6:{'crop':[970,0,2480,1310],'polygons':[
[(970,0),(1790,0),(1850,170),(1880,420),(1890,560),(1850,675),(1800,730),(1750,770),(1700,820),(1620,845),(1540,1050),(1490,1180),(1425,1120),(1300,900),(1115,790),(970,670)],
[(1830,335),(2330,325),(2400,630),(2360,860),(2250,1000),(2190,1080),(2090,1200),(2010,1190),(1950,1050),(1885,900),(1815,690)],
[(2320,570),(2479,570),(2479,1080),(2420,1120),(2320,1060),(2260,960),(2250,820)]
], 'protected':[[0,0,790,300],[95,460,950,1180],[0,1500,2480,3508]],
# Original hand, wrist, watch, and forearm retained exactly.
'exclude_polygons':[[(1730,840),(1770,720),(1880,690),(2040,735),(2160,950),(2235,1130),(2280,1310),(1815,1310),(1820,1020)]]}
}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
results=[]
for num,s in SPECS.items():
 stem=f'{num:02d}'
 original=Image.open(HERE/f'original-{stem}.png').convert('RGB')
 generated=Image.open(HERE/f'generated-{stem}.png').convert('RGB')
 x0,y0,x1,y1=s['crop']; generated_size=generated.size
 generated=generated.resize((x1-x0,y1-y0),Image.Resampling.LANCZOS)
 layer=original.copy();layer.paste(generated,(x0,y0))
 m=Image.new('L',original.size,0);d=ImageDraw.Draw(m)
 for poly in s['polygons']:d.polygon(poly,fill=255)
 # Inward feather: no new pixels beyond the explicitly documented polygon.
 hard=np.asarray(m).copy();blur=np.asarray(m.filter(ImageFilter.GaussianBlur(s.get('feather',7))))
 m=Image.fromarray(np.minimum(hard,blur))
 if num==4:
  from scipy.ndimage import distance_transform_edt
  distance=distance_transform_edt(hard>0)
  m=Image.fromarray((np.minimum(distance/s['feather'],1)*255).astype(np.uint8))
 d=ImageDraw.Draw(m)
 # Original pixels always prevail for text, lines, badge, and other exclusions.
 for r in s['protected']:d.rectangle((r[0],r[1],r[2]-1,r[3]-1),fill=0)
 for poly in s.get('exclude_polygons',[]):d.polygon(poly,fill=0)
 glyph_mask=None
 if 'glyph_protection_rect' in s:
  r=s['glyph_protection_rect']; arr=np.asarray(original); nearwhite=(arr.min(axis=2)>185)&((arr.max(axis=2).astype(int)-arr.min(axis=2))<75)
  g=np.zeros(arr.shape[:2],dtype=np.uint8); g[r[1]:r[3],r[0]:r[2]]=nearwhite[r[1]:r[3],r[0]:r[2]]*255
  glyph_mask=Image.fromarray(g).filter(ImageFilter.MaxFilter(17))
  glyph_mask.save(HERE/f'protected-glyphs-{stem}.png')
  m=Image.fromarray(np.where(np.asarray(glyph_mask)>0,0,np.asarray(m)).astype(np.uint8))
 # Never use generated content beyond the crop edges.
 cropmask=Image.new('L',original.size,0);ImageDraw.Draw(cropmask).rectangle((x0,y0,x1-1,y1-1),fill=255)
 m=Image.fromarray(np.minimum(np.asarray(m),np.asarray(cropmask)))
 m.save(HERE/f'mask-{stem}.png')
 out=Image.composite(layer,original,m);out.save(HERE/f'page-{stem}.png')
 a=np.asarray(original);b=np.asarray(out);change=np.any(a!=b,axis=2);allowed=np.asarray(m)>0
 assert not np.any(change & ~allowed)
 protected_checks=[]
 for r in s['protected']:
  protected_checks.append({'rect':r,'pixel_identical':bool(np.array_equal(a[r[1]:r[3],r[0]:r[2]],b[r[1]:r[3],r[0]:r[2]]))})
 assert all(t['pixel_identical'] for t in protected_checks)
 if glyph_mask is not None:
  assert not np.any(change & (np.asarray(glyph_mask)>0))
 ys,xs=np.where(change)
 record={'pdf_order_page':num,'source_pdf':str(PDF.relative_to(ROOT)),'source_pdf_sha256':sha(PDF),'source_image':f'original-{stem}.png','source_image_sha256':sha(HERE/f'original-{stem}.png'),'generation_input':f'input-{stem}.png','generation_input_sha256':sha(HERE/f'input-{stem}.png'),'input_crop_xyxy':s['crop'],'input_method':'img2img via image_gen.imagegen; narrow photographic crop only','input_preprocessing': 'p4 tiny residual white glyphs in local [0,870,110,1010] masked with neutral skin color; no generated text retained' if num==4 else 'crop only','generated_image':f'generated-{stem}.png','generated_size_px':generated_size,'generated_sha256':sha(HERE/f'generated-{stem}.png'),'output_image':f'page-{stem}.png','output_size_px':out.size,'output_sha256':sha(HERE/f'page-{stem}.png'),'mask_image':f'mask-{stem}.png','mask_sha256':sha(HERE/f'mask-{stem}.png'),'change_rect_xyxy':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],'change_region_rectangles_xyxy':[[min(v[0] for v in poly),min(v[1] for v in poly),max(v[0] for v in poly)+1,max(v[1] for v in poly)+1] for poly in s['polygons']], 'change_polygons_xy':s['polygons'],'excluded_person_parts':s.get('exclude_polygons',[]),'protected_rectangles':protected_checks,'protected_text_glyph_mask':f'protected-glyphs-{stem}.png' if glyph_mask is not None else None,'protected_text_glyphs_identical':True,'unchanged_outside_mask':True,'changed_pixels':int(change.sum()),'mask_feather_px':s.get('feather',7),'resampling':'Pillow LANCZOS to exact original crop size','review':'Generated and full-page composite inspected visually. Fictional Japanese-appearance people; no nationality inferred. Male faces clean shaven. Clothing, pose, gaze and photo framing visually retained. All original text, rules, badge and lower information remain original pixels.'}
 results.append(record)
 prompt=yaml.safe_load((HERE/f'input-{stem}.prompt.yaml').read_text());prompt['size']='2480x3508';prompt['reference_inputs'][0]['note']+=' '+record['input_preprocessing'];prompt['notes']+=' Generated crop resized with LANCZOS and composited through mask-'+stem+'.png; full mask geometry/protected areas and SHA256 recorded in changes.json. Native generated crop '+str(generated_size)+'; final full-page source resolution 2480x3508, A4 approximately 300dpi. AI photo crop effective resolution exceeds 150dpi.'
 (HERE/f'page-{stem}.prompt.yaml').write_text(yaml.safe_dump(prompt,allow_unicode=True,sort_keys=False))
 prompt['size']=f'{generated_size[0]}x{generated_size[1]}'
 (HERE/f'generated-{stem}.prompt.yaml').write_text(yaml.safe_dump(prompt,allow_unicode=True,sort_keys=False))
 preview=out.copy();preview.thumbnail((744,1053));preview.save(HERE/f'preview-page-{stem}.png')
(HERE/'changes.json').write_text(json.dumps({'schema':'person-photo-edit-v1','pages':results},ensure_ascii=False,indent=2)+'\n')
print(json.dumps([{'page':r['pdf_order_page'],'bbox':r['change_rect_xyxy'],'pixels':r['changed_pixels'],'outside_mask_unchanged':r['unchanged_outside_mask']} for r in results]))
