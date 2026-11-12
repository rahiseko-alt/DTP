"""Reconstruct OC side with live type, vector geometry/QR and protected source photographs.
This is a review candidate. Photographic repairs affect publication-ink regions only.
"""
from pathlib import Path
from decimal import Decimal
import fitz,pikepdf,numpy as np,json,hashlib,re,shutil,yaml,unicodedata
from scipy import ndimage
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
B=Path(__file__).resolve().parent;R=B.parents[2];A=B/'assets/flyer-back';A.mkdir(parents=True,exist_ok=True)
STORE=R/'shared/generated-assets/printpack-native-rebuild-20261111/flyer-back'
for generated in STORE.rglob('*'):
 if generated.is_file():
  target=A/generated.relative_to(STORE);target.parent.mkdir(parents=True,exist_ok=True)
  if not target.exists():shutil.copyfile(generated,target)
source=R/json.loads((B.parent/'receipts.json').read_text())[1]['path'];src=fitz.open(source);sp=src[1];W,H=210*72/25.4,297*72/25.4
sha=lambda f:hashlib.sha256(Path(f).read_bytes()).hexdigest()
assert sha(source)=='20d2c38ea4b640d2a3bc8dd246e63d6be306389b5639f06adeba3fcddaf43464'
hero=fitz.Pixmap(src,162);old=fitz.Pixmap(src,149);ha=np.frombuffer(hero.samples,dtype=np.uint8).reshape(hero.height,hero.width,3);oa=np.frombuffer(old.samples,dtype=np.uint8).reshape(old.height,old.width,3)
hero.save(A/'hero-adopted.png');old.save(A/'old-base.png')
# Preserve decoded photo RGB. Extraction is not retouching or upscaling.
def extract(pix,xyxy,name):
 x0,y0,x1,y1=xyxy;a=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,pix.n)[y0:y1,x0:x1];q=fitz.Pixmap(fitz.csRGB,x1-x0,y1-y0,a.tobytes(),False);q.save(A/name);return A/name
header_bg=extract(old,[440,0,722,75],'header-right.png')
crest=extract(old,[15,14,106,103],'official-crest-top.png')
footer_crest=extract(old,[10,937,84,1014],'official-crest-footer.png')
photos={
 'class':(None,fitz.Rect(23.78781128,657.3034668,189.23883057,725.7659912)),
 'friends':(extract(old,[251,801,441,886],'friends-source.png'),fitz.Rect(207.9845095,655.6734218,362.8401389,724.9509502)),
 'consult':(extract(old,[467,801,691,885],'consult-source.png'),fitz.Rect(384.0309092,655.6734218,566.5975459,724.1359205))}
classpix=fitz.Pixmap(src,163);classpix.save(A/'class-source.png');photos['class']=(A/'class-source.png',photos['class'][1])
# Source native overlays are retained; fused raster page/photo/crest images are removed.
with pikepdf.open(source) as pdf:
 for x in [149,162,163,156]:
  im=pdf.get_object(x,0);im.write(b'')
  for k in list(im.keys()):
   if str(k)!='/Length':del im[k]
  im.Type=pikepdf.Name('/XObject');im.Subtype=pikepdf.Name('/Form');im.BBox=pikepdf.Array([0,0,1,1])
 pdf.save(A/'native-source-only.pdf')
nd=fitz.open(A/'native-source-only.pdf')
nd[1].add_redact_annot(fitz.Rect(0,766.8,W,H),fill=False,cross_out=False)
nd[1].add_redact_annot(fitz.Rect(94.1,64.2,254.3,77.5),fill=False,cross_out=False)
nd[1].apply_redactions(images=0,graphics=0,text=0)
nd.save(A/'native-source-cleaned-before-fonts.pdf',garbage=4,deflate=True)
with pikepdf.open(A/'native-source-cleaned-before-fonts.pdf') as pdf:
 for obj in pdf.objects:
  if isinstance(obj,pikepdf.Dictionary) and '/Resources' in obj and '/Font' in obj.Resources:
   fonts=obj.Resources.Font
   for key in list(fonts):
    if str(fonts[key].get('/BaseFont',''))=='/Helvetica':del fonts[key]
 pdf.save(A/'native-source-cleaned.pdf')
