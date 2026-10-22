"""Register the fixed R03 review edition without modifying earlier editions."""
from pathlib import Path
import hashlib, json, subprocess

B = Path(__file__).resolve().parent
R = B.parents[1]
sources = json.loads((B / 'reviews/photo-input-receipts.json').read_text())
manifest = json.loads((B / 'reviews/edited-photo-manifest.json').read_text())
records = []
reason = 'Saved soft-photo R03 review edition; fixed identity verified, current standard-render freshness not asserted.'

def register(aid, file, media, refs):
    digest = hashlib.sha256(file.read_bytes()).hexdigest()
    catalog = json.loads((R / 'books/oc-approved-20261017/parts/catalog.yaml').read_text())
    existing = next((a for a in catalog['assets'] if a['id'] == aid and a['revision'] == digest), None)
    if existing:
        assert catalog['current'][aid] == digest and existing['saved'] and existing['role'] == 'support'
        subprocess.check_output(['node', '--import', 'tsx', 'system/scripts/assets.ts', 'get', '--document', 'oc-approved-20261017', '--id', aid, '--saved'], cwd=R, text=True)
        result = {'asset': existing}
    else:
        result = json.loads(subprocess.check_output([
            'node', '--import', 'tsx', 'system/scripts/assets.ts', 'register',
            '--document', 'oc-approved-20261017', '--id', aid,
            '--variant', 'original-art-soft-photo-r3', '--role', 'support',
            '--media', media, '--source', str(file), '--sha256', digest,
            '--confirmation', 'verified', '--built-from', json.dumps(refs),
            '--save-reason', reason], cwd=R, text=True))
    records.append({'id': aid, 'registration': result})
    (B / 'reviews/asset-registration.json').write_text(json.dumps(records, ensure_ascii=False, indent=2) + '\n')
    print(aid, flush=True)
    return {'id': aid, 'revision': digest}

def source_ref(key):
    a = sources[key]['asset']
    return {'id': a['id'], 'revision': a['revision']}

edited = {}
for slot, key in [('front-hero', 'hero'), ('front-class', 'class'), ('back-ai', 'ai'), ('back-business', 'business')]:
    item = manifest[slot]
    assert item['mode'] == 'soft-edit'
    refs = [source_ref(key)]
    if key in ['class', 'business']:
        refs.append(edited['hero'])  # Actual second image input, used for edit strength.
    edited[key] = register('ocjp3-edit-' + key, R / item['file'], 'image', refs)

underlay = {'id': 'latest-original-oc-pdf', 'revision': '2c0bd3b6d91449666adf9ac73091e10f7cb37831384ebe807d2ff6117cd264d1'}
front_refs = [underlay, edited['hero'], edited['class'], source_ref('friends'), source_ref('consult')]
back_refs = [underlay, edited['ai'], edited['business'], source_ref('lesson'), source_ref('exchange'), source_ref('event')]
all_refs = list({(ref['id'], ref['revision']): ref for ref in front_refs + back_refs}.values())
for aid, path, media, refs in [
    ('jp-oc-soft-r3-pdf', 'output/OC黄色帯版_原本写真加工_控えめ修正版R03_2P.pdf', 'pdf', all_refs),
    ('jp-oc-soft-r3-front', 'output/page-1.png', 'image', front_refs),
    ('jp-oc-soft-r3-back', 'output/page-2.png', 'image', back_refs),
    ('jp-oc-soft-r3-proof', 'reviews/build-proof.json', 'text', all_refs),
    ('jp-oc-soft-r3-verification', 'reviews/output-verification.json', 'text', all_refs),
]:
    register(aid, B / path, media, refs)
