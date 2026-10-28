"""Register table-only revisions; keep all admission documents and archived revisions."""
from pathlib import Path
import copy,hashlib,json,subprocess,zipfile
B=Path(__file__).resolve().parent;R=B.parents[1];doc='prospectus-isen-trial-2028'
proof=json.loads((B/'build-proof.json').read_text());verification=json.loads((B/'verification.json').read_text());assert verification['verified']
base=json.loads((B/'baseline.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
records=[];registered={};preview={};prefix='fee-annual-approved-20261028-'
def save(aid,path,media,refs):
 h=sha(path);cat=json.loads((R/f'books/{doc}/parts/catalog.yaml').read_text())
 a=next((a for a in cat['assets'] if a['id']==aid and a['revision']==h),None)
 if a is None:
  cmd=['node','--import','tsx','system/scripts/assets.ts','register','--document',doc,'--id',aid,'--variant','approved-annual-fee-table-20261028','--role','support','--media',media,'--source',str(path),'--sha256',h,'--confirmation','verified','--built-from',json.dumps(refs),'--save-reason','User-approved exact rewrite 2026-10-28: annual table with fee item, year1, year2; admission 100000/none, annual tuition780000 each, misc50000 each, facility50000 each, totals980000/880000, grand1860000 excluding examination fee. Exact note: 上記金額には検定料2万円は含みません。 Only reading pages12/13 fee blocks changed. Original covers, images, other text, payment deadlines, AI notice and imposition preserved. Outside blocks identical 150dpi pixels and text/fonts/glyph IDs; native coordinate serialization tolerance 0.0001pt. Saved composition, not standard-render freshness or release certification.']
  a=json.loads(subprocess.check_output(cmd,cwd=R,text=True))['asset']
 records.append({'document':doc,'asset':a});(B/'registration.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n');print(aid,flush=True)
 return {'id':aid,'revision':h},a
cat=json.loads((R/f'books/{doc}/parts/catalog.yaml').read_text());facts={'id':'tuition-20261027-facts','revision':cat['current']['tuition-20261027-facts']}
display,_=save(prefix+'display-data',R/'company-data/facts/booklet.yaml','text',[facts]);renderer,_=save(prefix+'renderer',B/'render-panels.mjs','text',[facts,display]);builder,_=save(prefix+'builder',B/'build.py','text',[])
panels=[]
for pn in [12,13]:
 ref,_=save(prefix+f'panel-{pn}',B/f'panels/page{pn}.pdf','pdf',[facts,display,renderer]);panels.append(ref)
for o in proof['outputs']:
 ref,a=save(prefix+o['label'].lower(),R/o['file'],'pdf',[{'id':o['source']['id'],'revision':o['source']['revision']},*panels,builder]);registered[o['label']]=a
 for region in o['regions']:
  pn=region['pdf_page'];_,pa=save(prefix+o['label'].lower()+f'-page-{pn:02}',B/f'previews/{o["label"]}-page-{pn:02}.png','image',[ref]);preview[(o['label'],region['reading_page'])]=pa
 if o['label']=='brochure-jp-r13':
  for pn in [9,13]:
   _,pa=save(prefix+f'r13-overview-{pn:02}',B/f'previews/brochure-jp-r13-overview-{pn:02}.jpg','image',[ref]);preview[('overview',pn)]=pa
outputs={o['label']:o for o in proof['outputs']}
def info(label):
 a=registered[label];o=outputs[label]
 return {'document':doc,'asset_id':a['id'],'file':a['file'],'sha256':a['sha256'],'bytes':a['size'],'download_file':o['file'],'retrieval_mode':'saved'}
def pv(a):return {'id':a['id'],'file':a['file'],'sha256':a['sha256']}
def update(target,label):
 target['previous_layout_edition']={k:target[k] for k in ['asset_id','file','sha256','bytes','download_file'] if k in target};target.update(info(label));target['variant']='approved-annual-fee-table-20261028'
 target['version_policy']='2026-10-28：人間が承認した費目／1年次／2年次の年額表へ。入学金100,000/ー、授業料780,000円×2、諸経費50,000円×2、施設設備費50,000円×2、年間合計980,000/880,000円。2年間合計は検定料別の1,860,000円。「上記金額には検定料2万円は含みません。」を正確に掲載。12/13Pの料金ブロックのみ修正し、表紙・画像・他本文・納付条件・AI注記・面付けを保持。'
 target['review_status']='7PDF・80P/面の料金ブロック外150dpi画素とネイティブ文字/書体/グリフ一致。ネイティブ座標はPDF直列化誤差0.0001pt以内。全元画像stream一致。3列・全年額・合計・指定注記を検査。親の自己点検。独立審査・実機試し刷り・入稿承認は未実施。'
 target['freshness_status']='保存済みの局所修正版。標準renderer全冊再生成の保証ではない。';target['table_revision']={'date':'2026-10-28','columns':proof['columns'],'note':proof['note'],'manifest':str((B/'manifest.json').relative_to(R))}
v=copy.deepcopy(base['index']);v['date']='2026-10-28';original=v['documents']['brochure'];update(original,'brochure-original')
for p in original['print_outputs']:p.update(info('brochure-original-'+p['paper']))
def revised_previews(items,label):
 revised=[]
 for x in items:
  if 'overview-09' in x['id'] and label=='brochure-jp-r13':revised.append(pv(preview[('overview',9)]))
  elif 'overview-13' in x['id'] and label=='brochure-jp-r13':revised.append(pv(preview[('overview',13)]))
  elif x['id'].endswith('page-12'):revised.append(pv(preview[(label,12)]))
  elif x['id'].endswith('page-13'):revised.append(pv(preview[(label,13)]))
  else:revised.append(x)
 return revised
original['previews']=revised_previews(original['previews'],'brochure-original');jp=next(x for x in v['production_targets'] if x['work_id']=='PAM-JP-ISEN');update(jp,'brochure-jp-r13');jp['status']='改稿13・設備費更新版・承認済み年額表へ改訂・確認用'
for p in jp['print_outputs']:p.update(info('brochure-jp-r13-'+p['paper']))
jp['master_output']=info('brochure-jp-r13-master');jp['previews']=revised_previews(jp['previews'],'brochure-jp-r13')
archive=B/'output/print-pdfs-brochure-annual-20261028.zip';mapping={'brochure-A3.pdf':'brochure-original-A3','brochure-A4.pdf':'brochure-original-A4'}
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
manifest={'date':'2026-10-28','source_commit':base['head'],'outputs':[dict(o,registered=info(o['label'])) for o in proof['outputs']],'bundle':{'file':str(archive.relative_to(R)),'sha256':sha(archive),'changed_entries':list(mapping),'unchanged_entries':['admissions-A3.pdf','admissions-A4.pdf','flyer-A4.pdf','PRINTING.txt']},'verification':'verification.json','note':proof['note'],'release':False};(B/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');refs=[{'id':a['id'],'revision':a['revision']} for a in registered.values()];save(prefix+'manifest',B/'manifest.json','text',refs);save(prefix+'verification',B/'verification.json','text',refs)
