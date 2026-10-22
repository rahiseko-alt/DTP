"""Lossless original page compositing of isolated photo edits. Requires generated/* files."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np,json,hashlib,shutil,yaml
O=Path(__file__).parent
S=json.loads((O/'spec.json').read_text())
protected={10:[[0,530,745,900],[1850,530,2480,620],[2030,1120,2480,1530],[1190,2100,1450,2480]],11:[[1000,200,1235,395],[1000,440,1270,625],[1900,200,2480,450],[1950,560,2190,780],[1000,670,1060,1000],[130,1410,245,1510],[1025,1410,1140,1545],[1350,1380,1445,1530],[1920,1400,2050,1530]]}
changes={'source_pdf':'books/prospectus-isen-trial-2028/parts/latest-prospectus-pdf/62aa8e4415e5e6aa4523e1c14d024d8d45112d81dc92ce8db16db7718066f880/latest-prospectus-pdf.pdf','method':'Extract photograph regions, build fixed contact sheets, edit with image_gen, resize by Lanczos and cut back to original integer rectangles with inward edge feathering. Restore original protected overlays/signs/graphics byte-for-byte. All pixels outside allowed photograph rectangles unchanged. No full-page generation.','pages':{}}
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
 for r in protected[n]:
  # Full original protected rectangle plus a 16px outward feather, leaving all protected pixels exact.
  pad=20;xx0=max(0,r[0]-pad);yy0=max(0,r[1]-pad);xx1=min(src.width,r[2]+pad);yy1=min(src.height,r[3]+pad)
  yy,xx=np.mgrid[yy0:yy1,xx0:xx1]
  dist=np.maximum.reduce([r[0]-xx,xx-r[2]+1,r[1]-yy,yy-r[3]+1,np.zeros_like(xx)])
  alpha=np.clip(1-dist/pad,0,1)
  out.paste(src.crop((xx0,yy0,xx1,yy1)),(xx0,yy0),Image.fromarray((alpha*255).astype('uint8')))
  out.paste(src.crop(r),r[:2])
 # At P10 circle area the rectangle preserves original clothing/table as well as overlay.
 # Smooth the outer left/top seam but preserve every pixel within the protected rectangle.
 out.save(O/f'page-{n}.png')
 a=np.array(src);b=np.array(out);diff=np.any(a!=b,axis=2);allow=np.array(allowed)>0
 assert not np.any(diff&~allow),'outside-photo mutation'
 for r in protected[n]:assert np.array_equal(a[r[1]:r[3],r[0]:r[2]],b[r[1]:r[3],r[0]:r[2]])
 changes['pages'][str(n)]={'size_px':list(src.size),'photo_rects':[r for k,s in S.items() if s['page']==n for r in s['rects']],'protected_rects':protected[n],'outside_photo_changed_pixels':int(np.count_nonzero(diff&~allow)),'protected_rect_changed_pixels':0,'changed_pixels':int(diff.sum()),'source_sha256':hashlib.sha256((O/f'p{n}-source.png').read_bytes()).hexdigest(),'output_sha256':hashlib.sha256((O/f'page-{n}.png').read_bytes()).hexdigest(),'note':'Original headers, body copy, monetary tables, logos, school building photograph and all non-photo areas preserved. P10 circle area also preserves clothing below faces; P11 restores title/description fringe and original wall sign.'}
 # compact preview for direct full-page checking
 out.resize((744,1053),Image.Resampling.LANCZOS).save(O/f'page-{n}-preview.png')
# Classroom photo has exact visible clip aspect; no monetary or native text pixels touched.
s=S['p12-photo'];im=Image.open(O/'p12-generated.png').convert('RGB');w,h=s['size_px'];im.resize((w,h),Image.Resampling.LANCZOS).save(O/'p12-photo.png')
changes['pages']['12']={**s,'output_sha256':hashlib.sha256((O/'p12-photo.png').read_bytes()).hexdigest(),'method':'Output only the exact visible photograph crop. Parent inserts it into clip_pt without changing any surrounding PDF content.'}
changes['files_sha256']={str(p.relative_to(O)):hashlib.sha256(p.read_bytes()).hexdigest() for p in O.glob('*.png')}
(O/'changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2))
print(json.dumps({n:{'size_px':s.get('size_px'),'clip_pt':s.get('clip_pt'),'outside_photo_changed_pixels':s.get('outside_photo_changed_pixels')} for n,s in changes['pages'].items()},indent=2))
