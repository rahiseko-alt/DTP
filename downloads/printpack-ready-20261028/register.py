from pathlib import Path
import json,hashlib,subprocess,copy
B=Path(__file__).resolve().parent;R=B.parents[1];proof=json.load(open(B/'build-proof.json'));v=json.load(open(B/'verification.json'));assert v['verified'];records=[];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();out={}
for o in proof['outputs']:
 doc=o['source']['document'];label=o['label'];prefix=f'printpack-20261028-{label}-';refs=[]
 def save(key,file,media,parents):
  aid=prefix+key;h=sha(file);cat=json.load(open(R/f'books/{doc}/parts/catalog.yaml'));a=next((x for x in cat['assets'] if x['id']==aid and x['revision']==h),None)
  if a is None:
   cmd=['node','--import','tsx','system/scripts/assets.ts','register','--document',doc,'--id',aid,'--variant','printpack-ready-20261028','--role','support','--media',media,'--source',str(file),'--sha256',h,'--confirmation','verified','--built-from',json.dumps(parents),'--save-reason','User explicitly requested upload-ready files for Printpack,operating orders themselves. A4 trim210x297mm,3mm real bleed from original edge rendering,crop marks outside bleed,CMYK Japan Color2011Coated output intent,outlined text/no live fonts,reading order16P brochure/2P flyer. Only brochure pagination/header badges corrected before print conversion;approved content/fees/notices/photos/QR preserved. Exact input receipts and processing spec retained. Print checks passed;factory upload/physical print not performed. Saved print composition,not standard-render release certification.'];a=json.loads(subprocess.check_output(cmd,cwd=R,text=True))['asset']
  records.append({'document':doc,'asset':a});(B/'registration.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n');print(aid,flush=True);return {'id':aid,'revision':h},a
 spec,_=save('spec',B/'production-spec.json','text',[]);pdf,a=save('pdf',R/o['file'],'pdf',[spec,{'id':o['source']['id'],'revision':o['source']['revision']}]);preview,pa=save('preview',B/f'previews/{label}-overview-01.jpg','image',[pdf]);save('verification',B/'verification.json','text',[pdf]);out[label]={'document':doc,'asset_id':a['id'],'file':a['file'],'sha256':a['sha256'],'bytes':a['size'],'download_file':o['file'],'retrieval_mode':'saved','pages':o['pages'],'trim_mm':[210,297],'media_mm':[230,317],'bleed_mm':3,'crop_marks':True,'color':'CMYK','pdfx_identifiers':'PDF/X-1a:2001','outlined_text':True,'manual_imposition':False,'preview':{'id':pa['id'],'file':pa['file'],'sha256':pa['sha256']}}
idx=json.load(open(R/'downloads/latest-materials.json'));before=copy.deepcopy(idx)
for label,wid in [('brochure','PAM-JP-ISEN'),('flyer','FLY-JP-OC-YELLOW')]:
 target=next(x for x in idx['production_targets'] if x['work_id']==wid);target['printpack_output']=out[label]
idx['printer_submissions']={'printer':'プリントパック','date':'2026-10-28','orders_placed':False,'uploads_performed':False,'brochure':out['brochure'],'flyer':out['flyer']}
assert idx['documents']==before['documents'];assert idx['print_bundle']==before['print_bundle']
(R/'downloads/latest-materials.json').write_text(json.dumps(idx,ensure_ascii=False,indent=2)+'\n');(B/'manifest.json').write_text(json.dumps({'outputs':out,'build_proof':'build-proof.json','verification':'verification.json','printer_upload':'user operation','main_merged':False},ensure_ascii=False,indent=2)+'\n')
