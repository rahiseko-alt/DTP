from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,subprocess
B=Path(__file__).resolve().parent;R=B.parents[1];v=json.loads((B/'baseline.json').read_text())['index'];photo=v['documents']['admissions'];plain=next(x for x in v['production_targets'] if x['work_id']=='ADM-JP-PLAIN-2027');items=[(photo,'admissions-photo','reading'),(plain,'admissions-plain','reading')]+[(x,'admissions-photo-old-cover-'+x['paper'],'print') for x in photo['print_outputs']]+[(x,'admissions-plain-'+x['paper'],'print') for x in plain['print_outputs']]
def get(item):
 a,label,kind=item;r=json.loads(subprocess.check_output(['node','--import','tsx','system/scripts/assets.ts','get','--document',a['document'],'--id',a['asset_id'],'--role','support','--saved'],cwd=R,text=True));assert r['asset']['sha256']==a['sha256'];r.update(label=label,kind=kind,document=a['document']);return r
receipts=list(ThreadPoolExecutor(max_workers=4).map(get,items));(B/'receipts.json').write_text(json.dumps(receipts,ensure_ascii=False,indent=2)+'\n')
import fitz
p=fitz.open(R/receipts[0]['path']);p[5].get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False).save(B/'before-page-06.png')
