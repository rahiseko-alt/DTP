"""Verify the notice and every unchanged page in all four R13 PDFs."""
from pathlib import Path
from collections import Counter
import ast,ctypes,ctypes.util,hashlib,json,re,subprocess,sys,tempfile
import fitz
from PIL import Image,ImageChops,ImageDraw
B=Path(__file__).resolve().parent;R=B.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
proof=json.loads((B/'build-proof.json').read_text());notice=proof['notice']
assert sha(B/'notice.json')==proof['notice_source_sha256']
normalize=lambda s:re.sub(r'\s+','',s)
note=normalize(''.join(notice['lines']))
decoder=ast.parse((R/'books/oc-yellow-photo-soft-r03-20261022/verify.py').read_text())
function=next(n for n in decoder.body if isinstance(n,ast.FunctionDef) and n.name=='decode')
exec(compile(ast.Module(body=[function],type_ignores=[]),'<shared-qr-decoder>','exec'))
def image_hashes(doc):
    refs={im[0]:im for p in doc for im in p.get_images(full=True)}
    return Counter((sha_bytes(doc.xref_stream_raw(x)),*info[2:6],sha_bytes(doc.xref_stream_raw(info[1])) if info[1] else None) for x,info in refs.items())
def sha_bytes(b):return hashlib.sha256(b).hexdigest()
records=[]
for item in proof['outputs']:
    source=R/item['source']['file'];output=R/item['file']
    assert sha(source)==item['source']['sha256'] and sha(output)==item['sha256']
    old=fitz.open(source);new=fitz.open(output)
    assert len(old)==len(new)==item['pages']
    assert image_hashes(old)==image_hashes(new),'Embedded image bytes changed'
    render_tmp=tempfile.TemporaryDirectory(prefix='dtp-notice-verify-')
    render_root=Path(render_tmp.name)
    for label,path in [('old',source),('new',output)]:
        subprocess.run([sys.executable,str(B/'render-previews.py'),str(path),str(render_root/label)],check=True)
    pages=[]
    for i,(p,q) in enumerate(zip(old,new),1):
        assert p.rect==q.rect
        regions=item['changed_regions'].get(str(i),[])
        original=normalize(p.get_text());current=normalize(q.get_text())
        if regions:
            assert current.count(note)==1,'Missing or duplicate notice'
            assert current.replace(note,'')==original,'Other native text changed'
        else:assert current==original,'Other page text changed'
        scale=150/72
        x=Image.open(render_root/f'old/page-{i:02}.png').convert('RGB')
        y=Image.open(render_root/f'new/page-{i:02}.png').convert('RGB')
        diff=ImageChops.difference(x,y)
        if regions:
            assert diff.getbbox() is not None,'Notice was not rendered'
            mask=Image.new('L',x.size,255);draw=ImageDraw.Draw(mask)
            for r in regions:
                x0,y0,x1,y1=r['rect_pt'];draw.rectangle((x0*scale-2,y0*scale-2,x1*scale+2,y1*scale+2),fill=0)
            assert ImageChops.multiply(diff.convert('L'),mask).getbbox() is None,(item['kind'],i,'Outside notice changed')
            assert item['notice_font_size_pt']>=6.5,'Notice is below 6.5pt in this output'
            fonts=[f[3] for f in q.get_fonts(full=True)]
            assert any('NotoSansJP' in f for f in fonts),fonts
        else:assert diff.getbbox() is None,(item['kind'],i,'Page changed')
        if item['kind']=='reading':
            preview=Image.open(B/f'output/page-{i:02}.png').convert('RGB')
            assert ImageChops.difference(preview,y).getbbox() is None,'Preview differs from PDF'
        pages.append({'page':i,'outside_notice_pixels_identical':True,'other_native_text_identical':True,'page_size_identical':True,'notice_added':bool(regions)})
    assert sum(p['notice_added'] for p in pages)==1
    records.append({'kind':item['kind'],'pdf_sha256':sha(output),'embedded_image_bytes_identical':True,'notice_font_size_pt':item['notice_font_size_pt'],'pages':pages})
    render_tmp.cleanup()
    print(item['kind'],'verified',len(pages),flush=True)

reading=fitz.open(B/'output/brochure-jp-r13.pdf')
pix=reading[14].get_pixmap(matrix=fitz.Matrix(2,2))
qr=decode(Image.frombytes('RGB',(pix.width,pix.height),pix.samples))
assert qr==['https://kaihougakuen.my.canva.site/']
record={'verified':True,'render_method':'fresh process per PDF; no text or image extraction before rendering','outputs':records,'brochure_qr':qr,'user_consent_record':'company-data/ledger.md: パンフレット掲載人物画像の承諾','independent_review':False,'print_test':False,'release':False}
(B/'verification.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
