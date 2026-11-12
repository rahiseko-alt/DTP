"""Assemble verified native parts in reading order; never label this as final."""
from pathlib import Path
from decimal import Decimal
import fitz,pikepdf,hashlib,json,re
B=Path(__file__).resolve().parent
parts={1:('cover-native-draft.pdf',0),2:('even-native-draft.pdf',0),3:('odd-native-pages-03-05-07-09.pdf',0),4:('even-native-draft.pdf',1),5:('odd-native-pages-03-05-07-09.pdf',1),6:('even-native-draft.pdf',2),7:('odd-native-pages-03-05-07-09.pdf',2),8:('p8-native-draft.pdf',0),9:('odd-native-pages-03-05-07-09.pdf',3),10:('support-p10-native-draft.pdf',0),11:('support-p11-native-draft.pdf',0)}
parts.update({i:('native-pages-12-16-working-master.pdf',i-12) for i in range(12,17)})
flyer={1:('flyer-front-native-trial.pdf',0),2:('flyer-back-native-candidate.pdf',0)}
W,H=210*72/25.4,297*72/25.4
proof=[]
for label,spec in [('brochure',parts),('flyer',flyer)]:
 out=fitz.open();rows=[]
 for page,(name,index) in spec.items():
  path=B/name;assert path.exists(),f'Missing native part: {name}'
  src=fitz.open(path);p=src[index];assert abs(p.rect.width-W)<.01 and abs(p.rect.height-H)<.01,(name,list(p.rect))
  assert len(p.get_text().strip())>20,(name,'no native publication type')
  bad=sum(c[1]==0 or c[0]==65533 for s in p.get_texttrace() for c in s['chars']);assert bad==0,(name,bad)
  out.insert_pdf(src,from_page=index,to_page=index)
  rows.append({'page':page,'input':name,'input_page':index+1,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'native_chars':len(p.get_text()),'image_count':len(p.get_images())})
 file=B/(label+'-native-assembled.pdf');raw=B/'inspection'/(label+'-assembled-before-cmap.pdf');out.save(raw,garbage=4,deflate=True);out.close()
 repairs=[]
 with pikepdf.open(raw) as pdf:
  box=pikepdf.Array([0,0,Decimal(210)*72/Decimal('25.4'),Decimal(297)*72/Decimal('25.4')])
  for p in pdf.pages:
   for key in ['/MediaBox','/CropBox','/TrimBox','/BleedBox','/ArtBox']:p.obj[key]=box
  for font in pdf.objects:
   if not isinstance(font,pikepdf.Dictionary) or '/ToUnicode' not in font:continue
   name=str(font.get('/BaseFont',''))
   if not any(k in name for k in ['DTPRebuiltSansJP','NotoSansCJK']):continue
   data=font.ToUnicode.read_bytes()
   for cid,alias,desired in [(b'000e',b'2011',b'002d'),(b'0001',b'00a0',b'0020')]:
    data,n=re.subn(rb'(<'+cid+rb'>\s*)<'+alias+rb'>',lambda m:m.group(1)+b'<'+desired+b'>',data,flags=re.I)
    if n:repairs.append({'font':name,'CID':cid.decode(),'alias':alias.decode(),'input_unicode':desired.decode()})
   font.ToUnicode.write(data)
  pdf.save(file,compress_streams=True)
 proof.append({'label':label,'file':file.name,'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'pages':rows,'input_alias_repairs':repairs})
(B/'assembly-working.json').write_text(json.dumps({'status':'working_not_submission','outputs':proof},ensure_ascii=False,indent=2)+'\n')
print(json.dumps(proof,ensure_ascii=False,indent=2))
