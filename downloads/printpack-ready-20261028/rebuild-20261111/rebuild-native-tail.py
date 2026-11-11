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
out=fitz.open();W,H=210*72/25.4,297*72/25.4
for pn in range(11,15):
 pg=out.new_page(width=W,height=H);pg.show_pdf_page(fitz.Rect(0,0,src[pn].rect.width,src[pn].rect.height),src,pn,keep_proportion=False)
pdf=B/'native-pages-12-15-map-restored.pdf';out.save(pdf,garbage=4,deflate=True)
report={'partial_only':True,'not_for_submission':True,'source':str(source.relative_to(root)),'map_source':str(svg.relative_to(root)),'map_source_sha256':hashlib.sha256(svg.read_bytes()).hexdigest(),'map_image_removed_xref':mapim[0],'map_rect_pt':list(rect),'pages':[]}
d=fitz.open(pdf)
for i,p in enumerate(d):report['pages'].append({'source_page':i+12,'chars':len(p.get_text()),'fonts':len(p.get_fonts()),'images':len(p.get_images()),'size_pt':list(p.rect)})
assert '名古屋駅から学校へ' in d[3].get_text()
d[3].get_pixmap(matrix=fitz.Matrix(150/72,150/72)).save(B/'inspection/native-page-15-restored.png');(B/'native-tail-map-restored.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
