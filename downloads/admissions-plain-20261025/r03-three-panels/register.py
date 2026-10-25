from pathlib import Path
import hashlib,json,subprocess
B=Path(__file__).resolve().parent;R=B.parents[2]
proof=json.loads((B/'build-proof.json').read_text());assert json.loads((B/'verification.json').read_text())['verified']
records=[]
def save(aid,path,media,refs):
    h=hashlib.sha256(path.read_bytes()).hexdigest();cat=json.loads((R/'books/admissions-guide-2027/parts/catalog.yaml').read_text())
    prior=next((a for a in cat['assets'] if a['id']==aid and a['revision']==h and cat['current'].get(aid)==h),None)
    if prior:value={'asset':prior}
    else:value=json.loads(subprocess.check_output(['node','--import','tsx','system/scripts/assets.ts','register','--document','admissions-guide-2027','--variant','plain-no-photo-r03','--id',aid,'--role','support','--media',media,'--source',str(path),'--sha256',h,'--confirmation','verified','--built-from',json.dumps(refs),'--save-reason','R03: Only the three user-specified areas on saved R02 pages 2-3: TOC P7/P11-22 white, total59 card white/navy, admission-permission card white with gold top stripe. No other paper changes. Text/fonts/positions/images and every other page retained. Saved review edition; original admissions edition retained; standard-render freshness/release not asserted.'],cwd=R,text=True))
    records.append({'id':aid,'registration':value});(B/'registration.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n');print(aid,flush=True)
    return {'id':aid,'revision':h}
old=proof['outputs'][0]['source']
alias={'id':old['id'],'revision':old['revision']}
policy=save('plain-r03-color-policy',B/'color-policy.json','text',[alias])
outputs=[]
for out in proof['outputs']:
    aid={'reading':'plain-r03-reading-pdf','print-a3':'plain-r03-print-a3','print-a4':'plain-r03-print-a4'}[out['kind']]
    refs=[alias,policy] if out['kind']=='reading' else [outputs[0],policy]
    outputs.append(save(aid,R/out['file'],'pdf',refs))
save('plain-r03-build-proof',B/'build-proof.json','text',outputs)
for n in [1,5,9,13,17,21]:save(f'plain-r03-overview-{n:02}',B/f'output/overview-{n:02}.jpg','image',[outputs[0]])
for n in [2,3]:save(f'plain-r03-page-{n:02}',B/f'output/page-{n:02}-detail.png','image',[outputs[0]])
