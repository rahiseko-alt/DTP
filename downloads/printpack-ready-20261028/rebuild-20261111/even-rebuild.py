"""Reconstruct P2/4/6 with native type/geometry and narrowly repaired photographs.

Draft, not a release approval. Coordinates follow the original image matrix and
the print build's source-page -> A4 normalization (no new photo resizing).
"""
from pathlib import Path
import json,hashlib,io,re,unicodedata
import fitz,pikepdf,numpy as np
from PIL import Image

B=Path(__file__).resolve().parent; R=Path('/workspace/DTP'); A=B/'assets/even';A.mkdir(parents=True,exist_ok=True)
source=R/json.loads((B.parent/'receipts.json').read_text())[0]['path'];src=fitz.open(source)
assert hashlib.sha256(source.read_bytes()).hexdigest()=='a856ca0aa6fef7099f47e9a3d81c679b8640a190f2d97577d03ece7561a1ab74'
W,H=210*72/25.4,297*72/25.4
STORE=R/'shared/generated-assets/printpack-native-rebuild-20261111/even'
REPAIR={2:(str(STORE/'repair-02-wide.png'),[0,0,2480,2300]),4:(str(STORE/'repair-04.png'),[0,590,1070,1470]),6:(str(STORE/'repair-06.png'),[0,350,970,1300])}
PATCH={2:[[90,850,1470,1490],[90,1450,1160,1720],[90,1680,1100,2300],[1700,1400,2420,2300]],4:[[80,730,1030,1450],[70,0,770,280]],6:[[130,500,970,1300],[80,0,770,280]]}
CUT={2:2300,4:1580,6:1500}
fonts={'R':'/workspace/.dtp-tools/native-fonts/DTPRebuiltSansJPRegular.otf','B':'/workspace/.dtp-tools/native-fonts/DTPRebuiltSansJPBold.otf','S':'/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc'}
reports=[];out=fitz.open()

# Preserve original native edits, their backgrounds, glyphs and placement. The
# full-page raster image is removed, never reused as a page background.
with pikepdf.open(source) as clean:
 for n in [2,4,6]:
  # The original raster carrier also paints an opaque full-page white base.
  # Remove that carrier stream, leaving the separately appended native edits.
  names={info[7] for info in src[n-1].get_images()}
  page=clean.pages[n-1];streams=list(page.obj.Contents)
  page.obj.Contents=pikepdf.Array([stream for stream in streams if not any(('/'+name+' Do').encode() in stream.read_bytes() for name in names)])
  for info in src[n-1].get_images():
   obj=clean.get_object(info[0],0);obj.write(b'')
   for key in list(obj.keys()):
    if str(key)!='/Length':del obj[key]
   obj.Type=pikepdf.Name('/XObject');obj.Subtype=pikepdf.Name('/Form');obj.BBox=pikepdf.Array([0,0,1,1])
 clean.save(A/'native-overlays.pdf')
overlay=fitz.open(A/'native-overlays.pdf')

