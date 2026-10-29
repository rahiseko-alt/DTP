from pathlib import Path
import fitz,pikepdf,numpy as np,json,hashlib,zxingcpp
from PIL import Image
B=Path(__file__).resolve().parent;src=B/'output/flyer-printpack-CMYK-20261028_クイック入稿用_A4_r03.pdf';out=B/'output/flyer-printpack-CMYK-20261028_クイック入稿用_A4_r04.pdf'
f=fitz.open(src);info=next(i for i in f[1].get_image_info() if i['width']==6520);x0,y0,x1,y1=info['bbox'];ink=np.array([237,203,87,94],np.uint8);counts={}
with pikepdf.open(src) as d:
 p=d.pages[1]
 for name,im in p.Resources.XObject.items():
  if im.get('/Subtype')!=pikepdf.Name('/Image'):continue
  w,h=int(im.Width),int(im.Height)
  if w==6520:
   raw=np.frombuffer(im.read_bytes(),np.uint8).reshape(h,w,4).copy();a=raw[::-1];xs=(x0+(np.arange(w)+.5)*(x1-x0)/w)*25.4/72;ys=(y0+(np.arange(h)+.5)*(y1-y0)/h)*25.4/72;area=(xs[None,:]>=108)&(xs[None,:]<=210)&(ys[:,None]>=269)&(ys[:,None]<=297)
  elif str(name)=='/EdgeFix3':
   raw=np.frombuffer(im.read_bytes(),np.uint8).reshape(h,w,4).copy();a=raw;area=np.broadcast_to(((np.arange(h)+.5)*297/h>=269)[:,None],(h,w))
  elif str(name)=='/EdgeFix1':
   raw=np.frombuffer(im.read_bytes(),np.uint8).reshape(h,w,4).copy();a=raw;area=np.broadcast_to(((np.arange(w)+.5)*210/w>=108)[None,:],(h,w))
  else:continue
  mask=area&(a[:,:,0]>180)&(a[:,:,1]>120)&(a[:,:,2]<60)&(a[:,:,3]<60);counts[str(name)]=int(mask.sum());a[mask]=ink;im.write(raw.tobytes())
 assert sum(counts.values())>0;d.save(out,compress_streams=True,fix_metadata_version=False)
checks=[]
with fitz.open(out) as d:
 for pn in range(2):
  old=f[pn].get_pixmap(matrix=fitz.Matrix(150/72,150/72),alpha=False);new=d[pn].get_pixmap(matrix=fitz.Matrix(150/72,150/72),alpha=False);a=np.frombuffer(old.samples,np.uint8).reshape(old.height,old.width,3);b=np.frombuffer(new.samples,np.uint8).reshape(new.height,new.width,3)
  delta=np.any(a!=b,axis=2)
  if pn==0:assert not delta.any()
  else:
   area=np.zeros(delta.shape,bool);area[int(268*150/25.4):,int(107*150/25.4):]=True;assert not delta[~area].any();Image.frombytes('RGB',(new.width,new.height),new.samples).save(B/'previews/quick-a4-flyer-back-r04.jpg',quality=95)
   d[pn].get_pixmap(matrix=fitz.Matrix(3,3),clip=fitz.Rect(105*72/25.4,267*72/25.4,210*72/25.4,297*72/25.4)).save('/workspace/downloads/contact-r04.png')
  qr=[]
  for dpi in [150,300]:
   decode=lambda pg:sorted(r.text for r in zxingcpp.read_barcodes(Image.frombytes('RGB',(pg.width,pg.height),pg.samples)))
   before=decode(f[pn].get_pixmap(matrix=fitz.Matrix(dpi/72,dpi/72),alpha=False));after=decode(d[pn].get_pixmap(matrix=fitz.Matrix(dpi/72,dpi/72),alpha=False));assert before==after and after;qr.append({'dpi':dpi,'decoded':after})
  checks.append({'page':pn+1,'changed_pixels':int(delta.sum()),'QR':qr})
with pikepdf.open(src) as s,pikepdf.open(out) as d:
 assert s.Root.OutputIntents[0].DestOutputProfile.read_bytes()==d.Root.OutputIntents[0].DestOutputProfile.read_bytes();assert not d.check_pdf_syntax();assert len(d.pages)==2
(B/'flyer-r04-verification.json').write_text(json.dumps({'output':out.name,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'changed_background_pixels':counts,'method':'Back right contact panel only: recolour exposed underlying blue to existing dark navy. White text and QR retained; no scaling or layout movement.','checks':checks,'visual_review':'pending'},ensure_ascii=False,indent=2)+'\n')
