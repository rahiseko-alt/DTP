"""Compare all PDF faces outside the approved annual fee block."""
from pathlib import Path
from collections import Counter
import hashlib,json,re,math
import fitz
from PIL import Image,ImageChops,ImageDraw
B=Path(__file__).resolve().parent;R=B.parents[1]
proof=json.loads((B/'build-proof.json').read_text());PRE=B/'previews';PRE.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def pixels(p):
    x=p.get_pixmap(matrix=fitz.Matrix(150/72,150/72),alpha=False)
    return Image.frombytes('RGB',(x.width,x.height),x.samples)
def images(d):
    return Counter((hashlib.sha256(d.xref_stream_raw(x)).hexdigest(),d.xref_get_key(x,'Width'),d.xref_get_key(x,'Height'),d.xref_get_key(x,'BitsPerComponent')) for x in range(1,d.xref_length()) if d.xref_get_key(x,'Subtype')==('name','/Image'))
def glyphs(p,rect=None):
    return sorted([(t['font'],round(t['size'],3),c[0],c[1],tuple(round(x,3) for x in c[2])) for t in p.get_texttrace() for c in t['chars'] if rect is None or not rect.intersects(fitz.Rect(c[3]))],key=str)
norm=lambda s:re.sub(r'\s+','',s)
results=[]
for out in proof['outputs']:
    assert sha(R/out['file'])==out['sha256'];assert sha(R/out['source']['file'])==out['source']['sha256']
    a=fitz.open(R/out['source']['file']);b=fitz.open(R/out['file']);assert len(a)==len(b)==out['pages']
    edit=out['changed_page'];area=fitz.Rect(out['changed_rect_pt']);thumbs=[]
    # Render before extracting any text/images: MuPDF extraction caches affect rendering.
    for i,(p,q) in enumerate(zip(a,b),1):
        assert p.rect==q.rect and p.rotation==q.rotation
        x,y=pixels(p),pixels(q);diff=ImageChops.difference(x,y)
        if i==edit:
            mask=Image.new('L',x.size,255);draw=ImageDraw.Draw(mask);s=150/72
            draw.rectangle((math.floor(area.x0*s)-2,math.floor(area.y0*s)-2,math.ceil(area.x1*s)+2,math.ceil(area.y1*s)+2),fill=0)
            assert ImageChops.multiply(diff.convert('L'),mask).getbbox() is None,(out['label'],i,'outside-table pixels')
            y.save(PRE/f'{out["label"]}-page-{i:02}.png')
        else:assert diff.getbbox() is None,(out['label'],i,'unchanged page pixels')
        y.thumbnail((600,850) if out['kind'] in ['reading','master'] else (800,566));thumbs.append(y.copy())
    assert images(a)==images(b),(out['label'],'original image streams')
    for i,(p,q) in enumerate(zip(a,b),1):assert glyphs(p,area if i==edit else None)==glyphs(q,area if i==edit else None),(out['label'],i,'outside-table glyph/font/position')
    q=b[edit-1];panel=fitz.Rect(out['table_rect_pt']);scale=panel.width/360;table=fitz.Rect(panel.x0,panel.y0,panel.x1,panel.y0+194*scale);xs=[0,.47,.735,1];columns=[]
    for j in range(3):
        rect=fitz.Rect(table.x0+table.width*xs[j]+.2,table.y0,table.x0+table.width*xs[j+1]-.2,table.y1)
        columns.append(norm(q.get_text(clip=rect)))
    for label,column in zip(proof['columns'],columns):assert label in column,(out['label'],label,column)
    assert all(t in columns[0] for t in ['入学金','授業料','諸経費','施設設備費','年間合計'])
    assert columns[1].count('100,000')==1 and columns[1].count('780,000')==1 and columns[1].count('50,000')==2 and columns[1].count('980,000')==1
    assert columns[2].count('ー')==1 and columns[2].count('780,000')==1 and columns[2].count('50,000')==2 and columns[2].count('880,000')==1
    text=norm(q.get_text(clip=panel));assert text.count('1,860,000')==1 and '2年間合計' in text and '上記金額には検定料2万円は含みません。' in text
    assert not any(t in text for t in ['前期','後期','390,000','440,000','930,000','830,000','1,760,000','1,880,000'])
    assert '0' not in [w[4] for w in q.get_text('words',clip=panel)]
    if out['kind']=='reading':
        for pn in [8,12,14,16,18,20,22]:assert not b[pn-1].get_text().strip() and not b[pn-1].get_images(),(out['label'],'blank reverse',pn)
    for start in range(0,len(thumbs),4):
        wide=out['kind'] not in ['reading','master'];cw,ch=(820,600) if wide else (620,880)
        canvas=Image.new('RGB',(cw*2,ch*2),'#eee');draw=ImageDraw.Draw(canvas)
        for j,im in enumerate(thumbs[start:start+4]):
            x=(j%2)*cw+10;y=(j//2)*ch+10;canvas.paste(im,(x,y));draw.text((x,y+im.height+3),f'PDF {start+j+1}',fill='#222')
        canvas.save(PRE/f'{out["label"]}-overview-{start+1:02}.jpg',quality=88)
    if out['kind']=='reading':
        for n in range(1,len(thumbs)-1,2):
            canvas=Image.new('RGB',(1240,880),'#eee');canvas.paste(thumbs[n],(10,10));canvas.paste(thumbs[n+1],(630,10));canvas.save(PRE/f'{out["label"]}-spread-{n+1:02}.jpg',quality=88)
    results.append({'label':out['label'],'sha256':out['sha256'],'page_faces':len(b),'outside_table_pixels_identical':True,'outside_table_native_glyphs_fonts_positions_identical':True,'all_original_image_streams_identical':True,'columns':columns,'facility_fee_is_annual_not_assigned_to_terms':True})
    print(out['label'],'verified',len(b),'faces',flush=True)
(B/'verification.json').write_text(json.dumps({'verified':True,'outputs':results,'independent_review':False,'physical_print_test':False,'release':False},ensure_ascii=False,indent=2)+'\n')
