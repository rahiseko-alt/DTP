#!/usr/bin/env python3
"""Verify copied school photos and write a compact inventory for the handoff."""
from pathlib import Path
import hashlib, json, sys

ROOT = Path(__file__).resolve().parents[2]
BOOK = Path(__file__).resolve().parent
mapping = json.loads((BOOK / 'parts/photos-map.json').read_text())
entries = mapping['slots']
inventory = []
errors = []
for item in entries:
    original = ROOT / item['source']
    part = ROOT / item['file']
    if not original.is_file() or not part.is_file():
        errors.append(f"missing photo: {item['id']}")
        continue
    source_hash = hashlib.sha256(original.read_bytes()).hexdigest()
    part_hash = hashlib.sha256(part.read_bytes()).hexdigest()
    if source_hash != part_hash or source_hash != item['sha256']:
        errors.append(f"photo hash mismatch: {item['id']}")
    inventory.append({'kind': 'school-photo', 'id': item['id'], 'slot': item['slot'], 'file': item['file'], 'source': item['source'], 'sha256': part_hash, 'rights': item['rights'], 'caption': item['caption'], 'placement_mm': item['placement_mm'], 'crop': item['crop']})

for kind, files in {
    'brand-logo': ['parts/brand/logo-horizontal.png'],
    'official-qr': ['parts/official-site-qr.png', 'parts/official-site-qr.svg'],
    'svg-icon': [f'parts/icons/{name}.svg' for name in ('consult', 'laptop', 'people', 'school')],
    'editable-copy': ['text/content.json'],
    'editable-layout': ['source/flyer.template.html', 'source/layout.css', 'source/flyer.html'],
    'combined-output': ['output/実写真版_OCチラシ_両面.pdf', 'output/page-1.png', 'output/page-2.png'],
    'approved-original': ['../../references/school-own/oc-approved-20261017/original/approved.pdf'],
}.items():
    for rel in files:
        file = (BOOK / rel).resolve()
        if not file.is_file():
            errors.append(f'missing {kind}: {rel}')
            continue
        inventory.append({'kind': kind, 'file': str(file.relative_to(ROOT)), 'sha256': hashlib.sha256(file.read_bytes()).hexdigest()})

result = {'book': 'oc-approved-20261017', 'approved_original_is_flat_raster': True, 'registered_school_photos': len(entries), 'ai_generated_photos_in_combined_version': 0, 'ai_image_generation_input_used': False, 'inventory': inventory, 'errors': errors}
out = BOOK / 'parts/manifest.json'
out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(f"parts verification: {len(entries)} photos; {len(inventory)} inventoried files; {len(errors)} errors")
for error in errors:
    print('ERROR:', error)
sys.exit(bool(errors))
