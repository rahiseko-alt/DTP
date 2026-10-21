#!/usr/bin/env python3
"""Deterministic, non-generative replacement of only the cover group photograph.
Run from repository root; original PDF and selected saved photograph remain unchanged.
"""
from pathlib import Path
import hashlib,json,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from scipy import ndimage
import fitz
ROOT=Path(__file__).resolve().parents[4]
W=ROOT/'books/prospectus-jp-isen-2028/work/cover'
PDF=ROOT/'books/prospectus-isen-trial-2028/parts/latest-prospectus-pdf/62aa8e4415e5e6aa4523e1c14d024d8d45112d81dc92ce8db16db7718066f880/latest-prospectus-pdf.pdf'
PHOTO=ROOT/'shared/generated-assets/cover-group-jp/日本人版マシな方1.png'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
doc=fitz.open(PDF);im=doc.extract_image(doc[0].get_images(full=True)[0][0]);(W/'source-cover.png').write_bytes(im['image'])
src=Image.open(W/'source-cover.png').convert('RGB');s=np.asarray(src);photo=Image.open(PHOTO).convert('RGB')
# A rectangular photographic crop preserves the complete saved group, including
# faces, hair, bodies, feet, and the natural room/floor around them.
vertices=[]
crop=(165,315,1245,1060);target_width=2480;scale=target_width/(crop[2]-crop[0]);target_height=round((crop[3]-crop[1])*scale);position=(0,780)
fg=photo.crop(crop).resize((target_width,target_height),Image.Resampling.LANCZOS)
fg.save(W/'replacement-photo-crop.png')
wall=np.median(s[640:700,1000:1500],axis=(0,1));floor=np.median(s[3015:3045,1000:1300],axis=(0,1))
bg=np.zeros_like(s)
# Extend blank wall above the photo using a clean wall color; no photo/person
# pixels are synthesized. The lower extension uses the real photo's clean floor.
photo_wall=np.median(np.asarray(photo)[320:350,180:260],axis=(0,1))
photo_floor=np.median(np.asarray(photo)[1045:1060,165:1245],axis=(0,1))
for yy in range(3508):
 if yy<position[1]:
  t=np.clip((yy-640)/(position[1]-640),0,1)
  bg[yy]=np.uint8(wall*(1-t)+photo_wall*t)
 elif yy>=position[1]+target_height:
  t=np.clip((yy-position[1]-target_height)/(2960-position[1]-target_height),0,1)
  bg[yy]=np.uint8(photo_floor*(1-t)+floor*t)
# Only the first 120px (blank/decorated wall) and last 32px (clean floor) are
# feathered; every person's face, hair, body and feet remains fully opaque.
photo_alpha=np.ones((target_height,target_width),np.float32)
photo_alpha[:120]=np.linspace(0,1,120)[:,None]
photo_alpha[-32:]=np.linspace(1,0,32)[:,None]
# Fill directly under the upper/lower edge with stable wall/floor color.
bg[position[1]:position[1]+120]=np.uint8(photo_wall)
bg[position[1]+target_height-32:position[1]+target_height]=np.uint8(photo_floor)
out=Image.fromarray(bg);out.paste(fg,position,Image.fromarray(np.uint8(photo_alpha*255)))
# Untouched header and bottom paper/floor are retained; a 40px transition is wholly
# inside the blank strip between the last small text and the original first head.
replace=np.zeros((3508,2480),np.float32);replace[680:2900]=1
replace[640:680]=np.linspace(0,1,40)[:,None];replace[2900:2960]=np.linspace(1,0,60)[:,None]
# Copy mask: seed neutral white strokes, select every text component, retain a
# four-pixel halo including antialias/shadow. No original people survive the mask.
lo=s.min(axis=2);ch=s.max(axis=2).astype(int)-lo.astype(int)
seed=(lo>185)&(ch<45);seed[:2760]=False
labels,n=ndimage.label(seed);sizes=np.bincount(labels.ravel());keep=sizes>15;keep[0]=False
copy=ndimage.binary_dilation(keep[labels],iterations=4)
# Exclude any small isolated nontext highlights above the first line.
copy[:2770]=False
Image.fromarray(np.uint8(copy)*255).save(W/'original-copy-protection-mask.png')
replace[copy]=0
result=Image.composite(out,src,Image.fromarray(np.uint8(replace*255)))
result.save(W/'cover-page.png',dpi=(300,300))
result.resize((620,877)).save(W/'cover-preview.png')
r=np.asarray(result)
report={'page_size_px':[2480,3508],'output_dpi_metadata':300,'source_pdf':str(PDF.relative_to(ROOT)),'source_pdf_sha256':sha(PDF),'source_page':1,'source_embedded_image_xref':5,'source_embedded_image_sha256':sha(W/'source-cover.png'),'selected_saved_photo':str(PHOTO.relative_to(ROOT)),'selected_saved_photo_sha256':sha(PHOTO),'selected_saved_photo_size_px':list(photo.size),'photo_native_effective_dpi_at_300dpi_page':300/scale,'photo_edge_feather_target_px':{'top_wall':120,'bottom_floor':32},'person_extent_source_px':[170,382,1238,1041],'person_extent_full_opacity_target_y':[934,2447],'method':'Non-generative PIL/numpy compositing of the complete rectangular saved photograph crop; isotropic resize only; wall/floor extension; original raster copy restored with protection mask.','photo_crop_source_px':list(crop),'photo_outer_contour_source_px':vertices,'foreground_target_size_px':list(fg.size),'foreground_position_px':list(position),'scale_x':scale,'scale_y_nominal':scale,'scale_y_raster':target_height/(crop[3]-crop[1]),'rounding_note':'Height rounded to nearest integer pixel; no intentional nonuniform stretching.','photo_replacement_region':{'full_width':True,'top_transition_y':[640,680],'opaque_y':[680,2900],'bottom_transition_y':[2900,2960]},'reconstructed_background':{'wall_rgb':wall.tolist(),'floor_rgb':floor.tolist(),'upper_extension_y':[640,780],'lower_floor_extension_y':[position[1]+target_height,2960],'photo_wall_rgb':photo_wall.tolist()},'protection':{'header_unmodified_y':[0,640],'copy_seed_min_channel':185,'copy_seed_max_chroma':45,'copy_seed_y_min':2760,'minimum_component_pixels':16,'dilation_px':4,'copy_mask_sha256':sha(W/'original-copy-protection-mask.png'),'protected_copy_pixels':int(copy.sum()),'protected_copy_changed_pixels':int(np.any(s[copy]!=r[copy],axis=1).sum()),'header_changed_pixels':int(np.any(s[:640]!=r[:640],axis=2).sum())},'output_sha256':sha(W/'cover-page.png'),'review':'See cover-review.md. Saved candidate photo was used exactly as requested; no persons regenerated.','constraints':['All header pixels y<640 are byte-identical. Original-copy-protection-mask.png preserves exact original copy strokes, antialias and surrounding 4px halo.','The complete photograph crop is approximately 1711px tall; excess wall/floor space is intentional to avoid body distortion.','The selected saved candidate has approximately 131 native dpi after placement at A4 width; upstream generated-image content and resolution are inherited unchanged.']}
(W/'provenance.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ['page_size_px','foreground_target_size_px','foreground_position_px','output_sha256','protection']},ensure_ascii=False,indent=2))
