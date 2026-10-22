"""Register this fixed adapter's outputs, reusing unchanged registered revisions."""
from pathlib import Path
import subprocess, json, hashlib

B = Path(__file__).resolve().parent
ROOT = B.parents[1]
document = 'prospectus-isen-trial-2028'
catalog = ROOT / f'books/{document}/parts/catalog.yaml'
source_sha = '62aa8e4415e5e6aa4523e1c14d024d8d45112d81dc92ce8db16db7718066f880'
items = [('jp-isen-reading-pdf', 'output/医専日本人版_16P_閲覧用.pdf', 'pdf'),
         ('jp-isen-print-a3', 'output/医専日本人版_A3_印刷用.pdf', 'pdf'),
         ('jp-isen-print-a4', 'output/医専日本人版_A4_印刷用.pdf', 'pdf'),
         ('jp-isen-master-pdf', 'output/医専日本人版_16P_確認用.pdf', 'pdf'),
         ('jp-isen-assembly-proof', 'reviews/assembly-proof.json', 'text')]
items += [(f'jp-isen-overview-{n:02}', f'output/overview-{n:02}.jpg', 'image') for n in (1, 5, 9, 13)]
records = []
for aid, rel, media in items:
    p = B / rel
    digest = hashlib.sha256(p.read_bytes()).hexdigest()
    cat = json.loads(catalog.read_text())
    prior = next((a for a in cat['assets'] if a['id'] == aid and a['revision'] == digest), None)
    if prior is not None and cat['current'].get(aid) == digest:
        value = {'asset': prior}
        reused = True
    else:
        args = ['node', '--import', 'tsx', 'system/scripts/assets.ts', 'register',
                '--document', document, '--id', aid, '--variant', 'japanese-people-edition',
                '--role', 'support', '--media', media, '--source', str(p), '--sha256', digest,
                '--confirmation', 'verified', '--built-from', json.dumps([{'id': 'jp-isen-saved-source16', 'revision': source_sha}])]
        args += ['--save-reason', 'Preserved review edition from the fixed adapter; current renderer input freshness is not asserted.']
        value = json.loads(subprocess.check_output(args, cwd=ROOT, text=True))
        reused = False
    records.append({'id': aid, 'registration': value, 'reused_unchanged': reused})
    print(aid, 'reused' if reused else 'registered', flush=True)
(B / 'reviews/asset-registration.json').write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n')
