"""Verify every PDF face against saved inputs, allowing only registered copy rectangles."""
from pathlib import Path
from collections import Counter
import hashlib,json,math,re
import fitz
from PIL import Image,ImageChops,ImageDraw
B=Path(__file__).resolve().parent;R=B.parents[1];proof=json.loads((B/'build-proof.json').read_text());PRE=B/'previews';PRE.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def pixels(p):
 x=p.get_pixmap(matrix=fitz.Matrix(150/72,150/72),alpha=False);return Image.frombytes('RGB',(x.width,x.height),x.samples)
def images(d):return Counter((hashlib.sha256(d.xref_stream_raw(x)).hexdigest(),d.xref_get_key(x,'Width'),d.xref_get_key(x,'Height'),d.xref_get_key(x,'BitsPerComponent')) for x in range(1,d.xref_length()) if d.xref_get_key(x,'Subtype')==('name','/Image'))
def glyphs(p):return [(t['font'],t['size'],c[0],c[1],tuple(c[2]),tuple(c[3])) for t in p.get_texttrace() for c in t['chars']]
results=[]
for out in proof['outputs']:
 assert sha(R/out['file'])==out['sha256'];assert sha(R/out['source']['file'])==out['source']['sha256'];a=fitz.open(R/out['source']['file']);b=fitz.open(R/out['file']);assert len(a)==len(b)==out['pages'];thumbs=[];maxdelta=0;added=0;clipped=[]
 for i,(p,q) in enumerate(zip(a,b),1):
  assert p.rect==q.rect and p.rotation==q.rotation;x,y=pixels(p),pixels(q);diff=ImageChops.difference(x,y);regions=[r for r in out['regions'] if r['pdf_page']==i]
  if regions:
   mask=Image.new('L',x.size,255);draw=ImageDraw.Draw(mask);dpi=150/72
   for region in regions:
    area=fitz.Rect(region['rect']);draw.rectangle((math.floor(area.x0*dpi)-1,math.floor(area.y0*dpi)-1,math.ceil(area.x1*dpi)+1,math.ceil(area.y1*dpi)+1),fill=0)
   assert ImageChops.multiply(diff.convert('L'),mask).getbbox() is None,(out['label'],i,'pixels outside copy rectangles changed')
   if out['kind']=='reading':y.save(PRE/f'{out["label"]}-page-{i:02}.png')
  else:assert diff.getbbox() is None,(out['label'],i,'unchanged page pixels')
  before,after=glyphs(p),glyphs(q);assert len(after)>=len(before)
  for g,h in zip(before,after):
   assert (g[0],g[2],g[3])==(h[0],h[2],h[3]),'original native glyph/font changed'
   delta=max(abs(g[1]-h[1]),*(abs(v-z) for v,z in zip(g[4],h[4])));maxdelta=max(maxdelta,delta);assert delta<.0001
  for g in after[len(before):]:
   added+=1
   if chr(g[2]).isspace():continue
   box=fitz.Rect(g[5]);assert any((fitz.Rect(r['rect'])+(-.75,-.75,.75,.75)).contains(box) for r in regions),(out['label'],i,'new glyph outside copy area',chr(g[2]),list(box))
  y.thumbnail((600,850) if out['kind'] in ['reading','master'] else (800,566));thumbs.append(y.copy())
 assert images(a)==images(b),(out['label'],'original image streams')
 # Unchanged native annual fee pages also prove no furigana reintroduced.
 if out['kind'] in ['reading','master']:
  for pn in [12,13]:
   assert b[pn-1].get_text()==a[pn-1].get_text();text=re.sub(r'\s+','',b[pn-1].get_text());assert all(t in text for t in ['980,000円','880,000円','1,860,000円','上記金額には検定料2万円は含みません。'])
 for start in range(0,len(thumbs),4):
  wide=out['kind']=='print';cw,ch=(820,600) if wide else (620,880);canvas=Image.new('RGB',(cw*2,ch*2),'#eee');draw=ImageDraw.Draw(canvas)
  for j,im in enumerate(thumbs[start:start+4]):
   x=(j%2)*cw+10;y=(j//2)*ch+10;canvas.paste(im,(x,y));draw.text((x,y+im.height+3),f'PDF {start+j+1}',fill='#222')
  canvas.save(PRE/f'{out["label"]}-overview-{start+1:02}.jpg',quality=88)
 if out['kind']=='reading':
  for n in range(1,len(thumbs)-1,2):
   canvas=Image.new('RGB',(1240,880),'#eee');canvas.paste(thumbs[n],(10,10));canvas.paste(thumbs[n+1],(630,10));canvas.save(PRE/f'{out["label"]}-spread-{n+1:02}.jpg',quality=88)
 results.append({'label':out['label'],'sha256':out['sha256'],'page_faces':len(b),'copy_regions':len(out['regions']),'native_glyphs_added':added,'outside_copy_pixels_identical_150dpi':True,'original_native_glyphs_fonts_positions_preserved':True,'native_coordinate_max_delta_pt':maxdelta,'all_original_image_streams_identical':True,'annual_fee_table_furigana_policy_cover_QR_AI_note_imposition_preserved':True});print(out['label'],'verified',len(b),'faces',flush=True)
metrics=json.loads((B/'overlay-metrics.json').read_text());assert all(not x['overflow'] for p in metrics['pages'] for x in p['patches'])
(B/'verification.json').write_text(json.dumps({'verified':True,'outputs':results,'total_page_faces':sum(x['page_faces'] for x in results),'dom_overflow':False,'independent_review':False,'physical_print_test':False,'release':False},ensure_ascii=False,indent=2)+'\n')
