"""Retrieve registered saved PDFs and deliver Japanese names with byte-verified bundle."""
from pathlib import Path
import copy,hashlib,json,shutil,subprocess,zipfile
B=Path(__file__).resolve().parent;R=B.parents[1];proof=json.loads((B/'build-proof.json').read_text());manifest=json.loads((B/'manifest.json').read_text());dest=Path('/workspace/設備費更新版');dest.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();records=[];files={}
from concurrent.futures import ThreadPoolExecutor
def retrieve(out):
 a=out['registered'];r=json.loads(subprocess.check_output(['node','--import','tsx','system/scripts/assets.ts','get','--document',a['document'],'--id',a['asset_id'],'--role','support','--saved'],cwd=R,text=True));assert sha(R/r['path'])==a['sha256'];kind={'brochure-jp-r13':'ページ順','brochure-jp-r13-master':'制作マスター','brochure-jp-r13-A3':'A3印刷用','brochure-jp-r13-A4':'A4印刷用'}[out['label']];p=dest/f'医専パンフレット_日本人向け_R13_{kind}_設備費更新版_カリキュラム資格注記追加版.pdf';shutil.copyfile(R/r['path'],p);assert sha(p)==a['sha256'];return kind,p,{'label':out['label'],'file':str(p),'sha256':sha(p),'get_receipt':r}
for kind,p,record in ThreadPoolExecutor(max_workers=4).map(retrieve,manifest['outputs']):files[kind]=p;records.append(record)

old_delivery=json.loads((R/'downloads/admissions-annual-table-20261028/delivery-files.json').read_text());archive=dest/'設備費更新版_配布用PDF一式_カリキュラム資格注記追加版.zip';mapping={}
with zipfile.ZipFile(old_delivery['zip']) as old,zipfile.ZipFile(archive,'w') as new:
 for entry in old.infolist():
  kind=next((k for k in ['ページ順','A3印刷用','A4印刷用'] if 'パンフレット' in entry.filename and k in entry.filename),None)
  data=files[kind].read_bytes() if kind else old.read(entry.filename);new.writestr(copy.copy(entry),data)
  if kind:mapping[entry.filename]=kind
assert len(mapping)==3,mapping
with zipfile.ZipFile(old_delivery['zip']) as old,zipfile.ZipFile(archive) as new:
 assert old.namelist()==new.namelist()
 for name in old.namelist():assert new.read(name)==(files[mapping[name]].read_bytes() if name in mapping else old.read(name))
(B/'delivery-files.json').write_text(json.dumps({'files':records,'zip':str(archive),'zip_sha256':sha(archive),'changed_entries':mapping,'other_entries_byte_identical':True},ensure_ascii=False,indent=2)+'\n');print(json.dumps({'files':[x['file'] for x in records],'zip':str(archive)},ensure_ascii=False),flush=True)