nd=fitz.open(A/'native-source-cleaned.pdf')
out=fitz.open();p=out.new_page(width=W,height=H)
records=[];repairs=[]
def color(h):return tuple(int(h[i:i+2],16)/255 for i in (1,3,5))
def fill(rect,c):p.draw_rect(fitz.Rect(rect),color=None,fill=color(c))
def coords_path(mask,rect):
 # Trace a selection as PDF clipping geometry; source/generated image pixels are not rewritten.
 fig,ax=plt.subplots();cs=ax.contour(np.pad(mask.astype(float),1),levels=[.5]);paths=cs.allsegs[0];plt.close(fig);ops=[]
 for vs in paths:
  if len(vs)<4:continue
  vs=vs[::1];xy=[(rect.x0+(x-.5)/mask.shape[1]*rect.width,H-(rect.y0+(y-.5)/mask.shape[0]*rect.height)) for x,y in vs]
  ops.append(f'{xy[0][0]:.6f} {xy[0][1]:.6f} m')
  ops.extend(f'{x:.6f} {y:.6f} l' for x,y in xy[1:]);ops.append('h')
 return '\n'.join(ops)
def image_patch(path,rect,mask):
 p.insert_image(rect,filename=str(path),keep_proportion=False);xref=p.get_contents()[-1];oldstream=out.xref_stream(xref);clip=coords_path(mask,rect)
 out.update_stream(xref,('q\n'+clip+'\nW* n\n').encode()+oldstream+b'\nQ\n')
# Hero photograph: all original pixels remain except the explicit ink-removal selections.
hr=sp.get_image_rects(162)[0];clean=STORE/'hero-generated-clean-candidate.png' if (STORE/'hero-generated-clean-candidate.png').exists() else A/'hero-generated-clean-candidate.png';assert clean.is_file()
if clean.resolve()!=(A/'hero-generated-clean-candidate.png').resolve():shutil.copyfile(clean,A/'hero-generated-clean-candidate.png')
# Tiny original-frame gutters are filled by translating source edge pixels underneath,
# without scaling or shifting any existing photograph content.
for dx in [-hr.x0,W-hr.x1]:p.insert_image(hr+(dx,0,dx,0),filename=str(A/'hero-adopted.png'),keep_proportion=False)
p.insert_image(hr,filename=str(A/'hero-adopted.png'),keep_proportion=False)
r,g,b=[ha[:,:,i].astype(int) for i in range(3)];yy,xx=np.indices(r.shape)
navy=(b-r>35)&(b-g>5)&(r<150)
yellow=(r>175)&(g>175)&(b<180)
# Top publication lettering/crest and underline; no foreground face is selected.
top=(xx<620)&(yy<255)
top[:35,:580]=True
# White two-line publication slogan over the dark sleeve, excluding hands/faces.
white=(r>150)&(g>150)&(b>150)&((np.maximum.reduce([r,g,b])-np.minimum.reduce([r,g,b]))<65)
band1=(xx>885)&(yy>-(xx-890)*.24+578)&(yy<-(xx-890)*.24+625)
band2=(xx>885)&(yy>-(xx-890)*.19+625)&(yy<-(xx-890)*.19+678)
slogan=band1|band2
# Printed bottom ribbon will be rebuilt above this strip. Hidden background is repaired here.
ribbon=(yy>580)
mask=ndimage.binary_dilation(top|slogan,iterations=7)|ribbon
# Do not permit any repaired pixels in the known visible face/hair/hand/watch areas.
protected=[(0,257,163,587),(152,246,340,493),(400,235,640,512),(620,0,838,267),(887,68,1039,281),(1010,75,1226,365),(881,239,1130,520),(604,417,876,591)]
for x0,y0,x1,y1 in protected:mask[y0:y1,x0:x1]=False
# Graphic yellow paint over fingertips is not source skin; it must be repaired too.
mask|=yellow&(yy>560)
alpha=ndimage.gaussian_filter(mask.astype(float),sigma=5)
for x0,y0,x1,y1 in protected:
 keep=~(yellow[y0:y1,x0:x1]&(yy[y0:y1,x0:x1]>560))
 alpha[y0:y1,x0:x1][keep]=0
