"""Register fixed saved review assets with original-photo dependency references."""
from pathlib import Path
import hashlib,json,subprocess
B=Path(__file__).resolve().parent;R=B.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
sources=json.loads((B/'reviews/photo-input-receipts.json').read_text())
manifest=json.loads((B/'reviews/edited-photo-manifest.json').read_text())
keys={'front-hero':'hero','front-class':'class','front-friends':'friends','front-consult':'consult','back-ai':'ai','back-business':'business','back-lesson':'lesson','back-exchange':'exchange','back-event':'event'}
records=[]
reason='Saved original-art OC review edition with original-photo image edits; identity verified, current standard-render freshness not asserted.'
def register(aid,p,media,refs):
 catalog=json.loads((R/'books/oc-approved-20261017/parts/catalog.yaml').read_text());digest=sha(p)
 existing=next((a for a in catalog['assets'] if a['id']==aid and a['revision']==digest),None)
 if existing:
  assert catalog['current'][aid]==digest and existing['saved'] and existing['role']=='support'
  subprocess.check_output(['node','--import','tsx','system/scripts/assets.ts','get','--document','oc-approved-20261017','--id',aid,'--saved'],cwd=R,text=True)
  result={'asset':existing}
 else:
  result=json.loads(subprocess.check_output(['node','--import','tsx','system/scripts/assets.ts','register','--document','oc-approved-20261017','--id',aid,'--variant','japanese-image-original-art-r2','--role','support','--media',media,'--source',str(p),'--sha256',digest,'--confirmation','verified','--built-from',json.dumps(refs),'--save-reason',reason],cwd=R,text=True))
 records.append({'id':aid,'registration':result});(B/'reviews/asset-registration.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n');print(aid,flush=True)
 return {'id':aid,'revision':digest}
edited=[]
for key,source_key in keys.items():
 a=sources[source_key]['asset'];edited.append(register('ocjp2-edit-'+source_key,R/manifest[key],'image',[{'id':a['id'],'revision':a['revision']}]))
refs=[{'id':'latest-original-oc-pdf','revision':'2c0bd3b6d91449666adf9ac73091e10f7cb37831384ebe807d2ff6117cd264d1'},*edited]
for aid,rel,media in [('jp-oc-original-art-r2-pdf','output/OC黄色帯版_原本写真加工_日本人イメージ_2P.pdf','pdf'),('jp-oc-original-art-r2-front','output/page-1.png','image'),('jp-oc-original-art-r2-back','output/page-2.png','image'),('jp-oc-original-art-r2-proof','reviews/build-proof.json','text'),('jp-oc-original-art-r2-verification','reviews/output-verification.json','text')]:register(aid,B/rel,media,refs)
