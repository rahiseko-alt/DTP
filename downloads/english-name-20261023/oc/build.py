"""OC R06: correct only the two English subtitles; retain both crests."""
from pathlib import Path
import hashlib,json
import fitz,numpy as np,yaml
B=Path(__file__).resolve().parent;R=B.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipt=json.loads((B/'source-get.json').read_text());source=R/receipt['path']
assert sha(source)==receipt['asset']['sha256']
facts=R/'company-data/facts/school.yaml';name=yaml.safe_load(facts.read_text())['name_en']
doc=fitz.open(source);assert len(doc)==2
page=doc[0]
pix=page.get_pixmap(matrix=fitz.Matrix(4,4))
rgb=np.frombuffer(pix.samples,np.uint8).reshape(pix.height,pix.width,pix.n)[:,:,:3].astype(float)
def sample(x,y):
    return rgb[min(rgb.shape[0]-1,max(0,round(y*4))),min(rgb.shape[1]-1,max(0,round(x*4)))]

fields=[{'id':'top-subtitle','rect_pt':[91,66,264,78],'pos':[94.2,74.5],'size':9.5,'color':[.35,.52,.71]},
        {'id':'footer-subtitle','rect_pt':[77,818.5,241,830.5],'pos':[79,827.3],'size':9.2,'color':[1,1,1]}]
def background_panel(rect):
    """Native PDF structure: interpolate the surrounding background colors.

    The top field sits on a soft white photographic fade, the bottom on a blue
    gradient. A flat rectangular fill would leave visible boxes. Coons color
    interpolation keeps their edge colors; no underlying image is modified.
    Each edge sample is outside the old letters, Japanese headings and crests.
    """
    x0,y0,x1,y1=rect
    corners=[sample(x0-.25,y0-.25),sample(x1+.25,y0-.25),sample(x0-.25,y1+.25),sample(x1+.25,y1+.25)]
    tl,tr,bl,br=corners
    shape=page.new_shape()
    for y in np.arange(y0,y1,1):
        h=min(1,y1-y);cy=y+h/2;t=(cy-y0)/(y1-y0)
        left=sample(x0-.25,cy);right=sample(x1+.25,cy)
        for x in np.arange(x0,x1,1):
            w=min(1,x1-x);cx=x+w/2;s=(cx-x0)/(x1-x0)
            top=sample(cx,y0-.25);bottom=sample(cx,y1+.25)
            bilinear=tl*(1-s)*(1-t)+tr*s*(1-t)+bl*(1-s)*t+br*s*t
            color=np.clip(top*(1-t)+bottom*t+left*(1-s)+right*s-bilinear,0,255)/255
            # Overlap tiles enough to prevent PDF antialias stitching from
            # revealing the old white letter pixels along tile boundaries.
            shape.draw_rect(fitz.Rect(x,y,min(x1,x+w+.55),min(y1,y+h+.55)))
            shape.finish(color=None,fill=tuple(color))
    shape.commit(overlay=True)
for field in fields:
    background_panel(field['rect_pt'])
    width=fitz.get_text_length(name,fontname='helv',fontsize=field['size'])
    assert field['pos'][0]+width<field['rect_pt'][2]
    page.insert_text(field['pos'],name,fontname='helv',fontsize=field['size'],color=tuple(field['color']),overlay=True)
(B/'output').mkdir(exist_ok=True)
output=B/'output/oc-flyer-r06.pdf'
doc.save(output,garbage=4,deflate=True)
final=fitz.open(output)
for i,p in enumerate(final,1):p.get_pixmap(matrix=fitz.Matrix(150/72,150/72)).save(B/f'output/page-{i}.png')
proof={'edition':'OC-R06-English-school-name','formal_name':name,'facts_sha256':sha(facts),'source':{'file':receipt['path'],'id':receipt['asset']['id'],'revision':receipt['asset']['revision'],'sha256':sha(source)},'pdf':str(output.relative_to(R)),'pdf_sha256':sha(output),'bytes':output.stat().st_size,'pages':2,'fields':fields,'crests_changed':False,'photos_changed':False,'back_changed':False,'release':False}
(B/'build-proof.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(proof,ensure_ascii=False,indent=2))