cp=fitz.Pixmap(str(A/'hero-generated-clean-candidate.png'));scaled=ndimage.zoom(alpha,(cp.height/hero.height,cp.width/hero.width),order=1)
am=fitz.Pixmap(fitz.csGRAY,cp.width,cp.height,np.rint(scaled[:cp.height,:cp.width]*255).astype(np.uint8).tobytes(),False)
p.insert_image(hr,filename=str(A/'hero-generated-clean-candidate.png'),mask=am.tobytes('png'),keep_proportion=False)
# Frame filling must use repaired imagery in the far left/right strip too.
# Original frame is ~1.2mm; only the extension strip is new, main photo stays unmoved.
# Header right is an unchanged, text-free crop from the source backdrop.
base_rect=sp.get_image_rects(149)[0];s=base_rect.width/722
header_rect=fitz.Rect(base_rect.x0+440*s,base_rect.y0,base_rect.x1,base_rect.y0+75*s)
p.insert_image(header_rect+(W-header_rect.x1,-base_rect.y0,W-header_rect.x1,-base_rect.y0),filename=str(header_bg),keep_proportion=False)
p.insert_image(header_rect,filename=str(header_bg),keep_proportion=False)
# White top left backing is the existing title panel; crest is an official raster mark.
fill([0,0,440*s+base_rect.x0,79],'#ffffff');p.insert_image(fitz.Rect(base_rect.x0+15*s,base_rect.y0+14*s,base_rect.x0+106*s,base_rect.y0+103*s),filename=str(crest),keep_proportion=False)
# Yellow ribbon geometry is recovered as decoration only; old letter pixels are never inserted.
rr,gg,bb=[oa[:,:,i].astype(int) for i in range(3)];by,bx=np.indices(rr.shape);brush=(rr>190)&(gg>175)&(bb<180)&(by>=410)&(by<584)
brush=ndimage.binary_fill_holes(ndimage.binary_closing(brush,iterations=9));brush[:405]=False
# Complete the occluded paint, rather than keeping glyph-shaped holes in decoration.
# Infer its upper/lower edge from unoccluded yellow samples in every column.
cols=np.flatnonzero(brush.any(axis=0));topedge=np.array([np.flatnonzero(brush[:,x])[0] for x in cols],float);bottomedge=np.array([np.flatnonzero(brush[:,x])[-1]+1 for x in cols],float)
topedge=ndimage.gaussian_filter1d(ndimage.median_filter(topedge,size=7),2);bottomedge=ndimage.gaussian_filter1d(ndimage.median_filter(bottomedge,size=7),2)
for x,lo,hi in zip(cols,topedge,bottomedge):brush[int(round(lo)):int(round(hi)),x]=True
brush_clean=STORE/'brush-restored-textless.png' if (STORE/'brush-restored-textless.png').exists() else A/'brush-restored-textless.png'
if brush_clean.resolve()!=(A/'brush-restored-textless.png').resolve():shutil.copyfile(brush_clean,A/'brush-restored-textless.png')
bp=fitz.Pixmap(str(brush_clean));ba=np.frombuffer(bp.samples,dtype=np.uint8).reshape(bp.height,bp.width,bp.n);assert bp.alpha
brush=ndimage.binary_fill_holes(ba[:,:,-1]>80)
brush_rect=fitz.Rect(base_rect.x0,base_rect.y0+398*s,base_rect.x1,base_rect.y0+590*s)
paths=coords_path(brush,brush_rect)
# A single opaque vector path avoids separate raster-strip joins.
xref=out.get_new_xref();out.update_object(xref,'<<>>');out.update_stream(xref,('q\n1 1 .15 rg\n'+paths+'\nf*\nQ\n').encode())
# append the decoration stream without replacing already-painted images
contents=list(p.get_contents())
out.xref_set_key(p.xref,'Contents','['+' '.join(f'{x} 0 R' for x in contents+[xref])+']')
# Unchanged separate photographs remain exactly at their original positions.
# Native source text, ellipses and experience frame, with raster page removed.
tab=p.new_shape();tab.draw_polyline([(16,611),(16,599)]);tab.draw_bezier((16,599),(16,589),(20,583),(32,583));tab.draw_line((32,583),(393,583));tab.draw_bezier((393,583),(402,583),(407,600),(410,611));tab.draw_line((410,611),(16,611));tab.finish(fill=color('#04529b'),color=None,closePath=True);tab.commit()
p.show_pdf_page(p.rect,nd,1,keep_proportion=False)
for key,(path,rect) in photos.items():p.insert_image(rect,filename=str(path),keep_proportion=False)
out.save(A/'DIAGNOSTIC-photo-without-new-publication-type.pdf',garbage=4,deflate=True)
# Rebuild the entire footer to eliminate misaligned pale backing and separate seams.
footer_y=766.8;split=108*72/25.4
fill([0,footer_y,split,H],'#07569a');fill([split,footer_y,W,H],'#0c325d')
p.insert_image(fitz.Rect(10,footer_y+8,70,footer_y+70),filename=str(footer_crest),keep_proportion=False)
F=Path('/workspace/.dtp-tools/native-fonts');FF=STORE/'fonts' if (STORE/'fonts').exists() else A/'fonts';fontfiles={'B':F/'DTPRebuiltSansJPBold.otf','R':F/'DTPRebuiltSansJPRegular.otf','Brush':FF/'Knewave-Regular.ttf','Hand':FF/'Yomogi-Regular.ttf'}
for k,f in fontfiles.items():p.insert_font(fontname='Back'+k,fontfile=str(f))
def typefit(value,box,font='B',c='#07174c',angle=0):
 # Render only to measure painted font bounds. The inserted object remains PDF text.
 box=fitz.Rect(box);temp=fitz.open();tp=temp.new_page(width=2200,height=500);tp.insert_font(fontname='F',fontfile=str(fontfiles[font]));origin=fitz.Point(60,250)
 opts={'render_mode':2,'border_width':.012} if font=='Hand' else {}
 tp.insert_text(origin,value,fontsize=60,fontname='F',morph=(origin,fitz.Matrix(angle)),color=(0,0,0),**opts)
 pix=tp.get_pixmap(matrix=fitz.Matrix(2,2),colorspace=fitz.csGRAY);a=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width);ys,xs=np.where(a<180);ink=fitz.Rect(xs.min()/2,ys.min()/2,(xs.max()+1)/2,(ys.max()+1)/2)
 sx=box.width/ink.width;sy=box.height/ink.height;pt=fitz.Point(box.x0+(origin.x-ink.x0)*sx,box.y0+(origin.y-ink.y0)*sy)
 # The anisotropic matrix follows the rotated text at source visual bounds.
 mat=fitz.Matrix(angle)*fitz.Matrix(sx,sy)
 p.insert_text(pt,value,fontsize=60,fontname='Back'+font,color=color(c),fill=color(c),morph=(pt,mat),**opts);records.append({'text':value,'ink_target_pt':list(box),'font':font,'angle':angle,'native':True})
