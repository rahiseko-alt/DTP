"""P8 native-type reconstruction draft. Not an approved print replacement."""
from pathlib import Path
import fitz,json,hashlib,subprocess,numpy as np,runpy
from PIL import Image
from collections import defaultdict
R=Path('/workspace/DTP'); B=Path(__file__).resolve().parent; A=B/'p8-assets';A.mkdir(exist_ok=True)
S=R/'books/prospectus-jp-isen-2028/work/teacher'; I=S/'page-08.png'
w,h=595.2755905511812,841.8897637795276;s=w/2480
D=fitz.open();p=D.new_page(width=w,height=h)
F=Path('/workspace/.dtp-tools/native-fonts'); fonts={}
for name,weight in [('R','Regular'),('B','Bold')]:
 file=F/f'DTPRebuiltSansJP{weight}.otf';p.insert_font(fontname='P8'+name,fontfile=str(file));fonts[name]=fitz.Font(fontfile=str(file))
records=[]
source_pixels=np.array(Image.open(I).convert('RGB'))
targets=defaultdict(list)
for value,roi,kind in runpy.run_path(str(B/'p8-ink-targets.py'))['TARGETS']:
 x0,y0,x1,y1=roi;crop=source_pixels[y0:y1,x0:x1]
 if kind=='white':mask=(crop.min(2)>190)
 else:mask=(crop[:,:,0]<140)&(crop[:,:,1]<160)&(crop[:,:,2]<190)
 yy,xx=np.where(mask);assert len(xx),(value,roi)
 targets[value].append([int(xx.min()+x0),int(yy.min()+y0),int(xx.max()+x0+1),int(yy.max()+y0+1)])
ink_cache={}
def font_ink(value,key):
 cachekey=(value,key)
 if cachekey not in ink_cache:
  temp=fitz.open();tp=temp.new_page(width=max(2000,fonts[key].text_length(value,fontsize=100)+100),height=300);tp.insert_font(fontname='Ink',fontfile=str(F/('DTPRebuiltSansJP'+('Bold' if key=='B' else 'Regular')+'.otf')));tp.insert_text((0,200),value,fontsize=100,fontname='Ink');px=tp.get_pixmap(colorspace=fitz.csGRAY);ar=np.frombuffer(px.samples,dtype=np.uint8).reshape(px.height,px.width);yy,xx=np.where(ar<160);ink_cache[cachekey]=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)];temp.close()
 return ink_cache[cachekey]

def rect(r,fill,stroke=None):p.draw_rect(fitz.Rect([v*s for v in r]),fill=fill,color=stroke,width=.35)
def text(x,y,t,px=48,bold=False,width=None,color=(.08,.1,.12),angle=0):
 key='B' if bold else 'R';size=px*s;point=fitz.Point(x*s,y*s);sx=1;sy=1;target=None
 if targets[t]:
  target=targets[t].pop(0);ink=font_ink(t,key);sx=(target[2]-target[0])/(ink[2]-ink[0]);sy=(target[3]-target[1])/(ink[3]-ink[1]);size=100*s
  point=fitz.Point((target[0]-ink[0]*sx)*s,(target[1]-(ink[1]-200)*sy)*s)
 elif width:sx=min(1,width*s/fonts[key].text_length(t,fontsize=size))
 mat=fitz.Matrix(sx,sy).prerotate(angle)
 p.insert_text(point,t,fontname='P8'+key,fontsize=size,color=color,morph=(point,mat));records.append({'text':t,'origin_pt':list(point),'font_pt':size,'horizontal_scale':sx,'vertical_scale':sy,'source_ink_bbox_px':target,'native':True})

def lines(x,y,items,px=48,step=65,**kw):
 for i,t in enumerate(items):text(x,y+i*step,t,px,**kw)
