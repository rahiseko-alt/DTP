from pathlib import Path
import fitz,pikepdf,numpy as np,hashlib,json,zxingcpp
from PIL import Image
B=Path(__file__).resolve().parent;src=B/'output/flyer-printpack-CMYK-20261028_クイック入稿用_A4_r02.pdf';out=B/'output/flyer-printpack-CMYK-20261028_クイック入稿用_A4_r03.pdf'
with fitz.open(src) as render, pikepdf.open(src) as d:
 for pn,p in enumerate(d.pages):
  pix=render[pn].get_pixmap(matrix=fitz.Matrix(300/72,300/72),colorspace=fitz.csCMYK,alpha=False);a=np.frombuffer(pix.samples,np.uint8).reshape(pix.height,pix.width,4).copy();n=round(1.2*300/25.4)
  # Sample original CMYK bytes directly; do not convert a rendered colour proof twice.
  infos=render[pn].get_image_info();info=next(i for i in infos if i['width']==(2480 if pn==0 else 6520))
  image=next(o for o in d.objects if isinstance(o,pikepdf.Stream) and o.get('/Subtype')==pikepdf.Name('/Image') and int(o.get('/Width',0))==info['width'])
  native=np.frombuffer(image.read_bytes(),np.uint8).reshape(int(image.Height),int(image.Width),4)
  if info['transform'][3]<0:native=native[::-1]
  if info['transform'][0]<0:native=native[:,::-1]
  rx0,ry0,rx1,ry1=info['bbox'];xs=(np.arange(pix.width)+.5)*render[pn].rect.width/pix.width;ys=(np.arange(pix.height)+.5)*render[pn].rect.height/pix.height
  ix=np.clip(((xs-rx0)/(rx1-rx0)*native.shape[1]).astype(int),0,native.shape[1]-1);iy=np.clip(((ys-ry0)/(ry1-ry0)*native.shape[0]).astype(int),0,native.shape[0]-1)
  a=native[iy[:,None],ix[None,:]].copy()
  if pn==0:
   top=float(p.MediaBox[3])-247.008
   a[ys>=top]=np.rint(np.array([.184,.357,.776,0])*255).astype(np.uint8)
   a[ys>=float(p.MediaBox[3])-243.258]=np.rint(np.array([.898,.757,.506,.478])*255).astype(np.uint8)
  a[:n]=a[n:n+1];a[-n:]=a[-n-1:-n];a[:,:n]=a[:,n:n+1];a[:,-n:]=a[:,-n-1:-n]
  x0,y0,x1,y1=map(float,p.MediaBox);w=x1-x0;h=y1-y0;th=h*n/pix.height;tw=w*n/pix.width
  # Give the printer a conventional zero-origin A4 page. Translate only, never scale.
  old=p.Contents;streams=list(old) if isinstance(old,pikepdf.Array) else [old]
  prefix=pikepdf.Stream(d,f'q 1 0 0 1 {-x0:.12f} {-y0:.12f} cm\n'.encode())
  suffix=pikepdf.Stream(d,b'Q\n')
  strips=[(a[:n],0,h-th,w,th),(a[-n:],0,0,w,th),(a[:,:n],0,0,tw,h),(a[:,-n:],w-tw,0,tw,h)];cmd=[]
  for j,(data,x,y,ww,hh) in enumerate(strips):
   im=pikepdf.Stream(d,np.ascontiguousarray(data).tobytes());im.Type=pikepdf.Name('/XObject');im.Subtype=pikepdf.Name('/Image');im.Width=data.shape[1];im.Height=data.shape[0];im.ColorSpace=pikepdf.Name('/DeviceCMYK');im.BitsPerComponent=8
   name=f'/EdgeFix{j}';p.Resources.XObject[name]=im
   # Overlap page edges by 0.02pt to avoid rasterizer white seams; clip at A4.
   cmd.append(f'q {ww+.04:.12f} 0 0 {hh+.04:.12f} {x-.02:.12f} {y-.02:.12f} cm {name} Do Q\n')
  p.Contents=pikepdf.Array([prefix]+streams+[suffix,pikepdf.Stream(d,(''.join(cmd)).encode())])
  from decimal import Decimal
  box=pikepdf.Array([0,0,Decimal(210)*Decimal(72)/Decimal('25.4'),Decimal(297)*Decimal(72)/Decimal('25.4')])
  for key in ['/MediaBox','/CropBox','/TrimBox','/BleedBox']:p.obj[key]=box
 d.save(out,compress_streams=True,fix_metadata_version=False)
checks=[]
with fitz.open(src) as old,fitz.open(out) as d:
 assert len(d)==2
 for pn,p in enumerate(d):
  assert abs(p.rect.width*25.4/72-210)<.001 and abs(p.rect.height*25.4/72-297)<.001 and not p.get_fonts()
  pix=p.get_pixmap(matrix=fitz.Matrix(150/72,150/72),alpha=False);op=old[pn].get_pixmap(matrix=fitz.Matrix(150/72,150/72),alpha=False);a=np.frombuffer(pix.samples,np.uint8).reshape(pix.height,pix.width,3);b=np.frombuffer(op.samples,np.uint8).reshape(op.height,op.width,3)
  diff=np.abs(a[9:-9,9:-9].astype(int)-b[9:-9,9:-9].astype(int));assert diff.mean()<0.02 and np.count_nonzero(np.any(diff>3,axis=2))==0, (pn,diff.max(),diff.mean())
  qr=[]
  for dpi in [150,300]:
   decode=lambda p:sorted(r.text for r in zxingcpp.read_barcodes(Image.frombytes('RGB',(p.width,p.height),p.samples)))
   new=decode(p.get_pixmap(matrix=fitz.Matrix(dpi/72,dpi/72),alpha=False));orig=decode(old[pn].get_pixmap(matrix=fitz.Matrix(dpi/72,dpi/72),alpha=False));assert new==orig and new;qr.append({'dpi':dpi,'decoded':new})
  checks.append({'page':pn+1,'QR':qr,'layout_unscaled':True,'interior_unchanged':True})
  if True:
   Image.frombytes('RGB',(pix.width,pix.height),pix.samples).save(B/f'previews/quick-a4-flyer-r03-page-{pn+1}.jpg',quality=95)
   for j,r in enumerate([fitz.Rect(0,0,45,45),fitz.Rect(p.rect.width-45,0,p.rect.width,45),fitz.Rect(0,p.rect.height-45,45,p.rect.height),fitz.Rect(p.rect.width-45,p.rect.height-45,p.rect.width,p.rect.height)]):p.get_pixmap(matrix=fitz.Matrix(4,4),clip=r).save(f'/workspace/downloads/r03-page-{pn+1}-corner-{j}.png')
with pikepdf.open(src) as s,pikepdf.open(out) as d:
 assert s.Root.OutputIntents[0].DestOutputProfile.read_bytes()==d.Root.OutputIntents[0].DestOutputProfile.read_bytes();assert not d.check_pdf_syntax()
(B/'flyer-front-r03-verification.json').write_text(json.dumps({'output':out.name,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'method':'Both pages: outer 1.2mm edge extension at 300ppi with edge overlap; zero-origin exact A4; no content scaling; r02 back interior retained','checks':checks,'CMYK_ICC_preserved':True,'visual_review':'pending'},ensure_ascii=False,indent=2)+'\n')
