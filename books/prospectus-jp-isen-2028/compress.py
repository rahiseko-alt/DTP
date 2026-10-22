from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,json,hashlib,fitz
from PIL import Image,ImageChops,ImageStat
from pypdf import PdfWriter
from pypdf.generic import NameObject,DictionaryObject
b=Path(__file__).resolve().parent;out=b/'output'
files=[('医専日本人版_16P_確認用.pdf','医専日本人版_16P_閲覧用.pdf'),('医専日本人版_A3_中綴じ_短辺反転.pdf','医専日本人版_A3_印刷用.pdf'),('医専日本人版_A4_中綴じ_短辺反転.pdf','医専日本人版_A4_印刷用.pdf')]
flags=['-sDEVICE=pdfwrite','-dCompatibilityLevel=1.7','-dNOPAUSE','-dBATCH','-dSAFER','-dDownsampleColorImages=true','-dColorImageResolution=200','-dColorImageDownsampleType=/Bicubic','-dAutoFilterColorImages=false','-dColorImageFilter=/DCTEncode','-dDownsampleGrayImages=true','-dGrayImageResolution=200','-dAutoFilterGrayImages=false','-dGrayImageFilter=/DCTEncode','-dJPEGQ=92','-dCompressFonts=true','-dSubsetFonts=true','-dDetectDuplicateImages=true']
def one(pair):
 source,dest=[out/p for p in pair];temp=out/(dest.stem+'-gs.pdf');subprocess.run(['gs',*flags,f'-sOutputFile={temp}',str(source)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
 writer=PdfWriter(clone_from=temp);writer._root_object[NameObject('/ViewerPreferences')]=DictionaryObject({NameObject('/Duplex'):NameObject('/DuplexFlipShortEdge'),NameObject('/PrintScaling'):NameObject('/None'),NameObject('/Direction'):NameObject('/L2R')});writer.write(dest);temp.unlink()
 a,c=fitz.open(source),fitz.open(dest);assert len(a)==len(c);deltas=[]
 for p,q in zip(a,c):
  assert max(abs(x-y) for x,y in zip(p.rect,q.rect))<.05
  x=p.get_pixmap(matrix=fitz.Matrix(.5,.5));y=q.get_pixmap(matrix=fitz.Matrix(.5,.5));u=Image.frombytes('RGB',(x.width,x.height),x.samples);v=Image.frombytes('RGB',(y.width,y.height),y.samples);delta=sum(ImageStat.Stat(ImageChops.difference(u,v)).mean)/3
  assert delta<4,(dest,delta);deltas.append(delta)
 return {'file':str(dest),'sha256':hashlib.file_digest(dest.open('rb'),'sha256').hexdigest(),'bytes':dest.stat().st_size,'pages':len(c),'max_mean_rgb_error':max(deltas),'compression':'200dpi JPEG92; compare against lossless assembly'}
with ThreadPoolExecutor(max_workers=3) as e: records=list(e.map(one,files))
(b/'reviews/compressed-output-proof.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n');print(json.dumps(records,ensure_ascii=False))
