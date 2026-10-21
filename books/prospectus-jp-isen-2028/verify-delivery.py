from pathlib import Path
import json,hashlib,re,collections,ctypes,ctypes.util
import fitz
from PIL import Image
B=Path(__file__).resolve().parent
def decode(pix):
 z=ctypes.CDLL(ctypes.util.find_library('zbar'));P=ctypes.c_void_p
 for name,args,result in [('zbar_image_scanner_create',[],P),('zbar_image_create',[],P),('zbar_image_scanner_set_config',[P,ctypes.c_int,ctypes.c_int,ctypes.c_int],ctypes.c_int),('zbar_image_set_format',[P,ctypes.c_ulong],None),('zbar_image_set_size',[P,ctypes.c_uint,ctypes.c_uint],None),('zbar_image_set_data',[P,P,ctypes.c_ulong,P],None),('zbar_scan_image',[P,P],ctypes.c_int),('zbar_image_first_symbol',[P],P),('zbar_symbol_next',[P],P),('zbar_symbol_get_data',[P],ctypes.c_char_p)]:
  f=getattr(z,name);f.argtypes=args;f.restype=result
 im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples).convert('L');buf=ctypes.create_string_buffer(im.tobytes());scanner=z.zbar_image_scanner_create();image=z.zbar_image_create();z.zbar_image_scanner_set_config(scanner,0,0,1);z.zbar_image_set_format(image,int.from_bytes(b'Y800','little'));z.zbar_image_set_size(image,*im.size);z.zbar_image_set_data(image,buf,len(im.tobytes()),None);z.zbar_scan_image(scanner,image);symbol=z.zbar_image_first_symbol(image);found=[]
 while symbol:found.append(z.zbar_symbol_get_data(symbol).decode());symbol=z.zbar_symbol_next(symbol)
 return found
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
amounts=lambda p:collections.Counter(re.findall(r'\d{1,3}(?:,\d{3})+円',re.sub(r'\s+','',p.get_text())))
master=B/'output/医専日本人版_16P_確認用.pdf';reading=B/'output/医専日本人版_16P_閲覧用.pdf'
a=fitz.open(master);b=fitz.open(reading);assert len(a)==len(b)==16
for p,q in zip(a,b):assert amounts(p)==amounts(q)
proof=json.loads((B/'reviews/assembly-proof.json').read_text())
prints=[]
for paper in ['A3','A4']:
 path=B/f'output/医専日本人版_{paper}_印刷用.pdf';doc=fitz.open(path);assert len(doc)==8
 for p,f in zip(doc,proof['print_faces']):assert amounts(p)==amounts(a[f['left']-1])+amounts(a[f['right']-1])
 prints.append({'paper':paper,'sha256':sha(path),'faces':8,'sheets':4})
qr=decode(b[14].get_pixmap(matrix=fitz.Matrix(2,2)));assert 'https://kaihougakuen.my.canva.site/' in qr,qr
result={'revision':3,'reading_pages':16,'master_sha256':sha(master),'reading_sha256':sha(reading),'print_outputs':prints,'native_currency_counts_unchanged_after_compression':True,'native_currency_counts_in_every_imposed_face_verified':True,'qr_decoded':qr,'physical_print_test':False}
(B/'reviews/delivery-check.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))
