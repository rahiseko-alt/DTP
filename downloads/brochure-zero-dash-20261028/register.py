"""Register table-only revisions; keep all admission documents and archived revisions."""
from pathlib import Path
import copy,hashlib,json,subprocess,zipfile
B=Path(__file__).resolve().parent;R=B.parents[1];doc='prospectus-isen-trial-2028'
proof=json.loads((B/'build-proof.json').read_text());verification=json.loads((B/'verification.json').read_text());assert verification['verified']
base=json.loads((B/'baseline.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
records=[];registered={};preview={};prefix='fee-zero-dash-20261028-'
def save(aid,path,media,refs):
 h=sha(path);cat=json.loads((R/f'books/{doc}/parts/catalog.yaml').read_text())
 a=next((a for a in cat['assets'] if a['id']==aid and a['revision']==h),None)
 if a is None:
  cmd=['node','--import','tsx','system/scripts/assets.ts','register','--document',doc,'--id',aid,'--variant','facility-fee-zero-dash-20261028','--role','support','--media',media,'--source',str(path),'--sha256',h,'--confirmation','verified','--built-from',json.dumps(refs),'--save-reason','User instruction 2026-10-28: replace standalone zero amounts and existing empty-cell dashes in the five-column period table with U+30FC ー. Two zero cells and eight existing dash cells changed; numerical fee facts unchanged. Only reading page13 / imposed face4 table replaced. Amounts, all other pixels/text/fonts/positions/images, AI notice and existing payment conditions retained. Saved composition, not standard-render freshness or release certification.']
  a=json.loads(subprocess.check_output(cmd,cwd=R,text=True))['asset']
 records.append({'document':doc,'asset':a});(B/'registration.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n');print(aid,flush=True)
 return {'id':aid,'revision':h},a
cat=json.loads((R/f'books/{doc}/parts/catalog.yaml').read_text());facts={'id':'tuition-20261027-facts','revision':cat['current']['tuition-20261027-facts']}
renderer,_=save(prefix+'renderer',B/'render-panel.mjs','text',[])
builder,_=save(prefix+'builder',B/'build.py','text',[])
panel,_=save(prefix+'panel',B/'panel.pdf','pdf',[facts,renderer])
for o in proof['outputs']:
 ref,a=save(prefix+o['label'].lower(),R/o['file'],'pdf',[{'id':o['source']['id'],'revision':o['source']['revision']},panel,builder]);registered[o['label']]=a
 _,pa=save(prefix+o['label'].lower()+'-page-'+str(o['changed_page']).zfill(2),B/f'previews/{o["label"]}-page-{o["changed_page"]:02}.png','image',[ref]);preview[o['label']]=pa
 if o['label']=='brochure-jp-r13':
  _,pa=save(prefix+'r13-overview-13',B/'previews/brochure-jp-r13-overview-13.jpg','image',[ref]);preview['overview']=pa
outputs={o['label']:o for o in proof['outputs']}
def info(label):
 a=registered[label];o=outputs[label]
 return {'document':doc,'asset_id':a['id'],'file':a['file'],'sha256':a['sha256'],'bytes':a['size'],'download_file':o['file'],'retrieval_mode':'saved'}
def pv(a):return {'id':a['id'],'file':a['file'],'sha256':a['sha256']}
def update(target,label):
 target['previous_layout_edition']={k:target[k] for k in ['asset_id','file','sha256','bytes','download_file'] if k in target}
 target.update(info(label));target['variant']='facility-fee-zero-dash-20261028'
 target['version_policy']='2026-10-28：5列内訳表の単独0をーへ変更し、空欄記号をー（U+30FC）で統一。年次・時期／授業料／諸経費／施設設備費／合計。施設費は各年年額50,000円、期への配分や納付時期は追加しない。料金・表の外枠/位置・表外の全内容・AI注記・画像・面付けは元の設備費更新PDFを保持。'
 target['review_status']='7PDF全80P/面の表外150dpi画素・文字/書体/字位置・全画像stream一致を確認。新しい施設設備費列に各年50,000円、各期はー。親の自己点検。独立審査・実機試し刷り・入稿承認は未実施。'
 target['freshness_status']='保存済みの局所修正版。標準renderer全冊再生成の保証ではない。'
 target['table_revision']={'date':'2026-10-28','columns':proof['columns'],'manifest':str((B/'manifest.json').relative_to(R))}
v=copy.deepcopy(base['index']);v['date']='2026-10-28';original=v['documents']['brochure'];update(original,'brochure-original')
for p in original['print_outputs']:p.update(info('brochure-original-'+p['paper']))
original['previews']=[pv(preview['brochure-original']) if x['id'].endswith('page-13') else x for x in original['previews']]
jp=next(x for x in v['production_targets'] if x['work_id']=='PAM-JP-ISEN');update(jp,'brochure-jp-r13');jp['status']='改稿13・設備費更新版・内訳5列・ゼロ表記統一版・確認用'
for p in jp['print_outputs']:p.update(info('brochure-jp-r13-'+p['paper']))
jp['master_output']=info('brochure-jp-r13-master')
jp['previews']=[pv(preview['overview']) if 'overview-13' in x['id'] else pv(preview['brochure-jp-r13']) if x['id'].endswith('page-13') else x for x in jp['previews']]
archive=B/'output/print-pdfs-zero-dash-20261028.zip';mapping={'brochure-A3.pdf':'brochure-original-A3','brochure-A4.pdf':'brochure-original-A4'}
with zipfile.ZipFile(R/base['index']['print_bundle']) as old,zipfile.ZipFile(archive,'w') as new:
 for entry in old.infolist():new.writestr(copy.copy(entry),(R/outputs[mapping[entry.filename]]['file']).read_bytes() if entry.filename in mapping else old.read(entry.filename))
with zipfile.ZipFile(R/base['index']['print_bundle']) as old,zipfile.ZipFile(archive) as new:
 assert old.namelist()==new.namelist()
 for name in old.namelist():assert new.read(name)==((R/outputs[mapping[name]]['file']).read_bytes() if name in mapping else old.read(name))
v['previous_print_bundle']={'file':base['index']['print_bundle'],'sha256':base['index']['bundle_sha256']};v['print_bundle']=str(archive.relative_to(R));v['bundle_sha256']=sha(archive)
for key in ['admissions','flyer']:assert v['documents'][key]==base['index']['documents'][key]
for a,b in zip(base['index']['production_targets'],v['production_targets']):
 if a['work_id']!='PAM-JP-ISEN':assert a==b
(R/'downloads/latest-materials.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
manifest={'date':'2026-10-28','source_commit':base['head'],'outputs':[dict(o,registered=info(o['label'])) for o in proof['outputs']],'bundle':{'file':str(archive.relative_to(R)),'sha256':sha(archive),'changed_entries':list(mapping),'unchanged_entries':['admissions-A3.pdf','admissions-A4.pdf','flyer-A4.pdf','PRINTING.txt']},'verification':'verification.json','release':False,'dash_character':'ー','cell_verification':'cell-verification.json'}
(B/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
refs=[{'id':a['id'],'revision':a['revision']} for a in registered.values()]
save(prefix+'manifest',B/'manifest.json','text',refs);save(prefix+'verification',B/'verification.json','text',refs)

save(prefix+'cell-verification',B/'cell-verification.json','text',refs)
