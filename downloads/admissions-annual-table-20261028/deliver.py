from pathlib import Path
import json,hashlib,subprocess,shutil,copy,zipfile
B=Path(__file__).resolve().parent;R=B.parents[1];m=json.loads((B/'manifest.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();dest=Path('/workspace/設備費更新版');files=[]
names={'admissions-photo':'募集要項_写真入り_ページ順_設備費更新版','admissions-photo-old-cover-A3':'募集要項_写真入り_旧表紙_A3印刷用_設備費更新版','admissions-photo-old-cover-A4':'募集要項_写真入り_旧表紙_A4印刷用_設備費更新版','admissions-plain':'募集要項_文字のみ_ページ順_設備費更新版','admissions-plain-A3':'募集要項_文字のみ_A3印刷用_設備費更新版'}
for o in m['outputs']:
 a=o['registered'];receipt=json.loads(subprocess.check_output(['node','--import','tsx','system/scripts/assets.ts','get','--document',a['document'],'--id',a['asset_id'],'--saved'],cwd=R,text=True));source=R/receipt['path'];assert sha(source)==a['sha256'];target=dest/(names[o['label']]+'_年額表改訂版.pdf');shutil.copyfile(source,target);assert sha(target)==a['sha256'];files.append({'label':o['label'],'file':str(target),'sha256':sha(target),'get_receipt':receipt});print(o['label'],'delivered',flush=True)
previous=json.loads((R/'downloads/brochure-remove-hours-20261028/delivery-files.json').read_text());archive=dest/'設備費更新版_配布用PDF一式_募集要項年額表改訂_パンフレット授業時間欄削除版.zip';mapping={}
with zipfile.ZipFile(previous['zip']) as old,zipfile.ZipFile(archive,'w') as new:
 for entry in old.infolist():
  match=next((x for x in files if entry.filename.startswith(names[x['label']]+'_')),None);info=copy.copy(entry)
  if match:target=Path(match['file']);mapping[entry.filename]=target;info.filename=target.name;payload=target.read_bytes()
  else:payload=old.read(entry.filename)
  new.writestr(info,payload)
assert len(mapping)==5,mapping
with zipfile.ZipFile(previous['zip']) as old,zipfile.ZipFile(archive) as new:
 assert len(old.namelist())==len(new.namelist())==8
 for name in old.namelist():assert new.read(mapping[name].name if name in mapping else name)==(mapping[name].read_bytes() if name in mapping else old.read(name))
(B/'delivery-files.json').write_text(json.dumps({'files':files,'zip':str(archive),'zip_sha256':sha(archive),'brochure_pdfs':'three preceding class-hours-removed PDFs byte-identical','changed_entries':list(mapping)},ensure_ascii=False,indent=2)+'\n')
