"""Verify semantic colors, unchanged characters/positions, and all 48 PDF faces."""
from pathlib import Path
from collections import Counter
import ast,ctypes,ctypes.util,hashlib,json,re,subprocess,sys,tempfile
import fitz
from PIL import Image,ImageChops,ImageDraw
B=Path(__file__).resolve().parent;R=B.parents[2]
proof=json.loads((B/'build-proof.json').read_text());policy=proof['policy']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rgb=lambda key:tuple(int(policy[key][i:i+2],16)/255 for i in [1,3,5])
near=lambda a,b:len(a)==len(b) and max(abs(x-y) for x,y in zip(a,b))<.0001
norm=lambda s:re.sub(r'\s+','',s)
def images(d):
    refs={im[0]:im for p in d for im in p.get_images(full=True)}
    return Counter((sha_bytes(d.xref_stream_raw(x)),*a[2:6],sha_bytes(d.xref_stream_raw(a[1])) if a[1] else None) for x,a in refs.items())
def sha_bytes(s):return hashlib.sha256(s).hexdigest()
def glyphs(p):
    return [(t['font'],t['size'],c[0],c[1],c[2]) for t in p.get_texttrace() for c in t['chars']]
def contrast(a,b):
    def luminance(c):return sum(w*(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4) for w,v in zip([.2126,.7152,.0722],c))
    x,y=sorted([luminance(a),luminance(b)]);return (y+.05)/(x+.05)
ratios={'white_on_navy':contrast(rgb('white'),rgb('navy')),'text_on_white':contrast(rgb('text'),rgb('white')),'muted_on_white':contrast(rgb('muted'),rgb('white'))}
assert min(ratios.values())>=policy['minimum_text_contrast']
records=[]
regions={p['page']:[fitz.Rect(r) for r in p['regions_pt']] for p in proof['pages']}
with tempfile.TemporaryDirectory(prefix='dtp-color-verify-') as tmp:
    temp=Path(tmp)
    for out in proof['outputs']:
        source=R/out['source']['file'];path=R/out['file'];assert sha(source)==out['source']['sha256'] and sha(path)==out['sha256']
        old=fitz.open(source);new=fitz.open(path);assert len(old)==len(new)==out['pages'] and images(old)==images(new)
        for label,pdf in [('old',source),('new',path)]:
            subprocess.run([sys.executable,str(B.parent/'render-previews.py'),str(pdf),str(temp/out['kind']/label)],check=True)
        pages=[]
        for i,(p,q) in enumerate(zip(old,new),1):
            assert p.rect==q.rect and norm(p.get_text())==norm(q.get_text()),(out['kind'],i,'Text/size changed')
            ga,gb=glyphs(p),glyphs(q);assert len(ga)==len(gb)
            for a,b in zip(ga,gb):
                assert a[0]==b[0] and a[2:4]==b[2:4] and abs(a[1]-b[1])<.001 and max(abs(x-y) for x,y in zip(a[4],b[4]))<.001,(out['kind'],i,'Glyph/font/position changed')
            changed=[]
            if out['kind']=='reading':changed=regions.get(i,[])
            else:
                for side,pn in enumerate(proof['faces'][i-1]):
                    if pn not in regions:continue
                    w,h=612.0,858.9599609375;mm=72/25.4;x0=y0=3*mm;cw=w-6*mm;ch=h-6*mm
                    scale=min(p.rect.width/2/cw,p.rect.height/ch)
                    dx=side*p.rect.width/2+(p.rect.width/2-cw*scale)/2-x0*scale
                    dy=(p.rect.height-ch*scale)/2-y0*scale
                    changed.extend(fitz.Rect(dx+r.x0*scale,dy+r.y0*scale,dx+r.x1*scale,dy+r.y1*scale) for r in regions[pn])
            a=Image.open(temp/f'{out["kind"]}/old/page-{i:02}.png').convert('RGB');b=Image.open(temp/f'{out["kind"]}/new/page-{i:02}.png').convert('RGB');diff=ImageChops.difference(a,b)
            if changed:
                mask=Image.new('L',a.size,255);draw=ImageDraw.Draw(mask);s=150/72
                for r in changed:draw.rectangle((r.x0*s-2,r.y0*s-2,r.x1*s+2,r.y1*s+2),fill=0)
                assert ImageChops.multiply(diff.convert('L'),mask).getbbox() is None,(out['kind'],i,'Outside color fields changed')
            else:assert diff.getbbox() is None,(out['kind'],i,'Unmodified page differs')
            if out['kind']=='reading':assert ImageChops.difference(Image.open(B/f'output/page-{i:02}.png').convert('RGB'),b).getbbox() is None
            pages.append({'page':i,'text_font_size_and_glyph_positions_retained':True,'outside_color_fields_pixels_identical':True,'changed':bool(changed)})
        records.append({'kind':out['kind'],'sha256':out['sha256'],'original_image_streams_identical':True,'pages':pages})

reading=fitz.open(R/proof['outputs'][0]['file'])
def filled(page,box,color):
    found=[d for d in page.get_drawings() if d.get('fill') and max(abs(a-b) for a,b in zip(d['rect'],box))<.01]
    assert found and any(near(d['fill'],rgb(color)) and d['fill_opacity']==1 for d in found),(box,color)
filled(reading[1],[45,285.75,210,307.5],'white')
filled(reading[1],[45,329.25,210,350.25],'white')
filled(reading[1],[444.75,549.75,552.75,757.5],'white')
filled(reading[1],[444.75,549.75,552.75,552.75],'gold')
filled(reading[2],[446.25,669,561,746.25],'white')
filled(reading[2],[446.25,669,561,672.75],'gold')
for t in reading[1].get_texttrace():
    txt=''.join(chr(c[0]) for c in t['chars'])
    point=fitz.Point((t['bbox'][0]+t['bbox'][2])/2,(t['bbox'][1]+t['bbox'][3])/2)
    if (txt in ['P7','P11-22'] and point.x<100) or (fitz.Rect(444.75,549.75,552.75,757.5).contains(point) and txt in ['合','計','合計','59']):assert near(t['color'],rgb('navy'))
for t in reading[2].get_texttrace():
    point=fitz.Point((t['bbox'][0]+t['bbox'][2])/2,(t['bbox'][1]+t['bbox'][3])/2)
    if fitz.Rect(446.25,669,561,746.25).contains(point):assert near(t['color'],rgb('navy' if point.y<695 else 'text'))
decoder=ast.parse((R/'books/oc-yellow-photo-soft-r03-20261022/verify.py').read_text());fn=next(n for n in decoder.body if isinstance(n,ast.FunctionDef) and n.name=='decode');exec(compile(ast.Module(body=[fn],type_ignores=[]),'<qr>','exec'))
qr=decode(Image.open(B/'output/page-23.png').convert('RGB'));assert qr==['https://kaihougakuen.my.canva.site/']
(B/'verification.json').write_text(json.dumps({'verified':True,'outputs':records,'semantic_color_checks':True,'contrast_ratios':ratios,'all_original_images_retained':True,'qr_decoded':qr,'independent_review':False,'print_test':False,'release':False},ensure_ascii=False,indent=2)+'\n')
print('verified: all 48 faces; only the three requested areas changed; text/font/size/positions/images retained',flush=True)
