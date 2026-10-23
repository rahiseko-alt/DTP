"""R12: replace only three English-name fields in four saved R11 PDFs."""
from pathlib import Path
import hashlib, json
import fitz, yaml

B=Path(__file__).resolve().parent
R=B.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
facts=R/'company-data/facts/school.yaml'
name=yaml.safe_load(facts.read_text())['name_en']
# PDF reading page number, local field rectangle, baseline and font size.
fields={
    10:{'box':[22,11,220,22],'pos':[24.5,19.7],'size':7.5,'color':[.39,.59,.71]},
    11:{'box':[16,11,220,22],'pos':[18,19.7],'size':7.5,'color':[.39,.59,.71]},
    16:{'box':[175,154,421,169],'pos':None,'size':10.5,'color':[.34,.37,.38]},
}
sources=[('reading','brochure-jp-r12.pdf'),('master','brochure-jp-r12-master.pdf'),('print-a3','brochure-jp-r12-A3.pdf'),('print-a4','brochure-jp-r12-A4.pdf')]
faces=[pair for k in range(4) for pair in [(16-2*k,1+2*k),(2+2*k,15-2*k)]]
records=[]
for kind,filename in sources:
    receipt=json.loads((B/f'receipts/{kind}-source.json').read_text())
    source=R/receipt['path']
    assert sha(source)==receipt['asset']['sha256']
    doc=fitz.open(source)
    reading=kind in ['reading','master']
    assert len(doc)==(16 if reading else 8)
    changed={}
    for n,spec in fields.items():
        if reading:
            pi=n-1;scale=1;dx=dy=0
        else:
            pi,side=next((i,s) for i,pair in enumerate(faces) for s,pn in enumerate(pair) if pn==n)
            pw,ph=doc[pi].rect.width,doc[pi].rect.height
            # Original booklet used fit-to-half-sheet, centered with aspect ratio intact.
            reference=fitz.open(R/json.loads((B/'receipts/reading-source.json').read_text())['path'])
            w,h=reference[n-1].rect.width,reference[n-1].rect.height
            scale=min(pw/2/w,ph/h)
            dx=side*pw/2+(pw/2-w*scale)/2
            dy=(ph-h*scale)/2
            reference.close()
        page=doc[pi]
        x0,y0,x1,y1=spec['box']
        box=fitz.Rect(dx+x0*scale,dy+y0*scale,dx+x1*scale,dy+y1*scale)
        page.draw_rect(box,color=None,fill=(1,1,1),overlay=True)
        size=spec['size']*scale
        if spec['pos']:
            x,y=spec['pos'];pos=(dx+x*scale,dy+y*scale)
        else:
            x=(595.2755905511812-fitz.get_text_length(name,fontname='helv',fontsize=spec['size']))/2
            pos=(dx+x*scale,dy+164*scale)
        assert pos[0]>=box.x0 and pos[0]+fitz.get_text_length(name,fontname='helv',fontsize=size)<=box.x1
        page.insert_text(pos,name,fontname='helv',fontsize=size,color=tuple(spec['color']),overlay=True)
        changed.setdefault(str(pi+1),[]).append({'reading_page':n,'rect_pt':list(box),'name':name})
    output=B/'output'/filename
    doc.save(output,garbage=4,deflate=True)
    records.append({'kind':kind,'file':str(output.relative_to(R)),'sha256':sha(output),'bytes':output.stat().st_size,'pages':len(doc),'source':{'file':receipt['path'],'id':receipt['asset']['id'],'revision':receipt['asset']['revision'],'sha256':sha(source)},'changed_regions':changed})
    print(kind,output.stat().st_size,flush=True)
    doc.close()
    if kind=='reading':
        final=fitz.open(output)
        for i,p in enumerate(final,1):
            p.get_pixmap(matrix=fitz.Matrix(150/72,150/72)).save(B/f'output/page-{i:02}.png')
proof={'edition':'R12-English-school-name','formal_name':name,'facts_file':str(facts.relative_to(R)),'facts_sha256':sha(facts),'outputs':records,'source_photographs_changed':False,'release':False}
(B/'build-proof.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
