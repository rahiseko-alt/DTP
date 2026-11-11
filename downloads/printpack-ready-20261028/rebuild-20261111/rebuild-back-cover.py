"""Rebuild brochure P16 from editable type and vector geometry only; review draft."""
from pathlib import Path
import fitz,pikepdf,yaml,json,html,hashlib,unicodedata,numpy as np,re
B=Path(__file__).resolve().parent;R=Path('/workspace/DTP');s=yaml.safe_load((R/'company-data/facts/school.yaml').read_text());N=(.141,.278,.42);P=(1,.1,.42);d=fitz.open();p=d.new_page(width=210*72/25.4,height=297*72/25.4)
F='/workspace/.dtp-tools/native-fonts'
if not (Path(F)/'DTPRebuiltSansJPRegular.otf').exists():
 from fontTools.ttLib import TTCollection
 Path(F).mkdir(exist_ok=True,parents=True)
 for weight in ['Regular','Bold']:
  collection=TTCollection(f'/usr/share/fonts/opentype/noto/NotoSansCJK-{weight}.ttc');font=collection.fonts[0];name='DTPRebuiltSansJP'+weight
  for record in font['name'].names:
   if record.nameID in [1,3,4,6,16]:record.string=name.encode(record.getEncoding())
  if 'CFF ' in font:
   cff=font['CFF '].cff;cff.fontNames[0]=name;cff.topDictIndex[0].FamilyName=name;cff.topDictIndex[0].FullName=name
  font.save(Path(F)/(name+'.otf'))
css='@font-face{font-family:NativeNoto;src:url(DTPRebuiltSansJPRegular.otf)}@font-face{font-family:NativeNoto;src:url(DTPRebuiltSansJPBold.otf);font-weight:bold}'
records=[]
measured=json.loads((B/'source-page16-ink-bboxes.json').read_text())['lines']
line_keys=iter(['school_name','corporation','department_heading','department_1','description_1','department_2','description_2','contact_header','phone_label','phone','email_label','email','address_label','address','traffic','site_label','url','slogan'])
def text(rect,value,size=10,bold=False,color='#24476b',align='left'):
 r=fitz.Rect(rect)
 # Keep the replacement as real PDF type. Match measured source ink bounds,
 # rather than assuming HTML font metrics reproduce the raster's baseline.
 scratch=fitz.open();sp=scratch.new_page(width=p.rect.width,height=p.rect.height)
 assert '\n' not in value
 fontname='RebuiltBold' if bold else 'RebuiltRegular';fontfile=F+('/DTPRebuiltSansJPBold.otf' if bold else '/DTPRebuiltSansJPRegular.otf')
 sp.insert_font(fontname=fontname,fontfile=fontfile)
 rgb=tuple(int(color[i:i+2],16)/255 for i in (1,3,5))
 sp.insert_text((r.x0,r.y0+size),value,fontname=fontname,fontsize=size,color=rgb)
 pix=sp.get_pixmap(matrix=fitz.Matrix(4,4),alpha=True);a=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,4)
 ys,xs=np.where(a[:,:,3]>20);ink=fitz.Rect(xs.min()/4,ys.min()/4,(xs.max()+1)/4,(ys.max()+1)/4)
 key=next(line_keys);target=fitz.Rect(measured[key]['source_ink_bbox_pt']);sx=target.width/ink.width;sy=target.height/ink.height
 clip=ink+(-1,-1,1,1);dest=target+(-sx,-sy,sx,sy)
 p.show_pdf_page(dest,scratch,0,clip=clip,keep_proportion=False)
 records.append({'text':value,'bbox_pt':list(target),'font_pt_before_fit':size,'ink_scale':[sx,sy],'kind':'native_type_fitted_to_measured_source_ink','source_line':key,'font_shape_fidelity':'replacement_font_not_identical_to_raster'})
