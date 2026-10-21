"""Lossless original page compositing of isolated photo edits. Requires generated/* files."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json,hashlib,shutil,yaml
from scipy import ndimage
O=Path(__file__).parent
S=json.loads((O/'spec.json').read_text())
protected={10:[[0,530,745,900],[1850,530,2480,620],[2030,1120,2480,1530],[1190,2100,1450,2480]],11:[[1000,200,1235,395],[1000,440,1270,625],[1900,200,2480,450],[1950,560,2190,780],[1000,670,1060,1000],[130,1410,245,1510],[1025,1410,1140,1545],[1350,1380,1445,1530],[1920,1400,2050,1530]]}
changes={'source_pdf':'books/prospectus-isen-trial-2028/parts/latest-prospectus-pdf/62aa8e4415e5e6aa4523e1c14d024d8d45112d81dc92ce8db16db7718066f880/latest-prospectus-pdf.pdf','method':'Extract photograph regions, build fixed contact sheets, edit with image_gen, resize by Lanczos and cut back to original integer rectangles with inward edge feathering. Protect original printed glyphs and maintain continuous original wall/right counselor. All pixels outside allowed photograph rectangles unchanged. No full-page generation.','pages':{}}
for n in [10,11]:
 src=Image.open(O/f'p{n}-source.png').convert('RGB');out=src.copy();allowed=Image.new('L',src.size,0);ad=ImageDraw.Draw(allowed)
 for key,s in S.items():
  if s['page']!=n:continue
  gen=Image.open(O/f'{key}-generated.png').convert('RGB').resize(s['size'],Image.Resampling.LANCZOS)
  for rect,tile in zip(s['rects'],s['tiles']):
   w,h=rect[2]-rect[0],rect[3]-rect[1];patch=gen.crop(tile).resize((w,h),Image.Resampling.LANCZOS)
   mask=Image.new('L',(w,h),0);md=ImageDraw.Draw(mask)
   if 'main' in key:md.rectangle((0,0,w,h),fill=255)
   elif n==10 or rect[1]>2000:md.rounded_rectangle((0,0,w-1,h-1),radius=14,fill=255)
   else:md.rectangle((0,0,w,h),fill=255)
   # Feather inward at crop boundaries to avoid visible rectangular photo joins.
   edge=np.minimum(np.arange(w),np.arange(w)[::-1])[None,:]
   edge=np.minimum(edge,np.minimum(np.arange(h),np.arange(h)[::-1])[:,None])
   feather=18 if 'main' in key else 9
   edge_alpha=np.clip(edge/feather,0,1)
   mask=Image.fromarray((np.array(mask)*edge_alpha).astype('uint8'))
   out.paste(patch,rect[:2],mask);ad.rectangle((rect[0],rect[1],rect[2]-1,rect[3]-1),fill=255)
 protection=Image.new('L',src.size,0)
 for r in protected[n]:
  rgb=np.array(src.crop(r)).astype(int)
  if n==10 and r==[2030,1120,2480,1530]:
   cyan=(rgb[:,:,0]>170)&((rgb[:,:,1]-rgb[:,:,0])>5)&((rgb[:,:,2]-rgb[:,:,0])>12)
   labs,num=ndimage.label(cyan);areas=np.bincount(labs.ravel());areas[0]=0
   glyph=ndimage.binary_fill_holes(labs==int(areas.argmax()))
   # Generated photograph already contains a clean blank circular panel.
   # Restore only original printed letters well inside that panel, never clothing/background.
   glyph=(rgb[:,:,0]<165)&(rgb[:,:,2]>rgb[:,:,0]+15)&(rgb[:,:,1]>rgb[:,:,0])&ndimage.binary_erosion(glyph,iterations=16)
   glyph=ndimage.binary_dilation(glyph,iterations=1)

  else:
   # Keep only printed navy/black glyphs; rectangular photo/background fragments are excluded.
   blue=(rgb[:,:,2]>rgb[:,:,0]+20)&(rgb[:,:,2]>rgb[:,:,1]+3)&(rgb[:,:,0]<175)
   dark=(rgb.mean(axis=2)<145)
   if n==11 and r[1]<1100 and r!=[1000,670,1060,1000]:dark=np.zeros(blue.shape,bool)
   labs,num=ndimage.label(blue|dark);glyph=np.zeros(blue.shape,bool)
   for k,sl in enumerate(ndimage.find_objects(labs),1):
    if sl is None:continue
    h=sl[0].stop-sl[0].start;w=sl[1].stop-sl[1].start;area=np.count_nonzero(labs[sl]==k)
    if 2<=area<=13000 and w<=350 and h<=210:glyph[sl]|=labs[sl]==k
   glyph=ndimage.binary_dilation(glyph,iterations=2)
  core=Image.fromarray(np.uint8(glyph)*255)
  # Preserve glyph pixels exactly, with a smooth small halo rather than a restored photo rectangle.
  soft=core.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(.6))
  alpha=Image.fromarray(np.maximum(np.array(core),np.array(soft)))
  out.paste(src.crop(r),r[:2],alpha)
  protection.paste(core,r[:2])
 if n==11:
  # Preserve the existing right-hand counselor and the continuous real wall/sign area.
  # It avoids both a blank generated sign rectangle and a sign patch intersecting her face.
  r=(1920,200,2480,1130);w,h=r[2]-r[0],r[3]-r[1]
  yy,xx=np.mgrid[:h,:w];distance=xx
  alpha_array=np.clip(distance/55,0,1)
  # At the wall's left boundary retain only neutral wall, excluding the original patterned sleeve.
  pixels=np.array(src.crop(r)).astype(float);neutral=(pixels.min(axis=2)>175)&((pixels.max(axis=2)-pixels.min(axis=2))<46)
  gate=np.ones((h,w));gate[:,:100]=ndimage.gaussian_filter(neutral.astype(float),2)[:,:100]
  alpha=Image.fromarray(np.uint8(alpha_array*gate*255))
  out.paste(src.crop(r),r[:2],alpha)
  # This retained region is original photography including the sign, not AI-rewritten type.
  pa=np.array(protection);pa[r[1]:r[3],r[0]:r[2]]=0;protection=Image.fromarray(pa)
 if n==11:
  # Printed headline uses a soft white readability fade, extending beyond the rectangular generator blank.
  r=(1000,200,2480,1130);w,h=r[2]-r[0],r[3]-r[1];yy,xx=np.mgrid[:h,:w]
  dx=np.maximum(xx-270,0);dy=np.maximum(np.maximum(240-yy,yy-425),0)
  distance=np.hypot(dx,dy);alpha=np.uint8(np.exp(-.5*(distance/45)**2)*255)
  # Keep all protected type exact; white backing fades beyond its generator blank edge.
  prot=np.array(protection.crop(r));alpha[prot>0]=0
  out.paste(Image.new('RGB',(w,h),'white'),r[:2],Image.fromarray(alpha))
 protection.save(O/f'page-{n}-text-protection-mask.png')
 # At P10 circle area the rectangle preserves original clothing/table as well as overlay.
 # Smooth the outer left/top seam but preserve every pixel within the protected rectangle.
 out.save(O/f'page-{n}.png')
 a=np.array(src);b=np.array(out);diff=np.any(a!=b,axis=2);allow=np.array(allowed)>0
 assert not np.any(diff&~allow),'outside-photo mutation'
 assert np.array_equal(a[np.array(protection)>0],b[np.array(protection)>0])
 changes['pages'][str(n)]={'size_px':list(src.size),'photo_rects':[r for k,s in S.items() if s['page']==n for r in s['rects']],'protected_glyph_regions':protected[n],'protected_glyph_mask':f'page-{n}-text-protection-mask.png','outside_photo_changed_pixels':int(np.count_nonzero(diff&~allow)),'protected_glyph_changed_pixels':0,'changed_pixels':int(diff.sum()),'source_sha256':hashlib.sha256((O/f'p{n}-source.png').read_bytes()).hexdigest(),'output_sha256':hashlib.sha256((O/f'page-{n}.png').read_bytes()).hexdigest(),'note':'Revision2: protect printed glyphs only, using the generated clean blank circle at P10. At P11 keep original wall/right counselor with a neutral-wall boundary and soften headline backing. All non-photo pixels retained.'}
 # compact preview for direct full-page checking
 out.resize((744,1053),Image.Resampling.LANCZOS).save(O/f'page-{n}-preview.png')
# Classroom photo has exact visible clip aspect; no monetary or native text pixels touched.
s=S['p12-photo'];im=Image.open(O/'p12-generated.png').convert('RGB');w,h=s['size_px'];im.resize((w,h),Image.Resampling.LANCZOS).save(O/'p12-photo.png')
changes['pages']['12']={**s,'output_sha256':hashlib.sha256((O/'p12-photo.png').read_bytes()).hexdigest(),'method':'Output only the exact visible photograph crop. Parent inserts it into clip_pt without changing any surrounding PDF content.'}
changes['files_sha256']={str(p.relative_to(O)):hashlib.sha256(p.read_bytes()).hexdigest() for p in O.glob('*.png')}
(O/'changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2))
print(json.dumps({n:{'size_px':s.get('size_px'),'clip_pt':s.get('clip_pt'),'outside_photo_changed_pixels':s.get('outside_photo_changed_pixels')} for n,s in changes['pages'].items()},indent=2))
