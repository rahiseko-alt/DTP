"""保存済み版から、裁断不要のA3/A4両面中綴じ用PDFと検証記録を作る。"""
from pathlib import Path
import hashlib,json,subprocess,sys
import fitz
from PIL import Image,ImageChops,ImageStat
from pypdf import PdfReader,PdfWriter,PageObject,Transformation
from pypdf.generic import NameObject,DictionaryObject

ROOT=Path(__file__).resolve().parents[4]
SPEC=json.loads(Path(__file__).with_name('spec.json').read_text())
MM=72/25.4
CACHE=ROOT/'.cache/print-booklets-20261020'
CACHE.mkdir(parents=True,exist_ok=True)
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

for book in SPEC['books']:
    src=ROOT/book['source']
    assert digest(src)==book['sha256'],f"入力SHA不一致: {src}"
    original=fitz.open(src)
    assert len(original)==book['pages'] and len(original)%4==0
    normalized=fitz.open()
    for i,page in enumerate(original):
        clip=fitz.Rect(page.rect)
        b=book['bleed_mm']*MM
        clip=fitz.Rect(clip.x0+b,clip.y0+b,clip.x1-b,clip.y1-b)
        target=normalized.new_page(width=210*MM,height=297*MM)
        target.show_pdf_page(target.rect,original,i,clip=clip,keep_proportion=True)
    normalized_file=CACHE/f"{book['id']}-trimmed-a4.pdf"
    normalized.save(normalized_file,garbage=4,deflate=True)
    normalized.close()
    source=fitz.open(normalized_file)
    n=len(source)
    faces=[]
    for k in range(n//4):
        faces.extend([{'sheet':k+1,'side':'front','left':n-2*k,'right':1+2*k},
                      {'sheet':k+1,'side':'back','left':2+2*k,'right':n-1-2*k}])
    assert sorted(v for f in faces for v in [f['left'],f['right']])==list(range(1,n+1))
    reading=[]
    for k in range(n//4):reading.extend([faces[2*k]['right'],faces[2*k+1]['left']])
    for k in reversed(range(n//4)):reading.extend([faces[2*k+1]['right'],faces[2*k]['left']])
    assert reading==list(range(1,n+1))
    outputs=[]
    for a4 in [False,True]:
        paper='A4' if a4 else 'A3'
        raw=CACHE/f"{book['id']}-{paper}-raw.pdf"
        args=[sys.executable,str(ROOT/'system/scripts/impose-booklet.py'),'--src',str(normalized_file),'--mode','saddle','--bleed-mm','0','--out',str(raw)]
        if a4:args.append('--a4-trial')
        subprocess.run(args,check=True)
        reader=PdfReader(raw);writer=PdfWriter()
        width,height=(297*MM,210*MM) if a4 else (420*MM,297*MM)
        for page in reader.pages:
            sheet=PageObject.create_blank_page(width=width,height=height)
            dx=(width-float(page.mediabox.width))/2
            dy=(height-float(page.mediabox.height))/2
            sheet.merge_transformed_page(page,Transformation().translate(dx,dy))
            writer.add_page(sheet)
        writer.add_metadata({'/Title':f"{book['title']} {paper}両面・短辺とじ・中綴じ",'/Subject':'面付け済み。1枚あたりのページ数1、冊子印刷OFF、実際のサイズ。中央で折って留める。'})
        writer._root_object[NameObject('/ViewerPreferences')]=DictionaryObject({NameObject('/Duplex'):NameObject('/DuplexFlipShortEdge'),NameObject('/PrintScaling'):NameObject('/None'),NameObject('/Direction'):NameObject('/L2R')})
        directory=ROOT/'books'/book['id']/'output/imposed';directory.mkdir(parents=True,exist_ok=True)
        suffix='_A4両面中綴じ_A5仕上がり.pdf' if a4 else '_A3両面中綴じ_A4仕上がり.pdf'
        out=directory/(book['basename']+suffix)
        with out.open('wb') as f:writer.write(f)
        imposed=fitz.open(out)
        assert len(imposed)==n//2
        differences=[]
        for i,face in enumerate(imposed):
            assert abs(face.rect.width-width)<.01 and abs(face.rect.height-height)<.01
            for side in ['left','right']:
                half=face.rect.width/2
                clip=fitz.Rect(0 if side=='left' else half,0,half if side=='left' else face.rect.width,face.rect.height)
                # 同じ原点と寸法へ戻して比較し、見開き中央の端数ptによる画素位相差を除く。
                check=fitz.open()
                restored=check.new_page(width=210*MM,height=297*MM)
                restored.show_pdf_page(restored.rect,imposed,i,clip=clip,keep_proportion=False)
                actual=restored.get_pixmap()
                expected=source[faces[i][side]-1].get_pixmap()
                def small(p):return Image.frombytes('RGB',(p.width,p.height),p.samples).resize((128,181),Image.Resampling.LANCZOS)
                delta=sum(ImageStat.Stat(ImageChops.difference(small(actual),small(expected))).mean)/3
                assert delta<2,(book['id'],paper,i+1,side,delta)
                differences.append(delta)
                check.close()
        outputs.append({'paper':paper,'finished_size':'A5' if a4 else 'A4','file':str(out.relative_to(ROOT)),'sha256':digest(out),'faces':len(imposed),'sheets':n//4,'size_mm':[round(width/MM,3),round(height/MM,3)],'max_thumbnail_mean_difference':max(differences),'all_half_sheets_compared':len(differences),'print_preferences':{'duplex':'short-edge','scaling':'none','driver_booklet_mode':False}})
    record={'date':SPEC['date'],'book':book['id'],'source_asset_id':book['source_asset_id'],'source':book['source'],'source_sha256':digest(src),'source_pages':n,'trim_bleed_mm':book['bleed_mm'],'binding':'left saddle stitch','faces':faces,'folded_reading_order':reading,'all_source_pages_used_once':True,'outputs':outputs,'self_review':True,'independent_review':False,'purpose':'現在の確認版を家庭・学校のプリンターで両面印刷して中綴じするための面付け。商業印刷入稿用のreleaseではない。'}
    record_path=ROOT/'books'/book['id']/'parts'/'saddle-print-20261020.json'
    record_path.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    print(book['title'],n,'pages;',n//4,'sheets; all comparisons passed')
