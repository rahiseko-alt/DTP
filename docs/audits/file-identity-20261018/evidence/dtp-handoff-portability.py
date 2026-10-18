import subprocess,json,pathlib,hashlib,shutil
root=pathlib.Path('/tmp/dtp-handoff-smoke'); output=pathlib.Path('/tmp/dtp-handoff-render'); receipt=next((root/'.cache/asset-render-receipts').glob('*.json')); source=output/'page-1.png'; sha=hashlib.sha256(source.read_bytes()).hexdigest(); results=[]
def run(label,r=root,s=source,rec=None):
 args=['node','--import','tsx','system/scripts/assets.ts','register','--document','oc-approved-20261017','--id','handoff-probe','--variant','real-photo-rebuild','--role','preview','--media','image','--source',str(s),'--sha256',sha,'--confirmation','verified','--build-snapshot',rec or str(receipt.relative_to(root)),'--dry-run']
 p=subprocess.run(args,cwd=r,text=True,capture_output=True); results.append({'label':label,'exit':p.returncode,'stdout':p.stdout[-500:],'stderr':p.stderr[-1000:]})
run('baseline-same-path')
moved=pathlib.Path('/tmp/dtp-handoff-moved'); shutil.copytree(output,moved)
run('copied-output-new-path',s=moved/'page-1.png')
html=root/'.cache/asset-rebuild/flyer.html'; saved=html.read_bytes(); html.unlink(); run('cache-html-missing'); html.write_bytes(saved)
other=pathlib.Path('/tmp/dtp-handoff-other-checkout'); shutil.copytree(root,other,ignore=shutil.ignore_patterns('node_modules')); (other/'node_modules').symlink_to('/workspace/DTP-asset-identity/node_modules',target_is_directory=True)
run('other-checkout-same-output',r=other)
run('other-checkout-moved-output',r=other,s=moved/'page-1.png')
# Retained output includes build-inputs.json; simulate losing checkout cache, keeping output.
shutil.rmtree(other/'.cache'); (other/'.cache').mkdir(); shutil.copy2(output/'build-inputs.json',other/'.cache/retained-receipt.json'); run('retained-output-receipt-without-html-cache',r=other,rec='.cache/retained-receipt.json')
pathlib.Path('/tmp/dtp-handoff-portability-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)); print(json.dumps(results,ensure_ascii=False,indent=2))
