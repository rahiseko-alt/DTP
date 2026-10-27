"""Register fee-only saved revisions and point distribution entries to them."""
from pathlib import Path
import copy,hashlib,json,subprocess,zipfile
B=Path(__file__).resolve().parent;R=B.parents[1]
proof=json.loads((B/'build-proof.json').read_text());verification=json.loads((B/'verification.json').read_text())
assert verification['verified'] and len(verification['outputs'])==len(proof['outputs'])
baseline=json.loads((B/'baseline.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
outputs={x['label']:x for x in proof['outputs']}
archive=B/'output/print-pdfs-fees-20261027.zip'
mapping={'brochure-A3.pdf':'brochure-original-A3','brochure-A4.pdf':'brochure-original-A4','admissions-A3.pdf':'admissions-photo-old-cover-A3','admissions-A4.pdf':'admissions-photo-old-cover-A4'}
with zipfile.ZipFile(R/baseline['index']['print_bundle']) as old,zipfile.ZipFile(archive,'w') as new:
 for info in old.infolist():new.writestr(copy.copy(info),(R/outputs[mapping[info.filename]]['file']).read_bytes() if info.filename in mapping else old.read(info.filename))
with zipfile.ZipFile(R/baseline['index']['print_bundle']) as old,zipfile.ZipFile(archive) as new:
 assert old.namelist()==new.namelist()
 for name in old.namelist():
  assert new.read(name)==((R/outputs[mapping[name]]['file']).read_bytes() if name in mapping else old.read(name))
records=[];registered={};preview_refs={}
def save(doc,aid,path,media,refs):
 h=sha(path);cat=json.loads((R/f'books/{doc}/parts/catalog.yaml').read_text())
 prior=next((a for a in cat['assets'] if a['id']==aid and a['revision']==h and cat['current'].get(aid)==h),None)
 if prior:a=prior
 else:
  v=json.loads(subprocess.check_output(['node','--import','tsx','system/scripts/assets.ts','register','--document',doc,'--id',aid,'--variant','tuition-facility-20261027','--role','support','--media',media,'--source',str(path),'--sha256',h,'--confirmation','verified','--built-from',json.dumps(refs),'--save-reason','2026-10-27 user-authorized fee-only revision: annual facility fee 50000 yen in EACH of years 1 and 2, totals 980000/880000/1860000; exam fee unchanged. Saved native PDF composition, not standard-renderer freshness or release certification. Each original edition/cover/photo/policy/page order retained.'],cwd=R,text=True));a=v['asset']
 records.append({'document':doc,'asset':a});(B/'registration.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n');print(aid,flush=True)
 return {'id':aid,'revision':h},a
for doc,group in [('prospectus-isen-trial-2028','brochure'),('admissions-guide-2027','admissions')]:
 facts,_=save(doc,'tuition-20261027-facts',R/'company-data/facts/admissions.yaml','text',[])
 renderer,_=save(doc,'tuition-20261027-panel-renderer',B/'render-panels.mjs','text',[])
 builder,_=save(doc,'tuition-20261027-builder',B/'build.py','text',[])
 panels=[]
 for name in (['annual','periods'] if group=='brochure' else ['admissions']):
  ref,_=save(doc,f'tuition-20261027-panel-{name}',B/f'panels/{name}.pdf','pdf',[facts,renderer]);panels.append(ref)
 for out in proof['outputs']:
  if out['document']!=doc:continue
  src={'id':out['source']['id'],'revision':out['source']['revision']}
  ref,a=save(doc,'tuition-20261027-'+out['label'].lower(),R/out['file'],'pdf',[src,facts,builder,*panels]);registered[out['label']]=a
  for page in sorted(out['changed_regions'],key=int):
   path=B/f'previews/{out["label"]}-page-{int(page):02}.png'
   pr,pa=save(doc,f'tuition-20261027-{out["label"].lower()}-page-{int(page):02}',path,'image',[ref]);preview_refs[(out['label'],int(page))]=pa
  if out['kind']=='reading' and out['label']=='brochure-jp-r12':
   for pn in [9,13]:
    pr,pa=save(doc,f'tuition-20261027-jp-overview-{pn:02}',B/f'previews/{out["label"]}-overview-{pn:02}.jpg','image',[ref]);preview_refs[('overview',pn)]=pa

def output_info(label):
 a=registered[label];out=outputs[label]
 return {'document':out['document'],'asset_id':a['id'],'file':a['file'],'sha256':a['sha256'],'bytes':a['size'],'download_file':out['file'],'retrieval_mode':'saved'}
def update(x,label):
 x['previous_fee_edition']={k:x[k] for k in ['asset_id','file','sha256','bytes','download_file'] if k in x}
 x.update(output_info(label));x['variant']='tuition-facility-20261027'
 x['version_policy']='2026-10-27料金改定。施設設備費は各年50,000円、年次合計980,000/880,000円、2年間1,860,000円。変更は料金欄のみ。元の表紙/写真/配色/料金以外の文章/納付期限/返還規定/ページ順を保持。旧版は別保管。'
 x['review_status']='全ページ/印刷面を150dpi比較し、料金領域外の画素・文字・書体・位置と元の全画像ストリームを保持。QR・白紙裏面・新合計を検証。親の目視、独立審査/実物試し刷り/入稿承認なし。'
 x['freshness_status']='保存済み料金改定版。既存PDFの料金領域を編集した成果物。現入力の標準renderer全冊再生成という意味ではない。'
def prints(group,papers,old=[]):
 result=[]
 for paper in papers:
  label=group+'-'+paper;x=copy.deepcopy(next((p for p in old if p['paper']==paper),{}));x.update(output_info(label))
  faces=outputs[label]['pages'];x.update(paper=paper,faces=faces,sheets=faces//2,duplex='短辺反転')
  if 'old-cover' in label:x['cover_note']='旧表紙の配布用PDFの料金のみ改定。表紙は元PDFのまま。'
  result.append(x)
 return result
def pv(a):return {'id':a['id'],'file':a['file'],'sha256':a['sha256']}
v=copy.deepcopy(baseline['index']);v['date']='2026-10-27'
original=v['documents']['brochure'];update(original,'brochure-original');original['print_outputs']=prints('brochure-original',['A3','A4'])
original['previews']=[pv(preview_refs[('brochure-original',p)]) for p in [12,13]]
photo=v['documents']['admissions'];update(photo,'admissions-photo');photo['print_outputs']=prints('admissions-photo-old-cover',['A3','A4'])
photo['previews'].append(pv(preview_refs[('admissions-photo',6)]))
for target in v['production_targets']:
 if target.get('work_id')=='PAM-JP-ISEN':
  update(target,'brochure-jp-r12');target['status']='改稿12・2026-10-27料金改定・確認用'
  target['print_outputs']=prints('brochure-jp-r12',['A3','A4'],target['print_outputs']);target['master_output']=output_info('brochure-jp-r12-master')
  for i,a in enumerate(target['previews']):
   for n in [9,13]:
    if a['id']==f'jp-isen-overview-{n:02}':target['previews'][i]=pv(preview_refs[('overview',n)])
  target['previews'] += [pv(preview_refs[('brochure-jp-r12',p)]) for p in [12,13]]
 elif target.get('work_id')=='ADM-JP-PLAIN-2027':
  update(target,'admissions-plain');target['status']='R05・2026-10-27料金改定・確認用'
  target['display_name']='募集要項_文字のみ版_日本人向け_2027年度_R05_料金改定_確認用'
  target['tags']=[('状態:確認用' if t=='状態:確定' else t) for t in target['tags']]
  target['print_outputs']=prints('admissions-plain',['A3'],target['print_outputs']);target['archive_directory']=str(B.relative_to(R))
  target['previews'].append(pv(preview_refs[('admissions-plain',6)]))
  target['fee_revision']={'date':'2026-10-27','edition':'R05','manifest':str((B/'manifest.json').relative_to(R)),'user_instruction':'PLEASE IMPLEMENT THIS PLAN: 料金改定。料金以外の変更禁止。'}
v['previous_print_bundle']={'file':baseline['index']['print_bundle'],'sha256':baseline['index']['bundle_sha256']}
v['print_bundle']=str(archive.relative_to(R));v['bundle_sha256']=sha(archive)
for key in ['excluded_variants','bundle_pdf_names']:assert v[key]==baseline['index'][key]
assert v['documents']['flyer']==baseline['index']['documents']['flyer']
for old,new in zip(baseline['index']['production_targets'],v['production_targets']):
 if old.get('work_id') not in ['PAM-JP-ISEN','ADM-JP-PLAIN-2027']:assert old==new
(R/'downloads/latest-materials.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
manifest={'date':'2026-10-27','timezone':'Asia/Tokyo','scope':'fee-only; current/distribution/in-progress editions; historical originals and discontinued variants retained','source_commit':baseline['head'],'facts_file':'company-data/facts/admissions.yaml','facts_sha256':proof['facts_sha256'],'outputs':[dict(out,registered=output_info(label)) for label,out in outputs.items()],'bundle':{'file':str(archive.relative_to(R)),'sha256':sha(archive),'replaced_entries':mapping,'unchanged_entries':['flyer-A4.pdf','PRINTING.txt']},'verification':'verification.json','independent_review':False,'physical_print_test':False,'release':False}
(B/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
for doc in ['prospectus-isen-trial-2028','admissions-guide-2027']:
 refs=[{'id':a['id'],'revision':a['revision']} for label,a in registered.items() if outputs[label]['document']==doc]
 save(doc,'tuition-20261027-manifest',B/'manifest.json','text',refs)
 save(doc,'tuition-20261027-verification',B/'verification.json','text',refs)
print('12 revised PDFs registered; four ZIP PDFs replaced; flyer/printing instructions and old originals unchanged',flush=True)
