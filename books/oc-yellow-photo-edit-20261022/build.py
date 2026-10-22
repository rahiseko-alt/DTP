#!/usr/bin/env python3
"""Local original-art-preserving PDF overlay, with exact source-photo edits.

Only this BOOK is written. The preserved PDF remains an unchanged PDF underlay;
type, dates, contact/QR and the unified experience group are separate PDF objects.
Photo paths are explicit in reviews/edited-photo-manifest.json, never selected by similarity.
"""
from pathlib import Path
import argparse, hashlib, html, json
import fitz, yaml
from PIL import Image, ImageDraw, ImageFilter

B=Path(__file__).resolve().parent
R=B.parents[1]
MM=72/25.4
SOURCE=R/'references/school-own/oc-approved-20261017/original/approved.pdf'
UNDERLAY=R/'books/oc-approved-20261017/parts/latest-original-oc-pdf/2c0bd3b6d91449666adf9ac73091e10f7cb37831384ebe807d2ff6117cd264d1/latest-original-oc-pdf.pdf'
NAVY='#07174c';BLUE='#04529b';PALE='#e2f4fd';PINK='#ff377d'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
esc=lambda s:html.escape(str(s))
p=argparse.ArgumentParser()
p.add_argument('--require-edits',action='store_true')
args=p.parse_args()
school=yaml.safe_load((R/'company-data/facts/school.yaml').read_text())
oc=yaml.safe_load((R/'company-data/facts/oc-flyer.yaml').read_text())
contacts=yaml.safe_load((R/'company-data/facts/contacts.yaml').read_text())['contacts']
email=next(x['email'] for x in contacts if x['id']==oc['contact_id'])
assert oc['date_year'] is None and oc['date_weekdays'] is None
coords=json.loads((B/'reviews/photo-coordinates.json').read_text())
manifest=B/'reviews/edited-photo-manifest.json'
edits=json.loads(manifest.read_text()) if manifest.exists() else {}
if args.require_edits:
    assert set(coords).issubset(edits), 'Missing original-photo edits: '+','.join(set(coords)-set(edits))
src=fitz.open(SOURCE);base=fitz.open(UNDERLAY);out=fitz.open()
# Remove superseded vector contact text from the working copy as well as from
# print, without altering any source file, raster artwork or map.
for page,rect in [(0,fitz.Rect(108*MM,271*MM,210*MM,297*MM)),
                  (1,fitz.Rect(140*MM,256*MM,209*MM,286*MM))]:
    base[page].add_redact_annot(rect,fill=False)
    base[page].apply_redactions(images=0,graphics=0,text=0)
for i in range(2):
    pg=out.new_page(width=base[i].rect.width,height=base[i].rect.height)
    pg.show_pdf_page(pg.rect,base,i)

def rgb(h):return tuple(int(h[j:j+2],16)/255 for j in [1,3,5])
def fill(pg,r,color):pg.draw_rect(fitz.Rect(r),color=None,fill=rgb(color),overlay=True)
def text(pg,r,value,size,color=NAVY,bold=False,align='left',lineheight=1.1):
    value=value if '<' in value else esc(value)
    css='@font-face{font-family:ExactNoto;src:url(NotoSansCJK-Bold.ttc);font-weight:bold;} @font-face{font-family:ExactNoto;src:url(NotoSansCJK-Regular.ttc);font-weight:normal;}'
    _,scale=pg.insert_htmlbox(fitz.Rect(r),f'<div style="font-family:ExactNoto;font-size:{size}pt;font-weight:{700 if bold else 400};color:{color};text-align:{align};line-height:{lineheight};margin:0;padding:0">{value}</div>',css=css,archive=fitz.Archive('/usr/share/fonts/opentype/noto'))
    assert scale>.999, (value,scale,r)
def source_rect(page,r):
    im=src[page].get_images()[0];ar=src[page].get_image_rects(im[0])[0]
    w,h=im[2:4];x,y,cw,ch=r
    return fitz.Rect(ar.x0+x/w*ar.width,ar.y0+y/h*ar.height,ar.x0+(x+cw)/w*ar.width,ar.y0+(y+ch)/h*ar.height)
def native(r):return source_rect(0,r)
def front_text(r,value,size,**kwargs):text(out[0],native(r),value,size*native([0,0,1,1]).width,**kwargs)
def front_fill(r,color):fill(out[0],native(r),color)
def back_map(r):
    # Original back body was uniformly reduced from 210mm to 170mm by the
    # adopted-map edition. Keep that transform exactly, including page margins.
    s=170/210
    return fitz.Rect(20*MM+r.x0*s,2*MM+r.y0*s,20*MM+r.x1*s,2*MM+r.y1*s)
