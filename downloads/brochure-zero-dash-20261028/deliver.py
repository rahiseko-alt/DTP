from pathlib import Path
import json,hashlib,subprocess,shutil,copy,zipfile
B=Path(__file__).resolve().parent;R=B.parents[1];old=R/'downloads/brochure-fees-five-columns-20261028/delivery-files.json';previous=json.loads(old.read_text());m=json.loads((B/'manifest.json').read_text());targets={x['label']:x for x in previous['files']};files=[]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for o in m['outputs']:
 a=o['registered'];receipt=json.loads(subprocess.check_output(['node','--import','tsx','system/scripts/assets.ts','get','--document',a['document'],'--id',a['asset_id'],'--saved'],cwd=R,text=True));source=R/receipt['path'];assert sha(source)==a['sha256']
 target=Path(targets[o['label']]['file'].replace('_5列修正版.pdf','_5列修正版_ゼロ表記統一.pdf'));shutil.copyfile(source,target);assert sha(target)==a['sha256'];files.append({'label':o['label'],'file':str(target),'sha256':sha(target),'get_receipt':receipt});print(o['label'],'delivered',flush=True)
archive=Path(previous['zip'].replace('_5列修正版.zip','_5列修正版_ゼロ表記統一.zip'));mapping={Path(targets[x['label']]['file']).name:Path(x['file']) for x in files}
with zipfile.ZipFile(previous['zip']) as oldzip,zipfile.ZipFile(archive,'w') as newzip:
 for entry in oldzip.infolist():
  item=copy.copy(entry)
  if entry.filename in mapping:item.filename=mapping[entry.filename].name;payload=mapping[entry.filename].read_bytes()
  else:payload=oldzip.read(entry.filename)
  newzip.writestr(item,payload)
with zipfile.ZipFile(previous['zip']) as oldzip,zipfile.ZipFile(archive) as newzip:
 assert len(oldzip.namelist())==len(newzip.namelist())==8
 for name in oldzip.namelist():
  if name in mapping:assert newzip.read(mapping[name].name)==mapping[name].read_bytes()
  else:assert newzip.read(name)==oldzip.read(name)
(B/'delivery-files.json').write_text(json.dumps({'files':files,'zip':str(archive),'zip_sha256':sha(archive)},ensure_ascii=False,indent=2)+'\n')
