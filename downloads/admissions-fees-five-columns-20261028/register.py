"""Register table-only revisions; keep all historical revisions and archived revisions."""
from pathlib import Path
import copy,hashlib,json,subprocess,zipfile
B=Path(__file__).resolve().parent;R=B.parents[1];doc='admissions-guide-2027'
proof=json.loads((B/'build-proof.json').read_text());verification=json.loads((B/'verification.json').read_text());assert verification['verified']
base=json.loads((B/'baseline.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
records=[];registered={};preview={};prefix='admissions-five-columns-20261028-'
def save(aid,path,media,refs):
 h=sha(path);cat=json.loads((R/f'books/{doc}/parts/catalog.yaml').read_text())
 a=next((a for a in cat['assets'] if a['id']==aid and a['revision']==h),None)
 if a is None:
  cmd=['node','--import','tsx','system/scripts/assets.ts','register','--document',doc,'--id',aid,'--variant','tuition-five-columns-dash-20261028','--role','support','--media',media,'--source',str(path),'--sha256',h,'--confirmation','verified','--built-from',json.dumps(refs),'--save-reason','User instruction 2026-10-28: make the admissions fee table five columns matching the brochure: period, tuition, misc expenses, annual facility fee, total. Facility fee is 50000 yen in each year, no term allocation or new deadlines. Standalone zero and empty cells use U+30FC ー. Only fee-table area of reading page6 / imposed face6 changed; prices, all other pixels/text/fonts/positions/images, covers, QR, blank backs and imposition retained. Saved composition, not standard-render freshness or release certification.']
  a=json.loads(subprocess.check_output(cmd,cwd=R,text=True))['asset']
 records.append({'document':doc,'asset':a});(B/'registration.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n');print(aid,flush=True)
 return {'id':aid,'revision':h},a
cat=json.loads((R/f'books/{doc}/parts/catalog.yaml').read_text());facts={'id':'tuition-20261027-facts','revision':cat['current']['tuition-20261027-facts']}
renderer,_=save(prefix+'renderer',B/'render-panel.mjs','text',[]);builder,_=save(prefix+'builder',B/'build.py','text',[]);panel,_=save(prefix+'panel',B/'panels/admissions.pdf','pdf',[facts,renderer])
for o in proof['outputs']:
 ref,a=save(prefix+o['label'].lower(),R/o['file'],'pdf',[{'id':o['source']['id'],'revision':o['source']['revision']},panel,builder]);registered[o['label']]=a
 _,pa=save(prefix+o['label'].lower()+'-page-'+str(o['changed_page']).zfill(2),B/f'previews/{o["label"]}-page-{o["changed_page"]:02}.png','image',[ref]);preview[o['label']]=pa
outputs={o['label']:o for o in proof['outputs']}
def info(label):
 a=registered[label];o=outputs[label]
 return {'document':doc,'asset_id':a['id'],'file':a['file'],'sha256':a['sha256'],'bytes':a['size'],'download_file':o['file'],'retrieval_mode':'saved'}
def pv(a):return {'id':a['id'],'file':a['file'],'sha256':a['sha256']}
def update(target,label):
 target['previous_layout_edition']={k:target[k] for k in ['asset_id','file','sha256','bytes','download_file'] if k in target};target.update(info(label));target['variant']='tuition-five-columns-dash-20261028'
 target['version_policy']='2026-10-28：学費表を年次・時期／授業料／諸経費／施設設備費／合計の5列へ。施設費は各年50,000円の年額行とし、期への配分や納付時期は追加しない。単独0と空欄はー（U+30FC）。金額・年次合計・総額・表外の全文/書体/位置/写真・表紙・願書/白紙裏・QR・面付けを保持。'
 target['review_status']='5PDF・84P/面を150dpi比較し、表外の画素・文字/書体/位置と全元画像stream一致。全5列と年額施設費、ー表記、合計を検証。親の自己点検。独立審査・実機試し刷り・入稿承認は未実施。'
 target['freshness_status']='保存済みの局所修正版。標準renderer全冊再生成の保証ではない。';target['table_revision']={'date':'2026-10-28','columns':proof['columns'],'dash':'ー','manifest':str((B/'manifest.json').relative_to(R))}
v=copy.deepcopy(base['index']);v['date']='2026-10-28';photo=v['documents']['admissions'];update(photo,'admissions-photo')
for p in photo['print_outputs']:
 p.update(info('admissions-photo-old-cover-'+p['paper']));p['cover_note']='旧表紙の配布版を保持し、学費表だけを5列・ー表記へ更新。'
photo['previews']=[pv(preview['admissions-photo']) if x['id'].endswith('page-06') else x for x in photo['previews']]
plain=next(x for x in v['production_targets'] if x['work_id']=='ADM-JP-PLAIN-2027');update(plain,'admissions-plain');plain['status']='R05・設備費更新版・学費表5列／ー表記統一・確認用'
for p in plain['print_outputs']:p.update(info('admissions-plain-'+p['paper']))
plain['previews']=[pv(preview['admissions-plain']) if x['id'].endswith('page-06') else x for x in plain['previews']]
archive=B/'output/print-pdfs-admissions-five-columns-20261028.zip';mapping={'admissions-A3.pdf':'admissions-photo-old-cover-A3','admissions-A4.pdf':'admissions-photo-old-cover-A4'}
with zipfile.ZipFile(R/base['index']['print_bundle']) as old,zipfile.ZipFile(archive,'w') as new:
 for entry in old.infolist():new.writestr(copy.copy(entry),(R/outputs[mapping[entry.filename]]['file']).read_bytes() if entry.filename in mapping else old.read(entry.filename))
with zipfile.ZipFile(R/base['index']['print_bundle']) as old,zipfile.ZipFile(archive) as new:
 assert old.namelist()==new.namelist()
 for name in old.namelist():assert new.read(name)==((R/outputs[mapping[name]]['file']).read_bytes() if name in mapping else old.read(name))
v['previous_print_bundle']={'file':base['index']['print_bundle'],'sha256':base['index']['bundle_sha256']};v['print_bundle']=str(archive.relative_to(R));v['bundle_sha256']=sha(archive)
for key in ['brochure','flyer']:assert v['documents'][key]==base['index']['documents'][key]
for a,b in zip(base['index']['production_targets'],v['production_targets']):
 if a['work_id']!='ADM-JP-PLAIN-2027':assert a==b
(R/'downloads/latest-materials.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
manifest={'date':'2026-10-28','source_commit':base['head'],'outputs':[dict(o,registered=info(o['label'])) for o in proof['outputs']],'bundle':{'file':str(archive.relative_to(R)),'sha256':sha(archive),'changed_entries':list(mapping),'unchanged_entries':['brochure-A3.pdf','brochure-A4.pdf','flyer-A4.pdf','PRINTING.txt']},'verification':'verification.json','release':False}
(B/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');refs=[{'id':a['id'],'revision':a['revision']} for a in registered.values()];save(prefix+'manifest',B/'manifest.json','text',refs);save(prefix+'verification',B/'verification.json','text',refs)
