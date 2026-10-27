"""Change only paint colors in three specified areas; retain all original geometry bytes."""
from pathlib import Path
from io import BytesIO
import hashlib,json,subprocess,sys
import fitz
from pypdf import PdfReader
from pypdf._utils import read_non_whitespace,read_until_regex
from pypdf.generic import NameObject,read_object
B=Path(__file__).resolve().parent;R=B.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
policy=json.loads((B/'color-policy.json').read_text())
rgb=lambda k:tuple(int(policy[k][i:i+2],16)/255 for i in [1,3,5])
cmd=lambda c:(' '.join(f'{x:.9f}' for x in c)+' rg ').encode()
receipt=json.loads((B/'receipts/reading-source.json').read_text());source=R/receipt['path']
assert sha(source)==receipt['asset']['sha256']
doc=fitz.open(source);assert len(doc)==24
reader=PdfReader(source)
paint_ops={b'f',b'f*',b'S',b's',b'Do',b'sh'}
both_ops={b'B',b'B*',b'b',b'b*'}
text_ops={b'Tj',b'TJ',b"'",b'"'}
def tokens(data):
    """Use the installed PDF parser to find spans without reserializing operands."""
    stream=BytesIO(data);start=None
    while True:
        peek=read_non_whitespace(stream)
        if not peek:break
        stream.seek(-1,1)
        if peek==b'%':
            while stream.read(1) not in [b'\r',b'\n',b'']:pass
            continue
        if start is None:start=stream.tell()
        if peek.isalpha() or peek in [b"'",b'"']:
            op=read_until_regex(stream,NameObject.delimiter_pattern)
            assert op!=b'BI','Inline image requires a different parser'
            yield start,stream.tell(),op
            start=None
        else:read_object(stream,None)
def inside(bbox,rect):return rect.contains(fitz.Point((bbox[0]+bbox[2])/2,(bbox[1]+bbox[3])/2))
proof_pages=[]
for n in [2,3]:
    page=doc[n-1];traces={t['seqno']:t for t in page.get_texttrace()}
    drawings={d['seqno']:d for d in page.get_drawings()}
    if n==2:
        rows=[fitz.Rect(45,285.75,210,307.5),fitz.Rect(45,329.25,210,350.25)]
        total=fitz.Rect(444.75,549.75,552.75,757.5)
        fills={20:rgb('white'),23:rgb('white'),454:rgb('white')}
        expected={20:rows[0],23:rows[1],454:total}
        regions=[list(r) for r in rows]+[list(total)]
    else:
        card=fitz.Rect(446.25,669,561,746.25)
        fills={630:rgb('white'),631:rgb('gold')}
        expected={630:card,631:fitz.Rect(446.25,669,561,672.75)}
        regions=[list(card)]
    for seq_no,rect in expected.items():
        assert seq_no in drawings and max(abs(a-b) for a,b in zip(drawings[seq_no]['rect'],rect))<.01
    raw=b'\n'.join(doc.xref_stream(x) for x in page.get_contents())
    operations=list(tokens(raw));parsed=reader.pages[n-1].get_contents().operations
    assert [v[2] for v in operations]==[v[1] for v in parsed]
    paint_log=[(i,t) for i,(t,_) in enumerate(page.get_bboxlog()) if not t.endswith('text')]
    paint_index=0;bt=None;edits=[];changes=[]
    ctm=fitz.Matrix(1,0,0,1,0,0);tm=fitz.Matrix(1,0,0,1,0,0)
    color=(0.,0.,0.);font_size=0.;stack=[];shows=[];first_point=None;first_size=None
    for i,(start,end,op) in enumerate(operations):
        args=parsed[i][0]
        if op==b'q':stack.append((fitz.Matrix(ctm),color,font_size))
        elif op==b'Q':ctm,color,font_size=stack.pop()
        elif op==b'cm':ctm=fitz.Matrix(*map(float,args))*ctm
        elif op==b'rg':color=tuple(map(float,args))
        elif op==b'g':color=(float(args[0]),)*3
        elif op==b'Tf':font_size=float(args[1])
        elif op==b'Tm':tm=fitz.Matrix(*map(float,args))
        if op==b'BT':
            bt=i;shows=[];first_point=None;first_size=None;tm=fitz.Matrix(1,0,0,1,0,0)
        if op in text_ops:
            if first_point is None:
                baseline=fitz.Point(tm.e,tm.f)*ctm
                first_point=fitz.Point(baseline.x,page.rect.height-baseline.y)
                first_size=abs(font_size)*(ctm.a**2+ctm.b**2)**.5
            shows.append((start,end,color))
        if op==b'ET':
            target=None;role=None
            if n==2 and first_point is not None:
                if any(row.contains(first_point) for row in rows) and first_point.x<95:
                    target=rgb('navy');role='toc-page-number'
                elif total.contains(first_point) and (first_size>20 or first_point.y<588):
                    target=rgb('navy');role='total-heading-and-number'
            if target is not None:
                for ss,ee,old_color in shows:edits.extend([(ss,cmd(target)),(ee,b' '+cmd(old_color))])
                changes.append({'kind':'text','role':role,'baseline':list(first_point),'font_size':first_size,'rgb':target})
            bt=None
        elif op in paint_ops|both_ops:
            seq,kind=paint_log[paint_index]
            if seq in fills:
                assert op==b'f' and kind=='fill-path',(n,seq,op,kind)
                edits.extend([(start,b'q /PlainOpaque gs '+cmd(fills[seq])),(end,b' Q ')])
                changes.append({'seqno':seq,'kind':'fill','bbox':list(drawings[seq]['rect']),'rgb':fills[seq]})
            paint_index+=2 if op in both_ops else 1
    assert paint_index==len(paint_log) and bt is None
    assert sum(c['kind']=='fill' for c in changes)==len(fills)
    if n==2:assert sum(c['kind']=='text' for c in changes)==5,changes
    # Every original byte remains, in the original order. Only color/opacity wrappers are inserted.
    result=bytearray();cursor=0
    for offset,insert in sorted(edits,key=lambda x:x[0]):
        assert offset>=cursor
        result.extend(raw[cursor:offset]);result.extend(insert);cursor=offset
    result.extend(raw[cursor:])
    xref=doc.get_new_xref();doc.update_object(xref,'<<>>');doc.update_stream(xref,bytes(result));page.set_contents(xref)
    doc.xref_set_key(page.xref,'Resources/ExtGState/PlainOpaque','<< /ca 1 /CA 1 >>')
    proof_pages.append({'page':n,'regions_pt':regions,'changes':changes,'original_content_sha256':hashlib.sha256(raw).hexdigest(),'method':'Insert color/opacity operators only; all original content bytes, text, fonts and coordinates retained'})
