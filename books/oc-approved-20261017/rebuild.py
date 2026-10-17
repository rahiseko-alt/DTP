#!/usr/bin/env python3
"""Generate editable HTML from source template, registered photo map, and school facts."""
from pathlib import Path
import json, html, yaml
ROOT=Path(__file__).resolve().parents[2]
BOOK=Path(__file__).resolve().parent
school=yaml.safe_load((ROOT/'company-data/facts/school.yaml').read_text())
address=school['address']
values={k:school[k] for k in ('name','name_en','tel','email','corporation')}
replacements={'school':values['name'],'english':values['name_en'],'tel':values['tel'],'email':values['email'],'corporation':values['corporation'],'address':'〒'+str(address['postal_code'])+' '+''.join(str(address[k]) for k in ('prefecture','city','line1')),'access':'・'.join(school['access']) if isinstance(school['access'],list) else school['access']}
map_path=BOOK/'parts/photos-map.json'
if not map_path.exists(): raise SystemExit('Photo map not ready: '+str(map_path))
data=json.loads(map_path.read_text())
entries=data if isinstance(data,list) else data.get('photos',data.get('entries',data.get('slots',[])))
if isinstance(entries,dict):entries=[dict(v,slot=k) for k,v in entries.items()]
for item in entries:
    file=item.get('file') or item.get('source')
    path=Path(file)
    if path.is_absolute(): target=path
    elif str(path).startswith('books/') or str(path).startswith('company-data/'):target=ROOT/path
    else:target=BOOK/path
    import os
    replacements[item['slot']]=os.path.relpath(target,BOOK/'source')
text=(BOOK/'source/flyer.template.html').read_text()
for item in entries:
    pos=item.get('crop',{}).get('object_position','50% 50%')
    text=text.replace('src="@@'+item['slot']+'@@"','src="@@'+item['slot']+'@@" style="object-position:'+html.escape(pos,quote=True)+'"')
copy=json.loads((BOOK/'text/content.json').read_text())
import re
def copy_value(match):
    value=copy
    for key in match.group(1).split('.'):
        value=value[int(key)] if isinstance(value,list) else value[key]
    # Date weekday badges are independent graphical elements in the template.
    if match.group(1).startswith('front.dates.'): value=value.replace('（日）','')
    result=html.escape(str(value))
    if match.group(1)=='front.lead':result=result.replace('、','、<br>',1)
    if match.group(1)=='front.photo_copy':result=result.replace('、','、<br>',1)
    return result
text=re.sub(r'@@copy:([^@]+)@@',copy_value,text)
for key,value in replacements.items():text=text.replace('@@'+key+'@@',html.escape(str(value),quote=True))
if '@@' in text:raise SystemExit('Unresolved template placeholders')
(BOOK/'source/flyer.html').write_text(text)
print(BOOK/'source/flyer.html')
