"""Change standalone zero and empty amounts to the requested U+30FC dash in the five-column table."""
from pathlib import Path
import hashlib,json
import fitz
B=Path(__file__).resolve().parent;R=B.parents[1]
fitz.TOOLS.set_small_glyph_heights(True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipts=json.loads((B/'receipts.json').read_text())
reading=fitz.open(R/next(x['path'] for x in receipts if x['label']=='brochure-original'))
w,h=reading[12].rect.width,reading[12].rect.height
table=fitz.Rect(31.416460037,378.91418457,564.50213623,515.564331055)
panel=fitz.open(B/'panel.pdf');assert len(panel)==1
(B/'output').mkdir(exist_ok=True);outputs=[]
for item in receipts:
    source=R/item['path'];assert sha(source)==item['asset']['sha256']
    doc=fitz.open(source)
    if item['kind'] in ['reading','master']:pi,s,dx,dy=12,1,0,0
    else:
        pi=3;p=doc[pi];s=min(p.rect.width/2/w,p.rect.height/h)
        dx=p.rect.width/2+(p.rect.width/2-w*s)/2;dy=(p.rect.height-h*s)/2
    rect=fitz.Rect(dx+table.x0*s,dy+table.y0*s,dx+table.x1*s,dy+table.y1*s)
    area=rect+(-s,-2.5*s,s,s);page=doc[pi]
    page.add_redact_annot(area,fill=None,cross_out=False)
    page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE,graphics=0,text=0)
    page.draw_rect(area,color=None,fill=(1,1,1),overlay=True)
    page.show_pdf_page(rect,panel,0,keep_proportion=False,overlay=True)
    target=B/'output'/f'{item["label"]}-facility-five-columns-zero-dash-20261028.pdf'
    doc.save(target,garbage=0,deflate=True)
    outputs.append({'label':item['label'],'document':item['document'],'kind':item['kind'],
        'file':str(target.relative_to(R)),'sha256':sha(target),'bytes':target.stat().st_size,
        'pages':len(doc),'changed_page':pi+1,'table_rect_pt':list(rect),'changed_rect_pt':list(area),
        'source':{'file':item['path'],'id':item['asset']['id'],'revision':item['asset']['revision'],'sha256':item['asset']['sha256']}})
    print(item['label'],'built',flush=True)
(B/'build-proof.json').write_text(json.dumps({'date':'2026-10-28','columns':['年次・時期','授業料','諸経費','施設設備費','合計'],'outputs':outputs,'release':False},ensure_ascii=False,indent=2)+'\n')