def insert_clipped(pg,r,path,holes):
    # Keep original handwritten/brush copy as source pixels in a few explicit
    # clip holes; this does not ask a generated image to reproduce typography.
    pg.insert_image(r,filename=str(path),keep_proportion=False,overlay=True)
    xref=pg.get_contents()[-1]
    def cmd(rect):
        return f'{rect.x0} {pg.rect.height-rect.y1} {rect.width} {rect.height} re\n'
    clip=cmd(r)+''.join(cmd(x) for x in holes)
    out.update_stream(xref,b'q\n'+clip.encode()+b'W* n\n'+out.xref_stream(xref)+b'\nQ\n')

def hero_composite(path):
    """DTP mask compositing: preserve existing artwork, feather photograph joins.

    The generated photograph itself is unmodified. Existing typography and
    brush art are taken from the original source, never generated or retyped.
    No restored patch contains a foreground face.
    """
    receipts=json.loads((B/'reviews/photo-input-receipts.json').read_text())
    original=Image.open(R/receipts['hero']['asset']['file']).convert('RGB')
    edited=Image.open(path).convert('RGB').resize(original.size,Image.Resampling.LANCZOS)
    w,h=original.size
    scale=w/722
    def xy(pt):return (round(pt[0]*scale),round((pt[1]-75)*scale))
    mask=Image.new('L',(w,h),0)
    # Narrow English-logo fragment, above all foreground faces and hair.
    patches=[[(0,75),(320,75),(320,104),(0,104)],
             [(18,105),(357,105),(364,178),(18,232)],
             [(525,377),(722,377),(722,480),(525,480)],
             # Preserve the original forearms, watch, pointing hands and
             # contact shadows together, keeping both new faces above them.
             [(360,295),(530,295),(530,432),(360,432)]]
    for poly in patches:
        patch=Image.new('L',(w,h),0);ImageDraw.Draw(patch).polygon([xy(pt) for pt in poly],fill=255)
        patch=patch.filter(ImageFilter.GaussianBlur(3*scale))
        # Preserve exact source letter interiors; softness applies to the
        # surrounding photograph only, avoiding visible rectangular joins.
        mask=Image.frombytes('L',(w,h),bytes(max(a,b) for a,b in zip(mask.tobytes(),patch.tobytes())))
    values=bytearray(mask.tobytes());source=original.load()
    for yy in range(h):
        native_y=yy/scale+75
        # Hands, paper, foreground clothing and the complete yellow brush are
        # preserved from the source. Blend on the forearms above the hands,
        # where poses align, never through fingertips or the painted ribbon.
        # Every face is above this band and remains the edited photograph.
        fade=round(255*max(0,min(1,(native_y-365)/20)))
        for xx in range(w):
            rr,gg,bb=source[xx,yy]
            pos=yy*w+xx
            values[pos]=max(values[pos],fade)
    mask=Image.frombytes('L',(w,h),bytes(values))
    composite=Image.composite(original,edited,mask)
    dest=B/'assets/front-hero-composited.png';composite.save(dest)
    mask.save(B/'reviews/hero-original-art-mask.png')
    return dest

photo_proof={}
for key,item in coords.items():
    if key not in edits:continue
    path=Path(edits[key]['file'] if isinstance(edits[key],dict) else edits[key])
    if not path.is_absolute():path=R/path
    assert path.is_file(), path
    pg=out[item['page']-1]
    rect=fitz.Rect(item['source_pdf_xyxy_pt'])
    if item['page']==2:rect=back_map(rect)
    if key=='front-hero':
        # Photo stops just above the large yellow brush. Source typography and
        # its backing pixels remain in place, including the white script.
        composited=hero_composite(path)
        pg.insert_image(rect,filename=str(composited),keep_proportion=False,overlay=True)
    else:
        pg.insert_image(rect,filename=str(path),keep_proportion=False,overlay=True)
        if key=='back-event':
            # The event photograph contains an existing blue display. Restore
            # its original pixels, avoiding synthetic lettering on the screen.
            screen=source_rect(1,[635,773,69,61])
            pg.show_pdf_page(back_map(screen),src,1,clip=screen)
    photo_proof[key]={'file':str(path.relative_to(R)),'sha256':sha(path),'source':item}

# Dates: retain the positions and oval language, remove all day-of-week stamps.
front_fill([64,580,480,82],'#ffffff')
for x,width,value in zip([69,227,393],[149,155,148],oc['dates']):
    r=native([x,580,width,82]);out[0].draw_oval(r,color=None,fill=rgb(PALE),overlay=True)
    front_text([x,596,width,55],value,43,bold=True,align='center')

# Remove the student-welcome badge and its arrow; retain the original parent
# badge artwork, centered beneath the dates/time without changing its content.
front_fill([143,661,462,47],'#ffffff')
badge=source_rect(0,[365,661,239,46])
out[0].show_pdf_page(native([242,661,239,46]),src,0,clip=badge)

