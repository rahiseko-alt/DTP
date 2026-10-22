"""Register two fixed saved R04 outputs; reuse the unchanged R03 back preview."""
from pathlib import Path
import hashlib,json,subprocess
B=Path(__file__).resolve().parent;R=B.parents[1]
proof=json.loads((B/'reviews/build-proof.json').read_text())
records=[]
def register(aid,path,media,refs):
 digest=hashlib.sha256(path.read_bytes()).hexdigest()
 result=json.loads(subprocess.check_output(['node','--import','tsx','system/scripts/assets.ts','register','--document','oc-approved-20261017','--id',aid,'--variant','original-art-parent-caption-r4','--role','support','--media',media,'--source',str(path),'--sha256',digest,'--confirmation','verified','--built-from',json.dumps(refs),'--save-reason','Saved R04 front caption/badge revision; current standard-render freshness is not asserted.'],cwd=R,text=True))
 records.append({'id':aid,'registration':result});(B/'reviews/asset-registration.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n');print(aid,flush=True)
 return {'id':aid,'revision':digest}
pdf=register('jp-oc-parent-r4-pdf',R/proof['pdf'],'pdf',[{'id':proof['source']['id'],'revision':proof['source']['revision']}])
register('jp-oc-parent-r4-front',B/'output/page-1.png','image',[pdf])
