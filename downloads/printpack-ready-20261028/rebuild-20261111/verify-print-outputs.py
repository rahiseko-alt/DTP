"""Check actual CMYK outline PDFs against their separate live-text masters."""
from pathlib import Path
from decimal import Decimal
from collections import Counter
import fitz,pikepdf,numpy as np,zxingcpp,json,hashlib,sys,subprocess,os
B=Path(__file__).resolve().parent;A=B/'inspection/final';A.mkdir(parents=True,exist_ok=True)
def images(p):return Counter((x['width'],x['height'],x['colorspace']) for x in p.get_image_info())
def decoded_images(doc,p):
 return Counter((x[2],x[3],hashlib.sha256(fitz.Pixmap(doc,x[0]).samples).hexdigest()) for x in p.get_images())
for label in sys.argv[1:] or ['brochure','flyer']:
 native=B/(label+'-CMYK-text-master.pdf');out=B/(label+'-CMYK-outline-print.pdf');nd,od=fitz.open(native),fitz.open(out);assert len(nd)==len(od)==(16 if label=='brochure' else 2)
 rows=[]
 with pikepdf.open(out) as pdf:
  assert pdf.Root.OutputIntents[0].DestOutputProfile.N==4
  for page in pdf.pages:
   for key in ['/MediaBox','/CropBox']:
    box=[Decimal(str(v)) for v in page.obj[key]];mm=[(box[2]-box[0])*Decimal('25.4')/72,(box[3]-box[1])*Decimal('25.4')/72];assert abs(mm[0]-210)<Decimal('.00000001') and abs(mm[1]-297)<Decimal('.00000001')
 with pikepdf.open(native) as pdf:
  embedded=[]
  for f in pdf.objects:
   if not isinstance(f,pikepdf.Dictionary) or f.get('/Type')!=pikepdf.Name('/Font'):continue
   if '/DescendantFonts' in f:continue
   descriptor=f.get('/FontDescriptor')
   if descriptor is not None:assert any(k in descriptor for k in ['/FontFile','/FontFile2','/FontFile3']),str(f.get('/BaseFont'))
 for i,p in enumerate(od):
  assert not p.get_fonts() and not p.get_text().strip()
  assert images(p)==images(nd[i]),(label,i+1,'Raster image inventory changed during outline conversion')
  assert decoded_images(nd,nd[i])==decoded_images(od,p),(label,i+1,'Photo pixels changed during outline conversion')
  assert set(x['colorspace'] for x in p.get_image_info())<={1,4}
  # Embedded fonts use raster hinting; vector outlines do not. Compare the
  # actual raster difference and additionally require lossless image identity.
  a=nd[i].get_pixmap(matrix=fitz.Matrix(150/72,150/72),alpha=False);b=p.get_pixmap(matrix=fitz.Matrix(150/72,150/72),alpha=False);aa=np.frombuffer(a.samples,np.uint8);bb=np.frombuffer(b.samples,np.uint8);delta=np.abs(aa.astype(np.int16)-bb.astype(np.int16));mean=float(delta.mean());fraction=float(np.mean(delta>20));assert mean<2.5 and fraction<.04,(label,i+1,mean,fraction)
  b.save(A/f'{label}-{i+1:02}.png');qrs={}
  if label=='flyer' or i==14:
   for dpi in [150,300]:
    values=[]
    for pp in [nd[i],p]:
     pix=pp.get_pixmap(matrix=fitz.Matrix(dpi/72,dpi/72),alpha=False);im=np.frombuffer(pix.samples,np.uint8).reshape(pix.height,pix.width,pix.n);values.append(sorted(x.text for x in zxingcpp.read_barcodes(im)))
    assert values[0] and values[0]==values[1],(label,i+1,dpi,values);qrs[str(dpi)]=values[1]
  rows.append({'page':i+1,'native_characters':len(nd[i].get_text()),'print_fonts':0,'CMYK_or_Gray_images':True,'raster_inventory_matches_native':True,'decoded_photo_pixels_unchanged_by_outlining':True,'outline_vs_native_150dpi_mean_channel_delta':mean,'outline_vs_native_channels_delta_over20_fraction':fraction,'QR':qrs})
  print(label,i+1,round(mean,6),qrs,flush=True)
 # A second renderer must parse and render every actual final page.
 prefix=A/(label+'-poppler');result=subprocess.run(['pdftoppm','-r','72','-jpeg',str(out),str(prefix)],capture_output=True,text=True,env={**os.environ,'XDG_CACHE_HOME':'/workspace/.dtp-cache'})
 assert result.returncode==0,(label,result.stderr)
 errors=[s for s in result.stderr.splitlines() if 'Error' in s or 'Warning' in s and 'Fontconfig' not in s];assert not errors,errors
 report={'status':'technical_checks_pass_parent_visual_review_required','label':label,'print_file':out.name,'print_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'native_file':native.name,'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'pages':rows,'Poppler_exit':result.returncode,'Poppler_stderr':result.stderr,'independent_review_scope':'See strict-* files for individual part SHA reviews; no claim of independent final-file review when quota prevented it.','physical_printer_check':'not_performed','font_shape_fidelity':'Replacement live fonts reproduce original measured layout; source raster handwriting and some glyph shapes differ.'}
 (B/(label+'-final-technical-check.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
