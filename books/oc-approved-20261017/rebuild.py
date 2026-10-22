#!/usr/bin/env python3
"""Rebuild only from a verified current input set. Registered outputs are immutable."""
from pathlib import Path
import hashlib, html, json, os, re, subprocess, yaml
ROOT = Path(__file__).resolve().parents[2]
BOOK = Path(__file__).resolve().parent
snapshot = json.loads(subprocess.check_output([
    'node', '--import', 'tsx', str(ROOT/'system/scripts/assets.ts'),
    'build-inputs', '--root', str(ROOT), '--document', 'oc-approved-20261017'
], cwd=ROOT))
inputs = {item['id']: ROOT/item['path'] for item in snapshot['inputs']}
school = yaml.safe_load((ROOT/snapshot['external'][0]['path']).read_text(encoding='utf-8'))
address = school['address']
replacements = {key: school[key] for key in ('tel', 'email', 'corporation')}
replacements.update(school=school['name'], english=school['name_en'],
    address='〒'+str(address['postal_code'])+' '+''.join(str(address[k]) for k in ('prefecture','city','line1')),
    access='・'.join(school['access']) if isinstance(school['access'],list) else school['access'])
media_manifest = json.loads(inputs['support-parts-photos-map-json'].read_text(encoding='utf-8'))
entries = media_manifest['slots']
if 'access_map' in media_manifest:
    declared_map = media_manifest['access_map']
    resolved_map = json.loads(subprocess.check_output([
        'node', '--import', 'tsx', str(ROOT/'system/scripts/assets.ts'),
        'get', '--root', str(ROOT), '--document', 'oc-approved-20261017',
        '--id', declared_map['asset_id'], '--role', 'support'
    ], cwd=ROOT))
    if resolved_map['asset']['sha256'] != declared_map['sha256']:
        raise SystemExit('Access map differs from the registered media manifest')
    replacements['access-map'] = os.path.relpath(ROOT/resolved_map['path'], BOOK/'source').replace('\\', '/')
text = inputs['layout-flyer-template'].read_text(encoding='utf-8')
for item in entries:
    replacements[item['slot']] = os.path.relpath(inputs[item['slot']], BOOK/'source').replace('\\', '/')
    pos = item.get('crop', {}).get('object_position', '50% 50%')
    text = text.replace('src="@@'+item['slot']+'@@"', 'src="@@'+item['slot']+'@@" style="object-position:'+html.escape(pos,quote=True)+'"')
copy = json.loads(inputs['editable-copy'].read_text(encoding='utf-8'))
for i, d in enumerate(copy.get('front', {}).get('dates', [])):
    m = re.match(r'^(.+?)[（(]([^）)]+)[）)]$', str(d).strip())
    if m:
        text = text.replace(
            f'<div class="date"><b>@@copy:front.dates.{i}@@</b><i>日</i></div>',
            f'<div class="date"><b>{html.escape(m.group(1))}</b><i>{html.escape(m.group(2))}</i></div>',
        )
def copy_value(match):
    value = copy
    for key in match.group(1).split('.'):
        value = value[int(key)] if isinstance(value,list) else value[key]
    if match.group(1).startswith('front.dates.'):
        value = re.sub(r'[（(][^）)]+[）)]', '', str(value))
    result = html.escape(str(value))
    if match.group(1) in ('front.lead', 'front.photo_copy'):
        result = result.replace('、','、<br>',1)
    return result
text = re.sub(r'@@copy:([^@]+)@@', copy_value, text)
for key, value in replacements.items():
    text = text.replace('@@'+key+'@@', html.escape(str(value),quote=True))
if '@@' in text:
    raise SystemExit('Unresolved template placeholders')
# Rebind official media through their registered current assets too.
for old, asset_id in {
    '../parts/brand/logo-horizontal.png':'support-parts-brand-logo-horizontal-png',
    '../parts/official-site-qr.png':'support-parts-official-site-qr-png',
    **{'../parts/icons/'+name+'.svg':'support-parts-icons-'+name+'-svg'
       for name in ('consult','laptop','people','school')}
}.items():
    text = text.replace(old, os.path.relpath(inputs[asset_id], BOOK/'source').replace('\\', '/'))
output = Path(os.environ.get('DTP_ASSET_BUILD_DIR', str(ROOT/'.cache/asset-rebuild'))).resolve()
output.relative_to(ROOT)  # Input snapshots stay inside the repository.
output.mkdir(parents=True,exist_ok=True)
file = output/'flyer.html'
file.write_text(text, encoding='utf-8')
snapshot['html'] = {'path':file.relative_to(ROOT).as_posix(), 'sha256':hashlib.sha256(file.read_bytes()).hexdigest()}
proof = output/'flyer.html.inputs.json'
proof.write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n', encoding='utf-8')
# Do not publish a build assembled while declarations/inputs were changing.
subprocess.check_call(['node','--import','tsx',str(ROOT/'system/scripts/assets.ts'),
    'build-check','--root',str(ROOT),'--snapshot',proof.relative_to(ROOT).as_posix()],cwd=ROOT,stdout=subprocess.DEVNULL)
print(file)
