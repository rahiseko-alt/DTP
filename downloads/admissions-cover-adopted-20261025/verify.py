"""Compare every output face with its predecessor and inspect native PDF content."""
from pathlib import Path
from collections import Counter
import hashlib,json,subprocess,sys,tempfile,shutil,ast,ctypes,ctypes.util
import fitz
from PIL import Image,ImageChops,ImageDraw
B=Path(__file__).resolve().parent;R=B.parents[1]
manifest=json.loads((B/'manifest.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,h in json.loads((B/'protected-snapshot.json').read_text()).items():assert sha(R/name)==h,name
previews=B/'previews';previews.mkdir(exist_ok=True)
records=[]
def glyphs(page):return [(t['font'],t['size'],c[0],c[1],c[2]) for t in page.get_texttrace() for c in t['chars']]
def image_streams(doc,page):
 return Counter(hashlib.sha256(doc.xref_stream_raw(x['xref'])).hexdigest() for x in page.get_image_info(xrefs=True) if x['xref'])
render=R/'downloads/admissions-plain-20261025/render-previews.py'
with tempfile.TemporaryDirectory(prefix='admissions-cover-') as tmp:
 temp=Path(tmp)
 for out in manifest['outputs']:
  kind=out['kind'];target=R/out['file'];source=R/out['source']['file']
  assert sha(target)==out['sha256'] and sha(source)==out['source']['revision']
  for label,path in [('old',source),('new',target)]:
   args=[sys.executable,str(render),str(path),str(temp/kind/label)]
   if label=='new' and kind!='print-a3':args.append('--overviews')
   subprocess.run(args,check=True)
  old=fitz.open(source);new=fitz.open(target);assert len(new)==len(old)==out['pages']
  pages=[]
  for i,(p,q) in enumerate(zip(old,new),1):
   a=Image.open(temp/kind/'old'/f'page-{i:02}.png').convert('RGB')
   b=Image.open(temp/kind/'new'/f'page-{i:02}.png').convert('RGB')
   assert p.rect==q.rect
   changed=i==1
   if not changed:
    assert ImageChops.difference(a,b).getbbox() is None,(kind,i,'pixels')
    assert p.read_contents()==q.read_contents(),(kind,i,'native content')
    assert glyphs(p)==glyphs(q),(kind,i,'glyphs/font/position')
    assert image_streams(old,p)==image_streams(new,q),(kind,i,'images')
   elif kind=='print-a3':
    # Only the right (cover) half of the first A3 face may differ.
    x=int(p.rect.width/2*150/72)-2
    assert ImageChops.difference(a.crop((0,0,x,a.height)),b.crop((0,0,x,b.height))).getbbox() is None
   else:
    cover=fitz.open(R/manifest['cover_pdf'])
    assert q.read_contents()==cover[0].read_contents()
    assert glyphs(q)==glyphs(cover[0])
    assert image_streams(new,q)==image_streams(cover,cover[0])
   pages.append({'page':i,'changed':changed,'unchanged_pixels_verified':not changed,'native_content_fonts_and_images_identical':not changed})
  if kind=='print-a3':
   # Verify every native glyph is placed on the specified left/right half.
   plain=fitz.open(R/manifest['outputs'][1]['file'])
   norm=lambda s:''.join(s.split())
   for face,pair in zip(new,manifest['faces']):
    for side,pn in enumerate(pair):
     rect=fitz.Rect(side*face.rect.width/2,0,(side+1)*face.rect.width/2,face.rect.height)
     assert norm(face.get_text(clip=rect))==norm(plain[pn-1].get_text()),(pn,'imposition')
   shutil.copyfile(temp/kind/'new'/'page-01.png',previews/'print-first-face.png')
   for start in [1,5,9]:
    canvas=Image.new('RGB',(1640,1200),'#eee');draw=ImageDraw.Draw(canvas)
    for j in range(4):
     im=Image.open(temp/kind/'new'/f'page-{start+j:02}.png');im.thumbnail((800,565))
     x=10+(j%2)*820;y=10+(j//2)*600;canvas.paste(im,(x,y))
     draw.text((x,y+568),str(manifest['faces'][start+j-1]),fill='#222')
    canvas.save(previews/f'print-faces-{start:02}.jpg',quality=90)
  else:
   shutil.copyfile(temp/kind/'new'/'cover.png',previews/f'{kind}-cover.png')
   shutil.copyfile(temp/kind/'new'/'back-cover.png',previews/f'{kind}-back-cover.png')
   for path in (temp/kind/'new').glob('review-spreads-*.jpg'):shutil.copyfile(path,previews/f'{kind}-{path.name}')
   shutil.copyfile(temp/kind/'new'/'overview-01.jpg',previews/f'{kind}-overview-01.jpg')
   blank=[n for n in range(1,25) if not new[n-1].get_text().strip() and not new[n-1].get_image_info()]
   assert blank==[8,12,14,16,18,20,22],(kind,blank)
  records.append({'kind':kind,'sha256':out['sha256'],'pages':pages,'only_cover_changed':True,'back_cover_identical':True})
 # Decode the unchanged web QR from both new reading PDFs.
 tree=ast.parse((R/'books/oc-yellow-photo-soft-r03-20261022/verify.py').read_text())
 fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='decode')
 exec(compile(ast.Module(body=[fn],type_ignores=[]),'<qr>','exec'))
 qr={kind:decode(Image.open(temp/kind/'new'/'page-23.png').convert('RGB')) for kind in ['photo','plain']}
 assert all(v==['https://kaihougakuen.my.canva.site/'] for v in qr.values())
result={'verified':True,'outputs':records,'faces':manifest['faces'],'qr_decoded':qr,'protected_old_files_unchanged':True,'independent_review':False,'physical_print_test':False,'release':False}
(B/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('Verified all 60 PDF pages/faces: only the cover changed; bodies/back covers/native content/images retained; QR and saddle order verified',flush=True)
