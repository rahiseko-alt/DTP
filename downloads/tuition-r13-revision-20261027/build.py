"""Patch fee tables and amounts in each saved PDF, without rebuilding other paper."""
from pathlib import Path
import hashlib,json,zipfile
import fitz,yaml
fitz.TOOLS.set_small_glyph_heights(True)
B=Path(__file__).resolve().parent;R=B.parents[1]
OUT=B/'output';OUT.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
facts=yaml.safe_load((R/'company-data/facts/admissions.yaml').read_text());tuition=facts['tuition']
assert [y['facility_fee'] for y in tuition['years']]==[50000,50000]
assert [y['total'] for y in tuition['years']]==[980000,880000] and tuition['grand_total']==1860000
TABLES={
 6:('admissions',fitz.Rect(192.75,263.25,552.75,495.75)),
 12:('annual',fitz.Rect(31.416460037,220.490188599,564.50213623,375.160125732)),
 13:('periods',fitz.Rect(31.416460037,378.91418457,564.50213623,515.564331055)),
}
OLD_NEW={'930,000':f"{tuition['years'][0]['total']:,}",'830,000':f"{tuition['years'][1]['total']:,}",'1,760,000':f"{tuition['grand_total']:,}",'1,780,000':f"{tuition['grand_total']+facts['exam_fee']:,}"}
receipts=json.loads((B/'receipts.json').read_text())
reference={}
for group,label,pages in [('brochure','brochure-original',[12,13]),('admissions','admissions-photo',[6])]:
 d=fitz.open(R/next(r['path'] for r in receipts if r['label']==label))
 reference[group]={pn:list(d[pn-1].rect) for pn in pages}

