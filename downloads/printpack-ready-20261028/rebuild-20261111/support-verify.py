"""Verify and freeze native P10/P11 drafts, including a native-text-hidden diagnostic."""
from pathlib import Path
import fitz,pikepdf,json,subprocess,hashlib,unicodedata,numpy as np
B=Path(__file__).resolve().parent;A=B/'support-assets';report=json.loads((B/'support-rebuild-report.json').read_text());checks=[];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();norm=lambda x:''.join(unicodedata.normalize('NFKC',x).split())
for pn in [10,11]:
 path=B/f'support-p{pn}-native-draft.pdf';d=fitz.open(path);p=d[0];txt=norm(p.get_text());expected=[x['text'] for x in report['text'] if x['page']==pn];missing=[x for x in expected if norm(x) not in txt]
 # Per-character display of the headline may create word spacing/newlines;
 # the text comparison removes only whitespace, never publication letters.
 assert not missing,missing
 assert len(d)==1 and abs(p.rect.width-210*72/25.4)<.001 and abs(p.rect.height-297*72/25.4)<.001
 zero=sum(c[1]==0 or c[0]==65533 for s in p.get_texttrace() for c in s['chars']);assert zero==0
 fontout=subprocess.run(['pdffonts',str(path)],text=True,capture_output=True,check=True).stdout;rows=fontout.splitlines()[2:];unembedded=[line for line in rows if line.split()[-5]!='yes'];assert not unembedded,unembedded
 target=A/f'p{pn}-poppler';render=subprocess.run(['pdftoppm','-png','-r','100','-singlefile',str(path),str(target)],text=True,capture_output=True,check=True);assert not render.stderr,render.stderr
 diag=A/f'p{pn}-DIAGNOSTIC-NATIVE-TEXT-HIDDEN.pdf'
 with pikepdf.open(path) as pdf:
  streams=[]
  for o in pdf.objects:
   if isinstance(o,pikepdf.Stream) and o.get('/Subtype')==pikepdf.Name.Form:streams.append(o)
  for page in pdf.pages:
   contents=page.obj.get('/Contents');streams.extend(list(contents) if isinstance(contents,pikepdf.Array) else [contents])
  for stream in streams:
   instructions=pikepdf.parse_content_stream(stream);out=[i for i in instructions if str(i.operator) not in ['Tj','TJ',"'",'"']];stream.write(pikepdf.unparse_content_stream(out))
  pdf.save(diag)
 nd=fitz.open(diag);nd[0].get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(A/f'p{pn}-native-hidden.png')
 # Check that every protected source hero sample is actually embedded unchanged.
 protected=[x for x in report['photos'] if x.get('page')==pn and x.get('name')=='source_hero_pixels_protected'][0]
 ref=fitz.open('/workspace/DTP/'+report['source']);sp=ref[pn-1];sourcepix=fitz.Pixmap(ref,sp.get_images()[0][0]);src=np.frombuffer(sourcepix.samples,dtype=np.uint8).reshape(sourcepix.height,sourcepix.width,sourcepix.n);x0,y0,x1,y1=protected['source_crop_px'];expectedphoto=src[y0:y1,x0:x1,:3]
 matching=[]
 for inf in p.get_images(full=True):
  if inf[2:4]!=(x1-x0,y1-y0):continue
  pp=fitz.Pixmap(d,inf[0]);a=np.frombuffer(pp.samples,dtype=np.uint8).reshape(pp.height,pp.width,pp.n)
  if a.shape==expectedphoto.shape and np.array_equal(a,expectedphoto):matching.append(inf[0])
 assert matching,'Original protected hero image bytes not found'
 with pikepdf.open(path) as pdf:boxes={k:[float(x) for x in pdf.pages[0].obj[k]] for k in ['/MediaBox','/CropBox','/TrimBox','/BleedBox','/ArtBox']}
 checks.append({'page':pn,'file':path.name,'sha256':sha(path),'characters':len(p.get_text()),'all_recorded_copy_present_NFKC_whitespace_normalized':not missing,'zero_glyphs':zero,'all_fonts_embedded':True,'font_count':len(rows),'boxes':boxes,'poppler_stderr':render.stderr,'protected_source_hero_image_exact_sample_match_xrefs':matching,'original_photo_repair_mask':protected,'native_hidden_diagnostic':diag.name})
report['outputs']={str(x['page']):{'file':x['file'],'sha256':x['sha256']} for x in checks};report['verification']=checks;report['status']='native_RGB_draft_ready_for_parent_independent_review_not_submission';report['issues']=['Handwritten source glyph shapes unavailable; replacement native type retains copy but is visibly different.','Ordinary raster typography has been retypeset to measured source ink; typeface outline details differ.','Footer sky/text fields repaired with imagegen and contiguous feathered fields; building/leaf pixels outside repair fields retained from original.','No full-page image is used as a page background; every publication label is native except genuine text seen inside photographs.','CMYK conversion and whole-book independent review remain parent tasks.']
(B/'support-rebuild-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(checks,ensure_ascii=False,indent=2))
