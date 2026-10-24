"""R13: add the approved two-line AI-image notice to the final saved page only."""
from pathlib import Path
import hashlib,json,subprocess,sys
import fitz

B=Path(__file__).resolve().parent;R=B.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec=json.loads((B/'notice.json').read_text())
layer=fitz.open(B/'output/note-layer.pdf')
normalize=lambda s:''.join(s.split())
assert normalize(layer[0].get_text())==normalize(''.join(spec['lines']))
blocks=layer[0].get_text('blocks')
rect=fitz.Rect(blocks[0][:4])
for block in blocks[1:]:rect|=fitz.Rect(block[:4])
rect=rect+(-1,-1,1,1)
assert rect.y0>800 and rect.y1<832,(rect,'Notice must be below the existing bottom rule and inside trim')
sources=[('reading','brochure-jp-r13.pdf'),('master','brochure-jp-r13-master.pdf'),('print-a3','brochure-jp-r13-A3.pdf'),('print-a4','brochure-jp-r13-A4.pdf')]
records=[]
for kind,filename in sources:
    receipt=json.loads((B/f'receipts/{kind}-source.json').read_text())
    source=R/receipt['path'];assert sha(source)==receipt['asset']['sha256']
    doc=fitz.open(source)
    if kind in ['reading','master']:
        pi=15;scale=1;dx=dy=0
    else:
        pi=0;pw,ph=doc[0].rect.width,doc[0].rect.height
        scale=min(pw/2/595.92,ph/842.88)
        dx=(pw/2-595.92*scale)/2;dy=(ph-842.88*scale)/2
    target=fitz.Rect(dx+rect.x0*scale,dy+rect.y0*scale,dx+rect.x1*scale,dy+rect.y1*scale)
    doc[pi].show_pdf_page(target,layer,0,clip=rect,keep_proportion=False,overlay=True)
    output=B/'output'/filename
    doc.save(output,garbage=4,deflate=True)
    records.append({'kind':kind,'file':str(output.relative_to(R)),'sha256':sha(output),'bytes':output.stat().st_size,'pages':len(doc),'source':{'file':receipt['path'],'id':receipt['asset']['id'],'revision':receipt['asset']['revision'],'sha256':sha(source)},'changed_regions':{str(pi+1):[{'reading_page':16,'rect_pt':list(target)}]},'notice_font_size_pt':spec['font_size_pt']*scale})
    print(kind,output.stat().st_size,flush=True);doc.close()

subprocess.run([sys.executable,str(B/'render-previews.py'),str(B/'output/brochure-jp-r13.pdf'),str(B/'output'),'--overviews'],check=True)
proof={'edition':'R13-AI-image-notice','notice':spec,'notice_source_file':str((B/'notice.json').relative_to(R)),'notice_source_sha256':sha(B/'notice.json'),'outputs':records,'source_photographs_changed':False,'release':False}
(B/'build-proof.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
