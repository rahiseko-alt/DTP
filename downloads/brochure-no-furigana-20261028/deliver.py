from pathlib import Path
import json,hashlib,subprocess,shutil,copy,zipfile
B=Path(__file__).resolve().parent;R=B.parents[1];m=json.loads((B/'manifest.json').read_text());prior=json.loads((R/'downloads/brochure-annual-table-20261028/delivery-files.json').read_text());names={x['label']:Path(x['file']) for x in prior['files']};sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();files=[]
for o in m['outputs']:
 a=o['registered'];receipt=json.loads(subprocess.check_output(['node','--import','tsx','system/scripts/assets.ts','get','--document',a['document'],'--id',a['asset_id'],'--saved'],cwd=R,text=True));source=R/receipt['path'];assert sha(source)==a['sha256'];target=Path(str(names[o['label']]).replace('_年額表改訂版.pdf','_年額表改訂版_ふりがな無し.pdf'));shutil.copyfile(source,target);assert sha(target)==a['sha256'];files.append({'label':o['label'],'file':str(target),'sha256':sha(target),'get_receipt':receipt});print(o['label'],'delivered',flush=True)
previous=json.loads((R/'downloads/brochure-annual-table-20261028/delivery-files.json').read_text());archive=Path('/workspace/設備費更新版/設備費更新版_配布用PDF一式_パンフレット年額表改訂版_ふりがな無し.zip');mapping={names[x['label']].name:Path(x['file']) for x in files}
with zipfile.ZipFile(previous['zip']) as old,zipfile.ZipFile(archive,'w') as new:
 for entry in old.infolist():
  info=copy.copy(entry)
  if entry.filename in mapping:info.filename=mapping[entry.filename].name;payload=mapping[entry.filename].read_bytes()
  else:payload=old.read(entry.filename)
  new.writestr(info,payload)
with zipfile.ZipFile(previous['zip']) as old,zipfile.ZipFile(archive) as new:
 assert len(old.namelist())==len(new.namelist())==8
 for name in old.namelist():assert new.read(mapping[name].name if name in mapping else name)==(mapping[name].read_bytes() if name in mapping else old.read(name))
(B/'delivery-files.json').write_text(json.dumps({'files':files,'zip':str(archive),'zip_sha256':sha(archive),'admissions_pdfs':'same bytes as preceding admissions five-column delivery'},ensure_ascii=False,indent=2)+'\n')
