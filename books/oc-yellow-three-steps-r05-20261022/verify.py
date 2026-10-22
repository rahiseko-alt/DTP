"""Check unchanged regions, all four decoded QRs, and three native headings."""
from pathlib import Path
import ast, ctypes, ctypes.util, hashlib, json
import fitz
from PIL import Image, ImageChops, ImageDraw
B=Path(__file__).resolve().parent
R=B.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
proof=json.loads((B/'reviews/build-proof.json').read_text())
source=R/proof['source']['file'];output=R/proof['pdf']
assert sha(source)==proof['source']['sha256'] and sha(output)==proof['pdf_sha256']
decoder=ast.parse((R/'books/oc-yellow-photo-soft-r03-20261022/verify.py').read_text())
function=next(n for n in decoder.body if isinstance(n,ast.FunctionDef) and n.name=='decode')
exec(compile(ast.Module(body=[function],type_ignores=[]),'<shared-qr-decoder>','exec'))
before=fitz.open(source);after=fitz.open(output)
assert len(after)==2
text=''.join(after[1].get_text().split())
for title in ['学校説明','体験授業','個別相談']:assert text.count(title)==1,title
assert '在校生交流' not in text
records=[]
for i in range(2):
    assert before[i].rect==after[i].rect
    p=before[i].get_pixmap(matrix=fitz.Matrix(150/72,150/72))
    old=Image.frombytes('RGB',(p.width,p.height),p.samples)
    current=Image.open(B/f'output/page-{i+1}.png').convert('RGB')
    diff=ImageChops.difference(old,current)
    if i==0:
        assert diff.getbbox() is None,'Front changed'
    else:
        mask=Image.new('L',old.size,255)
        x0,y0,x1,y1=proof['back_change_rect_pt']
        ImageDraw.Draw(mask).rectangle((x0*150/72-2,y0*150/72-2,x1*150/72+2,y1*150/72+2),fill=0)
        assert ImageChops.multiply(diff.convert('L'),mask).getbbox() is None,'Outside back flow changed'
    png_qr=decode(current)
    pix=after[i].get_pixmap(matrix=fitz.Matrix(2,2))
    pdf_qr=decode(Image.frombytes('RGB',(pix.width,pix.height),pix.samples))
    assert png_qr==pdf_qr==['mailto:aibusiness.kaihougakuen@gmail.com']
    records.append({'page':i+1,'png_sha256':sha(B/f'output/page-{i+1}.png'),'png_qr':png_qr,'pdf_qr':pdf_qr,'outside_requested_area_pixels_identical':True})
record={'pdf_sha256':sha(output),'verified':True,'front_pixels_identical':True,'back_outside_flow_pixels_identical':True,'retained_steps':['学校説明','体験授業','個別相談'],'photos_unchanged':True,'pages':records,'independent_review':False,'print_test':False}
(B/'reviews/output-verification.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(record,ensure_ascii=False,indent=2))
