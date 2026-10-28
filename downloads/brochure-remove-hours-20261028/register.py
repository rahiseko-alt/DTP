"""Register Japanese-audience revisions, preserving original brochure and all other materials."""
from pathlib import Path
import copy,hashlib,json,subprocess
B=Path(__file__).resolve().parent;R=B.parents[1];doc='prospectus-isen-trial-2028';prefix='no-hours-20261028-';variant='class-hours-removed-20261028'
proof=json.loads((B/'build-proof.json').read_text());verification=json.loads((B/'verification.json').read_text());assert verification['verified'];base=json.loads((B/'baseline.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();records=[];registered={};preview={}
reason='User instruction 2026-10-28: remove class-hours column from both department overview rows on PDF4/6. Reflow only these row interiors into duration and admission-capacity columns. No replacement attendance-day or annual-hours claim. Four current Japanese R13 PDFs only; preserve every pixel outside row interiors, all original native text/font/positions and image streams, current copy, cover, fee tables, no-furigana, QR, AI note and imposition. Old revisions retained. Saved composition, not release certification.'
def save(aid,path,media,refs):
 h=sha(path);cat=json.loads((R/f'books/{doc}/parts/catalog.yaml').read_text());a=next((a for a in cat['assets'] if a['id']==aid and a['revision']==h),None)
 if a is None:
  cmd=['node','--import','tsx','system/scripts/assets.ts','register','--document',doc,'--id',aid,'--variant',variant,'--role','support','--media',media,'--source',str(path),'--sha256',h,'--confirmation','verified','--built-from',json.dumps(refs),'--save-reason',reason];a=json.loads(subprocess.check_output(cmd,cwd=R,text=True))['asset']
 records.append({'document':doc,'asset':a});(B/'registration.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n');print(aid,flush=True);return {'id':aid,'revision':h},a
plan,_=save(prefix+'copy-plan',B/'patches.json','text',[]);renderer,_=save(prefix+'renderer',B/'render-overlays.mjs','text',[plan]);packet,_=save(prefix+'overlay-packet',B/'overlay-packet.pdf','pdf',[plan,renderer]);builder,_=save(prefix+'builder',B/'build.py','text',[plan,packet])
for o in proof['outputs']:
 ref,a=save(prefix+o['label'].lower(),R/o['file'],'pdf',[{'id':o['source']['id'],'revision':o['source']['revision']},builder,packet,plan]);registered[o['label']]=a
 if o['kind']=='reading':
  for pn in sorted({r['reading_page'] for r in o['regions']}):
   _,pa=save(prefix+f'page-{pn:02}',B/f'previews/{o["label"]}-page-{pn:02}.png','image',[ref]);preview[pn]=pa
  for pn in [1,5]:
   _,pa=save(prefix+f'overview-{pn:02}',B/f'previews/{o["label"]}-overview-{pn:02}.jpg','image',[ref]);preview[('overview',pn)]=pa
outputs={o['label']:o for o in proof['outputs']}
def info(label):
 a=registered[label];o=outputs[label];return {'document':doc,'asset_id':a['id'],'file':a['file'],'sha256':a['sha256'],'bytes':a['size'],'download_file':o['file'],'retrieval_mode':'saved'}
def pv(a):return {'id':a['id'],'file':a['file'],'sha256':a['sha256']}
v=copy.deepcopy(base['index']);v['date']='2026-10-28';jp=next(x for x in v['production_targets'] if x['work_id']=='PAM-JP-ISEN');jp['previous_copy_edition']={k:jp[k] for k in ['asset_id','file','sha256','bytes','download_file']};jp.update(info('brochure-jp-r13'));jp['variant']=variant;jp['status']='改稿13・設備費更新版・年額表改訂・ふりがな無し・日本人向け文面修正・授業時間欄削除版・確認用'
jp['version_policy']='2026-10-28：両学科の授業時間欄（週3日・1日100分×5限）を削除し、欄内を修業年限2年制／入学定員30名・29名の2項目へ。週5日や年間授業時間は新たに掲載しない。日本人向け文面・表紙・学費表・注記・ふりがな無し・画像・QR・面付けを保持。旧版保持。'
jp['review_status']='4PDF・48P/面の学科概要2行領域外150dpi画素一致。元の全文字/書体/位置と全画像stream一致。DOMはみ出しなし。変更2ページ拡大・全ページ/面一覧を親が自己点検。実機試し刷りと入稿承認は未実施。';jp['freshness_status']='保存済み局所修正版。標準renderer全冊再生成の保証ではない。'
for p in jp['print_outputs']:p.update(info('brochure-jp-r13-'+p['paper']))
jp['master_output']=info('brochure-jp-r13-master');jp['class_hours_removed_revision']={'date':'2026-10-28','removed':'両学科の授業時間欄','manifest':str((B/'manifest.json').relative_to(R))}
previews=[]
for x in jp['previews']:
 pn=next((n for n in [1,5] if 'overview-'+f'{n:02}' in x['id']),None);previews.append(pv(preview[('overview',pn)]) if pn else x)
previews += [pv(preview[p]) for p in sorted(k for k in preview if isinstance(k,int))];jp['previews']=previews
assert v['documents']==base['index']['documents']
for a,b in zip(base['index']['production_targets'],v['production_targets']):
 if a['work_id']!='PAM-JP-ISEN':assert a==b
assert v['print_bundle']==base['index']['print_bundle'] and v['bundle_sha256']==base['index']['bundle_sha256']
(R/'downloads/latest-materials.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');manifest={'date':'2026-10-28','source_commit':base['head'],'outputs':[dict(o,registered=info(o['label'])) for o in proof['outputs']],'preserved':['original brochure','admissions','flyer','classic print ZIP'],'verification':'verification.json','release':False};(B/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');refs=[{'id':a['id'],'revision':a['revision']} for a in registered.values()];save(prefix+'manifest',B/'manifest.json','text',refs);save(prefix+'verification',B/'verification.json','text',refs)
