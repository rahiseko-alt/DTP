"""印刷面付けを保ったまま、ブラウザで扱いやすい軽量PDFを作る。"""
from pathlib import Path
import subprocess,json,hashlib,re,collections,ctypes,ctypes.util
import fitz
from PIL import Image,ImageChops,ImageStat
from pypdf import PdfReader,PdfWriter
from pypdf.generic import NameObject,DictionaryObject

ROOT=Path(__file__).resolve().parents[4]
CACHE=ROOT/'.cache/pdf-light-20261020';CACHE.mkdir(parents=True,exist_ok=True)
SHA=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
GS=['-q','-dSAFER','-dBATCH','-dNOPAUSE','-sDEVICE=pdfwrite','-dCompatibilityLevel=1.7','-dAutoRotatePages=/None','-dDetectDuplicateImages=true','-dCompressFonts=true','-dDownsampleColorImages=true','-dColorImageResolution=200','-dColorImageDownsampleType=/Bicubic','-dAutoFilterColorImages=false','-dColorImageFilter=/DCTEncode','-dJPEGQ=88','-dDownsampleGrayImages=true','-dGrayImageResolution=200','-dGrayImageDownsampleType=/Bicubic','-dDownsampleMonoImages=true','-dMonoImageResolution=400']
GS+=['-sColorConversionStrategy=RGB','-dOverrideICC=true','-dUseFastColor=true']
def decode_qr(pix):
    z=ctypes.CDLL(ctypes.util.find_library('zbar'));P=ctypes.c_void_p
    for name,args,result in [('zbar_image_scanner_create',[],P),('zbar_image_create',[],P),('zbar_image_scanner_set_config',[P,ctypes.c_int,ctypes.c_int,ctypes.c_int],ctypes.c_int),('zbar_image_set_format',[P,ctypes.c_ulong],None),('zbar_image_set_size',[P,ctypes.c_uint,ctypes.c_uint],None),('zbar_image_set_data',[P,P,ctypes.c_ulong,P],None),('zbar_scan_image',[P,P],ctypes.c_int),('zbar_image_first_symbol',[P],P),('zbar_symbol_next',[P],P),('zbar_symbol_get_data',[P],ctypes.c_char_p)]:
        f=getattr(z,name);f.argtypes=args;f.restype=result
    im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples).convert('L');buf=ctypes.create_string_buffer(im.tobytes());scanner=z.zbar_image_scanner_create();image=z.zbar_image_create();z.zbar_image_scanner_set_config(scanner,0,0,1);z.zbar_image_set_format(image,int.from_bytes(b'Y800','little'));z.zbar_image_set_size(image,*im.size);z.zbar_image_set_data(image,buf,len(im.tobytes()),None);z.zbar_scan_image(scanner,image);symbol=z.zbar_image_first_symbol(image);found=[]
    while symbol:found.append(z.zbar_symbol_get_data(symbol).decode());symbol=z.zbar_symbol_next(symbol)
    return found

for book,prefix in [('prospectus-isen-trial-2028','brochure'),('admissions-guide-2027','admissions')]:
    record=json.loads((ROOT/'books'/book/'parts/saddle-print-20261020.json').read_text());outputs=[]
    for source in record['outputs']:
        paper=source['paper'];src=ROOT/source['file'];assert SHA(src)==source['sha256']
        raw=CACHE/f'{prefix}-{paper}-gs.pdf'
        subprocess.run(['gs',*GS,f'-sOutputFile={raw}',str(src)],check=True)
        out=src.parent/f'print-{prefix}-{paper}.pdf'
        writer=PdfWriter(clone_from=raw)
        writer._root_object[NameObject('/ViewerPreferences')]=DictionaryObject({NameObject('/Duplex'):NameObject('/DuplexFlipShortEdge'),NameObject('/PrintScaling'):NameObject('/None'),NameObject('/Direction'):NameObject('/L2R')})
        with out.open('wb') as f:writer.write(f)
        fitz.TOOLS.mupdf_warnings(reset=True)
        old=fitz.open(src);new=fitz.open(out);assert len(old)==len(new)
        differences=[]
        for i,(a,b) in enumerate(zip(old,new)):
            assert a.rotation==b.rotation==0
            assert abs(a.rect.width-b.rect.width)<.02 and abs(a.rect.height-b.rect.height)<.02
            amounts=lambda p:collections.Counter(re.findall(r'\d{1,3}(?:,\d{3})+円',re.sub(r'\s+','',p.get_text())))
            assert amounts(a)==amounts(b),(book,paper,i+1,'amount mismatch')
            def thumb(p):
                pix=p.get_pixmap();return Image.frombytes('RGB',(pix.width,pix.height),pix.samples).resize((320,226),Image.Resampling.LANCZOS)
            delta=sum(ImageStat.Stat(ImageChops.difference(thumb(a),thumb(b))).mean)/3
            assert delta<4,(book,paper,i+1,delta)
            differences.append(delta)
        qr=decode_qr(new[1].get_pixmap(matrix=fitz.Matrix(150/72,150/72)))
        assert 'https://kaihougakuen.my.canva.site/' in qr,qr
        assert not fitz.TOOLS.mupdf_warnings(reset=True),'PDF decode warning'
        outputs.append({'paper':paper,'file':str(out.relative_to(ROOT)),'sha256':SHA(out),'bytes':out.stat().st_size,'source':source['file'],'source_sha256':SHA(src),'source_asset_id':f'saddle-print-{paper.lower()}','source_bytes':src.stat().st_size,'faces':len(new),'dimensions_and_rotation_unchanged':True,'page_order_verified_by_all_face_image_comparison':True,'max_thumbnail_mean_difference':max(differences),'native_currency_counts_unchanged':True,'qr_decoded_from_sheet_1_back_at_150dpi':qr,'duplex':'short-edge','scaling':'none'})
    proof={'date':'2026-10-20','book':book,'method':'Ghostscriptによるカラー/グレー画像200dpi化・JPEG品質88とフォント圧縮。文字のベクターを保持し、両面短辺反転・縮小なしの設定を再設定。原版は保持。','ghostscript_version':subprocess.check_output(['gs','--version'],text=True).strip(),'ghostscript_arguments':GS,'outputs':outputs,'self_review':True,'independent_review':False,'physical_print_test':False}
    (ROOT/'books'/book/'parts/saddle-print-light-20261020.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
    print(book,[(o['paper'],round(o['bytes']/1e6,2),round(o['max_thumbnail_mean_difference'],3)) for o in outputs],flush=True)
