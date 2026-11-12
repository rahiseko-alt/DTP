"""Verify the frozen four-page native reconstruction, not printer approval."""
from pathlib import Path
import fitz,pikepdf,json,hashlib,unicodedata,subprocess,numpy as np
from PIL import Image
from scipy import ndimage
B=Path(__file__).resolve().parent;A=B/'odd-assets';report=json.loads((B/'odd-rebuild-report.json').read_text());path=B/report['pdf'];assert hashlib.sha256(path.read_bytes()).hexdigest()==report['sha256'];d=fitz.open(path);rows=[]
def norm(t):return ''.join(unicodedata.normalize('NFKC',t).split())
for i,p in enumerate(d):
 row=report['pages'][i];raw=p.get_text();missing=[r['text'] for r in row['text'] if norm(r['text']) not in norm(raw)]
 im=p.get_images();equal=[];source_crops=row['photos']+row.get('raster_symbols',[])
 for item in im:
  pix=fitz.Pixmap(d,item[0]);digest=hashlib.sha256(pix.samples).hexdigest();matches=[x for x in source_crops if x['RGB_sha256']==digest];assert matches,(row['page'],item[0]);rects=p.get_image_rects(item[0]);assert len(rects)==1
  match=matches[0];err=max(abs(a-b) for a,b in zip(rects[0],match['rect_pt']));assert err<.001,(row['page'],err)
  equal.append({'xref':item[0],'RGB_sha256':digest,'matches_source_crop':True,'placement_delta_pt':err})
 assert len(im)==len(source_crops)
 glyphzero=sum(c[1]==0 or c[0]==65533 for s in p.get_texttrace() for c in s['chars'])
 assert not missing and not glyphzero,(row['page'],missing,glyphzero)
 rows.append({'book_page':row['page'],'native_characters':len(raw),'glyph_zero_or_replacement':glyphzero,'missing_expected_lines':missing,'source_crop_verification':equal,'photograph_count':len(row['photos']),'text_free_symbol_count':len(row.get('raster_symbols',[])),'image_count':len(im),'font_count':len(p.get_fonts()),'MediaBox_pt':list(p.mediabox),'CropBox_pt':list(p.cropbox)})
 # Full-page two renderer proof at 100dpi, with any stderr retained.
 p.get_pixmap(matrix=fitz.Matrix(100/72,100/72)).save(A/f'mupdf-{i+1}.png')
proc=subprocess.run(['pdftoppm','-r','100','-png',str(path),str(A/'poppler')],capture_output=True,text=True);assert proc.returncode==0;assert not proc.stderr.strip(),proc.stderr
with pikepdf.open(path) as pdf:
 for obj in pdf.objects:
  if isinstance(obj,pikepdf.Dictionary) and obj.get('/Type')==pikepdf.Name('/FontDescriptor'):assert any(k in obj for k in ['/FontFile','/FontFile2','/FontFile3']),obj
result={'file':path.name,'sha256':report['sha256'],'status':'technical_checks_pass_visual_fidelity_limitations','pages':rows,'poppler_exit':proc.returncode,'poppler_stderr':proc.stderr,'all_font_descriptors_embedded':True,'scope':'Four pages only. RGB master, CMYK and printer outline derivative not checked here.','visual_review':'Parent/subagent must independently review final frozen SHA.','remaining_limitations':['Native replacement font glyph shapes differ from source raster typography.','Color-field gradients are native sampled shadings from source colors; faint paper texture is not reproduced.','Source photograph pixel arrays and normalized placement are preserved exactly; no person regeneration or retouching.']}
(B/'odd-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='pages'},ensure_ascii=False,indent=2))
