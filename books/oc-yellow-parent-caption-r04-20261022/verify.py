"""Verify R04's two permitted front regions, exact back pixels and four QRs."""
from pathlib import Path
import ast, ctypes, ctypes.util, hashlib, json, re, unicodedata
import fitz
from PIL import Image, ImageChops, ImageDraw

B=Path(__file__).resolve().parent;R=B.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
proof=json.loads((B/'reviews/build-proof.json').read_text())
source=R/proof['source']['file'];output=R/proof['pdf']
assert sha(source)==proof['source']['sha256'] and sha(output)==proof['pdf_sha256']
# Reuse only the existing pure QR decoder function, without running that
# earlier edition's verifier or writing any of its files.
decoder=ast.parse((R/'books/oc-yellow-photo-soft-r03-20261022/verify.py').read_text())
function=next(n for n in decoder.body if isinstance(n,ast.FunctionDef) and n.name=='decode')
exec(compile(ast.Module(body=[function],type_ignores=[]),'<shared-qr-decoder>','exec'))
before=fitz.open(source);after=fitz.open(output)
assert len(after)==2
text=unicodedata.normalize('NFKC',re.sub(r'\s+','',''.join(after[0].get_text())))
assert text.count('保護者の参加も歓迎')==1
for old in ['在校生と話せる','留学生と話せる','学校生活や日本での生活を','直接聞けます。']:assert old not in text,old
for kept in ['11/21','12/5','12/19','授業を体験','進路を相談できる','お子さまと一緒に','ご参加いただけます。','aibusiness.kaihougakuen@gmail.com']:assert kept in text,kept
results=[]
for i in range(2):
 assert before[i].rect==after[i].rect
 pix=before[i].get_pixmap(matrix=fitz.Matrix(150/72,150/72));old=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
 current=Image.open(B/f'output/page-{i+1}.png').convert('RGB')
 diff=ImageChops.difference(old,current)
 if i==0:
  mask=Image.new('L',old.size,255);draw=ImageDraw.Draw(mask)
  for x0,y0,x1,y1 in proof['front_change_rects_pt']:draw.rectangle((x0*150/72-2,y0*150/72-2,x1*150/72+2,y1*150/72+2),fill=0)
  assert ImageChops.multiply(diff.convert('L'),mask).getbbox() is None
  # Cover the full rendered badge outline, including the edge of the clipped
  # source form, without touching the date ovals above it.
  rect=fitz.Rect(proof['front_change_rects_pt'][0]);crop=current.crop((int(rect.x0*150/72)+2,int(rect.y0*150/72)+4,int(rect.x1*150/72)-2,int(rect.y1*150/72)-2))
  assert all(lo>=250 for lo,hi in crop.getextrema()),'Badge outline remains'
 else:assert diff.getbbox() is None,'Back page changed'
 png_qr=decode(current)
 pix=after[i].get_pixmap(matrix=fitz.Matrix(2,2));pdf_qr=decode(Image.frombytes('RGB',(pix.width,pix.height),pix.samples))
 assert png_qr==pdf_qr==['mailto:aibusiness.kaihougakuen@gmail.com']
 results.append({'page':i+1,'png_sha256':sha(B/f'output/page-{i+1}.png'),'png_qr':png_qr,'pdf_qr':pdf_qr,'outside_front_edit_regions_pixel_equal':True,'entire_back_pixel_equal':i==1})
record={'pdf_sha256':sha(output),'source_sha256':sha(source),'verified':True,'photos_pixel_unchanged':True,'front_parent_welcome_text_count':1,'old_middle_heading_and_explanation_removed':True,'back_entire_page_pixel_equal':True,'pages':results,'independent_review':False,'print_test':False}
(B/'reviews/output-verification.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(record,ensure_ascii=False,indent=2))
