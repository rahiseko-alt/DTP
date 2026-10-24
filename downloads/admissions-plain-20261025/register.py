"""Register a separate variant without advancing the original admissions PDF."""
from pathlib import Path
import hashlib,json,subprocess
B=Path(__file__).resolve().parent;R=B.parents[1]
proof=json.loads((B/'build-proof.json').read_text());verify=json.loads((B/'verification.json').read_text())
assert verify['verified']
document='admissions-guide-2027';variant='plain-no-photo-r01'
source={'id':proof['source']['id'],'revision':proof['source']['revision']}
records=[]
def register(aid,p,media,refs):
    h=hashlib.sha256(p.read_bytes()).hexdigest()
    catalog=json.loads((R/f'books/{document}/parts/catalog.yaml').read_text())
    existing=next((a for a in catalog['assets'] if a['id']==aid and a['revision']==h and catalog['current'].get(aid)==h),None)
    if existing:value={'asset':existing}
    else:
        value=json.loads(subprocess.check_output(['node','--import','tsx','system/scripts/assets.ts','register','--document',document,'--id',aid,'--variant',variant,'--role','support','--media',media,'--source',str(p),'--sha256',h,'--confirmation','verified','--built-from',json.dumps(refs),'--save-reason','Separate photo-free R01 based on the fixed 2027 24-page admissions PDF. Six photographs and three related captions removed; photo-free typographic cover, original colors/text/tables/forms/logo/map/QR retained. Saved review edition; original edition and current standard-rendered-pdf ID are not replaced. Standard-render freshness/release not asserted.'],cwd=R,text=True))
    records.append({'id':aid,'registration':value})
    (B/'registration.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
    print(aid,flush=True)
    return {'id':aid,'revision':h}
brief=register('plain-r01-brief',B/'brief.json','text',[source])
copy=register('plain-r01-cover-copy',B/'cover-copy.json','text',[source])
refs=[]
for output in proof['outputs']:
    assert any(v['sha256']==output['sha256'] for v in verify['outputs'])
    aid={'reading':'plain-reading-pdf','print-a3':'plain-print-a3','print-a4':'plain-print-a4'}[output['kind']]
    refs.append(register(aid,R/output['file'],'pdf',[source,brief,copy]))
register('plain-r01-build-proof',B/'build-proof.json','text',refs)
register('plain-cover',B/'output/cover.png','image',[refs[0]])
register('plain-back-cover',B/'output/back-cover.png','image',[refs[0]])
for start in [1,5,9,13,17,21]:register(f'plain-overview-{start:02}',B/f'output/overview-{start:02}.jpg','image',[refs[0]])
