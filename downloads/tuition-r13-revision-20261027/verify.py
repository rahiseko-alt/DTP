"""Fresh-render every PDF face, then inspect native text, images, and fee arithmetic."""
from pathlib import Path
from collections import Counter
import hashlib,json,re,ast,ctypes,ctypes.util,sys
import fitz
from PIL import Image,ImageChops,ImageDraw
B=Path(__file__).resolve().parent;R=B.parents[1]
proof=json.loads((B/'build-proof.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
PRE=B/'previews';PRE.mkdir(exist_ok=True)
for name,h in json.loads((B/'baseline.json').read_text())['protected'].items():assert sha(R/name)==h,name
def pix(page):
 p=page.get_pixmap(matrix=fitz.Matrix(150/72,150/72),alpha=False)
 return Image.frombytes('RGB',(p.width,p.height),p.samples)
def image_hashes(d):
 # Include even originally unused image/alpha objects; redaction can clean page resource lists.
 return Counter((hashlib.sha256(d.xref_stream_raw(x)).hexdigest(),d.xref_get_key(x,'Width'),d.xref_get_key(x,'Height'),d.xref_get_key(x,'BitsPerComponent')) for x in range(1,d.xref_length()) if d.xref_get_key(x,'Subtype')==('name','/Image'))
def outside_glyphs(p,regions,origins):
 result=[]
 for t in p.get_texttrace():
  for c in t['chars']:
   if tuple(round(x,3) for x in c[2]) in origins:continue
   if any(r.intersects(fitz.Rect(c[3])) for r in regions):continue
   result.append((t['font'],round(t['size'],3),c[0],c[1],tuple(round(x,3) for x in c[2])))
 return sorted(result,key=str)
norm=lambda s:re.sub(r'\s+','',s)
results=[]
for out in proof['outputs']:
 label=out['label'];assert sha(R/out['file'])==out['sha256'];assert sha(R/out['source']['file'])==out['source']['sha256']
 a=fitz.open(R/out['source']['file']);b=fitz.open(R/out['file']);assert len(a)==len(b)==out['pages']
 pages=[];thumbs=[];qr_im=None
 # Never extract text/images before this fresh render: MuPDF caches can alter later rendering.
 for i,(p,q) in enumerate(zip(a,b),1):
  assert p.rect==q.rect and p.rotation==q.rotation
  im_a,im_b=pix(p),pix(q);assert im_a.size==im_b.size
  diff=ImageChops.difference(im_a,im_b)
  regions=[fitz.Rect(x['rect_pt']) for x in out['changed_regions'].get(str(i),[])]
  if regions:
   mask=Image.new('L',im_a.size,255);draw=ImageDraw.Draw(mask);s=150/72
   for r in regions:draw.rectangle((r.x0*s-2,r.y0*s-2,r.x1*s+2,r.y1*s+2),fill=0)
   outside=ImageChops.multiply(diff.convert('L'),mask)
   if outside.getbbox():
    outside.save(f'/tmp/fees-outside-{label}-{i}.png');raise AssertionError((label,i,'Outside authorized fee fields changed',outside.getbbox()))
   im_b.save(PRE/f'{label}-page-{i:02}.png')
  else:assert diff.getbbox() is None,(label,i,'Unmodified page changed',diff.getbbox())
  if out['kind'] in ['reading','master'] and i==(15 if label.startswith('brochure') else 23):qr_im=im_b.copy()
  im_b.thumbnail((600,850) if out['kind'] in ['reading','master'] else (800,566));thumbs.append(im_b.copy())
  pages.append({'page':i,'fee_regions':len(regions),'outside_fee_regions_pixels_identical':True})
 assert image_hashes(a)==image_hashes(b),(label,'Embedded image bytes changed')
 for i,(p,q) in enumerate(zip(a,b),1):
  edits=out['changed_regions'].get(str(i),[])
  regions=[fitz.Rect(x['rect_pt']) for x in edits if x['kind']=='fee-table']
  origins={tuple(round(x,3) for x in pos) for item in edits for pos in item.get('glyph_origins',[])}
  assert outside_glyphs(p,regions,origins)==outside_glyphs(q,regions,origins),(label,i,'Outside fee text/font/position changed')
 for place in out['placements']:
  q=b[place['pdf_page']-1];text=norm(q.get_text(sort=True));pn=place['reading_page']
  for old in ['930,000','830,000','1,760,000','1,780,000']:assert old not in text,(label,pn,'Old fee left',old)
  for new in ({6:['980,000','880,000','1,860,000'],12:['980,000','880,000','1,860,000'],13:['1,880,000','1,860,000']}[pn]):assert new in text,(label,pn,'Missing new fee',new)
  assert '施設設備費' in text
  # Each table has a distinct annual fee, never a fabricated term assignment.
  if pn in [6,13]:assert text.count('施設設備費')==2,(label,pn,'Annual facility rows')
  else:assert text.count('施設設備費')==1
 if out['kind'] in ['reading','master']:
  if label.startswith('admissions'):
   for n in [8,12,14,16,18,20,22]:assert not b[n-1].get_text().strip() and not b[n-1].get_image_info()
  tree=ast.parse((R/'books/oc-yellow-photo-soft-r03-20261022/verify.py').read_text());fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='decode')
  exec(compile(ast.Module(body=[fn],type_ignores=[]),'<qr>','exec'))
  qr=decode(qr_im);assert qr==['https://kaihougakuen.my.canva.site/'],(label,qr)
 else:qr='Reading QR region is outside edits; all other face pixels identical'
 # Full-page contact sheets and all reading spreads for visual review.
 for start in range(0,len(thumbs),4):
  wide=out['kind'] not in ['reading','master'];cw,ch=(820,600) if wide else (620,880)
  canvas=Image.new('RGB',(cw*2,ch*2),'#eee');draw=ImageDraw.Draw(canvas)
  for j,im in enumerate(thumbs[start:start+4]):
   x=(j%2)*cw+10;y=(j//2)*ch+10;canvas.paste(im,(x,y));draw.text((x,y+im.height+3),f'PDF {start+j+1}',fill='#222')
  canvas.save(PRE/f'{label}-overview-{start+1:02}.jpg',quality=88)
 if out['kind']=='reading':
  for n in range(1,len(thumbs)-1,2):
   canvas=Image.new('RGB',(1240,880),'#eee');canvas.paste(thumbs[n],(10,10));canvas.paste(thumbs[n+1],(630,10));canvas.save(PRE/f'{label}-spread-{n+1:02}.jpg',quality=88)
 results.append({'label':label,'sha256':out['sha256'],'pages':pages,'outside_native_glyphs_fonts_positions_identical':True,'original_image_streams_identical':True,'qr':qr})
 print(label,'verified',len(pages),'faces',flush=True)
(B/'verification.json').write_text(json.dumps({'verified':True,'outputs':results,'fees_each_year':[50000,50000],'totals':[980000,880000,1860000],'with_exam':[1000000,1880000],'old_saved_files_unchanged':True,'independent_review':False,'physical_print_test':False,'release':False},ensure_ascii=False,indent=2)+'\n')
