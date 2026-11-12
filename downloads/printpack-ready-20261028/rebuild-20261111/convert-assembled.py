"""CMYK embedded-text masters and separate vector-outline print derivatives.

No image downsampling or PDF 1.3 transparency flattening is performed.
Outputs remain working files until independent review of their fixed hashes.
"""
from pathlib import Path
from collections import defaultdict,Counter
from decimal import Decimal
import fitz,pikepdf,subprocess,hashlib,json,re,os,unicodedata,math,sys
B=Path(__file__).resolve().parent;R=B.parents[2];ICC=B.parent/'profiles/JapanColor2011Coated.icc'
def family(f):
 n=str(f.DescendantFonts[0].get('/BaseFont')) if '/DescendantFonts' in f else str(f.get('/BaseFont'))
 return re.sub(r'^[A-Z]{6}\+','',n.lstrip('/'))
def cmap(data):
 t=data.decode('ascii');result={}
 for section in re.findall(r'beginbfchar(.*?)endbfchar',t,re.S):
  result.update({int(a,16):b.upper() for a,b in re.findall(r'<([a-fA-F0-9]+)>\s*<([a-fA-F0-9]+)>',section)})
 for section in re.findall(r'beginbfrange(.*?)endbfrange',t,re.S):
  for lo,hi,dest in re.findall(r'<([a-fA-F0-9]+)>\s*<([a-fA-F0-9]+)>\s*<([a-fA-F0-9]+)>',section):
   for c in range(int(lo,16),int(hi,16)+1):result[c]=format(int(dest,16)+c-int(lo,16),f'0{len(dest)}X')
 return result
def fontmaps(file):
 maps=defaultdict(lambda:defaultdict(set))
 with pikepdf.open(file) as pdf:
  used=defaultdict(set)
  def scan(obj,resources,current=None,ancestors=()):
   stack=[]
   for instruction in pikepdf.parse_content_stream(obj):
    if not isinstance(instruction,pikepdf.ContentStreamInstruction):continue
    operands,operator=instruction;op=str(operator)
    if op=='q':stack.append(current)
    elif op=='Q':current=stack.pop() if stack else current
    elif op=='Tf':current=resources.get('/Font',{}).get(operands[0])
    elif op=='Do':
     form=resources.get('/XObject',{}).get(operands[0])
     if form is not None and form.get('/Subtype')==pikepdf.Name('/Form') and form.objgen not in ancestors:scan(form,form.get('/Resources',resources),current,ancestors+(form.objgen,))
    elif op in ['Tj','TJ',"'",'"'] and current is not None and current.get('/Encoding')==pikepdf.Name('/Identity-H'):
     strings=list(operands[0]) if op=='TJ' else [operands[-1]]
     for value in strings:
      if isinstance(value,pikepdf.String):
       data=bytes(value);assert len(data)%2==0
       used[family(current)].update(int.from_bytes(data[j:j+2],'big') for j in range(0,len(data),2))
  for page in pdf.pages:scan(page,page.obj.Resources)
  for f in pdf.objects:
   if not isinstance(f,pikepdf.Dictionary) or '/ToUnicode' not in f:continue
   if f.get('/Encoding')!=pikepdf.Name('/Identity-H'):continue
   for cid,value in cmap(f.ToUnicode.read_bytes()).items():
    if cid in used[family(f)]:maps[family(f)][cid].add(value)
 return {name:{cid:next(iter(v)) for cid,v in row.items() if len(v)==1} for name,row in maps.items()}
def finish(raw,out,expected=None):
 repairs=[]
 with pikepdf.open(raw) as pdf:
  box=pikepdf.Array([0,0,Decimal(210)*72/Decimal('25.4'),Decimal(297)*72/Decimal('25.4')])
  for p in pdf.pages:
   for key in ['/MediaBox','/CropBox','/TrimBox','/BleedBox','/ArtBox']:p.obj[key]=box
  icc=pdf.make_stream(ICC.read_bytes());icc.N=4
  pdf.Root.OutputIntents=pikepdf.Array([pikepdf.Dictionary(Type=pikepdf.Name('/OutputIntent'),S=pikepdf.Name('/GTS_PDFX'),OutputConditionIdentifier='JapanColor2011Coated',Info='Japan Color 2011 Coated',DestOutputProfile=icc)])
  if expected:
   for f in pdf.objects:
    if not isinstance(f,pikepdf.Dictionary) or '/ToUnicode' not in f:continue
    if f.get('/Encoding')!=pikepdf.Name('/Identity-H'):continue
    known=expected.get(family(f),{});actual=cmap(f.ToUnicode.read_bytes());changes={cid:known[cid] for cid,value in actual.items() if cid in known and value!=known[cid]}
    # GS can omit a multi-codepoint ligature (e.g. source CID00DC = ffi)
    # entirely. Restore that original extraction entry, never its glyph paint.
    changes.update({cid:value for cid,value in known.items() if cid not in actual and len(value)>4})
    if not changes:continue
    # Preserve every drawing/glyph/font byte. Replace only extraction metadata
    # with the unambiguous original CID-to-Unicode table (GS byte-carry bug).
    actual.update(changes);lines=['/CIDInit /ProcSet findresource begin','12 dict begin','begincmap','/CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def','/CMapName /SourceUnicodeRestored def','/CMapType 2 def','1 begincodespacerange','<0000> <FFFF>','endcodespacerange']
    items=sorted(actual.items())
    for start in range(0,len(items),100):
     chunk=items[start:start+100];lines.append(f'{len(chunk)} beginbfchar');lines.extend(f'<{cid:04X}> <{value}>' for cid,value in chunk);lines.append('endbfchar')
    lines.extend(['endcmap','CMapName currentdict /CMap defineresource pop','end','end'])
    f.ToUnicode.write(('\n'.join(lines)+'\n').encode('ascii'));repairs.append({'font':family(f),'CID_repairs':{f'{k:04X}':v for k,v in changes.items()}})
  pdf.save(out,compress_streams=True)
 return repairs
