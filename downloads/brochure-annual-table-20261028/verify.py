"""Verify the approved annual table, note, and unchanged pixels/glyphs/images outside fee blocks."""
from pathlib import Path
from collections import Counter
import hashlib,json,re,math
import fitz
from PIL import Image,ImageChops,ImageDraw
B=Path(__file__).resolve().parent;R=B.parents[1];proof=json.loads((B/'build-proof.json').read_text());PRE=B/'previews';PRE.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();norm=lambda s:re.sub(r'\s+','',s)
def pixels(p):
 x=p.get_pixmap(matrix=fitz.Matrix(150/72,150/72),alpha=False);return Image.frombytes('RGB',(x.width,x.height),x.samples)
def images(d):return Counter((hashlib.sha256(d.xref_stream_raw(x)).hexdigest(),d.xref_get_key(x,'Width'),d.xref_get_key(x,'Height'),d.xref_get_key(x,'BitsPerComponent')) for x in range(1,d.xref_length()) if d.xref_get_key(x,'Subtype')==('name','/Image'))
def glyphs(p,areas):return sorted([(t['font'],t['size'],c[0],c[1],tuple(c[2])) for t in p.get_texttrace() for c in t['chars'] if not any(area.intersects(fitz.Rect(c[3])) for area in areas)],key=lambda g:(g[0],round(g[1],3),g[2],g[3],g[4]))
def compare_glyphs(p,q,areas):
 x,y=glyphs(p,areas),glyphs(q,areas);assert len(x)==len(y),'outside glyph count changed';maximum=0
 for g,h in zip(x,y):
  assert (g[0],g[2],g[3])==(h[0],h[2],h[3]),'outside text/font/glyph changed'
  delta=max(abs(g[1]-h[1]),*(abs(a-b) for a,b in zip(g[4],h[4])));maximum=max(maximum,delta)
  # Native PDF redaction serialization can round a coordinate by a few millionths of a point.
  # Require exact characters/fonts/glyph IDs, <=0.0001pt coordinates, and fully identical 150dpi pixels.
  assert delta<=0.0001,('outside native font size or position changed',delta)
 return maximum

results=[]
for out in proof['outputs']:
 assert sha(R/out['file'])==out['sha256'];assert sha(R/out['source']['file'])==out['source']['sha256'];a=fitz.open(R/out['source']['file']);b=fitz.open(R/out['file']);assert len(a)==len(b)==out['pages'];thumbs=[]
 for i,(p,q) in enumerate(zip(a,b),1):
  assert p.rect==q.rect and p.rotation==q.rotation;x,y=pixels(p),pixels(q);diff=ImageChops.difference(x,y);areas=[fitz.Rect(r['changed_rect_pt']) for r in out['regions'] if r['pdf_page']==i]
  if areas:
   mask=Image.new('L',x.size,255);draw=ImageDraw.Draw(mask);s=150/72
   for area in areas:draw.rectangle((math.floor(area.x0*s)-2,math.floor(area.y0*s)-2,math.ceil(area.x1*s)+2,math.ceil(area.y1*s)+2),fill=0)
   assert ImageChops.multiply(diff.convert('L'),mask).getbbox() is None,(out['label'],i,'outside fee blocks pixels');y.save(PRE/f'{out["label"]}-page-{i:02}.png')
  else:assert diff.getbbox() is None,(out['label'],i,'unchanged page pixels')
  y.thumbnail((600,850) if out['kind'] in ['reading','master'] else (800,566));thumbs.append(y.copy())
 assert images(a)==images(b),(out['label'],'all original image streams')
 max_glyph_delta=0
 for i,(p,q) in enumerate(zip(a,b),1):
  areas=[fitz.Rect(r['changed_rect_pt']) for r in out['regions'] if r['pdf_page']==i];max_glyph_delta=max(max_glyph_delta,compare_glyphs(p,q,areas))
 checks=[]
 for region in out['regions']:
  q=b[region['pdf_page']-1];rect=fitz.Rect(region['rect_pt']);table=fitz.Rect(region['table_rect_pt']);text=norm(q.get_text(clip=rect));xs=[0,.47,.735,1];cols=[]
  for j in range(3):cols.append(norm(q.get_text(clip=fitz.Rect(table.x0+table.width*xs[j]+.2,table.y0,table.x0+table.width*xs[j+1]-.2,table.y1))))
  for label,col in zip(proof['columns'],cols):assert label in col,(out['label'],region['reading_page'],label,col)
  for label in ['入学金','授業料','諸経費','施設設備費','年間合計']:assert cols[0].count(label)==1
  for amount in ['100,000円','780,000円','980,000円']:assert cols[1].count(amount)==1,(out['label'],amount,cols[1])
  assert cols[1].count('50,000円')==2
  for amount in ['780,000円','880,000円']:assert cols[2].count(amount)==1
  assert cols[2].count('50,000円')==2 and cols[2].count('ー')==1
  assert proof['note'] in text and text.count(proof['note'])==1
  assert '2年間合計：' in text and '1,860,000円' in text
  for forbidden in ['1,880,000','390,000','440,000','前期','後期','入学検定料を含む','入学金・入学検定料はこの表に含めていません']:assert forbidden not in text,(out['label'],region['reading_page'],forbidden)
  assert '0' not in [w[4] for w in q.get_text('words',clip=table)]
  checks.append({'reading_page':region['reading_page'],'pdf_page':region['pdf_page'],'columns':cols,'approved_note_once':True,'grand_total_excludes_exam':1860000})
 for start in range(0,len(thumbs),4):
  wide=out['kind']=='print';cw,ch=(820,600) if wide else (620,880);canvas=Image.new('RGB',(cw*2,ch*2),'#eee');draw=ImageDraw.Draw(canvas)
  for j,im in enumerate(thumbs[start:start+4]):
   x=(j%2)*cw+10;y=(j//2)*ch+10;canvas.paste(im,(x,y));draw.text((x,y+im.height+3),f'PDF {start+j+1}',fill='#222')
  canvas.save(PRE/f'{out["label"]}-overview-{start+1:02}.jpg',quality=88)
 if out['kind']=='reading':
  for n in range(1,len(thumbs)-1,2):
   canvas=Image.new('RGB',(1240,880),'#eee');canvas.paste(thumbs[n],(10,10));canvas.paste(thumbs[n+1],(630,10));canvas.save(PRE/f'{out["label"]}-spread-{n+1:02}.jpg',quality=88)
 results.append({'label':out['label'],'sha256':out['sha256'],'page_faces':len(b),'outside_fee_blocks_pixels_identical':True,'outside_fee_blocks_native_text_fonts_glyph_ids_identical':True,'outside_native_font_size_or_position_max_delta_pt':max_glyph_delta,'native_coordinate_tolerance_pt':0.0001,'all_original_image_streams_identical':True,'annual_tables':checks});print(out['label'],'verified',len(b),'faces',flush=True)
(B/'verification.json').write_text(json.dumps({'verified':True,'outputs':results,'independent_review':False,'physical_print_test':False,'release':False},ensure_ascii=False,indent=2)+'\n')
