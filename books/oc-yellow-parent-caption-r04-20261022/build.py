"""R04: two local front-page changes over the fixed R03 PDF; no photo edits."""
from pathlib import Path
import hashlib, json, html
import fitz, yaml

B=Path(__file__).resolve().parent
R=B.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipt=json.loads((B/'reviews/source-get.json').read_text())
source=R/receipt['path']
assert sha(source)==receipt['asset']['sha256']
oc=yaml.safe_load((R/'company-data/facts/oc-flyer.yaml').read_text())
assert oc['parent_welcome_badge'] is False and oc['experience_middle_description']
coords=json.loads((R/'books/oc-yellow-photo-soft-r03-20261022/reviews/photo-coordinates.json').read_text())['front-hero']
x0,y0,x1,y1=coords['source_pdf_xyxy_pt']
sx=(x1-x0)/722;sy=(y1-y0)/420;y0-=75*sy
def native(r):
 x,y,w,h=r
 return fitz.Rect(x0+x*sx,y0+y*sy,x0+(x+w)*sx,y0+(y+h)*sy)

doc=fitz.open(source);front=doc[0]
badge=native([241,661,241,50])
caption=native([245,889,204,44])
front.add_redact_annot(caption,fill=False)
front.apply_redactions(images=0,graphics=0,text=0)
front.draw_rect(badge,color=None,fill=(1,1,1),overlay=True)
front.draw_rect(caption,color=None,fill=tuple(int('f2faff'[i:i+2],16)/255 for i in [0,2,4]),overlay=True)
css='@font-face{font-family:ExactNoto;src:url(NotoSansCJK-Bold.ttc);font-weight:bold;}'
_,scale=front.insert_htmlbox(native([251,892,190,18]),'<div style="font-family:ExactNoto;font-size:'+str(14*sx)+'pt;font-weight:700;color:#07174c;text-align:center;line-height:1.1;margin:0;padding:0">'+html.escape(oc['experience_middle_label'])+'</div>',css=css,archive=fitz.Archive('/usr/share/fonts/opentype/noto'))
assert scale>.999
_,scale=front.insert_htmlbox(native([253,909,190,27]),'<div style="font-family:ExactNoto;font-size:'+str(11*sx)+'pt;font-weight:700;color:#07174c;text-align:center;line-height:1.1;margin:0;padding:0">'+html.escape(oc['experience_middle_description']).replace('\n','<br>')+'</div>',css=css,archive=fitz.Archive('/usr/share/fonts/opentype/noto'))
assert scale>.999
(B/'output').mkdir(exist_ok=True)
output=B/'output/OC黄色帯版_保護者歓迎位置修正R04_2P.pdf'
doc.save(output,garbage=4,deflate=True)
final=fitz.open(output)
for i,page in enumerate(final):page.get_pixmap(matrix=fitz.Matrix(150/72,150/72)).save(B/f'output/page-{i+1}.png')
proof={'edition':'R04-parent-caption','source':{'file':receipt['path'],'sha256':sha(source),'id':receipt['asset']['id'],'revision':receipt['asset']['revision']},'pdf':str(output.relative_to(R)),'pdf_sha256':sha(output),'pages':2,'facts_sha256':sha(R/'company-data/facts/oc-flyer.yaml'),'front_change_rects_pt':[list(badge),list(caption)],'changes':['Remove parent-welcome badge under dates','Replace middle experience heading and explanation with parent-welcome title and accompanying caption'],'photos_changed':False,'back_page_changed':False,'release':False}
(B/'reviews/build-proof.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(proof,ensure_ascii=False,indent=2))