def rect(r,fill=None,stroke=None,w=.7,radius=None):p.draw_rect(fitz.Rect(r),fill=fill,color=stroke,width=w,radius=radius)
def line(y):p.draw_line((36,y),(560,y),color=N,width=1.5)
line(44)
text([80,125,515,151],s['name'],21.6,True,align='center');text([160,186.2,435,207],s['corporation'],11.39,True,align='center');p.draw_line((269,212),(327,212),color=P,width=.9)
rect([67,259,528,361],(.96,.97,.98),(.82,.85,.88),radius=6/102);text([86,274,510,294],'設置学科（2年制・商業実務専門課程）',12.5,True)
text([86,300,250,319],'■ 国際ビジネスAI科',11,True,color='#252b30');text([230,301,515,321],'AI活用 / データ分析 / グローバルビジネス実務',9,color='#59636d')
text([86,325,250,344],'■ 総合ビジネス科',11,True,color='#252b30');text([230,326,515,346],'販売・サービス / 経営 / 事務 / マーケティング / IT',9,color='#59636d')
rect([67,385,528,638],None,N,radius=6/253);rect([67,385,528,414],N,None,radius=6/29);text([80,392,515,411],'お問い合わせ・入学相談窓口',12,True,color='#ffffff',align='center')
text([91,436,500,453],'【お電話でのお問い合わせ】',10.5,True,color='#59636d');text([90.25,454.6,500,483],'TEL. '+s['tel'],18.86,True)
text([91,496,500,513],'【メールでのお問い合わせ】',10.5,True,color='#59636d');text([90.25,515.3,510,543],s['email'],12.47,True,color='#252b30')
text([91,551,510,570],'【学校所在地・交通アクセス】',10.5,True,color='#59636d');a=s['address'];address='〒'+a['postal_code']+' '+a['prefecture']+a['city']+a['line1'];text([91,570,515,588],address,8.2,color='#333333')
text([91,587,518,612],'JR・名鉄・近鉄・地下鉄「名古屋駅」太閤通口（西口）より徒歩10分',9.5,True,color='#ff2167')
text([90,676,505,697],'学校公式サイト・最新募集要項はこちら',11.5,True,align='center');text([90,695,505,714],s['url'],10,color='#59636d',align='center');text([90,755.85,505,785],'学びを、未来の力に。',14.4,True,align='center');line(799)
notice=['本パンフレットには、AIにより生成・加工した画像を使用しています。','実在の人物の写真を参考にした画像については、ご本人からAIによる生成・加工および掲載への同意を得ています。']
# Copy the source text values, baseline, point size and colour without importing hidden page content.
source=R/json.loads((B.parent/'receipts.json').read_text())[0]['path'];ref=fitz.open(source)
p.insert_font(fontname='MasterNotoR',fontfile=F+'/DTPRebuiltSansJPRegular.otf')
p.insert_font(fontname='EmbeddedHelveticaMetric',fontfile='/usr/share/fonts/opentype/urw-base35/NimbusSans-Regular.otf')
for block in ref[15].get_text('dict')['blocks']:
 if 'lines' not in block:continue
 for line_info in block['lines']:
  for span in line_info['spans']:
   value=span['text']
   if not ('Artificial' in value or value.startswith('本パンフレット') or value.startswith('実在の人物')):continue
   origin=fitz.Point(span['origin']);size=span['size'];color=tuple((span['color']>>shift&255)/255 for shift in (16,8,0))
   if 'Artificial' in value:
    p.insert_text(origin,value,fontsize=size,fontname='EmbeddedHelveticaMetric',color=color)
   else:
    f=fitz.Font(fontfile=F+'/DTPRebuiltSansJPRegular.otf');width=f.text_length(value,fontsize=size);sx=(span['bbox'][2]-span['bbox'][0])/width
    p.insert_text(origin,value,fontsize=size,fontname='MasterNotoR',color=color,morph=(origin,fitz.Matrix(sx,1)))
   records.append({'text':value,'bbox_pt':list(span['bbox']),'font_pt':size,'kind':'native_source_values_retypeset','source_origin_pt':list(origin)})
assert not p.get_images();assert all(c[1]!=0 and c[0]!=65533 for span in p.get_texttrace() for c in span['chars']);assert unicodedata.normalize('NFKC',s['name']) in unicodedata.normalize('NFKC',p.get_text())
path=B/'native-page-16-draft.pdf';raw=B/'inspection/native-page16-before-cmap.pdf';d.save(raw,garbage=4,deflate=True)
# Noto CJK shares a glyph between U+002D/U+2011 and U+0020/U+00A0.
# PyMuPDF chooses the latter aliases for ToUnicode. All replacement input
# above explicitly uses ASCII hyphens/spaces: restore those input codepoints.
# This changes extraction only, never the embedded glyphs or paint operators.
cmap_repairs=[]
with pikepdf.open(raw) as pdf:
 for obj in pdf.objects:
  if not isinstance(obj,pikepdf.Dictionary) or '/ToUnicode' not in obj:continue
  if 'DTPRebuiltSansJP' not in str(obj.get('/BaseFont','')):continue
  data=obj.ToUnicode.read_bytes()
  for cid,alias,original in [(b'000e',b'2011',b'002d'),(b'0001',b'00a0',b'0020')]:
   pattern=rb'(<'+cid+rb'>\s*)<'+alias+rb'>'
   data,n=re.subn(pattern,lambda m:m.group(1)+b'<'+original+b'>',data,flags=re.I)
   if n:cmap_repairs.append({'font':str(obj.BaseFont),'CID':cid.decode(),'alias':alias.decode(),'input_unicode':original.decode()})
  obj.ToUnicode.write(data)
 pdf.save(path,compress_streams=True)
check=fitz.open(path);p=check[0]
for expected in [s['email'],s['tel'],s['url'],address]:assert expected in p.get_text(),expected
p.get_pixmap(matrix=fitz.Matrix(150/72,150/72)).save(B/'inspection/native-page-16-draft.png')
(B/'native-page-16-structure.json').write_text(json.dumps({'status':'draft_not_for_submission','file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'images':0,'fonts':len(p.get_fonts()),'glyph_zero':0,'copy':records,'ToUnicode_input_alias_repairs':cmap_repairs,'source_facts':'company-data/facts/school.yaml','layout_review':'pending','CMYK_and_ICC':'pending'},ensure_ascii=False,indent=2)+'\n')
