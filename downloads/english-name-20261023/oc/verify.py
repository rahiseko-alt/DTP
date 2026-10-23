"""Validate the two English-name fields without changing the OC artwork."""
from pathlib import Path
from collections import Counter
import ast,ctypes,ctypes.util,hashlib,json,re
import fitz
from PIL import Image,ImageChops,ImageDraw
B=Path(__file__).resolve().parent;R=B.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
proof=json.loads((B/'build-proof.json').read_text());source=R/proof['source']['file'];output=R/proof['pdf']
assert sha(source)==proof['source']['sha256'] and sha(output)==proof['pdf_sha256']
tree=ast.parse((R/'books/oc-yellow-photo-soft-r03-20261022/verify.py').read_text())
function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='decode')
exec(compile(ast.Module(body=[function],type_ignores=[]),'<shared-qr-decoder>','exec'))
old=fitz.open(source);new=fitz.open(output);assert len(old)==len(new)==2
def photos(doc):
    refs={x[0]:x for p in doc for x in p.get_images(full=True)}
    # extract_image can change MuPDF's cached rendering of an ICC image.
    # Hash stored streams directly, preserving a fresh PDF render for pixel QA.
    return Counter((hashlib.sha256(doc.xref_stream_raw(x)).hexdigest(),*info[2:6],hashlib.sha256(doc.xref_stream_raw(info[1])).hexdigest() if info[1] else None) for x,info in refs.items())
assert photos(old)==photos(new)
assert new[0].get_text().count(proof['formal_name'])==2
normalize=lambda t:re.sub(r'\s+','',t)
assert normalize(old[0].get_text())==normalize(new[0].get_text().replace(proof['formal_name'],''))
records=[]
for i,(before,after) in enumerate(zip(old,new)):
    assert before.rect==after.rect
    scale=150/72;a=before.get_pixmap(matrix=fitz.Matrix(scale,scale));b=after.get_pixmap(matrix=fitz.Matrix(scale,scale))
    original=Image.frombytes('RGB',(a.width,a.height),a.samples);current=Image.frombytes('RGB',(b.width,b.height),b.samples)
    diff=ImageChops.difference(original,current)
    if i==0:
        mask=Image.new('L',original.size,255);draw=ImageDraw.Draw(mask)
        for field in proof['fields']:
            x0,y0,x1,y1=field['rect_pt'];draw.rectangle((x0*scale-2,y0*scale-2,x1*scale+2,y1*scale+2),fill=0)
        assert ImageChops.multiply(diff.convert('L'),mask).getbbox() is None
        for x0,y0,x1,y1 in [(10,8,90,84),(10,771,76,839)]:
            assert diff.crop((x0*scale,y0*scale,x1*scale,y1*scale)).getbbox() is None,'Crest changed'
    else:
        assert diff.getbbox() is None,'Back changed'
        assert before.get_text()==after.get_text()
    png=Image.open(B/f'output/page-{i+1}.png').convert('RGB');assert ImageChops.difference(png,current).getbbox() is None
    pix=after.get_pixmap(matrix=fitz.Matrix(2,2));pdf_qr=decode(Image.frombytes('RGB',(pix.width,pix.height),pix.samples));png_qr=decode(png)
    assert pdf_qr==png_qr==['mailto:aibusiness.kaihougakuen@gmail.com']
    records.append({'page':i+1,'png_sha256':sha(B/f'output/page-{i+1}.png'),'outside_english_fields_pixels_identical':True,'page_size_identical':True,'png_qr':png_qr,'pdf_qr':pdf_qr})
record={'pdf_sha256':sha(output),'source_sha256':sha(source),'verified':True,'embedded_image_bytes_identical':True,'crests_pixel_identical':True,'back_page_pixel_identical':True,'formal_name_occurrences':2,'other_native_text_identical':True,'pages':records,'independent_review':False,'print_test':False}
(B/'verification.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print(json.dumps(record,ensure_ascii=False,indent=2))
