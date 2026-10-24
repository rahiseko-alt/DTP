"""Register saved R06 and reuse the pixel-identical R05 back preview."""
from pathlib import Path
import hashlib,json,subprocess
B=Path(__file__).resolve().parent;R=B.parents[2]
proof=json.loads((B/'build-proof.json').read_text());verified=json.loads((B/'verification.json').read_text())
assert verified['verified'] and verified['pdf_sha256']==proof['pdf_sha256']
records=[]
def register(aid,p,media,refs):
    h=hashlib.sha256(p.read_bytes()).hexdigest()
    catalog=json.loads((R/'books/oc-approved-20261017/parts/catalog.yaml').read_text())
    prior=next((a for a in catalog['assets'] if a['id']==aid and a['revision']==h),None)
    if prior and catalog['current'].get(aid)==h:value={'asset':prior}
    else:
        value=json.loads(subprocess.check_output(['node','--import','tsx','system/scripts/assets.ts','register','--document','oc-approved-20261017','--id',aid,'--variant','original-art-english-name-r6','--role','support','--media',media,'--source',str(p),'--sha256',h,'--confirmation','verified','--built-from',json.dumps(refs),'--save-reason','Saved OC R06: two English subtitles use school.yaml formal name. Both crests and every pixel outside those fields, including the entire R05 back, retained. Current standard-render freshness is not asserted.'],cwd=R,text=True))
    records.append({'id':aid,'registration':value});(B/'registration.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n');print(aid,flush=True)
    return {'id':aid,'revision':h}
pdf=register('jp-oc-english-r6-pdf',R/proof['pdf'],'pdf',[{'id':proof['source']['id'],'revision':proof['source']['revision']}])
register('jp-oc-english-r6-front',B/'output/page-1.png','image',[pdf])
