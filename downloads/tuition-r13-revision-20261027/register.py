"""Register R13 fee-only saved editions while preserving AI notice and all other materials."""
from pathlib import Path
import copy,hashlib,json,subprocess
B=Path(__file__).resolve().parent;R=B.parents[1]
proof=json.loads((B/'build-proof.json').read_text());verification=json.loads((B/'verification.json').read_text())
assert verification['verified'] and len(verification['outputs'])==4
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
records=[];registered={};preview_refs={}
def save(doc,aid,path,media,refs):
 h=sha(path);cat=json.loads((R/f'books/{doc}/parts/catalog.yaml').read_text())
 prior=next((a for a in cat['assets'] if a['id']==aid and a['revision']==h and cat['current'].get(aid)==h),None)
 if prior:a=prior
 else:
  v=json.loads(subprocess.check_output(['node','--import','tsx','system/scripts/assets.ts','register','--document',doc,'--id',aid,'--variant','tuition-facility-20261027','--role','support','--media',media,'--source',str(path),'--sha256',h,'--confirmation','verified','--built-from',json.dumps(refs),'--save-reason','2026-10-27 user-authorized fee-only revision: annual facility fee 50000 yen in EACH of years 1 and 2, totals 980000/880000/1860000; exam fee unchanged. Saved native PDF composition, not standard-renderer freshness or release certification. Each original edition/cover/photo/policy/page order retained.'],cwd=R,text=True));a=v['asset']
 records.append({'document':doc,'asset':a});(B/'registration.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n');print(aid,flush=True)
 return {'id':aid,'revision':h},a

doc='prospectus-isen-trial-2028'
cat=json.loads((R/f'books/{doc}/parts/catalog.yaml').read_text())
ref=lambda aid:{'id':aid,'revision':cat['current'][aid]}
facts=ref('tuition-20261027-facts');builder=ref('tuition-20261027-builder')
panels=[ref('tuition-20261027-panel-annual'),ref('tuition-20261027-panel-periods')]
for out in proof['outputs']:
 source={'id':out['source']['id'],'revision':out['source']['revision']}
 output_ref,a=save(doc,'tuition-20261027-'+out['label'].lower(),R/out['file'],'pdf',[source,facts,builder,*panels]);registered[out['label']]=a
 for pn in sorted(out['changed_regions'],key=int):
  _,pa=save(doc,f'tuition-20261027-{out["label"].lower()}-page-{int(pn):02}',B/f'previews/{out["label"]}-page-{int(pn):02}.png','image',[output_ref]);preview_refs[(out['label'],int(pn))]=pa
 if out['label']=='brochure-jp-r13':
  for pn in [9,13]:
   _,pa=save(doc,f'tuition-20261027-r13-overview-{pn:02}',B/f'previews/{out["label"]}-overview-{pn:02}.jpg','image',[output_ref]);preview_refs[('overview',pn)]=pa
outputs={x['label']:x for x in proof['outputs']}
def info(label):
 a=registered[label];out=outputs[label]
 return {'document':doc,'asset_id':a['id'],'file':a['file'],'sha256':a['sha256'],'bytes':a['size'],'download_file':out['file'],'retrieval_mode':'saved'}
def pv(a):return {'id':a['id'],'file':a['file'],'sha256':a['sha256']}
index_file=R/'downloads/latest-materials.json';old=json.loads(index_file.read_text());new=copy.deepcopy(old)
target=next(t for t in new['production_targets'] if t['work_id']=='PAM-JP-ISEN')
target['previous_fee_edition']={k:target[k] for k in ['asset_id','file','sha256','bytes','download_file'] if k in target}
target.update(info('brochure-jp-r13'))
target['variant']='tuition-facility-20261027'
target['status']='改稿13・AI注記を保持・2026-10-27料金改定・確認用'
target['version_policy']='R13のAI注記と本人承諾記録を保持し、料金表・合計だけを更新。施設設備費は各年50,000円、年次合計980,000/880,000円、2年間1,860,000円、検定料込み1,880,000円。表紙・写真・料金以外の本文・ページ順・納付期限・返還説明は各R13元PDFのまま。AI注記の採否は変更しない。'
target['review_status']='4出力全48P/面の料金外150dpi画素・文字・書体・位置・全画像stream一致、QR確認。親の自己点検、独立審査・実機試し刷り・入稿承認は未実施。'
target['freshness_status']='保存済み料金改定版。既存PDFの料金領域だけを更新。標準rendererによる全冊再生成の保証ではない。'
for p in target['print_outputs']:p.update(info('brochure-jp-r13-'+p['paper']))
target['master_output']=info('brochure-jp-r13-master')
for i,a in enumerate(target['previews']):
 for pn in [9,13]:
  if a['id']==f'jp-isen-overview-{pn:02}':target['previews'][i]=pv(preview_refs[('overview',pn)])
target['previews'] += [pv(preview_refs[('brochure-jp-r13',pn)]) for pn in [12,13]]
target['fee_revision']={'date':'2026-10-27','manifest':str((B/'manifest.json').relative_to(R))}
for k in old:
 if k!='production_targets':assert old[k]==new[k],k
for a,c in zip(old['production_targets'],new['production_targets']):
 if a['work_id']!='PAM-JP-ISEN':assert a==c
assert target['ai_image_status']==next(t for t in old['production_targets'] if t['work_id']=='PAM-JP-ISEN')['ai_image_status']
index_file.write_text(json.dumps(new,ensure_ascii=False,indent=2)+'\n')
manifest={'date':'2026-10-27','source_r13_commit':'21caee0badeadcacab90778919a736f53d1eca32','fee_merge_commit':'f2d6a8f','outputs':[dict(o,registered=info(o['label'])) for o in proof['outputs']],'verification':'verification.json','notice_retained':True,'main_merge':False,'release':False}
(B/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
refs=[{'id':a['id'],'revision':a['revision']} for a in registered.values()]
save(doc,'tuition-20261027-r13-manifest',B/'manifest.json','text',refs)
save(doc,'tuition-20261027-r13-verification',B/'verification.json','text',refs)
print('4 R13 fee editions registered; AI notice and all other index targets retained',flush=True)
