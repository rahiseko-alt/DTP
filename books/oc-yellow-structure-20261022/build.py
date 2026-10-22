#!/usr/bin/env python3
"""Build the Japanese-image OC yellow version without changing any preserved source."""
from pathlib import Path
import argparse, hashlib, html, json
import yaml
B=Path(__file__).resolve().parent
R=B.parents[1]
p=argparse.ArgumentParser();p.add_argument('--contact-email');p.add_argument('--contact-qr');p.add_argument('--pending-contact',action='store_true');args=p.parse_args()
school=yaml.safe_load((R/'company-data/facts/school.yaml').read_text())
oc=yaml.safe_load((R/'company-data/facts/oc-flyer.yaml').read_text())
contacts=yaml.safe_load((R/'company-data/facts/contacts.yaml').read_text())['contacts']
contact_fact=next(c for c in contacts if c['id']==oc['contact_id'])
if args.contact_email: assert args.contact_email==contact_fact['email']
if args.contact_qr: assert args.contact_qr==oc['contact_qr']
args.contact_email=contact_fact['email'];args.contact_qr=oc['contact_qr']
assert oc['experience_items']==[1] and oc['date_year'] is None and oc['date_weekdays'] is None
esc=lambda s:html.escape(str(s),quote=True)
uri=lambda path:(R/path).as_uri()
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
assets={
 'logo':'company-data/brand/logo/logo-horizontal.png',
 'hero':'shared/generated-assets/jp-existing-photo-b-r01/B-PHOTO-R07-S02.png',
 'experience':'shared/generated-assets/jp-students-four-r01/JP4-R01-S01.png',
 'course_ai':'books/prospectus-jp-isen-2028/work/learning-a/p05-01-revision2-photo.png',
 'course_business':'shared/generated-assets/jp-students-four-r01/JP4-R01-S01.png',
 'life_lesson':'books/prospectus-jp-isen-2028/work/learning-b/p07-photo-06.png',
 'life_exchange':'books/prospectus-jp-isen-2028/work/learning-b/p07-photo-02.png',
 'life_event':'books/prospectus-jp-isen-2028/work/learning-a/p05-08-revision2-photo.png',
 'map':'books/oc-approved-20261017/parts/support-school-access-map/f22d288efab6e1220898fac2d6d54fe8c014266a748d0637e0153fa7853de27f/support-school-access-map.png',
}
if not args.pending_contact and (not args.contact_email or not args.contact_qr):
 p.error('Final contact email and a matching mailto QR must be explicitly selected')
if args.contact_qr:
 q=Path(args.contact_qr);q=q if q.is_absolute() else R/q
 if not q.is_file():p.error('QR file not found')
 qr=f'<img class="contact-qr" src="{esc(q.as_uri())}" alt="メール作成用QR">'
else:qr='<div class="contact-qr pending"></div>'
email=args.contact_email or ''
address='〒'+str(school['address']['postal_code'])+' '+''.join(str(school['address'][k]) for k in ['prefecture','city','line1'])
contact=f'''<div class="contact-copy"><p class="contact-title">オープンキャンパスのお問い合わせ</p><div class="phone">{esc(school['tel'])}</div><a class="email" href="mailto:{esc(email)}">{esc(email)}</a></div><div class="qr-contact">{qr}<span>メールでお問い合わせ</span></div>'''
footer=f'<footer class="front-contact">{contact}</footer>'
flow=[('1','学校説明','学校の特徴や<br>学びの内容を紹介します。'),('2','体験授業','AIやビジネスの<br>授業を体験できます。'),('3','在校生交流','在校生と話して<br>学校生活を知ることができます。'),('4','個別相談','入試・学費・就職について<br>個別に相談できます。')]
flow_html=''.join(f'<div class="flow-step"><h3><b>{n}</b>{t}</h3><p>{body}</p></div>' for n,t,body in flow)
base=(B/'template.html').read_text()
replacements={
 'STYLE_URI':(B/'style.css').as_uri(), 'SCHOOL':esc(school['name']), 'CORPORATION':esc(school['corporation']),
 'ADDRESS':esc(address), 'ACCESS':esc(school['access'][0]), 'FRONT_CONTACT':footer,
 'BACK_CONTACT':contact,'FLOW':flow_html,
 'DATES':''.join('<div class="date">'+esc(d).replace('/','<span>/</span>')+'</div>' for d in oc['dates']),
 'EXPERIENCE_HEADING':esc(oc['experience_heading']),
}
for name,path in assets.items():replacements[name.upper()+'_URI']=esc(uri(path))
for key,val in replacements.items():base=base.replace('@@'+key+'@@',val)
assert '@@' not in base
(B/'output').mkdir(exist_ok=True)
(B/'output/flyer.html').write_text(base)
record={'version':'OC-YELLOW-JP-STRUCTURE-20261022','scope':'User five instructions; separate 2-page draft; preserved original unchanged','source_document':'oc-approved-20261017','source_pdf_sha256':'2c0bd3b6d91449666adf9ac73091e10f7cb37831384ebe807d2ff6117cd264d1','dates':oc['dates'],'date_year':None,'date_weekdays':None,'contact_email':args.contact_email,'contact_qr':str(q.relative_to(R)) if args.contact_qr else None,'contact_final':not args.pending_contact,'photo_generation_new':False,'photos_are_illustrative_ai_images':True,'assets':{name:{'file':path,'sha256':sha(R/path)} for name,path in assets.items()},'school_facts_sha256':sha(R/'company-data/facts/school.yaml'),'oc_facts_sha256':sha(R/'company-data/facts/oc-flyer.yaml'),'contacts_facts_sha256':sha(R/'company-data/facts/contacts.yaml')}
(B/'reviews/build-inputs.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(B/'output/flyer.html')
