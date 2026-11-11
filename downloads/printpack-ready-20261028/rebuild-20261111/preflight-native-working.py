"""Validate the five-page repair work only; this is not a complete submission."""
from pathlib import Path
from decimal import Decimal
from collections import Counter,defaultdict
import fitz,pikepdf,json,hashlib,unicodedata,math,re
B=Path(__file__).resolve().parent;R=Path('/workspace/DTP');status=R/'.cache/rebuild-20261111/native-master-cmyk.exit';assert status.read_text().strip()=='0'
source=B/'native-pages-12-16-CMYK-working.pdf';output=B/'native-pages-12-16-CMYK-font-embedded-working.pdf';icc=(B.parent/'profiles/JapanColor2011Coated.icc').read_bytes()
with pikepdf.open(source) as d:
 profile=pikepdf.Stream(d,icc);profile.N=4;d.Root.OutputIntents=pikepdf.Array([pikepdf.Dictionary(Type=pikepdf.Name('/OutputIntent'),S=pikepdf.Name('/GTS_PDFX'),OutputConditionIdentifier='JapanColor2011Coated',Info='Japan Color 2011 Coated',DestOutputProfile=profile)])
 for p in d.pages:
  box=pikepdf.Array([0,0,Decimal(210)*72/Decimal('25.4'),Decimal(297)*72/Decimal('25.4')])
  for k in ['/MediaBox','/CropBox','/TrimBox','/BleedBox']:p.obj[k]=box
 # Ghostscript 10.05.1 misincrements <5dfe> across a bfrange byte boundary:
 # source <4127><412b><5dfe> maps CID 412b to U+5E02 (市), not U+5D02 (崂).
 # Recover this mapping from the frozen master. No glyph/font/image bytes change.
 source_maps={}
 with pikepdf.open(R/'.cache/rebuild-20261111/frozen-native-master.pdf') as master_pdf:
  for f in master_pdf.objects:
   if not isinstance(f,pikepdf.Dictionary) or '/ToUnicode' not in f or '/DescendantFonts' not in f:continue
   name=str(f.DescendantFonts[0].get('/BaseFont')).lstrip('/')
   if name not in ['NotoSansCJKjp-Regular','DTPRebuiltSansJPRegular']:continue
   cmap=f.ToUnicode.read_bytes().decode('ascii')
   for section in re.findall(r'beginbfrange(.*?)endbfrange',cmap,re.S):
    for lo,hi,dest in re.findall(r'<([0-9a-fA-F]+)>\s*<([0-9a-fA-F]+)>\s*<([0-9a-fA-F]+)>',section):
     if int(lo,16)<=0x412b<=int(hi,16):source_maps[name]=int(dest,16)+0x412b-int(lo,16)
 assert set(source_maps.values())=={0x5e02}
 cmap_repairs=[]
 for f in d.objects:
  if not isinstance(f,pikepdf.Dictionary) or '/ToUnicode' not in f or '/DescendantFonts' not in f:continue
  name=str(f.DescendantFonts[0].get('/BaseFont')).split('+')[-1].lstrip('/')
  if name not in source_maps:continue
  assert f.Encoding==pikepdf.Name('/Identity-H')
  raw=f.ToUnicode.read_bytes();fixed,n=re.subn(rb'(<412b>\s*<412b>\s*)<5d02>',rb'\g<1><5e02>',raw,flags=re.I)
  if n:f.ToUnicode.write(fixed);cmap_repairs.append({'font':name,'CID':'412b','GS_unicode':'5D02','restored_source_unicode':'5E02','count':n})
 d.save(output,compress_streams=True)
master=fitz.open(R/'.cache/rebuild-20261111/frozen-native-master.pdf');out=fitz.open(output);assert len(out)==len(master)==5
rows=[]
def chars(p):
 result=defaultdict(list)
 for span in p.get_texttrace():
  for c in span['chars']:
   u=unicodedata.normalize('NFKC',chr(c[0]))
   if not u.isspace():result[u].append(c[2])
 for u in result:result[u].sort()
 return result
for i,p in enumerate(out):
 a,b=chars(master[i]),chars(p);counts_a={k:len(v) for k,v in a.items()};counts_b={k:len(v) for k,v in b.items()};missing={k:(counts_a.get(k,0),counts_b.get(k,0)) for k in set(counts_a)|set(counts_b) if counts_a.get(k,0)!=counts_b.get(k,0)};deltas=[]
 if not missing:
  for k in a:
   for x in a[k]:deltas.append(min(math.hypot(x[0]-y[0],x[1]-y[1]) for y in b[k]))
 row={'page':i+12,'live_text_chars':len(p.get_text()),'live_fonts':len(p.get_fonts()),'zero_or_replacement_glyphs':sum(c[1]==0 or c[0]==65533 for s in p.get_texttrace() for c in s['chars']),'normalized_character_count_changes':missing,'largest_character_origin_delta_pt':max(deltas,default=None),'images':len(p.get_images()),'image_components':sorted({m['colorspace'] for m in p.get_image_info()})};rows.append(row);assert row['live_text_chars']>50 and row['live_fonts']>0 and row['zero_or_replacement_glyphs']==0;assert set(row['image_components'])<={1,4};assert not missing,row;assert row['largest_character_origin_delta_pt']<.01,row;print(row)
report={'status':'partial_not_for_submission','file':output.name,'sha256':hashlib.sha256(output.read_bytes()).hexdigest(),'ghostscript_exit':0,'frozen_input_sha256':hashlib.sha256((R/'.cache/rebuild-20261111/frozen-native-master.pdf').read_bytes()).hexdigest(),'ICC_sha256':hashlib.sha256(icc).hexdigest(),'ToUnicode_repairs_from_master':cmap_repairs,'pages':rows,'full_book_complete':False,'independent_final_visual_review':'pending','printer_check':'not_performed'}
(B/'native-five-page-CMYK-preflight.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
