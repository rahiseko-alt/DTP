"""Rebuild the adopted cover: exact people/photo pixels, editable publication type.

Only text-bearing wall/carpet regions are repaired with image_gen background
plates. The central group photograph is extracted, never regenerated.
"""
from pathlib import Path
import fitz,pikepdf,json,hashlib,numpy as np,yaml
from PIL import Image,ImageFilter
from decimal import Decimal
B=Path(__file__).resolve().parent;R=B.parents[2];A=B/'assets/cover';A.mkdir(parents=True,exist_ok=True)
row=json.loads((B.parent/'receipts.json').read_text())[0];source=R/row['path'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source)==row['asset']['sha256']
src=fitz.open(source);sp=src[0];xref=sp.get_images()[0][0];pix=fitz.Pixmap(src,xref);rgb=np.frombuffer(pix.samples,np.uint8).reshape(pix.height,pix.width,pix.n);assert rgb.shape==(3508,2480,3)
original=Image.fromarray(rgb);W,H=210*72/25.4,297*72/25.4;sx,sy=W/sp.rect.width,H/sp.rect.height
rawrect=sp.get_image_rects(xref)[0];ir=fitz.Rect(rawrect.x0*sx,rawrect.y0*sy,rawrect.x1*sx,rawrect.y1*sy)
def box(x0,y0,x1,y1):return fitz.Rect(ir.x0+x0*ir.width/2480,ir.y0+y0*ir.height/3508,ir.x0+x1*ir.width/2480,ir.y0+y1*ir.height/3508)
photo=original.crop((0,640,2480,2638));photo.save(A/'photo-untouched.png')
floor=original.crop((0,2638,2480,3508));floor.save(A/'floor-original.png')
original.crop((2479,640,2480,2638)).save(A/'photo-edge.png')
d=fitz.open();p=d.new_page(width=W,height=H);header=R/'shared/generated-assets/printpack-native-rebuild-20261111/cover-header-clean.png';clean_floor=R/'shared/generated-assets/printpack-native-rebuild-20261111/cover-floor-clean.png'
header_rect=fitz.Rect(0,0,W,box(0,0,2480,640).y1)
p.insert_image(header_rect,filename=str(header),keep_proportion=False)
photo_rect=box(0,640,2480,2638);p.insert_image(photo_rect,filename=str(A/'photo-untouched.png'),keep_proportion=False)
p.insert_image(fitz.Rect(photo_rect.x1,photo_rect.y0,W,photo_rect.y1),filename=str(A/'photo-edge.png'),keep_proportion=False)
floor_rect=box(0,2638,2480,3508)
# Extend only the photo's previously missing rightmost 0.148mm. No scaling of
# the central photograph and no regenerated face/hand/clothing pixels.
floor_base=fitz.Rect(0,floor_rect.y0,W,max(H,floor_rect.y1));p.insert_image(floor_base,filename=str(clean_floor),keep_proportion=False)
# A glyph-shaped patch produces visible ghost lettering even after removing
# white pixels. Repair the continuous people-free carpet region instead. Keep
# the original, text-free top edge and feather only before the first glyph.
alpha_row=np.clip((135-np.arange(870))/65,0,1)*255
alpha=np.repeat(alpha_row[:,None],2480,axis=1).astype('uint8');mask=fitz.Pixmap(fitz.csGRAY,2480,870,alpha.tobytes(),False).tobytes('png')
p.insert_image(floor_rect,filename=str(A/'floor-original.png'),mask=mask,keep_proportion=False)
fonts={'Title':'/usr/share/fonts/opentype/urw-base35/NimbusSans-Bold.otf','JPR':'/workspace/.dtp-tools/native-fonts/DTPRebuiltSansJPRegular.otf','JPB':'/workspace/.dtp-tools/native-fonts/DTPRebuiltSansJPBold.otf','Serif':'/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc'}
for name,file in fonts.items():p.insert_font(fontname='Cover'+name,fontfile=file)
records=[]
def insert_fitted(value,bounds,font,color):
 # Measure painted ink, not ascender metrics; retain text as embedded glyphs.
 fd=fitz.Font(fontfile=fonts[font]);tmp=fitz.open();tp=tmp.new_page(width=max(1200,fd.text_length(value,fontsize=100)+80),height=250);tp.insert_font(fontname='F',fontfile=fonts[font]);tp.insert_text((20,150),value,fontsize=100,fontname='F',color=color)
 px=tp.get_pixmap(alpha=True,matrix=fitz.Matrix(2,2));ar=np.frombuffer(px.samples,np.uint8).reshape(px.height,px.width,4);yy,xx=np.where(ar[:,:,3]>30);ink=fitz.Rect(xx.min()/2-20,yy.min()/2-150,(xx.max()+1)/2-20,(yy.max()+1)/2-150)
 target=box(*bounds);mx,my=target.width/ink.width,target.height/ink.height;origin=fitz.Point(target.x0-ink.x0*mx,target.y0-ink.y0*my)
 p.insert_text(origin,value,fontsize=100,fontname='Cover'+font,color=color,morph=(origin,fitz.Matrix(mx,my)))
 records.append({'text':value,'source_ink_pixels':bounds,'target_ink_pt':list(target),'font':font,'native':True})
