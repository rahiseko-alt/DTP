"""Register the explicit saved OC review edition; do not assert current render freshness."""
from pathlib import Path
import hashlib,json,subprocess
B=Path(__file__).resolve().parent; R=B.parents[1]
source_sha='2c0bd3b6d91449666adf9ac73091e10f7cb37831384ebe807d2ff6117cd264d1'
items=[('jp-oc-reading-pdf','output/OC黄色帯版_日本人イメージ_構成変更案_2P.pdf','pdf'),('jp-oc-front','output/page-1.png','image'),('jp-oc-back','output/page-2.png','image'),('jp-oc-build-proof','reviews/build-inputs.json','text'),('jp-oc-verification','reviews/output-verification.json','text')]
records=[]
for aid,rel,media in items:
 p=B/rel;sha=hashlib.sha256(p.read_bytes()).hexdigest()
 result=subprocess.check_output(['node','--import','tsx','system/scripts/assets.ts','register','--document','oc-approved-20261017','--id',aid,'--variant','japanese-people-oc-revised','--role','support','--media',media,'--source',str(p),'--sha256',sha,'--confirmation','verified','--built-from',json.dumps([{'id':'latest-original-oc-pdf','revision':source_sha}]),'--save-reason','User-directed Japanese-image OC review edition; saved PDF/PNG with verified identity, not current-input standard-render provenance.'],cwd=R,text=True)
 records.append({'id':aid,'registration':json.loads(result)})
 print(aid,flush=True)
(B/'reviews/asset-registration.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
