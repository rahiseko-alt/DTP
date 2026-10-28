"""Verify only ten designated zero/empty cells changed against the prior five-column PDF."""
from pathlib import Path
import fitz,json,math
from PIL import Image,ImageDraw,ImageChops
B=Path(__file__).resolve().parent;R=B.parents[1]
proof=json.loads((B/'build-proof.json').read_text());result=[]
for out in proof['outputs']:
 a=fitz.open(R/out['source']['file']);b=fitz.open(R/out['file']);p=a[out['changed_page']-1];q=b[out['changed_page']-1];table=fitz.Rect(out['table_rect_pt']);xs=[0,.31,.48,.62,.83,1]
 # Header is row 0. Rows 3/6 are annual facility rows, the others are terms.
 cells=[(1,3),(2,2),(2,3),(3,1),(3,2),(4,3),(5,2),(5,3),(6,1),(6,2)]
 s=table.width/533.085676;rh=(table.height-s)/7
 boxes=[fitz.Rect(table.x0+xs[c]*table.width+s,table.y0+r*rh+s,table.x0+xs[c+1]*table.width-s,table.y0+(r+1)*rh-s) for r,c in cells]
 def render(page):
  pm=page.get_pixmap(matrix=fitz.Matrix(150/72,150/72),alpha=False);return Image.frombytes('RGB',(pm.width,pm.height),pm.samples)
 x,y=render(p),render(q);diff=ImageChops.difference(x,y);mask=Image.new('L',x.size,255);draw=ImageDraw.Draw(mask)
 for box in boxes:draw.rectangle((math.floor(box.x0*150/72),math.floor(box.y0*150/72),math.ceil(box.x1*150/72),math.ceil(box.y1*150/72)),fill=0)
 assert ImageChops.multiply(diff.convert('L'),mask).getbbox() is None,(out['label'],'pixels outside ten cells')
 def glyphs(page):return sorted([(t['font'],round(t['size'],3),c[0],c[1],tuple(round(v,3) for v in c[2])) for t in page.get_texttrace() for c in t['chars'] if not any(box.intersects(fitz.Rect(c[3])) for box in boxes)],key=str)
 assert glyphs(p)==glyphs(q),(out['label'],'glyphs outside ten cells')
 for box in boxes:assert q.get_text(clip=box).strip()=='ー',(out['label'],box,q.get_text(clip=box))
 result.append({'label':out['label'],'only_ten_cells_changed':True,'outside_ten_cells_pixels_identical':True,'outside_ten_cells_glyphs_identical':True,'zero_cells_replaced':2,'existing_empty_dashes_unified':8,'character':'ー','unicode':'U+30FC','cell_rects_pt':[list(x) for x in boxes]})
 print(out['label'],'ten cells verified',flush=True)
(B/'cell-verification.json').write_text(json.dumps({'verified':True,'outputs':result},ensure_ascii=False,indent=2)+'\n')
