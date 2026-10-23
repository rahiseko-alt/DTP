"""Save the reviewed English-name revision using the existing Japanese-edition IDs."""
from pathlib import Path
import hashlib,json,subprocess
B=Path(__file__).resolve().parent;R=B.parents[1]
proof=json.loads((B/'build-proof.json').read_text());verified=json.loads((B/'verification.json').read_text())
assert verified['verified']
records=[]
def register(aid,p,media,refs,reason=None):
    h=hashlib.sha256(p.read_bytes()).hexdigest()
    catalog=json.loads((R/'books/prospectus-isen-trial-2028/parts/catalog.yaml').read_text())
    prior=next((a for a in catalog['assets'] if a['id']==aid and a['revision']==h),None)
    if prior and catalog['current'].get(aid)==h:
        value={'asset':prior}
    else:
        value=json.loads(subprocess.check_output(['node','--import','tsx','system/scripts/assets.ts','register','--document','prospectus-isen-trial-2028','--id',aid,'--variant','japanese-people-edition','--role','support','--media',media,'--source',str(p),'--sha256',h,'--confirmation','verified','--built-from',json.dumps(refs),'--save-reason',reason or 'R12: English school name read from school.yaml, three fields replaced in the fixed R11 PDF. Images and all outside-field pixels retained. Saved review edition; current standard-render freshness is not asserted.'],cwd=R,text=True))
    records.append({'id':aid,'registration':value})
    (B/'registration.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
    print(aid,flush=True)
    return {'id':aid,'revision':h}
ids={'reading':'jp-isen-reading-pdf','master':'jp-isen-master-pdf','print-a3':'jp-isen-print-a3','print-a4':'jp-isen-print-a4'}
refs=[]
inputs={}
# Input aliases preserve fixed R11 provenance when the existing output IDs advance.
# Registration intentionally disallows self-references even across two revisions.
for item in proof['outputs']:
    inputs[item['kind']]=register('jp-isen-r11-source-'+item['kind'],R/item['source']['file'],'pdf',[{'id':item['source']['id'],'revision':item['source']['revision']}],reason='Fixed R11 input for the R12 English-name correction. Original PDF bytes retained; current standard-render freshness is not asserted.')
for item in proof['outputs']:
    assert any(v['pdf_sha256']==item['sha256'] for v in verified['outputs'])
    refs.append(register(ids[item['kind']],R/item['file'],'pdf',[inputs[item['kind']]]))
register('jp-isen-assembly-proof',B/'build-proof.json','text',refs)
for start in [1,5,9,13]:
    register(f'jp-isen-overview-{start:02}',B/f'output/overview-{start:02}.jpg','image',[refs[0]])
