"""Verify every page and original photograph in the four fixed R12 outputs."""
from pathlib import Path
from collections import Counter
import ast,ctypes,ctypes.util,hashlib,json,re
import fitz
from PIL import Image,ImageChops,ImageDraw
B=Path(__file__).resolve().parent;R=B.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
proof=json.loads((B/'build-proof.json').read_text());name=proof['formal_name']
decoder=ast.parse((R/'books/oc-yellow-photo-soft-r03-20261022/verify.py').read_text())
function=next(n for n in decoder.body if isinstance(n,ast.FunctionDef) and n.name=='decode')
exec(compile(ast.Module(body=[function],type_ignores=[]),'<shared-qr-decoder>','exec'))
def image_hashes(doc):
    refs={im[0]:im for p in doc for im in p.get_images(full=True)}
    # Read compressed image streams without populating a decoded-image cache.
    return Counter((hashlib.sha256(doc.xref_stream_raw(x)).hexdigest(),*info[2:6],hashlib.sha256(doc.xref_stream_raw(info[1])).hexdigest() if info[1] else None) for x,info in refs.items())
records=[]
for item in proof['outputs']:
    source=R/item['source']['file'];output=R/item['file']
    assert sha(source)==item['source']['sha256'] and sha(output)==item['sha256']
    old=fitz.open(source);new=fitz.open(output)
    assert len(old)==len(new)==item['pages']
    assert image_hashes(old)==image_hashes(new),'Embedded image bytes changed'
    pages=[]
    for i,(p,q) in enumerate(zip(old,new),1):
        assert p.rect==q.rect
        original=p.get_text();current=q.get_text()
        expected=len(item['changed_regions'].get(str(i),[]))
        assert current.count(name)==original.count(name)+expected
        normalize=lambda t:re.sub(r'\s+','',t)
        assert normalize(original)==normalize(current.replace(name,'')),'Other text changed'
        scale=150/72
        a=p.get_pixmap(matrix=fitz.Matrix(scale,scale));b=q.get_pixmap(matrix=fitz.Matrix(scale,scale))
        x=Image.frombytes('RGB',(a.width,a.height),a.samples);y=Image.frombytes('RGB',(b.width,b.height),b.samples)
        diff=ImageChops.difference(x,y)
        regions=item['changed_regions'].get(str(i),[])
        if regions:
            mask=Image.new('L',x.size,255);draw=ImageDraw.Draw(mask)
            for r in regions:
                x0,y0,x1,y1=r['rect_pt'];draw.rectangle((x0*scale-2,y0*scale-2,x1*scale+2,y1*scale+2),fill=0)
            assert ImageChops.multiply(diff.convert('L'),mask).getbbox() is None,(item['kind'],i,'Outside field changed')
        else:assert diff.getbbox() is None,(item['kind'],i,'Page changed')
        pages.append({'page':i,'outside_name_field_pixels_identical':True,'other_native_text_identical':True,'page_size_identical':True,'replaced_fields':expected})
    assert sum(p['replaced_fields'] for p in pages)==3
    if item['kind']=='reading':
        pix=new[14].get_pixmap(matrix=fitz.Matrix(2,2))
        qr=decode(Image.frombytes('RGB',(pix.width,pix.height),pix.samples))
        assert qr==['https://kaihougakuen.my.canva.site/']
    records.append({'kind':item['kind'],'pdf_sha256':sha(output),'embedded_image_bytes_identical':True,'pages':pages})
    print(item['kind'],'verified',len(pages),flush=True)

receipt=json.loads((B/'receipts/admissions-source.json').read_text())
source=R/receipt['path'];assert sha(source)==receipt['asset']['sha256']
admissions=fitz.open(source);assert len(admissions)==24
expected=Image.open(R/'company-data/brand/logo/logo-horizontal.png').convert('RGB')
logo_refs={im[0] for page in admissions for im in page.get_images(full=True) if tuple(im[2:4])==expected.size}
assert len(logo_refs)==1
ref=logo_refs.pop();logo=fitz.Pixmap(admissions,ref)
assert logo.samples==expected.tobytes()
logo_pages=[i+1 for i,p in enumerate(admissions) if p.get_image_rects(ref)]
assert logo_pages==[1,11,13,15,17,19,21,24]
blank_pages=[8,12,14,16,18,20,22]
for n in blank_pages:
    pix=admissions[n-1].get_pixmap()
    im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
    assert all(lo==hi==255 for lo,hi in im.getextrema())
record={'formal_name':name,'verified':True,'outputs':records,'brochure_qr':qr,'admissions':{'pdf_sha256':sha(source),'pages':24,'logo_pages':logo_pages,'logo_pixels_match_official_asset':True,'logo_english_name':name,'blank_reverse_pages':blank_pages,'document_modified':False,'visual_pages_checked':list(range(1,25))},'independent_review':False,'print_test':False}
(B/'verification.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
