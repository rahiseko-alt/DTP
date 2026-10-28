"""Register table-only revisions; keep all historical revisions and archived revisions."""
from pathlib import Path
import copy,hashlib,json,subprocess,zipfile
B=Path(__file__).resolve().parent;R=B.parents[1];doc='admissions-guide-2027'
proof=json.loads((B/'build-proof.json').read_text());verification=json.loads((B/'verification.json').read_text());assert verification['verified']
base=json.loads((B/'baseline.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
records=[];registered={};preview={};prefix='admissions-annual-20261028-'
def save(aid,path,media,refs):
 h=sha(path);cat=json.loads((R/f'books/{doc}/parts/catalog.yaml').read_text())
 a=next((a for a in cat['assets'] if a['id']==aid and a['revision']==h),None)
 if a is None:
  cmd=['node','--import','tsx','system/scripts/assets.ts','register','--document',doc,'--id',aid,'--variant','approved-annual-table-20261028','--role','support','--media',media,'--source',str(path),'--sha256',h,'--confirmation','verified','--built-from',json.dumps(refs),'--save-reason','User instruction 2026-10-28: make admissions fee page match approved annual brochure table. Three columns: item,year1,year2. Separate miscellaneous and annual facility fee rows, annual tuition780000, expenses50000, facility50000; first year980000, second880000, two years1860000. Exact note:上記金額には検定料2万円は含みません。 No new allocation/deadline/refund changes. Only reading page6 fee table and note changed; outside pixels/native glyphs/fonts/positions/all original image streams/covers/forms/blank backs/QR/imposition preserved. Each current photo/plain PDF retained as source. Saved composition, not renderer freshness or release certification.']
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
 target['previous_layout_edition']={k:target[k] for k in ['asset_id','file','sha256','bytes','download_file'] if k in target};target.update(info(label));target['variant']='approved-annual-table-20261028'
 target['version_policy']='2026-10-28：承認済みパンフレットと同じ費目／1年次／2年次の年額表へ。入学金100,000円／ー、授業料各780,000円、諸経費・施設設備費各50,000円、年間980,000円／880,000円、2年間1,860,000円。注記は「上記金額には検定料2万円は含みません。」。表と注記以外、納付期限・返還・画像・表紙・願書・白紙裏・QR・面付けは保持。旧版を残す。'
 target['review_status']='5PDF・84P/面の表・注記外150dpi画素、文字/書体/位置と全元画像stream一致。年額の内訳・合計・指定注記・ーを検証。変更頁を拡大目視。親の自己点検。実機試し刷り・入稿承認は未実施。'
 target['freshness_status']='保存済みの局所修正版。標準renderer全冊再生成の保証ではない。';target['table_revision']={'date':'2026-10-28','columns':proof['columns'],'dash':'ー','manifest':str((B/'manifest.json').relative_to(R))}
v=copy.deepcopy(base['index']);v['date']='2026-10-28';photo=v['documents']['admissions'];update(photo,'admissions-photo')
for p in photo['print_outputs']:
 p.update(info('admissions-photo-old-cover-'+p['paper']));p['cover_note']='旧表紙の配布版を保持し、学費表だけを承認済み年額表へ更新。'
photo['previews']=[pv(preview['admissions-photo']) if x['id'].endswith('page-06') else x for x in photo['previews']]
plain=next(x for x in v['production_targets'] if x['work_id']=='ADM-JP-PLAIN-2027');update(plain,'admissions-plain');plain['status']='R05・設備費更新版・承認済み年額表・指定注記・確認用'
for p in plain['print_outputs']:p.update(info('admissions-plain-'+p['paper']))
plain['previews']=[pv(preview['admissions-plain']) if x['id'].endswith('page-06') else x for x in plain['previews']]
archive=B/'output/print-pdfs-admissions-annual-20261028.zip';mapping={'admissions-A3.pdf':'admissions-photo-old-cover-A3','admissions-A4.pdf':'admissions-photo-old-cover-A4'}
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