for n in [2,4,6]:
 sp=src[n-1];main=max(sp.get_images(),key=lambda i:i[2]*i[3]);ir=sp.get_image_rects(main[0])[0]
 sx=W/sp.rect.width;sy=H/sp.rect.height;mx=ir.width*sx/2480;my=ir.height*sy/3508;ox=ir.x0*sx;oy=ir.y0*sy
 original_path=A/f'original-full-{n:02}.png'
 if not original_path.exists():fitz.Pixmap(src,main[0]).save(original_path)
 im=Image.open(original_path).convert('RGB');pixels=np.array(im);p=out.new_page(width=W,height=H);records=[]
 rendered=sp.get_pixmap(matrix=fitz.Matrix(2480/sp.rect.width,3508/sp.rect.height),alpha=False);ink_pixels=np.frombuffer(rendered.samples,np.uint8).reshape(rendered.height,rendered.width,rendered.n)[:3508,:2480,:3]
 norm=lambda value:re.sub(r'\s+','',unicodedata.normalize('NFKC',value))
 existing_native_lines=[(norm(span['text']),fitz.Rect(span['bbox'])*fitz.Matrix(sx,sy)) for block in sp.get_text('dict')['blocks'] for line_info in block.get('lines',[]) for span in line_info['spans']]
 def rr(box):return fitz.Rect(ox+box[0]*mx,oy+box[1]*my,ox+box[2]*mx,oy+box[3]*my)
 def rect(box,fill,stroke=None,radius=None):
  area=rr(box)
  if box[0]==0 and box[2]==2480:area.x0=0;area.x1=W
  p.draw_rect(area,color=stroke,fill=fill,width=.35,radius=radius)
 def line(a,b,color,width=.6):p.draw_line((ox+a[0]*mx,oy+a[1]*my),(ox+b[0]*mx,oy+b[1]*my),color=color,width=width)
 def gradient(box,top,bottom):
  area=rr(box)
  if box[0]==0 and box[2]==2480:area.x0=0;area.x1=W
  gd=pikepdf.Pdf.new();gp=gd.add_blank_page(page_size=(area.width,area.height));function=pikepdf.Dictionary(FunctionType=2,Domain=[0,1],C0=[float(v) for v in bottom],C1=[float(v) for v in top],N=1)
  shading=pikepdf.Dictionary(ShadingType=2,ColorSpace=pikepdf.Name('/DeviceRGB'),Coords=[0,0,0,area.height],Function=function,Extend=[True,True])
  gp.obj.Resources=pikepdf.Dictionary(Shading=pikepdf.Dictionary(G=shading));gp.obj.Contents=pikepdf.Stream(gd,b'/G sh')
  buf=io.BytesIO();gd.save(buf);gdoc=fitz.open(stream=buf.getvalue(),filetype='pdf');p.show_pdf_page(area,gdoc,0,keep_proportion=False)
 def sample(x,y):return tuple(pixels[y,x,:3]/255)
 def image_crop(image,box):
  buf=io.BytesIO();image.crop(tuple(box)).save(buf,format='PNG');return buf.getvalue()
 # Repaired crop appears only in approved publication-letter regions. Original
 # face/hair/body pixels outside those rectangles are extracted losslessly.
 repair_path,repair_rect=REPAIR[n]
 # Compose a PHOTO-only cache, not a page screenshot. The edit was performed by
 # image_gen. This composition restores the unedited original pixels outside
 # the approved continuous restoration regions and feathers only their edges.
 pd=fitz.open();pp=pd.new_page(width=2480,height=CUT[n]);pp.insert_image(pp.rect,stream=image_crop(im,[0,0,2480,CUT[n]]),keep_proportion=False)
 layers=[(repair_path,repair_rect,PATCH[n])]
 if n==2:layers=[(repair_path,repair_rect,[PATCH[n][-1]]),(str(STORE/'repair-02-left.png'),[0,850,1470,2300],PATCH[n][:-1])]
 for layer_path,layer_rect,patches in layers:
  gp=fitz.Pixmap(layer_path);gw,gh=gp.width,gp.height
  xx=layer_rect[0]+(np.arange(gw)+.5)*(layer_rect[2]-layer_rect[0])/gw;yy=layer_rect[1]+(np.arange(gh)+.5)*(layer_rect[3]-layer_rect[1])/gh
  alpha=np.zeros((gh,gw),dtype=float)
  for patch in patches:
   if n in [4,6] and patch[1]==0:continue
   distance=np.minimum(np.minimum(xx[None,:]-patch[0],patch[2]-xx[None,:]),np.minimum(yy[:,None]-patch[1],patch[3]-yy[:,None]))
   alpha=np.maximum(alpha,np.clip(distance/24,0,1))
  mask=fitz.Pixmap(fitz.csGRAY,gw,gh,(alpha*255).astype('uint8').tobytes(),False).tobytes('png')
  pp.insert_image(fitz.Rect(layer_rect),filename=layer_path,mask=mask,keep_proportion=False)
 for patch in PATCH[n]:
  if n in [4,6] and patch[1]==0:pp.draw_rect(fitz.Rect(patch),color=None,fill=(1,1,1))
 photo=pp.get_pixmap(colorspace=fitz.csRGB,alpha=False);photo_path=A/f'clean-photo-{n:02}.png';photo.save(photo_path)
 photo_rect=rr([0,0,2480,CUT[n]])
 p.insert_image(photo_rect,filename=str(photo_path),keep_proportion=False)
 # Keep the original placement; fill only the original carrier's sub-millimetre
 # outer shortfall with its nearest photo edge pixels. Never stretch the photo.
 cache_image=Image.open(photo_path)
 if photo_rect.x1<W:p.insert_image(fitz.Rect(photo_rect.x1,photo_rect.y0,W,photo_rect.y1),stream=image_crop(cache_image,[2479,0,2480,CUT[n]]),keep_proportion=False)
 if photo_rect.y0>0:p.insert_image(fitz.Rect(0,0,W,photo_rect.y0),stream=image_crop(cache_image,[0,0,2480,1]),keep_proportion=False)
 photo_pixels=np.frombuffer(photo.samples,dtype=np.uint8).reshape(photo.height,photo.width,3)
 protected=np.ones((CUT[n],2480),dtype=bool)
 # Image-mask interpolation may affect a one-pixel fringe at the crop edge.
 # Declare a two-pixel restoration halo and require exact identity beyond it.
 for x0,y0,x1,y1 in PATCH[n]:protected[max(0,y0-2):min(CUT[n],y1+2),max(0,x0-2):min(2480,x1+2)]=False
 photo_diff=np.any(photo_pixels!=pixels[:CUT[n]],axis=2)
 assert not np.any(photo_diff & protected),'Unchanged photo outside repair+2px interpolation halo differs'
 xs=sorted({0,2480,*[v for r in PATCH[n] for v in (r[0],r[2])]});ys=sorted({0,CUT[n],*[v for r in PATCH[n] for v in (r[1],r[3]) if 0<=v<=CUT[n]]})
 tiles=[]
 for y0,y1 in zip(ys,ys[1:]):
  for x0,x1 in zip(xs,xs[1:]):
   cx=(x0+x1)/2;cy=(y0+y1)/2
   if any(r[0]<=cx<r[2] and r[1]<=cy<r[3] for r in PATCH[n]):continue
   box=[x0,y0,x1,y1];tiles.append({'box_px':box,'decoded_rgb_sha256':hashlib.sha256(im.crop(tuple(box)).tobytes()).hexdigest()})
 for key,file in fonts.items():p.insert_font(fontname='Even'+key,fontfile=file)
 ink_cache={}
 def text(value,box,key='R',color=(.08,.1,.12),kind='dark',measure=True,angle=0):
  area=rr(box)+(-2,-2,2,2)
  if any(norm(value)==v and area.contains(fitz.Point((r.x0+r.x1)/2,(r.y0+r.y1)/2)) for v,r in existing_native_lines):return
  target=box[:]
  if measure and not angle:
   x0,y0,x1,y1=map(int,box);a=ink_pixels[y0:y1,x0:x1]
   if kind=='white':mask=a.min(2)>200
   elif kind=='blue':mask=(a[:,:,0]<120)&(a[:,:,2]>a[:,:,0]+25)&(a[:,:,1]<190)
   elif kind=='green':mask=(a[:,:,0]<145)&(a[:,:,1]>a[:,:,0]+10)&(a[:,:,2]<145)
   elif kind=='orange':mask=(a[:,:,0]>160)&(a[:,:,1]<150)&(a[:,:,2]<120)
   elif kind=='deepblack':mask=a.max(2)<75
   else:mask=(a.min(2)<130)&(a.max(2)<190)&((a.max(2).astype(int)-a.min(2).astype(int))<60)
   yy,xx=np.where(mask)
   if len(xx):target=[int(xx.min()+x0),int(yy.min()+y0),int(xx.max()+1+x0),int(yy.max()+1+y0)]
  ck=(value,key)
  if ck not in ink_cache:
   f=fitz.Font(fontfile=fonts[key]);tmp=fitz.open();tp=tmp.new_page(width=max(1500,f.text_length(value,fontsize=50)+50),height=150);tp.insert_font(fontname='Ink',fontfile=fonts[key]);tp.insert_text((10,100),value,fontname='Ink',fontsize=50);pix=tp.get_pixmap(colorspace=fitz.csGRAY);a=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width);yy,xx=np.where(a<150);ink_cache[ck]=[xx.min()-10,yy.min()-100,xx.max()+1-10,yy.max()+1-100]
  ink=ink_cache[ck];tr=rr(target);fx=tr.width/(ink[2]-ink[0]);fy=tr.height/(ink[3]-ink[1]);origin=fitz.Point(tr.x0-ink[0]*fx,tr.y0-ink[1]*fy)
  mat=fitz.Matrix(fx,fy).prerotate(angle);p.insert_text(origin,value,fontname='Even'+key,fontsize=50,color=color,morph=(origin,mat))
  records.append({'text':value,'target_ink_box_px':target,'native':True,'font':key,'photo_handwritten_approximation':bool(angle or key=='S')})
 def check(x,y,col,size=65):
  rect([x,y,x+size,y+size],col,radius=.04);line((x+size*.18,y+size*.49),(x+size*.42,y+size*.76),(1,1,1),1);line((x+size*.42,y+size*.76),(x+size*.84,y+size*.18),(1,1,1),1)
 def checkbox_lines(items,x,y,col,step=91,size=61):
  for j,value in enumerate(items):
   yy=y+j*step;check(x,yy,col);text(value,[x+85,yy-4,2420 if x>1200 else 1210,yy+size],measure=True)
 if n==2:
  green=tuple(np.median(pixels[2380:2490,130:150,:].reshape(-1,3),axis=0)/255)
  # Complex photographic glow is retained in the repaired photograph; blocks,
  # rules and typography are separate editable/native publication elements.
  for value,box in [('ゼロから',[110,850,800,1045]),('AIを使いこなす',[110,1045,1350,1250]),('社会の主役にする。',[110,1250,1490,1450]),('教育システム。',[110,1450,1170,1650])]:text(value,box,'S',kind='deepblack')
  rect([1700,1400,2420,2250],(.92,.95,.85));text('2026年4月開校',[1760,1445,2370,1545],'B',green,'green');text('2学科・2年制',[1760,1550,2350,1645],'B',green,'green');text('商業実務専門課程',[1760,1650,2390,1740],'B',green,'green');line((1760,1770),(2380,1770),green,.4)
  text('年間入学定員',[1770,1810,2320,1880],'B',green,'green');text('59',[1760,1885,2180,2210],'B',green,'green');text('名',[2190,2060,2375,2200],'B',green,'green')
  rect([0,2300,2480,3508],(.98,.98,.97));rect([125,2370,2400,2545],(.91,.94,.85));rect([125,2370,1655,2510],green)
  text('AI人材としての「基礎」を育てる',[145,2380,1645,2500],'B',(1,1,1),'white')
  rect([125,2550,2400,2650],(.96,.97,.94));line((835,2710),(835,3070),(.78,.83,.73));line((1670,2710),(1670,3070),(.78,.83,.73));line((125,3090),(2390,3090),(.78,.83,.73));line((1040,3140),(1040,3460),(.78,.83,.73))
  text('実践重視の学び',[125,2700,800,2785],'B',green,'green');text('AI活用教育',[1785,2700,2390,2785],'B',green,'green')
  for value,box in [('PBL・発表・アウトプット中心',[125,2800,800,2865]),('の授業で、学んだことを形に',[125,2880,800,2945]),('します。',[125,2960,500,3025]),('生成AIの基本利用から、',[1785,2800,2390,2870]),('画像生成・データ分析・',[1785,2885,2390,2950]),('業務での活用まで学びます。',[1785,2970,2390,3040])]:text(value,box)
  text('ITスキル',[125,3098,1000,3188],'B',green,'green');text('キャリア支援',[1140,3098,2390,3190],'B',green,'green')
  for value,box in [('ITスキルⅠ・ITで、ITパスポート',[125,3205,1050,3275]),('やOffice活用につながる',[125,3287,1000,3357]),('基礎を学びます。',[125,3367,1000,3436]),('就職指導・キャリアガイダンスにより、',[1140,3220,2390,3289]),('卒業後の進路づくりを支えます。',[1140,3302,2390,3373])]:text(value,box)
 else:
  blue=tuple(np.median(pixels[1700:2400,10:40,:].reshape(-1,3),axis=0)/255);light=(.88,.94,.98) if n==4 else (1,.92,.87);top=1580 if n==4 else 1500
  rect([70,0,770,280],light);rect([70,0,770,165],blue)
  text('2年制',[210,10,630,145],'B',(1,1,1),'white');text('国際ビジネスAI科' if n==4 else '総合ビジネス科',[180,190,690,250],'B',blue,'blue' if n==4 else 'orange')
  scripts=([('AIで、',[130,720,550,850]),('世界とつながる。',[100,880,1000,1030]),('もっと広い',[140,1050,800,1210]),('未来へ。',[140,1240,630,1420])] if n==4 else [('学んだスキルで',[180,590,930,740]),('仕事ができる。',[180,780,930,920]),('自分の未来が',[180,960,900,1110]),('見えてくる。',[180,1140,800,1290])])
  for value,box in scripts:text(value,box,'R',(1,1,1) if n==4 else (.03,.03,.03),measure=False,angle=6 if n==4 else 8)
  ctop=np.median(pixels[top+10:top+50,10:40,:].reshape(-1,3),axis=0)/255;cbottom=np.median(pixels[2680:2720,10:40,:].reshape(-1,3),axis=0)/255
  gradient([0,top,2480,2735],ctop,cbottom)
  text('ビジネス分野',[940,top+25,1560,top+110],'B',(1,1,1),'white');text('国際ビジネスAI科' if n==4 else '総合ビジネス科',[135,top+130,2345,top+390],'B',(1,1,1),'white')
  if n==4:text('AIを活用し、国際ビジネスの現場で活躍できる力を身につける学科です。',[145,top+440,2370,top+515],'R',(1,1,1),'white')
  cy=2140 if n==4 else 2115
  for x in [100,890,1680]:rect([x,cy,x+750,cy+285],(1,1,1),radius=.03)
  # Native simple line icons: no raster letter/icon components.
  if n==4:
   rect([155,cy+80,280,cy+210],None,blue);text('AI',[175,cy+110,265,cy+175],'B',blue,measure=False)
   for y in range(cy+70,cy+230,35):line((130,y),(155,y),blue);line((280,y),(305,y),blue)
   p.draw_circle((ox+1040*mx,oy+(cy+145)*my),70*mx,color=blue,width=.8)
   p.draw_oval(rr([1005,cy+75,1075,cy+215]),color=blue,width=.6);line((970,cy+145),(1110,cy+145),blue);line((985,cy+105),(1095,cy+105),blue);line((985,cy+185),(1095,cy+185),blue)
   for x,y in [(1815,cy+105),(1900,cy+100)]:p.draw_circle((ox+x*mx,oy+y*my),25*mx,color=blue,width=.7);p.draw_oval(rr([x-38,y+30,x+38,y+105]),color=blue,width=.7)
   cards=[('AI活用',355,['生成AI・画像生成','データ分析・AIツール']),('異文化理解',1970,['多文化共生','グローバルマインド'])]
  else:
   for pts in [[(160,cy+225),(180,cy+90),(285,cy+90),(305,cy+225),(160,cy+225)]]:
    for aa,bb in zip(pts,pts[1:]):line(aa,bb,blue,1.2)
   p.draw_oval(rr([200,cy+35,265,cy+125]),color=blue,width=1)
   for x,hh in [(965,85),(1010,120),(1055,170)]:rect([x,cy+225-hh,x+25,cy+225],blue)
   line((955,cy+100),(1090,cy+35),blue,1.1);line((1090,cy+35),(1070,cy+80),blue,1.1)
   rect([1765,cy+50,1900,cy+235],None,blue)
   for yy in [cy+95,cy+130,cy+165,cy+200]:line((1790,yy),(1875,yy),blue,1)
   cards=[('販売・サービス',410,['接客・店舗運営','顧客対応']),('経営',1200,['ビジネス基礎','経営の考え方']),('事務',2020,['PC・書類作成','ビジネス実務'])]
  for title,x,body in cards:
   edge=min(x+400,2400)
   text(title,[x,cy+35,edge,cy+115],'B',blue,'blue' if n==4 else 'orange')
   for j,value in enumerate(body):text(value,[x,cy+120+j*75,edge,cy+190+j*75],color=blue if n==4 else (.08,.1,.12),kind='blue' if n==4 else 'dark')
  rect([100,cy+315,2430,2735],light);line((1270,cy+335),(1270,2715),blue,.5)
  # Original native duration/capacity correction below is imported unchanged.
  rect([0,2735,2480,3508],(1,1,1));rect([100,2790,1190,2910],light);rect([1285,2790,2390,2910],light);line((1240,2785),(1240,3480),(.78,.84,.87) if n==4 else (.98,.62,.42),.5)
  hy0,hy1=(2810,2900) if n==4 else (2750,2890)
  text('目指せる資格・検定',[135,hy0,1170,hy1],'B',blue,'blue' if n==4 else 'orange');text('こんな人におすすめ',[1320,hy0,2370,hy1],'B',blue,'blue' if n==4 else 'orange')
  if n==4:
   # Text of the left qualification list is native in the accepted source.
   for j,value in enumerate(['AIを使って仕事がしたい','海外と関わる仕事に興味がある','いろいろな国の人と働きたい','AIとビジネスを一緒に学びたい','グローバルに活躍したい']):
    yy=2960+j*91;check(1375,yy,blue)
    if j!=3:text(value,[1470,yy-5,2420,yy+75])
  else:
   for j,value in enumerate(['仕事で役立つ力を身につけたい','販売・サービスの仕事に興味がある','事務やパソコンスキルを学びたい','将来、自分のお店や会社をつくりたい','さまざまな分野を広く学びたい','安定した就職を目指したい']):
    yy=[2900,2986,3071,3156,3242,3329][j];check(1335,yy,blue)
    if j!=0:text(value,[1430,yy-5,2420,yy+75])
 # Import original native edits with precisely the print build's A4 matrix.
 p.show_pdf_page(p.rect,overlay,n-1,keep_proportion=False)
 # Print-build folio is separate from the raster page's obsolete folio.
 p.insert_font(fontname='Folio',fontfile='/usr/share/fonts/opentype/urw-base35/NimbusSans-Bold.otf');p.insert_textbox(fitz.Rect(5*72/25.4,287*72/25.4,12*72/25.4,292*72/25.4),str(n),fontsize=9,fontname='Folio',color=(.25,.25,.25))
 reports.append({'source_page':n,'native_copy':records,'original_image_rect_source_pt':list(ir),'source_page_size_pt':list(sp.rect),'normalization':[sx,sy],'photo_pixel_matrix_to_A4':[mx,my,ox,oy],'original_tiles':tiles,'photo_cache':str(photo_path.relative_to(R)),'original_photo_pixels_outside_restoration_unchanged':True,'changed_original_photo_pixels':int(photo_diff.sum()),'repair_image':repair_path,'repair_coordinates_px':repair_rect,'repair_visible_areas_px':PATCH[n],'source_faces_outside_repair_regions_original_pixels':True,'limitations':['Handwritten and other image glyph shapes are approximated with embedded fonts.','Restoration patches require independent photo-fidelity and seam review.','CMYK conversion and complete-book integration not yet performed.']})

