"""Fresh-process rendering: never populate MuPDF's text/image extraction caches."""
from pathlib import Path
import sys,fitz
from PIL import Image,ImageDraw
source=Path(sys.argv[1]);output=Path(sys.argv[2]);output.mkdir(parents=True,exist_ok=True)
doc=fitz.open(source)
for i,page in enumerate(doc,1):
    page.get_pixmap(matrix=fitz.Matrix(150/72,150/72)).save(output/f'page-{i:02}.png')
if '--overviews' in sys.argv:
    for start in [1,5,9,13]:
        canvas=Image.new('RGB',(1248,1768),'#eeeeee')
        for j in range(4):
            im=Image.open(output/f'page-{start+j:02}.png').convert('RGB');im.thumbnail((604,854))
            x=10+(j%2)*624+(604-im.width)//2;y=10+(j//2)*884
            canvas.paste(im,(x,y));ImageDraw.Draw(canvas).text((x,y+im.height+3),f'PDF {start+j}',fill='#333333')
        canvas.save(output/f'overview-{start:02}.jpg',quality=90)
    # Cover and detail are rendered before any text extraction as well.
    doc[-1].get_pixmap(matrix=fitz.Matrix(1.3,1.3)).save(output/'back-cover.png')
    doc[-1].get_pixmap(matrix=fitz.Matrix(3,3),clip=fitz.Rect(35,792,564,837)).save(output/'notice-detail.png')
