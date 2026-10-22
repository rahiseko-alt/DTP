"""R05: only the back flow panel changes; keep R04 photos and front intact."""
from pathlib import Path
import hashlib, html, json
import fitz, yaml

B = Path(__file__).resolve().parent
R = B.parents[1]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
receipt = json.loads((B/'reviews/source-get.json').read_text())
source = R/receipt['path']
assert sha(source) == receipt['asset']['sha256']
steps = yaml.safe_load((R/'company-data/facts/oc-flyer.yaml').read_text())['back_flow_steps']
assert [s['title'] for s in steps] == ['学校説明', '体験授業', '個別相談']
original = fitz.open(source)
doc = fitz.open(source)
back = doc[1]
# Coordinates are in the existing 150 dpi back preview, converted to PDF points.
scale = 72/150
def rect(box):
    return fitz.Rect(*(v*scale for v in box))
panel = rect((157, 840, 1091, 1006))
back.draw_rect(panel, color=None, fill=(1,1,1), overlay=True)
css = '@font-face{font-family:ExactNoto;src:url(NotoSansCJK-Bold.ttc);font-weight:bold;}'
archive = fitz.Archive('/usr/share/fonts/opentype/noto')
def text(box, content, size, color='#073c79'):
    _, shrink = back.insert_htmlbox(rect(box), '<div style="font-family:ExactNoto;font-weight:bold;font-size:'+str(size)+'pt;color:'+color+';text-align:center;line-height:1.25;margin:0;padding:0">'+html.escape(content).replace('\n','<br>')+'</div>', css=css, archive=archive)
    assert shrink > .999, (content, shrink)

# Reuse only each retained pictogram from the identified R04 PDF.
icons = [(220,890,309,950), (451,890,525,950), (951,890,1031,950)]
for i, (center, step, icon) in enumerate(zip([295,625,955],steps,icons),1):
    cx,cy=(center-67)*scale,867*scale
    back.draw_circle((cx,cy), 19*scale, color=None, fill=(1,.23,.48), overlay=True)
    back.insert_text((cx-3.4, cy+4.5), str(i), fontsize=14, fontname='helv', color=(1,1,1))
    text((center-62,850,center+115,883),step['title'],10.2)
    width=icon[2]-icon[0]
    back.show_pdf_page(rect((center-width/2,890,center+width/2,950)),original,1,clip=rect(icon),overlay=True)
    text((center-140,955,center+140,1004),step['description'],8.2)
for x in [457,787]:
    points=[fitz.Point(x*scale,902*scale),fitz.Point((x+23)*scale,916*scale),fitz.Point(x*scale,930*scale)]
    shape=back.new_shape()
    shape.draw_polyline(points+[points[0]])
    shape.finish(color=None,fill=(.55,.69,.84))
    shape.commit()

# Font subsetting avoids the original 61 MB download without changing images.
doc.subset_fonts(fallback=True)
output=B/'output/oc-flyer-r05.pdf'
doc.save(output,garbage=4,deflate=True)
final=fitz.open(output)
for i,p in enumerate(final,1):
    p.get_pixmap(matrix=fitz.Matrix(150/72,150/72)).save(B/f'output/page-{i}.png')
proof={'edition':'R05-three-steps','source':{'file':receipt['path'],'id':receipt['asset']['id'],'revision':receipt['asset']['revision'],'sha256':sha(source)},'pdf':str(output.relative_to(R)),'pdf_sha256':sha(output),'bytes':output.stat().st_size,'pages':2,'back_change_rect_pt':list(panel),'facts_sha256':sha(R/'company-data/facts/oc-flyer.yaml'),'steps':steps,'photos_changed':False,'front_changed':False,'release':False}
(B/'reviews/build-proof.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(proof,ensure_ascii=False,indent=2))
