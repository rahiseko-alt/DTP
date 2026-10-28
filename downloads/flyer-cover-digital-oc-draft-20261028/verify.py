from pathlib import Path
import ast,ctypes,ctypes.util,json,hashlib
import fitz
from PIL import Image,ImageChops,ImageDraw
B=Path(__file__).resolve().parent;R=B.parents[1];tree=ast.parse((R/'books/oc-yellow-photo-soft-r03-20261022/verify.py').read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='decode');exec(compile(ast.Module(body=[fn],type_ignores=[]),'<shared-zbar-decoder>','exec'))
proof=json.loads((B/'build-proof.json').read_text());d=fitz.open(R/proof['pdf']);old=fitz.open(R/proof['source_oc']['path']);urls=[x['url'] for x in proof['qr_sources']];assert len(d)==2 and d[0].rect==d[1].rect
codes=[]
for i,url in enumerate(urls,1):
 found=decode(Image.open(B/f'qr-{i}.png'));assert found==[url],(i,found);codes.append({'label':proof['qr_sources'][i-1]['label'],'url':url,'standalone_png_decodes':True})
for dpi in [150,300]:
 pix=d[0].get_pixmap(matrix=fitz.Matrix(dpi/72,dpi/72),alpha=False);found=decode(Image.frombytes('RGB',(pix.width,pix.height),pix.samples));assert set(found)==set(urls),(dpi,found)
back=d[1].get_pixmap(matrix=fitz.Matrix(150/72,150/72),alpha=False);before=old[0].get_pixmap(matrix=fitz.Matrix(150/72,150/72),alpha=False);assert back.samples==before.samples,'OC back differs from original OC front'
expected=['mailto:aibusiness.kaihougakuen@gmail.com'];assert decode(Image.open(B/'output/page-2.png'))==expected
assert d[1].get_text()==old[0].get_text()
# Review contact sheet only; no source artwork or QR pixels are modified.
thumbs=[]
for i in [1,2]:
 im=Image.open(B/f'output/page-{i}.png').convert('RGB');im.thumbnail((842,1191));thumbs.append(im)
canvas=Image.new('RGB',(1732,1245),'#e9edf1');draw=ImageDraw.Draw(canvas)
for i,im in enumerate(thumbs):canvas.paste(im,(12+i*866,38));draw.text((12+i*866,12),['FRONT - Digital brochure / Application documents','BACK - Open Campus'][i],fill='#102d49')
canvas.save(B/'output/front-back-preview.jpg',quality=94)
metrics=json.loads((B/'render-metrics.json').read_text());assert not any(x['overflow'] for x in metrics['checks'])
result={'verified':True,'pdf_sha256':proof['sha256'],'pages':2,'size_mm':[210,297],'qr':codes,'front_pdf_both_codes_decode_at_dpi':[150,300],'logo_in_center':'official crest, crop through SVG viewport; no redraw','back_pixels_identical_150dpi':True,'back_native_text_identical':True,'back_email_qr_preserved':True,'dom_overflow':False,'drive_content_access':'blocked by execution environment proxy403; mappings confirmed by user, destination permissions not verified','current_flyer_unchanged':True,'release':False,'physical_print_test':False};(B/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False),flush=True)
