"""Native-type reconstruction of flyer front; independent final inspection pending.
The existing photo is extracted without resampling. The native CTA and QR overlay
are imported unchanged. Only the text-baked header wall is repaired with imagegen.
"""
from pathlib import Path
import hashlib,json,io,os,shutil
from decimal import Decimal
import pikepdf
import fitz,yaml
import numpy as np
from PIL import Image
B=Path(__file__).resolve().parent;R=B.parents[2];A=B/'assets/flyer-front';A.mkdir(parents=True,exist_ok=True)
STORE=R/'shared/generated-assets/printpack-native-rebuild-20261111/flyer-front'
for generated in STORE.glob('*.png'):
 if not (A/generated.name).exists():shutil.copyfile(generated,A/generated.name)
rows=json.loads((B.parent/'receipts.json').read_text());source=R/rows[1]['path'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(source)==rows[1]['asset']['sha256']
source_doc=fitz.open(source);sp=source_doc[0];xref=sp.get_images()[0][0];ir=sp.get_image_rects(xref)[0];raw=source_doc.extract_image(xref);decoded=fitz.Pixmap(source_doc,xref);original=Image.frombytes('RGB',(decoded.width,decoded.height),decoded.samples);assert original.size==(2480,3508)
# Extraction only: no resampling, retouch, recolouring or person changes.
y0,y1=640,2597;photo=original.crop((0,y0,2480,y1));photo.save(A/'photo-extraction.png')
original.crop((0,0,2480,640)).save(A/'header-original.png')
w,h=210*72/25.4,297*72/25.4;d=fitz.open();p=d.new_page(width=w,height=h)
photo_rect=fitz.Rect(ir.x0,ir.y0+y0*ir.height/3508,ir.x1,ir.y0+y1*ir.height/3508)
# User approved local background repair on 2026-11-11. The generated input
# contains ONLY the header wall crop, no people. All people remain source pixels.
header=A/'header-clean.png';assert header.exists(),'Missing imagegen-repaired header asset'
p.insert_image(fitz.Rect(0,0,w,photo_rect.y0),filename=str(header),keep_proportion=False)
# The source matrix is 0.418718pt short of A4. Extend only the final source
# pixel column into that microscopic outer strip; never scale the photograph.
photo.crop((photo.width-1,0,photo.width,photo.height)).save(A/'photo-right-column.png')
# Paint the extension underneath the unmodified main photograph. A 0.1pt
# overscan beyond the page/photograph bounds avoids floating-point hairlines.
p.insert_image(fitz.Rect(photo_rect.x1-.1,photo_rect.y0-.1,w+.1,photo_rect.y1+.1),filename=str(A/'photo-right-column.png'),keep_proportion=False)
p.insert_image(photo_rect,filename=str(A/'photo-extraction.png'),keep_proportion=False)
p.insert_font(fontname='TitleBold',fontfile='/usr/share/fonts/opentype/urw-base35/NimbusSans-Bold.otf')
p.insert_font(fontname='JPBold',fontfile='/workspace/.dtp-tools/native-fonts/DTPRebuiltSansJPBold.otf')
p.insert_font(fontname='JPRegular',fontfile='/workspace/.dtp-tools/native-fonts/DTPRebuiltSansJPRegular.otf')
copy=[]
source_pixels=np.frombuffer(decoded.samples,dtype=np.uint8).reshape(decoded.height,decoded.width,decoded.n).astype(int)
font_files={'TitleBold':'/usr/share/fonts/opentype/urw-base35/NimbusSans-Bold.otf','JPBold':'/workspace/.dtp-tools/native-fonts/DTPRebuiltSansJPBold.otf','JPRegular':'/workspace/.dtp-tools/native-fonts/DTPRebuiltSansJPRegular.otf'}
def source_ink(roi):
 x0,y0,x1,y1=roi;a=source_pixels[y0:y1,x0:x1];mask=(a[:,:,2]-a[:,:,0]>35)&(a[:,:,1]-a[:,:,0]>15)&(a[:,:,0]<100);yy,xx=np.where(mask)
 pixels=[int(xx.min()+x0),int(yy.min()+y0),int(xx.max()+1+x0),int(yy.max()+1+y0)]
 rect=fitz.Rect(ir.x0+pixels[0]*ir.width/2480,ir.y0+pixels[1]*ir.height/3508,ir.x0+pixels[2]*ir.width/2480,ir.y0+pixels[3]*ir.height/3508)
 return rect,pixels,tuple(np.median(a[mask],axis=0)/255)
def font_ink(t,font,color):
 # Tight painted glyph bounds, measured independently of font ascender metadata.
 f=fitz.Font(fontfile=font_files[font]);dd=fitz.open();pp=dd.new_page(width=f.text_length(t,fontsize=20)+40,height=80);pp.draw_rect(pp.rect,color=None,fill=(.70,.73,.78));pp.insert_font(fontname='F',fontfile=font_files[font]);pp.insert_text((20,40),t,fontname='F',fontsize=20,color=color);pix=pp.get_pixmap(matrix=fitz.Matrix(16,16),alpha=False);a=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,pix.n);a=a.astype(int);yy,xx=np.where((a[:,:,2]-a[:,:,0]>35)&(a[:,:,1]-a[:,:,0]>15)&(a[:,:,0]<100))
 return fitz.Rect(xx.min()/16-20,yy.min()/16-40,(xx.max()+1)/16-20,(yy.max()+1)/16-40)
