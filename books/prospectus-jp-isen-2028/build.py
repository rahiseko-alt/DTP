#!/usr/bin/env python3
"""保存済み医専16Pの表紙を再構成し本文写真を差し替える固定アダプター。原本は保持。"""
from pathlib import Path
import hashlib, io, json, subprocess
import fitz
from PIL import Image, ImageDraw
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
BOOK = Path(__file__).resolve().parent
SOURCE_SHA = '62aa8e4415e5e6aa4523e1c14d024d8d45112d81dc92ce8db16db7718066f880'
SOURCE = ROOT / f'books/prospectus-isen-trial-2028/parts/latest-prospectus-pdf/{SOURCE_SHA}/latest-prospectus-pdf.pdf'
PAGES = {1:'revision3-cover/cover-page.png',2:'heroes/page-02.png',3:'learning-a/page-03.png',
         4:'heroes/page-04.png',5:'learning-a/page-05.png',6:'heroes/page-06.png',
         7:'learning-b/page-07.png',8:'teacher/page-08.png',9:'learning-b/page-09.png',
         10:'support/page-10.png',11:'support/page-11.png'}
PHOTO12 = [327.9923095703125,53.80705642700195,564.502197265625,150.66348266601562]
def sha(p):
    return hashlib.file_digest(p.open('rb'),'sha256').hexdigest()

def main():
    assert sha(SOURCE)==SOURCE_SHA
    output=BOOK/'output';output.mkdir(exist_ok=True)
    proofdir=BOOK/'reviews';proofdir.mkdir(exist_ok=True)
    src=fitz.open(SOURCE);doc=fitz.open(SOURCE);assert len(doc)==16
    inputs=[]
    for pn,rel in PAGES.items():
        p=BOOK/'work'/rel
        im=Image.open(p);assert im.size==(2480,3508),(pn,im.size)
        xref=doc[pn-1].get_images(full=True)[0][0]
        doc[pn-1].replace_image(xref,filename=str(p))
        inputs.append({'page':pn,'file':str(p.relative_to(ROOT)),'sha256':sha(p)})
    photo=BOOK/'work/support/p12-photo.png';assert photo.is_file()
    doc[11].insert_image(fitz.Rect(PHOTO12),filename=str(photo),keep_proportion=False,overlay=True)
    inputs.append({'page':12,'file':str(photo.relative_to(ROOT)),'sha256':sha(photo),'rect_pt':PHOTO12})
    dest=output/'医専日本人版_16P_確認用.pdf'
    doc.set_metadata({**doc.metadata,'title':'AIビジネス専門学校 医専日本人版 16P 確認用','subject':'既存医専版の写真差替。加工人物画像を含む。年度・学費・入試条件は制作元と同じ。'})
    doc.save(dest,garbage=4,deflate=True);doc.close()
    final=fitz.open(dest);assert len(final)==16
    checks={}
    for i in range(16):
        a,b=src[i],final[i];assert a.rect==b.rect
        assert a.get_text()==b.get_text(),('native text',i+1)
        if i>=12:
            assert a.get_pixmap().samples==b.get_pixmap().samples,('unchanged page',i+1)
        if i==11:
            pa,pb=a.get_pixmap(matrix=fitz.Matrix(2,2)),b.get_pixmap(matrix=fitz.Matrix(2,2))
            aa=np.frombuffer(pa.samples,np.uint8).reshape(pa.height,pa.width,pa.n)
            bb=np.frombuffer(pb.samples,np.uint8).reshape(pb.height,pb.width,pb.n)
            mask=np.zeros(aa.shape[:2],bool);x0,y0,x1,y1=PHOTO12
            mask[int(y0*2)-2:int(y1*2)+3,int(x0*2)-2:int(x1*2)+3]=True
            assert np.array_equal(aa[~mask],bb[~mask]),'p12 photograph outside'
        checks[str(i+1)]={'native_text_identical':True,'page_size_identical':True,
                          'whole_page_pixels_identical':True if i>=12 else None}
    previewdir=output/'pages';previewdir.mkdir(exist_ok=True)
    for i,p in enumerate(final):
        p.get_pixmap(matrix=fitz.Matrix(1.4,1.4)).save(previewdir/f'page-{i+1:02}.png')
    for start in (1,5,9,13):
        canvas=Image.new('RGB',(1000,1470),'#dddddd');draw=ImageDraw.Draw(canvas)
        for k,pn in enumerate(range(start,start+4)):
            im=Image.open(previewdir/f'page-{pn:02}.png');im.thumbnail((490,705))
            x=(k%2)*500+(500-im.width)//2;y=(k//2)*735+25
            canvas.paste(im,(x,y));draw.text((x,y-20),f'PDF {pn}',fill='black')
        canvas.save(output/f'overview-{start:02}.jpg')
    # All sixteen reading pages appear exactly once in each four-sheet booklet.
    faces=[{'sheet':k+1,'side':side,'left':left,'right':right}
           for k in range(4) for side,left,right in [('front',16-2*k,1+2*k),('back',2+2*k,15-2*k)]]
    assert sorted(v for f in faces for v in (f['left'],f['right']))==list(range(1,17))
    printouts=[];mm=72/25.4
    for paper,w,h in [('A3',420,297),('A4',297,210)]:
        imposed=fitz.open()
        for f in faces:
            p=imposed.new_page(width=w*mm,height=h*mm)
            for side,pn in enumerate((f['left'],f['right'])):
                rect=fitz.Rect(side*w/2*mm,0,(side+1)*w/2*mm,h*mm)
                p.show_pdf_page(rect,final,pn-1)
        target=output/f'医専日本人版_{paper}_中綴じ_短辺反転.pdf'
        imposed.save(target,garbage=4,deflate=True);imposed.close()
        printouts.append({'paper':paper,'file':str(target.relative_to(ROOT)),'sha256':sha(target),'faces':8,'sheets':4})
    proof={'source':str(SOURCE.relative_to(ROOT)),'source_sha256':SOURCE_SHA,'source_unchanged':sha(SOURCE)==SOURCE_SHA,
           'file':str(dest.relative_to(ROOT)),'sha256':sha(dest),'pages':16,'inputs':inputs,'checks':checks,
           'changed_pages':list(range(1,13)),'unchanged_pages':[13,14,15,16],
           'p12_native_text_and_photo_outside_pixels_identical':True,'print_faces':faces,'print_outputs':printouts,
           'release':False,'physical_print_test':False,'scope':'改稿5は表紙下部を透過グラデーションと滑らかな写真フェードへ調整。元医専の英字見出し・校名・白明朝コピーを元位置で保持し、既存切抜き写真を灰色背景へ合成。本文は人間確認済み改稿2のまま。'}
    (proofdir/'assembly-proof.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'file':str(dest),'sha256':proof['sha256'],'pages':16,'print':printouts},ensure_ascii=False))

if __name__=='__main__':main()
