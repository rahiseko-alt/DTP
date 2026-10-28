"""Remove only native ruby reading glyphs; preserve every base glyph, image, and page geometry."""
from pathlib import Path
from collections import Counter
import hashlib,json,re
import fitz
B=Path(__file__).resolve().parent;R=B.parents[1];fitz.TOOLS.set_small_glyph_heights(True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();receipts=json.loads((B/'receipts.json').read_text());plan=json.loads((B/'ruby-source-plan.json').read_text());reference=fitz.open(R/next(x['path'] for x in receipts if x['label']=='brochure-jp-r13'));w,h=reference[0].rect.width,reference[0].rect.height;faces=[pair for k in range(4) for pair in [(16-2*k,1+2*k),(2+2*k,15-2*k)]]
(B/'output').mkdir(exist_ok=True);outputs=[]
for item in receipts:
 source=R/item['path'];assert sha(source)==item['asset']['sha256'];doc=fitz.open(source);regions=[]
 for spec in plan:
  pn=spec['reading_page']
  if item['kind'] in ['reading','master']:pi,s,dx,dy=pn-1,1,0,0
  else:
   pi,side=next((i,j) for i,pair in enumerate(faces) for j,n in enumerate(pair) if n==pn);p=doc[pi];s=min(p.rect.width/2/w,p.rect.height/h);dx=side*p.rect.width/2+(p.rect.width/2-w*s)/2;dy=(p.rect.height-h*s)/2
  page=doc[pi];half=fitz.Rect(dx,dy,dx+w*s,dy+h*s);removed=[]
  for span in page.get_texttrace():
   txt=''.join(chr(c[0]) for c in span['chars'])
   if abs(span['size']/s-6.50214)>.03 or not re.fullmatch(r'[ぁ-ゖァ-ヺー・\s]+',txt):continue
   for char in span['chars']:
    if chr(char[0]).isspace():continue
    if not half.contains(fitz.Point(*char[2])):continue
    box=fitz.Rect(char[3]);cx=(box.x0+box.x1)/2;cy=(box.y0+box.y1)/2
    removed.append({'font':span['font'],'size':span['size'],'unicode':char[0],'glyph_id':char[1],'origin':list(char[2]),'bbox':list(box)})
    page.add_redact_annot(fitz.Rect(cx-.02*s,cy-.02*s,cx+.02*s,cy+.02*s),fill=None,cross_out=False)
  assert Counter(chr(x['unicode']) for x in removed)==Counter(''.join(spec['ruby_texts'])),(item['label'],pn,'native ruby differs from source HTML', ''.join(chr(x['unicode']) for x in removed),spec['ruby_texts'])
  assert removed
  page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE,graphics=0,text=0)
  regions.append({'reading_page':pn,'pdf_page':pi+1,'scale':s,'offset':[dx,dy],'removed_ruby_glyphs':removed})
 target=B/'output'/f'{item["label"]}-no-furigana-20261028.pdf';doc.save(target,garbage=0,deflate=True)
 outputs.append({'label':item['label'],'document':item['document'],'kind':item['kind'],'file':str(target.relative_to(R)),'sha256':sha(target),'bytes':target.stat().st_size,'pages':len(doc),'regions':regions,'source':{'file':item['path'],'id':item['asset']['id'],'revision':item['asset']['revision'],'sha256':item['asset']['sha256']}});print(item['label'],'built',sum(len(r['removed_ruby_glyphs']) for r in regions),'ruby glyphs',flush=True)
(B/'build-proof.json').write_text(json.dumps({'date':'2026-10-28','scope':'remove ruby readings only from current brochure; preserve base characters and layout','outputs':outputs,'release':False},ensure_ascii=False,indent=2)+'\n')
