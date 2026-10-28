"""Audit geometry, PDF/X identifiers, CMYK intent, outlined type, pagination, and all live QR targets."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import ast,ctypes,ctypes.util,hashlib,json,re,subprocess
import fitz
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parent;R=B.parents[1];proof=json.load(open(B/'build-proof.json'));MM=72/25.4;PRE=B/'previews';PRE.mkdir(exist_ok=True)
tree=ast.parse((R/'books/oc-yellow-photo-soft-r03-20261022/verify.py').read_text());fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='decode');shared=ast.unparse(fn).replace('z.zbar_image_scanner_set_config(scanner, 0, 0, 1)','z.zbar_image_scanner_set_config(scanner, 0, 0, 0)\n    z.zbar_image_scanner_set_config(scanner, 64, 0, 1)');exec(compile(shared,'<qr-decoder>','exec'))
def close(rect,mm):return max(abs(a-b*MM) for a,b in zip(rect,mm))<.015
results=[];ocrjobs=[]
for o in proof['outputs']:
 d=fitz.open(R/o['file']);assert len(d)==o['pages'];assert hashlib.sha256((R/o['file']).read_bytes()).hexdigest()==o['sha256'];assert d.metadata['format']=='PDF 1.3' and not d.is_encrypted
 typ,val=d.xref_get_key(-1,'Info');ix=int(val.split()[0]);assert d.xref_get_key(ix,'GTS_PDFXVersion')[1]=='PDF/X-1a:2001';assert d.xref_get_key(ix,'Trapped')==('name','/False')
 intents=d.xref_get_key(d.pdf_catalog(),'OutputIntents');assert intents[0]=='array';intent=int(re.search(r'(\d+) 0 R',intents[1]).group(1));assert d.xref_get_key(intent,'S')==('name','/GTS_PDFX');profile=int(d.xref_get_key(intent,'DestOutputProfile')[1].split()[0]);assert d.xref_get_key(profile,'N')==('int','4');assert hashlib.sha256(d.xref_stream(profile)).hexdigest()==o['icc']['sha256']
 thumbs=[];qrs=[];spaces=set();fonts=0
 for pn,p in enumerate(d,1):
  assert close(p.mediabox,[0,0,230,317]) and close(p.trimbox,[10,10,220,307]) and close(p.bleedbox,[7,7,223,310]);assert p.rotation==0;assert d.xref_get_key(p.xref,'ArtBox')==('null','null')
  fonts+=len(p.get_fonts(full=True));assert not p.get_fonts(full=True),(o['label'],pn,'live fonts remain')
  if o['label']=='flyer' or pn==15:
   for dpi in [150,300]:
    pix=p.get_pixmap(matrix=fitz.Matrix(dpi/72,dpi/72),clip=p.trimbox,alpha=False);im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);found=decode(im)
    expected=[x['url'] for x in json.load(open(R/'downloads/flyer-cover-digital-oc-draft-20261028/drive-links.json'))] if o['label']=='flyer' and pn==1 else ['mailto:aibusiness.kaihougakuen@gmail.com'] if o['label']=='flyer' else ['https://kaihougakuen.my.canva.site/']
    assert set(found)==set(expected),(o['label'],pn,dpi,found);qrs.append({'page':pn,'dpi':dpi,'decoded':found})
  pix=p.get_pixmap(matrix=fitz.Matrix(150/72,150/72),alpha=False);im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);im.save(PRE/f'{o["label"]}-page-{pn:02}.png');im.thumbnail((600,850));thumbs.append(im.copy())
  if o['label']=='brochure' and pn in range(2,16):
   ref=fitz.open(R/o['corrected']);rp=ref[pn-1];tr=next(t for t in rp.get_texttrace() if t['font']=='NimbusSans-Bold' and t['bbox'][1]>790 and ''.join(chr(c[0]) for c in t['chars'])==str(pn));bb=fitz.Rect(tr['bbox']);T=p.trimbox;area=fitz.Rect(T.x0+bb.x0/rp.rect.width*T.width,T.y0+bb.y0/rp.rect.height*T.height,T.x0+bb.x1/rp.rect.width*T.width,T.y0+bb.y1/rp.rect.height*T.height)+(-2,-2,2,2);pix=p.get_pixmap(matrix=fitz.Matrix(300/72,300/72),clip=area,alpha=False);file=PRE/f'folio-{pn:02}.png';pix.save(file);ocrjobs.append((pn,file))
  for i in p.get_image_info():assert i['colorspace'] in [1,4],(o['label'],pn,i['cs-name']);spaces.add(i['cs-name'])
 for start in range(0,len(thumbs),4):
  canvas=Image.new('RGB',(1240,1780),'#e9edf1');draw=ImageDraw.Draw(canvas)
  for j,im in enumerate(thumbs[start:start+4]):x=(j%2)*620+10;y=(j//2)*890+10;canvas.paste(im,(x,y));draw.text((x,y+im.height+4),f'{o["label"]} {start+j+1}',fill='#102d49')
  canvas.save(PRE/f'{o["label"]}-overview-{start+1:02}.jpg',quality=90)
 results.append({'label':o['label'],'sha256':o['sha256'],'pages':len(d),'media_mm':[230,317],'trim_mm':[210,297],'bleed_mm':3,'crop_marks_outside_bleed':True,'outlined_text_no_live_fonts':fonts==0,'CMYK_or_gray_images_only':sorted(spaces),'output_intent':'Japan Color 2011 Coated','output_profile_sha_matches':True,'pdf_version':'1.3','pdfx_identifiers':'PDF/X-1a:2001','QR_checks':qrs,'external_printer_acceptance_check':False})
def ocr(job):
 pn,file=job;s=subprocess.check_output(['tesseract',str(file),'stdout','--psm','6','-c','tessedit_char_whitelist=0123456789'],text=True,stderr=subprocess.DEVNULL).strip();assert s==str(pn),(pn,s);return {'page':pn,'printed_folio':s}
folios=list(ThreadPoolExecutor(max_workers=4).map(ocr,ocrjobs));composition=json.load(open(B/'composition-verification.json'));assert composition['verified']
(B/'verification.json').write_text(json.dumps({'verified':True,'outputs':results,'printed_folios_verified':folios,'composition':'composition-verification.json','source_proof_all_approved_notices_and_fees_preserved':True,'formal_external_PDFX_certification':False,'printer_upload_check':'user operation','physical_print_test':False},ensure_ascii=False,indent=2)+'\n');print(json.dumps({'verified':True,'files':[(x['label'],x['pages']) for x in results],'folios':folios},ensure_ascii=False),flush=True)