def put(t,roi,font='JPBold'):
 target,pixel_bounds,color=source_ink(roi);unit=font_ink(t,font,color);scale=target.height/unit.height;size=20*scale;sx=target.width/(unit.width*scale);x=target.x0-unit.x0*scale*sx;baseline=target.y0-unit.y0*scale;o=fitz.Point(x,baseline)
 p.insert_text(o,t,fontsize=size,fontname=font,color=color,morph=(o,fitz.Matrix(sx,1)))
 copy.append({'text':t,'origin_pt':[x,baseline],'font_size_pt':size,'font':font,'horizontal_scale':sx,'source_ink_pixels':pixel_bounds,'source_ink_bbox_pt':list(target),'source_color_median_RGB':[round(c*255) for c in color],'font_unit_ink_bbox_pt':list(unit)})
school=yaml.safe_load((R/'company-data/facts/school.yaml').read_text());courses=yaml.safe_load((R/'company-data/facts/courses.yaml').read_text())['courses']
put('AI BUSINESS’28',(0,0,2480,400),'TitleBold')
put(school['name'],(0,400,1140,590))
separator,separator_pixels,separator_color=source_ink((1140,400,1180,590));p.draw_rect(separator,color=None,fill=separator_color)
put(' ／ '.join(c['name'] for c in courses),(1200,400,2480,500))
# Existing source publication copy, not newly asserted facts.
put('AI活用 / ビジネス実務 / データ分析 / グローバルビジネス / マーケティング / IT活用 /',(1200,500,2480,558))
put('プレゼンテーション / プロジェクト実習 / キャリア支援',(1200,558,2480,630))
overlay=R/'books/oc-approved-20261017/parts/digital-cover-oc-draft-20261028-front-overlay/4325d546bb41e7672e75db321c40bbd3f238ade73362e092b38930f699497e9e/digital-cover-oc-draft-20261028-front-overlay.pdf';assert sha(overlay)=='4325d546bb41e7672e75db321c40bbd3f238ade73362e092b38930f699497e9e'
o=fitz.open(overlay);p.show_pdf_page(p.rect,o,0,keep_proportion=False)
out=B/'flyer-front-native-trial.pdf';d.save(out,deflate=True,garbage=4)
with pikepdf.open(out) as a4:
 box=pikepdf.Array([0,0,Decimal(210)*72/Decimal('25.4'),Decimal(297)*72/Decimal('25.4')])
 for key in ['/MediaBox','/CropBox','/TrimBox','/BleedBox','/ArtBox']:a4.pages[0].obj[key]=box
 temp=A/'front-a4-boxes.pdf';a4.save(temp,compress_streams=True)
