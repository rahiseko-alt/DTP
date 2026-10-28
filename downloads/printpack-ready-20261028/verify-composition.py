from pathlib import Path
from collections import Counter
import json,hashlib,math
import fitz
from PIL import Image,ImageChops,ImageDraw
B=Path(__file__).resolve().parent;R=B.parents[1];proof=json.load(open(B/'composition-proof.json'));results=[]
def image_hashes(d):return Counter(hashlib.sha256(d.xref_stream_raw(x)).hexdigest() for x in range(1,d.xref_length()) if d.xref_get_key(x,'Subtype')==('name','/Image'))
for o in proof['outputs']:
 a,b=fitz.open(R/o['source']['file']),fitz.open(R/o['corrected']);assert len(a)==len(b)==o['pages']
 for pn,(p,q) in enumerate(zip(a,b),1):
  pix=p.get_pixmap(matrix=fitz.Matrix(150/72,150/72),alpha=False);im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);new=q.get_pixmap(matrix=fitz.Matrix(150/72,150/72),alpha=False);out=Image.frombytes('RGB',(new.width,new.height),new.samples);diff=ImageChops.difference(im,out);regions=next((r['allowed_regions_source_pt'] for r in o['folio_changes'] if r['page']==pn),[])
  if regions:
   mask=Image.new('L',im.size,255);draw=ImageDraw.Draw(mask)
   for r in regions:draw.rectangle((math.floor(r[0]*150/72)-2,math.floor(r[1]*150/72)-2,math.ceil(r[2]*150/72)+2,math.ceil(r[3]*150/72)+2),fill=0)
   assert ImageChops.multiply(diff.convert('L'),mask).getbbox() is None,(o['label'],pn,'outside pagination areas changed')
  else:assert diff.getbbox() is None,(o['label'],pn,'unchanged page')
  if o['label']=='brochure' and pn in range(2,16):
   text=q.get_text(clip=fitz.Rect(0,q.rect.height-35,q.rect.width,q.rect.height));assert str(pn) in text,(pn,text)
 assert image_hashes(a)==image_hashes(b)
 if o['label']=='brochure':
  import re
  text=''.join(re.sub(r'\s+','',p.get_text()) for p in b);assert text.count('※掲載しているカリキュラム・授業内容・目標とする資格・検定は、変更となる場合があります。')==6
  for n in [12,13]:
   text=re.sub(r'\s+','',b[n-1].get_text());assert all(x in text for x in ['980,000円','880,000円','1,860,000円','上記金額には検定料2万円は含みません。'])
 results.append({'label':o['label'],'pages':len(a),'outside_folio_pixels_identical_150dpi':True,'original_image_streams_preserved':True,'fees_and_approved_notes_preserved':True})
(B/'composition-verification.json').write_text(json.dumps({'verified':True,'outputs':results},ensure_ascii=False,indent=2)+'\n');print(results,flush=True)