def blue(value,roi,font):
 x0,y0,x1,y1=roi;a=rgb[y0:y1,x0:x1].astype(int);mask=(a[:,:,2]-a[:,:,0]>70)&(a[:,:,1]-a[:,:,0]>20)&(a[:,:,0]<100);yy,xx=np.where(mask);bounds=[int(xx.min()+x0),int(yy.min()+y0),int(xx.max()+1+x0),int(yy.max()+1+y0)];color=tuple(np.median(a[mask],axis=0)/255);insert_fitted(value,bounds,font,color)
school=yaml.safe_load((R/'company-data/facts/school.yaml').read_text());courses=yaml.safe_load((R/'company-data/facts/courses.yaml').read_text())['courses']
blue('AI BUSINESS’28',(60,50,2480,400),'Title');blue(school['name'],(0,400,1140,590),'JPB')
a=rgb[400:590,1140:1180].astype(int);m=(a[:,:,2]-a[:,:,0]>35)&(a[:,:,1]-a[:,:,0]>15)&(a[:,:,0]<100);yy,xx=np.where(m);p.draw_rect(box(int(xx.min()+1140),int(yy.min()+400),int(xx.max()+1141),int(yy.max()+401)),fill=tuple(np.median(a[m],axis=0)/255),color=None)
blue(' ／ '.join(c['name'] for c in courses),(1200,400,2480,500),'JPB')
blue('AI活用 / ビジネス実務 / データ分析 / グローバルビジネス / マーケティング / IT活用 /',(1200,500,2480,558),'JPB')
blue('プレゼンテーション / プロジェクト実習 / キャリア支援',(1200,558,2480,630),'JPB')
first=[[94,2793,331,3008],[385,2794,490,3005],[556,2793,722,3003],[773,2777,1004,3013],[1074,2824,1253,2980],[1336,2814,1474,2993],[1561,2791,1742,3005],[1800,2785,1987,3013]]
second=[[53,3074,372,3443],[380,3068,686,3443],[697,3186,929,3413],[946,3068,1239,3422],[1248,3070,1567,3443],[1615,3160,1833,3407],[1881,3141,2097,3421],[2145,3157,2339,3415],[2400,3135,2456,3423]]
for value,bounds in zip('AIを使いこなす',first):insert_fitted(value,bounds,'Serif',(1,1,1))
for value,bounds in zip('社会の主役になる！',second):insert_fitted(value,bounds,'Serif',(1,1,1))
file=B/'cover-native-draft.pdf';d.save(file,garbage=4,deflate=True)
with pikepdf.open(file,allow_overwriting_input=True) as pdf:
 a4=pikepdf.Array([0,0,Decimal(210)*72/Decimal('25.4'),Decimal(297)*72/Decimal('25.4')]);pg=pdf.pages[0]
 for key in ['/MediaBox','/CropBox','/TrimBox','/BleedBox','/ArtBox']:pg.obj[key]=a4
 for obj in pdf.objects:
  if isinstance(obj,pikepdf.Dictionary) and '/SMask' in obj:obj.SMask.ColorSpace=pikepdf.Name.DeviceGray
 pdf.save(file)
check=fitz.open(file);cp=check[0];cp.get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(A/'preview.png')
matches=[]
for item in cp.get_images():
 if item[2:4]==(2480,1998):
  q=fitz.Pixmap(check,item[0]);matches.append(q.samples==photo.tobytes())
assert matches and all(matches)
assert all(c[1]!=0 and c[0]!=65533 for s in cp.get_texttrace() for c in s['chars'])
report={'status':'draft_independent_review_pending','file':file.name,'sha256':sha(file),'source_sha256':sha(source),'source_normalization':[sx,sy],'source_image_matrix_A4':list(ir),'photo_crop_pixels':[0,640,2480,2638],'photo_decoded_equal':all(matches),'photo_regenerated':False,'photo_retouched':False,'photo_edge_extension_mm':(W-ir.x1)*25.4/72,'header_background':{'file':str(header.relative_to(R)),'sha256':sha(header),'method':'image_gen text removal, no people in input crop'},'floor_background':{'file':str(clean_floor.relative_to(R)),'sha256':sha(clean_floor),'method':'image_gen continuous people-free carpet repair; original top70px preserved, next65px feathered before first lettering; no glyph-shaped masks'},'publication_type':records,'live_text_chars':len(cp.get_text()),'glyph_zero':0,'limitations':['New embedded fonts reproduce measured ink bounds; exact raster letterform equivalence cannot be guaranteed.','RGB working master; CMYK conversion and final independent print preflight pending.']}
(B/'cover-native-draft.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['sha256','photo_decoded_equal','live_text_chars','glyph_zero']},ensure_ascii=False))