def transform(doc,item,pn):
 group='brochure' if item['label'].startswith('brochure') else 'admissions'
 if item['kind'] in ['reading','master']:return pn-1,1,0,0
 count=16 if group=='brochure' else 24
 faces=[pair for k in range(count//4) for pair in [(count-2*k,1+2*k),(2+2*k,count-1-2*k)]]
 pi,side=next((i,s) for i,pair in enumerate(faces) for s,n in enumerate(pair) if n==pn)
 w,h=reference[group][pn][2:];bleed=3*72/25.4 if group=='admissions' else 0
 cw,ch=w-2*bleed,h-2*bleed;p=doc[pi]
 scale=min(p.rect.width/2/cw,p.rect.height/ch)
 dx=side*p.rect.width/2+(p.rect.width/2-cw*scale)/2-bleed*scale
 dy=(p.rect.height-ch*scale)/2-bleed*scale
 return pi,scale,dx,dy

def rect_map(rect,s,dx,dy):return fitz.Rect(dx+rect.x0*s,dy+rect.y0*s,dx+rect.x1*s,dy+rect.y1*s)

def font_for(doc,page,font_name,text):
 candidates=[(doc,page)]
 # Optimized print PDFs have per-page font subsets that can omit a newly needed digit.
 # Reuse the exact same font family from the saved reading originals, never an OS substitute.
 for r in receipts:
  if r['label'] not in ['brochure-original','admissions-photo']:continue
  source=fitz.open(R/r['path'])
  candidates.extend((source,source[pn-1]) for pn in ([12,13] if r['label'].startswith('brochure') else [6]))
 for source,p in candidates:
  for x in p.get_fonts(full=True):
   if font_name not in x[3]:continue
   buf=source.extract_font(x[0])[3]
   if not buf:continue
   font=fitz.Font(fontbuffer=buf)
   if all(font.has_glyph(ord(c)) for c in text):return buf
 raise AssertionError(('Cannot reuse original numeric font',font_name,text))

def money_fields(doc,page,half,table):
 fields=[]
 for block in page.get_text('rawdict')['blocks']:
  if block['type']!=0:continue
  for line in block['lines']:
   for span in line['spans']:
    chars=span['chars'];text=''.join(c['c'] for c in chars)
    for old,new in OLD_NEW.items():
     start=0
     while (pos:=text.find(old,start))>=0:
      cc=chars[pos:pos+len(old)];start=pos+len(old);box=fitz.Rect()
      for c in cc:box|=fitz.Rect(c['bbox'])
      center=fitz.Point((box.x0+box.x1)/2,(box.y0+box.y1)/2)
      if not half.contains(center) or table.contains(center):continue
      buffer=font_for(doc,page,span['font'],new);font=fitz.Font(fontbuffer=buffer)
      # Optimized PDFs can have incorrect ascent metrics. Enclose the actual replacement font too.
      baseline=cc[0]['origin'][1]
      box|=fitz.Rect(box.x0,baseline-font.ascender*span['size'],box.x1,baseline-font.descender*span['size'])
      fields.append({'old':old,'new':new,'chars':cc,'font':span['font'],'size':span['size'],'color':span['color'],'box':box,'buffer':buffer})
 return fields

def build(item):
 source=R/item['path'];assert sha(source)==item['asset']['sha256']
 doc=fitz.open(source);group='brochure' if item['label'].startswith('brochure') else 'admissions'
 changed={};details=[]
 for pn in ([12,13] if group=='brochure' else [6]):
  pi,s,dx,dy=transform(doc,item,pn);page=doc[pi]
  panel_id,local=TABLES[pn];table=rect_map(local,s,dx,dy)
  half=page.rect if item['kind'] in ['reading','master'] else fitz.Rect(0 if table.x0<page.rect.width/2 else page.rect.width/2,0,page.rect.width/2 if table.x0<page.rect.width/2 else page.rect.width,page.rect.height)
  fields=money_fields(doc,page,half,table)
  assert len(fields)==({6:3,12:1,13:2}[pn]),(item['label'],pn,len(fields))
  # Redact only native text. Preserve every image and every original vector path.
  area=table+(-s,-2.5*s,s,s)
  page.add_redact_annot(area,fill=None,cross_out=False)
  for f in fields:
   for c in f['chars']:
    x=(c['bbox'][0]+c['bbox'][2])/2;y=c['origin'][1]-.3*f['size']
    page.add_redact_annot(fitz.Rect(x-.05,y-.05,x+.05,y+.05),fill=None,cross_out=False)
  page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE,graphics=0,text=0)
  page.draw_rect(area,color=None,fill=(1,1,1),overlay=True)
  panel=fitz.open(B/f'panels/{panel_id}.pdf');assert len(panel)==1
  page.show_pdf_page(table,panel,0,keep_proportion=False,overlay=True)
  changed.setdefault(str(pi+1),[]).append({'reading_page':pn,'kind':'fee-table','rect_pt':list(area),'facility_fee_each_year':50000})
  for j,f in enumerate(fields):
   name=f'Fee{pn}N{j}';page.insert_font(fontname=name,fontbuffer=f['buffer'])
   col=tuple(((f['color']>>k)&255)/255 for k in [16,8,0])
   for c,char in zip(f['chars'],f['new']):page.insert_text(c['origin'],char,fontname=name,fontsize=f['size'],color=col,overlay=True)
   changed[str(pi+1)].append({'reading_page':pn,'kind':'fee-number','rect_pt':list(f['box']),'old':f['old'],'new':f['new'],'glyph_origins':[list(c['origin']) for c in f['chars']]})
  details.append({'reading_page':pn,'pdf_page':pi+1,'scale':s,'offset':[dx,dy]})
 # Keep original image objects, including unused transparency resources in optimized PDFs.
 target=OUT/f"{item['label']}-fees-20261027.pdf";doc.save(target,garbage=0,deflate=True)
 result={'label':item['label'],'kind':item['kind'],'document':item['document'],'file':str(target.relative_to(R)),'sha256':sha(target),'bytes':target.stat().st_size,'pages':len(doc),'source':{'file':item['path'],'id':item['asset']['id'],'revision':item['asset']['revision'],'sha256':item['asset']['sha256']},'changed_regions':changed,'placements':details}
 print(item['label'],target.stat().st_size,flush=True);return result

if __name__=='__main__':
 import sys
 selected=[r for r in receipts if len(sys.argv)==1 or r['label'] in sys.argv[1:]]
 outputs=[build(r) for r in selected]
 proof={'date':'2026-10-27','fees':tuition,'exam_fee':facts['exam_fee'],'facts_sha256':sha(R/'company-data/facts/admissions.yaml'),'outputs':outputs,'release':False,'independent_review':False,'physical_print_test':False}
 (B/'build-proof.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
