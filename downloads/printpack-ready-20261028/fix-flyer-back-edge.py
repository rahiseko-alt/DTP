from pathlib import Path
import pikepdf,numpy as np,fitz,hashlib,json,zxingcpp
from PIL import Image
B=Path(__file__).resolve().parent
src=B/'output/flyer-printpack-CMYK-20261028_クイック入稿用_A4.pdf'
out=B/'output/flyer-printpack-CMYK-20261028_クイック入稿用_A4_r02.pdf'
with pikepdf.open(src) as d:
 p=d.pages[1];images=[o for o in d.objects if isinstance(o,pikepdf.Stream) and o.get('/Subtype')==pikepdf.Name('/Image') and int(o.get('/Width',0))==6520];assert len(images)==1
 im=images[0];w,h=int(im.Width),int(im.Height);assert im.ColorSpace==pikepdf.Name('/DeviceCMYK') and im.BitsPerComponent==8
 a=np.frombuffer(im.read_bytes(),np.uint8).reshape(h,w,4).copy();old=a.copy()
 # Full source image is 230 x 317 mm; A4 starts 10 mm from each side.
 x0=round(10*w/230);x1=round(220*w/230);y0=round(10*h/317);y1=round(307*h/317)
 n=round(1.8*w/230)
 # Extend adjacent interior pixels over the white margin / grey frame only.
 a[y0:y0+n,x0:x1]=a[y0+n:y0+n+1,x0:x1]
 a[y1-n:y1,x0:x1]=a[y1-n-1:y1-n,x0:x1]
 a[y0:y1,x0:x0+n]=a[y0:y1,x0+n:x0+n+1]
 a[y0:y1,x1-n:x1]=a[y0:y1,x1-n-1:x1-n]
 assert np.array_equal(a[y0+n:y1-n,x0+n:x1-n],old[y0+n:y1-n,x0+n:x1-n])
 im.write(a.tobytes());d.save(out,compress_streams=True,recompress_flate=False,fix_metadata_version=False)
with fitz.open(src) as s,fitz.open(out) as d:
 assert len(d)==2 and not any(p.get_fonts() for p in d)
 checks=[]
 for pn in range(2):
  p=d[pn];assert abs(p.rect.width*25.4/72-210)<.001 and abs(p.rect.height*25.4/72-297)<.001
  b=p.get_pixmap(matrix=fitz.Matrix(150/72,150/72),alpha=False);o=s[pn].get_pixmap(matrix=fitz.Matrix(150/72,150/72),alpha=False)
  aa=np.frombuffer(b.samples,np.uint8).reshape(b.height,b.width,3);bb=np.frombuffer(o.samples,np.uint8).reshape(o.height,o.width,3)
  if pn==0:assert np.array_equal(aa,bb)
  else:assert np.array_equal(aa[12:-12,12:-12],bb[12:-12,12:-12])
  qr=[]
  for dpi in [150,300]:
   pix=p.get_pixmap(matrix=fitz.Matrix(dpi/72,dpi/72),alpha=False);orig=s[pn].get_pixmap(matrix=fitz.Matrix(dpi/72,dpi/72),alpha=False)
   decode=lambda z:sorted(x.text for x in zxingcpp.read_barcodes(Image.frombytes('RGB',(z.width,z.height),z.samples)))
   assert decode(pix)==decode(orig) and decode(pix);qr.append({'dpi':dpi,'decoded':decode(pix)})
  checks.append({'page':pn+1,'QR':qr,'front_unchanged':pn==0,'interior_unchanged':True})
  if pn==1:
   b.save('/workspace/downloads/flyer-back-r02.png')
   for j,r in enumerate([fitz.Rect(0,0,45,45),fitz.Rect(p.rect.width-45,0,p.rect.width,45),fitz.Rect(0,p.rect.height-45,45,p.rect.height),fitz.Rect(p.rect.width-45,p.rect.height-45,p.rect.width,p.rect.height)]):p.get_pixmap(matrix=fitz.Matrix(4,4),clip=r).save(f'/workspace/downloads/flyer-back-r02-corner-{j}.png')
with pikepdf.open(src) as s,pikepdf.open(out) as d:
 assert s.Root.OutputIntents[0].DestOutputProfile.read_bytes()==d.Root.OutputIntents[0].DestOutputProfile.read_bytes()
 assert not d.check_pdf_syntax()
report={'output':out.name,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'edit':'Back page only: outer 1.8mm edge extension over baked-in white/grey frame. No scaling; CMYK retained.','checks':checks,'visual_review':'pending'}
(B/'flyer-back-r02-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(report['sha256'])
