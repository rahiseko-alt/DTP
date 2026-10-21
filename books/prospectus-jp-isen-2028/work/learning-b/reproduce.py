"""Rebuild final pages from source + retained tool outputs; no generation is simulated."""
from PIL import Image,ImageDraw,ImageFilter
from pathlib import Path
import json,hashlib,yaml,sys
ONLY_PAGES = [int(v) for v in sys.argv[1:]] or [7,9]
import numpy as np
D=Path(__file__).parent
geo=json.loads((D/'geometry.json').read_text()); rec=json.loads((D/'generation-records.json').read_text())
# Photo-local head / hair / neck edit masks. Clothes, hands, background and text stay original.
E={
7:{1:[[165,-30,455,438]],2:[[105,-35,345,335],[415,-35,700,372],[15,100,140,245],[290,170,405,310],[685,180,760,310]],3:[[235,-30,535,350]],4:[[135,-20,395,410],[385,-30,670,390]],5:[],6:[[0,60,120,310],[65,100,180,290],[110,65,280,325],[210,50,405,340],[335,95,460,300],[400,-40,650,342],[590,30,735,300],[670,80,780,285]],7:[[75,-30,365,370],[370,-60,780,425],[305,265,440,385]],8:[[50,85,230,355],[125,-35,420,410],[390,-30,725,420],[290,-30,430,230],[640,50,740,290]],9:[[30,185,195,430],[125,85,345,395],[265,-35,620,430]]},
9:{1:[[155,-40,470,330]],2:[[150,-30,505,390]],3:[[80,-35,425,340]],4:[[170,-50,500,355]],5:[[130,-40,525,400]],6:[[175,-40,505,380]],7:[[230,-10,565,400]],8:[[-40,-50,245,340]],9:[[15,-40,380,375],[310,-30,480,230]],10:[[-30,-20,270,360]]}}
changes={'source_pdf':'books/prospectus-isen-trial-2028/parts/latest-prospectus-pdf/62aa8e4415e5e6aa4523e1c14d024d8d45112d81dc92ce8db16db7718066f880/latest-prospectus-pdf.pdf','method':'Image Gen photo atlas edits; normalized atlas geometry; soft head/hair/neck masks over unchanged original page; source graphics and screens restored exactly. No page text generated.','pages':[]}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for pn in ONLY_PAGES:
 src=Image.open(D/f'source-page-{pn:02}.png').convert('RGB'); out=src.copy(); changed_mask=Image.new('L',src.size,0); entries=[]
 for atlas in geo['atlases']:
  if atlas['page']!=pn:continue
  aid=atlas['id']; gen=Image.open(D/f'{aid}-generated.png').convert('RGB'); gen_native=gen.size; gen=gen.resize(atlas['size'],Image.Resampling.LANCZOS)
  for cell in atlas['cells']:
   i=cell['photo'];r=cell['source_rect'];w,h=r[2]-r[0],r[3]-r[1]
   edit=gen.crop(cell['atlas_rect']).resize((w,h),Image.Resampling.LANCZOS)
   mask=Image.new('L',(w,h),0); dr=ImageDraw.Draw(mask)
   for b in E[pn][i]:dr.ellipse(b,fill=255)
   # Clip out clothes that the atlas model changed; keep original garments.
   clips={ (9,1):[(0,0),(w,0),(w,245),(350,245),(340,288),(225,280),(210,245),(0,245)],
    (9,4):[(0,0),(w,0),(w,270),(350,270),(335,310),(235,295),(210,270),(0,270)],
    (9,7):[(235,0),(w,0),(w,297),(495,297),(460,320),(415,295),(355,295),(300,260),(262,190)],
    (9,8):[(0,0),(w,0),(w,230),(170,230),(155,278),(65,260),(65,230),(0,230)],
    (9,9):[(0,0),(w,0),(w,270),(285,270),(270,305),(165,300),(145,270),(0,270)],
    (9,10):[(0,0),(210,0),(230,130),(220,250),(175,300),(110,280),(78,240),(0,240)] }
   if (pn,i) in clips:
    cm=Image.new('L',(w,h),0);ImageDraw.Draw(cm).polygon(clips[(pn,i)],fill=255)
    mask=Image.fromarray(np.minimum(np.array(mask),np.array(cm)))
   mask=mask.filter(ImageFilter.GaussianBlur(5))
   if pn==7 and i==4:
    # Keep the original hair tip / shirt junction so restored red lettering cannot pierce new hair.
    tip=Image.new('L',(w,h),0);ImageDraw.Draw(tip).ellipse((175,135,285,245),fill=255)
    tip=tip.filter(ImageFilter.GaussianBlur(8));mask=Image.fromarray(np.uint8(np.array(mask)*(1-np.array(tip)/255)))
   # Preserve microphone + hand grip on original presentation photo.
   if pn==9 and i==5:
    dr=ImageDraw.Draw(mask);dr.polygon([(315,213),(353,213),(370,225),(379,245),(376,260),(390,268),(401,282),(405,312),(395,330),(420,399),(311,399),(306,350),(307,300),(309,276),(319,262),(312,245)],fill=0)
   base=src.crop(r); photo=Image.composite(edit,base,mask)
   # Revision 2: restore original T-shirt contours, eliminating partial generated shirt collars.
   garment_polygons = {
    8:[(0,208),(40,225),(75,235),(100,240),(110,247),(150,267),(190,285),(220,315),(260,355),(300,400),(560,438),(0,438)],
    9:[(0,125),(25,133),(40,148),(55,185),(78,230),(110,270),(160,295),(195,280),(220,250),(240,230),(270,230),(305,245),(340,280),(560,330),(560,438),(0,438)]}
   if pn==9 and i in garment_polygons:
    gm=Image.new('L',(w,h),0);ImageDraw.Draw(gm).polygon(garment_polygons[i],fill=255)
    # Full original garment plus a 4px antialiased transition on the skin side only.
    gm_soft=gm.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(2))
    gm=Image.fromarray(np.maximum(np.array(gm),np.array(gm_soft)))
    photo=Image.composite(base,photo,gm)

   out.paste(photo,(r[0],r[1]));changed_mask.paste(mask,(r[0],r[1]))
   photo.save(D/f'p{pn:02}-photo-{i:02}.png')
   record={**rec[aid],'size':f'{w}x{h}','notes':rec[aid]['notes']+f' Photo {i}; source page rect={r}; mask ellipses={E[pn][i]}; source pixels outside mask retained. Native atlas size={gen_native}; LANCZOS resize used.'}
   if pn==7 and i==4:
    record['notes']+=' Revision2 final correction: original reddish hair component [354,1958,361,1962] is excluded from red-shirt lettering protection, using margin rectangle [351,1954,365,1967]. Generated hair remains continuous; actual garment text is unchanged.'
   (D/f'p{pn:02}-photo-{i:02}.prompt.yaml').write_text(yaml.safe_dump(record,allow_unicode=True,sort_keys=False))
   entries.append({'photo':i,'rect':r,'atlas':aid,'atlas_rect':cell['atlas_rect'],'head_mask_ellipses':E[pn][i],'source_pixels_sha256':hashlib.sha256(base.tobytes()).hexdigest(),'photo_output_sha256':sha(D/f'p{pn:02}-photo-{i:02}.png'),'revision2_garment_polygon':garment_polygons.get(i) if pn==9 else None,'method':'source-unchanged (no visible face)' if not E[pn][i] else 'Image Gen atlas + soft head mask + revision2 original garment contour' if pn==9 and i in [8,9] else 'Image Gen atlas + soft head mask'})
 # Exact protection restoration after all generated photo insertion.
 prot=Image.new('L',src.size,0);pd=ImageDraw.Draw(prot)
 for q in geo['protection'][str(pn)]:
  if q['type']=='ellipse':pd.ellipse(q['rect'],fill=255)
  else:
   if pn==7:
    # Restore only actual red lettering pixels + antialias, without a hard white rectangle over hair.
    region=Image.new('L',src.size,0);ImageDraw.Draw(region).polygon(q['points'],fill=255)
    rgb=np.array(src).astype(int); red=(rgb[:,:,0]>140)&((rgb[:,:,0]-rgb[:,:,1])>70)&((rgb[:,:,0]-rgb[:,:,2])>60)
    rm=Image.fromarray((red&(np.array(region)>0)).astype('uint8')*255).filter(ImageFilter.MaxFilter(3))
    # The source hair's reddish highlight is not shirt lettering. The threshold
    # selected one isolated 7x4px component at [354,1958,361,1962], which placed
    # a red triangle onto the replacement dark hair. Exclude only that component
    # plus 3px antialias margin; real printed-shirt pixels begin below this box.
    ImageDraw.Draw(rm).rectangle((351,1954,364,1966),fill=0)
    prot=Image.fromarray(np.maximum(np.array(prot),np.array(rm)));pd=ImageDraw.Draw(prot)
   else:pd.polygon(q['points'],fill=255)
 out=Image.composite(src,out,prot)
 out.save(D/f'page-{pn:02}.png');changed_mask.save(D/f'page-{pn:02}-edit-mask.png');prot.save(D/f'page-{pn:02}-protect-mask.png')
 a=np.array(src);b=np.array(out);p=np.array(prot)>0;m=np.array(changed_mask)>0
 photo_scope=np.zeros(a.shape[:2],bool)
 for rr in geo['photos'][str(pn)]:photo_scope[rr[1]:rr[3],rr[0]:rr[2]]=True
 diff=np.any(a!=b,axis=2)
 assert not diff[~photo_scope].any(), 'Changed outside photo rects'
 assert not diff[p].any(),'Changed protected source pixels'
 assert not diff[~m].any(),'Changed outside head masks'
 changes['pages'].append({'page':pn,'size':list(out.size),'source_png_sha256':sha(D/f'source-page-{pn:02}.png'),'output_png_sha256':sha(D/f'page-{pn:02}.png'),'photos':entries,'protection':geo['protection'][str(pn)],'protection_exclusions':[{'rect_xyxy':[351,1954,365,1967],'reason':'Source reddish hair highlight, not printed shirt lettering; 27px isolated component excluded to avoid red triangle on replacement hair'}] if pn==7 else [],'changed_pixels':int(diff.sum()),'outside_photos_changed_pixels':int(diff[~photo_scope].sum()),'protected_changed_pixels':int(diff[p].sum()),'outside_head_mask_changed_pixels':int(diff[~m].sum())})
 print(pn,'changed',int(diff.sum()),'protected',int(diff[p].sum()))
if (D/'changes.json').exists():
 prior=json.loads((D/'changes.json').read_text())
 changes['pages']=[x for x in prior.get('pages',[]) if x['page'] not in ONLY_PAGES]+changes['pages']
(D/'changes.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2))
# Human review contact sheets made from final source-preserving composite photos.
for pn in ONLY_PAGES:
 src=Image.open(D/f'page-{pn:02}.png'); rs=geo['photos'][str(pn)];cw,ch=744,450;cols=3;rows=(len(rs)+2)//3
 cs=Image.new('RGB',(cols*cw,rows*ch),'white')
 for k,r in enumerate(rs):cs.paste(src.crop(r).resize((cw,ch)),((k%cols)*cw,(k//cols)*ch))
 cs.save(D/f'p{pn:02}-final-contact.png')
