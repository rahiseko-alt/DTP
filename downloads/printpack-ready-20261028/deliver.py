from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,hashlib,subprocess,shutil
B=Path(__file__).resolve().parent;R=B.parents[1];m=json.load(open(B/'manifest.json'));dest=Path('/workspace/プリントパック入稿データ');dest.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
names={'brochure':'専門学校パンフレット_A4_16P_両面カラー_中綴じ左綴じ_入稿用.pdf','flyer':'チラシ_A4_両面カラー_表パンフレットQR_裏OC_入稿用.pdf'}
def get(item):
 label,a=item;r=json.loads(subprocess.check_output(['node','--import','tsx','system/scripts/assets.ts','get','--document',a['document'],'--id',a['asset_id'],'--role','support','--saved'],cwd=R,text=True));source=R/r['path'];assert sha(source)==a['sha256'];p=dest/names[label];shutil.copyfile(source,p);p.chmod(0o644);assert sha(p)==a['sha256'];return {'label':label,'file':str(p),'sha256':sha(p),'bytes':p.stat().st_size,'get_receipt':r}
files=list(ThreadPoolExecutor(max_workers=2).map(get,m['outputs'].items()));shutil.copyfile(B/'入稿メモ.txt',dest/'入稿メモ.txt');(B/'delivery-files.json').write_text(json.dumps({'files':files,'memo':str(dest/'入稿メモ.txt'),'orders_placed':False,'uploads_performed':False},ensure_ascii=False,indent=2)+'\n');print([(x['label'],x['bytes']) for x in files],flush=True)