reading=B/'output/admissions-plain-2027-r03.pdf';doc.save(reading,garbage=4,deflate=True)
outputs=[{'kind':'reading','file':str(reading.relative_to(R)),'sha256':sha(reading),'bytes':reading.stat().st_size,'pages':24}]
final=fitz.open(reading);mm=72/25.4
faces=[pair for k in range(6) for pair in [(24-2*k,1+2*k),(2+2*k,23-2*k)]]
for kind,w,h in [('print-a3',420,297),('print-a4',297,210)]:
    out=fitz.open()
    for pair in faces:
        face=out.new_page(width=w*mm,height=h*mm)
        for side,pn in enumerate(pair):
            clip=final[pn-1].rect+(3*mm,3*mm,-3*mm,-3*mm)
            face.show_pdf_page(fitz.Rect(side*w*mm/2,0,(side+1)*w*mm/2,h*mm),final,pn-1,clip=clip,keep_proportion=True)
    path=B/f'output/admissions-plain-2027-r03-{kind.removeprefix("print-").upper()}.pdf';out.save(path,garbage=4,deflate=True)
    old=json.loads((B/f'receipts/{kind}-source.json').read_text())
    outputs.append({'kind':kind,'file':str(path.relative_to(R)),'sha256':sha(path),'bytes':path.stat().st_size,'pages':12,'source':{'file':old['path'],'id':old['asset']['id'],'revision':old['asset']['revision'],'sha256':old['asset']['sha256']}})
outputs[0]['source']={'file':receipt['path'],'id':receipt['asset']['id'],'revision':receipt['asset']['revision'],'sha256':receipt['asset']['sha256']}
proof={'edition':'R03','material_id':'ADM-JP-PLAIN-2027','policy':policy,'pages':proof_pages,'outputs':outputs,'faces':faces,'release':False}
(B/'build-proof.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
subprocess.run([sys.executable,str(B.parent/'render-previews.py'),str(reading),str(B/'output'),'--overviews'],check=True)
for n in [2,3]:
    subprocess.run([sys.executable,'-c',"import fitz,sys; d=fitz.open(sys.argv[1]); d[int(sys.argv[2])-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(sys.argv[3])",str(reading),str(n),str(B/f'output/page-{n:02}-detail.png')],check=True)
print([(o['kind'],o['bytes']) for o in outputs],flush=True)