# Restore publication words absent from the source's native overlay.
typefit('学校法人 海鵬学園',[94,18,202,29],font='B')
typefit('AIビジネス専門学校',[94,35,367,61],font='B')
def hero_box(rawbox):return [hr.x0+rawbox[0]/hero.width*hr.width,hr.y0+rawbox[1]/hero.height*hr.height,hr.x0+rawbox[2]/hero.width*hr.width,hr.y0+rawbox[3]/hero.height*hr.height]
# Source handwriting has unequal glyph sizes/spacing; preserve each measured footprint.
headline1=[('A',[52,73,93,141]),('I',[110,74,122,130]),('を',[141,75,168,121]),('学',[189,57,235,120]),('び',[245,69,287,104]),('、',[304,88,315,101])]
headline2=[('未',[71,150,117,211]),('来',[132,143,176,202]),('の',[188,153,214,181]),('仕',[223,134,273,184]),('事',[282,118,322,182]),('に',[333,133,362,165]),('つ',[374,129,403,157]),('な',[414,116,449,156]),('げ',[461,110,493,150]),('よ',[505,105,531,144]),('う',[544,108,566,143]),('！',[585,88,596,122])]
for row,angle in [(headline1,7),(headline2,8)]:
 for glyph,rawbox in row:typefit(glyph,hero_box(rawbox),font='Hand',angle=angle)
typefit('いっしょに学び、',hero_box([904,520,1182,609]),font='Hand',c='#ffffff',angle=12)
typefit('いっしょに成長する。',hero_box([911,576,1208,664]),font='Hand',c='#ffffff',angle=10)
# The original brush lettering uses different sizes/baselines for every glyph.
# Keep these original ink bounds rather than forcing the whole phrase into one line box.
brush_glyphs=[('O',[25,425,136,563]),('P',[124,450,208,556]),('E',[198,457,270,547]),('N',[257,455,348,547]),('C',[362,453,436,550]),('A',[430,466,490,547]),('M',[488,470,561,543]),('P',[552,468,614,559]),('U',[613,472,665,538]),('S',[653,463,710,550])]
for glyph,rawbox in brush_glyphs:
 box=[base_rect.x0+rawbox[0]*s,base_rect.y0+rawbox[1]*s,base_rect.x0+rawbox[2]*s,base_rect.y0+rawbox[3]*s]
 typefit(glyph,box,font='Brush',c='#00478b')
