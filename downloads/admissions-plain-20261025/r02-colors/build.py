"""Change only paint colors in two PDF pages; retain all original geometry bytes."""
from pathlib import Path
from io import BytesIO
import hashlib,json,subprocess,sys
import fitz
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
for n in [4,5]:
    page=doc[n-1];traces={t['seqno']:t for t in page.get_texttrace()}
    drawings={d['seqno']:d for d in page.get_drawings()}
    if n==4:
        fills={s:rgb('navy') for s,d in drawings.items() if d.get('fill') and abs(d['rect'].x0-51)<.01 and abs(d['rect'].x1-153)<.01 and d['rect'].height>90}
        assert len(fills)==3
        tabs=[drawings[s]['rect'] for s in fills]
        regions=[list(r) for r in tabs]
    else:
        fills={s:rgb('navy' if d['rect'].y0<168 else 'white') for s,d in drawings.items() if d.get('fill') and abs(d['rect'].width-138)<.01 and d['rect'].x0>=139 and d['rect'].x1<=562 and 116<=d['rect'].y0<468}
        assert len(fills)==21
        regions=[[51,116.25,561,467.25]]
    raw=b'\n'.join(doc.xref_stream(x) for x in page.get_contents())
    operations=list(tokens(raw));seq=0;bt=None;edits=[];changes=[]
    for i,(start,end,op) in enumerate(operations):
        if op==b'BT':bt=i
        if op==b'ET':
            assert seq in traces,(n,seq,'Text trace/stream order differs')
            t=traces[seq];target=None;role=None
            if n==4 and any(inside(t['bbox'],r) for r in tabs):target=rgb('white');role='uniform-exam-label'
            if n==5:
                if inside(t['bbox'],fitz.Rect(139.5,116.25,561,166.5)):target=rgb('white');role='uniform-column-heading'
                elif inside(t['bbox'],fitz.Rect(139.5,169.5,561,467.25)):
                    text=''.join(chr(c[0]) for c in t['chars']).strip()
                    target=rgb('muted' if text in ['－','—','–','-','―'] else 'text');role='table-content'
                elif inside(t['bbox'],fitz.Rect(51,169.5,139.5,467.25)):target=rgb('white');role='row-heading'
            if target is not None:
                assert len(t['color'])==3 and t['opacity']==1
                for ss,ee,oo in operations[bt+1:i]:
                    if oo in text_ops:
                        edits.extend([(ss,cmd(target)),(ee,b' '+cmd(t['color']))])
                changes.append({'seqno':seq,'kind':'text','role':role,'bbox':list(t['bbox']),'rgb':target})
            bt=None;seq+=1
        elif op in paint_ops|both_ops:
            if seq in fills:
                assert op==b'f',(n,seq,op)
                edits.extend([(start,b'q /PlainOpaque gs '+cmd(fills[seq])),(end,b' Q ')])
                changes.append({'seqno':seq,'kind':'fill','bbox':list(drawings[seq]['rect']),'rgb':fills[seq]})
            seq+=2 if op in both_ops else 1
    assert seq==len(page.get_bboxlog()) and bt is None
    # Every original byte remains, in the original order. Only color/opacity wrappers are inserted.
    result=bytearray();cursor=0
    for offset,insert in sorted(edits,key=lambda x:x[0]):
        assert offset>=cursor
        result.extend(raw[cursor:offset]);result.extend(insert);cursor=offset
    result.extend(raw[cursor:])
    xref=doc.get_new_xref();doc.update_object(xref,'<<>>');doc.update_stream(xref,bytes(result));page.set_contents(xref)
    doc.xref_set_key(page.xref,'Resources/ExtGState/PlainOpaque','<< /ca 1 /CA 1 >>')
    proof_pages.append({'page':n,'regions_pt':regions,'changes':changes,'original_content_sha256':hashlib.sha256(raw).hexdigest(),'method':'Insert color/opacity operators only; all original content bytes, text, fonts and coordinates retained'})
reading=B/'output/admissions-plain-2027-r02.pdf';doc.save(reading,garbage=4,deflate=True)
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
    path=B/f'output/admissions-plain-2027-r02-{kind.removeprefix("print-").upper()}.pdf';out.save(path,garbage=4,deflate=True)
    old=json.loads((B/f'receipts/{kind}-source.json').read_text())
    outputs.append({'kind':kind,'file':str(path.relative_to(R)),'sha256':sha(path),'bytes':path.stat().st_size,'pages':12,'source':{'file':old['path'],'id':old['asset']['id'],'revision':old['asset']['revision'],'sha256':old['asset']['sha256']}})
outputs[0]['source']={'file':receipt['path'],'id':receipt['asset']['id'],'revision':receipt['asset']['revision'],'sha256':receipt['asset']['sha256']}
proof={'edition':'R02','material_id':'ADM-JP-PLAIN-2027','policy':policy,'pages':proof_pages,'outputs':outputs,'faces':faces,'release':False}
(B/'build-proof.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
subprocess.run([sys.executable,str(B.parent/'render-previews.py'),str(reading),str(B/'output'),'--overviews'],check=True)
for n in [4,5]:
    subprocess.run([sys.executable,'-c',"import fitz,sys; d=fitz.open(sys.argv[1]); d[int(sys.argv[2])-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(sys.argv[3])",str(reading),str(n),str(B/f'output/page-{n:02}-detail.png')],check=True)
print([(o['kind'],o['bytes']) for o in outputs],flush=True)