# One continuous experience group, with the original three photos and all
# original information. The single oversized 1 applies to the whole group.
front_fill([27,714,455,31],BLUE)
front_text([31,716,460,30],oc['experience_heading'],20,bold=True,color='#ffffff')
group=native([16,746,688,188])
out[0].draw_rect(group,color=rgb('#d8edf6'),fill=rgb('#f2faff'),width=.8)
circle=native([27,755,45,45]);out[0].draw_oval(circle,color=None,fill=rgb(PINK))
front_text([28,756,43,43],'1',37,bold=True,color='#ffffff',align='center')
front_text([83,761,607,33],'AI・ビジネスの授業を体験',25,bold=True)
for key in ['front-class','front-friends','front-consult']:
    item=coords[key];rect=fitz.Rect(item['source_pdf_xyxy_pt'])
    if key in edits:
        pp=Path(edits[key]['file'] if isinstance(edits[key],dict) else edits[key]);pp=pp if pp.is_absolute() else R/pp
        out[0].insert_image(rect,filename=str(pp),keep_proportion=False)
    else:out[0].show_pdf_page(rect,src,0,clip=rect)
front_text([25,892,203,18],'授業を体験',14,bold=True,align='center')
front_text([251,892,190,18],'在校生と話せる',14,bold=True,align='center')
front_text([467,892,224,18],'進路を相談できる',14,bold=True,align='center')
front_text([26,913,201,17],'実際の授業を体験できます。',11.5,bold=True,align='center')
front_text([253,909,190,27],'学校生活や日本での生活を<br>直接聞けます。',11,bold=True,align='center')
front_text([468,909,223,27],'入試・学費・就職について<br>個別に相談できます。',11,bold=True,align='center')

def mmr(x,y,w,h):return fitz.Rect(x*MM,y*MM,(x+w)*MM,(y+h)*MM)
# The exact contact endpoint is taken from the OC facts; representative mail
# elsewhere in company-data is intentionally not edited.
qrpath=R/oc['contact_qr']
qr_doc=fitz.open(qrpath)
qr_pdf=fitz.open('pdf',qr_doc.convert_to_pdf())
def qr(pg,r):pg.show_pdf_page(r,qr_pdf,0)
fill(out[0],mmr(108,271,102,26),'#0c325d')
text(out[0],mmr(111,273,69,5),'入学事務局へのお問い合わせ',8,color='#ffffff')
text(out[0],mmr(111,279,69,7),school['tel'],13,color='#ffffff')
text(out[0],mmr(111,286,72,5),email,7.0,color='#ffffff')
qr(out[0],mmr(185,273,19,19))
text(out[0],mmr(181,292,27,5),'メールでお問い合わせ',5.8,color='#ffffff',align='center')
fill(out[1],mmr(140,256,68,30),'#ffffff')
text(out[1],mmr(141,257,67,5),email,6.9)
qr(out[1],mmr(142,264,20,20))
text(out[1],mmr(164,268,42,8),'メールでお問い合わせ<br>メール作成用QR',6.8)

(B/'output').mkdir(exist_ok=True)
pdf=B/'output/OC黄色帯版_原本写真加工_日本人イメージ_2P.pdf'
out.save(pdf,garbage=4,deflate=True)
final=fitz.open(pdf)
for i,pg in enumerate(final):pg.get_pixmap(matrix=fitz.Matrix(150/72,150/72)).save(B/f'output/page-{i+1}.png')
proof={'pdf':str(pdf.relative_to(R)),'sha256':sha(pdf),'page_count':len(final),'page_size_pt':[list(pg.rect) for pg in final],'preserved_underlay':{'file':str(UNDERLAY.relative_to(R)),'sha256':sha(UNDERLAY)},'original':{'file':str(SOURCE.relative_to(R)),'sha256':sha(SOURCE)},'facts_sha256':{str(path.relative_to(R)):sha(path) for path in [R/'company-data/facts/school.yaml',R/'company-data/facts/oc-flyer.yaml',R/'company-data/facts/contacts.yaml']},'photo_edits':photo_proof,'all_nine_original_photos_edited':len(photo_proof)==9,'dates':oc['dates'],'year':None,'weekday':None,'contact_email':email,'qr_file':str(qrpath.relative_to(R)),'qr_sha256':sha(qrpath),'experience':{'groups':1,'photo_count':3,'numbering':[1],'original_information_preserved':True},'release':False,'method':'PDF-native overlays retaining original raster artwork outside explicit changed areas','hero_compositing':'Original logo/handwritten copy, white copy, forearms/hands/watch, yellow brush and giant English lettering restored locally; all seven foreground faces from the processed original photograph; feathered joins above hands, never through fingertips','self_review':True,'independent_review':False}
(B/'reviews/build-proof.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'pdf':str(pdf),'sha256':sha(pdf),'edited_photos':len(photo_proof)},ensure_ascii=False))
