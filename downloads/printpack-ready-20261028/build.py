"""Print-only composition: correct old folios, normalize A4, extend 3mm bleed outside trim, add crop marks."""
from pathlib import Path
from statistics import median
import json,hashlib,math
import fitz
B=Path(__file__).resolve().parent;R=B.parents[1];MM=72/25.4;W,H=210*MM,297*MM;PAD=10*MM;BLEED=3*MM;FONT='/usr/share/fonts/opentype/urw-base35/NimbusSans-Bold.otf';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();rows=json.load(open(B/'receipts.json'));ocr={x['page']:x for x in json.load(open(B/'folio-ocr.json'))};(B/'intermediate').mkdir(exist_ok=True);records=[]
oldnums={2:'5',3:'6',4:'3',5:'4',6:'5',7:'6',8:'7',9:'8',10:'17',11:'19',12:'16',13:'21',14:'22',15:'23'}
def sample_bg(page,rect):
 # Sample background only at the four padded corners, not the old numeral.
 vals=[]
 for x,y in [(rect.x0,rect.y0),(rect.x1-.25,rect.y0),(rect.x0,rect.y1-.25),(rect.x1-.25,rect.y1-.25)]:
  pix=page.get_pixmap(matrix=fitz.Matrix(4,4),clip=fitz.Rect(x,y,x+.25,y+.25),alpha=False,colorspace=fitz.csRGB)
  if pix.width and pix.height:vals.append(pix.pixel(0,0))
 return tuple(median(v[k] for v in vals)/255 for k in range(3))
