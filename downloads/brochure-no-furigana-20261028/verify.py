"""Compare all PDF faces and every base glyph; permit changes only to recorded ruby glyphs."""
from pathlib import Path
from collections import Counter
import hashlib,json,math,re
import fitz
from PIL import Image,ImageChops,ImageDraw
B=Path(__file__).resolve().parent;R=B.parents[1];proof=json.loads((B/'build-proof.json').read_text());PRE=B/'previews';PRE.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def pixels(p):
 x=p.get_pixmap(matrix=fitz.Matrix(150/72,150/72),alpha=False);return Image.frombytes('RGB',(x.width,x.height),x.samples)
def images(d):return Counter((hashlib.sha256(d.xref_stream_raw(x)).hexdigest(),d.xref_get_key(x,'Width'),d.xref_get_key(x,'Height'),d.xref_get_key(x,'BitsPerComponent')) for x in range(1,d.xref_length()) if d.xref_get_key(x,'Subtype')==('name','/Image'))
def glyphs(p):return [(t['font'],t['size'],c[0],c[1],tuple(c[2])) for t in p.get_texttrace() for c in t['chars']]
def key(g):return (g[0],round(g[1],4),g[2],g[3],tuple(round(v,4) for v in g[4]))
def removed_key(g):return (g['font'],round(g['size'],4),g['unicode'],g['glyph_id'],tuple(round(v,4) for v in g['origin']))
def compare_base(p,q,removed):
 before=glyphs(p);after=glyphs(q);drop=Counter(removed_key(g) for g in removed);assert not (drop-Counter(key(g) for g in before))
 kept=[]
 for g in before:
  k=key(g)
  if drop[k]:drop[k]-=1
  else:kept.append(g)
 assert len(kept)==len(after),(len(kept),len(after),'a base glyph was removed/added')
 order=lambda g:(g[0],round(g[1],3),g[2],g[3],g[4]);kept.sort(key=order);after.sort(key=order);maximum=0
 for g,h in zip(kept,after):
  assert (g[0],g[2],g[3])==(h[0],h[2],h[3]),'base text/font/glyph ID changed'
  delta=max(abs(g[1]-h[1]),*(abs(a-b) for a,b in zip(g[4],h[4])));maximum=max(maximum,delta);assert delta<=0.0001,('base font size or position changed',delta)
 return maximum
results=[]
for out in proof['outputs']:
 assert sha(R/out['file'])==out['sha256'];assert sha(R/out['source']['file'])==out['source']['sha256'];a=fitz.open(R/out['source']['file']);b=fitz.open(R/out['file']);assert len(a)==len(b)==out['pages'];thumbs=[]
 for i,(p,q) in enumerate(zip(a,b),1):
  assert p.rect==q.rect and p.rotation==q.rotation;x,y=pixels(p),pixels(q);diff=ImageChops.difference(x,y);regions=[r for r in out['regions'] if r['pdf_page']==i]
  if regions:
   mask=Image.new('L',x.size,255);draw=ImageDraw.Draw(mask);dpi=150/72
   for region in regions:
    for g in region['removed_ruby_glyphs']:
     area=fitz.Rect(g['bbox'])+(-region['scale'],-region['scale'],region['scale'],region['scale']);draw.rectangle((math.floor(area.x0*dpi)-1,math.floor(area.y0*dpi)-1,math.ceil(area.x1*dpi)+1,math.ceil(area.y1*dpi)+1),fill=0)
   assert ImageChops.multiply(diff.convert('L'),mask).getbbox() is None,(out['label'],i,'pixels outside ruby glyphs changed');y.save(PRE/f'{out["label"]}-page-{i:02}.png')
  else:assert diff.getbbox() is None,(out['label'],i,'unchanged page pixels')
  y.thumbnail((600,850) if out['kind'] in ['reading','master'] else (800,566));thumbs.append(y.copy())
 assert images(a)==images(b),(out['label'],'original image streams')
 maximum=0;removed_count=0
 for i,(p,q) in enumerate(zip(a,b),1):
  regions=[r for r in out['regions'] if r['pdf_page']==i];removed=[g for r in regions for g in r['removed_ruby_glyphs']];maximum=max(maximum,compare_base(p,q,removed));removed_count+=len(removed)
  if regions:
   s=regions[0]['scale'];remaining=[t for t in q.get_texttrace() if abs(t['size']/s-6.50214)<.03 and re.fullmatch(r'[ぁ-ゖァ-ヺー・\s]+',''.join(chr(c[0]) for c in t['chars']))];assert not remaining,(out['label'],i,'ruby remains')
   if regions[0]['reading_page'] in [12,13]:
    text=re.sub(r'\s+','',q.get_text());assert '980,000円' in text and '880,000円' in text and '1,860,000円' in text;assert '上記金額には検定料2万円は含みません。' in text
 assert removed_count==153
 for start in range(0,len(thumbs),4):
  wide=out['kind']=='print';cw,ch=(820,600) if wide else (620,880);canvas=Image.new('RGB',(cw*2,ch*2),'#eee');draw=ImageDraw.Draw(canvas)
  for j,im in enumerate(thumbs[start:start+4]):
   x=(j%2)*cw+10;y=(j//2)*ch+10;canvas.paste(im,(x,y));draw.text((x,y+im.height+3),f'PDF {start+j+1}',fill='#222')
  canvas.save(PRE/f'{out["label"]}-overview-{start+1:02}.jpg',quality=88)
 if out['kind']=='reading':
  for n in range(1,len(thumbs)-1,2):
   canvas=Image.new('RGB',(1240,880),'#eee');canvas.paste(thumbs[n],(10,10));canvas.paste(thumbs[n+1],(630,10));canvas.save(PRE/f'{out["label"]}-spread-{n+1:02}.jpg',quality=88)
 results.append({'label':out['label'],'sha256':out['sha256'],'page_faces':len(b),'ruby_glyphs_removed':removed_count,'remaining_native_ruby':0,'outside_ruby_pixels_identical':True,'all_base_characters_fonts_glyph_ids_identical':True,'base_font_size_or_position_max_delta_pt':maximum,'native_coordinate_tolerance_pt':0.0001,'all_original_image_streams_identical':True,'annual_fee_table_and_approved_note_unchanged':True});print(out['label'],'verified',len(b),'faces; removed',removed_count,'ruby glyphs',flush=True)
(B/'verification.json').write_text(json.dumps({'verified':True,'outputs':results,'independent_review':False,'physical_print_test':False,'release':False},ensure_ascii=False,indent=2)+'\n')
