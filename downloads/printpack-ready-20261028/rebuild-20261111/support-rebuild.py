"""Reconstruct P10/P11 using adopted photo crops, native structure and native type.
Working drafts only: font shape and local background fidelity require independent review.
"""
from pathlib import Path
import fitz,pikepdf,json,hashlib,numpy as np,subprocess,io,re
from decimal import Decimal
import unicodedata
from scipy.ndimage import gaussian_filter
from PIL import Image
import shutil
B=Path(__file__).resolve().parent;R=Path('/workspace/DTP');A=B/'support-assets';A.mkdir(exist_ok=True)
STORE=R/'shared/generated-assets/printpack-native-rebuild-20261111/support'
for generated in STORE.glob('*.png'):
 if not (A/generated.name).exists():shutil.copyfile(generated,A/generated.name)
S=R/'books/prospectus-jp-isen-2028/work/support';rows=json.loads((B.parent/'receipts.json').read_text());source=R/rows[0]['path'];ref=fitz.open(source)
legacy=json.loads((R/'system/assets/legacy-baseline.json').read_text())['files'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inputs={}
for p in S.glob('*.png'):
 rel=str(p.relative_to(R))
 if rel in legacy:assert sha(p)==legacy[rel],rel
inputs['provenance']='Legacy-baseline photo components; not falsely claimed as registered managed assets. Canonical document resolve succeeded; guessed variant jp-existing-photo search NO_MATCH; no substitute chosen.'
with pikepdf.open(source) as pdf:
 for page in pdf.pages:
  for x in page.Resources.get('/XObject',{}).values():
   if x.get('/Subtype')==pikepdf.Name.Image:
    x.write(b'')
    for k in list(x.keys()):
     if str(k)!='/Length':del x[k]
    x.Type=pikepdf.Name.XObject;x.Subtype=pikepdf.Name.Form;x.BBox=pikepdf.Array([0,0,1,1])
 pdf.save(A/'source-native-only.pdf')
native=fitz.open(A/'source-native-only.pdf');D=fitz.open();records=[];photo_records=[]
source_font_cache={}
def copy_native_type(page_index,area,target):
 # Import only the actual selected text, not an entire clipped source page:
 # clipped page imports retain many invisible duplicate copies of the header.
 page=native[page_index];candidates=[]
 for info in page.get_fonts():
  if info[0] not in source_font_cache:
   data=native.extract_font(info[0])[3]
   if data:
    try:source_font_cache[info[0]]=(data,fitz.Font(fontbuffer=data),info[3].split('+')[-1])
    except Exception:source_font_cache[info[0]]=None
   else:source_font_cache[info[0]]=None
  item=source_font_cache[info[0]]
  if item:candidates.append((info[0],*item))
 for block in page.get_text('dict')['blocks']:
  for ln in block.get('lines',[]):
   for span in ln['spans']:
    bb=fitz.Rect(span['bbox']);center=fitz.Point((bb.x0+bb.x1)/2,(bb.y0+bb.y1)/2)
    if not area.contains(center):continue
    value=unicodedata.normalize('NFKC',span['text']);color=tuple((span['color']>>s&255)/255 for s in (16,8,0));origin=fitz.Point(span['origin']);size=span['size']
    chosen=next((x for x in candidates if x[3]==span['font'] and all(x[2].has_glyph(ord(c)) for c in value)),None)
    if chosen:
     fid,data,font,_=chosen;name='PatchFont'+str(fid);target.insert_font(fontname=name,fontbuffer=data)
    else:
     fontfile='/usr/share/fonts/opentype/urw-base35/NimbusSans-Regular.otf' if span['font']=='Helvetica' else str(fontfiles['B' if span['flags']&16 else 'R']);name='PatchFallback'+('Helvetica' if span['font']=='Helvetica' else ('Bold' if span['flags']&16 else 'Regular'));target.insert_font(fontname=name,fontfile=fontfile);font=fitz.Font(fontfile=fontfile)
    width=font.text_length(value,fontsize=size);scale=bb.width/width if width else 1
    target.insert_text(origin,value,fontname=name,fontsize=size,color=color,morph=(origin,fitz.Matrix(scale,1)))
fontdir=Path('/workspace/.dtp-tools/native-fonts');fontfiles={'R':fontdir/'DTPRebuiltSansJPRegular.otf','B':fontdir/'DTPRebuiltSansJPBold.otf'};fonts={k:fitz.Font(fontfile=str(v)) for k,v in fontfiles.items()}
navy=(.025,.20,.36);blue=(.10,.37,.56)
for pn in [10,11]:
 sp=ref[pn-1];ir=sp.get_image_rects(sp.get_images()[0][0])[0];p=D.new_page(width=sp.rect.width,height=sp.rect.height);pix=fitz.Pixmap(ref,sp.get_images()[0][0]);arr=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,pix.n);im=Image.fromarray(arr[:,:,:3]);old=np.array(Image.open(S/f'page-{pn}.png').convert('RGB'))
 def pt(x,y):return fitz.Point(ir.x0+x*ir.width/2480,ir.y0+y*ir.height/3508)
 def rect(r):return fitz.Rect(pt(r[0],r[1]),pt(r[2],r[3]))
 def box(r,color,stroke=None,radius=0):p.draw_rect(rect(r),fill=color,color=stroke,width=.5,radius=radius or None)
 def crop(r,name,img=im):
  path=A/f'p{pn}-{name}.png';img.crop(tuple(r)).save(path);rr=rect(r);p.insert_image(rr,filename=str(path),keep_proportion=False);photo_records.append({'page':pn,'name':name,'source_crop_px':r,'placement_pt':list(rr),'source_pixel_sha256':hashlib.sha256(img.crop(tuple(r)).tobytes()).hexdigest(),'source_image_path':str(source),'raster_publication_text_visible':'inspect in composed page'})
 def place(path,r,name):
  rr=rect(r);p.insert_image(rr,filename=str(path),keep_proportion=False);photo_records.append({'page':pn,'name':name,'file':str(path.relative_to(R)),'sha256':sha(path),'placement_pt':list(rr),'keep_proportion':False})
 def repaired_footer(r,preserve_x,caption=None):
  path=A/f'footer{pn}-clean-generated.png';rr=rect(r);p.insert_image(rr,filename=str(path),keep_proportion=False)
  original=im.crop(tuple(r));ww,hh=original.size;xx=np.arange(ww)[None,:]+r[0]
  alpha=np.broadcast_to(np.clip((xx-preserve_x)/35,0,1),(hh,ww)).copy()
  if caption:
   x0,y0,x1,y1=caption; yy,xx=np.mgrid[:hh,:ww];gx=xx+r[0];gy=yy+r[1]
   dx=np.maximum(np.maximum(x0-gx,gx-x1),0);dy=np.maximum(np.maximum(y0-gy,gy-y1),0);distance=np.hypot(dx,dy)
   keep=np.clip(distance/18,0,1);alpha=np.minimum(alpha,keep)
  mask=fitz.Pixmap(fitz.csGRAY,ww,hh,np.uint8(alpha*255).tobytes(),False).tobytes('png');buf=io.BytesIO();original.save(buf,format='PNG');p.insert_image(rr,stream=buf.getvalue(),mask=mask,keep_proportion=False)
  photo_records.append({'page':pn,'name':'footer_source_protected','source_crop_px':r,'native_masks':'continuous sky field and caption rectangle, 18/35px outer feather; never glyph-shaped','preserve_original_after_x':preserve_x+35,'caption_repair':caption,'candidate_file':str(path.relative_to(R)),'candidate_sha256':sha(path),'protected_source_pixels':int((alpha==1).sum()),'mask_only':True})
 def hero(r,erase_rects):
  # Original adopted photograph pixels are preserved. Repair is limited to wall
  # fields where publication lettering had been baked in, never to faces.
  path=S/f'p{pn}-main-generated.png';rr=rect(r);p.insert_image(rr,filename=str(path),keep_proportion=False)
  original=im.crop(tuple(r));ww,hh=original.size;alpha=np.ones((hh,ww));yy,xx=np.mgrid[:hh,:ww];gx=xx+r[0];gy=yy+r[1]
  for x0,y0,x1,y1 in erase_rects:
   dx=np.maximum(np.maximum(x0-gx,gx-x1),0);dy=np.maximum(np.maximum(y0-gy,gy-y1),0);dist=np.hypot(dx,dy);alpha=np.minimum(alpha,np.clip(dist/12,0,1))
  mask=fitz.Pixmap(fitz.csGRAY,ww,hh,np.uint8(alpha*255).tobytes(),False).tobytes('png');buf=io.BytesIO();original.save(buf,format='PNG');p.insert_image(rr,stream=buf.getvalue(),mask=mask,keep_proportion=False)
  photo_records.append({'page':pn,'name':'source_hero_pixels_protected','source_crop_px':r,'repair_fields':erase_rects,'protected_original_pixels':int((alpha==1).sum()),'total_pixels':ww*hh,'decoded_original_pixel_sha256':hashlib.sha256(original.tobytes()).hexdigest(),'keep_proportion':False,'face_pixels_not_regenerated':True})
 def line(value,roi,bold=False,color=navy):
  x0,y0,x1,y1=roi;c=old[y0:y1,x0:x1].astype(int);mask=(c[:,:,0]<145)&(c[:,:,1]<170)&(c[:,:,2]<210);yy,xx=np.where(mask);assert len(xx),(pn,value,roi)
  colors=c[mask];lum=colors.mean(1);core=colors[lum<=np.quantile(lum,.2)];color=tuple(np.median(core,axis=0)/255)
  ink=fitz.Rect(pt(x0+xx.min(),y0+yy.min()),pt(x0+xx.max()+1,y0+yy.max()+1));k='B' if bold else 'R';t=fitz.open();tp=t.new_page(width=max(1200,fonts[k].text_length(value,fontsize=100)+100),height=300);tp.insert_font(fontname='F',fontfile=str(fontfiles[k]));tp.insert_text((20,200),value,fontname='F',fontsize=100,color=color)
  px=tp.get_pixmap(matrix=fitz.Matrix(1,1),alpha=True);a=np.frombuffer(px.samples,dtype=np.uint8).reshape(px.height,px.width,4);ys,xs=np.where(a[:,:,3]>20);ib=fitz.Rect(xs.min(),ys.min(),xs.max()+1,ys.max()+1);sx=ink.width/ib.width;sy=ink.height/ib.height;pad=2;clip=ib+(-pad,-pad,pad,pad);dest=ink+(-pad*sx,-pad*sy,pad*sx,pad*sy);p.show_pdf_page(dest,t,0,clip=clip,keep_proportion=False)
  records.append({'page':pn,'text':value,'source_roi_px':roi,'source_ink_bbox_pt':list(ink),'native':True,'source_font_shape':'unavailable_raster_approximation'})
 def headline(value,roi):
  x0,y0,x1,y1=roi;c=old[y0:y1,x0:x1].astype(int);m=(c[:,:,0]<145)&(c[:,:,1]<170)&(c[:,:,2]<210);xs=np.where(m.any(0))[0];gaps=[(int(xs[i]+1+x0),int(xs[i+1]+x0),int(xs[i+1]-xs[i]-1)) for i in np.where(np.diff(xs)>1)[0]];gaps=sorted(sorted(gaps,key=lambda v:v[2],reverse=True)[:len(value)-1]);edges=[int(xs.min()+x0)]+[int((a+b)/2) for a,b,_ in gaps]+[int(xs.max()+1+x0)]
  assert len(edges)==len(value)+1
  for ch,left,right in zip(value,edges,edges[1:]):line(ch,[left,y0,right,y1],True)
 def lines(values,x0,x1,y,step,height,bold=False,color=navy):
  for i,v in enumerate(values):line(v,[x0,y+i*step,x1,y+i*step+height],bold,color)
 def basic(value,x,y,size=48,bold=False,width=None,angle=0,color=navy):
  k='B' if bold else 'R';name='Support'+k;p.insert_font(fontname=name,fontfile=str(fontfiles[k]));z=ir.width/2480;fs=size*z;o=pt(x,y);sx=1 if width is None else width*z/fonts[k].text_length(value,fontsize=fs);mat=fitz.Matrix(sx,1).prerotate(angle);p.insert_text(o,value,fontname=name,fontsize=fs,color=color,morph=(o,mat));records.append({'page':pn,'text':value,'origin_pt':list(o),'native':True,'approximate_handwritten':bool(angle)})
 # Upper background: ordinary source photography never becomes an entire page image.
 if pn==10:
  place(A/'p10-upper-clean-generated.png',[1400,0,2480,620],'upper_wall_background_repair')
  crop([1460,0,1680,530],'upper_original_window_columns')
  hero([0,530,2480,1530],[[0,530,745,900],[1850,530,2480,620]])
  # Preserve the original bubble silhouette. Replace only its flat text field.
  field=arr[1220:1475,2110:2435,:3];clean=field[(field[:,:,0]>180)&(field[:,:,1]>field[:,:,0]+5)&(field[:,:,2]>field[:,:,0]+12)];bubble_color=tuple(np.median(clean,axis=0)/255);box([2110,1220,2435,1475],bubble_color)
  # Cards and photos; all surrounding publication letters are native.
  cardcols=[(45,510,(.94,.97,.99)),(530,990,(.99,.95,.97)),(1010,1470,(.94,.98,.94)),(1490,1960,(.99,.97,.92)),(1980,2440,(.96,.95,.99))]
  for x0,x1,c in cardcols:box([x0,1565,x1,2650],c,radius=.02)
  specs=json.loads((S/'spec.json').read_text())
  for i,r in enumerate(specs['p10-small']['rects']):crop(r,f'small-{i}')
  for i,r in enumerate([[175,1570,370,1777],[665,1570,860,1777],[1147,1570,1342,1777],[1632,1570,1827,1777],[2119,1570,2314,1777]]):crop(r,f'icon-{i}')
  # Pale blue footer, original building/leaf photography retained at right.
  repaired_footer([70,2692,2480,3340],1720,[1810,3200,2310,3310])
  # The original photographic diagram's printed labels are covered by native circles.
  for cx,cy,radius,c in [(1785,3080,111,(.91,.98,1)),(1999,3052,113,(.94,.92,1)),(2212,3080,111,(.91,.98,1))]:
   syy,sxx=np.mgrid[cy-70:cy+70,cx-70:cx+70];field=old[cy-70:cy+70,cx-70:cx+70];select=((sxx-cx)**2+(syy-cy)**2<70**2)&(field.min(2)>180);c=tuple(np.median(field[select],axis=0)/255)
   p.draw_circle(pt(cx,cy),radius*ir.width/2480,fill=c,color=(.68,.77,.87),width=.8)


  line('多様な仲間と、ともに学び、未来をつくる',[1680,37,2390,100],False,blue)
  p.draw_line(pt(100,97),pt(1335,97),color=(.35,.63,.8),width=.6)
  headline('教員・支援体制',[75,170,1415,390])
  box([75,395,1415,418],(.68,.83,.92))
  line('学生一人ひとりを支える、安心のサポート体制',[95,455,1450,531],True)
  # Native current support intro is imported later (no duplicate old copy).
  basic('いつでも相談できる',1715,345,63,width=605,angle=12)
  basic('先生がいる。',1880,440,63,width=400,angle=12)
  basic('だから、がんばれる。',1850,555,58,width=520,angle=12)
  p.draw_line(pt(1910,591),pt(2380,436),color=blue,width=.9)
  # Clean circle in generated photo contains no source letter pixels.
  lines(['どんな小さな','ことでも、','気軽に相談','できます。'],2130,2410,1240,59,52,False,blue)
  line('専門分野の教員',[82,1780,487,1853],True)
  lines(['AI・ビジネス・ITの','基礎から丁寧に','指導します。'],90,485,1870,59,54)
  line('生活・進路相談',[1035,1780,1450,1853],True)
  lines(['学校生活、進路、','就職などを','相談できます。'],1080,1445,1870,59,54)
  line('学習サポート',[2035,1780,2425,1853],True)
  lines(['勉強につまずいた時も、','一人で悩まない','環境です。'],2010,2440,1870,59,54)
  box([125,2736,590,2815],(.31,.68,.86),radius=.2)
  basic('保護者の皆さまへ',180,2795,43,False,390,color=(1,1,1))
  lines(['学習面だけでなく、生活面・進路面まで、','教員と支援スタッフが連携して','学生一人ひとりを支えます。'],120,1380,2850,88,78,True)
  line('本校では、学生が安心して学び、充実した学校生活を送れるよう、',[120,3130,1230,3181])
  line('教員・支援スタッフが日常的にコミュニケーションを取り、きめ細やかな支援を行っています。',[120,3190,1675,3241])
  line('保護者の皆さまにも、安心してお子さまをお預けいただける環境づくりに努めています。',[120,3250,1580,3301])
  # Labels reconstructed directly; bounding boxes are local to each original circle.
  line('学習',[1700,3035,1880,3080],False,blue);line('のサポート',[1705,3088,1870,3125],False,blue)
  line('生活',[1935,3005,2065,3050],False,blue);line('のサポート',[1920,3058,2080,3095],False,blue)
  line('進路',[2140,3035,2280,3080],False,blue);line('のサポート',[2125,3088,2295,3125],False,blue)
  line('教員と支援スタッフが',[1850,3208,2225,3247],True,blue);line('チームで支えます',[1870,3257,2140,3296],True,blue)
 else:
  place(A/'p11-upper-clean-generated.png',[1000,0,2480,200],'upper_wall_background_repair')
  crop([1000,0,1700,200],'upper_original_plant')
  hero([1000,200,2480,1130],[[1000,200,1235,395],[1000,440,1270,625],[1900,200,2480,425],[1900,425,2200,470],[1000,670,1060,1000]])
  # Preserve source right-hand counsellor, including every visible face/hand pixel.
  # At upper wall only publication handwriting remains; no person lies above y450.

  cardcols=[(75,660,(.99,.95,.97)),(685,1250,(.93,.97,.99)),(1270,1830,(.93,.98,.95)),(1855,2410,(1,.97,.92))]
  for x0,x1,c in cardcols:box([x0,1167,x1,1630],c,radius=.02)
  specs=json.loads((S/'spec.json').read_text())
  for i,r in enumerate(specs['p11-small']['rects']):crop(r,f'small-{i}')
  for i,(x0,x1,c) in enumerate(cardcols):box([x0,1760,x1,2320],c,radius=.02)
  for i,r in enumerate([[245,1768,475,1968],[820,1768,1050,1968],[1400,1768,1630,1968],[1990,1768,2220,1968]]):crop(r,f'icon-{i}')
  for i,(x0,x1,c) in enumerate(cardcols):box([x0,2450,x1,3005],c,radius=.02)
  # Reinsert the lower row after card backgrounds.
  for i,r in enumerate(specs['p11-small']['rects'][4:]):crop(r,f'lower-photo-{i}')
  repaired_footer([0,3030,2480,3400],1600)
  line('多様な仲間と、ともに学び、未来をつくる',[1750,32,2420,100],False,blue)
  p.draw_line(pt(80,95),pt(1235,95),color=(.35,.63,.8),width=.6)
  headline('保護者の方へ',[65,160,1240,385]);box([65,385,1235,405],(.68,.83,.92))
  line('お子さまの未来を、一緒に支えます。',[80,445,1260,525],True)
  line('学び・生活・進路まで、学校全体で安心を支えます。',[80,555,1300,620],True)
  lines(['AIビジネス専門学校は、','学生一人ひとりの可能性を大切にし、','学習・生活・進路のすべての面で支える学校です。','保護者の皆さまと連携し、安心してお子さまを','預けていただける環境づくりに努めています。'],90,1040,675,64,55)
  basic('お子さまの夢を',1930,250,57,width=400,angle=12)
  basic('これからも',2060,325,57,width=300,angle=12)
  basic('一緒に応援します。',2025,400,57,width=430,angle=12)
  p.draw_line(pt(2060,458),pt(2430,345),color=blue,width=.7)
  box([75,1040,1015,1167],(.85,.94,1),radius=.03);line('こんな心配はありませんか？',[125,1060,970,1150],True)
  line('AIビジネス専門学校のサポート体制',[75,1670,1180,1755],True)
  line('学びも、生活も、進路も。学校全体でしっかりサポートします。',[1490,1690,2420,1745],False,blue)
  # Current native question/body patches, imported below, replace the old words.
  line('学習サポート',[735,1980,1210,2040],True)
  line('進路・就職サポート',[1890,1980,2400,2045],True)
  lines(['進路相談、就職活動の','サポート、ビジネスマナー','指導など、卒業後の','キャリア形成を支援します。'],1900,2390,2060,60,54)
  # Number circles are native structure and text.
  for i,(cx,c) in enumerate([(145,(.2,.58,.8)),(750,(.83,.39,.58)),(1330,(.4,.69,.28)),(1905,(.96,.64,.16))]):
   p.draw_circle(pt(cx,2510),52*ir.width/2480,fill=c,color=None);basic(str(i+1),cx-19,2540,75,color=(1,1,1))
  lines(['先生・スタッフが','一人ひとりをサポート'],840,1220,2470,57,52,True)
  line('お子さまの可能性は、ここから広がります。',[100,3075,1430,3160],True)
  line('AIビジネス専門学校は、学生と保護者の皆さまと共に歩み、',[100,3195,1220,3245])
  line('お子さまの夢の実現に向けて全力でサポートします。',[100,3251,1090,3301])
  line('どんなことでも、お気軽にご相談ください。私たちは、いつでも皆さまのそばにいます。',[100,3308,1600,3358])
 # Shared footer lettering, old folio deliberately omitted.
 line('AIビジネス専門学校',[80,3380,650,3455],True)
 line('学ぶ人の、未来とともに。',[660,3410,1060,3460],False,blue)
 p.draw_line(pt(1090,3420),pt(2340,3420),color=(.36,.6,.77),width=.6)
 # Existing native copy patches preserve latest approved wording and metrics.
 plans=json.loads((R/'books/prospectus-isen-trial-2028/parts/jp-copy-20261028-copy-plan/c3169fd3b5e5ad1aa99df7d96492043d000818db0356aee7df403e94aa0f4b69/jp-copy-20261028-copy-plan.json').read_text())['patches']
 for patch in [x for x in plans if x['page']==pn]:
  rr=rect(patch['rect_px']);hexcolor=patch.get('bg','#ffffff');p.draw_rect(rr,fill=tuple(int(hexcolor[k:k+2],16)/255 for k in (1,3,5)),color=None);copy_native_type(pn-1,rr,p)
 rr=rect([70,25,900,90]);copy_native_type(pn-1,rr,p)
 p.draw_line(pt(100 if pn==10 else 80,97),pt(1335 if pn==10 else 1235,97),color=(.35,.63,.8),width=.6)
 # Extend only the missing outer strip with original edge samples; do not
 # scale or shift the adopted photograph to hide the 0.148mm source shortfall.
 right=A/f'p{pn}-right-edge.png';im.crop((2479,0,2480,3508)).save(right);p.insert_image(fitz.Rect(ir.x1-.01,ir.y0,sp.rect.width,ir.y1),filename=str(right),keep_proportion=False)
 top=A/f'p{pn}-top-edge.png';im.crop((0,0,2480,1)).save(top);p.insert_image(fitz.Rect(0,0,sp.rect.width,ir.y0+.01),filename=str(top),keep_proportion=False)
 # Normalize exactly as the historical print pipeline. No new photo shrinking.
 out=fitz.open();op=out.new_page(width=210*72/25.4,height=297*72/25.4);op.show_pdf_page(op.rect,D,len(D)-1,keep_proportion=False)
 op.insert_font(fontname='PrintFolio',fontfile='/usr/share/fonts/opentype/urw-base35/NimbusSans-Bold.otf');op.insert_textbox(fitz.Rect(192*72/25.4,287*72/25.4,205*72/25.4,292*72/25.4),str(pn),fontsize=9,fontname='PrintFolio',color=(.25,.25,.25),align=2)
 path=B/f'support-p{pn}-native-draft.pdf';out.save(path,deflate=True,garbage=4);op.get_pixmap(matrix=fitz.Matrix(1.25,1.25)).save(A/f'p{pn}-preview.png');out.close()
