#!/usr/bin/env python3
"""Verify exact printed content, all four rendered QRs and preserved source art."""
from pathlib import Path
import ctypes,ctypes.util,hashlib,json,re,unicodedata
import fitz,yaml
from PIL import Image,ImageDraw,ImageChops
B=Path(__file__).resolve().parent;R=B.parents[1];MM=72/25.4
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def decode(im):
 z=ctypes.CDLL(ctypes.util.find_library('zbar'));P=ctypes.c_void_p
 signatures=[('zbar_image_scanner_create',[],P),('zbar_image_create',[],P),('zbar_image_scanner_set_config',[P,ctypes.c_int,ctypes.c_int,ctypes.c_int],ctypes.c_int),('zbar_image_set_format',[P,ctypes.c_ulong],None),('zbar_image_set_size',[P,ctypes.c_uint,ctypes.c_uint],None),('zbar_image_set_data',[P,P,ctypes.c_ulong,P],None),('zbar_scan_image',[P,P],ctypes.c_int),('zbar_image_first_symbol',[P],P),('zbar_symbol_next',[P],P),('zbar_symbol_get_data',[P],ctypes.c_char_p),('zbar_image_destroy',[P],None),('zbar_image_scanner_destroy',[P],None)]
 for name,args,res in signatures:f=getattr(z,name);f.argtypes=args;f.restype=res
 im=im.convert('L');raw=im.tobytes();buf=ctypes.create_string_buffer(raw);scanner=z.zbar_image_scanner_create();image=z.zbar_image_create()
 z.zbar_image_scanner_set_config(scanner,0,0,1);z.zbar_image_set_format(image,int.from_bytes(b'Y800','little'));z.zbar_image_set_size(image,*im.size);z.zbar_image_set_data(image,buf,len(raw),None);z.zbar_scan_image(scanner,image)
 found=[];symbol=z.zbar_image_first_symbol(image)
 while symbol:found.append(z.zbar_symbol_get_data(symbol).decode());symbol=z.zbar_symbol_next(symbol)
 z.zbar_image_destroy(image);z.zbar_image_scanner_destroy(scanner);return found
facts=yaml.safe_load((R/'company-data/facts/oc-flyer.yaml').read_text());contacts=yaml.safe_load((R/'company-data/facts/contacts.yaml').read_text())['contacts'];email=next(c['email'] for c in contacts if c['id']==facts['contact_id']);payload='mailto:'+email
proof=json.loads((B/'reviews/build-proof.json').read_text());pdf=R/proof['pdf'];doc=fitz.open(pdf)
assert proof['sha256']==sha(pdf) and len(doc)==2 and proof['all_nine_original_photos_edited']
compact=unicodedata.normalize('NFKC',re.sub(r'\s+','',''.join(p.get_text() for p in doc)))
for val in facts['dates']+[facts['experience_heading'],'在校生と話せる','進路を相談できる','実際の授業を体験できます。','学校生活や日本での生活を直接聞けます。','入試・学費・就職について個別に相談できます。']:assert val in compact,val
for val in ['11/9','11/23','12/7','留学生歓迎','3つのこと','ai-nyushi@jp-academy.net','http://','https://']:assert val not in compact,val
assert compact.count(email)==2
assert facts['date_year'] is None and facts['date_weekdays'] is None
for source in ['original','preserved_underlay']:assert sha(R/proof[source]['file'])==proof[source]['sha256']
original=fitz.open(R/proof['original']['file']);base=fitz.open(R/proof['preserved_underlay']['file'])
coords=json.loads((B/'reviews/photo-coordinates.json').read_text())
def native(r):
 im=original[0].get_images()[0];a=original[0].get_image_rects(im[0])[0];x,y,w,h=r
 return fitz.Rect(a.x0+x/im[2]*a.width,a.y0+y/im[3]*a.height,a.x0+(x+w)/im[2]*a.width,a.y0+(y+h)/im[3]*a.height)
def mmr(x,y,w,h):return fitz.Rect(x*MM,y*MM,(x+w)*MM,(y+h)*MM)
def back(r):return fitz.Rect(20*MM+r.x0*170/210,2*MM+r.y0*170/210,20*MM+r.x1*170/210,2*MM+r.y1*170/210)
allowed=[[native(coords['front-hero']['source_native_xywh']),native([64,580,480,82]),native([143,661,462,47]),native([16,711,688,225]),mmr(108,271,102,26)],[]]
allowed[1]=[back(fitz.Rect(v['source_pdf_xyxy_pt'])) for v in coords.values() if v['page']==2]+[mmr(140,256,69,30)]
record={'pdf_sha256':sha(pdf),'pages':2,'printed_gmail_count':2,'nine_processed_original_photos':True,'experience_groups':1,'experience_photos':3,'experience_numbering':[1],'qr_expected':payload,'pages_verified':[],'preserved_sources_sha_unchanged':True}
for i,page in enumerate(doc):
 assert abs(page.rect.width-595.2756)<.01 and abs(page.rect.height-841.8898)<.01
 png=B/f'output/page-{i+1}.png';png_values=decode(Image.open(png));pix=page.get_pixmap(matrix=fitz.Matrix(2,2),alpha=False);pdf_values=decode(Image.frombytes('RGB',(pix.width,pix.height),pix.samples))
 assert png_values==[payload] and pdf_values==[payload],(png_values,pdf_values)
 mat=fitz.Matrix(150/72,150/72)
 pix=base[i].get_pixmap(matrix=mat);before=Image.frombytes('RGB',(pix.width,pix.height),pix.samples);after=Image.open(png).convert('RGB')
 diff=ImageChops.difference(before,after).convert('L');mask=Image.new('L',before.size,255);draw=ImageDraw.Draw(mask)
 for rect in allowed[i]:draw.rectangle((rect.x0*150/72-3,rect.y0*150/72-3,rect.x1*150/72+3,rect.y1*150/72+3),fill=0)
 outside=ImageChops.multiply(diff,mask);assert outside.getbbox() is None,('Unexpected change outside approved regions',i+1,outside.getbbox())
 # A comparison sheet is evidence for visual review, not an alternative output.
 canvas=Image.new('RGB',(before.width*2,before.height),'#ffffff');canvas.paste(before,(0,0));canvas.paste(after,(before.width,0));canvas.thumbnail((1800,1600));canvas.save(B/f'reviews/comparison-round-2-page-{i+1}.jpg',quality=92)
 record['pages_verified'].append({'page':i+1,'a4_portrait':True,'png_sha256':sha(png),'png_qr':png_values,'pdf_qr':pdf_values,'unchanged_art_outside_explicit_masks_pixel_equal':True})
(B/'reviews/output-verification.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n');print(json.dumps(record,ensure_ascii=False,indent=2))
