from pathlib import Path
import json,hashlib,subprocess,concurrent.futures,collections,re,ctypes,ctypes.util
import fitz
from PIL import Image,ImageChops,ImageStat
from pypdf import PdfReader,PdfWriter
from pypdf.generic import NameObject,DictionaryObject
root=Path.cwd();work=root/'.cache/map-rollout';outdir=work/'print';outdir.mkdir(exist_ok=True);mm=72/25.4;sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
def asset(doc,aid):
 v=json.loads(subprocess.check_output(['node','--import','tsx','system/scripts/assets.ts','get','--document',doc,'--id',aid],text=True));return root/v['path'],v['asset']['sha256']
def decode(pix):
 z=ctypes.CDLL(ctypes.util.find_library('zbar'));P=ctypes.c_void_p
 for name,args,result in [('zbar_image_scanner_create',[],P),('zbar_image_create',[],P),('zbar_image_scanner_set_config',[P,ctypes.c_int,ctypes.c_int,ctypes.c_int],ctypes.c_int),('zbar_image_set_format',[P,ctypes.c_ulong],None),('zbar_image_set_size',[P,ctypes.c_uint,ctypes.c_uint],None),('zbar_image_set_data',[P,P,ctypes.c_ulong,P],None),('zbar_scan_image',[P,P],ctypes.c_int),('zbar_image_first_symbol',[P],P),('zbar_symbol_next',[P],P),('zbar_symbol_get_data',[P],ctypes.c_char_p)]:
  f=getattr(z,name);f.argtypes=args;f.restype=result
 im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples).convert('L');buf=ctypes.create_string_buffer(im.tobytes());scanner=z.zbar_image_scanner_create();image=z.zbar_image_create();z.zbar_image_scanner_set_config(scanner,0,0,1);z.zbar_image_set_format(image,int.from_bytes(b'Y800','little'));z.zbar_image_set_size(image,*im.size);z.zbar_image_set_data(image,buf,len(im.tobytes()),None);z.zbar_scan_image(scanner,image);symbol=z.zbar_image_first_symbol(image);found=[]
 while symbol:found.append(z.zbar_symbol_get_data(symbol).decode());symbol=z.zbar_symbol_next(symbol)
 return found
GS=['-sDEVICE=pdfwrite','-dCompatibilityLevel=1.7','-dNOPAUSE','-dBATCH','-dSAFER','-dColorConversionStrategy=/RGB','-sColorConversionStrategy=RGB','-dDownsampleColorImages=true','-dColorImageResolution=200','-dColorImageDownsampleType=/Bicubic','-dAutoFilterColorImages=false','-dColorImageFilter=/DCTEncode','-dDownsampleGrayImages=true','-dGrayImageResolution=200','-dGrayImageDownsampleType=/Bicubic','-dAutoFilterGrayImages=false','-dGrayImageFilter=/DCTEncode','-dDownsampleMonoImages=true','-dMonoImageResolution=600','-dJPEGQ=88','-dCompressFonts=true','-dSubsetFonts=true','-dDetectDuplicateImages=true']
amounts=lambda p:collections.Counter(re.findall(r'\d{1,3}(?:,\d{3})+円',re.sub(r'\s+','',p.get_text())))
def thumb(p):
 pix=p.get_pixmap();return Image.frombytes('RGB',(pix.width,pix.height),pix.samples).resize((320,226),Image.Resampling.LANCZOS)
all_records=[]
for doc,prefix,aid,bleed in [('prospectus-isen-trial-2028','brochure','latest-prospectus-pdf',0),('admissions-guide-2027','admissions','standard-rendered-pdf',3)]:
 source,expected=asset(doc,aid);assert sha(source)==expected;src=fitz.open(source);n=len(src);assert n in [16,24]
 faces=[{'sheet':k+1,'side':side,'left':left,'right':right} for k in range(n//4) for side,left,right in [('front',n-2*k,1+2*k),('back',2+2*k,n-1-2*k)]]
 assert sorted(p for f in faces for p in [f['left'],f['right']])==list(range(1,n+1))
 tasks=[]
 for paper,width,height in [('A3',420,297),('A4',297,210)]:
  raw=outdir/f'{prefix}-{paper}-raw.pdf';pdf=fitz.open()
  for f in faces:
   page=pdf.new_page(width=width*mm,height=height*mm)
   for side,pn in enumerate([f['left'],f['right']]):
    rect=src[pn-1].rect;b=bleed*mm;clip=fitz.Rect(b,b,rect.width-b,rect.height-b);target=fitz.Rect(side*width/2*mm,0,(side+1)*width/2*mm,height*mm);page.show_pdf_page(target,src,pn-1,clip=clip)
  pdf.save(raw,garbage=4,deflate=True);pdf.close();tasks.append((paper,raw))
 def finish(task):
  paper,raw=task;gs=outdir/f'{prefix}-{paper}-gs.pdf';final=outdir/f'print-{prefix}-{paper}.pdf'
  subprocess.run(['gs',*GS,f'-sOutputFile={gs}',str(raw)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
  writer=PdfWriter(clone_from=gs);writer._root_object[NameObject('/ViewerPreferences')]=DictionaryObject({NameObject('/Duplex'):NameObject('/DuplexFlipShortEdge'),NameObject('/PrintScaling'):NameObject('/None'),NameObject('/Direction'):NameObject('/L2R')})
  with final.open('wb') as f:writer.write(f)
  return paper,raw,final
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex: finished=list(ex.map(finish,tasks))
 outputs=[]
 for paper,raw,final in finished:
  before,after=fitz.open(raw),fitz.open(final);assert len(before)==len(after)==n//2;deltas=[]
  for i,(a,b) in enumerate(zip(before,after)):
   assert a.rotation==b.rotation==0 and abs(a.rect.width-b.rect.width)<.02 and abs(a.rect.height-b.rect.height)<.02
   assert amounts(a)==amounts(b),(doc,paper,i,'currency')
   want=amounts(src[faces[i]['left']-1])+amounts(src[faces[i]['right']-1]);assert amounts(a)==want
   delta=sum(ImageStat.Stat(ImageChops.difference(thumb(a),thumb(b))).mean)/3;assert delta<4,(doc,paper,i,delta);deltas.append(delta)
  qr=decode(after[1].get_pixmap(matrix=fitz.Matrix(150/72,150/72)));assert 'https://kaihougakuen.my.canva.site/' in qr,qr
  outputs.append({'paper':paper,'file':str(final.relative_to(root)),'sha256':sha(final),'bytes':final.stat().st_size,'faces':len(after),'all_face_comparisons':deltas,'qr_decoded':qr,'currency_counts_unchanged':True,'duplex':'short-edge','scaling':'none'})
 record={'document':doc,'source_id':aid,'source_file':str(source.relative_to(root)),'source_sha256':expected,'pages':n,'sheets':n//4,'faces':faces,'outputs':outputs,'method':'A3/A4横、1面に2ページ、短辺反転。200dpi/JPEG88の軽量化後に全印刷面を照合。','self_review':True,'independent_review':False,'physical_print_test':False};(work/f'{prefix}-print-proof.json').write_text(json.dumps(record,ensure_ascii=False,indent=2));all_records.append(record);print(prefix,[(v['paper'],v['bytes']) for v in outputs],flush=True)
(work/'all-print-proofs.json').write_text(json.dumps(all_records,ensure_ascii=False,indent=2))
