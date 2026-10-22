#!/usr/bin/env python3
"""Verify the rendered two-page flyer, including every visible QR destination."""
from pathlib import Path
import ctypes, ctypes.util, hashlib, json, re
import fitz, yaml
from PIL import Image
B=Path(__file__).resolve().parent;R=B.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
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
pdf=B/'output/OC黄色帯版_日本人イメージ_構成変更案_2P.pdf';doc=fitz.open(pdf);assert len(doc)==2
text=''.join(page.get_text() for page in doc);compact=re.sub(r'\s+','',text)
for date in facts['dates']:assert date in compact,date
for absent in ['11/9','11/23','12/7','留学生歓迎','３つのこと','3つのこと','ai-nyushi@jp-academy.net','http://','https://']:assert absent not in compact,absent
assert compact.count(email)==2
front=re.sub(r'\s+','',doc[0].get_text());assert facts['experience_heading'] in front
for absent in ['在校生と話せる','進路を相談できる']:assert absent not in front
proof={'pdf_sha256':sha(pdf),'pages':2,'dates':facts['dates'],'year_or_weekday_added':False,'printed_mail_count':compact.count(email),'qr_expected':payload,'qr_source':facts['contact_qr'],'qr_source_sha256':sha(R/facts['contact_qr']),'pages_verified':[]}
for n,page in enumerate(doc):
 assert abs(page.rect.width-595.28)<1 and abs(page.rect.height-841.89)<1
 png=B/f'output/page-{n+1}.png';png_values=decode(Image.open(png));pix=page.get_pixmap(matrix=fitz.Matrix(2,2),alpha=False);pdf_values=decode(Image.frombytes('RGB',(pix.width,pix.height),pix.samples))
 assert png_values==[payload],png_values
 assert pdf_values==[payload],pdf_values
 proof['pages_verified'].append({'page':n+1,'a4_portrait':True,'png_sha256':sha(png),'png_qr':png_values,'pdf_qr':pdf_values})
source=json.loads((B/'reviews/source-identification.json').read_text())
for obj in source['source_assets'].values():assert sha(R/obj['path'])==obj['sha256']
proof['preserved_original_pdf_front_back_sha_unchanged']=True
(B/'reviews/output-verification.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n');print(json.dumps(proof,ensure_ascii=False,indent=2))
