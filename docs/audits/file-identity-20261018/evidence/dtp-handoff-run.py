import subprocess,json,pathlib,hashlib,shutil,os
root=pathlib.Path('/tmp/dtp-handoff-smoke'); report=[]
def run(label,args,cwd=root):
 p=subprocess.run(args,cwd=cwd,text=True,capture_output=True); report.append({'label':label,'exit':p.returncode,'stdout':p.stdout[-1400:],'stderr':p.stderr[-1800:]}); return p
base=['node','--import','tsx','system/scripts/assets.ts']
source=root/'probe.txt'; source.write_text('interrupted registration probe\n'); sha=hashlib.sha256(source.read_bytes()).hexdigest()
args=['register','--document','oc-approved-20261017','--id','interrupted-probe','--variant','real-photo-rebuild','--role','support','--media','text','--source',str(source),'--sha256',sha,'--confirmation','verified']
run('kill-after-target-publish',['node','--import','./kill-after-publish.mjs','--import','tsx','system/scripts/assets.ts']+args)
lock=root/'.cache/asset-write.lock'; report.append({'label':'journal-and-published-file','journal':(lock/'owner.json').exists(),'target':list(map(str,root.glob('books/**/interrupted-probe.txt')))})
run('resolve-blocked',base+['resolve','--name','医専チラシ'])
cat=root/'books/oc-approved-20261017/parts/catalog.yaml'; catsha=hashlib.sha256(cat.read_bytes()).hexdigest()
run('recover-dead-pid',base+['recover','--catalog-sha256',catsha]); run('resolve-after-recover',base+['resolve','--name','医専チラシ'])
run('kill-before-owner-json',['node','--import','./kill-before-journal.mjs','--import','tsx','system/scripts/assets.ts']+args)
run('recover-no-journal',base+['recover','--catalog-sha256',catsha]); run('resolve-no-journal',base+['resolve','--name','医専チラシ'])
shutil.rmtree(lock)
pathlib.Path('/tmp/dtp-handoff-lock-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps(report,ensure_ascii=False,indent=2))