for row in rows:
 inp=R/row['path'];assert sha(inp)==row['asset']['sha256'];src=fitz.open(inp);patches=[]
 if row['label']=='brochure':
  for pn in range(2,16):
   p=src[pn-1];sx,sy=p.rect.width/W,p.rect.height/H;areas=[];native=[];headers=[]
   if pn>=12 or pn==9:
    for w in p.get_text('words'):
     if w[4]==oldnums[pn] and (w[1]<55 or w[1]>790):
      rect=fitz.Rect(w[:4]);native.append(rect)
      if w[1]<55:headers.append(rect)
    assert native,(pn,'native folio missing')
    for r in native:p.add_redact_annot(r+(-.35,-.35,.35,.35),fill=None,cross_out=False);areas.append(list(r+(-.35,-.35,.35,.35)))
    p.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE,graphics=0,text=0)
   else:
    data=ocr[pn];c=data.get('isolated',data);sc=c.get('scale',4);clip=fitz.Rect(c['clip']);words=[w for w in c['words'] if w['text']==oldnums[pn]];assert len(words)==1,(pn,c)
    word=words[0];rect=fitz.Rect(clip.x0+int(word['left'])/sc,clip.y0+int(word['top'])/sc,clip.x0+(int(word['left'])+int(word['width']))/sc,clip.y0+(int(word['top'])+int(word['height']))/sc)+(-1,-1,1,1)
    color=sample_bg(p,rect);p.draw_rect(rect,color=None,fill=color,overlay=True);areas.append(list(rect))
   # Preserve each existing folio side; move numerals inside the 5mm safe region.
   left=pn in [2,4,6,8];rect=fitz.Rect(5*MM if left else W-14*MM,H-10*MM,14*MM if left else W-5*MM,H-5*MM);rect=fitz.Rect(rect.x0*sx,rect.y0*sy,rect.x1*sx,rect.y1*sy)
   if pn in [7,11]:rect=rect+(0,8,0,8)
   rc=p.insert_textbox(rect,str(pn),fontsize=(8 if pn in [7,11] else 9)*sx,fontname='PageNumber',fontfile=FONT,color=(.141,.278,.42) if pn>=10 else (.25,.25,.25),align=0 if left else 2,overlay=True);assert rc>=0,(pn,rc);areas.append(list(rect))
   for h in headers:
    rect=fitz.Rect(h.x0-2,h.y0-1.3,h.x1+2,h.y1+2);rc=p.insert_textbox(rect,str(pn),fontsize=8.3*sx,fontname='PageNumber',fontfile=FONT,color=(1,1,1),align=1,overlay=True);assert rc>=0,(pn,'header',rc);areas.append(list(rect))
   patches.append({'page':pn,'old_folio':oldnums[pn],'new_folio':str(pn),'allowed_regions_source_pt':areas,'header_badge_updated':bool(headers)})
 corrected=B/'intermediate'/f'{row["label"]}-corrected-source.pdf';src.save(corrected,garbage=0,deflate=True)
 normalized=fitz.open()
 for pi in range(len(src)):
  p=normalized.new_page(width=W,height=H);p.show_pdf_page(p.rect,src,pi,keep_proportion=False)
 normfile=B/'intermediate'/f'{row["label"]}-A4-trim-RGB.pdf';normalized.save(normfile,garbage=0,deflate=True);norm=fitz.open(normfile);out=fitz.open()
 for pi in range(len(norm)):
  p=out.new_page(width=W+2*PAD,height=H+2*PAD);p.draw_rect(p.rect,color=None,fill=(1,1,1));T=fitz.Rect(PAD,PAD,PAD+W,PAD+H);edge=.5
  # Only exterior bleed is extended from existing edges; the complete trim is unchanged.
  regions=[(fitz.Rect(PAD,PAD-BLEED,PAD+W,PAD),fitz.Rect(0,0,W,edge)),(fitz.Rect(PAD,PAD+H,PAD+W,PAD+H+BLEED),fitz.Rect(0,H-edge,W,H)),(fitz.Rect(PAD-BLEED,PAD,PAD,PAD+H),fitz.Rect(0,0,edge,H)),(fitz.Rect(PAD+W,PAD,PAD+W+BLEED,PAD+H),fitz.Rect(W-edge,0,W,H))]
  for xx in [0,1]:
   for yy in [0,1]:
    dest=fitz.Rect(PAD+W if xx else PAD-BLEED,PAD+H if yy else PAD-BLEED,PAD+W+BLEED if xx else PAD,PAD+H+BLEED if yy else PAD);clip=fitz.Rect(W-edge if xx else 0,H-edge if yy else 0,W if xx else edge,H if yy else edge);regions.append((dest,clip))
  for dest,clip in regions:
   # Rasterize only the tiny exterior edge strip, avoiding repeated full-page CMYK transforms.
   pix=norm[pi].get_pixmap(matrix=fitz.Matrix(300/72,300/72),clip=clip,alpha=False,colorspace=fitz.csRGB);p.insert_image(dest,pixmap=pix,keep_proportion=False,overlay=True)
  p.show_pdf_page(T,norm,pi,keep_proportion=False)
  p.set_trimbox(T);p.set_bleedbox(T+(-BLEED,-BLEED,BLEED,BLEED))
  # K-only crop marks, entirely outside the bleed. No marks appear inside the artwork.
  for x in [T.x0,T.x1]:
   p.draw_line((x,T.y0-8*MM),(x,T.y0-3.7*MM),color=(0,0,0,1),width=.25);p.draw_line((x,T.y1+3.7*MM),(x,T.y1+8*MM),color=(0,0,0,1),width=.25)
  for y in [T.y0,T.y1]:
   p.draw_line((T.x0-8*MM,y),(T.x0-3.7*MM,y),color=(0,0,0,1),width=.25);p.draw_line((T.x1+3.7*MM,y),(T.x1+8*MM,y),color=(0,0,0,1),width=.25)
 dest=B/'intermediate'/f'{row["label"]}-framed-RGB.pdf';out.set_metadata({'title':'PrintPack A4 '+row['label'],'subject':'A4 trim,3mm bleed,reading order,color print','creator':'Print production PDF composition'});out.save(dest,garbage=0,deflate=True)
 records.append({'label':row['label'],'source':{'document':row['document_id'],'id':row['asset']['id'],'revision':row['asset']['revision'],'file':row['path'],'sha256':row['asset']['sha256']},'corrected':str(corrected.relative_to(R)),'normalized':str(normfile.relative_to(R)),'framed':str(dest.relative_to(R)),'pages':len(out),'media_mm':[230,317],'trim_mm':[210,297],'bleed_mm':3,'folio_changes':patches});print(row['label'],'framed',len(out),'pages',flush=True)
(B/'composition-proof.json').write_text(json.dumps({'outputs':records,'source_preserved':True,'bleed_method':'PDF edge extension outside trim only','crop_marks':'K-only, outside3mm bleed','manual_imposition':False},ensure_ascii=False,indent=2)+'\n')