# Keep editable Unicode mappings faithful to ASCII input.
for pn in [10,11]:
 path=B/f'support-p{pn}-native-draft.pdf'
 with pikepdf.open(path,allow_overwriting_input=True) as pdf:
  exact=pikepdf.Array([0,0,Decimal(210)*72/Decimal('25.4'),Decimal(297)*72/Decimal('25.4')])
  for name in ['/MediaBox','/CropBox','/TrimBox','/BleedBox','/ArtBox']:pdf.pages[0].obj[name]=exact
  for xobj in pdf.objects:
   if isinstance(xobj,pikepdf.Stream) and '/SMask' in xobj:xobj.SMask.ColorSpace=pikepdf.Name.DeviceGray
  for obj in pdf.objects:
   if isinstance(obj,pikepdf.Dictionary) and '/ToUnicode' in obj and 'DTPRebuiltSansJP' in str(obj.get('/BaseFont','')):
    data=obj.ToUnicode.read_bytes();data=re.sub(rb'(<000e>\s*)<2011>',rb'\g<1><002d>',data,flags=re.I);data=re.sub(rb'(<0001>\s*)<00a0>',rb'\g<1><0020>',data,flags=re.I);obj.ToUnicode.write(data)
  pdf.save(path)
report={'status':'draft_not_for_submission','inputs':inputs,'source':str(source.relative_to(R)),'source_sha256':sha(source),'photos':photo_records,'text':records,'issues':['Replacement font shapes and handwriting differ from source raster type.','P11 original counsellor region retained from y450; upper wall needs strict seam/handwriting review.','Footer building crops retain surrounding source diagram elements underneath native opaque labels; strict visual check required.','Photo boundaries/card background and roundness are reconstructed and require independent exactness comparison.','RGB working files; CMYK conversion and independent review not done.'],'outputs':{str(pn):{'file':f'support-p{pn}-native-draft.pdf','sha256':sha(B/f'support-p{pn}-native-draft.pdf')} for pn in [10,11]}}
(B/'support-rebuild-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report['outputs'],indent=2))
