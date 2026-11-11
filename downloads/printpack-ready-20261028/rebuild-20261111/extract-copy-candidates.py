"""Recover editable copy candidates for human verification; never overlays or a release generator."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import fitz,json,subprocess,csv,io,hashlib
B=Path(__file__).resolve().parent;R=Path('/workspace/DTP');source=R/json.loads((B.parent/'receipts.json').read_text())[0]['path'];tmp=R/'.cache/rebuild-20261111/copy';tmp.mkdir(exist_ok=True,parents=True)
def one(pn):
 with fitz.open(source) as d:
  p=d[pn-1];im=tmp/f'p{pn:02}.png';pix=p.get_pixmap(matrix=fitz.Matrix(250/72,250/72),alpha=False);pix.save(im);native=p.get_text('dict')
 raw=subprocess.check_output(['tesseract',str(im),'stdout','--tessdata-dir','/workspace/.dtp-tools/tessdata','-l','jpn+eng','--psm','3','tsv'],stderr=subprocess.DEVNULL,text=True)
 words=[]
 for w in csv.DictReader(io.StringIO(raw),delimiter='\t'):
  if w.get('text','').strip():
   x,y,ww,hh=[int(w[k]) for k in ['left','top','width','height']];words.append({'text':w['text'],'confidence':float(w['conf']),'bbox_pt':[v*72/250 for v in [x,y,x+ww,y+hh]],'line_id':[w[k] for k in ['block_num','par_num','line_num']]})
 result={'page':pn,'source':str(source.relative_to(R)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'status':'unverified_copy_candidates_not_for_print','native_text':native,'OCR_candidates':words};dest=B/'copy-candidates';dest.mkdir(exist_ok=True);(dest/f'page-{pn:02}.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('Copy candidates ready:',pn,flush=True)
with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(one,list(range(1,12))+[16]))
