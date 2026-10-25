"""A separate photo-free saved edition; retain the original 24-page source."""
from pathlib import Path
import hashlib,json,subprocess,sys
import fitz,yaml
B=Path(__file__).resolve().parent;R=B.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipt=json.loads((B/'receipts/source.json').read_text());source=R/receipt['path']
assert sha(source)==receipt['asset']['sha256']
doc=fitz.open(source);assert len(doc)==24
original_rect=doc[0].rect
colors=yaml.safe_load((R/'company-data/brand/colors/colors.yaml').read_text())['colors']
rgb=lambda name:tuple(int(colors[name][i:i+2],16)/255 for i in [1,3,5])
copy=json.loads((B/'cover-copy.json').read_text())
photo_ids={1:5,2:87,4:123,5:128,6:144,24:326}
captions={2:'教室でのグループ活動',4:'教室で課題に取り組む在校生',6:'入学式で書類を受け取る新入生'}
removed=[];regions={};logo_ref=46
logo_hash=hashlib.sha256(doc.xref_stream_raw(logo_ref)).hexdigest()
map_hash=hashlib.sha256(doc.xref_stream_raw(323)).hexdigest()
for n,xref in photo_ids.items():
    p=doc[n-1];info=next(i for i in p.get_images(full=True) if i[0]==xref)
    assert info[2]>1000 and info[3]>1000
    bbox=p.get_image_rects(xref)[0]
    clips=[fitz.Rect(v['scissor']) for v in p.get_drawings(extended=True) if v['type']=='clip' and 'scissor' in v]
    clip=min((c&bbox for c in clips if not (c&bbox).is_empty),key=lambda r:r.get_area())
    if n==24:clip=bbox&p.rect  # The smaller diagonal-strip clip belongs to a later drawing.
    removed.append({'page':n,'source_xref':xref,'source_image_sha256':hashlib.sha256(doc.xref_stream_raw(xref)).hexdigest(),'source_size':list(info[2:4]),'visible_region_pt':list(clip)})
    regions[str(n)]=[{'kind':'removed-photo','rect_pt':list(clip)}]
    p.delete_image(xref)
    if n in captions:
        matches=p.search_for(captions[n]);assert len(matches)==1,(n,matches)
        text_rect=matches[0]
        panels=[d['rect'] for d in p.get_drawings() if d.get('fill') and min(d['fill'])>.95 and d['rect'].contains(text_rect)]
        panel=min(panels,key=lambda r:r.get_area())
        p.add_redact_annot(panel,fill=rgb('surface' if n==4 else 'background'),cross_out=False)
        p.apply_redactions(images=0,graphics=0,text=0)
        regions[str(n)].append({'kind':'removed-photo-caption','rect_pt':list(panel),'text':captions[n]})

# Only the cover is recomposed. All other pages retain their original text/layout.
doc.delete_page(0)
page=doc.new_page(pno=0,width=original_rect.width,height=original_rect.height)
layer=fitz.open(B/'output/cover-layer.pdf')
page.show_pdf_page(page.rect,layer,0,keep_proportion=False)
mm=72/25.4
logo_rect=fitz.Rect(91*mm,249*mm,177*mm,(249+86*274/1121)*mm)
page.insert_image(logo_rect,xref=logo_ref,keep_proportion=False)
page.draw_rect(logo_rect,color=rgb('accent'),width=.4*mm,overlay=True)
regions['1']=[{'kind':'photo-free-cover-recomposition','rect_pt':list(original_rect)}]
reading=B/'output/admissions-plain-2027-r01.pdf'
doc.save(reading,garbage=4,deflate=True)
outputs=[{'kind':'reading','file':str(reading.relative_to(R)),'sha256':sha(reading),'bytes':reading.stat().st_size,'pages':24}]
final=fitz.open(reading)
faces=[pair for k in range(6) for pair in [(24-2*k,1+2*k),(2+2*k,23-2*k)]]
for kind,w,h in [('print-a3',420,297),('print-a4',297,210)]:
    out=fitz.open();placement=[]
    for pair in faces:
        face=out.new_page(width=w*mm,height=h*mm);slots=[]
        for side,n in enumerate(pair):
            clip=final[n-1].rect+ (3*mm,3*mm,-3*mm,-3*mm)
            slot=fitz.Rect(side*w*mm/2,0,(side+1)*w*mm/2,h*mm)
            face.show_pdf_page(slot,final,n-1,clip=clip,keep_proportion=True)
            slots.append({'reading_page':n,'source_clip_pt':list(clip),'slot_pt':list(slot)})
        placement.append(slots)
    output=B/f'output/admissions-plain-2027-r01-{kind.removeprefix("print-").upper()}.pdf'
    out.save(output,garbage=4,deflate=True)
    outputs.append({'kind':kind,'file':str(output.relative_to(R)),'sha256':sha(output),'bytes':output.stat().st_size,'pages':12,'sheets':6,'duplex':'短辺反転','faces':faces,'placements':placement})
proof={'material_id':'ADM-JP-PLAIN-2027','edition':'R01','source':{'file':receipt['path'],'id':receipt['asset']['id'],'revision':receipt['asset']['revision'],'sha256':sha(source)},'removed_photographs':removed,'changed_regions':regions,'removed_captions':captions,'retained_logo_stream_sha256':logo_hash,'retained_map_stream_sha256':map_hash,'cover_copy':copy,'outputs':outputs,'release':False}
(B/'build-proof.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
subprocess.run([sys.executable,str(B/'render-previews.py'),str(reading),str(B/'output'),'--overviews'],check=True)
for x in outputs:print(x['kind'],x['pages'],x['bytes'],flush=True)
