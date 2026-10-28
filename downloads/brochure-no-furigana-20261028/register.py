"""Register table-only revisions; keep all admission documents and archived revisions."""
from pathlib import Path
import copy,hashlib,json,subprocess,zipfile
B=Path(__file__).resolve().parent;R=B.parents[1];doc='prospectus-isen-trial-2028'
proof=json.loads((B/'build-proof.json').read_text());verification=json.loads((B/'verification.json').read_text());assert verification['verified']
base=json.loads((B/'baseline.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
records=[];registered={};preview={};prefix='brochure-no-ruby-20261028-'
def save(aid,path,media,refs):
 h=sha(path);cat=json.loads((R/f'books/{doc}/parts/catalog.yaml').read_text())
 a=next((a for a in cat['assets'] if a['id']==aid and a['revision']==h),None)
 if a is None:
  cmd=['node','--import','tsx','system/scripts/assets.ts','register','--document',doc,'--id',aid,'--variant','no-furigana-20261028','--role','support','--media',media,'--source',str(path),'--sha256',h,'--confirmation','verified','--built-from',json.dumps(refs),'--save-reason','User instruction 2026-10-28: unify the brochure without furigana. Remove only 153 native ruby reading glyphs on reading pages12-15 in each current PDF. Preserve all base text/fonts/glyph IDs and positions (native serialization tolerance 0.0001pt), exact pixels outside ruby glyph areas, all original image streams, annual fee table and exact approved examination-fee note, covers, AI notice, QR and imposition. Original revisions retained. Saved composition, not standard-render freshness or release certification.']
  a=json.loads(subprocess.check_output(cmd,cwd=R,text=True))['asset']
 records.append({'document':doc,'asset':a});(B/'registration.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n');print(aid,flush=True)
 return {'id':aid,'revision':h},a
plan,_=save(prefix+'source-plan',B/'ruby-source-plan.json','text',[]);builder,_=save(prefix+'builder',B/'build.py','text',[plan])
for o in proof['outputs']:
 ref,a=save(prefix+o['label'].lower(),R/o['file'],'pdf',[{'id':o['source']['id'],'revision':o['source']['revision']},builder,plan]);registered[o['label']]=a
 if o['kind']=='reading':
  for region in o['regions']:
   pn=region['reading_page'];_,pa=save(prefix+o['label'].lower()+f'-page-{pn:02}',B/f'previews/{o["label"]}-page-{pn:02}.png','image',[ref]);preview[(o['label'],pn)]=pa
  if o['label']=='brochure-jp-r13':
   for pn in [9,13]:
    _,pa=save(prefix+f'r13-overview-{pn:02}',B/f'previews/brochure-jp-r13-overview-{pn:02}.jpg','image',[ref]);preview[('overview',pn)]=pa
outputs={o['label']:o for o in proof['outputs']}
def info(label):
 a=registered[label];o=outputs[label]
 return {'document':doc,'asset_id':a['id'],'file':a['file'],'sha256':a['sha256'],'bytes':a['size'],'download_file':o['file'],'retrieval_mode':'saved'}
def pv(a):return {'id':a['id'],'file':a['file'],'sha256':a['sha256']}
def update(target,label):
 target['previous_layout_edition']={k:target[k] for k in ['asset_id','file','sha256','bytes','download_file'] if k in target};target.update(info(label));target['variant']='no-furigana-20261028'
 target['version_policy']='2026-10-28：パンフレット全体をふりがな無しへ統一。ふりがなのある12-15Pから読みだけ153字を削除し、本文の全字・書体・位置、年額表、指定注記、表紙・画像・AI注記・QR・面付けを保持。年額表と2年間合計1,860,000円・検定料別の注記は直前の承認版のまま。旧版を保持。'
 target['review_status']='7PDF・80P/面のふりがな領域外150dpi画素一致。本文の全文字/書体/グリフ一致、字位置・字号の直列化誤差0.0001pt以内、全元画像stream一致。4ページの読み153字を源HTMLと照合して削除し残存なし。親の自己点検。独立審査・実機試し刷り・入稿承認は未実施。';target['freshness_status']='保存済み局所修正版。標準renderer全冊再生成の保証ではない。';target['furigana_revision']={'date':'2026-10-28','policy':'ふりがな無し','removed_reading_glyphs':153,'manifest':str((B/'manifest.json').relative_to(R))}
def revised_previews(items,label):
 result=[];seen=set()
 for x in items:
  pn=next((p for p in range(12,16) if x['id'].endswith(f'page-{p:02}')),None)
  if pn:result.append(pv(preview[(label,pn)]));seen.add(pn)
  elif label=='brochure-jp-r13' and 'overview-09' in x['id']:result.append(pv(preview[('overview',9)]))
  elif label=='brochure-jp-r13' and 'overview-13' in x['id']:result.append(pv(preview[('overview',13)]))
  else:result.append(x)
 for pn in range(12,16):
  if pn not in seen:result.append(pv(preview[(label,pn)]))
 return result
v=copy.deepcopy(base['index']);v['date']='2026-10-28';original=v['documents']['brochure'];update(original,'brochure-original')
for p in original['print_outputs']:p.update(info('brochure-original-'+p['paper']))
original['previews']=revised_previews(original['previews'],'brochure-original');jp=next(x for x in v['production_targets'] if x['work_id']=='PAM-JP-ISEN');update(jp,'brochure-jp-r13');jp['status']='改稿13・設備費更新版・年額表改訂・ふりがな無し・確認用'
for p in jp['print_outputs']:p.update(info('brochure-jp-r13-'+p['paper']))
jp['master_output']=info('brochure-jp-r13-master');jp['previews']=revised_previews(jp['previews'],'brochure-jp-r13')
archive=B/'output/print-pdfs-brochure-no-furigana-20261028.zip';mapping={'brochure-A3.pdf':'brochure-original-A3','brochure-A4.pdf':'brochure-original-A4'}
with zipfile.ZipFile(R/base['index']['print_bundle']) as old,zipfile.ZipFile(archive,'w') as new:
 for entry in old.infolist():new.writestr(copy.copy(entry),(R/outputs[mapping[entry.filename]]['file']).read_bytes() if entry.filename in mapping else old.read(entry.filename))
with zipfile.ZipFile(R/base['index']['print_bundle']) as old,zipfile.ZipFile(archive) as new:
 assert old.namelist()==new.namelist()
 for name in old.namelist():assert new.read(name)==((R/outputs[mapping[name]]['file']).read_bytes() if name in mapping else old.read(name))
v['previous_print_bundle']={'file':base['index']['print_bundle'],'sha256':base['index']['bundle_sha256']};v['print_bundle']=str(archive.relative_to(R));v['bundle_sha256']=sha(archive)
for key in ['admissions','flyer']:assert v['documents'][key]==base['index']['documents'][key]
for a,b in zip(base['index']['production_targets'],v['production_targets']):
 if a['work_id']!='PAM-JP-ISEN':assert a==b
(R/'downloads/latest-materials.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');manifest={'date':'2026-10-28','source_commit':base['head'],'outputs':[dict(o,registered=info(o['label'])) for o in proof['outputs']],'bundle':{'file':str(archive.relative_to(R)),'sha256':sha(archive),'changed_entries':list(mapping),'unchanged_entries':['admissions-A3.pdf','admissions-A4.pdf','flyer-A4.pdf','PRINTING.txt']},'verification':'verification.json','release':False};(B/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');refs=[{'id':a['id'],'revision':a['revision']} for a in registered.values()];save(prefix+'manifest',B/'manifest.json','text',refs);save(prefix+'verification',B/'verification.json','text',refs)
