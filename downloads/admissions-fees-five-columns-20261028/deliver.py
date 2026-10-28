from pathlib import Path
import json,hashlib,subprocess,shutil,copy,zipfile
B=Path(__file__).resolve().parent;R=B.parents[1];m=json.loads((B/'manifest.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();dest=Path('/workspace/設備費更新版');files=[]
names={'admissions-photo':'募集要項_写真入り_ページ順_設備費更新版','admissions-photo-old-cover-A3':'募集要項_写真入り_旧表紙_A3印刷用_設備費更新版','admissions-photo-old-cover-A4':'募集要項_写真入り_旧表紙_A4印刷用_設備費更新版','admissions-plain':'募集要項_文字のみ_ページ順_設備費更新版','admissions-plain-A3':'募集要項_文字のみ_A3印刷用_設備費更新版'}
for o in m['outputs']:
 a=o['registered'];receipt=json.loads(subprocess.check_output(['node','--import','tsx','system/scripts/assets.ts','get','--document',a['document'],'--id',a['asset_id'],'--saved'],cwd=R,text=True));source=R/receipt['path'];assert sha(source)==a['sha256'];target=dest/(names[o['label']]+'_5列修正版_ゼロ表記統一.pdf');shutil.copyfile(source,target);assert sha(target)==a['sha256'];files.append({'label':o['label'],'file':str(target),'sha256':sha(target),'get_receipt':receipt});print(o['label'],'delivered',flush=True)
previous=json.loads((R/'downloads/brochure-zero-dash-20261028/delivery-files.json').read_text());archive=dest/'設備費更新版_配布用PDF一式_パンフレット募集要項5列統一.zip';mapping={names[x['label']]+'.pdf':Path(x['file']) for x in files}
with zipfile.ZipFile(previous['zip']) as old,zipfile.ZipFile(archive,'w') as new:
 for entry in old.infolist():
  info=copy.copy(entry)
  if entry.filename in mapping:info.filename=mapping[entry.filename].name;payload=mapping[entry.filename].read_bytes()
  else:payload=old.read(entry.filename)
  new.writestr(info,payload)
with zipfile.ZipFile(previous['zip']) as old,zipfile.ZipFile(archive) as new:
 assert len(old.namelist())==len(new.namelist())==8
 for name in old.namelist():assert new.read(mapping[name].name if name in mapping else name)==(mapping[name].read_bytes() if name in mapping else old.read(name))
(B/'delivery-files.json').write_text(json.dumps({'files':files,'zip':str(archive),'zip_sha256':sha(archive),'brochure_pdfs':'same bytes as preceding brochure zero-dash delivery'},ensure_ascii=False,indent=2)+'\n')
