"""Save the reviewed AI-image-notice revision using the existing Japanese-edition IDs."""
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
        value=json.loads(subprocess.check_output(['node','--import','tsx','system/scripts/assets.ts','register','--document','prospectus-isen-trial-2028','--id',aid,'--variant','japanese-people-edition','--role','support','--media',media,'--source',str(p),'--sha256',h,'--confirmation','verified','--built-from',json.dumps(refs),'--save-reason',reason or 'R13: Add the user-approved AI-generation and consent notice only to page 16 of the fixed R12 PDFs. Images and all outside-notice pixels retained. Saved review edition; current standard-render freshness is not asserted.'],cwd=R,text=True))
    records.append({'id':aid,'registration':value})
    (B/'registration.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
    print(aid,flush=True)
    return {'id':aid,'revision':h}
ids={'reading':'jp-isen-reading-pdf','master':'jp-isen-master-pdf','print-a3':'jp-isen-print-a3','print-a4':'jp-isen-print-a4'}
refs=[]
inputs={}
# Input aliases preserve fixed R12 provenance when the existing output IDs advance.
# Registration intentionally disallows self-references even across two revisions.
notice_ref=register('jp-isen-ai-notice-copy',B/'notice.json','text',[],reason='User-confirmed AI generation, processing and brochure publication consent, 2026-10-24; approved disclosure text and typography. Scope limited to the current Japanese ISEN brochure.')
for item in proof['outputs']:
    inputs[item['kind']]=register('jp-isen-r12-source-'+item['kind'],R/item['source']['file'],'pdf',[{'id':item['source']['id'],'revision':item['source']['revision']}],reason='Fixed R12 input for the R13 AI-image-notice addition. Original PDF bytes retained; current standard-render freshness is not asserted.')
for item in proof['outputs']:
    assert any(v['pdf_sha256']==item['sha256'] for v in verified['outputs'])
    refs.append(register(ids[item['kind']],R/item['file'],'pdf',[inputs[item['kind']],notice_ref]))
register('jp-isen-assembly-proof',B/'build-proof.json','text',refs)
for start in [1,5,9,13]:
    register(f'jp-isen-overview-{start:02}',B/f'output/overview-{start:02}.jpg','image',[refs[0]])
