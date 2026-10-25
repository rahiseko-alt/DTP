"""Render in a fresh process without populating extraction caches first."""
from pathlib import Path
import sys,fitz
from PIL import Image,ImageDraw
source=Path(sys.argv[1]);output=Path(sys.argv[2]);output.mkdir(parents=True,exist_ok=True)
doc=fitz.open(source)
for i,p in enumerate(doc,1):p.get_pixmap(matrix=fitz.Matrix(150/72,150/72)).save(output/f'page-{i:02}.png')
if '--overviews' in sys.argv:
    for start in [1,5,9,13,17,21]:
        canvas=Image.new('RGB',(1248,1768),'#eeeeee');draw=ImageDraw.Draw(canvas)
        for j in range(4):
            im=Image.open(output/f'page-{start+j:02}.png').convert('RGB');im.thumbnail((604,854))
            x=10+(j%2)*624+(604-im.width)//2;y=10+(j//2)*884
            canvas.paste(im,(x,y));draw.text((x,y+im.height+3),f'PDF {start+j}',fill='#333333')
        canvas.save(output/f'overview-{start:02}.jpg',quality=90)
    # Every reading spread, including both single-page covers.
    pairs=[[1]]+[[i,i+1] for i in range(2,24,2)]+[[24]]
    for i,pair in enumerate(pairs):
        canvas=Image.new('RGB',(1248,884),'#eeeeee');draw=ImageDraw.Draw(canvas)
        for j,n in enumerate(pair):
            im=Image.open(output/f'page-{n:02}.png').convert('RGB');im.thumbnail((604,854))
            x=10+j*624 if len(pair)==2 else (1248-im.width)//2
            canvas.paste(im,(x,10));draw.text((x,867),f'PDF {n}',fill='#333333')
        canvas.save(output/f'spread-{i:02}.jpg',quality=90)
    for k in range(6):
        canvas=Image.new('RGB',(1248,1768),'#eeeeee')
        for j,n in enumerate([1+2*k,2+2*k]):canvas.paste(Image.open(output/f'spread-{n:02}.jpg'),(0,884*j))
        canvas.save(output/f'review-spreads-{k+1:02}.jpg',quality=90)
    doc[0].get_pixmap(matrix=fitz.Matrix(1.3,1.3)).save(output/'cover.png')
    doc[-1].get_pixmap(matrix=fitz.Matrix(1.3,1.3)).save(output/'back-cover.png')
    for paper in ['A3','A4']:
        imposed=output/f'admissions-plain-2027-r01-{paper}.pdf'
        if imposed.exists():
            sheet=fitz.open(imposed)
            sheet[0].get_pixmap(matrix=fitz.Matrix(1.1,1.1)).save(output/f'print-first-face-{paper}.png')