os.replace(temp,out)
out_doc=fitz.open(out);op=out_doc[0];op.get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False).save(A/'preview.png')
report={'status':'DRAFT_PENDING_INDEPENDENT_REVIEW','source':str(source.relative_to(R)),'source_sha256':sha(source),'output':out.name,'output_sha256':sha(out),'pages':1,'size_pt':[w,h],'photo_extraction':{'source_xref':xref,'source_image_rect_pt':list(ir),'source_image_matrix':list(sp.get_image_info()[0]['transform']),'right_shortfall_pt':w-ir.x1,'right_shortfall_mm':(w-ir.x1)*25.4/72,'crop_pixels':[0,y0,2480,y1],'placement_pt':list(photo_rect),'resampled':False,'retouched':False,'source_pixel_mode':original.mode},'native_header_copy':copy,'native_characters':len(op.get_text()),'font_count':len(op.get_fonts()),'blockers':['Original raster glyph shapes cannot be identically reproduced by the replacement fonts; header ink bounds are fitted to source.','Independent visual comparison and full CMYK conversion pending.'],'cta_policy':'Original managed native overlay imported unchanged; no page screenshot used as background.','final_submission':False}
(B/'flyer-front-native-trial.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
# Reproducible verification of the trial, deliberately separate from acceptance.
import numpy as np,zxingcpp
checks={}
for name,rect in [('photo_interior',[2,156,592,622]),('cta',[0,625,w,h])]:
 rr=fitz.Rect(rect);x=sp.get_pixmap(matrix=fitz.Matrix(2,2),clip=rr,alpha=False);y=op.get_pixmap(matrix=fitz.Matrix(2,2),clip=rr,alpha=False);xx=np.frombuffer(x.samples,dtype=np.uint8);yy=np.frombuffer(y.samples,dtype=np.uint8);delta=np.abs(xx.astype(int)-yy.astype(int));checks[name]={'dpi':144,'different_channels':int(np.count_nonzero(delta)),'max_channel_delta':int(delta.max()),'mean_channel_delta':float(delta.mean())}
checks['qr']={}
for dpi in (150,300):
 pix=op.get_pixmap(matrix=fitz.Matrix(dpi/72,dpi/72),alpha=False);im=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,pix.n);checks['qr'][dpi]=[q.text for q in zxingcpp.read_barcodes(im)]
report['verification']=checks;report['visual_review']='Imagegen repaired only the people-free header crop. Source people-photo pixels and original native CTA/QR remain intact. Independent visual review is pending.'
(B/'flyer-front-native-trial.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(checks,ensure_ascii=False,indent=2))
photo_xref=next(i[0] for i in op.get_images() if (i[2],i[3])==(photo.width,photo.height));embedded=fitz.Pixmap(out_doc,photo_xref);expected=np.frombuffer(decoded.samples,dtype=np.uint8).reshape(decoded.height,decoded.width,decoded.n)[y0:y1,:,:];actual=np.frombuffer(embedded.samples,dtype=np.uint8).reshape(embedded.height,embedded.width,embedded.n)
assert np.array_equal(expected,actual),'Extracted photo pixels changed'
report['photo_extraction']['decoded_pixel_equal_to_original_crop']=True
report['glyph_zero']=sum(c[1]==0 for span in op.get_texttrace() for c in span['chars'])
(B/'flyer-front-native-trial.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
measurements=[]
for row in copy:
 target=fitz.Rect(row['source_ink_bbox_pt']);roi=target+(-1,-1,1,1);pix=op.get_pixmap(matrix=fitz.Matrix(8,8),clip=roi,alpha=False);a=np.frombuffer(pix.samples,dtype=np.uint8).reshape(pix.height,pix.width,pix.n).astype(int);yy,xx=np.where((a[:,:,2]-a[:,:,0]>35)&(a[:,:,1]-a[:,:,0]>15)&(a[:,:,0]<100));actual=fitz.Rect((pix.x+xx.min())/8,(pix.y+yy.min())/8,(pix.x+xx.max()+1)/8,(pix.y+yy.max()+1)/8);error=[a-b for a,b in zip(actual,target)];measurements.append({'text':row['text'],'source_ink_bbox_pt':list(target),'native_ink_bbox_pt':list(actual),'edge_delta_pt':error,'maximum_absolute_edge_delta_pt':max(abs(v) for v in error),'measurement_dpi':576})
report['header_ink_comparison']=measurements;report['header_ink_maximum_absolute_edge_delta_pt']=max(r['maximum_absolute_edge_delta_pt'] for r in measurements);report['right_edge_options']={'adopted':'keep_original_photo_mapping_and_extend_last_source_pixel_column_only','original_transform':list(sp.get_image_info()[0]['transform']),'not_performed':['stretch or enlarge photograph','regenerate people'],'authorization':'User explicitly authorized local background repair while preserving photographs faithfully.','extension_width_pt':w-ir.x1,'extension_source':'Last original pixel column, PDF-clipped and mapped only into outer 0.147714mm strip.'}
(B/'flyer-front-native-trial.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(measurements,ensure_ascii=False,indent=2))

report['header_repair']={'method':'imagegen background repair, people-free header crop only','input_crop':str((A/'header-original.png').relative_to(R)),'input_sha256':sha(A/'header-original.png'),'generated_original':str((A/'header-clean-generated-original.png').relative_to(R)),'generated_original_sha256':sha(A/'header-clean-generated-original.png'),'placed_asset':str(header.relative_to(R)),'placed_asset_sha256':sha(header),'generation_crop_pixels':[0,80,2172,638],'people_pixels_sent_to_generator':False,'wall_not_pixel_identical':'Local texture reconstruction was authorized; visible original wall seam and tonal gradient were requested and retained.'}
(B/'flyer-front-native-trial.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