def gs(src,dest,outline):
 cmd=['gs','-dSAFER','--permit-file-read='+str(ICC),'-dBATCH','-dNOPAUSE','-sDEVICE=pdfwrite','-dCompatibilityLevel=1.4','-dAutoRotatePages=/None','-dEmbedAllFonts=true','-dSubsetFonts=true','-dNoOutputFonts='+str(outline).lower(),'-sColorConversionStrategy='+('LeaveColorUnchanged' if outline else 'CMYK'),'-dProcessColorModel=/DeviceCMYK','-sOutputICCProfile='+str(ICC),'-dDownsampleColorImages=false','-dDownsampleGrayImages=false','-dDownsampleMonoImages=false','-dAutoFilterColorImages=false','-dColorImageFilter=/FlateEncode','-dAutoFilterGrayImages=false','-dGrayImageFilter=/FlateEncode','-sOutputFile='+str(dest),str(src)]
 log=B/'inspection'/(dest.stem+'.gs.log')
 with log.open('w') as f:result=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,env={**os.environ,'XDG_CACHE_HOME':'/workspace/.dtp-cache'})
 assert result.returncode==0,(result.returncode,str(log))
 return cmd
def glyphs(page):
 result=defaultdict(list)
 for s in page.get_texttrace():
  for c in s['chars']:
   if chr(c[0]).isspace():continue
   result[unicodedata.normalize('NFKC',chr(c[0]))].append(c[2])
 return result
all_reports=[]
for label in sys.argv[1:] or ['brochure','flyer']:
 source=B/(label+'-native-assembled.pdf');fixed=B/'inspection'/(label+'-frozen-native.pdf');fixed.write_bytes(source.read_bytes());expected=fontmaps(fixed)
 raw=B/'inspection'/(label+'-CMYK-raw.pdf');native=B/(label+'-CMYK-text-master.pdf');outline_raw=B/'inspection'/(label+'-CMYK-outline-raw.pdf');outline=B/(label+'-CMYK-outline-print.pdf')
 command=gs(fixed,raw,False);repairs=finish(raw,native,expected)
 old=fitz.open(fixed);new=fitz.open(native);assert len(old)==len(new)==(16 if label=='brochure' else 2);pages=[]
 for i,p in enumerate(new):
  a,b=glyphs(old[i]),glyphs(p);assert {k:len(v) for k,v in a.items()}=={k:len(v) for k,v in b.items()},(label,i+1,'character mismatch')
  delta=max((min(math.dist(x,y) for y in b[k]) for k in a for x in a[k]),default=0);assert delta<.03,(label,i+1,delta)
  assert all(c[1]!=0 and c[0]!=65533 for s in p.get_texttrace() for c in s['chars'])
  assert set(m['colorspace'] for m in p.get_image_info())<={1,4},(label,i+1,'non-CMYK image')
  pages.append({'page':i+1,'native_chars':len(p.get_text()),'origin_max_delta_pt':delta,'images':len(p.get_images())})
 command_outline=gs(native,outline_raw,True);finish(outline_raw,outline)
 op=fitz.open(outline);assert len(op)==len(new)
 for p in op:assert not p.get_fonts() and not p.get_text().strip(),'Outline derivative still contains text/font objects'
 report={'status':'fixed_output_independent_review_pending','label':label,'native_master':native.name,'native_sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'outline_print':outline.name,'outline_sha256':hashlib.sha256(outline.read_bytes()).hexdigest(),'frozen_source_sha256':hashlib.sha256(fixed.read_bytes()).hexdigest(),'GS_commands':[command,command_outline],'CMYK_master_CMap_source_restorations':repairs,'ICC_sha256':hashlib.sha256(ICC.read_bytes()).hexdigest(),'pages':pages,'independent_final_visual_and_outline_comparison':'pending'}
 all_reports.append(report);print(json.dumps({'label':label,'native_sha256':report['native_sha256'],'outline_sha256':report['outline_sha256'],'pages':len(pages),'unicode_fonts_repaired':len(repairs)},ensure_ascii=False),flush=True)
 (B/(label+'-conversion-preflight.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
