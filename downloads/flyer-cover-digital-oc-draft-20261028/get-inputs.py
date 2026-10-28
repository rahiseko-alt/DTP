from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,subprocess,hashlib
import fitz
B=Path(__file__).resolve().parent;R=B.parents[1];idx=json.loads((R/'downloads/latest-materials.json').read_text());items=[next(x for x in idx['production_targets'] if x['work_id']==wid) for wid in ['PAM-JP-ISEN','FLY-JP-OC-YELLOW']]
def get(a):
 r=json.loads(subprocess.check_output(['node','--import','tsx','system/scripts/assets.ts','get','--document',a['document'],'--id',a['asset_id'],'--saved'],cwd=R,text=True));assert hashlib.sha256((R/r['path']).read_bytes()).hexdigest()==a['sha256'];r['work_id']=a['work_id'];return r
receipts=list(ThreadPoolExecutor(max_workers=2).map(get,items));(B/'receipts.json').write_text(json.dumps(receipts,ensure_ascii=False,indent=2)+'\n')
for item in receipts:
 d=fitz.open(R/item['path']);name='brochure-cover' if item['work_id']=='PAM-JP-ISEN' else 'oc'
 for pn in ([0] if name=='brochure-cover' else [0,1]):d[pn].get_pixmap(matrix=fitz.Matrix(1.4,1.4),alpha=False).save(B/f'{name}-{pn+1:02}.png')