# Layout images use the exact adopted component; publication text is never inserted as an image.
p.insert_image(fitz.Rect(0,0,w,1322*s),filename=str(S/'background-extended.png'))
# Existing composite's measured placement and 70/50 px transition, applied as a PDF soft mask.
photo=R/'shared/generated-assets/jp-existing-photo-b-r01/B-PHOTO-R07-S02.png'; pix=fitz.Pixmap(str(photo));pw,ph=pix.width,pix.height
alpha=np.minimum(np.minimum(np.arange(pw)[None,:]/(70*pw/1960),np.ones((ph,1))),np.minimum(np.arange(ph)[:,None]/(50*pw/1960),np.ones((1,pw))));alpha=np.clip(alpha*255,0,255).astype('uint8')
mask=fitz.Pixmap(fitz.csGRAY,pw,ph,alpha.tobytes(),False).tobytes('png')
p.insert_image(fitz.Rect(520*s,275*s,2480*s,1322*s),filename=str(photo),mask=mask)
# Handwritten source font is unavailable: explicit unresolved fidelity issue, not a passed match.
lines(100,306,['AIを使いこなす力で、','学びも、仕事も、','もっと広がる。'],88,step=125,angle=12)
blue=(0,.31,.55) # Native sampled-function shading is installed after saving.
text(136,1526,'Google認定資格を持つ講師から、',161,True,2215,(1,1,1))
text(136,1767,'AIを実践的に学ぶ。',208,True,1870,(1,1,1))
lines(150,1885,['AIビジネス専門学校では、Google認定資格を持つ講師が、','最新のAIツールとGoogleのサービスを使い、実践的に指導します。','学校で学んだことを、将来の仕事にそのまま活かせる力を育てます。'],58,step=92,color=(1,1,1))
rect([60,2165,1220,2280],(.9,.96,1));rect([60,2165,78,2280],blue)
text(108,2250,'Google認定資格を持つ講師が指導',64,True,1100,blue)
lines(1295,2210,['教育の専門知識と最新のAI活用スキルを持つ講師が、','基礎から実践まで丁寧に教えます。'],45,step=65)
for x in [57,847,1680]:
 p.draw_rect(fitz.Rect(x*s,2330*s,(x+772)*s,3000*s),color=(.88,.91,.93),width=.8,radius=.02)
# Crop formal symbol marks only; all explanatory and title letters are retyped.
icons=[('g1',[160,2380,342,2570]),('g2',[955,2380,1140,2570]),('gem',[1770,2380,1960,2570]),('small-gem',[167,3150,318,3290]),('workspace',[485,3150,1035,3285]),('notebook',[1225,3155,1370,3290]),('canva',[1660,3125,1840,3310]),('chatgpt',[2135,3125,2310,3310])]
for name,r in icons:
 out=A/(name+'.png');subprocess.run(['magick',str(I),'-crop',f'{r[2]-r[0]}x{r[3]-r[1]}+{r[0]}+{r[1]}','+repage',str(out)],check=True)
 p.insert_image(fitz.Rect([v*s for v in r]),filename=str(out))
for x,title,level in [(400,'Google','レベル1'),(1210,'Google','レベル2'),(2030,'Gemini',None)]:
 lines(x,2409,[title,'認定教育者']+([level] if level else []),62,step=75,bold=True,color=blue)
for x,level in [(213,'Level 1'),(1000,'Level 2')]:lines(x,2655,['Google for Education','Certified Educator',level],45,step=50)
lines(1830,2675,['Google for Education','Gemini Educator'],45,step=52)
for x,items in [(90,['授業でGoogleツールを','活用するための基礎知識と','実践力を持つ教員の資格です。']),(914,['より高度なテクノロジー活用と','学習環境設計のスキルを持つ','教員の資格です。']),(1738,['教育における生成AI(Gemini)の','効果的な活用能力を持つ','教員の資格です。'])]:lines(x,2830,items,47,step=67)
rect([60,3040,548,3125],(0,.51,.69));text(112,3100,'主な使用ツール',57,True,color=(1,1,1));text(594,3100,'授業・課題・発表・学校生活の中で、さまざまなツールを使い学びます。',47,width=1690)
for x in [449,1080,1530,1980]:p.draw_line((x*s,3165*s),(x*s,3468*s),color=(.7,.85,.94),width=.7)
for x,label,width in [(163,'Gemini',185),(545,'Google Workspace',490),(1150,'NotebookLM',290),(2140,'ChatGPT',260)]:text(x,3357,label,57,True,width,blue if label in ['Gemini','Google Workspace'] else (.08,.1,.12))
for x,items,width in [(80,['生成AI','文章・画像・分析'],330),(490,['文書作成・資料作成','共同作業・データ管理'],540),(1120,['調査・情報整理','レポート作成'],360),(1575,['デザイン・画像作成','SNS・ポスター制作'],390),(2020,['情報収集・アイデア出し','文章作成・要約'],420)]:
 for i,t in enumerate(items):text(x,3420+i*65,t,46,width=width)
