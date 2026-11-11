"""Rebuild brochure P16 from editable type and vector geometry only; review draft."""
from pathlib import Path
import fitz,pikepdf,yaml,json,html,hashlib,unicodedata
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
def text(rect,value,size=10,bold=False,color='#24476b',align='left'):
 r=fitz.Rect(rect);h=f'<div style="font-family:NativeNoto;font-size:{size}pt;font-weight:{700 if bold else 400};color:{color};line-height:1.15;text-align:{align};margin:0;padding:0">{html.escape(value).replace(chr(10),"<br>")}</div>';spare,scale=p.insert_htmlbox(r,h,css=css,archive=fitz.Archive(F));assert scale>.999,(value,scale);records.append({'text':value,'bbox_pt':list(r),'font_pt':size,'kind':'native'})
def rect(r,fill=None,stroke=None,w=.7,radius=None):p.draw_rect(fitz.Rect(r),fill=fill,color=stroke,width=w,radius=radius)
def line(y):p.draw_line((36,y),(560,y),color=N,width=1.5)
line(44)
text([80,125,515,151],s['name'],21.6,True,align='center');text([160,188,435,207],s['corporation'],10.5,True,align='center');p.draw_line((269,212),(327,212),color=P,width=.9)
rect([67,259,528,361],(.96,.97,.98),(.82,.85,.88),radius=6/102);text([86,274,510,294],'設置学科（2年制・商業実務専門課程）',12.5,True)
text([86,300,250,319],'■ 国際ビジネスAI科',11,True,color='#252b30');text([230,301,515,321],'AI活用 / データ分析 / グローバルビジネス実務',9,color='#59636d')
text([86,325,250,344],'■ 総合ビジネス科',11,True,color='#252b30');text([230,326,515,346],'販売・サービス / 経営 / 事務 / マーケティング / IT',9,color='#59636d')
rect([67,385,528,638],None,N,radius=6/253);rect([67,385,528,414],N,None,radius=6/29);text([80,392,515,411],'お問い合わせ・入学相談窓口',12,True,color='#ffffff',align='center')
text([91,436,500,453],'【お電話でのお問い合わせ】',10.5,True,color='#59636d');text([91,457,500,483],'TEL. '+s['tel'],19,True)
text([91,496,500,513],'【メールでのお問い合わせ】',10.5,True,color='#59636d');text([91,518,510,543],s['email'],13,True,color='#252b30')
text([91,551,510,570],'【学校所在地・交通アクセス】',10.5,True,color='#59636d');a=s['address'];address='〒'+a['postal_code']+' '+a['prefecture']+a['city']+a['line1'];text([91,570,515,588],address,8.2,color='#333333')
text([91,587,518,612],'JR・名鉄・近鉄・地下鉄「名古屋駅」太閤通口（西口）より徒歩10分',9.5,True,color='#ff2167')
text([90,676,505,697],'学校公式サイト・最新募集要項はこちら',11.5,True,align='center');text([90,695,505,714],s['url'],10,color='#59636d',align='center');text([90,760,505,785],'学びを、未来の力に。',14,True,align='center');line(799)
notice=['本パンフレットには、AIにより生成・加工した画像を使用しています。','実在の人物の写真を参考にした画像については、ご本人からAIによる生成・加工および掲載への同意を得ています。']
# Preserve the original native English name, address and AI notice at their exact positions.
source=R/json.loads((B.parent/'receipts.json').read_text())[0]['path'];ref=fitz.open(source);xrefs=[i[0] for i in ref[15].get_images()]
with pikepdf.open(source) as q:
 for xref in xrefs:
  im=q.get_object(xref,0);im.write(b'')
  for k in list(im.keys()):
   if str(k)!='/Length':del im[k]
  im.Type=pikepdf.Name('/XObject');im.Subtype=pikepdf.Name('/Form');im.BBox=pikepdf.Array([0,0,1,1])
 q.save(B/'inspection/back-cover-native-source.pdf',compress_streams=True)
ref=fitz.open(B/'inspection/back-cover-native-source.pdf')
for clip in [fitz.Rect(195,151,400,169),fitz.Rect(65,802,570,837)]:p.show_pdf_page(clip,ref,15,clip=clip,keep_proportion=False)
assert not p.get_images();assert all(c[1]!=0 and c[0]!=65533 for span in p.get_texttrace() for c in span['chars']);assert unicodedata.normalize('NFKC',s['name']) in unicodedata.normalize('NFKC',p.get_text())
path=B/'native-page-16-draft.pdf';d.save(path,garbage=4,deflate=True);p.get_pixmap(matrix=fitz.Matrix(150/72,150/72)).save(B/'inspection/native-page-16-draft.png');(B/'native-page-16-structure.json').write_text(json.dumps({'status':'draft_not_for_submission','file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'images':0,'fonts':len(p.get_fonts()),'glyph_zero':0,'copy':records,'source_facts':'company-data/facts/school.yaml','layout_review':'pending','CMYK_and_ICC':'pending'},ensure_ascii=False,indent=2)+'\n')