path=B/'even-native-draft.pdf';raw=A/'even-before-cmap.pdf';out.save(raw,garbage=4,deflate=True)
with pikepdf.open(raw) as pdf:
 for obj in pdf.objects:
  if not isinstance(obj,pikepdf.Dictionary) or '/ToUnicode' not in obj or 'DTPRebuiltSansJP' not in str(obj.get('/BaseFont','')):continue
  data=obj.ToUnicode.read_bytes();data=re.sub(rb'(<000e>\s*)<2011>',rb'\g<1><002d>',data,flags=re.I);data=re.sub(rb'(<0001>\s*)<00a0>',rb'\g<1><0020>',data,flags=re.I);obj.ToUnicode.write(data)
 pdf.save(path,compress_streams=True)
check=fitz.open(path)
for i,p in enumerate(check):
 assert len(p.get_text())>100
 assert all(c[1]!=0 and c[0]!=65533 for span in p.get_texttrace() for c in span['chars'])
 p.get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(A/f'preview-{[2,4,6][i]:02}.png')
 reports[i]['native_text_chars']=len(p.get_text());reports[i]['image_count']=len(p.get_images());reports[i]['fonts']=len(p.get_fonts())
(B/'even-rebuild-report.json').write_text(json.dumps({'status':'DRAFT_REQUIRES_INDEPENDENT_REVIEW','source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'pages':reports},ensure_ascii=False,indent=2)+'\n')
print(path,hashlib.sha256(path.read_bytes()).hexdigest())