# Adopt the print-only build.py folio font, A4 position, point size and colour.
p.insert_font(fontname='PrintFolio',fontfile='/usr/share/fonts/opentype/urw-base35/NimbusSans-Bold.otf')
folio_rect=fitz.Rect(5*72/25.4,h-10*72/25.4,14*72/25.4,h-5*72/25.4)
assert p.insert_textbox(folio_rect,'8',fontsize=9,fontname='PrintFolio',color=(.25,.25,.25),align=0)>=0
records.append({'text':'8','source':'downloads/printpack-ready-20261028/build.py','rect_pt':list(folio_rect),'font_pt':9,'font':'NimbusSans-Bold','native':True})
file=B/'p8-native-draft.pdf';D.save(file,garbage=4,deflate=True);D.close()
import pikepdf
from decimal import Decimal
# Smooth native PDF shading, sampled only from blue background pixels, excluding white text.
ny,nx=9,17;colors=[]
for gy in np.linspace(2113,1322,ny):
 for gx in np.linspace(0,2479,nx):
  crop=source_pixels[max(1322,int(gy)-30):min(2114,int(gy)+31),max(0,int(gx)-40):min(2480,int(gx)+41)]
  pixels=crop.reshape(-1,3);pixels=pixels[(pixels[:,0]<45)&(pixels[:,1]<120)&(pixels[:,2]<190)]
  colors.extend(np.median(pixels,axis=0).astype('uint8').tolist())
with pikepdf.open(file,allow_overwriting_input=True) as pdf:
 fun=pdf.make_stream(bytes(colors));fun.FunctionType=0;fun.Domain=pikepdf.Array([0,1,0,1]);fun.Range=pikepdf.Array([0,1,0,1,0,1]);fun.Size=pikepdf.Array([nx,ny]);fun.BitsPerSample=8;fun.Order=1
 shade=pdf.make_indirect(pikepdf.Dictionary(ShadingType=1,ColorSpace=pikepdf.Name.DeviceRGB,Domain=pikepdf.Array([0,1,0,1]),Matrix=pikepdf.Array([w,0,0,(2114-1322)*s,0,h-2114*s]),Function=fun))
 page=pdf.pages[0]
 a4=pikepdf.Array([0,0,Decimal('595.2755905511811023622047244'),Decimal('841.8897637795275590551181102')])
 for box in ['/MediaBox','/CropBox','/TrimBox','/BleedBox','/ArtBox']:page.obj[box]=a4
 for xobject in page.Resources.XObject.values():
  if '/SMask' in xobject:xobject.SMask.ColorSpace=pikepdf.Name.DeviceGray
 page.Resources.Shading=pikepdf.Dictionary(P8Blue=shade);page.contents_add(pdf.make_stream(b'q /P8Blue sh Q\n'),prepend=True);pdf.save(file)
D=fitz.open(file);p=D[0];p.get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(A/'preview.png')
report={'status':'incomplete_fidelity_review_required_not_for_submission','pdf':file.name,'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'native_character_count':len(p.get_text()),'raster_publication_letters_intended':False,'known_issues':['Source handwritten font unavailable: substituted Noto font is visibly different.','Typography widths/positions measured manually and require strict visual correction.','Blue background is rebuilt as smooth native sampled-function shading from measured text-free blue pixels; minor texture is not reproduced.','Formal logo crops retain raster official symbol shapes (Canva includes wordmark).','Soft mask composition uses original adopted photo and existing clean background; exact raster comparison pending.'],'text':records}
(B/'p8-rebuild-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