typefit('オープンキャンパス',[301,452,462,469],font='B')
typefit('10:00〜12:30',[454,492,570,510],font='B')
typefit('（受付9:30〜）',[468,517,558,531],font='B')
school=yaml.safe_load((R/'company-data/facts/school.yaml').read_text());contacts=yaml.safe_load((R/'company-data/facts/contacts.yaml').read_text())['contacts'];email=next(x['email'] for x in contacts if x['id']=='oc-flyer-email')
typefit('学校法人 海鵬学園',[79,782,174,791],c='#ffffff')
typefit(school['name'],[78,795,287,815],c='#ffffff')
# Source Helvetica was not embedded. Use its metrically compatible Nimbus
# program, preserving the original source origins, point sizes, widths and colour.
p.insert_font(fontname='EnglishEmbeddedMetric',fontfile='/usr/share/fonts/opentype/urw-base35/NimbusSans-Regular.otf')
english_font=fitz.Font(fontfile='/usr/share/fonts/opentype/urw-base35/NimbusSans-Regular.otf')
for block in sp.get_text('dict')['blocks']:
 for line in block.get('lines',[]):
  for span in line['spans']:
   if 'Artificial Intelligence' not in span['text']:continue
   origin=fitz.Point(span['origin']);size=span['size'];rgb=tuple((span['color']>>shift&255)/255 for shift in (16,8,0));sx=(span['bbox'][2]-span['bbox'][0])/english_font.text_length(span['text'],fontsize=size)
   p.insert_text(origin,span['text'],fontname='EnglishEmbeddedMetric',fontsize=size,color=rgb,morph=(origin,fitz.Matrix(sx,1)))
   records.append({'text':span['text'],'kind':'source_English_origin_size_width_preserved_embedded_Nimbus','origin_pt':list(origin),'font_pt':size,'horizontal_scale':sx})
typefit('入学事務局へのお問い合わせ',[316,776,428,784],font='R',c='#ffffff')
typefit(school['tel'],[316,793,400,804],font='R',c='#ffffff')
typefit(email,[316,814,464,820],font='R',c='#ffffff')
qd=fitz.open(R/'shared/generated-assets/qr/qr-mailto-aibusiness-kaihougakuen.svg');qp=fitz.open(stream=qd.convert_to_pdf(),filetype='pdf');p.show_pdf_page(fitz.Rect(524.4094,773.8583,578.2677,827.7166),qp,0)
typefit('メールでお問い合わせ',[513,831,590,836],font='R',c='#ffffff')
raw=A/'before-cmap.pdf';out.save(raw,garbage=4,deflate=True)
final=B/'flyer-back-native-candidate.pdf'
with pikepdf.open(raw) as pdf:
 for image in pdf.objects:
  if isinstance(image,pikepdf.Stream) and image.get('/Subtype')==pikepdf.Name('/Image') and '/SMask' in image:
   # Poppler rejects an ICCBased grayscale soft mask; alpha is scalar DeviceGray.
   image.SMask.ColorSpace=pikepdf.Name('/DeviceGray')
 for f in pdf.objects:
  if isinstance(f,pikepdf.Dictionary) and '/ToUnicode' in f:
   d=f.ToUnicode.read_bytes();d=re.sub(rb'(<[0-9a-f]+>\s*)<2011>',rb'\g<1><002d>',d,flags=re.I);f.ToUnicode.write(d)
 for pg in pdf.pages:
  box=pikepdf.Array([0,0,Decimal(210)*72/Decimal('25.4'),Decimal(297)*72/Decimal('25.4')])
  for k in ['/MediaBox','/CropBox','/TrimBox','/BleedBox','/ArtBox']:pg.obj[k]=box
 pdf.save(final,compress_streams=True)
check=fitz.open(final);pg=check[0];pg.get_pixmap(matrix=fitz.Matrix(150/72,150/72)).save(A/'preview.png')
report={'status':'REVIEW_CANDIDATE_NOT_APPROVED','file':final.name,'sha256':sha(final),'source':str(source.relative_to(R)),'source_sha256':sha(source),'page_count':1,'native_chars':len(pg.get_text()),'font_count':len(pg.get_fonts()),'zero_glyphs':sum(c[1]==0 for s in pg.get_texttrace() for c in s['chars']),'native_copy':records,'hero':{'source_xref':162,'source_decoded_rgb_sha256':hashlib.sha256(hero.samples).hexdigest(),'generated_candidate_sha256':sha(clean),'only_masked_publication_regions_repaired':True,'protected_source_rectangles_px':protected,'repair_mask_pixels':int(mask.sum()),'total_pixels':int(mask.size),'original_hero_rect_pt':list(hr),'main_photo_scaled_or_shifted':False},'limits':['Handwritten and brush type is retypeset in local OFL Yomogi/CaveatBrush; exact source letterforms not available.','Generation is confined to publication-ink selections; source persons remain protected. Independent visual inspection required.','RGB master only. CMYK/outline derivative and final combined two-page review pending.'],'final_submission':False}
(B/'flyer-back-rebuild-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'pdf':str(final),'sha256':sha(final),'chars':report['native_chars'],'glyph0':report['zero_glyphs']},ensure_ascii=False))
