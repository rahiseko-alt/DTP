from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,subprocess,hashlib
B=Path(__file__).resolve().parent;R=B.parents[1];v=json.load(open(B/'baseline.json'))['index'];j=next(x for x in v['production_targets'] if x['work_id']=='PAM-JP-ISEN');f=json.load(open(R/'downloads/flyer-cover-digital-oc-draft-20261028/manifest.json'));items=[('brochure',j['master_output']['document'],j['master_output']['asset_id']),('flyer',f['document'],f['pdf']['id'])]
def get(x):
 label,doc,aid=x;r=json.loads(subprocess.check_output(['node','--import','tsx','system/scripts/assets.ts','get','--document',doc,'--id',aid,'--role','support','--saved'],cwd=R,text=True));assert hashlib.sha256((R/r['path']).read_bytes()).hexdigest()==r['asset']['sha256'];r['label']=label;return r
(B/'receipts.json').write_text(json.dumps(list(ThreadPoolExecutor(max_workers=2).map(get,items)),ensure_ascii=False,indent=2)+'\n')
