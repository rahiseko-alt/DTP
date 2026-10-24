"""Check content retention, photo removal, all pages, and booklet placement."""
from pathlib import Path
import ast,ctypes,ctypes.util,hashlib,json,re,subprocess,sys,tempfile
from collections import Counter
import fitz
from PIL import Image,ImageChops,ImageDraw
B=Path(__file__).resolve().parent;R=B.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
proof=json.loads((B/'build-proof.json').read_text());source=R/proof['source']['file']
assert sha(source)==proof['source']['sha256']
norm=lambda s:re.sub(r'\s+','',s)
decoder=ast.parse((R/'books/oc-yellow-photo-soft-r03-20261022/verify.py').read_text())
function=next(n for n in decoder.body if isinstance(n,ast.FunctionDef) and n.name=='decode')
exec(compile(ast.Module(body=[function],type_ignores=[]),'<shared-qr-decoder>','exec'))
old=fitz.open(source);new=fitz.open(B/'output/admissions-plain-2027-r01.pdf')
assert len(old)==len(new)==24
images={im[0]:im for p in new for im in p.get_images(full=True)}
streams={hashlib.sha256(new.xref_stream_raw(x)).hexdigest() for x in images}
assert not streams.intersection(p['source_image_sha256'] for p in proof['removed_photographs'])
assert proof['retained_logo_stream_sha256'] in streams
assert proof['retained_map_stream_sha256'] in streams
assert all(tuple(info[2:4]) in [(1121,274),(3072,2048),(1,1)] for info in images.values()),'Unexpected image retained/introduced'
assert sorted({tuple(im[2:4]) for im in images.values() if min(im[2:4])>1})==[(1121,274),(3072,2048)]
with tempfile.TemporaryDirectory(prefix='dtp-plain-verify-') as tmp:
    temp=Path(tmp)
    for label,path in [('old',source),('new',B/'output/admissions-plain-2027-r01.pdf')]:
        subprocess.run([sys.executable,str(B/'render-previews.py'),str(path),str(temp/label)],check=True)
    pages=[]
    for i,(p,q) in enumerate(zip(old,new),1):
        assert p.rect==q.rect,(i,'size changed')
        original=p.get_text();current=q.get_text();regions=proof['changed_regions'].get(str(i),[])
        if i==1:
            c=proof['cover_copy'];required=[c['intake'],''.join(c['title_lines']),c['lead'],c['corporation'],c['forms_pages'],c['forms_notice']]+[v for course in c['courses'] for v in course.values()]
            assert all(norm(t) in norm(current) for t in required),'Cover information missing'
        else:
            caption=proof['removed_captions'].get(str(i),'')
            assert norm(original.replace(caption,''))==norm(current),(i,'Other text changed')
        a=Image.open(temp/f'old/page-{i:02}.png').convert('RGB');b=Image.open(temp/f'new/page-{i:02}.png').convert('RGB')
        diff=ImageChops.difference(a,b)
        if regions:
            mask=Image.new('L',a.size,255);draw=ImageDraw.Draw(mask);scale=150/72
            for reg in regions:
                x0,y0,x1,y1=reg['rect_pt'];draw.rectangle((x0*scale-2,y0*scale-2,x1*scale+2,y1*scale+2),fill=0)
            assert ImageChops.multiply(diff.convert('L'),mask).getbbox() is None,(i,'Outside photo/cover region changed')
        else:assert diff.getbbox() is None,(i,'Unchanged page differs')
        png=Image.open(B/f'output/page-{i:02}.png').convert('RGB')
        assert ImageChops.difference(png,b).getbbox() is None,(i,'PDF/PNG mismatch')
        pages.append({'page':i,'size_identical':True,'other_text_retained':True,'outside_changed_regions_pixels_identical':True,'preview_matches_pdf':True,'changed':bool(regions)})
    blank=[8,12,14,16,18,20,22]
    for n in blank:
        im=Image.open(temp/f'new/page-{n:02}.png').convert('RGB')
        assert all(lo==hi==255 for lo,hi in im.getextrema()),('Reverse not white',n)

# Extract the official raster logo without using extraction before preview rendering.
official=Image.open(R/'company-data/brand/logo/logo-horizontal.png').convert('RGB')
logo_refs={x for x,im in images.items() if tuple(im[2:4])==official.size}
assert len(logo_refs)==1
logo_ref=logo_refs.pop();assert fitz.Pixmap(new,logo_ref).samples==official.tobytes()
assert [i+1 for i,p in enumerate(new) if p.get_image_rects(logo_ref)]==[1,11,13,15,17,19,21,24]
qr_image=Image.open(B/'output/page-23.png').convert('RGB');qr=decode(qr_image)
assert qr==['https://kaihougakuen.my.canva.site/']
print_qr={}
for output in proof['outputs']:
    path=R/output['file'];assert sha(path)==output['sha256']
    if output['kind']=='reading':continue
    doc=fitz.open(path);assert len(doc)==12
    refs={im[0] for p in doc for im in p.get_images(full=True)}
    hashes={hashlib.sha256(doc.xref_stream_raw(x)).hexdigest() for x in refs}
    assert not hashes.intersection(p['source_image_sha256'] for p in proof['removed_photographs'])
    actual_pages=[]
    for i,p in enumerate(doc):
        pair=output['faces'][i];want=''.join(new[n-1].get_text() for n in pair)
        assert norm(p.get_text())==norm(want),(output['kind'],i,'Booklet order/content differs')
        actual_pages.extend(pair)
        # Native text for each source page must lie on its assigned sheet half.
        for side,n in enumerate(pair):
            rect=fitz.Rect(side*p.rect.width/2,0,(side+1)*p.rect.width/2,p.rect.height)
            assert norm(p.get_text(clip=rect))==norm(new[n-1].get_text()),(output['kind'],i,n,'Left/right slot differs')
    assert sorted(actual_pages)==list(range(1,25))
    qr_face=next(i for i,pair in enumerate(output['faces']) if 23 in pair)
    pix=doc[qr_face].get_pixmap(matrix=fitz.Matrix(3.5,3.5))
    decoded=decode(Image.frombytes('RGB',(pix.width,pix.height),pix.samples))
    assert decoded==qr,(output['kind'],'Print QR differs',decoded)
    print_qr[output['kind']]={'face':qr_face+1,'decoded':decoded}

result={'verified':True,'outputs':[{'kind':o['kind'],'sha256':o['sha256'],'pages':o['pages']} for o in proof['outputs']],'source_unchanged_sha256':sha(source),'removed_photo_count':6,'retained_raster_kinds':['official school logo','access map','transparent 1px image replacements'],'logo_pages':[1,11,13,15,17,19,21,24],'official_logo_pixels_identical':True,'map_stream_identical':True,'blank_reverse_pages':blank,'pages':pages,'booklet_order_verified':True,'qr_decoded':qr,'print_qr_decoded':print_qr,'fresh_process_rendering':True,'independent_review':False,'physical_print_test':False,'release':False}
(B/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('verified: 24 reading pages, both 12-face impositions, 6 photographs removed, logo/map/QR retained',flush=True)
