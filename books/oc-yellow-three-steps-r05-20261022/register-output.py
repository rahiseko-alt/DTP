"""Register fixed saved R05 PDF and back preview; front reuses R04."""
from pathlib import Path
import hashlib,json,subprocess
B=Path(__file__).resolve().parent;R=B.parents[1]
proof=json.loads((B/'reviews/build-proof.json').read_text())
assert json.loads((B/'reviews/output-verification.json').read_text())['pdf_sha256']==proof['pdf_sha256']
records=[]
def register(aid,path,media,refs):
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    result=json.loads(subprocess.check_output(['node','--import','tsx','system/scripts/assets.ts','register','--document','oc-approved-20261017','--id',aid,'--variant','original-art-three-steps-r5','--role','support','--media',media,'--source',str(path),'--sha256',digest,'--confirmation','verified','--built-from',json.dumps(refs),'--save-reason','Saved R05 three-step back flow revision. Front and other back areas pixel-identical to R04. Font-subset download copy; current standard-render freshness is not asserted.'],cwd=R,text=True))
    records.append({'id':aid,'registration':result})
    (B/'reviews/asset-registration.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
    print(aid,flush=True)
    return {'id':aid,'revision':digest}
pdf=register('jp-oc-three-r5-pdf',R/proof['pdf'],'pdf',[{'id':proof['source']['id'],'revision':proof['source']['revision']}])
register('jp-oc-three-r5-back',B/'output/page-2.png','image',[pdf])
