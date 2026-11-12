"""Verify the exact OC-side candidate; geometry/photo checks do not grant visual approval."""
from pathlib import Path
import fitz,pikepdf,numpy as np,json,hashlib,unicodedata,subprocess,zxingcpp,os
B=Path(__file__).resolve().parent;A=B/'assets/flyer-back';R=B.parents[2]
source=R/json.loads((B.parent/'receipts.json').read_text())[1]['path'];s=fitz.open(source);d=fitz.open(B/'flyer-back-native-candidate.pdf');p=d[0]
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest();report={'file':'flyer-back-native-candidate.pdf','sha256':sha(B/'flyer-back-native-candidate.pdf'),'source_sha256':sha(source),'pages':len(d)}
assert len(d)==1
report['boxes']={k:list(getattr(p,k)) for k in ['mediabox','cropbox','trimbox','bleedbox','artbox']}
for box in report['boxes'].values():assert max(abs(x-y) for x,y in zip(box,[0,0,210*72/25.4,297*72/25.4]))<.0001
text=p.get_text();report['text']=text;report['native_characters']=len(text);report['glyph_zero']=sum(c[1]==0 or c[0]==65533 for sp in p.get_texttrace() for c in sp['chars']);assert not report['glyph_zero']
for value in ['11/21','12/5','12/19','AIビジネス専門学校','オープンキャンパスでできること','保護者の参加も歓迎','052-451-3821','aibusiness.kaihougakuen@gmail.com']:
 assert value in unicodedata.normalize('NFKC',text),value
qr={}
for dpi in [150,300]:
 pix=p.get_pixmap(matrix=fitz.Matrix(dpi/72,dpi/72),alpha=False);arr=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,pix.n);decoded=[q.text for q in zxingcpp.read_barcodes(arr)];qr[dpi]=decoded;assert 'mailto:aibusiness.kaihougakuen@gmail.com' in decoded
report['QR']=qr
fonts=[]
with pikepdf.open(B/'flyer-back-native-candidate.pdf') as pdf:
 for obj in pdf.objects:
  if not isinstance(obj,pikepdf.Dictionary) or obj.get('/Type')!=pikepdf.Name('/Font') or '/FontDescriptor' not in obj:continue
  desc=obj.FontDescriptor;embedded=any(k in desc for k in ['/FontFile','/FontFile2','/FontFile3']);fonts.append({'name':str(obj.get('/BaseFont')),'embedded':embedded});assert embedded
report['embedded_fonts']=fonts
# Compare untouched source photographic interiors by rendering the same page-space crop.
# DTP raster placement uses original decode and original matrix, not generated faces.
hr=s[1].get_image_rects(162)[0];regions={'standing_man_face':[650,35,795,225],'front_man_face':[440,300,610,470],'left_masked_face':[185,300,310,440],'front_woman_face':[930,270,1080,440],'back_woman_face':[930,110,1010,235],'back_masked_face':[1050,145,1175,300],'hands_watch':[650,450,850,555]}
photo=[]
for name,(x0,y0,x1,y1) in regions.items():
 rect=fitz.Rect(hr.x0+x0/1226*hr.width,hr.y0+y0/713*hr.height,hr.x0+x1/1226*hr.width,hr.y0+y1/713*hr.height)
 aa=s[1].get_pixmap(matrix=fitz.Matrix(4,4),clip=rect,alpha=False);bb=p.get_pixmap(matrix=fitz.Matrix(4,4),clip=rect,alpha=False);x=np.frombuffer(aa.samples,dtype=np.uint8).astype(int);y=np.frombuffer(bb.samples,dtype=np.uint8).astype(int);diff=abs(x-y)
 row={'region':name,'page_rect_pt':list(rect),'dpi':288,'max_channel_delta':int(diff.max()),'mean_channel_delta':float(diff.mean()),'nonzero_channels':int(np.count_nonzero(diff))};photo.append(row)
 # ICC-less RGB extraction can differ by one code value from source ICC rendering.
 assert row['max_channel_delta']<=3 and row['mean_channel_delta']<.2,row
report['protected_photographic_regions']=photo
# Full page Poppler render, stderr required empty. Parent also visually reviews both.
env=os.environ.copy();env['XDG_CACHE_HOME']='/workspace/.dtp-cache'
fontconfig=A/'fontconfig.xml';fontconfig.write_text('<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd"><fontconfig><dir>/usr/share/fonts</dir><cachedir>/workspace/.dtp-cache/fontconfig</cachedir></fontconfig>\n');env['FONTCONFIG_FILE']=str(fontconfig.resolve())
proc=subprocess.run(['pdftoppm','-f','1','-singlefile','-r','150','-png',str(B/'flyer-back-native-candidate.pdf'),str(A/'poppler')],capture_output=True,text=True,env=env);report['poppler_returncode']=proc.returncode;report['poppler_stderr']=proc.stderr
unexpected=[line for line in proc.stderr.splitlines() if line.strip() and line.strip() not in ['Fontconfig error: No writable cache directories','/var/cache/fontconfig']]
report['poppler_PDF_errors']=unexpected;report['environment_cache_warning_only']=bool(proc.stderr) and not unexpected
assert proc.returncode==0 and not unexpected
report['status']='TECHNICAL_CHECKS_PASS_VISUAL_APPROVAL_PENDING';report['limitations']=['RGB candidate; full CMYK/outline derivative/combined flyer pending.','Publication type uses replacement fonts with measured source glyph bounds; exact original handwritten shapes unavailable.','Photo repair is confined to annotation-covered backgrounds/sleeve/paint regions; protected visible people compared explicitly.']
(B/'flyer-back-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'sha256':report['sha256'],'native_chars':len(text),'qr':qr,'faces_max_delta':max(r['max_channel_delta'] for r in photo),'poppler_stderr':proc.stderr},ensure_ascii=False))
