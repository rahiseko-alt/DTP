"""Supplement visual inspection with Japanese OCR on nine changed raster/native pages."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,json,re
B=Path(__file__).resolve().parent

def scan(n):
 s=subprocess.check_output(['tesseract',str(B/f'draft/page-{n:02}.png'),'stdout','--tessdata-dir','/tmp/brochure-jpn-tessdata','-l','jpn','--psm','3'],stderr=subprocess.DEVNULL,text=True)
 (B/'ocr'/f'after-{n:02}.txt').write_text(s);compact=re.sub(r'\s+','',s);terms=[t for t in ['日本語','JLPT','在留','多言語','留学生','外国人','外国ルーツ','日本で働','すべてオンライン'] if t in compact];return {'page':n,'suspicious_terms':terms}
results=list(ThreadPoolExecutor(max_workers=3).map(scan,[2,3,4,5,6,7,9,10,11]));(B/'ocr-after.json').write_text(json.dumps({'supplementary_only':True,'pages':results},ensure_ascii=False,indent=2)+'\n');print(json.dumps(results,ensure_ascii=False),flush=True)
