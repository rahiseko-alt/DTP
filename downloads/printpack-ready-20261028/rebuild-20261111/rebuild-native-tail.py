"""Partial rebuild only. Restore the existing native SVG map; keep source type as vectors."""
from pathlib import Path
import fitz,pikepdf,json,hashlib,copy,xml.etree.ElementTree as ET
B=Path(__file__).resolve().parent;R=B.parents[2];root=Path('/workspace/DTP')
rows=json.loads((B.parent/'receipts.json').read_text());source=root/rows[0]['path'];svg=root/'books/prospectus-isen-trial-2028/parts/access-route-svg/91d9705a30a9fd3ae7e0e15dd8d76d93da2bc4fe8359b3e845310dfcda126408/access-route-svg.svg'
src=fitz.open(source);mapim=next(i for i in src[14].get_images() if i[2:4]==(3072,2048));rect=src[14].get_image_rects(mapim[0])[0]
with pikepdf.open(source) as d:
 im=d.get_object(mapim[0],0);im.write(b'')
 for k in list(im.keys()):
  if str(k)!='/Length':del im[k]
 im.Type=pikepdf.Name('/XObject');im.Subtype=pikepdf.Name('/Form');im.BBox=pikepdf.Array([0,0,1,1]);d.save(B/'inspection/map-removed-source.pdf',compress_streams=True)
src=fitz.open(B/'inspection/map-removed-source.pdf');from native_map import make_native_map
mp=make_native_map(svg);src[14].show_pdf_page(rect,mp,0)
# Correct only the old native header/folio numerals. Preserve all other text.
folio_fonts={}
for weight in ['Black','Bold']:
 seen=set()
 for page in src:
  for info in page.get_fonts():
   if info[0] in seen or not info[3].endswith('-'+weight):continue
   seen.add(info[0]);data=src.extract_font(info[0])[3]
   if not data:continue
   font=fitz.Font(fontbuffer=data)
   if all(font.has_glyph(ord(c)) for c in '12345'):
    folio_fonts[weight]=(data,font);break
  if weight in folio_fonts:break
 assert weight in folio_fonts
for pn,old_number in [(12,'16'),(13,'21'),(14,'22'),(15,'23')]:
 pg=src[pn-1];spans=[s for b in pg.get_text('dict')['blocks'] for l in b.get('lines',[]) for s in l['spans'] if s['text']==old_number and (s['bbox'][1]<55 or s['bbox'][1]>790)]
 areas=[fitz.Rect(s['bbox']) for s in spans];assert len(areas)==2,(pn,areas)
 for area in areas:pg.add_redact_annot(area+(-.2,-.2,.2,.2),fill=None,cross_out=False)
 pg.apply_redactions(images=0,graphics=0,text=0)
 for span,area in zip(spans,areas):
  weight='Black' if area.y0<55 else 'Bold';data,font=folio_fonts[weight];name='OriginalFolio'+weight
  pg.insert_font(fontname=name,fontbuffer=data);origin=fitz.Point(span['origin']);size=span['size'];color=tuple((span['color']>>s&255)/255 for s in (16,8,0))
  sx=area.width/font.text_length(str(pn),fontsize=size)
  pg.insert_text(origin,str(pn),fontsize=size,fontname=name,color=color,morph=(origin,fitz.Matrix(sx,1)))
out=fitz.open();W,H=210*72/25.4,297*72/25.4
for pn in range(11,15):
 pg=out.new_page(width=W,height=H);pg.show_pdf_page(fitz.Rect(0,0,src[pn].rect.width,src[pn].rect.height),src,pn,keep_proportion=False)
pdf=B/'native-pages-12-15-map-restored.pdf';out.save(pdf,garbage=4,deflate=True)
report={'partial_only':True,'not_for_submission':True,'source':str(source.relative_to(root)),'map_source':str(svg.relative_to(root)),'map_source_sha256':hashlib.sha256(svg.read_bytes()).hexdigest(),'map_image_removed_xref':mapim[0],'map_rect_pt':list(rect),'pages':[]}
d=fitz.open(pdf)
for i,p in enumerate(d):report['pages'].append({'source_page':i+12,'chars':len(p.get_text()),'fonts':len(p.get_fonts()),'images':len(p.get_images()),'size_pt':list(p.rect)})
assert '名古屋駅から学校へ' in d[3].get_text()
d[3].get_pixmap(matrix=fitz.Matrix(150/72,150/72)).save(B/'inspection/native-page-15-restored.png');(B/'native-tail-map-restored.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
