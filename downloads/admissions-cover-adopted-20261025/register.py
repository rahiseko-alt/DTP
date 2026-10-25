"""Save the three verified revisions and update their download selectors."""
from pathlib import Path
import hashlib,json,subprocess,copy
B=Path(__file__).resolve().parent;R=B.parents[1]
manifest=json.loads((B/'manifest.json').read_text())
assert json.loads((B/'verification.json').read_text())['verified']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
records=[]
def save(aid,path,media,refs):
 h=sha(path);cat=json.loads((R/'books/admissions-guide-2027/parts/catalog.yaml').read_text())
 prior=next((a for a in cat['assets'] if a['id']==aid and a['revision']==h and cat['current'].get(aid)==h),None)
 if prior:value={'asset':prior}
 else:
  value=json.loads(subprocess.check_output(['node','--import','tsx','system/scripts/assets.ts','register','--document','admissions-guide-2027','--variant','navy-cover-adopted-20261025','--id',aid,'--role','support','--media',media,'--source',str(path),'--sha256',h,'--confirmation','verified','--built-from',json.dumps(refs),'--save-reason','2026-10-25 user GO: replace only the cover in photo reading / plain R04 reading / plain R04 A3 saddle PDFs with the exact approved navy cover, without the year underline. Saved composition; bodies and back covers unchanged, all 60 faces compared. Not a standard-renderer rebuild or print-release certification.'],cwd=R,text=True))
 records.append({'id':aid,'registration':value})
 (B/'registration.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
 print(aid,flush=True)
 return {'id':aid,'revision':h}
trial=R/'downloads/admissions-cover-trial-20261025-02'
html=save('navy-cover-2027-html',trial/'cover.html','text',[])
cover=save('navy-cover-2027-pdf',R/manifest['cover_pdf'],'pdf',[html])
builder=save('navy-cover-adoption-builder',B/'build.py','text',[])
outputs={}
for out in manifest['outputs']:
 parent={'id':out['source']['id'],'revision':out['source']['revision']}
 refs=[parent,cover,builder]
 if out['kind']=='print-a3':refs.append(outputs['plain'])
 outputs[out['kind']]=save(out['asset_id'],R/out['file'],'pdf',refs)
preview_refs={}
for name in ['plain-cover','photo-back-cover','plain-back-cover','photo-overview-01','plain-overview-01']:
 kind='photo' if name.startswith('photo') else 'plain'
 ext='jpg' if 'overview' in name else 'png'
 preview_refs[name]=save('navy-'+name,B/f'previews/{name}.{ext}','image',[outputs[kind]])
save('navy-cover-adoption-manifest',B/'manifest.json','text',list(outputs.values()))
save('navy-cover-adoption-verification',B/'verification.json','text',list(outputs.values()))
cat=json.loads((R/'books/admissions-guide-2027/parts/catalog.yaml').read_text())
def asset(ref):return next(a for a in cat['assets'] if a['id']==ref['id'] and a['revision']==ref['revision'])
def update_output(target,out):
 a=asset(outputs[out['kind']])
 target.update({'asset_id':a['id'],'file':a['file'],'sha256':a['sha256'],'bytes':a['size'],'download_file':out['file']})
def preview(name):
 a=asset(preview_refs[name]);return {'id':a['id'],'file':a['file'],'sha256':a['sha256']}
p=R/'downloads/latest-materials.json';v=json.loads(p.read_text());before=copy.deepcopy(v)
docs=v['documents'].values() if isinstance(v['documents'],dict) else v['documents']
photo=next(x for x in docs if x.get('document')=='admissions-guide-2027')
photo.setdefault('previous_cover_edition',{k:photo[k] for k in ['asset_id','file','sha256','bytes','download_file']})
update_output(photo,manifest['outputs'][0])
photo['variant']='navy-cover-adopted-20261025'
photo['version_policy']='承認された濃紺・金アクセント・白明朝・年度下線なしの表紙だけを差し替え。本文2〜24P・裏表紙・写真は元の写真入り版のまま。旧版は保持。'
photo['display_name']='募集要項_写真入り版_日本人向け_2027年度_24P_新表紙'
photo['previews']=[preview('plain-cover'),preview('photo-back-cover'),preview('photo-overview-01')]
photo['review_status']='全24Pを比較し、2〜24Pの画素・文字・書体・位置・画像ストリームが元版と一致。親が全ページ/見開きを目視。独立審査・実物試し刷り未実施。'
plain=next(x for x in v['production_targets'] if x.get('work_id')=='ADM-JP-PLAIN-2027')
plain.setdefault('previous_edition',{k:plain[k] for k in ['variant','asset_id','file','sha256','bytes','download_file','approval','archive_directory']})
if 'previous_a4_reduced_proof' not in plain:
 plain['previous_a4_reduced_proof']=copy.deepcopy(next(x for x in plain['print_outputs'] if x['paper']=='A4'))
plain['previous_a4_reduced_proof']['status']='旧R03の縮小確認用。今回の新表紙は未反映・現行印刷用として案内しない。'
update_output(plain,manifest['outputs'][1])
plain.update({'variant':'navy-cover-adopted-20261025','status':'確定・ユーザー採用済み（R04・表紙のみ改訂・2026-10-25）','archive_directory':str(B.relative_to(R))})
plain['version_policy']='確定R03の1P表紙のみ、承認済み濃紺・金アクセント・白明朝・年度下線なしの表紙へ差し替え。本文2〜24Pと裏表紙、先の配色修正、願書の白紙裏面を保持。旧R03/R02/R01と写真入り旧版は履歴として保持。'
plain['review_status']='全60P/面を比較。文字のみ版2〜24Pの画素/ネイティブ文字/書体/位置/画像がR03と一致。A3は初面右の表紙以外が一致。QRと全12面の左右ページ順を検証し、親が全ページ/見開き/印刷面を目視。独立審査・実物試し刷り未実施。'
plain['previews']=[preview('plain-cover'),preview('plain-back-cover'),preview('plain-overview-01')]
printout=next(x for x in plain['print_outputs'] if x['paper']=='A3')
update_output(printout,manifest['outputs'][2]);plain['print_outputs']=[printout]
approval={'date':'2026-10-25','edition':'R04（文字のみ版）/写真入り表紙改訂R01','manifest':str((B/'manifest.json').relative_to(R)),'cover_sha256':manifest['cover_sha256'],'statement':manifest['approval']}
plain['approval']=approval;photo['cover_approval']=approval
v['date']='2026-10-25'
# No non-admissions document, bundle, or excluded variant may change.
for key in before:
 if key not in ['documents','production_targets','date']:assert before[key]==v[key],key
for key,x in before['documents'].items():
 if x.get('document')!='admissions-guide-2027':assert x==v['documents'][key]
for x,y in zip(before['production_targets'],v['production_targets']):
 if x.get('work_id')!='ADM-JP-PLAIN-2027':assert x==y
p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
print('Three PDFs saved and download selectors updated; old PDFs retained')
